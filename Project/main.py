from flask import Flask, render_template, request, redirect, url_for, session
from collections import OrderedDict
#import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

'''
Firestore documentation:
https://firebase.google.com/docs/firestore
API:
https://googleapis.dev/python/firestore/latest/index.html
'''

# Use the application default credentials
cred = credentials.Certificate("gc_privatekey.json")
firebase_admin.initialize_app(cred)
db_firestore = firestore.client()

app = Flask(__name__)
app.secret_key = "hello"


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']


        #Get the document with the entered username
        doc_ref = db_firestore.collection(u'users').document(username)
        doc = doc_ref.get()

        #Check if there is a document with that username in the database
        if doc.exists:
            #If there is, check if the passwords match
            db_pass = doc.get('password')
            if db_pass == password:
                #If passwords match, log in.
                #Send all user information to template.
                db_username = doc.get('username')
                db_email = doc.get('email')
                db_usertype = doc.get('usertype')
                session['usertype'] = doc.get('usertype')
                return render_template('manage.html', username=db_username, email=db_email, usertype=db_usertype)

    return render_template('login.html')



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    '''
    TODO:
    - Add validation to check if user already exists in the database.
    - Alert to let them know their account was successfully created.
    '''

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        usertype = request.form['usertype']

        # NEW CODE USING FIRESTORE
        doc_ref = db_firestore.collection(u'users').document(username)
        doc_ref.set({
            u'username': username,
            u'email': email,
            u'password': password,
            u'usertype': usertype
        })
        return render_template('login.html', error=None)

    return render_template('signup.html', error=None)



@app.route('/manage', methods=['POST', 'GET'])
def manage():

    return render_template('manage.html', error=None)

"""
To update data for an existing entry use the update() method.
db.child("users").child("Morty").update({"name": "Mortiest Morty"})

To create your own keys use the set() method. The key in the example below is "Morty".

data = {"name": "Mortimer 'Morty' Smith"}
db.child("users").child("Morty").set(data)

push
To save data with a unique, auto-generated, timestamp-based key, use the push() method.

data = {"name": "Mortimer 'Morty' Smith"}
db.child("users").push(data)

Source:
https://github.com/thisbejim/Pyrebase
"""



@app.route('/create', methods=['POST', 'GET'])
def create():

    user = session["usertype"]
    if request.method == 'POST':
        postcategory = request.form['p-category']
        posttitle = request.form['p-title']
        postcontent = request.form['post-content']
        posttag = request.form['p-tag']


        # NEW CODE USING FIRESTORE
        doc_ref = db_firestore.collection(u'posts').document(posttitle)
        doc_ref.set({
            u'title': posttitle,
            u'category': postcategory,
            u'content': postcontent,
            u'tags': posttag

        })
        return redirect(url_for('create', username=user))


    return render_template('create.html', username=user)



@app.route('/all_categories', methods=['POST', 'GET'])
def categories():
    all_categories = db_firestore.collection("categories").stream()

    return render_template('all_categories.html', all_categories=all_categories, error=None)



@app.route('/results', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        '''
        TODO: Get elif for categories to work.
        '''

        if 'tags' in request.form:
            searchInput = request.form['filterValue']
            tags = searchInput.split("#")

            #GET DATA STREAM
            posts = db_firestore.collection("posts").where("tags", "array_contains_any", tags).stream()
            

            return render_template('results.html', type='tags', tags=tags, posts=posts)
            
        elif 'category' in request.form:
            filterValue = request.form['category']

            #GET DATA STREAM
            posts = db_firestore.collection("posts").where("category", "==", filterValue)

            return render_template('results.html', type='category', filterValue=filterValue)

    return render_template('results.html', error=None)

if __name__ == "__main__":
    app.run(debug=True)
