
from flask import Flask,render_template,redirect,request,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
import secrets
import os
from translations import translations

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.secret_key =secrets.token_hex(16)



DEFAULT_IMAGE_PATH = 'static/uploads/default_pic/default.jpg'  # Define the default image path
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User table with one-to-many relationship with Post and Comment
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password = db.Column(db.String(120) , nullable=False)
    is_authenticated =db.Column(db.Boolean, default=False, nullable=False)

    # One-to-many relationship
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='commenter', lazy=True)
    
    def set_auth_true(self) :
        self.is_authenticated = True

    def set_auth_false(self) :
        self.is_authenticated = False

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def verify_password(self, password):
        return check_password_hash(self._password, password)
    


# Post table with one-to-many relationship with Comment
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(120), nullable=True)  # New field for storing image path
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_posts', lazy=True))  # Relationship to User model
    # One-to-many relationship
    comments = db.relationship('Comment', backref='post', lazy=True)

    def __repr__(self):
        return f'<Post {self.title}>'

# Comment table with foreign keys to User and Post
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Foreign key to Post
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_comment', lazy=True))  # Relationship to User model

    def __repr__(self):
        return f'<Comment {self.content[:20]}>'


# Initialize the database
@app.before_request
def create_tables():
    db.create_all()
    if not "language" in session:
        session["language"] = 'fa'




@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if "username" not in session :
        return redirect(url_for('login'))
    if "user_id" not in session :
        return redirect(url_for('login'))

    if request.method == 'POST' and "post_submit" in request.form:
        title = request.form['post_title']
        content = request.form['post_description']
        image = request.files.get('post_img')  # Get the image from the form
        user_id = session.get('user_id')

        if not user_id:
            flash(translations[session['language']]['login_to_create']) 
            return redirect(url_for('login'))

        if image and image.filename != '':  # Check if an image was uploaded
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
        else:
            image_path = DEFAULT_IMAGE_PATH  # Use default image if no image was uploaded

        new_post = Post(title=title, content=content, image=image_path, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        flash(translations[session['language']]['created_successfully']) 
        return redirect(url_for('home'))

    return render_template('post-create.html',user=session['username'], user_id = session['user_id'],
                           translations=translations[session["language"]])

@app.route("/all_posts")
def show_all_posts() :

    if "username" in session :
        username = session['username']
        posts = Post.query.all()
    else :
        return redirect(url_for("login"))
    return render_template("all_post.html",user = username,posts = posts)


@app.route('/post/<int:post_id>', methods = ['POST' , 'GET'])
def detail_post(post_id):

    post = Post.query.get_or_404(post_id)
    
    if "user_id" in session:
        user= User.query.get_or_404(session['user_id'])
        user_id = session.get("user_id")
    else:
        user=""

    if request.method == "POST" and "comment_submit" in request.form:
        comment = request.form['comment']
        new_comment = Comment(content = comment , post_id = post_id , user_id =user_id )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('detail_post',post_id = post_id))


    comments = Comment.query.filter_by(post_id = post_id)

    #return render_template('post.html', user=user, post=post,comments = comments)
    return render_template('post.html', user=session['username'], user_id = session['user_id'], post=post,comments = comments,
                           translations=translations[session["language"]])

@app.route('/set_language/<lang>')
def set_language(lang):
    session['language'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route("/")
@app.route("/home")
def home():

    if "username" in session :

        username = session['username']
        user_id = session['user_id']
        posts = Post.query.all()

        return render_template("home.html",user_id= user_id,user = username,posts=posts,
                                translations=translations[session["language"]], lang=session["language"])


    else :
        flash(translations[session['language']]['login_first'])  
        return redirect(url_for("login"))


@app.route("/login",methods = ['POST','GET'])
def login () :

    if "username" in session:
        flash(translations[session['language']]['already_logged_in']) 
        return redirect(url_for("home"))

    if request.method == "POST" and "sign_in" in request.form:
        username = request.form['username']
        password = request.form['password']

        # Query the user by username
        user = User.query.filter_by(username=username).first()

        if user:
            print(f"User found: {user.username}")  # Debugging
            print(f"Entered password: {password}")  # Debugging

            if user.verify_password(password):
                print("Password matched")  # Debugging
                session['user_id'] = user.id  # Store user_id in session
                session['username'] = user.username
                user.set_auth_true()
                flash(translations[session['language']]['login_successful']) 
                return redirect(url_for("home"))
            else:
                print("Password comparison failed")  # Debugging
                flash(translations[session['language']]['wrong_password']) 
        else:
            print("User not found")  # Debugging
            flash(translations[session['language']]['wrong_username']) 

    return render_template("login.html", translations=translations[session["language"]])



@app.route("/sign-up",methods = ["POST","GET"])
def signup() :
    if "user_id" in session :
        flash(translations[session['language']]['logout_before_signup']) 
        return redirect(url_for('home'))

    if request.method == 'POST' and "sign_up" in request.form :

        username = request.form['username']
        if User.query.filter_by(username=username).first() :
            flash(translations[session['language']]['username_alredy taken'],"info") 
            return redirect(url_for("signup"))
        password = request.form['password']
        # hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(username=username, password=password)
        
        db.session.add(new_user)
        db.session.commit()
        
        session["username"] = username
        session["user_id"] = new_user.id
        new_user.set_auth_true()

        flash(translations[session['language']]['congrats_account_created']) 
        return redirect(url_for("home"))
    else : 
        return render_template("signup.html", translations=translations[session["language"]])

@app.route("/profile")
def profile() :
    if "username" not in session :
        flash(translations[session["language"]]['need_to_login'])

        return redirect(url_for('login'))
    else :
        user_id = session["user_id"]
        user = User.query.filter_by(id = user_id)
        user_post = Post.query.filter_by(user_id = user_id)

        return render_template("profile.html" , user = session['username'], translations=translations[session["language"]],
                                user_specs=user , user_posts = user_post)


@app.route("/logout/<pk>")
def logout(pk) :

    if "username" not in session :

        return redirect(url_for("login"))
    
    user = User.query.get_or_404(pk)
    user.set_auth_false()

    session.pop("username",None)
    session.pop("user_id",None)

    flash(translations[session["language"]]['you_logged_out'],"info") 
    return redirect(url_for("login"))

@app.route("/delete-post")
def delete_post():
    return "Test"

@app.route("/edit-post")
def edit_post():
    return "Test"

if __name__ == '__main__':
    app.run(debug=True)
