from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
#stringfield to type strings,passwordfield to type passwords
#submitfield to click submit,boolean for the rememberme option
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError,Regexp
from flaskapp.models import User
class RegistrationForm(FlaskForm):
    username=StringField('Username',
                         validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',
                        validators=[DataRequired(),Email()])
    password=PasswordField('Password',
                        validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',
                        validators=[DataRequired(),EqualTo('password')])
    address = StringField('Address', validators=[
        DataRequired(),
        Length(min=10, max=120),
        Regexp(r'^\d+\s+\w+(\s+\w+)*\s+st\.$',
                message="Invalid address format. Please enter in the format 'number name_of_street st.'")])
    city=StringField('City',
                         validators=[DataRequired(),Length(min=2,max=20)])
    country=StringField('Country',
                         validators=[DataRequired(),Length(min=2,max=20)])
    submit=SubmitField('SIGN UP!')
    
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another one.')
    def validate_email(self,email):
        email=User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('That email is already taken. Please choose another one.')

class LoginForm(FlaskForm):
    email=StringField('Email',
                            validators=[DataRequired(),Email()])
    password=PasswordField('Password',
                            validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('LOGIN')