"""
🛡️ SECURITY MODULE — Bot Probability
Central security layer: rate limiting, IP logging, honeypot traps, anti-scan warfare.
"""

import time
import re
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
        self._cleanup_thread = threading.Thread(target=self._auto_cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def _auto_cleanup(self):
        while True:
            time.sleep(600)
            self._cleanup()
    
    def _cleanup(self):
        now = time.time()
        with self._lock:
            expired_keys = [k for k, v in self._store.items() if not [t for t in v if now - t < 3600]]
            for key in expired_keys:
                del self._store[key]
            for key in list(self._store.keys()):
                self._store[key] = [t for t in self._store[key] if now - t < 3600]
    
    def is_rate_limited(self, key, max_calls, window_seconds):
        now = time.time()
        with self._lock:
            if key not in self._store:
                self._store[key] = []
            self._store[key] = [t for t in self._store[key] if now - t < window_seconds]
            if len(self._store[key]) >= max_calls:
                oldest = self._store[key][0]
                retry_after = int(window_seconds - (now - oldest)) + 1
                return True, retry_after
            self._store[key].append(now)
            return False, 0
    
    def get_count(self, key, window_seconds):
        """Get current hit count for a key within window."""
        now = time.time()
        with self._lock:
            if key not in self._store:
                return 0
            return len([t for t in self._store[key] if now - t < window_seconds])
    
    def record_hit(self, key):
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
        self._blocked = {}  # ip -> (unblock_timestamp, reason)
        self._strike_count = {}  # ip -> number of offenses
        self._lock = threading.Lock()
    
    def block(self, ip, duration_seconds=3600, reason=""):
        with self._lock:
            # Escalating bans: each offense doubles the duration
            self._strike_count[ip] = self._strike_count.get(ip, 0) + 1
            strikes = self._strike_count[ip]
            actual_duration = duration_seconds * (2 ** (strikes - 1))  # 1h -> 2h -> 4h -> 8h...
            max_duration = 86400 * 7  # Cap at 7 days
            actual_duration = min(actual_duration, max_duration)
            
            self._blocked[ip] = time.time() + actual_duration
        _log_security_event("IP_BLOCKED", ip, f"Duration={actual_duration}s Strike#{strikes} | {reason}")
    
    def is_blocked(self, ip):
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
    
    def get_blocked_count(self):
        with self._lock:
            now = time.time()
            return len({ip: t for ip, t in self._blocked.items() if t > now})


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
    _ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{event_type}] IP={ip} | {details}\n"
    try:
        with open(SECURITY_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass
    print(f"SECURITY | {entry.strip()}")


def log_failed_login(ip, email):
    _log_security_event("FAILED_LOGIN", ip, f"email={email}")

def log_suspicious_activity(ip, details):
    _log_security_event("SUSPICIOUS", ip, details)

def log_honeypot_triggered(ip, path):
    _log_security_event("HONEYPOT_TRIGGER", ip, f"path={path}")

def log_rate_limited(ip, endpoint):
    _log_security_event("RATE_LIMITED", ip, f"endpoint={endpoint}")

def log_scan_detected(ip, details):
    _log_security_event("SCAN_DETECTED", ip, details)

# ============================================================
# DECORATORS
# ============================================================

def rate_limit(max_calls, window_seconds, scope=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = _get_client_ip()
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
    @wraps(f)
    def wrapper(*args, **kwargs):
        ip = _get_client_ip()
        if ip_blocker.is_blocked(ip):
            return jsonify({"status": "error", "message": "Acesso bloqueado."}), 403
        return f(*args, **kwargs)
    return wrapper

# ============================================================
# HONEYPOT ROUTES — Trap attackers scanning for vulnerabilities
# ============================================================

HONEYPOT_PATHS = [
    # WordPress
    '/wp-admin', '/wp-login.php', '/wp-login', '/wp-content', '/wp-includes',
    '/wp-config.php', '/wp-config.php.bak', '/wp-config.txt',
    '/xmlrpc.php', '/wp-cron.php', '/wp-json',
    # PHP Admin / DB Tools
    '/phpmyadmin', '/phpMyAdmin', '/pma', '/myadmin', '/mysql',
    '/adminer.php', '/adminer', '/dbadmin',
    # Common CMS / Admin paths
    '/administrator', '/admin.php', '/admin.asp', '/admin.jsp',
    '/joomla', '/drupal', '/magento',
    # Config / Secrets
    '/.env', '/.env.bak', '/.env.old', '/.env.production',
    '/.git', '/.git/config', '/.git/HEAD', '/.gitignore',
    '/.svn', '/.svn/entries',
    '/.htaccess', '/.htpasswd',
    '/config.php', '/config.yml', '/config.json', '/config.bak',
    '/web.config', '/application.yml', '/appsettings.json',
    # Database dumps
    '/backup', '/backup.sql', '/dump.sql', '/database.sql',
    '/db.sql', '/db_backup.sql', '/data.sql',
    '/backup.zip', '/backup.tar.gz', '/site.zip',
    # Server info
    '/server-status', '/server-info', '/info.php', '/phpinfo.php', '/test.php',
    '/status', '/health', '/debug',
    # API / DevOps
    '/api/v1/admin', '/debug/vars', '/debug/pprof',
    '/actuator', '/actuator/health', '/actuator/env',
    '/metrics', '/prometheus', '/grafana',
    '/console', '/shell', '/terminal',
    # AWS / Cloud
    '/.aws/credentials', '/aws.yml',
    '/robots.txt.bak',
    # Common exploit paths
    '/cgi-bin', '/cgi-bin/test', '/cgi-bin/admin',
    '/eval', '/exec', '/cmd', '/command',
    '/.well-known/security.txt',
]

def register_honeypots(app):
    """Register honeypot trap routes on the Flask app."""
    
    def honeypot_handler(path=''):
        ip = _get_client_ip()
        full_path = request.path
        log_honeypot_triggered(ip, full_path)
        ip_blocker.block(ip, duration_seconds=7200, reason=f"Honeypot: {full_path}")
        # Return convincing 404 — never reveal it's a trap
        return jsonify({"status": "error", "message": "Not Found"}), 404
    
    registered = 0
    for path in HONEYPOT_PATHS:
        endpoint_name = f"hp_{abs(hash(path))}"
        try:
            app.add_url_rule(
                path,
                endpoint=endpoint_name,
                view_func=honeypot_handler,
                methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
            )
            registered += 1
        except Exception:
            pass  # Skip duplicates silently
    
    print(f"SECURITY | {registered} honeypot traps armed!")


# ============================================================
# ANTI-SCAN ENGINE — Deep request inspection
# ============================================================

# Suspicious file extensions that scanners probe for
BLOCKED_EXTENSIONS = {
    '.php', '.asp', '.aspx', '.jsp', '.cgi', '.pl', '.sh', '.bat', '.cmd',
    '.exe', '.dll', '.com', '.bin', '.msi',
    '.bak', '.old', '.orig', '.save', '.swp', '.tmp',
    '.sql', '.sqlite', '.db', '.mdb',
    '.log', '.conf', '.ini', '.cfg',
    '.xml', '.yml', '.yaml', '.toml',
    '.zip', '.tar', '.gz', '.rar', '.7z',
}

# Patterns that indicate SQL injection, path traversal, or command injection
ATTACK_PATTERNS = [
    # SQL Injection
    re.compile(r"('|\"|;|--|\bOR\b\s+\b1\b\s*=\s*\b1\b|\bUNION\b\s+\bSELECT\b|\bDROP\b\s+\bTABLE\b|\bINSERT\b\s+\bINTO\b)", re.IGNORECASE),
    # Path traversal
    re.compile(r"(\.\.\/|\.\.\\|%2e%2e|%252e%252e|\.\.%2f|\.\.%5c)", re.IGNORECASE),
    # Command injection
    re.compile(r"(;\s*(ls|cat|whoami|id|pwd|uname|ping|curl|wget|nc|bash|sh|cmd)\b|`.*`|\$\(.*\)|\|\||\&\&)", re.IGNORECASE),
    # XSS attempts
    re.compile(r"(<script|javascript:|on(error|load|click|mouseover)\s*=|<img\s+src\s*=\s*[\"']?javascript)", re.IGNORECASE),
    # LDAP injection
    re.compile(r"(\*\)\(\||\)\(\&|\(cn=\*|\(objectClass=\*)", re.IGNORECASE),
    # Null byte injection
    re.compile(r"(%00|\\x00|\\0)", re.IGNORECASE),
]

# Scanner user agents (expanded list)
SCANNER_USER_AGENTS = [
    'sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab', 'gobuster', 'dirbuster',
    'wfuzz', 'hydra', 'burpsuite', 'owasp', 'acunetix', 'nessus', 'qualys',
    'openvas', 'arachni', 'skipfish', 'w3af', 'zap', 'nuclei', 'httpx',
    'subfinder', 'amass', 'ffuf', 'feroxbuster', 'dirb', 'whatweb',
    'wpscan', 'joomscan', 'droopescan', 'cmsmap',
    'python-requests/', 'go-http-client', 'java/', 'libwww-perl',
    'curl/', 'wget/',  # Only block bare curl/wget without browser context
    'scrapy', 'mechanize', 'phantom', 'headless',
    'bot', 'spider', 'crawl',  # Generic bot patterns
]

# Whitelist for known good bots (search engines, uptime monitors)
WHITELISTED_UA_PATTERNS = [
    'googlebot', 'bingbot', 'slurp', 'duckduckbot', 'baiduspider',
    'uptimerobot', 'pingdom', 'render',
    'mercadopago', 'mercadolibre',  # Payment webhooks
]

# Valid routes that should NEVER trigger scan detection
VALID_ROUTE_PREFIXES = [
    '/', '/login', '/subscribe', '/admin', '/payment',
    '/api/', '/webhook/', '/static/', '/favicon.ico',
]


def _is_scanner_ua(ua):
    """Check if user agent belongs to a scanner, respecting whitelist."""
    ua_lower = ua.lower()
    # Whitelist check first
    if any(w in ua_lower for w in WHITELISTED_UA_PATTERNS):
        return False
    # Then check scanner patterns
    return any(s in ua_lower for s in SCANNER_USER_AGENTS)


def _has_attack_payload(text):
    """Check if text contains attack patterns (SQLi, XSS, traversal, etc.)."""
    for pattern in ATTACK_PATTERNS:
        if pattern.search(text):
            return True
    return False


def _has_suspicious_extension(path):
    """Check if the path ends with a suspicious file extension."""
    lower_path = path.lower()
    return any(lower_path.endswith(ext) for ext in BLOCKED_EXTENSIONS)


def _is_valid_route(path):
    """Check if path looks like a legitimate route on our app."""
    return any(path == prefix or path.startswith(prefix) for prefix in VALID_ROUTE_PREFIXES)


# ============================================================
# GLOBAL REQUEST SHIELD — before_request middleware
# ============================================================

def register_security_middleware(app):
    """Register global security middleware on the Flask app."""
    
    @app.before_request
    def security_gate():
        ip = _get_client_ip()
        path = request.path
        
        # ─── LAYER 1: IP Blacklist ───
        if ip_blocker.is_blocked(ip):
            return jsonify({
                "status": "error",
                "message": "Acesso temporariamente bloqueado."
            }), 403
        
        # ─── LAYER 2: Global Rate Limit (120 req/min) ───
        key = f"global:{ip}"
        limited, retry_after = limiter.is_rate_limited(key, 120, 60)
        if limited:
            log_rate_limited(ip, f"GLOBAL ({path})")
            return jsonify({"status": "error", "message": "Rate limit excedido."}), 429
        
        # ─── LAYER 3: Scanner User-Agent Detection ───
        ua = request.headers.get('User-Agent', '')
        if not ua:
            # No user agent = likely a script/scanner
            log_scan_detected(ip, "Empty User-Agent")
            limiter.record_hit(f"scan_score:{ip}")
        elif _is_scanner_ua(ua):
            log_scan_detected(ip, f"Scanner UA: {ua[:120]}")
            ip_blocker.block(ip, duration_seconds=86400, reason=f"Scanner UA: {ua[:80]}")
            return jsonify({"status": "error", "message": "Forbidden"}), 403
        
        # ─── LAYER 4: Suspicious File Extensions ───
        if _has_suspicious_extension(path):
            log_scan_detected(ip, f"Suspicious extension: {path}")
            limiter.record_hit(f"scan_score:{ip}")
            # Don't block immediately, but track as scan behavior
        
        # ─── LAYER 5: Attack Payload Detection ───
        # Check URL path + query string
        full_url = request.url
        if _has_attack_payload(full_url):
            log_scan_detected(ip, f"Attack payload in URL: {full_url[:200]}")
            ip_blocker.block(ip, duration_seconds=14400, reason="Attack payload in URL")
            return jsonify({"status": "error", "message": "Forbidden"}), 403
        
        # Check POST body for attacks
        if request.method == 'POST' and request.content_type and 'json' in request.content_type:
            try:
                raw = request.get_data(as_text=True)
                if len(raw) > 50000:  # 50KB max payload
                    log_scan_detected(ip, f"Oversized payload: {len(raw)} bytes")
                    return jsonify({"status": "error", "message": "Payload too large"}), 413
                if _has_attack_payload(raw):
                    log_scan_detected(ip, f"Attack payload in body")
                    ip_blocker.block(ip, duration_seconds=14400, reason="Attack payload in body")
                    return jsonify({"status": "error", "message": "Forbidden"}), 403
            except Exception:
                pass
        
        # ─── LAYER 6: 404 Flood Detection (Scanner Fingerprint) ───
        # Scanners generate lots of 404s rapidly — track and block
        # (This is tracked in after_request via _track_404)
        scan_score = limiter.get_count(f"scan_score:{ip}", 120)  # hits in last 2 min
        if scan_score >= 8:
            log_scan_detected(ip, f"Scan score {scan_score} — auto-blocking")
            ip_blocker.block(ip, duration_seconds=14400, reason=f"High scan score: {scan_score}")
            return jsonify({"status": "error", "message": "Forbidden"}), 403
        
        # ─── LAYER 7: Method Validation ───
        allowed_methods = {'GET', 'POST', 'HEAD', 'OPTIONS', 'PUT', 'DELETE'}
        if request.method not in allowed_methods:
            log_scan_detected(ip, f"Invalid method: {request.method}")
            return jsonify({"status": "error", "message": "Method not allowed"}), 405
    
    @app.after_request
    def track_scan_behavior(response):
        """Track 404s to detect directory enumeration / scanning."""
        if response.status_code == 404:
            ip = _get_client_ip()
            path = request.path
            
            # Don't count legitimate missed routes (like favicon, static assets)
            if not path.startswith('/static/') and path != '/favicon.ico':
                limiter.record_hit(f"scan_score:{ip}")
                
                # Log the 404 for analysis
                scan_count = limiter.get_count(f"scan_score:{ip}", 120)
                if scan_count >= 5:
                    log_scan_detected(ip, f"404 flood ({scan_count} in 2min): {path}")
        
        return response


# ============================================================
# UTILITIES
# ============================================================

def _get_client_ip():
    """Get client IP, respecting reverse proxy headers."""
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    real_ip = request.headers.get('X-Real-IP', '')
    if real_ip:
        return real_ip.strip()
    return request.remote_addr or '0.0.0.0'


def get_security_report():
    """Returns a dict summarizing current security state (for admin panel)."""
    with ip_blocker._lock:
        now = time.time()
        active_blocks = {ip: t for ip, t in ip_blocker._blocked.items() if t > now}
        blocked_count = len(active_blocks)
        blocked_ips = list(active_blocks.keys())[:10]
    
    with limiter._lock:
        tracked_keys = len(limiter._store)
    
    recent_events = []
    try:
        if os.path.exists(SECURITY_LOG):
            with open(SECURITY_LOG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_events = [l.strip() for l in lines[-30:]]
    except Exception:
        pass
    
    return {
        "blocked_ips_count": blocked_count,
        "blocked_ips_sample": blocked_ips,
        "tracked_rate_limit_keys": tracked_keys,
        "recent_events": recent_events
    }


