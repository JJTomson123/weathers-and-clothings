import os
import secrets
import time
import random
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

#wea = data[50][12]
#wea = "晴"
#wea = "陰"
#wea = ""
wea = "雨"
if wea == "晴":
    bkweather = "/static/movie/sunnyday.mp4"
elif wea == "陰":
    bkweather = "/static/movie/cloudy.mp4"
elif "雨" in list(wea):
    bkweather = "/static/movie/rainyday.mp4"
else:
    bkweather = "/static/movie/sunnycloudy.mp4"

@app.route("/home")
def home():
    temp = (int(data[50][5]) + int(data[50][6]))//2
    username = str(current_user.username)
    path = "/static/uploads/" + username + "/pants/trousers"
    bath = (os.path.dirname(__file__))
    if temp > 20:
        upp = os.path.join(os.path.dirname(__file__), path)
        downp = bath + path
    else:
        upp = "/static/uploads/" + username + "/pants/trousers"
        downp = bath + path
    pdown = random.choice([x for x in os.listdir(downp)])
    down = path + "/" + pdown
    print(down)
    return render_template('home.html', weat=bkweather, down=down)

#here is weather html
@app.route("/")
@app.route("/weather")
def weather():

    return render_template('weather.html', title='Weather',data=data, weat=bkweather)


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
        os.mkdir(os.path.join(basepath,request.values['username'],'褲'))
        os.mkdir(os.path.join(basepath,request.values['username'],'褲','短褲'))
        os.mkdir(os.path.join(basepath,request.values['username'],'褲','長褲'))
        os.mkdir(os.path.join(basepath,request.values['username'],'上衣'))
        os.mkdir(os.path.join(basepath,request.values['username'],'上衣','大褸'))
        os.mkdir(os.path.join(basepath,request.values['username'],'上衣','短袖'))
        os.mkdir(os.path.join(basepath,request.values['username'],'上衣','雨衣'))
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
    two_dimensional_list = [['001','褲/短褲'],['002','褲/長褲'],['003','上衣/大褸'],['004','上衣/短袖'],['005','上衣/雨衣']]

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
    
@app.route('/album/', methods=['POST', 'GET'])
def album():

	colspan=int(int(session.get('width'))/150)
	if colspan>7:
		colspan=7
	basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
	dirs=os.listdir(os.path.join(basepath,session.get('username')))
	dirs.insert(0,'ALL')
	dirs.insert(0,'')

	dict2={} #record all folder has what number name

	for dir in dirs:
		if dir == "ALL" or dir == '':
			continue
		dict2[dir]={'photo':[],'video':[]}
		path=os.path.join(basepath,session.get('username'),dir,'photo')
		for lists in os.listdir(path):
			dict2[dir]['photo'].append(lists)
		path=os.path.join(basepath,session.get('username'),dir,'video')
		for lists in os.listdir(path):
			dict2[dir]['video'].append(lists)
	if request.method == 'POST':
		if request.values['folder']!='0' and request.values['folder']!='1':
			return render_template('album.html',dirs=dirs,colspan=colspan, \
				filefolder=[dirs[int(request.values['folder'])]],files=dict2,username=session.get('username'))
		elif request.values['folder'] =='1':
			return render_template('album.html',dirs=dirs, colspan=colspan,\
				filefolder=dirs[2:],files=dict2,username=session.get('username'))
	return render_template('album.html',dirs=dirs, files=dict2, filefolder=dirs[2:],colspan=colspan,username=session.get('username'))