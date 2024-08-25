
from flask import Flask,render_template,redirect,request,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import secrets


# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.secret_key =secrets.token_hex(16)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User table with one-to-many relationship with Post and Comment
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password = db.Column(db.String(120) , nullable=False)

    # One-to-many relationship
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='commenter', lazy=True)


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

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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

    def __repr__(self):
        return f'<Comment {self.content[:20]}>'


# Initialize the database
@app.before_request
def create_tables():
    db.create_all()


@app.route("/")
@app.route("/home")
def home():

    if "username" in session :
    
        username = session['username']
        
        return render_template("home.html",user = username)
    
    else :
        flash("please log in")
        return redirect(url_for("login"))


@app.route("/login",methods = ['POST','GET'])
def login () :

    if "username" in session:
        flash("You are already logged in")
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
                session['username'] = username
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
    if "username" in session :
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
        flash(F"congratulations your account has been created User : {username}")
        return redirect(url_for("home"))
    else : 
        return render_template("signup.html")


@app.route("/logout")
def logout() :

    if "username" not in session :

        return redirect(url_for("login"))

    session.pop("username",None)
    flash("You have been logged out","info")
    return redirect(url_for("login"))



if __name__ == '__main__':
    app.run(debug=True)
