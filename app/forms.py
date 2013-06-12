#from flask import Flask
#from app import *

from flask.ext.wtf import Form, TextField, IntegerField, TextAreaField, validators, ValidationError
from flask.ext.wtf import Required, Length
from wtforms.validators import *

class UserForm(Form):
	username = TextField('Username',validators = [Required()])
	email = TextField('Email adress')
	password = TextField('Password',validators = [Length(min = 6, max = 40)])
	about_me = TextAreaField('About me', validators = [Length(min = 0,max = 140)])

	#def validate(self):
	#	if not Form.validate(self):
    #		return False
	#	user = User.query.filter_by(username=self.username.data).first()
	#	if user != None:
	#		self.username.errors.append('This nickname is already in use. Please choose another one.')
	#		return False
	#	return True

class PostForm(Form):
	title = TextField('Title',validators = [Required()])
	text = TextAreaField('Text')
	category = TextField('Category')

class SearchForm(Form):
	search = TextField('Search', validators = [Required()])

class EditForm(Form):
	about_me=TextAreaField('About me', validators = [Length(min=0, max=140)])