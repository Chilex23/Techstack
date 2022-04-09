import math, os, random, datetime
from flask import render_template, request, redirect, url_for, flash, make_response, session 
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc

from techstackapp import app, db
from techstackapp.mymodels import Admin, Category, User, Products, Order, Order_details, HireOrder, Hireperiod


@app.route("/admin/login")
def admin_login():
    return render_template("admin/adminlogin.html")

@app.route("/admin/orders")
def admin_orders():
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    else:
        allorders = Order.query.order_by(desc(Order.order_id)).all()
        u_products = Products.query.filter(Products.admin_id == admin).order_by(desc(Products.product_id)).all()
        hire_prod = Products.query.filter(Products.admin_id == admin, Products.product_type=='Hire').all()
        hire_orders = []
        for i in hire_prod:
            hire_orders.append(i.prodhireorders)
        return render_template("admin/adminorder.html", allorders=allorders, u_products=u_products, hire_orders=hire_orders)

@app.route("/admin/confirmhire/<id>")
def admin_confirm_hire(id):
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
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
        return redirect("/admin/orders")

@app.route("/admin/confirmorder/<id>")
def admin_confirm_order(id):
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    else:
        user_order = Order.query.get(id)
        user_order.order_status = "Delivered"
        db.session.commit()
        return redirect("/admin/orders")

@app.route("/admin/confirmreturn/<id>")
def confirm_return(id):
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    else:
        user_hire = HireOrder.query.get(id)

        hire_id = user_hire.hireorder_id
        return_obj = Hireperiod.query.filter(Hireperiod.hireorder_id == hire_id).first()
        return_obj.return_date = datetime.datetime.now()
        return_obj.r_status = 'Returned'
        db.session.commit()
        return redirect("/admin/orders")

@app.route("/admin/rejectorder/<id>")
def admin_reject_order(id):
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    else:
        user_order = Order.query.get(id)
        user_order.order_status = "Cancelled"
        db.session.commit()
        return redirect("/admin/orders")

@app.route("/admin/rejecthire/<id>")
def admin_reject_hire(id):
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    else:
        user_hire = HireOrder.query.get(id)
        user_hire.hireorder_status = "Rejected"
        db.session.commit()
        return redirect("/admin/orders")

@app.route("/admin/order/<id>")
def admin_order_details(id):
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    else:
        loggedin = session.get('loggedin')
        order_deet = Order.query.get(id)
        return render_template("admin/adminorderdts.html", order_deet=order_deet)


@app.route("/admin/submit/login", methods=['POST'])
def admin_submitlogin():
    username = request.form.get('username')
    pwd = request.form.get('password')

    if '' not in request.form.values():
        #Query the admin table with only the username
        deets = Admin.query.filter(Admin.admin_name ==username).first()
        if deets:
            #get the password hash
            formated_pwd = deets.admin_pass
            #Check the password hash from db with password from frontend
            check = check_password_hash(formated_pwd, pwd)
            #if the check is true then the passwords match
            if check:
                id = deets.admin_id
                session['admin'] = id
                return redirect('/admin/home')
            else:
                #Keep a failed message in flash, then redirect to login page
                flash('Invalid Credentials')
                return redirect(url_for('admin_login'))
        else:
            #Keep a failed message in flash, then redirect to login page
            flash('Invalid Credentials')
            return redirect(url_for('admin_login'))
    else:
        flash("Fields must be completed")
        return redirect("/admin/login")

@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "GET":
        return render_template("admin/adminregister.html")
    else:
        #Retrieve the form data
        username = request.form.get("username")
        pwd1 = request.form.get("password")
        pwd2 = request.form.get("password2")

        if "" in request.form.values():
            flash("Fields must be completed")
            return redirect(url_for('admin_register'))
        elif pwd1 != pwd2:
            flash("Passwords must match")
            return redirect(url_for('admin_register'))
        else:
            formated = generate_password_hash(pwd1)
            #Instantiante an object and give it parameters with values of the form in the table columns
            a = Admin(admin_name=username, admin_pass=formated)
            #Insert into the database
            db.session.add(a)
            db.session.commit()
            id = a.admin_id
            #If successfully registered create a session with their id and redirect them to their dashboard
            session['admin'] = id
            return redirect('/admin/home')

