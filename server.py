# Created by Andy Then 

from flask import Flask, request, redirect, render_template, session, make_response
from flask_session import Session
from datetime import datetime

import boto3
import uuid

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

''' 
Normally key credentials should be stored in environment variables or a configuration file.
For security reasons, they are are not included in this code.
'''
AWSKEY = ''
AWSSECRET = ''

PUBLIC_BUCKET = 'andy-web-public'
STORAGE_URL = 'https://s3.amazonaws.com/' + PUBLIC_BUCKET + '/'

def get_public_bucket():
    s3 = boto3.resource(service_name='s3', region_name='us-east-1', aws_access_key_id=AWSKEY, aws_secret_access_key=AWSSECRET)
    bucket = s3.Bucket(PUBLIC_BUCKET)
    return bucket

def get_table(name):
    client = boto3.resource(service_name='dynamodb', region_name='us-east-1', aws_access_key_id=AWSKEY, aws_secret_access_key=AWSSECRET)
    table = client.Table(name)
    return table

# Simple login check
@app.route('/')
def index():
    if is_logged_in():
        username = session['username']
        return render_template('feed.html', username=username)
    return redirect('/login')

# Shows the feed page
@app.route('/feed')
def feed():
    if not is_logged_in():
        return redirect('/login')
    username = session['username']
    return render_template('feed.html', username=username)

# Profile page. Will redirect if not logged in
@app.route('/profile')
def profile_redirect():
    if not is_logged_in():
        return redirect('/login')
    return redirect(f'/profile/{session["username"]}')

@app.route('/postview')
def postview():
    if not is_logged_in():
        return redirect('/login')
    return render_template('postview.html')


# Function to maintain session
def add_remember_key(email):
    table = get_table("Remember")
    key = str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4())

    item = {"key":key, "email":email}
    table.put_item(Item=item)
    return key

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/post')
def post_page():
    if not is_logged_in():
        return redirect('/login')
    username = session['username']
    return render_template('feed.html', username=username)

#creates a new profile with a blank photo
@app.route('/create_profile', methods=['POST'])
def create_profile():
    table = get_table('users')
    uid = str(uuid.uuid4())
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    upload = {'uid':uid, 'username':username, 'email':email, 'password':password, 'photo':''}

    table.put_item(Item=upload)

    return {'result':'OK', 'username':username, 'uid':uid}


#list all posts
@app.route('/listposts')
def listposts():
    table = get_table('posts')
    posts = []
    for item in table.scan()['Items']:
        parent_pid = item['parent_pid']
        if parent_pid != '':
            continue

        date = item['date']
        text = item['text']
        pid = item['pid']
        uid = item['uid']
        user = get_user_by_uid(uid)
        username = user["username"]
        post = {'date':date, 'text':text, 'username':username, 'uid':uid, 'pid':pid}
        posts.append(post)

    posts_sorted = sorted(posts, key=lambda x: x['date'], reverse=True)

    return {'posts':posts_sorted}

#list only the posts from the user you are looking at
@app.route('/list_users_posts')
def listusersposts():
    table = get_table('posts')
    posts = []
    user_uid = request.args.get('uid')

    for item in table.scan()['Items']:
        if item['uid'] == user_uid:
            date = item['date']
            text = item['text']
            pid = item['pid']
            uid = item['uid']
            user = get_user_by_uid(uid)
            username = user["username"]
            post = {'date':date, 'text':text, 'username':username, 'uid':uid, 'pid':pid}
            posts.append(post)

    posts_sorted = sorted(posts, key=lambda x: x['date'], reverse=True)

    return {'posts':posts_sorted}

#lists the replies of a post
@app.route('/list_replies')
def listreplies():
     table = get_table('posts')
     results = []
     parent_pid = request.args.get('parent_pid')

     for Item in table.scan()['Items']:
         if Item["parent_pid"] != parent_pid:
             continue

         uid = Item['uid']
         date = Item['date']
         text = Item['text']
         user = get_user_by_uid(uid)
         username = user["username"]

         upload = {'date':date, 'text':text, 'username':username}
         results.append(upload)

     results_sorted = sorted(results, key=lambda x: x['date'], reverse=True)
     return {'results':results_sorted}




#create a new post
@app.route('/post', methods=['POST'])
def post():
    uid = session["uid"]
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pid = str(uuid.uuid4())


    table = get_table('posts')
    text = request.form.get('text')
    upload = {'uid':uid, 'text':text, 'date':today, 'pid': pid, 'parent_pid': ''}
    table.put_item(Item=upload)

    return {'results':'OK'}

