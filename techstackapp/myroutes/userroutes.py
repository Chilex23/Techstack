import math, os, json, datetime
from random import random
import requests
from flask import render_template, request, redirect, url_for, flash, make_response, session 
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc

from techstackapp import app,db
from techstackapp.mymodels import User, Products, Category, Order, HireOrder, Order_details, Hireperiod, Payment


key = os.environ.get('API_Key')
@app.route("/")
def home():
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    all_products = Products.query.all()
    flash_sales = Products.query.filter(Products.product_price<=40000, Products.product_type != 'Hire').all()
    session['cart'] = []
    cart = session.get('cart')
    cart_len = len(cart)
    return render_template("user/index.html", all_products=all_products, userdeets=userdeets, cart_len=cart_len, flash_sales=flash_sales)

@app.route("/login")
def userlogin():
    return render_template("user/login.html")

@app.route("/submit/login", methods=['POST'])
def submit_userlogin():
    username = request.form.get('username')
    pwd = request.form.get('password')

    if '' not in request.form.values():
        #Query the user with only the username
        deets = User.query.filter(User.user_username ==username).first()
        if deets:
            #get the password hash
            formated_pwd = deets.user_pass
            #Check the password hash from db with password from frontend
            check = check_password_hash(formated_pwd, pwd)
            #if the check is true then the passwords match
            if check:
                id = deets.user_id
                session['loggedin'] = id
                session['cart'] = []
                return redirect('/')
            else:
                #Keep a failed message in flash, then redirect to login page
                flash('Invalid Credentials')
                return redirect(url_for('userlogin'))
        else:
            flash('Invalid Credentials')
            return redirect(url_for('userlogin'))
    else:
        flash("Fields must be completed")
        return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("user/register.html")
    else:
        #Retrieve the form data
        email = request.form.get("email")
        phone = request.form.get("phone")
        username = request.form.get("username")
        pwd1 = request.form.get("password")
        pwd2 = request.form.get("password2")

        if "" in request.form.values():
            flash("Fields must be completed")
            return redirect(url_for('register'))
        elif pwd1 != pwd2:
            flash("Passwords must match")
            return redirect(url_for('register'))
        else:
            formated = generate_password_hash(pwd1)
            #Instantiante an object and give it parameters with values of the form in the table columns
            u = User(user_email=email, user_pass=formated, user_phone=phone, user_username=username)
            #Insert into the database
            db.session.add(u)
            db.session.commit()
            id = u.user_id
            #If successfully registered create a session with their id and redirect them to their dashboard
            session['loggedin'] = id
            session['cart'] = []
            return redirect('/userhome')

@app.route('/user/logout')
def logout():
    #Remove the user from the session dictionary
    session.pop('loggedin')
    return redirect('/login')

@app.route("/buy")
def buy():
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    all_products = Products.query.filter(Products.product_type =='Sale').all()
    cart = session.get('cart')
    cart_len = len(cart)
    return render_template("user/buy.html", userdeets=userdeets, all_products=all_products, cart_len=cart_len)

@app.route("/category")
def view_allcategory():
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    allcat = Category.query.all()
    cart = session.get('cart')
    cart_len = len(cart)
    return render_template("user/allcat.html", userdeets=userdeets, allcat=allcat, cart_len=cart_len)

@app.route("/category/<id>")
def category(id):
    loggedin = session.get('loggedin')
    all_products = Products.query.filter(Products.product_cat == id, Products.product_status=='In session').all()
    userdeets = User.query.get(loggedin)
    cat = Category.query.get(id)
    cart = session.get('cart')
    cart_len = len(cart)
    return render_template("user/category.html", userdeets=userdeets, cat=cat, all_products=all_products, cart_len=cart_len)


@app.route("/hire")
def hire():
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    all_products = Products.query.filter(Products.product_type =='Hire').all()
    cart = session.get('cart')
    cart_len = len(cart)
    return render_template("user/hire.html", userdeets=userdeets, all_products=all_products, cart_len=cart_len)

