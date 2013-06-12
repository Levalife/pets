from flask import Flask
#from flask.ext.sqlalchemy import SQLAlchemy
from app import app, db
import flask.ext.whooshalchemy as whooshalchemy
from datetime import datetime
import arrow
import re

from config import WHOOSH_ENABLED




ROLE_USER = 0
ROLE_ADMIN = 1
FIRST_TIME = None

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


#User().posts - all users posts

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column (db.String(80), unique = True)
	email = db.Column (db.String(80), unique = True)
	password = db.Column (db.String(80))
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	about_me = db.Column(db.String(140), default = FIRST_TIME)
	last_seen = db.Column(db.DateTime, default = FIRST_TIME)
	followed = db.relationship('User', 
		secondary = followers,
		primaryjoin = (followers.c.follower_id == id),
		secondaryjoin = (followers.c.followed_id == id),
		backref = db.backref('followers', lazy = 'dynamic'),
		lazy = 'dynamic')

	def __init__(self, username, email, password, role, about_me, last_seen):
		self.username = username
		self.email = email
		self.password = password
		self.role = role
		self.about_me = about_me
		self.last_seen = last_seen

	def is_active(self):
		return True

	def is_authenticated(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id)
		except AttributeError:
			raise NotImplementedError("No `id` attribute - override get_id")

	@staticmethod
	def make_unique_username(username):
		if User.query.filter_by(username = username).first() == None:
			return username
		version = 2
		while True:
			new_username = username + str(version)
			if User.query.filter_by(username = new_username).first() == None:
				break
			version += 1
		return new_username 

	@staticmethod
	def make_valid_username(username):
		return re.sub('[^a-zA-Z0-9_\.]', '', username)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			return self

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
			return self

	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		return Post.query.join(followers, (followers.c.followed_id == Post.author_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())


	def __repr__(self):
		return '<User %r>' % (self.username)

#Post().author.username - username, equivalent to User().username

class Post(db.Model):
	__searchable__=['title', 'text']

	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(160), unique = True)
	author_id = db.Column (db.Integer, db.ForeignKey('user.id'))
	author = db.relationship ('User', backref = db.backref('posts', lazy ='dynamic'))
	text = db.Column(db.Text)
	category = db.Column (db.String(80))
	timestamp = db.Column(db.DateTime)

	def __init__(self, title, author, text, category, timestamp = None):
		self.title = title
		self.author = author
		self.text = text
		self.category = category
		if timestamp is None:
			timestamp = datetime.utcnow()
		self.timestamp = timestamp
		
	def __repr__(self):
		return '<Post %r>' % (self.title)	

whooshalchemy.whoosh_index(app, Post)


if WHOOSH_ENABLED:
    import flask.ext.whooshalchemy as whooshalchemy
    whooshalchemy.whoosh_index(app, Post)