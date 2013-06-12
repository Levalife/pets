from flask import Flask, render_template, redirect, flash, request, g, session, url_for
from flask.ext.login import LoginManager, current_user, login_user, logout_user, login_required
from flask import jsonify
from flask.ext.babel import gettext
#from app import *
from app import app, db, login_manager, babel
from models import User, Post, ROLE_USER, ROLE_ADMIN, FIRST_TIME
from forms import UserForm, PostForm, SearchForm,EditForm
from emails import follower_notification
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES, WHOOSH_ENABLED
from datetime import datetime
import arrow


@babel.localeselector
def get_locale():
	return  "ru" #request.accept_languages.best_match(LANGUAGES.keys())

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user
	g.search_form = SearchForm(request.form)
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
	g.search_enabled = WHOOSH_ENABLED

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', u'POST'])
@app.route('/home', methods=['GET', 'POST'])
@app.route('/home/<int:page>', methods=['GET', 'POST'])
def home(page = 1):
	time = {}
	posts = Post.query.order_by(Post.id.desc()).paginate(page, POSTS_PER_PAGE, False)
	for post in posts.items:
		time[post.id] = arrow.get(post.timestamp).to('local').format('DD.MM.YYYY HH:mm:ss')
	return render_template('home.html', posts=posts, time=time)

@app.route('/registration', methods = ['POST','GET'])
def registration():
	
	form = UserForm(request.form)
	if request.method == 'POST' and form.validate:
		username = form.username.data

		email = form.email.data
		if User.query.filter_by(email = email).first():
			flash(gettext('Email already registered.'))
			return render_template('registration.html', form=form)
		elif User.query.filter_by(username = username).first():
			new_username = User.make_unique_username(username)
			flash(gettext('Login is already exist. You can try this one: ') + new_username) 
			return render_template('registration.html', form=form)
		
		reg = User(username, form.email.data, form.password.data, ROLE_USER, form.about_me.data, FIRST_TIME)
		
		db.session.add(reg)
		db.session.commit()
		#make the user follow him/herself
		#db.session.add(reg.follow(reg))
		#db.session.commit()
		flash(gettext('You were successfully registrated.'))
		return redirect(url_for('home'))
	return render_template('registration.html', form=form)



@app.route('/login', methods = ['POST', 'GET'])
def login():
	form = UserForm(request.form)
	user = User.query.filter(User.email==form.email.data).scalar()
	if user:
		remember = request.form.get('remember', 'no') == 'yes'
		if user.password == form.password.data:
			login_user(user, remember=remember)
			flash(gettext('You were logged in.'))
			return redirect(request.args.get("next") or url_for('home'))
		else:
			flash(gettext('Invalid email or password.'))
	else: 
		flash(gettext('Invalid email or password.'))
	return redirect(url_for('home'))

@app.route('/add_post', methods = ['POST', 'GET'])
@login_required
def add_post():
	form = PostForm(request.form)
	if request.method == 'POST' and form.validate:
		post = Post(form.title.data, g.user, form.text.data, form.category.data)
		db.session.add(post)
		db.session.commit()
		flash(gettext('Your post successfully added.'))
		return redirect(url_for('home'))
	return render_template('add_post.html', form=form)

@app.route('/post_page/<id>')
def post_page(id):
	time={}
	post = Post.query.filter(Post.id==id).scalar()
	time[post.id] = arrow.get(post.timestamp).to('local').format('DD.MM.YYYY HH:mm:ss')
	return render_template('post_page.html', post=post, time=time)


@app.route('/logout')
def logout():
	logout_user()
	flash(gettext('Logged out.'))
	return redirect(url_for('home'))

@app.route('/search', methods=['POST', 'GET'])
def search():
	if request.method == 'POST' and g.search_form.validate_on_submit():
		query = g.search_form.search.data
		return redirect(url_for('search_results', query=g.search_form.search.data))
	return redirect(url_for('home'))

