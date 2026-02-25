import data_fetcher
import result_checker
import ai_engine
# user_manager deprecated - replaced by payment_system
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import time
import datetime
import requests
import traceback
import threading
import importlib
# Payment System Integration
from payment_system import init_payment_system, db, User, Payment, PaymentManager

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# --- INITIALIZE PAYMENT SYSTEM ---
init_payment_system(app)

# Login Manager Setup
login_manager = LoginManager()
login_manager.login_view = 'login_page'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Mercado Pago SDK
mp_manager = PaymentManager(os.getenv('MP_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN_HERE'))

# --- MIDDLEWARE & SECURITY ---
@app.before_request
def start_timer():
    g.start = time.time()

@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    diff = time.time() - g.start
    response.headers['X-Neural-Latency'] = f"{diff:.4f}s"
    if request.path.startswith('/api'):
        # TURBO: Allow short browser caching for read-only data endpoints
        cacheable_endpoints = ['/api/games', '/api/history', '/api/history_stats', 
                               '/api/today_scout', '/api/history_trebles', '/api/leverage']
        if any(request.path.startswith(ep) for ep in cacheable_endpoints) and request.method == 'GET':
            response.headers['Cache-Control'] = 'public, max-age=300, stale-while-revalidate=600'
        else:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api'):
        return jsonify({"status": "error", "message": "Endpoint Neural não encontrado"}), 404
    return render_template('index.html'), 200

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"status": "critical_error", "message": "Falha no Núcleo de Processamento", "details": str(e)}), 500

# --- JOB AUTOMATION ---

def run_update_job():
    """Runs the daily update in a background thread."""
    print("⏳ Starting Background Update Job...")
    try:
        # Re-import to ensure fresh execution context
        # We need to run the actual script logic.
        # Ideally, we call data_fetcher directly to populate files
        # AND THEN sync to cloud if needed.
        
        # HACK: Execute the existing script file as a subprocess or import logic
        # Using import logic is safer for memory in this context but script relies on __main__
        # Let's use data_fetcher directly to refresh cache
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"🔄 Refreshing data for {today}...")
        data_fetcher.get_games_for_date(today, force_refresh=True)
        print("✅ Data Fetcher Complete.")
        
        # Auto-check results from ESPN
        print("🔍 Checking game results via ESPN...")
        result_summary = result_checker.check_and_update_results()
        print(f"✅ Result Check Complete: {result_summary}")
        
        print("✅ Background Update Job All Done.")
    except Exception as e:
        print(f"❌ Background Update Job Failed: {e}")
        traceback.print_exc()

@app.route('/api/cron/update', methods=['GET', 'POST'])
def cron_update():
    """
    Trigger this endpoint to start the daily update process asynchronously.
    Perfect for cron-job.org or other schedulers.
    """
    key = request.args.get('key')
    authorized_key = os.environ.get('CRON_KEY', 'update_secret_123')
    
    if key != authorized_key:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    # Run in thread to avoid timeout
    thread = threading.Thread(target=run_update_job)
    thread.start()
    
    return jsonify({
        "status": "accepted", 
        "message": "Update process started in background.", 
        "timestamp": datetime.datetime.now().isoformat()
    }), 202

@app.route('/api/cron/results', methods=['GET', 'POST'])
def cron_results():
    """Dedicated endpoint to check & update game results from ESPN."""
    key = request.args.get('key')
    authorized_key = os.environ.get('CRON_KEY', 'update_secret_123')
    if key != authorized_key:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    try:
        summary = result_checker.check_and_update_results()
        return jsonify({"status": "ok", **summary})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- DEBUG ENDPOINT (admin only) ---
