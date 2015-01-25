# from flask.ext.security import utils
# import patches
# utils.send_mail = patches.my_send_mail
from flask import Flask, flash, render_template, request, session, redirect, url_for, abort, send_from_directory, Blueprint
from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask.ext.bcrypt import *
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.base import MenuLink
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.assets import Environment, Bundle
import os.path as op
import json
from decorators import async
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from sqlalchemy.sql.expression import func, distinct
from flask.ext.script import Shell, Manager, Command, Option
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, LoginForm, \
        RegisterForm, ForgotPasswordForm, current_user, login_required, url_for_security, roles_required
from flask.ext.security.forms import ChangePasswordForm


# Create app
app = Flask(__name__)
app.config.from_object('config.config')
app.config.from_object('env.env') #overwrites config.config for production server
app.config.from_object('env.email') #overwrites config.config for production server
custom = Blueprint('custom', __name__, static_folder='custom',  static_url_path='/custom')
app.register_blueprint(custom)
assets = Environment(app)
jsItems = Bundle('custom/customItems.js', 'custom/customAll.js', filters='jsmin', output='gen/items.js')
jsMgmt = Bundle('custom/customMgmt.js', 'custom/customAll.js', filters='jsmin', output='gen/mgmt.js')
jsOrders = Bundle('custom/customOrders.js', 'custom/customAll.js', filters='jsmin', output='gen/orders.js')
jsProfile = Bundle('custom/customProfile.js', 'custom/customAll.js', filters='jsmin', output='gen/profile.js')
css = Bundle('custom/style.css', filters='cssmin', output='gen/packed.css')
assets.register('jsItems', jsItems)
assets.register('jsMgmt', jsMgmt)
assets.register('jsOrders', jsOrders)
assets.register('jsProfile', jsProfile)
assets.register('css_all', css)

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

# uncomment the below to make /admin return 404 for non-admins
# @app.before_request
# def check_for_admin(*args, **kw):
#     if request.path.startswith('/admin/'):
#         if not current_user.has_role('admin'):
#             abort(404)

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
    username = db.Column(db.String(255), unique=True)
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
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'))

    def __str__(self):
        return '<farmer=%s item=%s>' % (self.user.email, self.name)

    def __init__(self, name, description, price, max_available, unit, active, user_id, week_id):
        self.name = name
        self.description = description
        self.price = price
        self.max_available = max_available
        self.unit = unit
        self.active = active
        self.user_id = user_id
        self.week_id = week_id

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    amount = db.Column(db.Float())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, week_id, item_id, amount, user_id):
        self.week_id = week_id
        self.item_id = item_id
        self.amount = amount
        self.user_id = user_id

class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    current = db.Column(db.Boolean())
    active = db.Column(db.Boolean())
    orders = db.relationship('Order', backref=db.backref('week', lazy='joined'), lazy='dynamic')      

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@async
def send_security_email(msg):
    with app.app_context():
       mail.send(msg)

@security.send_mail_task
def async_security_email(msg):
    send_security_email(msg)

# Views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
        
@app.route('/farmers')
@login_required
@roles_required('farmer')
def farmers():
    return render_template('farmers.html')

@app.route('/order')
@login_required
@roles_required('buyer')
def order():
    return render_template('order.html')

@app.route('/manage')
@login_required
@roles_required('manager')
def manage():
    return render_template('manage.html')
        
@app.route('/farmers/getold')
@login_required
@roles_required('farmer')
def farmers_old():
    this_week = Week.query.filter(Week.current == True).first()
    results = Item.query.filter(Item.user == current_user, Item.week_id == (this_week.id - 1)).all()
    obj = {'old_items': []}
    for i in range(len(results)):
        obj['old_items'].append({'name': results[i].name, 'description': results[i].description, 'price': results[i].price, 'max_available': results[i].max_available, 'units': results[i].unit, 'active': results[i].active})
    return json.dumps(obj)

@app.route('/farmers/update', methods=['GET', 'POST'])
@login_required
@roles_required('farmer')
def farmers_update():
    this_week = Week.query.filter(Week.current == True).first()
    results = Item.query.filter(Item.user == current_user, Item.week_id == this_week.id).all()
    if request.method == 'GET':
        obj = {'old_items': []}
        for i in range(len(results)):
            obj['old_items'].append({'name': results[i].name, 'description': results[i].description, 'price': results[i].price, 'max_available': results[i].max_available, 'units': results[i].unit, 'active': results[i].active, 'id': results[i].id})
        return json.dumps(obj)
    elif request.method == 'POST':
        items = request.get_json(force=True)
        item_ids = []
        for item in items:
            if type(item['active']) == str or type(item['active']) == unicode:
                if item['active'].lower() == 'false': item['active'] = False
                else: item['active'] = True
            try: item_ids.append(item['id'])
            except: pass
        for item in items:
            new = Item(item['name'], item['description'], item['price'], item['max_available'], item['units'], item['active'], current_user.id, this_week.id)
            try: new.id = item['id']
            except: pass
            db.session.merge(new)
            db.session.commit()
        for item in results:
            if not item.id in item_ids and item.week_id == this_week.id:
                db.session.delete(item)
                db.session.commit()
        return json.dumps({'message': 'Your Items have been updated', 'priority': 'success'})