@app.route('/search_results/<query>')
def search_results(query):
	time={}
	results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
	if list(results):
		for post in results:
			time[post.id] = arrow.get(post.timestamp).to('local').format('DD.MM.YYYY HH:mm:ss')
		return render_template('search_results.html', query=query, results=results, time=time)
	flash(gettext("Search didn't give results."))
	return redirect(url_for('home'))

@app.route('/user/<username>')
@app.route('/user/<username>/<int:page>')
@login_required
def user(username, page = 1):
	time = {}
	user = User.query.filter_by(username = username).scalar()
	
	if user == None:
		flash(gettext('User %(username)s not found.', username = username))
		return redirect(url_for('home'))
	
	user_time = gettext(arrow.get(user.last_seen).to('local').humanize())

	#posts = user.posts
	posts = Post.query.filter(Post.author==user).paginate(page, POSTS_PER_PAGE, False)
	for post in posts.items:
		time[post.id] = arrow.get(post.timestamp).to('local').format('DD.MM.YYYY HH:mm:ss')
	return render_template('user.html', user=user, posts=posts, time=time, user_time=user_time)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	form = EditForm(request.form)
	if form.validate_on_submit():
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash(gettext('Your changes have been saved.'))
		return redirect(url_for('user', username=g.user.username))
	else:
		form.about_me.data = g.user.about_me
	return render_template('edit.html', form=form)

@app.route('/edit_post/<id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	form = PostForm(request.form)
	post = Post.query.filter_by(id=id).scalar()
	if form.validate_on_submit():
		post.title = form.title.data
		post.text = form.text.data
		post.category = form.category.data
		post.timestamp = datetime.utcnow()
		db.session.add(post)
		db.session.commit()
		flash(gettext('Your changes have been saved.'))
		return redirect(url_for('post_page', id=post.id))
	else:
		form.title.data = post.title
		form.text.data = post.text
		form.category.data = post.category
	return render_template('edit_post.html', form=form, id=post.id)


@app.errorhandler(404)
def internal_error(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html'), 500


@app.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user == None:
		flash(gettext('User %(username)s not found.', usernmae = username))
		#flash("User " + username + ' not found.')
		return redirect(url_for('home'))
	if user == g.user:
		flash(gettext("You can\'t follow yourself"))
		return redirect(url_for('user', user = user))
	# link bitween g.user and user 
	u = g.user.follow(user)
	if u is None:
		flash(gettext('Cannot follow  %(username)s .', username=username))
		return redirect(url_for('user', username=username))
	db.session.add(u)
	db.session.commit()
	flash(gettext('You are now following %(username)s !', username=username))
	follower_notification(user, g.user)
	return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username = username).first()
	if user == None:
		flash(gettext('User %(username)s not found.', usernmae = username))
		return redirect(url_for('home'))
	if user == g.user:
		flash(gettext('You can\'t unfollow yourself'))
		return redirect(url_for('user', username = username))

	u = g.user.unfollow(user)
	if u is None:
		flash(gettext('Cannot unfollow  %(username)s .', username=username))
		return redirect(url_for('user', username-username))
	db.session.add(u)
	db.session.commit()
	flash(gettext('You have stopped following %(username)s .', username=username))
	return redirect(url_for('user', username = username))

@app.route('/my_line')
@login_required
def my_line(page = 1):
	time = {}
	posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
	for post in posts.items:
			time[post.id] = arrow.get(post.timestamp).to('local').format('DD.MM.YYYY HH:mm:ss')
	return render_template("my_line.html",posts=posts, time=time)

@app.route('/delete/<int:id>')
@login_required
def delete_post(id):
	post = Post.query.get(id)
	if post == None:
		flash(gettext('Post don\'t found.'))
		return redirect(url_for('home'))
	if post.author.id != g.user.id:
		flash(gettext('You cannot delete this post.'))
		return redirect(url_for('home'))
	db.session.delete(post)
	db.session.commit()
	flash(gettext('Your post has been deleted.'))
	return redirect(url_for('home'))
