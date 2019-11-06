# -*- encoding: utf-8 -*-
"""
Flask Boilerplate
Author: AppSeed.us - App Generator 
"""

from app         import db
from flask_login import UserMixin

from . common    import COMMON, STATUS, DATATYPE
from datetime import datetime
class User(UserMixin, db.Model):

    id          = db.Column(db.Integer,     primary_key=True)
    user        = db.Column(db.String(64),  unique = True)
    email       = db.Column(db.String(120), unique = True)
    name        = db.Column(db.String(500))
    role        = db.Column(db.Integer)
    password    = db.Column(db.String(500))
    password_q  = db.Column(db.Integer)

    def __init__(self, user, password, name, email):
        self.user       = user
        self.password   = password
        self.password_q = DATATYPE.CRYPTED
        self.name       = name
        self.email      = email

        self.group_id = None
        self.role     = None

    def __repr__(self):
        return '<User %r>' % (self.id)

    def save(self):

        # inject self into db session    
        db.session.add ( self )

        # commit change and save the object
        db.session.commit( )

        return self 

class Sensor(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    sensor_id = db.Column(db.Integer)
    volume = db.Column(db.Float)
    time = db.Column(db.DateTime)

    def __init__(self, sensor_id,volume,time):
        self.sensor_id = sensor_id

        self.volume = volume
        self.time = time
    def __repr__(self):
        return '<Sensor %r>' % (self.id)

    def save(self):

        db.session.add(self)
        db.session.commit()

