from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item, User

from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# import flask.ext.login as flask_login


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('google_client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catelog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwebsite.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

############################################### helpers 
def validate_category_name(name):
    return True

def validate_category_descrip(description):
    return True

### validate items inputs from users

def validate_item_name(name):
    return True

def validate_item_descrip(description):
    return True


def validate_item_category(cate_index):
    cates = session.query(Category).order_by(desc(Category.created)).all()
    cate = cates[cate_index]
    return cate.id

# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

######################################################### routing and handlers
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))

## google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('google_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

## google logout
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

########## facebook log in 
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

########## facebook log out
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

############################################################################# end of connect

########################################################### JSON API
@app.route('/category/json/')
@app.route('/category/JSON/')
def showCategoriesJSON():
    cates = session.query(Category).order_by(desc(Category.created)).all()
    return jsonify(Categories=[i.serialize for i in cates])

@app.route('/category/<string:cate>/items/json/', methods=['GET'])
@app.route('/category/<string:cate>/items/JSON/', methods=['GET'])
def viewItemsJSON(cate):
    cate = session.query(Category).filter_by(name=cate).one()
    items = session.query(Item).filter_by(category_id=cate.id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/category/<string:cate>/item/<string:item>/json/', methods=['GET'])
@app.route('/category/<string:cate>/item/<string:item>/JSON/', methods=['GET'])
def viewItemJSON(cate, item):
    cate = session.query(Category).filter_by(name=cate).one()
    item = session.query(Item).filter_by(category_id=cate.id, name=item).first()
    return jsonify(Items=item.serialize)

############################################################# routing
@app.route('/')
@app.route('/category/')
def showCategories():
    cates = session.query(Category).order_by(desc(Category.created)).all()
    items = session.query(Item).order_by(desc(Item.created)).limit(10)
    return render_template('frontpage.html', clicked_cate=None, cates = cates, items=items, items_title="Lasted items")

# Create a new restaurant
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if validate_category_name(name) and validate_category_descrip(description):
            #dummy_user = session.query(User).filter_by(name="ZGH").one()

            newCate = Category(
                name=name, description=description, user_id=login_session['user_id'])
            
            session.add(newCate)

            flash('New Category %s Successfully Created' % newCate.name)
            session.commit()

            return redirect(url_for('showCategories'))
        else:
          error ="Some inputs are not valid"

          return render_template('new_category.html', name=name, description=description , error = error )

    else:
        return render_template('new_category.html')

# # Edit a restaurant
@app.route('/category/<string:cate>/', methods=['GET'])
def viewCategory(cate):
    cate = session.query(Category).filter_by(name=cate).one()
    if request.method == "GET": 
        return render_template('view_category.html', cate = cate)
   

# # Edit a restaurant
@app.route('/category/<string:cate>/edit/', methods=['GET', 'POST'])
def editCategory(cate):
    editCategory = session.query(Category).filter_by(name=cate).one()
    if 'username' not in login_session:
        return redirect('/login')

    if editCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"

    if not editCategory:
        return render_template("404.html", requested_url=request.url)

    if request.method == "GET": 
        return render_template('edit_category.html', cate = editCategory)
    else:
        name = request.form['name']
        description = request.form['description']
        if validate_category_name(name) and validate_category_descrip(description):
            editCategory.name = name
            editCategory.description = description
            session.add(editCategory)

            flash('Category %s Successfully Updated' % editCategory.name)
            session.commit()
            return redirect(url_for('showCategories'))
        else:
          error ="Some inputs are not valid"
          return render_template('edit_category.html', cate=editCategory , error = error )

# # Edit a restaurant
@app.route('/category/<string:cate>/delete/', methods=['GET', 'POST'])
def deleteCategory(cate):
    cate = session.query(Category).filter_by(name=cate).one()

    if 'username' not in login_session:
        return redirect('/login')

    if cate.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"

    if request.method == "GET": 
        return render_template('delete_category.html', cate = cate)
    elif request.method=="POST":
        session.delete(cate)


        flash('Category %s Successfully deleted' % cate.name)
        session.commit()

        ## delete the items in that category
        items = session.query(Item).filter_by(category_id=cate.id).all()
        for item in items:
            session.delete(item)
            session.commit()

        flash('All items in Category %s are successfully deleted' % cate.name)
        return redirect(url_for('showCategories'))
        

# # show the items of a category
@app.route('/category/<string:cate>/items/', methods=['GET'])
def viewItems(cate):
    cate = session.query(Category).filter_by(name=cate).one()
    items = session.query(Item).filter_by(category_id=cate.id).order_by(desc(Item.created)).all()

    cates = session.query(Category).order_by(desc(Category.created)).all()

    if (not cate):
        return render_template("404.html", requested_url=request.url)
    
    if request.method == "GET": 
        return render_template('frontpage.html', items= items, cates=cates,
         clicked_cate = cate, items_title="Items in %s" % cate.name)

## view a item of a category
@app.route('/category/<string:cate>/item/<string:item>/', methods=['GET'])
def viewItem(cate, item):
    cate = session.query(Category).filter_by(name=cate).one()
    item = session.query(Item).filter_by(category_id=cate.id, name=item).first()

    if (not cate) or (not item):
        return render_template("404.html", requested_url=request.url)

    if request.method == "GET": 
        return render_template('view_item.html', item = item)

@app.route('/item/new/', methods=['GET', 'POST'])
def newItem():
    # if 'username' not in login_session:
    #     return redirect('/login')

    cates = session.query(Category).order_by(desc(Category.created)).all()

    if 'username' not in login_session:
        return redirect('/login')

    if request.method == "GET":
        return render_template('new_item.html', cates= cates) 
    elif request.method == "POST":
        name = request.form['item-name']
        cate_index = int(request.form.get('item-category'))-1
        description = request.form['item-description']

        if validate_item_name(name) and validate_item_descrip(description) and validate_item_category(cate_index):
            # print name, cate_index, description
    
            # dummy_user = session.query(User).filter_by(name="ZGH").one()
            selected_cate = cates[cate_index]
            # print dummy_user.name, selected_cate.name

            newItem = Item(
                name=name, description=description, 
                user_id=login_session['user_id'],
                category=selected_cate, category_id = selected_cate.id
                )

            session.add(newItem)

            print "new item %s" % newItem.category

            flash('New Item %s of category %s Successfully Created' % (
                newItem.name, newItem.category.name))

            session.commit()

            return redirect(url_for('showCategories'))
        else:
          error ="Some inputs are not valid"

          return render_template('new_item.html', cates=cates, name=name, description=description , error = error )


@app.route('/category/<string:cate>/item/<string:item>/edit/', methods=['GET', 'POST'])
def editItem(cate, item):
    # if 'username' not in login_session:
    #     return redirect('/login')
    cates = session.query(Category).order_by(desc(Category.created)).all()
    cate = session.query(Category).filter_by(name=cate).one()
    item = session.query(Item).filter_by(category_id=cate.id, name=item).first()

    ### check authentication and authority
    if 'username' not in login_session:
        return redirect('/login')

    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
    
    if (not cate) or (not item):
        return render_template("404.html", requested_url=request.url)
    if request.method == "GET":
        return render_template('edit_item.html', item = item, cates=cates)
    if request.method == "POST":
        name = request.form['item-name']
        cate_index = int(request.form.get('item-category'))-1
        description = request.form['item-description']
        print name, cate, description

        if validate_item_name(name):
            item.name = name
        if validate_item_descrip(description):
            item.description = description
        if validate_item_category(cate_index):
            selected_cate = cates[cate_index]
            item.category_id = selected_cate.id
        
        session.add(item)
        
        flash('Item %s of Category %s Successfully updated' % (item.name, item.category.name))
        session.commit()

        return redirect(url_for('showCategories'))


@app.route('/category/<string:cate>/item/<string:item>/delete/', methods=['GET', 'POST'])
def deleteItem(cate, item):

    cates = session.query(Category).order_by(desc(Category.created)).all()
    cate = session.query(Category).filter_by(name=cate).one()
    item = session.query(Item).filter_by(category_id=cate.id, name=item).first()

    ### check authentication and authority
    if 'username' not in login_session:
        return redirect('/login')

    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
    
    if (not cate) or (not item):
        return render_template("404.html", requested_url=request.url)
    if request.method == "GET":
        return render_template('delete_item.html', item = item)

    if request.method == "POST":
        if item:
            session.delete(item)
            session.commit()
            flash('Item %s of Category %s Successfully deleted' % (item.name, item.category.name))
            return redirect(url_for('showCategories'))



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    # login_manager = flask_login.LoginManager()
    # login_manager.init_app(app)

    app.debug = True
    app.run(host='0.0.0.0', port=8070)
