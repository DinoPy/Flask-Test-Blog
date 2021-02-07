from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm,RegisterForm , LoginForm,CommentForm
from flask_gravatar import Gravatar
from functools import wraps
from flask import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blablasecret12313123'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager= LoginManager()
login_manager.init_app(app)

## GARAVATAR ##

gravatar = Gravatar(app,size=100,
                    rating="g",
                    force_default=True,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


##CONFIGURE TABLES -------- DATABASE


class Users(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False, unique=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comment = relationship ("Comment", back_populates="author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column (db.Integer , db.ForeignKey('users.id'))
    author =  relationship("Users", back_populates="posts")
    comments =  relationship("Comment", back_populates = "post")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column (db.Integer, db.ForeignKey ( "users.id"))
    post_id = db.Column (db.Integer, db.ForeignKey ('blog_posts.id'))
    post = relationship ("BlogPost" , back_populates = "comments")
    author = relationship("Users", back_populates = "comment")
    comment = db.Column (db.String)


db.create_all()







@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



# def admin_only(func):
#     @app.errorhandler(403)
#     def admin():
#         if current_user.is_authenticated:
#             if current_user.id == 1:
#                 func()
#             else:
#                 "You don't have access to this page.", 403
#     return admin

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, logged_in = current_user)


@app.route('/register',methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        try:
            new_user = Users(__tablename__ = "Authentication", username = request.form["username"], email = request.form["register_email"],
                                password= generate_password_hash(request.form["password"],"pbkdf2:sha256" , 8))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
        except:
            flash("The email already exists in the data base", "info")
            return redirect(url_for('login'))

    return render_template("register.html",form=register_form, logged_in = current_user)


@app.route('/login', methods = ["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_email= db.session.query(Users).filter_by (email = request.form["login_email"]).first()
        if login_email:
            if check_password_hash(login_email.password, request.form["password"]):
                login_user(login_email)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Incorrect password. Please try again.")
                return redirect(url_for("login"))
        else:
            flash("Incorrect email, please try again.","error")
            return redirect(url_for("login"))
    return render_template("login.html",form=login_form, logged_in = current_user)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods = ["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    comment_form = CommentForm()
    all_comments = Comment.query.all()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to be logged in to comment","info")
            return redirect(url_for('login'))
        comment = (request.form["body"])
        new_comment = Comment(comment=comment, author_id = current_user.id ,post_id = requested_post.id )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("post.html", post=requested_post, logged_in = current_user,
                           form = comment_form, comments=all_comments)


@app.route("/about")
def about():
    return render_template("about.html", logged_in = current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html", logged_in = current_user)


@app.route("/new-post", methods = ["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, logged_in = current_user)


@app.route("/edit-post/<int:post_id>", methods = ["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, logged_in = current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run()
