from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory, jsonify
#from markupsafe import escape
import os

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route("/")
@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/account-settings")
def account_settings():
    return render_template('account-settings.html')

@app.route("/categories")
def categories():
    return render_template('categories.html')

@app.route('/site-settings')
def site_settings():
    return render_template('site-settings.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/home-alter')
def home_alter():
    return render_template('home_alter.html')

@app.route('/home')
def home():
    mini_post_specs=[{'views':1000,'likes':20,'dislikes':10,'comments_num':5,'post_img':"post-01.jpg",'profile_pic':"notification-01.jpg",'post_description': "This is a bird. i saw it in my  way to work, today!", 'profile_name': 'Janice','publish_date': "June 2, 2018 19:PM"},
                {'views':1500,'likes':10,'dislikes':1,'comments_num':2,'post_img':"post-02.jpg",'profile_pic':"notification-02.jpg", 'post_description': "This is something", 'profile_name': 'Emma','publish_date': "July 28, 2018 18:PM"},
                {'views':800,'likes':25,'dislikes':50,'comments_num':1,'post_img':"post-03.jpg",'profile_pic':"notification-03.jpg", 'post_description': "This is something", 'profile_name': 'Janice','publish_date': "June 2, 2018 19:PM"},
                {'views':10200,'likes':204,'dislikes':110,'comments_num':5,'post_img':"post-04.jpg",'profile_pic':"notification-04.jpg",'post_description': "This is something. i saw it in my  way to work, today!", 'profile_name': 'Ali','publish_date': "June 2, 2024 20:PM"}]
    
    return render_template('home.html', mini_post_specs=mini_post_specs)

@app.route('/post')
def post():
    post_specs=[{'views':1000,'likes':20,'dislikes':10,'comments_num':5,'post_img':"post-01.jpg",'profile_pic':"notification-01.jpg"}]
    return render_template('post.html',post_spec=post_specs[0])

@app.route('/chats-list')
def chats_list():
    #category = request.args.get('category')
    category = "general"
    # Fetch chat rooms based on the category
    rooms = get_chat_rooms_for_category(category)  # Implement this function
    return render_template('chats-list.html', category=category, rooms=rooms)

def get_chat_rooms_for_category(category):
    # This is a placeholder function. Implement logic to fetch chat rooms.
    if category == "general":
        return ["Room 1", "Room 2", "Room 3"]
    elif category == "development":
        return ["Dev Room 1", "Dev Room 2"]
    elif category == "bug-reports":
        return ["Bug Room 1"]
    return []

app.run(host='0.0.0.0', port=35000)