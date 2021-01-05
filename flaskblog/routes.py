import os
import secrets
import time
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, session
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required



uname = ""

@app.route("/")
@app.route("/home")
def home():
    n = 15
    if n > 20:
        bg = "/static/fr.jpg"
    else:
        bg = "/static/bk.jpg"
    return render_template('home.html', bg=bg)

#here is weather html
@app.route("/weather")
def weather():
    return render_template('weather.html', title='Weather')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


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
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    global uname
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        uname = user.username
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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

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
            picture_file = save_picture1(form.picture.data)
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
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



@app.route('/upload/', methods=['GET', 'POST'])
def save_picture1(form_picture):
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
def upload():
    
	basepath = os.path.join(os.path.dirname(__file__), 'static/uploads')
	dirs = os.path.join(basepath,session.get('username'))
    


	if request.method == 'POST':
		flist = request.files.getlist("file[]")
		
		for f in flist:
			try:
				basepath = os.path.join(os.path.dirname(__file__), 'static','uploads',session.get('username'))
				format=f.filename[f.filename.index('.'):]
				fileName=time.time()
				if format in ('.jpg','.png','.jpeg','.HEIC','.jfif'):
					format='.jpg'
					
				if request.values['folder']=='0':
					return render_template('wardrobe.html',alert='Please choose a folder',dirs=dirs)

				elif request.values['folder']=='1':
					if not os.path.isdir(os.path.join(basepath,session.get('username'),request.values['foldername'])):
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername']))
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername'],'video'))
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername'],'photo'))
			except:
				return render_template('wardrobe.html',alert='Please select a file',dirs=dirs)

		return redirect(url_for('upload'))
	return render_template('wardrobe.html',dirs=dirs)

@app.route("/wardrobe", methods=['GET', 'POST'])
@login_required
def wardrobe():
    form = UpdateAccountForm()
    two_dimensional_list = [['001','尼龍'],['002','羽絨'],['003','棉']]
    return render_template('wardrobe.html', form=form, title='Wardrobe',two_dimensional_list=two_dimensional_list)
  
@app.route('/data', methods=['GET', 'POST'])
def data():
    id_value = request.form.get('datasource')
    two_dimensional_list = [['001','尼龍'],['002','羽絨'],['003','棉']]
    def description_value(select):
        for data in two_dimensional_list:
            if data[0] == select:
                return data[1]
    return description_value(id_value)