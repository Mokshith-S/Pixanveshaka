
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask import Flask,session,render_template,redirect,request,send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import easyocr
import cv2
import warnings
import re

app = Flask(__name__,template_folder="templates")
file = os.path.join(app.static_folder,"key.json")

with open(file,'r') as f:
    params = json.load(f)["params"]
app.config["SQLALCHEMY_DATABASE_URI"] = params["sql_conn"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = params["secret_key"]
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# class Regvalid(FlaskForm):
#     name = StringField("Name: ",validators=[DataRequired(),Length(min=10,max=20)])
#     phone = TelField("Telephone: ",validators=[DataRequired(),Length(min=0,max=10)])
#     email = EmailField("Email: ",validators=[DataRequired()])
#     username = StringField("Username: ",validators=[DataRequired()])
#     password = PasswordField("Password: ",validators=[DataRequired()])
#     submit = SubmitField("Submit")

class Admin(db.Model):
    username = db.Column(db.String(10),primary_key=True) 
    password = db.Column(db.String(20),nullable=False)

class User(db.Model):
    name = db.Column(db.String(10),nullable=False)
    phone=db.Column(db.Integer,nullable=False)
    email = db.Column(db.String(20),nullable=False) 
    username = db.Column(db.String(20),primary_key=True) 
    password = db.Column(db.String(60),nullable=False) 
    reg_date = db.Column(db.DateTime,nullable=False,default=datetime.now()) 
    ban = db.Column(db.Integer,nullable=False,default=0) 

class Feedback(db.Model):
    fno = db.Column(db.Integer,primary_key=True) 
    username = db.Column(db.String(10),nullable=False) 
    content = db.Column(db.String(20),nullable=False) 
    time = db.Column(db.DateTime,nullable=False)

class History(db.Model):
    hisno = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(10),nullable=False) 
    login_time = db.Column(db.DateTime,nullable=True) 
    logout_time = db.Column(db.DateTime,nullable=True) 

class Profile(db.Model):
    username = db.Column(db.String(10),primary_key=True) 
    language = db.Column(db.String(5),nullable=False) 
 

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/signup",methods=["POST","GET"])
def signup():
    error=[True,True,True,True,True,]
   

    if request.method == "POST":
        msg=''
         # 4-8 character one number
        pass_p=re.compile("^[a-zA-Z0-9]{4,8}$")
        # mail pattern  
        email_p=re.compile("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
        # username 
        name_p = re.compile("^[A-Za-z]+$")
        # phone 
        tel_p = re.compile("^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$")
        #username 
        user_p = re.compile("^[a-zA-Z0-9_]*$")
        name=request.form.get("firstName")

        if name_p.match(name) is None or len(name)==0 or len(name)>10:
            error[0]=False
        email=request.form.get("emailAddress")

        if email_p.match(email) is None:
            error[1]=False
        phone=request.form.get("phoneNumber")
        if tel_p.match(phone) is None:
            error[2]=False
        username=request.form.get("userName")
        if user_p.match(username) is None or len(name)==0 or len(username)>10:
            error[3]=False
        password=request.form.get("password")
        if pass_p.match(password) is None:
            error[4]=False
        update=True
        user1 = User.query.filter_by(username=username).first()
        user2 = Admin.query.filter_by(username=username).first()
        if user1 is not None or user2 is not None:
            return render_template("registration.html",msg="User already exist",error=error)
        for i in error:
            if i == False:
                update=False
                break
        try:
            
            if update==True:
                password=bcrypt.generate_password_hash(password).decode('utf-8')
                entry=User(name=name,phone=phone,email=email,username=username,password=password)
                db.session.add(entry)
                db.session.commit()
                return redirect("/")
            
        except Exception as e:
            msg="Username taken"
        return render_template("registration.html",msg="",error=error)
    else:
        return render_template("registration.html",error=error)

@app.route("/login",methods=['POST','GET'])
def login():
    valid=""
    if request.method == "POST":      
        username = request.form.get("username")
        password = request.form.get("password")
        nameu=User.query.filter_by(username=username).first()
        namea=Admin.query.filter_by(username=username).first()
        if nameu is not None and nameu.ban == 1:
            return render_template("ban.html")
      
        if nameu is None and namea is None:
            return render_template("login.html",valid="Username or Password is not valid")

        if nameu is not None and nameu.username==username:
            if bcrypt.check_password_hash(nameu.password,password):
                session['user']=username
                session['download']=False
                session['message']=None
                session['reset']=False
                entry = History(username=username,login_time=datetime.now())
                db.session.add(entry)
                db.session.commit()
                path = os.path.join(os.path.join(os.path.dirname(__file__),'user'),username)
                if not os.path.exists(path):
                    os.mkdir(path)
                return redirect("/home")
            else:
                return render_template("login.html",valid="Username or Password is not valid")

        elif namea is not None and namea.username==username:
            if bcrypt.check_password_hash(namea.password,password):
                session['user']=username
                return redirect("/admin_panel")
            else:
                return render_template("login.html",valid="Username or Password is not valid")
    return render_template("login.html",valid=valid)

@app.route("/admin_panel")
def admin_panel():
    try:
        admin = Admin.query.all()
        for ad in admin:
            if session['user'] == ad.username:
                a_username=ad.username 
        if 'user' in session and session['user'] == a_username:
            views = User.query.all()
            return render_template("admin_view.html",views=views)
        else:
            return render_template("denial.html")
    except:
        return render_template("denial.html")
        

@app.route("/feedback")
def admin_feed():
    try:
        user = Admin.query.filter_by(username=session['user'])
        if 'user' in session and user is not None:
            feed = Feedback.query.all()
            return render_template("view_feed.html",feed=feed)
    except:
        return render_template("denial.html")

@app.route("/history")
def history():
    try:
        admin = Admin.query.filter_by(username=session['user'])
        if admin is not None:
            history = History.query.all()
            return render_template("history.html",history=history)
    except:
        return render_template("denial.html")
    
@app.route("/home")
def home():
    try:
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.join(os.path.dirname(__file__),'user'),session['user'])
        if len(os.listdir(app.config['UPLOAD_FOLDER'])) != 0 and session['download']==False:

            for files in os.listdir(app.config['UPLOAD_FOLDER']):
                if files.rsplit('.')[-1] != 'txt':
                    file=os.path.join(app.config['UPLOAD_FOLDER'],files)
                    os.remove(file)
                if files.rsplit('.')[-1] == 'txt':
                    with open(os.path.join(app.config['UPLOAD_FOLDER'],files),'r+') as f:
                        f.truncate(0)
        if session['reset'] == True:
            session['message']=0
            session['download']=False
        session['reset']=True
        return render_template("home.html",message=session['message'],download=session['download'])
    except Exception as e:
        return render_template("denial.html")