@app.route('/api/debug')
@login_required
def debug_endpoint():
    """Internal diagnostics — admin only."""    
    if getattr(current_user, 'role', 'user') != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    results = {"status": "running", "checks": {}}
    
    # Check 1: Can we import data_fetcher?
    try:
        import data_fetcher as df
        results["checks"]["import"] = "OK"
    except Exception as e:
        results["checks"]["import"] = f"FAIL: {e}"
        return jsonify(results)
    
    # Check 2: Can we call get_games_for_date?
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        data = df.get_games_for_date(today)
        results["checks"]["get_games"] = f"OK - {len(data.get('games', []))} games found"
        results["data_keys"] = list(data.keys()) if isinstance(data, dict) else str(type(data))
    except Exception as e:
        results["checks"]["get_games"] = f"FAIL: {e}"
        results["traceback"] = traceback.format_exc()
    
    # Check 3: Can we call get_history_games?
    try:
        hist = df.get_history_games()
        results["checks"]["history"] = f"OK - {len(hist)} entries"
    except Exception as e:
        results["checks"]["history"] = f"FAIL: {e}"
    
    # Check 4: Can we call get_today_scout?
    try:
        scout = df.get_today_scout()
        results["checks"]["scout"] = f"OK - {scout}"
    except Exception as e:
        results["checks"]["scout"] = f"FAIL: {e}"
    
    return jsonify(results)

# --- ROUTES ---

# --- ADMIN ROUTES ---

@app.route('/admin')
@login_required
def admin_dashboard():
    # Role check
    if getattr(current_user, 'role', 'user') != 'admin':
        return "Acesso Negado: Requer privilégios de Administrador.", 403
        
    users = User.query.all()
    active_count = 0
    expired_count = 0
    
    # Process user data for template
    processed_users = []
    now = datetime.datetime.utcnow()
    
    for u in users:
        is_active = False
        days_left = 0
        
        if u.role == 'admin':
            is_active = True
            days_left = 9999
        elif u.subscription_end and u.subscription_end > now:
            is_active = True
            delta = u.subscription_end - now
            days_left = delta.days
        else:
            is_active = False
            days_left = 0
            
        if is_active:
            active_count += 1
        else:
            expired_count += 1
            
        # Attach temporary attributes for template rendering
        # (We can't modify the SQLAlch object directly easily, so we use a wrapper or just setattr if it allows)
        setattr(u, 'subscription_active', is_active)
        setattr(u, 'days_left', days_left)
        processed_users.append(u)
        
    return render_template('admin.html', users=processed_users, active_count=active_count, expired_count=expired_count)

@app.route('/admin/renew/<int:user_id>', methods=['POST'])
@login_required
def admin_renew_user(user_id):
    if getattr(current_user, 'role', 'user') != 'admin':
        return "Acesso Negado", 403
        
    user = User.query.get(user_id)
    if not user:
        return "Usuário não encontrado", 404
        
    # Renew for 7 days from NOW
    user.subscription_end = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    db.session.commit()
    
    return redirect('/admin')


# /promote_me removido por segurança — era um backdoor de admin

@app.route('/')
@login_required # Protect Home
def home():
    if not current_user.is_active_subscriber:
        return redirect(url_for('subscription_page'))
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        return redirect('/')
    return render_template('login.html')

@app.route('/subscribe', methods=['GET'])
@login_required
def subscription_page():
    if current_user.is_active_subscriber:
        return redirect('/')
    return render_template('subscribe.html')

# --- API ENDPOINTS (DATA) ---

@app.route('/api/games')
@login_required
def games():
    if not current_user.is_active_subscriber: return jsonify({"error": "Subscription Required"}), 403
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    date = request.args.get('date', today)
    try:
        updates = data_fetcher.get_games_for_date(date)
        return jsonify(updates)
    except Exception as e:
        print(f"CRITICAL ERROR /api/games: {e}")
        import traceback
        traceback.print_exc()
        # Return empty safe structure
        return jsonify({
            "games": [], 
            "trebles": [], 
            "status": "error", 
            "message": str(e)
        })

@app.route('/api/history')
@login_required
def history():
    if not current_user.is_active_subscriber: return jsonify({"error": "Subscription Required"}), 403
    data = data_fetcher.get_history_games()
    return jsonify(data)

@app.route('/api/history_stats')
@login_required
def history_stats():
    if not current_user.is_active_subscriber: return jsonify({"error": "Subscription Required"}), 403
    data = data_fetcher.get_history_stats()
    return jsonify(data)

@app.route('/api/today_scout')
@login_required
def today_scout():
    if not current_user.is_active_subscriber: return jsonify({"error": "Subscription Required"}), 403
    try:
        scout = data_fetcher.get_today_scout()
        return jsonify(scout)
    except Exception as e:
        print(f"CRITICAL ERROR /api/today_scout: {e}")
        return jsonify({
            "total": 0, "greens": 0, "reds": 0, "pending": 0, "accuracy": 0
        })

