import datetime
import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func
from elasticapm.contrib.flask import ElasticAPM

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLITE_DB_PATH = 'sqlite:///' + os.path.abspath(os.path.join(BASE_DIR, 'demo', 'db.sql'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', SQLITE_DB_PATH)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': os.environ.get('ELASTIC_APM_SERVICE_NAME', 'opbeans-flask'),
    'SERVER_URL': os.environ.get('ELASTIC_APM_SERVER_URL', 'http://localhost:8200'),
    'DEBUG': True,
}
db = SQLAlchemy(app)
apm = ElasticAPM(app)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(1000))
    company_name = db.Column(db.String(1000))
    email = db.Column(db.String(1000))
    address = db.Column(db.String(1000))
    postal_code = db.Column(db.String(1000))
    city = db.Column(db.String(1000))
    country = db.Column(db.String(1000))


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    products = db.relationship('Product', secondary='order_lines')


class ProductType(db.Model):
    __tablename__ = 'product_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)

    def __str__(self):
        return self.name


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(1000), unique=True)
    name = db.Column(db.String(1000))
    description = db.Column(db.Text)
    product_type_id = db.Column('type_id', db.Integer, db.ForeignKey('product_types.id'), nullable=False)
    product_type = db.relationship('ProductType', backref=db.backref('products', lazy=True))
    stock = db.Column(db.Integer)
    cost = db.Column(db.Integer)
    selling_price = db.Column(db.Integer)
    orders = db.relationship('Order', secondary='order_lines')


class OrderLine(db.Model):
    __tablename__ = 'order_lines'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    product = db.relationship('Product')

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    order = db.relationship('Order')

    amount = db.Column(db.Integer)


@app.route('/api/products')
def products():
    product_list = Product.query.all()
    data = []
    for p in product_list:
        data.append({
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'stock': p.stock,
            'type_name': p.product_type.name
        })
    return jsonify(data)


@app.route('/api/products/top')
def top_products():
    product_list = db.session.query(
        Product.id,
        Product.sku,
        Product.name,
        Product.stock,
        func.sum(OrderLine.amount).label('sold')
    ).join(OrderLine).group_by(Product.id).order_by('-sold').limit(3)
    return jsonify([{
        'id': p.id,
        'sku': p.sku,
        'name': p.name,
        'stock': p.stock,
        'sold': p.sold,
    } for p in product_list])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