@app.route("/admin/addcategory", methods=["POST", "GET"])
def add_category():
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    else:
        if request.method == "GET":
            return render_template("admin/admincatform.html")
        else:
            #Retrieve the form
            #Insert into db
            catname = request.form.get("catname")
            cat_pic = request.files.get('image')
            original_file =  cat_pic.filename

            if "" not in request.form.values():
                cat = Category()
                extension = os.path.splitext(original_file)
                if extension[1].lower() in ['.jpg','.png']:
                    fn = math.ceil(random.random() * 100000000)  
                    save_as = str(fn) + extension[1] 
                    cat_pic.save(f"techstackapp/static/image/categories/{save_as}")
                    cat.cat_img = save_as
                    cat.cat_name = catname
                    db.session.add(cat)
                    db.session.commit()
                    flash("Category added")
                    return redirect("/admin/home")
                else:
                    flash('File Not Allowed')
                    return redirect("/admin/addcategory")
            else:
                flash("Fields must be completed")
                return redirect("/admin/addcategory")  

@app.route("/admin/allcategories")
def admin_viewcat():
    #Run a query to see all categories
    allcat = Category.query.all()
    return render_template("/admin/admincrud.html", allcat=allcat)

@app.route("/admin/edit/<id>", methods=['POST','GET'])
def edit_category(id):
    admin = session.get('admin')
    if admin == None:
        return render_template('admin/login.html')
    else:
        if request.method == 'GET':
            cat = Category.query.get(id)
            return render_template("admin/admineditcat.html", cat=cat)
        else:
            #retrieve the edited details
            catname = request.form.get('catname')
            cat_image = request.files.get('image')

            cat2 = Category.query.get(id)
            original_file =  cat_image.filename

            extension = os.path.splitext(original_file)
            if extension[1].lower() in ['.jpg','.png']:
                fn = math.ceil(random.random() * 100000000)  
                save_as = str(fn) + extension[1] 
                cat_image.save(f"techstackapp/static/image/categories/{save_as}")
                cat2.cat_img = save_as
                cat2.cat_name = catname
                db.session.add(cat2)
                db.session.commit()
                flash("Category Edited")
                return redirect("/admin/allcategories")
            else:
                flash('File Not Allowed')
                return redirect(f"/admin/edit/{id}")

@app.route("/admin/delete/<id>")
def delete_category(id):
    admin = session.get('admin')
    if admin == None:
        return render_template('admin/login.html')
    else:
        x = db.session.query(Category).get(id)
        db.session.delete(x)
        db.session.commit()
        flash(f"Category {id} deleted")
        return redirect("/admin/allcategories")

@app.route('/admin/logout')
def admin_logout():
    #Remove the admin from the session dictionary
    session.pop('admin')
    #redirect them to the login page
    return redirect('/admin/login')

@app.route("/admin/home")
def admin_home():
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    else:
        return render_template("admin/adminhome.html")

@app.route('/admin/post', methods=['POST','GET'])
def admin_post():
    admin = session.get("admin")
    if admin == None:
        return redirect("/admin/login")
    if request.method == "GET":
        admindeets = Admin.query.get(admin)
        category = Category.query.all()
        return render_template("admin/adminpost.html", admindeets=admindeets, category=category)
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
            fn = math.ceil(random.random() * 100000000)  
            save_as = str(fn) + extension[1] 
            pic_object.save(f"techstackapp/static/image/products/{save_as}")
            #Instantiate a product object with all the data
            p = Products()
            #Insert into the database
            p.product_img = save_as
            p.product_name =pname
            p.product_cat = pcat
            p.product_desc = pdesc
            p.product_type = ptype
            p.product_price = price
            p.admin_id = admin
             #If the product is for hire
            if ptype == "Hire":
                p.hire_period = hire_period
            db.session.add(p)
            db.session.commit()
            flash("Product successfully added")            
            return redirect("/admin/post")
        else:
            flash('File Not Allowed')
            return redirect("/admin/post")
        
@app.route("/admin/products")
def admin_products():
    admin = session.get('admin')
    if admin == None:
        return redirect("/admin/login")
    else:
        admin_products = Products.query.all()
        return render_template("admin/adminproducts.html", admin_products=admin_products)

@app.route("/admin/allusers")
def all_users():
    admin = session.get('admin')
    if admin == None:
        return redirect("/admin/login")
    else:
        users = User.query.all()
        return render_template("admin/allusers.html", users=users)

@app.route("/admin/deleteuser/<id>")
def remove_user(id):
    admin = session.get('admin')
    if admin == None:
        return redirect("/admin/login")
    else:
        user = User.query.get(id)
        db.session.delete(user)
        flash(f"{user.user_username} has been removed")
        return redirect("/admin/allusers")