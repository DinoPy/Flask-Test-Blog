from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL , Email, Length
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    username= StringField ("Enter your username",validators=[DataRequired()])
    register_email= StringField("Enter Email", validators=[Email()])
    password= PasswordField("Enter Password", validators=[Length(12,30)])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    login_email = StringField("Enter Email", validators=[DataRequired()])
    password = PasswordField("Enter Password", validators=[DataRequired()])
    submit = SubmitField("Log in")

class CommentForm (FlaskForm):
    body = CKEditorField("Comment",validators=[DataRequired()])
    submit = SubmitField("Comment")