from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('google_client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

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