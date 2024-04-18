import os
import secrets
import pickle
from flask import jsonify
from PIL import Image
from flask import  render_template, url_for, flash, redirect,request
from flaskapp import app,db,bcrypt,mail
from flaskapp.models import User,MedicalTextRecords
from flaskapp.forms import RegistrationForm, LoginForm,UpdateAccountForm,PredictionForm,DetectionForm,RequestResetForm,ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from flaskapp.attributes import dictionary
from flask_mail import Message

model=pickle.load(open('./flaskapp/model.pkl','rb'))

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
@login_required
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
        exang = form.exang.data
        oldpeak = form.oldpeak.data
        slope = form.slope.data
        thal = form.thal.data
         # Make prediction
        prediction = model.predict([[age, sex, cp, trestbps, cholestrol, fbs, restecg, exang, oldpeak, slope, thal]]) 
        result = int(prediction[0])   
        # Assuming other values are directly mapped without conversion
        medicalrecord = MedicalTextRecords(
            age=form.age.data,
            sex=sex_label,  # Use the label instead of the value from the form
            cp=cp_label,
            trestbps=form.trestbps.data,
            cholestrol=form.cholestrol.data,
            fbs=fbs_label,
            restecg=restecg_label,
            # thalach=form.thalach.data,
            exang=exang_label,
            oldpeak=form.oldpeak.data,
            slope=slope_label,
            # ca=form.ca.data,
            thal=thal_label,
            result=result,
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

@app.route("/detection", methods=['GET', 'POST'])
@login_required
def detection():
    form=DetectionForm()
    return render_template('detection.html',form=form)

@app.route("/result", methods=['GET', 'POST'])
@login_required
def result():
    return render_template('result.html')


@app.route("/mymedicalrecords", methods=['GET', 'POST'])
@login_required
def mymedicalrecords():
    user_medical_records = current_user.medicaltextrecords
    
    return render_template('mymedicalrecords.html',user_medical_records=user_medical_records)

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