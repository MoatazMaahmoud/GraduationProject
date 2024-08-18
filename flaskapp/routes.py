import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from keras.models import Model
from keras import backend as K
import wfdb
import os
import secrets
import pickle
import numpy as np
from flask import jsonify
from PIL import Image
from flask import  render_template, url_for, flash, redirect,request
from flaskapp import app,db,bcrypt,mail
from flaskapp.models import User,MedicalTextRecords,MedicalSignalRecords
from flaskapp.forms import RegistrationForm, LoginForm,UpdateAccountForm,PredictionForm,DetectionForm,RequestResetForm,ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from flaskapp.attributes import dictionary
from flask_mail import Message
import numpy as np
prediction_model=pickle.load(open('./flaskapp/multiclass_model.pkl','rb'))

# Define any custom objects or layers here
custom_objects = {
    'K': K
}
detection_model = load_model("./MLII-balancedNotWeighted16batch25ep-lowtrainparam.hdf5", custom_objects=custom_objects)
class_labels = {
    'N': 'Normal beat',
    'V': 'Premature ventricular contraction',
    '/': 'Paced beat',
    'A': 'Atrial premature contraction',
    'F': 'Fusion of ventricular and normal beat',
    '~': 'Signal quality change'
}


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")

def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    #if user accessed login,register pages while he is logged in already redirect him on login page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                    address=form.address.data,city=form.city.data,country=form.country.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')       
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
#save pic function takes the form.picture.data then
#changes its name to a random hex and adds its original extension
#saves the pic in a path of the app
#opens the passed image then resize it to 125,125
#saves the picture_path
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    #form_picture.save(picture_path)
    output_size = (125, 125)
    i = Image.open(form_picture)
    #resize it to 125x125
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



def load_and_preprocess_dat(record_name, sample_length=256):
    # Read the .hea and .dat files using wfdb
    record = wfdb.rdsamp(record_name)
    data = record[0]

    print(f"Original data shape: {data.shape}")

    # Ensure the data is in the required shape (sample_length, 1)
    if data.shape[0] > sample_length:
        data = data[:sample_length, 0]  # Assuming single channel ECG data
    elif data.shape[0] < sample_length:
        data = np.pad(data[:, 0], (0, sample_length - data.shape[0]), 'constant')  # Assuming single channel ECG data

    data = np.expand_dims(data, axis=0)  # Add batch dimension
    data = np.expand_dims(data, axis=2)  # Add channel dimension

    print(f"Preprocessed data shape: {data.shape}")

    return data


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    #update form
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        #update ith the new data in the form fields
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    #display the current email,username in the email,username fields
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    #path of the current user's image
    image_file=url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title='My account',image_file=image_file,form=form)

def load_and_preprocess_dat(record_name, sample_length=256):
    # Read the .hea and .dat files using wfdb
    record = wfdb.rdsamp(record_name)
    data = record[0]

    print(f"Original data shape: {data.shape}")

    # Ensure the data is in the required shape (sample_length, 1)
    if data.shape[0] > sample_length:
        data = data[:sample_length, 0]  # Assuming single channel ECG data
    elif data.shape[0] < sample_length:
        data = np.pad(data[:, 0], (0, sample_length - data.shape[0]), 'constant')  # Assuming single channel ECG data

    data = np.expand_dims(data, axis=0)  # Add batch dimension
    data = np.expand_dims(data, axis=2)  # Add channel dimension

    print(f"Preprocessed data shape: {data.shape}")

    return data

@app.route("/detection", methods=['GET', 'POST'])
@login_required
def detection():
    form = DetectionForm()
    
    if form.validate_on_submit():
        if form.signal.data:
            # Generate a random hex to be used as the new filename
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(form.signal.data.filename)
            signal_fn = random_hex + f_ext

            # Ensure the filename is secure and save the file
            signal_path = os.path.join(app.root_path, 'static/signal_files', signal_fn)
            form.signal.data.save(signal_path)

            # Use the specified directory
            mit_bih_directory = r'C:/Users/ALEX STORE/Desktop/MIT-BIH'
            signal_base = os.path.join(mit_bih_directory, os.path.splitext(form.signal.data.filename)[0])

            # Load the .dat file and process it for prediction
            try:
                signal_data = load_and_preprocess_dat(signal_base)
            except Exception as e:
                flash(f'Error processing the uploaded file: {e}', 'danger')
                return redirect(url_for('detection'))

            # Make prediction using the detection model
            result = detection_model.predict(signal_data)
            # Extract the prediction result (take the class with highest probability)
            result_class_index = np.argmax(result, axis=-1)
            predicted_class_symbol = list(class_labels.keys())[result_class_index[0][0]]
            predicted_class_string = class_labels[predicted_class_symbol]

            # Save the filename and result in the database
            record = MedicalSignalRecords(signal_file=signal_fn, result=predicted_class_string, user_id=current_user.id)
            db.session.add(record)
            db.session.commit()

            flash('Your file has been uploaded and processed!', 'success')
            # Pass the result to the detection_result page via URL parameter
            return redirect(url_for('detection_result', result=predicted_class_string))

    return render_template('detection.html', title='Detection', form=form)


