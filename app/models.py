from datetime import datetime, timezone
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    failed_logins = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    quotes = db.relationship('Quote', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.now(timezone.utc):
            return True
        return False


class HouseType(db.Model):
    __tablename__ = 'house_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    finish_level = db.Column(db.String(20))  # popular, intermedio, lujo
    color = db.Column(db.String(20), default='#3b82f6')
    icon = db.Column(db.String(50), default='bi-house')
    components = db.relationship('Component', backref='house_type', lazy=True)
    quotes = db.relationship('Quote', backref='house_type', lazy=True)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50), default='bi-tools')
    components = db.relationship('Component', backref='category', lazy=True)


class Component(db.Model):
    __tablename__ = 'components'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    house_type_id = db.Column(db.Integer, db.ForeignKey('house_types.id'), nullable=True)  # NULL = todos
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(20), default='global')
    unit_price = db.Column(db.Float, nullable=False)
    is_required = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    default_quantity = db.Column(db.Float, default=1.0)
    group_name = db.Column(db.String(100), nullable=True)  # solo se elige 1 del grupo
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    house_type_id = db.Column(db.Integer, db.ForeignKey('house_types.id'), nullable=False)
    name = db.Column(db.String(200), default='Mi Cotización')
    land_m2 = db.Column(db.Float, default=120.0)
    construction_m2 = db.Column(db.Float, default=80.0)
    subtotal = db.Column(db.Float, default=0.0)
    supervision_pct = db.Column(db.Float, default=15.0)
    supervision_amount = db.Column(db.Float, default=0.0)
    contingency_pct = db.Column(db.Float, default=10.0)
    contingency_amount = db.Column(db.Float, default=0.0)
    total_price = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, final
    floorplan_image_b64 = db.Column(db.Text, nullable=True)  # imagen DALL-E en base64
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    items = db.relationship('QuoteItem', backref='quote', lazy=True, cascade='all, delete-orphan')


class QuoteItem(db.Model):
    __tablename__ = 'quote_items'
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    component = db.relationship('Component')
