
from flask import Flask, render_template, request, session, redirect, url_for, abort
from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.bcrypt import *
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
import os.path as op
import json
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from flask.ext.script import Shell, Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, LoginForm, \
        RegisterForm, ForgotPasswordForm, current_user, login_required, url_for_security
from flask.ext.security.forms import ChangePasswordForm

# Create app
app = Flask(__name__)
app.config.from_object('config.config')
app.config.from_object('env.env') #overwrites config.config for production server
app.config.from_object('env.email') #overwrites config.config for production server

# Setup mail extension
mail = Mail(app)

# Setup babel
babel = Babel(app)

# useful for a separate production servers
def my_app(environ, start_response): 
    path = environ["PATH_INFO"]  
    if path == "/":  
        return app(environ, start_response)     
    else:  
        return app(environ, start_response) 

@babel.localeselector
def get_locale():
    override = request.args.get('lang')

    if override:
        session['lang'] = override

    rv = session.get('lang', 'en')
    return rv

@app.context_processor
def inject_userForms():
    return dict(login_form=LoginForm(), register_user_form=RegisterForm(), \
        forgot_password_form=ForgotPasswordForm(), change_password_form=ChangePasswordForm())

# Create database connection object
def _make_context():
    return dict(app=app, mail=mail, db=db, babel=babel, security=security, admin=admin)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=_make_context))

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    items = db.relationship('Item', backref=db.backref('user', lazy='joined'), lazy='dynamic')
    orders = db.relationship('Order', backref=db.backref('user', lazy='joined'), lazy='dynamic')

    def __str__(self):
        return '<User id=%s email=%s>' % (self.id, self.email)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    price = db.Column(db.Float())
    max_available = db.Column(db.Float())
    unit = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    active = db.Column(db.Boolean())
    orders = db.relationship('Order', backref=db.backref('item', lazy='joined'), lazy='dynamic')

    def __str__(self):
        return '<farmer=%s item=%s>' % (self.user.email, self.name)

    def __init__(self, name, description, price, max_available, unit):
        self.name = name
        self.description = description
        self.price = price
        self.max_available = max_available
        self.unit = unit

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer())
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    amount = db.Column(db.Float())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, week, item_id, amount, user_id):
        self.week = week
        self.item_id = item_id
        self.amount = amount
        self.user_id = user_id

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# db.create_all()

# Views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    if current_user.is_authenticated():
        return render_template('profile.html')
    else:
        return redirect(url_for_security('login'))
        
@app.route('/farmers')
def farmers():
    if current_user.has_role('farmer'):
        return render_template('farmers.html')
    else:
        return redirect(url_for_security('login'))

@app.route('/order')
def order():
    if current_user.has_role('buyer'):
        return render_template('order.html')
    else:
        return redirect(url_for_security('login'))

@app.route('/farmers/update')
def farmers_update():
    if current_user.has_role('farmer'):
        if request.method == 'GET':
            obj = {'items': []}
            results = Item.query.filter(Item.user == current_user).all()
            for i in range(len(results)):
                obj['items'].append({'name': results[i].name, 'description': results[i].description, 'price': results[i].price, 'units': results[i].unit, 'available': results[i].max_available, 'farmer': results[i].user.email, 'id': results[i].id})
            print obj
            return json.dumps(obj)
        elif request.method == 'POST':
            items = request.get_json(force=True)
            for item in items:
                new = Item(4, item['id'], item['amount'], current_user.id)
                db.session.add(new)
                db.session.commit()
            return 'Items POSTed'
    else:
        abort(404)

@app.route('/order/update', methods=['GET', 'POST'])
def order_update():
    if current_user.has_role('buyer'):
        if request.method == 'GET':
            obj = {'items': [], 'orders': []}
            results = Item.query.filter(Item.active == True).order_by(asc(Item.user_id)).all()
            for i in range(len(results)):
                obj['items'].append({'name': results[i].name, 'description': results[i].description, 'price': results[i].price, 'units': results[i].unit, 'available': results[i].max_available, 'farmer': results[i].user.email, 'id': results[i].id})
            print obj
            return json.dumps(obj)
        elif request.method == 'POST':
            orders = request.get_json(force=True)
            print orders
            for order in orders:
                new = Order(4, order['id'], order['quantity'], current_user.id)
                db.session.add(new)
                db.session.commit()
            return 'Order POSTed'
    else:
        abort(404)

admin = Admin(app)

# Admin Views
class MyModelView(ModelView):
    def is_accessible(self):
        return True  # remove
        # return current_user.has_role('admin')  # uncomment to lock down admin

class MyFileView(FileAdmin):
    def is_accessible(self):
        return True  # remove
        # return current_user.has_role('admin')  # uncomment to lock down admin

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(Item, db.session))
admin.add_view(MyModelView(Order, db.session))
path = op.join(op.dirname(__file__), 'static')
admin.add_view(MyFileView(path, '/static/', name='Static Files'))

if __name__ == '__main__':
    manager.run()