@app.route("/detection_result", methods=['GET'])
@login_required
def detection_result():
    # Retrieve the prediction result from the URL parameter
    result = request.args.get('result', None)
    if result is None:
        flash('No result found.', 'danger')
        return redirect(url_for('detection'))

    return render_template('detection_result.html', result=result)


                           

@app.route("/prediction", methods=['GET', 'POST'])
@login_required
def prediction():
    form=PredictionForm()
    if form.validate_on_submit():
        # Get the label for 'sex' based on the selected value from the form
        sex_label = dictionary['sex']['choices'].get(form.sex.data)

        # Get the label for 'cp' based on the selected value from the form
        cp_label = dictionary['cp']['choices'].get(form.cp.data)

        # Get the label for 'fbs' based on the selected value from the form
        fbs_label = dictionary['fbs']['choices'].get(form.fbs.data)

        # Get the label for 'restecg' based on the selected value from the form
        restecg_label = dictionary['restecg']['choices'].get(form.restecg.data)

        # Get the label for 'exang' based on the selected value from the form
        exang_label = dictionary['exang']['choices'].get(form.exang.data)

        # Get the label for 'slope' based on the selected value from the form
        slope_label = dictionary['slope']['choices'].get(form.slope.data)

        # Get the label for 'thal' based on the selected value from the form
        thal_label = dictionary['thal']['choices'].get(form.thal.data)
        age = form.age.data
        sex = form.sex.data
        cp = form.cp.data
        trestbps = form.trestbps.data
        cholestrol = form.cholestrol.data
        fbs = form.fbs.data
        restecg = form.restecg.data
        thalach=form.thalach.data
        exang = form.exang.data
        oldpeak = form.oldpeak.data
        slope = form.slope.data
        ca=form.ca.data
        thal = form.thal.data
       # Example: Ensure input shape and type
        input_data = [[age, sex, cp, trestbps, cholestrol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]]
        input_data = np.array(input_data, dtype=np.float32)  # Convert to numpy array with float32 type

        # Perform the prediction
        prediction = prediction_model.predict(input_data)
        result = int(prediction[0]) 
        string_result="none"  
        if result == 0:
            string_result = "Healthy, Not Candidate to heart disease"
        elif result == 1:
            string_result = "Mild Heart Disease"
        elif result == 2:
            string_result = "Moderate Heart Disease"
        elif result == 3:
            string_result = "Severe Heart Disease"
        elif result == 4:
            string_result = "Very Severe Heart Disease"
        else:
            string_result = "Unknown result"  # In case result is outside the expected range
        # Assuming other values are directly mapped without conversion
        medicalrecord = MedicalTextRecords(
            age=form.age.data,
            sex=sex_label,  # Use the label instead of the value from the form
            cp=cp_label,
            trestbps=form.trestbps.data,
            cholestrol=form.cholestrol.data,
            fbs=fbs_label,
            restecg=restecg_label,
            thalach=form.thalach.data,
            exang=exang_label,
            oldpeak=form.oldpeak.data,
            slope=slope_label,
            ca=form.ca.data,
            thal=thal_label,
            prediction_result=string_result,
            patient=current_user
        )
        db.session.add(medicalrecord)
        db.session.commit()
        # Redirect to the prediction result page
        return redirect(url_for('prediction_result', prediction=result))
    return render_template('prediction.html',form=form)

@app.route("/prediction/result/<int:prediction>", methods=['GET'])
@login_required
def prediction_result(prediction):
    # Retrieve the prediction result from the URL parameter
    return render_template('prediction_result.html', prediction=prediction)

# @app.route("/predict", methods=['GET', 'POST'])
# @login_required
# def predict():
#     if request.method == 'POST':
#         # Extracting form data
#         age = request.form.get('age', type=int)
#         sex = request.form.get('sex', type=int)
#         cp = request.form.get('cp', type=int)
#         trestbps = request.form.get('trestbps', type=int)
#         cholestrol = request.form.get('cholestrol', type=int)
#         fbs = request.form.get('fbs', type=int)
#         restecg = request.form.get('restecg', type=int)
#         # thalach = request.form.get('thalach', type=int)
#         exang = request.form.get('exang', type=int)
#         oldpeak = request.form.get('oldpeak', type=float)
#         slope = request.form.get('slope', type=int)
#         # ca = request.form.get('ca', type=int)
#         thal = request.form.get('thal', type=int)
        
#         # Make prediction
#         prediction = model.predict([[age, sex, cp, trestbps, cholestrol, fbs, restecg, exang, oldpeak, slope,thal]])
        
#         # Respond with prediction result
#         return jsonify({"prediction": prediction.tolist()})  # Convert to list for JSON serialization



@app.route("/result", methods=['GET', 'POST'])
@login_required
def result():
    return render_template('result.html')


@app.route("/mymedicalrecords", methods=['GET', 'POST'])
@login_required
def mymedicalrecords():
    user_medical_records = current_user.medicaltextrecords
    
    return render_template('mymedicalrecords.html',user_medical_records=user_medical_records)


@app.route("/mysignalrecords")
@login_required  # Ensures that only logged-in users can access this page
def mysignalrecords():
    # Query to get all signal records for the current user
    records = MedicalSignalRecords.query.with_entities(
        MedicalSignalRecords.date_posted, MedicalSignalRecords.result
    ).filter_by(user_id=current_user.id).all()
    
    return render_template('mysignalrecords.html', records=records)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
