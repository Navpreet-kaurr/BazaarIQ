from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import hashlib
import time
import os
import json

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create Flask app for Vercel serverless
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, '..', 'templates'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_change_in_production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize database with error handling for Vercel's read-only filesystem
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Database init warning: {e}")

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, default=0)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='orders')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if not name or not email or not password:
            flash('All fields are required')
            return render_template('register.html')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered')
            return render_template('register.html')
            
        hashed_password = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash('Registered and logged in successfully!')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        category = request.form.get('category')
        stock = request.form.get('stock')
        
        if not name or not price or not category or not stock:
            flash('All fields are required')
            return render_template('products.html', products=Product.query.all())
        
        product = Product(name=name, price=float(price), category=category, stock=int(stock))
        db.session.add(product)
        db.session.commit()
        flash('Product added!')
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/delete_product/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!')
    return redirect(url_for('products'))

@app.route('/cart/add/<int:product_id>')
@login_required
def add_to_cart(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id)
        db.session.add(cart_item)
    db.session.commit()
    flash('Added to cart!')
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/cart/decrement/<int:id>')
@login_required
def decrement_cart(id):
    item = Cart.query.get_or_404(id)
    if item.quantity > 1:
        item.quantity -= 1
        db.session.commit()
    else:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:id>')
@login_required
def remove_from_cart(id):
    item = Cart.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/orders', methods=['POST'])
@login_required
def place_order():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Cart empty!')
        return redirect(url_for('cart'))
    
    total = sum(item.product.price * item.quantity for item in items)
    order = Order(user_id=current_user.id, total_price=total)
    db.session.add(order)
    db.session.flush()
    
    for item in items:
        order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity)
        db.session.add(order_item)
        product = Product.query.get(item.product_id)
        if product:
            product.stock -= item.quantity
    
    db.session.query(Cart).filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Order placed!')
    return redirect(url_for('orders_list'))

@app.route('/orders_list')
@login_required
def orders_list():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/dashboard')
@login_required
def dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    
    return render_template('dashboard.html', 
                         total_users=total_users, 
                         total_products=total_products,
                         total_orders=total_orders, 
                         revenue=revenue, 
                         logs=[],
                         category_indexed=False)

# Export app for Vercel - app is already defined as the Flask instance above
# Vercel's @vercel/python runtime expects 'app' to be available

# Optional: Keep handler for backwards compatibility with some Vercel setups
def handler(event, context):
    """Vercel serverless handler"""
    return app