@app.route('/post', methods=['POST','GET'])
def post():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    if request.method == "GET":
        userdeets = User.query.get(loggedin)
        category = Category.query.all()
        cart = session.get('cart')
        cart_len = len(cart)
        return render_template("user/post.html", userdeets=userdeets, category=category, cart_len=cart_len)
    else:
        #Retrieve all the form data
        pname = request.form.get('name')
        pdesc = request.form.get('desc')
        ptype = request.form.get('prod_type')
        price = request.form.get('price')
        pcat = request.form.get('prod_cat')
        hire_period = request.form.get('hperiod')
        pic_object = request.files.get('img')
        original_file =  pic_object.filename

        #if '' not in request.form.values():
        extension = os.path.splitext(original_file)
        if extension[1].lower() in ['.jpg','.png']:
            fn = math.ceil(random() * 100000000)  
            save_as = str(fn) + extension[1] 
            pic_object.save(f"techstackapp/static/image/products/{save_as}")
            p = Products()
            #Insert into the database
            p.product_img = save_as
            p.product_name =pname
            p.product_cat = pcat
            p.product_desc = pdesc
            p.product_type = ptype
            p.product_price = price
            p.user_id = loggedin
            #If the product is for hire
            if ptype == "Hire":
                p.hire_period = hire_period
            db.session.add(p)
            db.session.commit()
            flash("Product successfully added")            
            return redirect("/post")
        else:
            flash('File Not Allowed')
            return redirect("/post")
        # else:
        #     flash("Fields must be completed")
        #     return redirect("/post")
        
        
  
@app.route("/product/<id>")
def product_details(id):
    loggedin = session.get('loggedin')
   
    userdeets = User.query.get(loggedin)
    all_products = Products.query.limit(3)
    product = Products.query.get(id)
    cart = session.get('cart')
    cart_len = len(cart)
    return render_template("user/product.html", userdeets=userdeets, all_products=all_products, product=product, cart_len=cart_len)

@app.route("/userhome")
def userhome():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    else:
        userdeets = User.query.get(loggedin)
        cart = session.get('cart')
        cart_len = len(cart)
        return render_template("user/userhome.html", userdeets=userdeets, cart_len=cart_len)

@app.route("/user/update", methods=['POST','GET'])
def user_editprofile():
    loggedin = session.get("loggedin")
    if loggedin == None:
        return redirect("/login")
    if request.method == "GET":
        userdeets = User.query.get(loggedin)
        cart = session.get('cart')
        cart_len = len(cart)
        return render_template("user/updateprofile.html", userdeets=userdeets, cart_len=cart_len)
    else:
        user = User.query.get(loggedin)
        #Change the fields
        user.user_fname = request.form.get('fname')
        user.user_lname = request.form.get('lname')
        user.user_phone= request.form.get('phone')
        user.user_address = request.form.get('address')
        user.user_username = request.form.get('username')
        user.user_email = request.form.get('email')
        pic_object = request.files.get('image')
        original_file =  pic_object.filename
        
        if original_file !='': #check if file is not empty
            extension = os.path.splitext(original_file)
            if extension[1].lower() in ['.jpg','.png']:
                fn = math.ceil(random() * 100000000)  
                save_as = str(fn) + extension[1] 
                pic_object.save(f"techstackapp/static/image/users/{save_as}")
                user.user_img = save_as
                db.session.add(user)
                db.session.commit()            
                return redirect("/userhome")
            else:
                flash('File Not Allowed')
                return redirect("/userhome")
        else:
            save_as =""
            user.user_img = save_as
            db.session.add(user)
            db.session.commit() 
            return redirect("/userhome")  
        

@app.route("/userbids")
def userbids():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    else:
        userdeets = User.query.get(loggedin)
        allorders = Order.query.filter(Order.orderuser_id==loggedin).order_by(desc(Order.order_id)).all()
        u_products = Products.query.filter(Products.user_id == loggedin).all()
        hire_orders = HireOrder.query.filter(HireOrder.hireuser_id == loggedin).order_by(desc(HireOrder.hireorder_id)).all()

        hire_prod = Products.query.filter(Products.user_id == loggedin, Products.product_type=='Hire').all()
        hireorder = []
        for i in hire_prod:
            hireorder.append(i.prodhireorders)
        cart3 = session.get('cart')
        cart_len = len(cart3)
        return render_template("user/userbids.html", userdeets=userdeets, allorders=allorders, u_products=u_products, hire_orders=hire_orders, hireorder=hireorder, cart_len=cart_len)

