import data_fetcher
import ai_engine
# user_manager deprecated - replaced by payment_system
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import time
import datetime
import requests
import traceback
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

# --- ROUTES ---

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
    updates = data_fetcher.get_games_for_date(date)
    return jsonify(updates)

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
    data = data_fetcher.get_today_scout()
    return jsonify(data)

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
