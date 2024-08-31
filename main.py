
from flask import Flask,render_template,redirect,request,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    comments = db.relationship('Comment',cascade="all, delete-orphan", backref='post', lazy=True)

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

        if image and image.filename != '':
            if allowed_file(image.filename):  # Check if an image was uploaded
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
            else:
                flash("this file format is not supported only jpeg,jpg,png is accepted")
                return redirect(url_for('create_post'))
        else:
            image_path = DEFAULT_IMAGE_PATH  # Use default image if no image was uploaded

        new_post = Post(title=title, content=content, image=image_path, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        flash(translations[session['language']]['created_successfully']) 
        return redirect(url_for('home'))

    return render_template('post-create.html',user=session['username'], user_id = session['user_id'],
                           translations=translations[session["language"]])


@app.route('/post/<int:post_id>', methods = ['POST' , 'GET'])
def detail_post(post_id):
    if "username" not in session:
        flash("Please Login!")
        return redirect(url_for("login"))
    
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

@app.route("/profile", methods=['POST' , 'GET'])
def profile() :
    if "username" not in session :
        flash(translations[session["language"]]['need_to_login'])

        return redirect(url_for('login'))
    
    else :
        user_id = session["user_id"]
        user = User.query.filter_by(id = user_id)
        user_post = Post.query.filter_by(user_id = user_id)

        return render_template("profile.html" , user = session['username'], translations=translations[session["language"]],
                                user_specs=user , user_posts = user_post, user_id = session['user_id'])


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

@app.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author.id != session.get('user_id'):
        flash('You are not authorized to delete this post')
        return redirect(url_for('profile'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!')

    return redirect(url_for('profile'))

@app.route('/post/update/<int:post_id>', methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    print(post.image)
    if post.author.id != session.get('user_id'):
        flash('You are not authorized to update this post')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']


        # if image and image.filename != '':  # Check if an image was uploaded
        #     filename = secure_filename(image.filename)
        #     image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #     image.save(image_path)
        # else:
        #     image_path = DEFAULT_IMAGE_PATH  # Use default image if no image was uploaded


        # Handle image upload if a new image is provided
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                if allowed_file(file.filename):
                    # Remove the old image file
                    if post.image:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)

                    # Save the new image and update the path
                    filename = secure_filename(file.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(image_path)
                    post.image = image_path  # Update the image path in the database
                else:
                    flash("this file format is not supported only jpeg,jpg,png is accepted")
                    return(redirect(url_for('update_post',post_id = post.id)))
        # Commit changes to the database
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('profile'))

    #return render_template('update_post.html', post=post)

    return render_template('update_post.html',translations=translations[session["language"]], post=post,
                            user_id= session['user_id'], user = session['username'])



# Route to change username
@app.route('/change_username', methods=['GET', 'POST'])
def change_username():

    if "username" not in session :
        flash(translations[session["language"]]['need_to_login'])
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_username = request.form.get('current_username')
        new_username = request.form.get('new_username')

        #ensure that the authenticated user is doing the precdure
        if current_username != session['username'] :
            flash("your current username is not correct")
            return redirect(url_for('change_username'))
        else:
        # Find user by current username
            user = User.query.filter_by(username=current_username).first()

        if user:
            # Check if new username is not already taken
            if User.query.filter_by(username=new_username).first():
                flash('Username already taken. Please choose a different username.', 'error')
            else:
                user.username = new_username
                db.session.commit()
                session["username"] = user.username
                flash('Username successfully changed!', 'success')
                return redirect(url_for('profile'))  # Redirect to a user profile page
        else:
            flash('Current username not found.', 'error')

    return render_template('change_username.html')


# Route to change password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if "username" not in session :
        flash(translations[session["language"]]['need_to_login'])
        return redirect(url_for('login'))
        #ensure that the authenticated user is doing the precdure


    if request.method == 'POST':
        current_username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        #ensure that the authenticated user is doing the precdure        
        if current_username != session['username'] :
            flash("your current username is not correct")
            return redirect(url_for('change_password'))
        else:
            # Find user by username
            user = User.query.filter_by(username=current_username).first()

        if user and check_password_hash(user._password, current_password):
            user.password = new_password  # Password setter will hash the new password
            db.session.commit()
            flash('Password successfully changed!', 'success')
            return redirect(url_for('profile'))  # Redirect to a user profile page
        else:
            flash('Incorrect username or password.', 'error')

    return render_template('change_password.html')



if __name__ == '__main__':
    app.run(debug=True)
