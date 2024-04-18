from datetime import datetime
from flaskapp import db,login_manager,app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    __tablename__='Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(20), nullable=False)
#     we're simply setting this up with our
# secret key and an expiration time and which by default is 30 minutes and then
# we're returning that token which is created by the dump s method and it also contains a payload of the current user id
# so now let's put a method in place that verifies a token 
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            #load the token
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    #this medicaltextrecords is used to access all medical text records of a user example:
    #user_1.medicaltextrecords ->would return all the records for this user_1
    #patient is used to know which patient has this medical record example:
    #record.patient ->would return the patient that has this record
    medicaltextrecords = db.relationship('MedicalTextRecords', backref='patient', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.address}','{self.city},'{self.country}'')"



class MedicalTextRecords(db.Model):
    __tablename__='MedicalTextRecords'
    id = db.Column(db.Integer, primary_key=True)
    age=db.Column(db.Integer,nullable=False)
    sex = db.Column(db.String(20), nullable=False)
    cp=db.Column(db.String(20),nullable=False)#-- Value 1: typical angina -- Value 2: atypical angina -- Value 3: non-anginal pain -- Value 4: asymptomatic
    trestbps=db.Column(db.Integer,nullable=False)#resting blood pressure
    cholestrol=db.Column(db.Integer,nullable=False)
    fbs=db.Column(db.String(20),nullable=False)#(fasting blood sugar > 120 mg/dl)  (1 = true; 0 = false)
    restecg=db.Column(db.String(100),nullable=False) #resting electrocardiographic results-- Value 0: normal-- Value 1: having ST-T wave abnormality (T wave inversions and/or ST elevation or depression of > 0.05 mV) -- Value 2: showing probable or definite left ventricular hypertrophy by Estes' criteria
    # thalach=db.Column(db.Integer,nullable=False) #maximum heart rate achieved
    exang=db.Column(db.String(3),nullable=False)#exercise induced angina (1 = yes; 0 = no)
    oldpeak =db.Column(db.Float,nullable=False) #ST depression induced by exercise relative to rest
    slope=db.Column(db.String(20),nullable=False) #the slope of the peak exercise ST segment -- Value 1: upsloping -- Value 2: flat -- Value 3: downsloping
    # ca=db.Column(db.Integer,nullable=False) #number of major vessels (0-3) colored by flourosopy
    thal=db.Column(db.String(20),nullable=False) #3 = normal; 6 = fixed defect; 7 = reversable defect
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    result=db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'),nullable=False)

    def __repr__(self):
        return f"MedicalTextRecords('{self.age}','{self.sex}','{self.cp}','{self.trestbps}','{self.cholestrol}','{self.fbs}','{self.restecg}','{self.thalach}','{self.exang}','{self.oldpeak}','{self.slope}','{self.ca}','{self.thal}')"
    