@app.route('/order/update', methods=['GET', 'POST'])
@login_required
@roles_required('buyer')
def order_update():
    this_week = Week.query.filter(Week.current == True).first()
    the_orders = Order.query.filter(Order.user_id == current_user.id and Order.week == this_week.id).all()
    the_order_ids = [i.id for i in the_orders]
    if request.method == 'GET':
        obj = {'items': [], 'old_orders': []}
        the_items = Item.query.filter(Item.active == True, Item.week_id == this_week.id).order_by(asc(Item.user_id)).all()
        for i in range(len(the_items)):
            gone = 0
            for order in the_items[i].orders:
                gone += order.amount
            obj['items'].append({'name': the_items[i].name, 'description': the_items[i].description, 'price': the_items[i].price, 'units': the_items[i].unit, 'available': the_items[i].max_available - gone, 'farmer': the_items[i].user.username, 'id': the_items[i].id})
        for i in range(len(the_orders)):
            obj['old_orders'].append({'name': the_orders[i].item.name, 'quantity': the_orders[i].amount, 'units': the_orders[i].item.unit, 'price': the_orders[i].item.price, 'id': the_orders[i].id, 'item_id': the_orders[i].item_id})
        return json.dumps(obj)
    elif request.method == 'POST':
        orders = request.get_json(force=True)
        order_ids = []
        for i in orders:
            try: order_ids.append(i['id'])
            except: pass
        for order in orders:
            gone = db.session.query(func.sum(Order.amount)).filter(Order.week_id == this_week.id, Order.item_id == order['item_id']).first()[0]
            if 'id' in order: 
                this_quan = Order.query.get(order['id']).amount
            else: 
                this_quan = 0
            if not gone:
                gone = 0
            if not this_quan:
                this_quan = 0
            left = float(Item.query.get(order['item_id']).max_available) - gone + float(this_quan)
            order['quantity'] = min(left, float(order['quantity']))
            new = Order(this_week.id, order['item_id'], order['quantity'], current_user.id)
            try: new.id = order['id']
            except: pass
            db.session.merge(new)
            db.session.commit()
        for order in the_orders:
            if not order.id in order_ids:
                db.session.delete(order)
                db.session.commit()
        response = {'message': 'Your Order has been placed', 'priority': 'success', 'items': []}
        return json.dumps(response)

@app.route('/profile/update', methods=['POST'])
@login_required
@roles_required('farmer')
def update_profile():
    update = request.get_json(force=True)
    current_user.username = update['username']
    db.session.commit()
    return json.dumps([{'type': 'success', 'message': 'Your username has been changed to: ' + update['username']}])

@app.route('/manage/update', methods=['GET', 'POST'])
@login_required
@roles_required('manager')
def manage_update():
    this_week = Week.query.filter(Week.current == True).first()
    the_orders = Order.query.filter(Order.week == this_week).all()
    the_order_ids = [i.id for i in the_orders]
    if request.method == 'GET':
        obj = {'buyers': [], 'old_orders': []}
        obj['buyers'] = [i.email for i in User.query.all() if i.has_role('buyer')]
        for i in range(len(the_orders)):
            obj['old_orders'].append({'name': the_orders[i].item.name, 'quantity': the_orders[i].amount, 'units': the_orders[i].item.unit, 'price': the_orders[i].item.price, 'id': the_orders[i].id, 'item_id': the_orders[i].item_id, 'user': the_orders[i].user.username, 'user_id': the_orders[i].user.id})
        return json.dumps(obj)
    elif request.method == 'POST':
        orders = request.get_json(force=True)
        order_ids = []
        for i in orders:
            try: order_ids.append(i['id'])
            except: pass
        for order in orders:
            this_quan = Order.query.get(order['id']).amount
            new = Order(this_week.id, order['item_id'], order['quantity'], order['user_id'])
            new.id = order['id']
            db.session.merge(new)
            db.session.commit()
        response = {'message': str(orders[0]['user']) + '\'s order has been updated', 'priority': 'success', 'items': []}
        return json.dumps(response)

admin = Admin(app)

# Admin Views
class MyModelView(ModelView):
    def is_accessible(self):
        return True  # remove to lock down admin
        # return current_user.has_role('admin')  # uncomment to lock down admin

class MyFileView(FileAdmin):
    def is_accessible(self):
        return True  # remove to lock down admin
        # return current_user.has_role('admin')  # uncomment to lock down admin

admin.add_view(MyModelView(User, db.session, name='Users', category='Models'))
admin.add_view(MyModelView(Role, db.session, name='Roles', category='Models'))
admin.add_view(MyModelView(Item, db.session, name='Items', category='Models'))
admin.add_view(MyModelView(Order, db.session, name='Orders', category='Models'))
admin.add_view(MyModelView(Week, db.session, name='Weeks', category='Models'))
path = op.join(op.dirname(__file__), 'static')
admin.add_view(MyFileView(path, '/static/', name='Static Files'))
admin.add_link(MenuLink(name='Main Site', url='/'))

if __name__ == '__main__':
    manager.run()
