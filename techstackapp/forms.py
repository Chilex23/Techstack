from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Length

#This class generates fields for contact form
class LoginForm(FlaskForm):
    username = StringField("Your email:", validators=[DataRequired(), Email()])
    pwd = PasswordField("Enter Password:")
    loginbtn = SubmitField("Login")