@app.route('/api/history_trebles')
@login_required
def history_trebles():
    if not current_user.is_active_subscriber: return jsonify({"error": "Subscription Required"}), 403
    data = data_fetcher.get_history_trebles()
    return jsonify(data)

@app.route('/api/analyze')
@login_required
def analyze():
    if not current_user.is_active_subscriber: return jsonify({"error": "Subscription Required"}), 403
    game_id = request.args.get('id')
    analysis = ai_engine.analyze_match(game_id)
    return jsonify(analysis)

@app.route('/api/leverage')
@login_required
def leverage():
    if not current_user.is_active_subscriber: return jsonify({"error": "Subscription Required"}), 403
    data = data_fetcher.get_leverage_plan()
    return jsonify(data)

# --- AUTH & PAYMENT ENDPOINTS ---

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            "status": "success", 
            "message": "Login realizado", 
            "user": {"email": user.email, "is_active": user.is_active_subscriber}
        })
    return jsonify({"status": "error", "message": "Credenciais inválidas"}), 401

@app.route('/api/register', methods=['POST'])
def register_api():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email já cadastrado"}), 409
        
    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user) # Auto login after register
    
    return jsonify({"status": "success", "message": "Conta criada! Assine para acessar.", "redirect": "/subscribe"})

@app.route('/api/logout')
@login_required
def logout_api():
    logout_user()
    return jsonify({"status": "success", "message": "Logout realizado"})

@app.route('/api/check_session')
def check_session():
    if current_user.is_authenticated:
        return jsonify({
            "logged_in": True, 
            "user": current_user.email, 
            "is_valid": current_user.is_active_subscriber,
            "is_admin": (current_user.role == 'admin')
        })
    return jsonify({"logged_in": False})

# --- PAYMENT FLOW ---

@app.route('/api/payment/create', methods=['POST'])
@login_required
def create_payment():
    try:
        mp_token = os.getenv('MP_ACCESS_TOKEN', '')
        if not mp_token or 'YOUR_' in mp_token:
            raise Exception("MP_ACCESS_TOKEN is missing or invalid in environment")

        print(f"💰 Creating preference for: {current_user.email}")
        preference = mp_manager.create_preference(current_user.email)
        
        # Check if Preference response is valid
        if 'id' not in preference:
             raise Exception(f"Invalid MP Response: {preference}")

        return jsonify({"status": "success", "preference_id": preference['id'], "init_point": preference['init_point']})
    except Exception as e:
        print(f"❌ Payment Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500

@app.route('/webhook/mercadopago', methods=['POST', 'GET'], strict_slashes=False)
def mp_webhook():
    print(f"🔔 Webhook received: {request.method} {request.url}")
    
    topic = request.args.get('topic') or request.args.get('type')
    p_id = request.args.get('id') or request.args.get('data.id')

    if topic == 'payment' and p_id:
        print(f"🔎 Checking payment {p_id}...")
        try:
            payment_info = mp_manager.check_payment_status(p_id)
            print(f"💳 Status: {payment_info['status']}")
            
            if payment_info['status'] == 'approved':
                payer_email = payment_info['payer']['email']
                # Try to match by email first
                user = User.query.filter_by(email=payer_email).first()
                if user:
                    # Upgrade Subscription
                    user.subscription_end = datetime.datetime.utcnow() + datetime.timedelta(days=7)
                    db.session.commit()
                    print(f"✅ Subscription ACTIVATED for {user.email}")
                else:
                    print(f"⚠️ User not found for email {payer_email}")
        except Exception as e:
            print(f"❌ Webhook Processing Error: {e}")
            return jsonify({"status": "error", "error": str(e)}), 500
                
    return jsonify({"status": "ok"}), 200

@app.route('/payment/success')
def payment_success():
    return render_template('payment_success.html')

@app.route('/payment/failure')
def payment_failure():
    return render_template('payment_failure.html')

@app.route('/payment/pending')
def payment_pending():
    return render_template('payment_pending.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
