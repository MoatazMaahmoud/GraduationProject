from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
#stringfield to type strings,passwordfield to type passwords
#submitfield to click submit,boolean for the rememberme option
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,IntegerField,FloatField
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

class UpdateAccountForm(FlaskForm):
    username=StringField('Username',
                         validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',
                        validators=[DataRequired(),Email()])
    # the text below :'Update profile picture' is the label will be displayed in the html
    picture=FileField('Update profile picture',validators=[FileAllowed(['jpg','png','jpeg'])])
    submit=SubmitField('Update')
    
    def validate_username(self,username):
        if username.data!=current_user.username:
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose another one.')
    def validate_email(self,email):
        if email.data!=current_user.email:
            email=User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('That email is already taken. Please choose another one.')

class DetectionForm(FlaskForm):
    signal=FileField('Upload your signal file please',validators=[DataRequired(),FileAllowed(['dat'])])
    submit=SubmitField('Detect')

class PredictionForm(FlaskForm):
    #1-fields needed to be filled here
    age=IntegerField('Age',validators=[DataRequired()])
    sex = SelectField('Sex',validators=[DataRequired()], choices=[('', '-- Select an Option --'),('1', 'Male'),
                                                 ('0', 'Female')],default='')

    cp= SelectField('Chest Pain Type',validators=[DataRequired()], choices=[('', '-- Select an Option --'),('1', 'Typical Angina'), ('2', 'Atypical Angina'),
                                                ('3', 'Non-anginal Pain'),('4', 'Asymptomatic')], default='')#-- Value 1: typical angina -- Value 2: atypical angina -- Value 3: non-anginal pain -- Value 4: asymptomatic
    trestbps=IntegerField('Resting Blood Pressure in mm Hg',validators=[DataRequired()])#resting blood pressure
    fbs=SelectField('Fasting Blood Sugar > 120 mg/dl',validators=[DataRequired()],choices=[('', '-- Select an Option --'),
                                                ('1', 'True'), ('0', 'False')], default='')#(fasting blood sugar > 120 mg/dl)  (1 = true; 0 = false)
    cholestrol=IntegerField('Cholestrol',validators=[DataRequired()])
    
    restecg=SelectField('Resting ECG Results',validators=[DataRequired()], choices=[('', '-- Select an Option --'), ('0', 'Normal'), ('1', 'having ST-T wave abnormality')
                                                ,('2','probable or definite left ventricular hypertrophy')], default='') #resting electrocardiographic results-- Value 0: normal-- Value 1: having ST-T wave abnormality (T wave inversions and/or ST elevation or depression of > 0.05 mV) -- Value 2: showing probable or definite left ventricular hypertrophy by Estes' criteria
    thalach=IntegerField('Maximum Heart Rate',validators=[DataRequired()])#maximum heart rate achieved
    exang=SelectField('Exercise Induced Angina',validators=[DataRequired()], choices=[('', '-- Select an Option --'), ('1', 'Yes'), ('0', 'No')], default='')#exercise induced angina (1 = yes; 0 = no)
    oldpeak =FloatField('ST depression induced by exercise relative to rest',
                                                validators=[DataRequired()]) #ST depression induced by exercise relative to rest
    slope=SelectField('Slope of the Peak Exercise ST Segment',validators=[DataRequired()], choices=[('', '-- Select an Option --'), ('1', 'Upsloping'), ('2', 'Flat'),
                                                ('3', 'Downsloping')], default='') #the slope of the peak exercise ST segment -- Value 1: upsloping -- Value 2: flat -- Value 3: downsloping
    ca=SelectField('Number of Vessels Colored by Flourosopy',validators=[DataRequired()], choices=[('', '-- Select an Option --'), ('0', '0'), ('1', '1'),('2', '2'),
                                               ('3', '3')], default='') #number of major vessels (0-3) colored by flourosopy
    thal=SelectField('Thalassemia',validators=[DataRequired()], choices=[('', '-- Select an Option --'), ('3', 'normal'), ('6', 'Fixed defect'),
                                                ('7', 'Reversable defect')], default='') #3 = normal; 6 = fixed defect; 7 = reversable defect
    submit=SubmitField('Predict')
    
class DetectionForm(FlaskForm):
    signal=FileField('Upload your dat file here!',validators=[DataRequired(),FileAllowed(['dat'])])
    submit=SubmitField('Detect')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')