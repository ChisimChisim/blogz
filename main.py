from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password_build-a-blog@localhost:3307/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    reg_date = db.Column(db.DateTime)

    def __init__(self, title, body, reg_date=None):
        self.title = title
        self.body = body
        if reg_date is None:
            reg_date = datetime.utcnow()
        self.reg_date = reg_date

@app.route('/blog')
def index():
    if request.args:
        id = request.args.get('id')
        blog = Blog.query.filter_by(id=id).first()
        return render_template('blog_entry.html',title="blog.title", blog=blog) 
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
        new_blog = Blog(blog_title, blog_body)
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


if __name__ == '__main__':
    app.run()