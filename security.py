"""
🛡️ SECURITY MODULE — Bot Probability
Central security layer: rate limiting, IP logging, honeypot traps.
"""

import time
import threading
import datetime
import os
import json
from functools import wraps
from flask import request, jsonify, abort

# ============================================================
# RATE LIMITER — In-memory tracker per IP
# ============================================================

class RateLimiter:
    """Thread-safe in-memory rate limiter using sliding window."""
    
    def __init__(self):
        self._store = {}  # key -> list of timestamps
        self._lock = threading.Lock()
        # Auto-cleanup every 10 minutes
        self._cleanup_thread = threading.Thread(target=self._auto_cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def _auto_cleanup(self):
        while True:
            time.sleep(600)
            self._cleanup()
    
    def _cleanup(self):
        """Remove expired entries to prevent memory leak."""
        now = time.time()
        with self._lock:
            expired_keys = []
            for key, timestamps in self._store.items():
                # Keep only timestamps from last hour
                self._store[key] = [t for t in timestamps if now - t < 3600]
                if not self._store[key]:
                    expired_keys.append(key)
            for key in expired_keys:
                del self._store[key]
    
    def is_rate_limited(self, key, max_calls, window_seconds):
        """
        Check if key exceeded max_calls within window_seconds.
        Returns (is_limited, retry_after_seconds).
        """
        now = time.time()
        with self._lock:
            if key not in self._store:
                self._store[key] = []
            
            # Remove timestamps outside window
            self._store[key] = [t for t in self._store[key] if now - t < window_seconds]
            
            if len(self._store[key]) >= max_calls:
                oldest = self._store[key][0]
                retry_after = int(window_seconds - (now - oldest)) + 1
                return True, retry_after
            
            # Record this attempt
            self._store[key].append(now)
            return False, 0
    
    def record_hit(self, key):
        """Record a hit without checking (for manual tracking)."""
        now = time.time()
        with self._lock:
            if key not in self._store:
                self._store[key] = []
            self._store[key].append(now)


# Global rate limiter instance
limiter = RateLimiter()

# ============================================================
# IP BLOCKER — Dynamic IP blacklist
# ============================================================

class IPBlocker:
    """Blocks IPs flagged by honeypots or excessive abuse."""
    
    def __init__(self):
        self._blocked = {}  # ip -> unblock_timestamp
        self._lock = threading.Lock()
    
    def block(self, ip, duration_seconds=3600):
        """Block an IP for duration_seconds (default 1 hour)."""
        with self._lock:
            self._blocked[ip] = time.time() + duration_seconds
        _log_security_event("IP_BLOCKED", ip, f"Blocked for {duration_seconds}s")
    
    def is_blocked(self, ip):
        """Check if IP is currently blocked."""
        with self._lock:
            if ip in self._blocked:
                if time.time() < self._blocked[ip]:
                    return True
                else:
                    del self._blocked[ip]
            return False
    
    def unblock(self, ip):
        with self._lock:
            self._blocked.pop(ip, None)


# Global IP blocker instance
ip_blocker = IPBlocker()

# ============================================================
# SECURITY EVENT LOGGER
# ============================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
SECURITY_LOG = os.path.join(LOG_DIR, "security.log")

def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def _log_security_event(event_type, ip, details=""):
    """Append security event to the security log file."""
    _ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{event_type}] IP={ip} | {details}\n"
    
    try:
        with open(SECURITY_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass  # Fail silently — logging should never crash the app
    
    # Also print to console for immediate visibility
    print(f"🛡️ SECURITY | {entry.strip()}")


def log_failed_login(ip, email):
    _log_security_event("FAILED_LOGIN", ip, f"email={email}")

def log_suspicious_activity(ip, details):
    _log_security_event("SUSPICIOUS", ip, details)

def log_honeypot_triggered(ip, path):
    _log_security_event("HONEYPOT_TRIGGER", ip, f"path={path}")

def log_rate_limited(ip, endpoint):
    _log_security_event("RATE_LIMITED", ip, f"endpoint={endpoint}")

# ============================================================
# DECORATORS
# ============================================================

def rate_limit(max_calls, window_seconds, scope=None):
    """
    Rate limiting decorator for Flask routes.
    
    Usage:
        @app.route('/api/login', methods=['POST'])
        @rate_limit(5, 900)  # 5 attempts per 15 min
        def login_api():
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = _get_client_ip()
            
            # Check if IP is globally blocked
            if ip_blocker.is_blocked(ip):
                return jsonify({
                    "status": "error",
                    "message": "Acesso temporariamente bloqueado. Tente novamente mais tarde."
                }), 429
            
            key = f"rl:{scope or request.endpoint}:{ip}"
            limited, retry_after = limiter.is_rate_limited(key, max_calls, window_seconds)
            
            if limited:
                log_rate_limited(ip, request.endpoint)
                response = jsonify({
                    "status": "error",
                    "message": "Muitas tentativas. Tente novamente mais tarde.",
                    "retry_after": retry_after
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(retry_after)
                return response
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def check_blocked_ip(f):
    """Decorator to reject requests from blocked IPs."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        ip = _get_client_ip()
        if ip_blocker.is_blocked(ip):
            return jsonify({
                "status": "error",
                "message": "Acesso bloqueado."
            }), 403
        return f(*args, **kwargs)
    return wrapper

# ============================================================
# HONEYPOT ROUTES — Trap attackers scanning for vulnerabilities
# ============================================================

HONEYPOT_PATHS = [
    '/wp-admin', '/wp-login.php', '/wp-login',
    '/administrator', '/admin.php',
    '/phpmyadmin', '/phpMyAdmin', '/pma',
    '/.env', '/.git', '/.git/config',
    '/config.php', '/wp-config.php',
    '/xmlrpc.php', '/wp-content',
    '/backup', '/backup.sql', '/dump.sql',
    '/api/v1/admin', '/debug/vars',
    '/actuator', '/actuator/health',
    '/server-status', '/server-info',
    '/.well-known/security.txt',
]

def register_honeypots(app):
    """Register honeypot trap routes on the Flask app."""
    
    def honeypot_handler(path=''):
        ip = _get_client_ip()
        full_path = request.path
        log_honeypot_triggered(ip, full_path)
        
        # Block IP for 2 hours after hitting a honeypot
        ip_blocker.block(ip, duration_seconds=7200)
        
        # Return a convincing 404 (don't reveal it's a trap)
        return jsonify({"status": "error", "message": "Not Found"}), 404
    
    for path in HONEYPOT_PATHS:
        endpoint_name = f"honeypot_{path.replace('/', '_').replace('.', '_')}"
        app.add_url_rule(
            path,
            endpoint=endpoint_name,
            view_func=honeypot_handler,
            methods=['GET', 'POST', 'PUT', 'DELETE']
        )
    
    print(f"🛡️ SECURITY | {len(HONEYPOT_PATHS)} honeypot traps armed!")


# ============================================================
# GLOBAL REQUEST SHIELD — before_request middleware
# ============================================================

def register_security_middleware(app):
    """Register global security middleware on the Flask app."""
    
    @app.before_request
    def security_gate():
        ip = _get_client_ip()
        
        # 1. Check if IP is blocked
        if ip_blocker.is_blocked(ip):
            return jsonify({
                "status": "error",
                "message": "Acesso temporariamente bloqueado."
            }), 403
        
        # 2. Global rate limit: 120 requests/min per IP (generous for normal use)
        key = f"global:{ip}"
        limited, retry_after = limiter.is_rate_limited(key, 120, 60)
        if limited:
            log_rate_limited(ip, f"GLOBAL ({request.path})")
            return jsonify({
                "status": "error",
                "message": "Rate limit excedido."
            }), 429
        
        # 3. Detect suspicious user agents
        ua = request.headers.get('User-Agent', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab', 'gobuster', 'dirbuster', 'wfuzz', 'hydra']
        if any(agent in ua for agent in suspicious_agents):
            log_suspicious_activity(ip, f"Suspicious UA: {ua[:100]}")
            ip_blocker.block(ip, duration_seconds=86400)  # 24h block
            return jsonify({"status": "error", "message": "Forbidden"}), 403


# ============================================================
# UTILITIES
# ============================================================

def _get_client_ip():
    """Get client IP, respecting reverse proxy headers."""
    # Check X-Forwarded-For (Render, Heroku, Cloudflare, etc.)
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'


def get_security_report():
    """Returns a dict summarizing current security state (for admin panel)."""
    with ip_blocker._lock:
        blocked_count = len(ip_blocker._blocked)
        blocked_ips = list(ip_blocker._blocked.keys())[:10]
    
    with limiter._lock:
        tracked_keys = len(limiter._store)
    
    # Read last 20 security log entries
    recent_events = []
    try:
        if os.path.exists(SECURITY_LOG):
            with open(SECURITY_LOG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_events = [l.strip() for l in lines[-20:]]
    except Exception:
        pass
    
    return {
        "blocked_ips_count": blocked_count,
        "blocked_ips_sample": blocked_ips,
        "tracked_rate_limit_keys": tracked_keys,
        "recent_events": recent_events
    }
