from datetime import datetime
from flaskapp import db,login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    #medicaltextrecords = db.relationship('MedicalTextRecords', backref='Patient', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.address}','{self.city},'{self.country}'')"



class MedicalTextRecords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age=db.Column(db.Integer,nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    cp=db.Column(db.String(10),nullable=False)#-- Value 1: typical angina -- Value 2: atypical angina -- Value 3: non-anginal pain -- Value 4: asymptomatic
    trestbps=db.Column(db.Integer,nullable=False)#resting blood pressure
    cholestrol=db.Column(db.Integer,nullable=False)
    fbs=db.Column(db.Integer,nullable=False)#(fasting blood sugar > 120 mg/dl)  (1 = true; 0 = false)
    #restecg=db.Column(db.Integer,nullable=False) #resting electrocardiographic results-- Value 0: normal-- Value 1: having ST-T wave abnormality (T wave inversions and/or ST elevation or depression of > 0.05 mV) -- Value 2: showing probable or definite left ventricular hypertrophy by Estes' criteria
    thalac=db.Column(db.Integer,nullable=False) #maximum heart rate achieved
    exang=db.Column(db.String(3),nullable=False)#exercise induced angina (1 = yes; 0 = no)
    oldpeak =db.Column(db.Float,nullable=False) #ST depression induced by exercise relative to rest
    slope=db.Column(db.String(20),nullable=False) #the slope of the peak exercise ST segment -- Value 1: upsloping -- Value 2: flat -- Value 3: downsloping
    ca=db.Column(db.Integer,nullable=False) #number of major vessels (0-3) colored by flourosopy
    thal=db.Column(db.Integer,nullable=False) #3 = normal; 6 = fixed defect; 7 = reversable defect
    result=db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"MedicalTextRecords('{self.age}', '{self.sex}',)"