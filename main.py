from flask import Flask, render_template, request, redirect, url_for, session,logging,flash
from passlib.hash import sha256_crypt
from flask_login import logout_user
import os
import bcrypt
import pyrebase

firebaseConfig={
    'apiKey': "AIzaSyCl84_OgJF--zt9AUyJSQjIAH-89P-A8X4",
    'authDomain': "plant-disease-detection-802ad.firebaseapp.com",
    'databaseURL': "https://plant-disease-detection-802ad.firebaseio.com",
    'projectId': "plant-disease-detection-802ad",
    'storageBucket': "plant-disease-detection-802ad.appspot.com",
    'messagingSenderId': "370961869561",
    'appId': "1:370961869561:web:1f9ca525cc65ac8cc49028",
    'measurementId': "G-4NEQMN54D4"}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

person = {"is_logged_in":False,"user_status":False,"Email":""}




app = Flask(__name__)

app.secret_key = os.urandom(24)



@app.route('/logout')
def logout():
    if person["is_logged_in"]==True:
        person["is_logged_in"]=False 
        return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/')
def start():
    return render_template("login.html")

@app.route('/forgotpassword', methods = ['GET','POST'])
def forgotpassword():
    if(request.method=='GET'):
        return render_template("forgotpassword.html") 
    else:
        Email = request.form['Email']
        auth.send_password_reset_email(Email)
        flash("Request Submitted! Check mail to Reset your Password")
        return redirect(url_for('login'))

@app.route('/reset' , methods = ['GET','POST'])
def reset():
    if person["is_logged_in"]==True and person["user_status"]==False:
        if(request.method=='GET'):
            return redirect(url_for('profile'))
            
        else:
            auth.send_password_reset_email(person['Email'])
            flash("Request Submitted! Check mail to Reset your Password")
            return redirect(url_for('profile'))
            
            
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if person["is_logged_in"]==True and person["user_status"]==False:
        if(request.method=='GET'):
            user = db.child("User").order_by_child("Email").equal_to(person["Email"]).get()
            value=""
            for data in user.each():
                value = data.val()
            return render_template("home.html",params=value)
            
    return redirect(url_for('login'))




@app.route('/login' , methods = ['GET','POST'])
def login():
    global person
    if(person["is_logged_in"]==True and person['user_status']==False):
        return redirect(url_for('home'))
    else:
        if(request.method=='POST'):
            Email = request.form.get('Email')
            Password = request.form.get("Password")
            try:
                auth.sign_in_with_email_and_password(Email,Password)
                
                user = db.child("User").order_by_child("Email").equal_to(Email).get()
                
                
                person["is_logged_in"] = True
                person["Email"] = Email
            
                value = False
                for data in user.each():
                    value = data.val()['Status']
                if(value==True):
                    person["user_status"] = True
                    return redirect(url_for('dashboard'))
                else:
                    person["user_status"] = False
                    return redirect(url_for('home'))
            except:
                flash("Invalid Email or Password")
                return redirect(url_for('login'))
        return render_template('login.html') 


@app.route('/dashboard')
def dashboard():
    if person["is_logged_in"]==True and person["user_status"]==True:
        return render_template("dashboard.html")
    return redirect(url_for('login'))



@app.route('/signup', methods = ['GET','POST'])
def register():
    if(request.method=='GET'):
        return render_template("signup.html")
    else:
        '''Add values into database from the webpage'''
        Name= request.form['Name']
        Phone= request.form['Phone']
        Address= request.form['Address']
        Email= request.form['Email']
        Password= request.form['Password']
        Confirm = request.form['Confirm']
        if(Password==Confirm):
            try:
                auth.create_user_with_email_and_password(Email,Password)
                data = {'Name':Name,'Phone':Phone,'Address':Address,'Email':Email,'Status':False}
                db.child("User").push(data)
                flash("Successfully! Registered")
                return redirect(url_for('login'))
            except:
                flash("Registration Failed (Use Atleast Six Lenght String)")
                return render_template("signup.html")
        else:
            flash("Registration Failed (Password did not Matched)")
            return render_template("signup.html")
        
            

    return render_template("signup.html")


@app.route('/profile' , methods = ['GET','POST'])
def profile():
    if person["is_logged_in"]==True and person["user_status"]==False:
        if(request.method=='GET'):
            user = db.child("User").order_by_child("Email").equal_to(person["Email"]).get()
            value=""
            for data in user.each():
                value = data.val()
            return render_template("profile.html",params=value)
        else:
            udata = db.child("User").get()
            Name= request.form['Name']
            Phone= request.form['Phone']
            Address= request.form['Address']
            
            for ud in udata.each():
                if ud.val()['Email']==person['Email']:
                    db.child('User').child(ud.key()).update({'Name':Name,'Phone':Phone,'Address':Address})
            flash("Profile Updated")
            return redirect(url_for('profile'))
    return render_template("login.html")
        

            
  







@app.route('/contactus', methods = ['GET','POST'])
def contactus():
    if person["is_logged_in"]==True and person["user_status"]==False:
        if(request.method=='GET'):
            return render_template("contactus.html")
        else:
            '''Add values into database from the webpage'''
            Name= request.form['Name']
            Email= request.form['Email']
            Text= request.form['Text']
            try:
                data = {'Name':Name,'Email':Email,'Text':Text}
                user = db.child("User").order_by_child("Email").equal_to(person['Email']).get()
                for u in user.each():
                    db.child("User").child(u.key()).child("Contactus").push(data)
                flash("Successfully! Message Submit")
                return redirect(url_for('contact'))
            except:
                return render_template("contactus.html")

        return render_template("contactus.html")

    return redirect(url_for('login'))

@app.route('/testplant')
def testplant():
    if person["is_logged_in"]==True and person["user_status"]==False:
        return render_template("testplant.html")
    return redirect(url_for('login'))




if __name__=="__main__":
    app.run(debug=True)