@app.route("/user/confirmhire/<id>")
def confirm_hire(id):
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    else:
        user_hire = HireOrder.query.get(id)
        prod_id = user_hire.hireproduct_id
        user_hire.hireorder_status = "Accepted"
        db.session.commit()
        db.session.execute(f"UPDATE hire_order SET hireorder_status = 'Rejected' WHERE NOT hireorder_id='{id}' AND hireproduct_id = '{prod_id}' ")
        db.session.commit()

        product = Products.query.get(user_hire.hireproduct_id)
        prod_hireperiod = product.hire_period
        
        return_obj = Hireperiod()
        return_obj.hireorder_id = id
        db.session.add(return_obj)
        db.session.commit()
        now = datetime.datetime.now()
        s2 = now.strftime("%Y-%m-%d")
        db.session.execute(f"UPDATE hireperiod SET due_date = DATE_ADD('{s2}', INTERVAL '{prod_hireperiod}' DAY) WHERE hireorder_id = {id}")
        db.session.commit()
        db.session.execute(f"UPDATE products SET product_status = 'Sold' WHERE  product_id = {user_hire.hireproduct_id} ")
        db.session.commit()
        return redirect("/userbids")


@app.route("/user/confirmorder/<id>")
def confirm_order(id):
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    else:
        user_order = Order.query.get(id)
        user_order.order_status = "Delivered"
        db.session.commit()
        return redirect("/userbids")

@app.route("/user/rejectorder/<id>")
def reject_order(id):
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    else:
        user_order = Order.query.get(id)
        user_order.order_status = "Cancelled"
        db.session.commit()
        return redirect("/userbids")

@app.route("/user/rejecthire/<id>")
def reject_hire(id):
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    else:
        user_hire = HireOrder.query.get(id)
        user_hire.hireorder_status = "Rejected"
        db.session.commit()
        return redirect("/userbids")

@app.route("/user/confirmreturn/<id>")
def user_confirm_return(id):
    loggedin = session.get("loggedin")
    if loggedin == None:
        return redirect("/user/login")
    else:
        user_hire = HireOrder.query.get(id)

        hire_id = user_hire.hireorder_id
        return_obj = Hireperiod.query.filter(Hireperiod.hireorder_id == hire_id).first()
        return_obj.return_date = datetime.datetime.now()
        return_obj.r_status = 'Returned'
        db.session.commit()
        return redirect("/userbids")

@app.route("/user/order/<id>")
def order_details(id):
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    else:
        userdeets = User.query.get(loggedin)
        order_deet = Order.query.get(id)
        return render_template("user/orderdeets.html", order_deet=order_deet, userdeets=userdeets)

@app.route("/user/hire/<id>")
def user_hire(id):
    loggedin = session.get('loggedin')
    if loggedin == None:
        flash("You have to be logged in or registered to Hire.")
        return redirect("/login")
    else:
        product_id = Products.query.get(id)
        hire_order = HireOrder(hireuser_id=loggedin, hireproduct_id=product_id.product_id)
        db.session.add(hire_order)
        db.session.commit()
        flash("You request for hire has been placed")
        return redirect(f"/product/{product_id.product_id}")

@app.route("/user/products")
def user_products():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/login")
    else:
        userdeets = User.query.get(loggedin)
        user_products = Products.query.filter(Products.user_id == loggedin).all()
        cart3 = session.get('cart')
        cart_len = len(cart3)
        return render_template("user/postedprod.html", userdeets=userdeets, user_products=user_products, cart_len=cart_len)

@app.route("/check/username")
def check_username():
    user = request.args.get("username")
    #query the user table
    deets = User.query.filter(User.user_username==user).first()
    if deets:
        return "Username is taken"
    else:
        return "Username is available"

@app.route("/cart/add", methods=['POST', "GET"])
def add_product_to_cart():
    if request.method == "GET":
        #get the product id
        id = request.args.get("id")
        cart2 = session.get('cart')
        if id not in cart2:
            #append it to the cart list
            cart2.append(id)
        session['cart'] = cart2
        items = len(cart2)    
        return f"{items}"        

@app.route("/cart/view")
def view_cart():
    loggedin = session.get('loggedin')
    cart3 = session.get('cart')
    cart_len = len(cart3)
    obj = []
    for i in cart3:
        u = Products.query.get(i)
        if u:
            obj.append(u)
    userdeets = User.query.get(loggedin)
    return render_template("user/cart.html", cart_items=obj, userdeets=userdeets, cart_len=cart_len)

