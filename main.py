from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password_blogz@localhost:3307/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    reg_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, reg_date=None):
        self.title = title
        self.body = body
        if reg_date is None:
            reg_date = datetime.utcnow()
        self.reg_date = reg_date
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password        

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session and '/static/' not in request.path:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("This username does not exist", 'error')
        elif user.password != password:
            flash("The password is incorrect", 'error')
        else:    
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')        
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error_username = ''
    error_password = ''
    error_verify = ''
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        if not username or len(username) < 3:
            error_username = "That's not a valid username"
            if not password or len(password) < 3:
                error_password = "That's not a valid password"   
            if not verify:
                error_verify = "Passwords don't match" 
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                error_username = "A user with that username already exists"
            if not password or len(password) < 3:
                error_password = "That's not a valid password" 
            if not verify or password != verify:
                error_verify = "Passwords don't match" 
        
        if not error_username and not error_password and not error_verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:    
            return render_template('signup.html', title="Signup", 
                  username=username, error_username=error_username, error_password=error_password, error_verify=error_verify)           
    else:
        return render_template('signup.html', title="Signup")  

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')         

@app.route('/blog')
def list_blogs():

    if request.args.get('id'):
        id = request.args.get('id')
        blog = Blog.query.filter_by(id=id).first()
        return render_template('blog_entry.html',title="blog.title", blog=blog) 
    elif request.args.get('user'): 
        username = request.args.get('user')
        blogs =  Blog.query.join(User, Blog.owner_id==User.id).filter(User.username==username)
        return render_template('singleUser.html',title="Blog posts!", blogs=blogs) 
    else:
        blogs = Blog.query.order_by(db.desc(Blog.reg_date)).all()
        return render_template('blog_list.html',title="Buid a Blog", blogs=blogs)

@app.route('/blog', methods=['POST'])
def add_blog():
    blog_title = request.form['blog_title']
    blog_body = request.form['blog_body']
    #Validation for title
    error_title = ''
    error_body = ''
    if not blog_title:
        error_title = "Please fill in the title"
    if not blog_body:
        error_body = "Please fill in the body"      

    if error_title or error_body:
        return render_template('newpost.html',title="Add a Blog Entry", error_title=error_title, error_body=error_body)
    else:    
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        db.session.flush()
        reg_id = new_blog.id

    return redirect('/blog?id=' + str(reg_id))

@app.route('/blog', methods=['GET'])
def show_blog():
    id = request.args.get('id')
    blog = Blog.query.filter_by(id=id).first()
    return render_template('blog_entry.html',title="blog.title", blog=blog) 


@app.route('/newpost')
def newpost_form():
    return render_template('newpost.html',title="Add a Blog Entry")

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html',title="Blog users!", users=users)



if __name__ == '__main__':
    app.run()