
from datetime import datetime, timedelta
import mercadopago
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize extensions (will be bound to app in app.py)
db = SQLAlchemy()

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    subscription_end = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String(20), default='user') # 'admin', 'user'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active_subscriber(self):
        """Checks if subscription is active."""
        if self.role == 'admin': return True
        if not self.subscription_end: return False
        return self.subscription_end > datetime.utcnow()

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mp_payment_id = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20)) # pending, approved, rejected
    amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Payment Logic
class PaymentManager:
    def __init__(self, access_token):
        self.sdk = mercadopago.SDK(access_token)
        
    def create_preference(self, user_email):
        """Creates a payment preference for 1 week access."""
        preference_data = {
            "items": [
                {
                    "title": "Acesso VIP - Bot Probability (7 Dias)",
                    "quantity": 1,
                    "unit_price": 29.90,
                    "currency_id": "BRL"
                }
            ],
            "payer": {
                "email": user_email
            },
            "back_urls": {
                "success": f"{os.getenv('BASE_URL', 'http://localhost:5000')}/payment/success",
                "failure": f"{os.getenv('BASE_URL', 'http://localhost:5000')}/payment/failure",
                "pending": f"{os.getenv('BASE_URL', 'http://localhost:5000')}/payment/pending"
            },
            "auto_return": "approved",
            "notification_url": f"{os.getenv('BASE_URL', 'http://localhost:5000')}/webhook/mercadopago" 
        }
        
        preference_response = self.sdk.preference().create(preference_data)
        return preference_response["response"]

    def check_payment_status(self, payment_id):
        payment_info = self.sdk.payment().get(payment_id)
        return payment_info["response"]

def init_payment_system(app):
    """Initializes DB and Payment System with Flask App"""
    # Use Postgres from Supabase if available in ENV, otherwise fallback to local SQLite
    db_url = os.environ.get('SUPABASE_DB_URL', 'sqlite:///users.db')
    # If the URL starts with postgres://, SQLAlchemy requires it to be postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_change_in_prod')
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not User.query.filter_by(role='admin').first():
            print("Creating default admin...")
            admin = User(email='admin@bot.com', role='admin', subscription_end=datetime.utcnow() + timedelta(days=36500))
            admin.set_password('admin123') # CHANGE THIS PASSWORD IMMEDIATELY
            db.session.add(admin)
            db.session.commit()
