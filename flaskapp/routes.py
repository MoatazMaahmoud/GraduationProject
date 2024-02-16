import os
import secrets
from PIL import Image
from flask import  render_template, url_for, flash, redirect,request
from flaskapp import app,db,bcrypt
from flaskapp.models import User,MedicalTextRecords
from flaskapp.forms import RegistrationForm, LoginForm,UpdateAccountForm,PredictionForm,DetectionForm
from flask_login import login_user, current_user, logout_user, login_required

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
    return render_template('prediction.html',form=form)

@app.route("/detection", methods=['GET', 'POST'])
@login_required
def detection():
    form=DetectionForm()
    return render_template('detection.html',form=form)