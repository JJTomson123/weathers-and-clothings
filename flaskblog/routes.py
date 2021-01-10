import os
import secrets
import time
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, session
from flaskblog import app, db, bcrypt
from flaskblog.forms import *
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import csv


with open('./flaskblog/cwb_weather_data/taiwan_cwb.csv', newline='',encoding='utf-8') as f:
    reader = csv.reader(f)
    data = list(reader)
bkweather = "/static/movie/cloudy.mp4"
@app.route("/")
@app.route("/home")
def home():
    cloth_path = "/static/uploads/as/coats/007ca61f4814aea4.JPG"
    n = 15
    if n > 20:
        bg = "/static/fr.jpg"
    else:
        bg = "/static/bk.jpg"
    return render_template('home.html', bg=bg, weat=bkweather, j=cloth_path)

#here is weather html
@app.route("/weather")
def weather():
    with open('./flaskblog/cwb_weather_data/taiwan_cwb.csv', newline='',encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return render_template('weather.html', title='Weather',**locals(), weat=bkweather)
    #return render_template('weather.html', title='Weather')

@app.route("/about")
def about():
    return render_template('about.html', title='About', weat=bkweather)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #here will create new user folder when register
        basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
        os.mkdir(os.path.join(basepath,request.values['username']))
        os.mkdir(os.path.join(basepath,request.values['username'],'pants'))
        os.mkdir(os.path.join(basepath,request.values['username'],'pants','trousers'))
        os.mkdir(os.path.join(basepath,request.values['username'],'pants','shorts'))
        os.mkdir(os.path.join(basepath,request.values['username'],'coats'))
        os.mkdir(os.path.join(basepath,request.values['username'],'coats','coats'))
        os.mkdir(os.path.join(basepath,request.values['username'],'coats','jackets'))
        os.mkdir(os.path.join(basepath,request.values['username'],'coats','rainwear'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, weat=bkweather)


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
    return render_template('login.html', title='Login', form=form, weat=bkweather)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    form = UpdateAccountForm()
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    preuse = str(form.username.data)
    cloth_path = "static/uploads/" + preuse
    picture_path = os.path.join(app.root_path, cloth_path, picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=('uploads/'+ str(current_user.username) + "/" )+ current_user.image_file)
    return render_template('account.html', title='Account',image_file=image_file, form=form, weat=bkweather)




@app.route("/wardrobe", methods=['GET', 'POST'])
@login_required
def wardrobe():
    id_value = request.form.get('datasource')
    two_dimensional_list = [['001','pants'],['002','coats']]
    two_dimensional_list2 = [['001','shorts'],['002','trousers']]
    two_dimensional_list3 = [['001','coats'],['002','jackets'],['003','rainwear']]
    def description_value(select):
        for data in two_dimensional_list:
            if data[0] == select:
                return data[1]
    ip = description_value(id_value)
    form = ImagesForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = upload(form.picture.data,ip)
        db.session.commit()
        return redirect(url_for('wardrobe'))
    return render_template('wardrobe.html', title='Wardrobe', form=form, two_dimensional_list=two_dimensional_list, weat=bkweather)
  

def upload(form_picture, path1):
    form = ImagesForm()
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    pa=str(path1)
    preuse = str(current_user.username)
    cloth_path = "static/uploads/" + preuse+"/"+pa
    picture_path = os.path.join(app.root_path, cloth_path, picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
    
