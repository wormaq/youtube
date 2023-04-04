from flask import Flask, render_template, request, redirect, flash, send_from_directory
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from models import db, Post, MyUser, Favorite, Subscribes
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from wtforms import FileField, SubmitField


app = Flask(__name__)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
app.secret_key = os.urandom(24)

@login_manager.user_loader
def load_user(user_id):
    return MyUser.select().where(MyUser.id==int(user_id)).first()
    

@app.before_request
def before_request():
    db.connect()
    
@app.after_request
def after_request(response):
    db.close()
    return response   

@app.route('/')
def index():
    query = request.args.get('query', '')
    if query:
        all_posts = Post.select().where(Post.title.contains(query))
    else:
        all_posts = Post.select()
    return render_template('index.html', posts=all_posts, query=query)

# UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
# app.config['UPLOAD_FOLDER'] = 'path/to/uploads'
# UPLOAD_FOLDER = 'path/to/uploads'

# UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in app.config['UPLOAD_EXTENSIONS']

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/uploads/<filename>')
def send_uploaded_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        if request.files:
            title = request.form['title']
            description = request.form['description']
            video_file = request.files['video']
            
            filename = secure_filename(video_file.filename)
            print(filename)
            
            video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            


        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
            video_data = f.read()

        if filename:
            Post.create(
                title=title,
                author=current_user,
                description=description,
                video=filename,
                filename=filename
            )
        else:
            pass
        return redirect ('/')
    return render_template('create.html')



def validate_password(password):  
    if len(password) < 8:  
        return False  
    if not re.search("[a-z]", password):  
        return False  
    if not re.search("[0-9]", password):  
        return False  
    return True 


@app.route('/register/', methods = ['GET', 'POST'])
def register():
    if request.method=='POST':
        email = request.form['email'] 
        username = request.form['username'] 
        password = request.form['password'] 
        age = request.form['age'] 
        user = MyUser.select().where(MyUser.email==email).first()
        if user:
            flash('Email address already exists')
            return redirect('/register/')
        else: 
            if validate_password(password):
                MyUser.create(
                    email=email,
                    username = username,
                    password=generate_password_hash(password, method='sha256'),
                    age=age
                )
                return redirect('/login/')
    return render_template('register.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = MyUser.select().where(MyUser.email==email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect('/login/')
        else: 
            login_user(user)
            return redirect('/')
    return render_template('login.html')

@app.route('/<int:id>/update/', methods=('GET', 'POST'))
@login_required
def update(id):
    post = Post.select().where(Post.id==id).first()
    if request.method == 'POST':
        if post:
            if current_user==post.author:
                title = request.form['title']
                description = request.form['description']
                obj = Post.update({
                    Post.title: title,
                    Post.description:description
                }).where(Post.id==id)
                obj.execute()
                return redirect(f'/{id}/')
        return f'Post with id = {id} does not exist'
    return render_template('update.html', post=post)


@app.route('/<int:id>/delete/', methods=('GET', 'POST'))
@login_required
def delete(id):
    post = Post.select().where(Post.id==id).first()
    if request.method == 'POST':
        if post:
            if current_user==post.author:
                post.delete_instance()
                return redirect(f'/')
        return f'You are not owner'
    return render_template('delete.html', post=post)

@app.route('/profile/<int:id>/')
@login_required
def profile(id):
    author = MyUser.select().where(MyUser.id == id).first()
    posts = Post.select().where(Post.author == author)
    if author:
        return render_template('profile.html', user = author, posts = posts)
    else:
        return f'User with id={id} does not exist'
    

@app.route('/profile/')
@login_required
def current_profile():
    posts = Post.select().where(Post.author_id == current_user.id)
    return render_template('profile.html', user = current_user, posts = posts)


@app.route('/<int:id>/')
def retrive_post(id):
    post = Post.select().where(Post.id==id).first()
    if post:
        return render_template('post_detail.html', post=post)
    return f'Post with id = {id} does not exist'

@app.route('/favorite/add/<int:id>')
@login_required
def add_to_favorites(id):
    post = Post.select().where(Post.id==id).first()
    if post:
        favorite = Favorite.select().where(Favorite.post_id==id, Favorite.user_id==current_user.id).first()
        if not favorite:
            Favorite.create(post_id=id, user_id=current_user.id)
        return redirect(f'/{id}/')
        # return render_template ('favorite.html')
    return f'Post with id = {id} does not exist'

@app.route('/favorite/delete/<int:id>')
@login_required
def remove_from_favorites(id):
    post = Post.select().where(Post.id==id).first()
    if post:
        favorite = Favorite.select().where(Favorite.post_id==id, Favorite.user_id==current_user.id).first()
        if favorite:
            favorite.delete_instance()
        return redirect(f'/{id}/')
    return f'Post with id = {id} does not exist'

@app.route('/favorite/')
@login_required
def favorite():
    posts = Post.select().join(Favorite).where(Favorite.user_id == current_user.id)
    if current_user:
        return render_template ('favorite.html', user = current_user, posts = posts)
    
@app.route('/profile/subscribe/<int:id>')
@login_required
def subscribe(id):
    author = MyUser.select().where(MyUser.id == id).first()
    # posts = Post.select().where(Post.author == author)
    if author:
        subscribe = Subscribes.select().where(Subscribes.author_id==id, Subscribes.user_id==current_user.id).first()
        if not subscribe:
            Subscribes.create(author_id = id, user_id = current_user.id)
        return redirect(f'/{id}/')

@app.route('/subscribe/')
@login_required
def subscribe_list():
    author = MyUser.select().join(Subscribes).where(Subscribes.user_id == current_user.id)
    if current_user:
        return render_template ('subscribe.html', user = current_user, author = author)
    




@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/login/')


if __name__ == '__main__':
    app.run(debug=True)