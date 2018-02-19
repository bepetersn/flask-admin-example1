#!/usr/bin/env python

import os
import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import Column, Integer, ForeignKey, Unicode 


# Commands

cli = click.group(__name__)(lambda: None)

@cli.command()
def initdb():
    with app.app_context(): 
        db.drop_all()
        db.create_all()

@cli.command()
def run():
    app.run()


# Models

db = SQLAlchemy()


class Order(db.Model):
    id = Column(Integer, primary_key=True)
    jobs = db.relationship('Job', backref='order', lazy='dynamic')
    location_id = Column(Integer, ForeignKey('location.id'))
    location = db.relationship('Location', backref=db.backref('orders', lazy='dynamic'))


class Location(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)


class Job(db.Model):
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))


# Views

class AdminModelView(ModelView):
    def __init__(self, **kwargs):
        ModelView.__init__(self, self.model, db.session, **kwargs)


class AdminOrderView(AdminModelView):
    model = Order
    column_display_pk = True
    column_filters = ('id', 'location_id', )
    form_ajax_refs = {
        'jobs': {'fields': ['id']},
        'location': {'fields': ['id', 'name']},
    }


class AdminJobView(AdminModelView):
    model = Job
    column_display_pk = True
    column_filters = ('order_id', 'order.location.name', ) 
    column_list = ('id', 'order_id', 'order.location.name', )
    form_ajax_refs = {
        'order': {'fields': ['id']},
    }


class AdminLocationView(AdminModelView):
    model = Location
    column_list = ('id', 'name',)
    column_filters = ('id', 'name',)


# Setup admin

admin = Admin()
admin.add_view(AdminLocationView())
admin.add_view(AdminOrderView())
admin.add_view(AdminJobView())


# Setup app

app = Flask(__name__)
app.config['SECRET_KEY'] = "FAKE"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
admin.init_app(app)


# Run

if __name__ == '__main__':
    cli()