# reply method
@app.route('/post_reply', methods=['POST'])
def post_reply():
    uid = session["uid"]
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pid = str(uuid.uuid4())


    table = get_table('posts')
    text = request.form.get('text')
    parent_pid = request.form.get('parent_pid')
    upload = {'uid':uid, 'text':text, 'date':today, 'pid': pid, 'parent_pid': parent_pid}
    table.put_item(Item=upload)

    return {'results':'OK'}


def get_user_by_uid(uid):
    table = get_table('users')
    result = table.get_item(Key={"uid":uid})
    if 'Item' not in result:
        return None
    return result['Item']


# Here you can see the replies of a post
@app.route('/replies/<pid>')
def post_view(pid):
     table = get_table('posts')
     item = table.get_item(Key={"pid":pid})
     item = item['Item']

     user = get_user_by_uid(item['uid'])

     return render_template('postview.html', text=item['text'], username=user['username'], date=item['date'], pid=pid)


def get_user_by_email(email):
    table = get_table('users')
    for item in table.scan()['Items']:
        if item['email'] == email:
            return item
    return None

def get_user_by_username(username):
    table = get_table('users')
    for item in table.scan()['Items']:
        if item['username'] == username:
            return item
    return None



@app.route('/login', methods=['GET'])
def login():
    email = request.args.get("email")
    if email is not None:  
        try:
            password = request.args.get("password")
            remember = request.args.get("remember", "no")

            user = get_user_by_email(email)
            if user is None:
                return {'result': 'Email not found'}

            if password != user['password']:
                return {'result': 'Password does not match'}

            # Set session data
            session["email"] = user["email"]
            session["username"] = user["username"]
            session["uid"] = user["uid"]

            # Create response
            response = make_response({'result': 'OK'})
            
            if remember == "no":
                response.set_cookie("remember", "", expires=0)
            else:
                key = add_remember_key(user["email"])
                response.set_cookie("remember", key, max_age=60*60*24*14) #remember for 14 days

            return response
        except Exception as e:
            return {'result': str(e)}

    return render_template('login.html')

def is_logged_in():
    return "uid" in session

def auto_login():
    cookie = request.cookies.get("remember")
    if cookie is None:
        return False

    table = get_table("Remember")
    result = table.get_item(Key={"key": cookie})
    if 'Item' not in result:
        return False

    remember = result['Item']  

    table = get_table("users")
    result = table.get_item(Key={"email": remember["email"]})
    if 'Item' not in result:
        return False

    user = result['Item']  
    session["email"] = user["email"]
    session["username"] = user["username"]

    return True


@app.route('/logout')
def logout():
    session.pop("email", None)
    session.pop("username", None)
    session.pop("uid", None)

    response = make_response(redirect('/'))
    response.delete_cookie("remember")
    return response



@app.route('/profile/<username>')
def profile(username):
    user = get_user_by_username(username)
    uid = user['uid']
    photo = user['photo']
    return render_template('profile.html', username=username, uid=uid, photo=photo, session=session)



@app.route('/uploadfile', methods=['POST'])
def uploadfile():
    bucket = get_public_bucket()
    file = request.files["file"]
    filename = file.filename

    ct = "image/jpeg"
    if filename.endswith(".png"):
        ct = "image/png"

    bucket.upload_fileobj(file, filename, ExtraArgs={"ContentType": ct})

    full_filename = STORAGE_URL + filename

    table = get_table('users')

    uid = session['uid']
    table.update_item(
        Key={'uid': uid},
        UpdateExpression='set photo=:photo',
        ExpressionAttributeValues={':photo': full_filename}
    )

    return {'results': 'OK'}

#delete a post
@app.route('/deletepost', methods=['POST'])
def delete_post():
    if not is_logged_in():
        return {'error': 'Not logged in'}
        
    table = get_table('posts')
    pid = request.form.get('pid')
    
    # Get the post to verify ownership
    response = table.get_item(Key={'pid': pid})
    if 'Item' not in response:
        return {'error': 'Post not found'}
        
    post = response['Item']
    if post['uid'] != session['uid']:
        return {'error': 'Not authorized'}
        
    table.delete_item(Key={'pid': pid})
    
    return {'result': 'OK'}

if __name__ == '__main__':
    app.run(debug=True)