from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from functools import wraps
import json
import os

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # owner, manager, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    product = db.relationship('Product', backref=db.backref('purchases', lazy=True))

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    product = db.relationship('Product', backref=db.backref('sales', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Language dictionaries
LANGUAGES = {
    'en': {
        'dashboard': 'Dashboard',
        'products': 'Products',
        'purchases': 'Purchases', 
        'sales': 'Sales',
        'reports': 'Reports',
        'users': 'Users',
        'staff_activities': 'Staff Activities',
        'search_products': 'Search Products',
        'change_password': 'Change Password',
        'logout': 'Logout',
        'welcome': 'Welcome',
        'total_products': 'Total Products',
        'low_stock_alert': 'Low Stock Alert',
        'todays_revenue': 'Today\'s Revenue',
        'my_todays_sales': 'My Today\'s Sales',
        'recent_sales': 'Recent Sales',
        'recent_purchases': 'Recent Purchases',
        'my_recent_sales': 'My Recent Sales',
        'view_products': 'View Products',
        'record_purchase': 'Record Purchase',
        'make_sale': 'Make Sale',
        'view_reports': 'View Reports',
        'my_reports': 'My Reports',
        'manage_products': 'Manage Products',
        'add_product': 'Add Product',
        'edit_product': 'Edit Product',
        'delete_product': 'Delete Product',
        'product_name': 'Product Name',
        'description': 'Description',
        'purchase_price': 'Purchase Price',
        'selling_price': 'Selling Price',
        'stock_quantity': 'Stock Quantity',
        'min_stock': 'Min Stock',
        'actions': 'Actions',
        'record_bulk_purchase': 'Record Bulk Purchase',
        'quantity': 'Quantity',
        'unit_price': 'Unit Price',
        'total_amount': 'Total Amount',
        'date': 'Date',
        'time': 'Time',
        'insufficient_stock': 'Insufficient Stock',
        'record_sale': 'Record Sale',
        'login': 'Login',
        'username': 'Username',
        'password': 'Password',
        'current_password': 'Current Password',
        'new_password': 'New Password',
        'confirm_password': 'Confirm Password',
        'add_user': 'Add User',
        'role': 'Role',
        'staff': 'Staff',
        'manager': 'Manager',
        'owner': 'Owner',
        'created_date': 'Created Date',
        'low_stock_warning': 'Low Stock Warning',
        'need_restock': 'Need Restock',
        'sales_report': 'Sales Report',
        'purchases_report': 'Purchases Report',
        'total_sales': 'Total Sales',
        'total_purchases': 'Total Purchases',
        'total_profit': 'Total Profit',
        'low_stock_items': 'Low Stock Items',
        'sales_analytics': 'Sales Analytics',
        'purchase_analytics': 'Purchase Analytics',
        'top_products': 'Top Products',
        'quantity_sold': 'Quantity Sold',
        'revenue': 'Revenue',
        'quantity_bought': 'Quantity Bought',
        'total_cost': 'Total Cost',
        'staff_monitoring': 'Staff Monitoring',
        'today_sales': 'Today\'s Sales',
        'total_revenue': 'Total Revenue',
        'performance': 'Performance',
        'excellent': 'Excellent',
        'good': 'Good',
        'average': 'Average',
        'no_sales': 'No Sales',
        'average_sale': 'Average Sale',
        'filter_by_date': 'Filter by Date',
        'today': 'Today',
        'success_added': 'added successfully!',
        'success_updated': 'updated successfully!',
        'success_deleted': 'deleted successfully!',
        'success_recorded': 'recorded successfully!',
        'success_changed': 'changed successfully!',
        'invalid_login': 'Invalid username or password',
        'access_denied': 'Access denied!',
        'owner_required': 'Owner privileges required.',
        'manager_required': 'Manager or Owner privileges required.',
        'product': 'Product',
        'purchase': 'Purchase',
        'sale': 'Sale',
        'user': 'User',
        'password_changed': 'Password changed successfully!',
        'current_password_incorrect': 'Current password is incorrect!',
        'passwords_not_match': 'New passwords do not match!',
        'cannot_delete_own_account': 'You cannot delete your own account!'
    },
    'sw': {
        'dashboard': 'Dashibodi',
        'products': 'Bidhaa',
        'purchases': 'Ununuzi',
        'sales': 'Mauzo',
        'reports': 'Ripoti',
        'users': 'Watumiaji',
        'staff_activities': 'Shughuli za Wafanyikazi',
        'search_products': 'Tafuta Bidhaa',
        'change_password': 'Badilisha Nenosiri',
        'logout': 'Toka',
        'welcome': 'Karibu',
        'total_products': 'Jumla ya Bidhaa',
        'low_stock_alert': 'Taarifa ya Hisa Ndogo',
        'todays_revenue': 'Mapato ya Leo',
        'my_todays_sales': 'Mauzo Yangu ya Leo',
        'recent_sales': 'Mauzo ya Hivi Karibuni',
        'recent_purchases': 'Ununuzi wa Hivi Karibuni',
        'my_recent_sales': 'Mauzo Yangu ya Hivi Karibuni',
        'view_products': 'Angalia Bidhaa',
        'record_purchase': 'Rekodi Ununuzi',
        'make_sale': 'Fanya Mauzo',
        'view_reports': 'Angalia Ripoti',
        'my_reports': 'Ripoti Zangu',
        'manage_products': 'Dhibiti Bidhaa',
        'add_product': 'Ongeza Bidhaa',
        'edit_product': 'Hariri Bidhaa',
        'delete_product': 'Futa Bidhaa',
        'product_name': 'Jina la Bidhaa',
        'description': 'Maelezo',
        'purchase_price': 'Bei ya Ununuzi',
        'selling_price': 'Bei ya Kuuza',
        'stock_quantity': 'Idadi ya Hisa',
        'min_stock': 'Hisa Ndogo',
        'actions': 'Vitendo',
        'record_bulk_purchase': 'Rekodi Ununuzi Mkubwa',
        'quantity': 'Idadi',
        'unit_price': 'Bei ya Kimoja',
        'total_amount': 'Jumla ya Kiasi',
        'date': 'Tarehe',
        'time': 'Muda',
        'insufficient_stock': 'Hisa Haitoshi',
        'record_sale': 'Rekodi Mauzo',
        'login': 'Ingia',
        'username': 'Jina la Mtumiaji',
        'password': 'Nenosiri',
        'current_password': 'Nenosiri la Sasa',
        'new_password': 'Nenosiri Jipya',
        'confirm_password': 'Thibitisha Nenosiri',
        'add_user': 'Ongeza Mtumiaji',
        'role': 'Wajibu',
        'staff': 'Mfanyakazi',
        'manager': 'Meneja',
        'owner': 'Mmiliki',
        'created_date': 'Tarehe ya Uundaji',
        'low_stock_warning': 'Onyo la Hisa Ndogo',
        'need_restock': 'Inahitaji Kujazwa Tena',
        'sales_report': 'Ripoti ya Mauzo',
        'purchases_report': 'Ripoti ya Ununuzi',
        'total_sales': 'Jumla ya Mauzo',
        'total_purchases': 'Jumla ya Ununuzi',
        'total_profit': 'Jumla ya Faida',
        'low_stock_items': 'Bidhaa zenye Hisa Ndogo',
        'sales_analytics': 'Uchambuzi wa Mauzo',
        'purchase_analytics': 'Uchambuzi wa Ununuzi',
        'top_products': 'Bidhaa Bora',
        'quantity_sold': 'Idadi Iliyouzwa',
        'revenue': 'Mapato',
        'quantity_bought': 'Idadi Iliyonunuliwa',
        'total_cost': 'Jumla ya Gharama',
        'staff_monitoring': 'Ufuatiliaji wa Wafanyikazi',
        'today_sales': 'Mauzo ya Leo',
        'total_revenue': 'Jumla ya Mapato',
        'performance': 'Utendaji',
        'excellent': 'Bora Sana',
        'good': 'Nzuri',
        'average': 'Wastani',
        'no_sales': 'Hakuna Mauzo',
        'average_sale': 'Wastani wa Mauzo',
        'filter_by_date': 'Chuja kwa Tarehe',
        'today': 'Leo',
        'success_added': 'imeongezwa kikamilifu!',
        'success_updated': 'imesasishwa kikamilifu!',
        'success_deleted': 'imefutwa kikamilifu!',
        'success_recorded': 'imerekodiwa kikamilifu!',
        'success_changed': 'imebadilishwa kikamilifu!',
        'invalid_login': 'Jina la mtumiaji au nenosiri batili',
        'access_denied': 'Ufikiaji umekataliwa!',
        'owner_required': 'Haki za mmiliki zinahitajika.',
        'manager_required': 'Haki za Meneja au Mmiliki zinahitajika.',
        'product': 'Bidhaa',
        'purchase': 'Ununuzi',
        'sale': 'Mauzo',
        'user': 'Mtumiaji',
        'password_changed': 'Nenosiri limebadilishwa kikamilifu!',
        'current_password_incorrect': 'Nenosiri la sasa si sahihi!',
        'passwords_not_match': 'Nenosiri jipya halifanani!',
        'cannot_delete_own_account': 'Huwezi kufuta akaunti yako mwenyewe!'
    }
}

@app.before_request
def before_request():
    # Set default language to English if not set
    if 'language' not in session:
        session['language'] = 'en'
    g.language = session['language']
    g.languages = LANGUAGES

def get_text(key):
    """Helper function to get text in current language"""
    return LANGUAGES.get(g.language, {}).get(key, key)

# Role-based access control decorators
def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'owner':
            flash(get_text('access_denied') + ' ' + get_text('owner_required'))
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def manager_or_owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['owner', 'manager']:
            flash(get_text('access_denied') + ' ' + get_text('manager_required'))
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Format currency as TZS
def format_currency(amount):
    return "TZS {:,.0f}".format(amount)

# Add to template context
@app.context_processor
def utility_processor():
    return dict(format_currency=format_currency, get_text=get_text, current_language=g.language)

@app.route('/change_language/<lang>')
@login_required
def change_language(lang):
    if lang in ['en', 'sw']:
        session['language'] = lang
    return redirect(request.referrer or url_for('dashboard'))

# Routes
@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash(get_text('invalid_login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash(get_text('current_password_incorrect'))
            return redirect(url_for('change_password'))
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash(get_text('passwords_not_match'))
            return redirect(url_for('change_password'))
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash(get_text('password_changed'))
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Dashboard statistics
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.stock_quantity <= Product.min_stock).count()
    
    # Today's sales - different calculation for staff
    today = date.today()
    
    if current_user.role == 'staff':
        # Staff only see their own sales
        today_sales = Sale.query.filter(
            Sale.user_id == current_user.id,
            db.func.date(Sale.sale_date) == today
        ).all()
        recent_sales = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.sale_date.desc()).limit(5).all()
        recent_purchases = []  # Staff don't see purchases
    else:
        # Managers and owners see all data
        today_sales = Sale.query.filter(db.func.date(Sale.sale_date) == today).all()
        recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(5).all()
        recent_purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).limit(5).all()
    
    today_revenue = sum(sale.total_amount for sale in today_sales)
    
    return render_template('dashboard.html', 
                         total_products=total_products,
                         low_stock=low_stock,
                         today_revenue=today_revenue,
                         recent_sales=recent_sales,
                         recent_purchases=recent_purchases)

@app.route('/products')
@login_required
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/add_product', methods=['POST'])
@login_required
@manager_or_owner_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        purchase_price = float(request.form['purchase_price'])
        selling_price = float(request.form['selling_price'])
        stock_quantity = int(request.form['stock_quantity'])
        min_stock = int(request.form['min_stock'])
        
        product = Product(
            name=name,
            description=description,
            purchase_price=purchase_price,
            selling_price=selling_price,
            stock_quantity=stock_quantity,
            min_stock=min_stock
        )
        
        db.session.add(product)
        db.session.commit()
        flash(get_text('product') + ' ' + get_text('success_added'))
    
    return redirect(url_for('products'))

@app.route('/edit_product/<int:id>', methods=['POST'])
@login_required
@manager_or_owner_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.purchase_price = float(request.form['purchase_price'])
        product.selling_price = float(request.form['selling_price'])
        product.stock_quantity = int(request.form['stock_quantity'])
        product.min_stock = int(request.form['min_stock'])
        
        db.session.commit()
        flash(get_text('product') + ' ' + get_text('success_updated'))
    
    return redirect(url_for('products'))

@app.route('/delete_product/<int:id>')
@login_required
@manager_or_owner_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash(get_text('product') + ' ' + get_text('success_deleted'))
    return redirect(url_for('products'))

@app.route('/buying')
@login_required
@manager_or_owner_required
def buying():
    products = Product.query.all()
    purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    return render_template('buying.html', products=products, purchases=purchases)

@app.route('/add_purchase', methods=['POST'])
@login_required
@manager_or_owner_required
def add_purchase():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        total_amount = quantity * unit_price
        
        purchase = Purchase(
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            user_id=current_user.id
        )
        
        # Update product stock
        product = Product.query.get(product_id)
        product.stock_quantity += quantity
        
        db.session.add(purchase)
        db.session.commit()
        flash(get_text('purchase') + ' ' + get_text('success_recorded'))
    
    return redirect(url_for('buying'))

@app.route('/sales')
@login_required
def sales():
    products = Product.query.filter(Product.stock_quantity > 0).all()
    sales_list = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('sales.html', products=products, sales=sales_list)

@app.route('/add_sale', methods=['POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        
        product = Product.query.get(product_id)
        
        if product.stock_quantity < quantity:
            flash(get_text('insufficient_stock'))
            return redirect(url_for('sales'))
        
        unit_price = product.selling_price
        total_amount = quantity * unit_price
        
        sale = Sale(
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            user_id=current_user.id
        )
        
        # Update product stock
        product.stock_quantity -= quantity
        
        db.session.add(sale)
        db.session.commit()
        flash(get_text('sale') + ' ' + get_text('success_recorded'))
    
    return redirect(url_for('sales'))

@app.route('/search_products')
@login_required
def search_products():
    query = request.args.get('q', '')
    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    else:
        products = []
    return render_template('search_products.html', products=products, query=query)

@app.route('/daily_summary')
@login_required
def daily_summary():
    today = date.today()
    
    # Today's sales
    today_sales = Sale.query.filter(db.func.date(Sale.sale_date) == today).all()
    today_revenue = sum(sale.total_amount for sale in today_sales)
    total_items_sold = sum(sale.quantity for sale in today_sales)
    
    # Today's purchases
    today_purchases = Purchase.query.filter(db.func.date(Purchase.purchase_date) == today).all()
    today_purchase_cost = sum(purchase.total_amount for purchase in today_purchases)
    
    return render_template('daily_summary.html',
                         today_revenue=today_revenue,
                         total_items_sold=total_items_sold,
                         today_purchase_cost=today_purchase_cost,
                         today_sales=today_sales,
                         today_purchases=today_purchases,
                         today_date=today)

# Reports and Analytics Routes
@app.route('/reports')
@login_required
def reports():
    if current_user.role == 'staff':
        return redirect(url_for('staff_reports'))
    
    # Sales report
    sales_data = Sale.query.all()
    total_sales = sum(sale.total_amount for sale in sales_data)
    
    # Purchase report
    purchases_data = Purchase.query.all()
    total_purchases = sum(purchase.total_amount for purchase in purchases_data)
    
    # Profit calculation
    profit = total_sales - total_purchases
    
    # Low stock products
    low_stock_products = Product.query.filter(Product.stock_quantity <= Product.min_stock).all()
    
    return render_template('reports.html',
                         total_sales=total_sales,
                         total_purchases=total_purchases,
                         profit=profit,
                         low_stock_products=low_stock_products)

@app.route('/api/sales_chart_data')
@login_required
def sales_chart_data():
    if current_user.role == 'staff':
        return jsonify({'labels': [], 'data': [], 'period': 'daily'})
    
    period = request.args.get('period', 'daily')
    
    if period == 'daily':
        # Last 7 days
        dates = [(datetime.now() - timedelta(days=i)).date() for i in range(6, -1, -1)]
        labels = [date.strftime('%a') for date in dates]
        data = []
        for date in dates:
            daily_sales = Sale.query.filter(db.func.date(Sale.sale_date) == date).all()
            total = sum(sale.total_amount for sale in daily_sales)
            data.append(total)
    
    elif period == 'weekly':
        # Last 8 weeks
        labels = []
        data = []
        for i in range(7, -1, -1):
            week_start = datetime.now() - timedelta(weeks=i+1)
            week_end = datetime.now() - timedelta(weeks=i)
            weekly_sales = Sale.query.filter(
                Sale.sale_date >= week_start,
                Sale.sale_date < week_end
            ).all()
            total = sum(sale.total_amount for sale in weekly_sales)
            labels.append(f'W{i+1}')
            data.append(total)
    
    else:  # monthly
        # Last 6 months
        labels = []
        data = []
        for i in range(5, -1, -1):
            month = datetime.now().month - i
            year = datetime.now().year
            if month <= 0:
                month += 12
                year -= 1
            monthly_sales = Sale.query.filter(
                db.extract('year', Sale.sale_date) == year,
                db.extract('month', Sale.sale_date) == month
            ).all()
            total = sum(sale.total_amount for sale in monthly_sales)
            labels.append(f'{month}/{year}')
            data.append(total)
    
    return jsonify({
        'labels': labels,
        'data': data,
        'period': period
    })

@app.route('/api/purchases_chart_data')
@login_required
def purchases_chart_data():
    if current_user.role == 'staff':
        return jsonify({'labels': [], 'data': [], 'period': 'daily'})
    
    period = request.args.get('period', 'daily')
    
    if period == 'daily':
        dates = [(datetime.now() - timedelta(days=i)).date() for i in range(6, -1, -1)]
        labels = [date.strftime('%a') for date in dates]
        data = []
        for date in dates:
            daily_purchases = Purchase.query.filter(db.func.date(Purchase.purchase_date) == date).all()
            total = sum(purchase.total_amount for purchase in daily_purchases)
            data.append(total)
    
    elif period == 'weekly':
        labels = []
        data = []
        for i in range(7, -1, -1):
            week_start = datetime.now() - timedelta(weeks=i+1)
            week_end = datetime.now() - timedelta(weeks=i)
            weekly_purchases = Purchase.query.filter(
                Purchase.purchase_date >= week_start,
                Purchase.purchase_date < week_end
            ).all()
            total = sum(purchase.total_amount for purchase in weekly_purchases)
            labels.append(f'W{i+1}')
            data.append(total)
    
    else:  # monthly
        labels = []
        data = []
        for i in range(5, -1, -1):
            month = datetime.now().month - i
            year = datetime.now().year
            if month <= 0:
                month += 12
                year -= 1
            monthly_purchases = Purchase.query.filter(
                db.extract('year', Purchase.purchase_date) == year,
                db.extract('month', Purchase.purchase_date) == month
            ).all()
            total = sum(purchase.total_amount for purchase in monthly_purchases)
            labels.append(f'{month}/{year}')
            data.append(total)
    
    return jsonify({
        'labels': labels,
        'data': data,
        'period': period
    })

@app.route('/api/sales_analytics')
@login_required
def sales_analytics():
    if current_user.role == 'staff':
        return jsonify({'analytics': [], 'period': 'all'})
    
    period = request.args.get('period', 'all')
    
    # Base query
    query = db.session.query(
        Product.name,
        db.func.sum(Sale.quantity).label('total_quantity'),
        db.func.sum(Sale.total_amount).label('total_revenue')
    ).join(Sale, Product.id == Sale.product_id)
    
    # Apply period filter
    if period == 'daily':
        today = date.today()
        query = query.filter(db.func.date(Sale.sale_date) == today)
    elif period == 'weekly':
        week_ago = datetime.now() - timedelta(days=7)
        query = query.filter(Sale.sale_date >= week_ago)
    elif period == 'monthly':
        month_ago = datetime.now() - timedelta(days=30)
        query = query.filter(Sale.sale_date >= month_ago)
    # 'all' period shows everything
    
    product_sales = query.group_by(Product.id, Product.name)\
                        .order_by(db.desc('total_revenue'))\
                        .all()
    
    analytics = []
    for product in product_sales:
        analytics.append({
            'product_name': product.name,
            'total_quantity': product.total_quantity or 0,
            'total_revenue': product.total_revenue or 0
        })
    
    return jsonify({
        'analytics': analytics,
        'period': period
    })

@app.route('/api/purchases_analytics')
@login_required
def purchases_analytics():
    if current_user.role == 'staff':
        return jsonify({'analytics': [], 'period': 'all'})
    
    period = request.args.get('period', 'all')
    
    # Base query
    query = db.session.query(
        Product.name,
        db.func.sum(Purchase.quantity).label('total_quantity'),
        db.func.sum(Purchase.total_amount).label('total_cost')
    ).join(Purchase, Product.id == Purchase.product_id)
    
    # Apply period filter
    if period == 'daily':
        today = date.today()
        query = query.filter(db.func.date(Purchase.purchase_date) == today)
    elif period == 'weekly':
        week_ago = datetime.now() - timedelta(days=7)
        query = query.filter(Purchase.purchase_date >= week_ago)
    elif period == 'monthly':
        month_ago = datetime.now() - timedelta(days=30)
        query = query.filter(Purchase.purchase_date >= month_ago)
    # 'all' period shows everything
    
    product_purchases = query.group_by(Product.id, Product.name)\
                            .order_by(db.desc('total_cost'))\
                            .all()
    
    analytics = []
    for product in product_purchases:
        analytics.append({
            'product_name': product.name,
            'total_quantity': product.total_quantity or 0,
            'total_cost': product.total_cost or 0
        })
    
    return jsonify({
        'analytics': analytics,
        'period': period
    })

@app.route('/staff_reports')
@login_required
def staff_reports():
    # Sales report for staff - only their own sales
    sales_data = Sale.query.filter_by(user_id=current_user.id).order_by(Sale.sale_date.desc()).all()
    total_sales = sum(sale.total_amount for sale in sales_data)
    
    # Today's sales for the staff member
    today = date.today()
    today_sales = Sale.query.filter(
        Sale.user_id == current_user.id,
        db.func.date(Sale.sale_date) == today
    ).all()
    today_revenue = sum(sale.total_amount for sale in today_sales)
    
    return render_template('staff_reports.html',
                         sales_data=sales_data,
                         total_sales=total_sales,
                         today_revenue=today_revenue)

@app.route('/staff_activities')
@login_required
@owner_required
def staff_activities():
    # Get date filter from request
    selected_date = request.args.get('date', date.today().isoformat())
    
    try:
        filter_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        filter_date = date.today()
    
    # Get all staff users
    staff_users = User.query.filter(User.role.in_(['staff', 'manager'])).all()
    
    staff_activities = []
    for user in staff_users:
        # Filtered date sales by this staff
        filtered_sales = Sale.query.filter(
            Sale.user_id == user.id,
            db.func.date(Sale.sale_date) == filter_date
        ).all()
        
        # Total sales by this staff
        total_sales = Sale.query.filter_by(user_id=user.id).all()
        
        # Recent activities (last 10 sales)
        recent_activities = Sale.query.filter_by(user_id=user.id).order_by(Sale.sale_date.desc()).limit(10).all()
        
        staff_activities.append({
            'user': user,
            'today_sales_count': len(filtered_sales),
            'today_revenue': sum(sale.total_amount for sale in filtered_sales),
            'total_sales_count': len(total_sales),
            'total_revenue': sum(sale.total_amount for sale in total_sales),
            'recent_activities': recent_activities,
            'last_activity': recent_activities[0].sale_date if recent_activities else None
        })
    
    return render_template('staff_activities.html', 
                         staff_activities=staff_activities,
                         selected_date=filter_date)

@app.route('/users')
@login_required
@owner_required
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/add_user', methods=['POST'])
@login_required
@owner_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        flash(get_text('user') + ' ' + get_text('success_added'))
    
    return redirect(url_for('users'))

@app.route('/edit_user/<int:id>', methods=['POST'])
@login_required
@owner_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.role = request.form['role']
        
        # Update password only if provided
        new_password = request.form.get('password')
        if new_password:
            user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        flash(get_text('user') + ' ' + get_text('success_updated'))
    
    return redirect(url_for('users'))

@app.route('/delete_user/<int:id>')
@login_required
@owner_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    # Prevent owner from deleting themselves
    if user.id == current_user.id:
        flash(get_text('cannot_delete_own_account'))
        return redirect(url_for('users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(get_text('user') + ' ' + get_text('success_deleted'))
    return redirect(url_for('users'))
# ============================
# EMERGENCY PASSWORD RESET (NO LOGIN REQUIRED)
# ============================

@app.route('/emergency_password_reset')
def emergency_password_reset():
    """EMERGENCY: Reset owner password without login"""
    try:
        # Find and reset owner password
        owner = User.query.filter_by(username='owner').first()
        if owner:
            owner.password_hash = generate_password_hash('emergency123')
            db.session.commit()
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Emergency Password Reset</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container mt-5">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h4>✅ EMERGENCY PASSWORD RESET SUCCESSFUL</h4>
                        </div>
                        <div class="card-body">
                            <h5>Owner account has been reset!</h5>
                            <div class="alert alert-info">
                                <strong>Username:</strong> owner<br>
                                <strong>New Password:</strong> emergency123
                            </div>
                            <p class="text-danger">
                                <strong>⚠️ IMPORTANT:</strong> 
                                Change this password immediately after login!
                            </p>
                            <a href="/login" class="btn btn-primary btn-lg">
                                Go to Login Page
                            </a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            return "Owner user not found in database!"
    except Exception as e:
        return f"Error: {str(e)}"

# ============================
# SYSTEM RESET ROUTE (OWNER ONLY)
# ============================

@app.route('/admin/reset_system')
@login_required
@owner_required
def reset_system():
    """Reset the entire system - OWNER ONLY"""
    try:
        # Delete all data
        db.session.query(Sale).delete()
        db.session.query(Purchase).delete()
        db.session.query(Product).delete()
        db.session.query(User).delete()
        
        # Recreate default owner
        owner = User(
            username='owner',
            password_hash=generate_password_hash('owner123'),
            role='owner'
        )
        db.session.add(owner)
        db.session.commit()
        
        # Logout user and redirect to login
        logout_user()
        flash('✅ System reset successfully! Default login: owner / owner123', 'success')
        return redirect(url_for('login'))
        
    except Exception as e:
        flash(f'❌ Error resetting system: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

def create_default_user():
    if not User.query.filter_by(username='owner').first():
        owner = User(
            username='owner',
            password_hash=generate_password_hash('owner123'),
            role='owner'
        )
        db.session.add(owner)
        db.session.commit()
        print("Default user created: username='owner', password='owner123'")

def create_default_user():
    if not User.query.filter_by(username='owner').first():
        owner = User(
            username='owner',
            password_hash=generate_password_hash('owner123'),
            role='owner'
        )
        db.session.add(owner)
        db.session.commit()
        print("Default user created: username='owner', password='owner123'")

# Application startup
if __name__ == '__main__':
    # Read environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    with app.app_context():
        db.create_all()
        create_default_user()
    
    print("MrCheap Shop System started successfully!")
    app.run(host=host, port=port, debug=debug)