@app.route("/cart/remove")
def remove_from_cart():
    id = request.args.get('id')
    cart4 = session.get('cart')
    cart4.remove(id)
    session['cart'] = cart4
    items = len(cart4)    
    return f"{items}" 

@app.route("/user/checkout", methods=['POST'])
def checkout():
    user_id = session.get('loggedin')
    if user_id == None:
        flash("You have to be logged in to checkout")
        return redirect("/login")
    #Retrieve the form data
    pid = request.form.getlist("prodId")
    qty = request.form.getlist('quantity')
    ship_address = request.form.get("address")
    if pid and qty and ship_address:
        each_prodamt = []
        totamt = 1000
        user_order = Order(orderuser_id = user_id, order_address=ship_address)
        db.session.add(user_order)
        db.session.commit()
        orderid = user_order.order_id
        #Generate a random number as transaction ref
        ref = int(random() * 10000000)
        session['refno'] = ref
        session['orderid'] = orderid

        for x,y in enumerate(pid):
            prod = Products.query.get(y)
            prod_amt = prod.product_price * int(qty[x])
            totamt = totamt + prod_amt
            each_prodamt.append(prod_amt)
            order_deets = Order_details(orderdet_orderid=orderid, orderdet_productid=y, quantity=qty[x], orderdet_amt=prod_amt)
            db.session.add(order_deets)
        db.session.commit()

        user_pay = Payment(pay_userid=user_id, pay_orderid=orderid, pay_ref=ref, pay_amt=totamt)
        db.session.add(user_pay)
        db.session.commit()
        
        return redirect("/user/confirmcheckout")
    else:
        flash("No items in the cart")
        return redirect("/cart/view")   

@app.route("/user/confirmcheckout", methods=['POST','GET'])
def confirm_checkout():
    loggedin = session.get('loggedin')
    ref = session.get('refno')
    orderid = session.get('orderid')
    if loggedin == None or ref == None:
        return redirect("/")
    userdeets = User.query.get(loggedin) 
    deets = Payment.query.filter(Payment.pay_ref==ref).first()
    order_deets = Payment.query.filter(Payment.pay_orderid==orderid).first()
    if request.method == 'GET':
        cart = session.get('cart')
        cart_len = len(cart)                         
        return render_template("user/confirmcheckout.html", deets = deets, userdeets=userdeets, orderdeets=order_deets, cart_len=cart_len)
    else:
        data = {"email":userdeets.user_email,"amount":deets.pay_amt*100, "reference":deets.pay_ref}
        headers = {"Content-Type": "application/json", "Authorization": f"{key}"}
        try:
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
            rspjson = json.loads(response.text) 
            if rspjson.get('status') == True:
                authurl = rspjson['data']['authorization_url']
                return redirect(authurl)
            else:
                return render_template("user/tryagain.html")
        except:
            return render_template("user/confailed.html")
        

@app.route("/user/payverify")
def paystack():
    reference = request.args.get('reference')
    ref = session.get('refno')
    #update our database 
    headers = {"Content-Type": "application/json","Authorization": f"{key}"}

    try:
        response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        rsp =response.json()#in json format
        if rsp['data']['status'] =='success':
            amt = rsp['data']['amount']
            ipaddress = rsp['data']['ip_address']
            p = Payment.query.filter(Payment.pay_ref==ref).first()
            p.pay_status = 'paid'
            db.session.add(p)
            db.session.commit()
            cart = session.get('cart')
            for i in cart:
                cart.remove(i)
            session['cart'] = []
            return render_template("user/accepted.html")  #update database and redirect them to the feedback page
        else:
            p = Payment.query.filter(Payment.pay_ref==ref).first()
            p.pay_status = 'failed'
            db.session.add(p)
            db.session.commit()
            return render_template("user/rejected.html")
    except:
        return "Connection to Paystack failed"  
    #return render_template("user/demo.html", response=rsp)


@app.route("/user/search", methods=['POST'])
def search():
    loggedin = session.get('loggedin')
    queryText = request.form.get('search')
    results = Products.query.filter(Products.product_name.ilike(f'%{queryText}%')).all()
    userdeets = User.query.get(loggedin)
    cart = session.get('cart')
    cart_len = len(cart)
    return render_template("user/search.html", results=results, userdeets=userdeets, queryText=queryText, cart_len=cart_len)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('user/error404.html', error=error), 404 