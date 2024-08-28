
from flask import Flask,render_template,redirect,request,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
import secrets
import os

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



@app.route('/create_post', methods=['GET', 'POST'])
def create_post():

    if "user_id" not in session :
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')  # Get the image from the form
        user_id = session.get('user_id')

        if not user_id:
            flash('You need to be logged in to create a post.')
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

        return redirect(url_for('home'))

    return render_template('post_form.html')

@app.route("/all_posts")
def show_all_posts() :

    posts = Post.query.all()

    return render_template("all_post.html",posts = posts)


@app.route('/post/<int:post_id>')
def detail_post(post_id):
    post = Post.query.get_or_404(post_id)
    if "user_id" in session:
        user= User.query.get_or_404(session['user_id'])
    else:
        user=""
    return render_template('post.html', user=user, post=post)


@app.route("/")
@app.route("/home")
def home():

    if "username" in session :

        username = session['username']
        posts = Post.query.all()

        return render_template("home.html",user = username,posts=posts)


    else :
        flash("Please Login!")
        return redirect(url_for("login"))


@app.route("/login",methods = ['POST','GET'])
def login () :

    if "username" in session:
        flash("You Are Already Logged In!")
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
                flash("Login successful!")
                return redirect(url_for("home"))
            else:
                print("Password comparison failed")  # Debugging
                flash("Invalid credentials, please try again.")
        else:
            print("User not found")  # Debugging
            flash("Invalid username, please try again.")

    return render_template("login.html")



@app.route("/sign-up",methods = ["POST","GET"])
def signup() :
    if "user_id" in session :
        flash("first you need to log out to sign up")
        return redirect(url_for('home'))

    if request.method == 'POST' and "sign_up" in request.form :

        username = request.form['username']
        if User.query.filter_by(username=username).first() :
            flash("this username is alredy taken","info")
            return redirect(url_for("signup"))
        password = request.form['password']
        # hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(username=username, password=password)
        
        db.session.add(new_user)
        db.session.commit()
        
        session["username"] = username
        session["password"] = password
        new_user.set_auth_true()

        flash(F"congratulations your account has been created User : {username}")
        return redirect(url_for("home"))
    else : 
        return render_template("signup.html")


@app.route("/logout/<pk>")
def logout(pk) :

    if "username" not in session :

        return redirect(url_for("login"))
    
    user = User.query.filter_by(id=pk)
    user.set_auth_false()

    session.pop("username",None)
    flash("You have been logged out","info")
    return redirect(url_for("login"))



if __name__ == '__main__':
    app.run(debug=True)
