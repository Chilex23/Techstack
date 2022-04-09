import datetime
from techstackapp import db


class Admin(db.Model):
    admin_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    admin_name = db.Column(db.String(255), nullable=False)
    admin_pass = db.Column(db.String(255), nullable=False)
    #Relationship
    admin_prodobj = db.relationship('Products', back_populates ='adminobj')
    
class User(db.Model): 
    user_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    user_email = db.Column(db.String(255), nullable=False)
    user_pass = db.Column(db.String(255), nullable=False)
    user_fname = db.Column(db.String(255), nullable=True)
    user_lname = db.Column(db.String(255), nullable=True)
    user_img = db.Column(db.String(255), nullable=True)
    user_address = db.Column(db.Text(), nullable=True)
    user_phone = db.Column(db.String(255), nullable=False)
    user_reg = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    user_username = db.Column(db.String(255), nullable=False)
    #setup the relationships         
    productobj = db.relationship('Products', back_populates ='userobj')
    orders = db.relationship('Order', back_populates ='userobj')
    paymentobj = db.relationship('Payment', back_populates ='userobj')
    hireorders = db.relationship('HireOrder', back_populates ='duser')
    
class Category(db.Model): 
    cat_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    cat_name = db.Column(db.String(255), nullable=False)
    cat_img = db.Column(db.String(255), nullable=True)
    #set up the relationship
    products = db.relationship('Products', back_populates ='prod_catobj')
   
class Products(db.Model): 
    product_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_price = db.Column(db.Integer(), nullable=False)
    product_type = db.Column(db.Enum('Hire','Sale'))
    product_desc = db.Column(db.Text())
    product_img = db.Column(db.String(255), nullable=False)
    hire_period = db.Column(db.Integer(), nullable=True)
    product_status = db.Column(db.Enum("In session","Sold"), default="In session")
    #create the foreign key
    product_cat = db.Column(db.Integer(), db.ForeignKey("category.cat_id"))
    user_id = db.Column(db.Integer(), db.ForeignKey("user.user_id"))
    admin_id = db.Column(db.Integer(), db.ForeignKey("admin.admin_id"))

    #set up the relationship
    prod_catobj = db.relationship('Category', back_populates ='products')
    userobj = db.relationship('User', back_populates ='productobj')
    adminobj = db.relationship('Admin', back_populates ='admin_prodobj')
    orders = db.relationship('Order_details', back_populates='prodobj')
    prodhireorders = db.relationship('HireOrder', back_populates ='dproduct')

class Order(db.Model): 
    order_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    order_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    order_status = db.Column(db.Enum("Delivered","Processing","Cancelled"), default="Processing")
    order_address = db.Column(db.Text())
    #create the foreign key
    orderuser_id = db.Column(db.Integer(), db.ForeignKey("user.user_id"))

    #set up the relationship
    userobj = db.relationship('User', back_populates ='orders')
    order_deets = db.relationship('Order_details', back_populates ='orderobj')
    pay_deets = db.relationship('Payment', back_populates ='order_paid4')

class Order_details(db.Model):
    orderdet_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    quantity = db.Column(db.Integer(), nullable=False)
    orderdet_amt = db.Column(db.Float())

    #create the foreign key
    orderdet_orderid = db.Column(db.Integer(), db.ForeignKey("order.order_id"))
    orderdet_productid = db.Column(db.Integer(), db.ForeignKey("products.product_id"))
    #set up the relationship
    orderobj = db.relationship('Order', back_populates ='order_deets')
    prodobj = db.relationship('Products', back_populates='orders')

class HireOrder(db.Model):
    __tablename__="hire_order"
    hireorder_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    hireuser_id = db.Column(db.Integer(), db.ForeignKey("user.user_id"))
    hireproduct_id = db.Column(db.Integer(), db.ForeignKey("products.product_id"))
    hireorder_status = db.Column(db.Enum("Accepted","Pending","Rejected"), default="Pending")

    dproduct = db.relationship('Products', back_populates ='prodhireorders')
    duser = db.relationship('User', back_populates ='hireorders')
    return_obj = db.relationship('Hireperiod', back_populates ='hireorder_obj')

class Hireperiod(db.Model): 
    rDate_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    r_status = db.Column(db.Enum("Returned","Hired"), default="Hired")
    due_date = db.Column(db.Date(), nullable=True)
    return_date = db.Column(db.Date(), nullable=True)
    hireorder_id = db.Column(db.Integer(), db.ForeignKey("hire_order.hireorder_id"))

    hireorder_obj = db.relationship('HireOrder', back_populates ='return_obj')
   
class Payment(db.Model): 
    pay_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    pay_userid = db.Column(db.Integer(), db.ForeignKey("user.user_id"))
    pay_orderid = db.Column(db.Integer(), db.ForeignKey("order.order_id"))
    pay_ref = db.Column(db.String(255), nullable=False)
    pay_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    pay_status=db.Column(db.Enum("pending","paid","failed"), default="pending")
    pay_amt=db.Column(db.Float())
    pay_response=db.Column(db.Text(), nullable=True)

    
    #set up the relationship
    userobj = db.relationship('User', back_populates ='paymentobj')
    order_paid4 = db.relationship('Order', back_populates ='pay_deets')

   
    