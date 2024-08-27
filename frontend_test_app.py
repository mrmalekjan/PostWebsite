from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory, jsonify
#from markupsafe import escape
import os

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/account-settings")
def account_settings():
    return render_template('account-settings.html')

@app.route('/site-settings')
def site_settings():
    return render_template('site-settings.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route("/")
@app.route('/home')
def home():
    username="mammad"
    posts=[{"title":"ssssss", "id":1, "user":{"username":"ali"}, 'image':'static/uploads/360_F_461470323_6TMQSkCCs9XQoTtyer8VCsFypxwRiDGU.jpg'}]
    return render_template("home.html",user = username,posts=posts)

@app.route('/post/<int:post_id>')
def detail_post(post_id):
    post = ""
    return render_template('post_detail.html', post=post)

@app.route('/post')
def post():
    post_specs=[{'post_id':102,'views':1000,'likes':20,'dislikes':10,'comments_num':5,'post_img':"post-01.jpg",'profile_pic':"notification-01.jpg",'post_description': "This is a bird. i saw it in my  way to work, today!", 'profile_name': 'Janice','publish_date': "June 2, 2018 19:PM"},
                {'post_id':82,'views':1500,'likes':10,'dislikes':1,'comments_num':2,'post_img':"post-02.jpg",'profile_pic':"notification-02.jpg", 'post_description': "This is something", 'profile_name': 'Emma','publish_date': "July 28, 2018 18:PM"},
                {'post_id':33,'views':800,'likes':25,'dislikes':50,'comments_num':1,'post_img':"post-03.jpg",'profile_pic':"notification-03.jpg", 'post_description': "This is something", 'profile_name': 'Janice','publish_date': "June 2, 2018 19:PM"},
                {'post_id':122,'views':10200,'likes':204,'dislikes':110,'comments_num':5,'post_img':"post-04.jpg",'profile_pic':"notification-04.jpg",'post_description': "This is something. i saw it in my  way to work, today!", 'profile_name': 'Ali','publish_date': "June 2, 2024 20:PM"}]
    comments=[{'author':'Janice','text':'aslkcniqnpqnqpnqi'}, {'author':'Ali','text':'bdfbdfvdfvsdvaslkcniqnpqnqpnqi'}]
    
    post_id = request.args.get('post_id')
    for post in post_specs:
        if int(post['post_id']) == int(post_id):
            post_spec = post
    return render_template('post.html', user="", post_spec=post_spec, comments=comments)

@app.route('/profile')
def profile():
    # Fetch user data from your database
    user = {'name':'Ali','profile_pic':"notification-03.jpg",'bio':'I am a human being!!', 'post_count':10,
             'post_count':212, 'followers_count':15000, 'following_count':1000, 'cover_photo': 'post-05.jpg'}
    post_specs=[{'title': 'SOME TITLE','post_id':102,'views':1000,'likes':20,'dislikes':10,'comments_num':5,'post_img':"post-01.jpg",'profile_pic':"notification-01.jpg",'post_description': "This is a bird. i saw it in my  way to work, today!", 'profile_name': 'Janice','publish_date': "June 2, 2018 19:PM"},
                {'title': 'SOME TITLE', 'post_id':82,'views':1500,'likes':10,'dislikes':1,'comments_num':2,'post_img':"post-02.jpg",'profile_pic':"notification-02.jpg", 'post_description': "This is something", 'profile_name': 'Emma','publish_date': "July 28, 2018 18:PM"},
                {'title': 'SOME TITLE', 'post_id':33,'views':800,'likes':25,'dislikes':50,'comments_num':1,'post_img':"post-03.jpg",'profile_pic':"notification-03.jpg", 'post_description': "This is something", 'profile_name': 'Janice','publish_date': "June 2, 2018 19:PM"},
                {'title': 'SOME TITLE', 'post_id':122,'views':10200,'likes':204,'dislikes':110,'comments_num':5,'post_img':"post-04.jpg",'profile_pic':"notification-04.jpg",'post_description': "This is something. i saw it in my  way to work, today!", 'profile_name': 'Ali','publish_date': "June 2, 2024 20:PM"}]
    user_posts = post_specs
    return render_template('profile.html', 
                            followers_count=user['followers_count'],
                            following_count=user['following_count'],
                            post_count=user['post_count'],
                            profile_name=user['name'], 
                            profile_pic=user['profile_pic'], 
                            bio=user['bio'],
                            cover_photo=user['cover_photo'], 
                            user_posts=user_posts)


@app.route('/post-create')
def post_create():
    return render_template("post-create.html", user="")


app.run(host='0.0.0.0', port=15000)