@app.route("/profile",methods=['POST','GET'])
def profile():
    try:
        user=User.query.filter_by(username=session['user']).first()
        status=False
        if 'user' in session and session['user'] == user.username:
            if request.method == "POST":
                content = request.form.get('message')
                entry = Feedback(username=session['user'],content=content,time=datetime.now())
                db.session.add(entry)
                db.session.commit()
                status=True
            lang = Profile.query.filter_by(username=session['user']).first()
            if lang is None:
                lang = "000"
            else:
                lang = lang.language
            return render_template("profile.html",name=user.name,phone=user.phone,email=user.email,username=user.username,status=status,lang=lang)
    except:
        return render_template("denial.html")


@app.route("/language",methods=['POST','GET'])
def lang():
    try:
        lang=""
        if request.method == "POST":
            if request.form.get("c"):
                lang+="1"
            else:
                lang+="0"
            if request.form.get("cpp"):
                lang+="1"
            else:
                lang+="0"
            if request.form.get("java"):
                lang+="1"
            else:
                lang+="0"
            entry = Profile.query.filter_by(username=session['user'])
            if entry is not None:
                Profile.query.filter_by(username=session['user']).delete()
                db.session.commit()
            entry = Profile(username=session['user'],language=lang)
            db.session.add(entry)
            db.session.commit()
        return redirect("/profile")
    except:
        return render_template("denial.html")

@app.route("/uploader", methods=['GET','POST'])
def uploader():
    try:
        user = User.query.filter_by(username=session['user'])
        if user is not None:
            for check in request.files.getlist('files[]'):
                if check.filename == '':
                    session['reset']=False
                    session['message']=3
                    return redirect('/home')
            if request.method == 'POST':

                session['message']=None
                session['download']=False
                temp_loc = os.path.join(app.config['UPLOAD_FOLDER'],"temp.txt")

                reader = easyocr.Reader(['en'],gpu=True)
                with open(temp_loc,'w') as f:
                    pass
                with open(temp_loc,'r+') as f:
                    f.truncate(0)
                for fc in request.files.getlist('files[]'):
                    ext = fc.filename.rsplit('.')
                    if ext[-1] == 'png' or ext[-1] == 'jpeg' or ext[-1] == 'jpg':
                        try:
                            fc.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fc.filename)))
                            file=os.path.join(app.config['UPLOAD_FOLDER'],fc.filename)
                            warnings.filterwarnings("ignore",category=UserWarning)
                            img = cv2.imread(file,0)
                            result = reader.readtext(img,detail=0)
 
                            with open(temp_loc,"a") as f_content:
                                for i in result:
                                    f_content.write('\n')
                                    f_content.writelines(i)
                            
                        except:
                            session['message'] = 2
                            session['reset']=False
                            return redirect("/home")
                    else:
                        session['message'] = 1
                        session['reset']=False
                        return redirect("/home")
                session['reset']=False
                session['download'] = True
                return redirect("/home")
    except Exception as e:
        return render_template("denial.html")

@app.route("/download")
def download():
    try:
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.join(os.path.dirname(__file__),'user'),session['user'])
        file =  os.path.join(app.config['UPLOAD_FOLDER'],"temp.txt")
        return send_file(file,as_attachment=True)
    except:
        return render_template("denial.html")

@app.route("/logout")
def logout():
    try:
        user = User.query.filter_by(username=session['user']).first()
        entry = History.query.filter_by(username=user.username).first()
        if user is not None:
            History.query.filter_by(username=user.username,logout_time=None).update(dict(logout_time=datetime.now()))
            db.session.commit()
        session.pop('user')
        return redirect("/")
    except:
        session.pop('user')
        return redirect("/")

@app.route("/process",methods=['POST','GET'])
def process():
    try:
        if request.method == 'POST':
            admin = Admin.query.filter_by(username=session['user'])
            if admin is not None:
                user = request.form.get("val")

                User.query.filter_by(username=user).update(dict(ban=1))
                db.session.commit()

                return redirect("/admin_panel")
            else:
                return render_template("denial.html")
    except:
        return render_template("denial.html")


app.run(debug=True)
