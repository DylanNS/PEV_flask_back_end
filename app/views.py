# -*- encoding: utf-8 -*-
"""
Dark Dashboard - coded in Flask
Author: AppSeed.us - App Generator 
"""

# all the imports necessary
from flask import json, url_for, redirect, render_template, flash, g, session, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException, NotFound, abort
from sqlalchemy import desc
import os
from flask import Flask, make_response, current_app
from app  import app

from flask       import url_for, redirect, render_template, flash, g, session, jsonify, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from app         import app, lm, db, bc
from . models    import User, Sensor
from . common    import COMMON, STATUS
from . assets    import *
from . forms     import LoginForm, RegisterForm, SensorRegisterForm
from datetime import datetime
import os, shutil, re, cgi
from functools import update_wrapper

# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@lm.unauthorized_handler
def unauthorized():
    flash("You need to login first")
    return redirect('login')

@app.route("/sensor/delete/<sensorID>")
@login_required
def delete_sensor(sensorID):
    Sensor.query.filter_by(sensor_id=sensorID).delete()
    db.session.commit()
    return redirect(url_for('Dashboard'))


# authenticate user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/sensor/volume/<sensorID>')
def volume(sensorID):
    sensor_data = Sensor.query.filter_by(sensor_id=sensorID).order_by(desc(Sensor.time)).first()
    chart_config =   {
      "chart": {
          "caption": "Volume Sensor "+str(sensor_data.sensor_id),
          "lowerLimit": "0",
          "upperLimit": "100",
          "showValue": "1",
          "numberSuffix": "%",
          "theme": "fusion",
          "showToolTip": "0"
      },
      "colorRange": {
          "color": [{
              "minValue": "0",
              "maxValue": "50",
              "code": "#62B58F"
          }, {
              "minValue": "50",
              "maxValue": "75",
              "code": "#FFC533"
          }, {
              "minValue": "75",
              "maxValue": "100",
              "code": "#F2726F"
          }]
      },
      "dials": {
          "dial": [{
              "value": sensor_data.volume
          }]
      }
    }
    response = jsonify( chart_config)
    return response
# get sensor data
@app.route('/sensor/all_volume')
def all_volume():
    # Get all sensor volume data
    sensor_data = Sensor.query.all()
    sensor_volume = {}
    for s in sensor_data:
        res =  sensor_volume.get(s.sensor_id,False)
        if  (res == False) or (res!=False and (res.time < s.time)):
            sensor_volume[s.sensor_id] = s
    list_sensor =[]
    for s in sensor_volume.values():
        list_sensor.append({"sensor_id": s.sensor_id, "volume": s.volume, "time": s.time})
    return jsonify(list_sensor)
# get all sensor ids
@app.route('/sensor/all')
def all():
    # Get all sensor ids
    sensor_data = Sensor.query.all()
    sensor_volume = {}
    for s in sensor_data:
        res =  sensor_volume.get(s.sensor_id,False)
        if  (res == False) or (res!=False and res.time < s.time):
            sensor_volume[s.sensor_id] = s
    list_sensor =[]
    for s in sensor_volume.values():
        list_sensor.append(s.sensor_id)
    return jsonify(list_sensor)

# SingUp user
@app.route('/signup', methods=['GET', 'POST'])
def Signup():
    
    # define login form here
    form = RegisterForm(request.form)

    msg = None

    # custommize your pate title / description here
    page_title       = 'SignUP - SMPEV'
    page_description = 'SMPEV Dashboard, registration page.'

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        name     = request.form.get('name'    , '', type=str) 
        email    = request.form.get('email'   , '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user:
            msg = 'Error: Username exists!'
        elif(user_by_email):
            msg = 'Error: e-mail exists!'
        else:                    
            pw_hash = bc.generate_password_hash(password)

            user = User(username, pw_hash, name, email)

            user.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>' 
            return redirect(url_for('login'))


    # try to match the pages defined in -> themes/light-bootstrap/pages/
    return render_template( 'layouts/default.html',
                            title=page_title,
                            content=render_template( 'pages/index.html', 
                                                     form=form,
                                                     msg=msg) )

@app.route('/sensor',methods=['GET','POST'])
@login_required
def sensor():
    # define login form here
    form = SensorRegisterForm(request.form)

    msg = None

    # custommize your pate title / description here
    page_title       = 'Register - Sensor Data'
    page_description = 'Sensor Data Registration Page.'

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        sensor_id = request.form.get('sensor_id', '', type=int)
        volume = request.form.get('volume', '', type=float) 
        #time     = datetime.now()          
        #parsing strings into datetimes
        #dt_time = datetime(time.strftime("%d/%m/%Y %H:%M:%S"))
        dt_time = datetime.now()
        sensor = Sensor(sensor_id, volume, dt_time)
        sensor.save()
        msg = 'Sensor Data created, please <a href="' + url_for('login') + '">login</a>' 
        return redirect(url_for('Dashboard'))


    # try to match the pages defined in -> themes/light-bootstrap/pages/
    return render_template( 'layouts/default.html',
                            title=page_title,
                            content=render_template( 'pages/index.html', 
                                                     form=form,
                                                     msg=msg) )

# authenticate user
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    # define login form here
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # custommize your page title / description here
    page_title = 'Login - Flask Dark Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Dark Dashboard, login page.'

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        if user:
            
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect('/index.html')
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unkkown user"
    print(form.errors)
    # try to match the pages defined in -> themes/light-bootstrap/pages/
    return render_template( 'layouts/default.html',
                            title=page_title,
                            content=render_template( 'pages/index.html', 
                                                     form=form,
                                                     msg=msg) )
# Used only for static export
@app.route('/dashboard')
@login_required
def Dashboard():

    # custommize your page title / description here
    page_title = 'SMPEV'
    page_description = 'SMPEV Dashboard'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/index.html') )

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    content = None

    try:

        # try to match the pages defined in -> themes/light-bootstrap/pages/
        return render_template('layouts/default.html',
                                content=render_template( 'pages/'+path) )
    except:
        abort(404)

#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(app.root_path, 'static'),
#                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

#@app.route('/sitemap.xml')
#def sitemap():
#    return send_from_directory(os.path.join(app.root_path, 'static'),
#                               'sitemap.xml')

# ------------------------------------------------------

# error handling
# most common error codes have been added for now
# TO DO:
# they could use some styling so they don't look so ugly

def http_err(err_code):
	
    err_msg = 'Oups !! Some internal error ocurred. Thanks to contact support.'
	
    if 400 == err_code:
        err_msg = "It seems like you are not allowed to access this link."

    elif 404 == err_code:    
        err_msg  = "The URL you were looking for does not seem to exist."
        err_msg += "<br /> Define the new page in /pages"
    
    elif 500 == err_code:    
        err_msg = "Internal error. Contact the manager about this."

    else:
        err_msg = "Forbidden access."

    return err_msg
    
@app.errorhandler(401)
def e401(e):
    return http_err( 401) # "It seems like you are not allowed to access this link."

@app.errorhandler(404)
def e404(e):
    return http_err( 404) # "The URL you were looking for does not seem to exist.<br><br>
	                      # If you have typed the link manually, make sure you've spelled the link right."

@app.errorhandler(500)
def e500(e):
    return http_err( 500) # "Internal error. Contact the manager about this."

@app.errorhandler(403)
def e403(e):
    return http_err( 403 ) # "Forbidden access."

@app.errorhandler(410)
def e410(e):
    # "The content you were looking for has been deleted."
    return http_err( 410)