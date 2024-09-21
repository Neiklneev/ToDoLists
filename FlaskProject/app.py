from flask import Flask, render_template, session, redirect, url_for, request, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.secret_key = 'qe3r1578dcb34ftr'
app.permanent_session_lifetime = timedelta(minutes=60)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
login_manager = LoginManager(app)

db = SQLAlchemy(app)

bcrypt = Bcrypt()





# Database Models

class User(db.Model, UserMixin):
	__tablename__ = 'authentication'
	uid = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	name = db.Column(db.String(1000))


	def __repr__(self):
		return f'A User with username {self.name}'
	
	def get_id(self):
           return (self.uid)


class Item(db.Model):
	__tablename__ = 'todolist'
	iid = db.Column(db.Integer, primary_key=True)
	id_of_creator = db.Column(db.Integer)
	title = db.Column(db.String(100), unique=True)
	description = db.Column(db.String(1000))
	due_str = db.Column(db.String(100))


	def __repr__(self):
		return f'An item in the todolist of USER {self.id_of_creator} with title {self.title}'
	
	def get_creator(self):
           return (self.iid)



@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))



# CRUD

@app.route('/')
@app.route('/home/')
def home():
	if current_user.is_authenticated:
		item_list = Item.query.filter(Item.id_of_creator==current_user.uid)
		return render_template('index.html', context={'items': item_list, 'greeting': current_user.name})
	else:
		flash('You are not logged in. To access most of the functionality of this site you will need to log in.')
		return redirect(url_for('login'))



@app.route('/create/', methods=['POST', 'GET'])
def create_item():
	if request.method=='POST':
		if current_user.is_authenticated:
			title = request.form['title']
			due_str = request.form['due_str']
			description = request.form['description']
			newitem = Item(id_of_creator=current_user.uid, title=title, due_str=due_str, description=description)
			db.session.add(newitem)
			db.session.commit()
			flash('Your item has been added successfully!')
			return redirect(url_for('home'))


		else:
			flash('You are not logged in. To access most of the functionality of this site you will need to log in.')
			return redirect(url_for('login'))

	else:
		if current_user.is_authenticated:
			return render_template('create.html')
		else:
			flash('You are not logged in. To access most of the functionality of this site you will need to log in.')
			return redirect(url_for('login'))





@app.route('/delete/<item_id>', methods=['POST', 'GET'])
def delete_item(item_id):
	if request.method == 'POST':
		tbdeleted = Item.query.get(item_id)
		db.session.delete(tbdeleted)
		db.session.commit()
		flash('Your item has been deleted successfully.')
		return redirect(url_for('home'))
	else:

		if current_user.is_authenticated:

			ownerid = Item.query.get(item_id).id_of_creator

			if current_user.uid == ownerid:
				return render_template('delete.html')

			else:
				return redirect(url_for('home'))


		else:
			flash('You are not logged in. To access most of the functionality of this site you will need to log in.')
			return redirect(url_for('login'))



@app.route('/about')
def about():
	return render_template('about.html')







# Authentication Views

@app.route('/profile/')
def profile():
	if current_user.is_authenticated:
		return render_template('profile.html', email=current_user.email, name=current_user.name)
	else:
		flash('To view your profile please log in first.')
		return redirect('login.html')


@app.route('/login/', methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		username = request.form['username']
		passw = request.form['password']
		usr = User.query.filter(User.name == username).first()



		if usr:
			if bcrypt.check_password_hash(usr.password, passw):
				login_user(usr)
				flash('Logged in Successfully!')
				return redirect(url_for('home'))
			else:
				flash('Your Username/Password was incorrect.')
				return render_template('login.html')
		else:
			flash('That account does not exist. Please sign up here.')
			return redirect(url_for('signup'))
	else:
		if current_user.is_authenticated:
			flash('You are already logged in.')
			return redirect(url_for('home'))
		return render_template('login.html')




@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method=='POST':

		# Fetching Data
		username = request.form['username']
		passw = request.form['password']
		email = request.form['email']
		

		# Error Handling
		username_taken = User.query.filter(User.name==username).first()
		email_taken = User.query.filter(User.email==email).first()
		

		if passw == '':
			flash('Your password cannot be empty.')
			return render_template('signup.html')
		if username_taken:
			flash('That username is already taken.')
			return render_template('signup.html')
		if email_taken:
			flash('That username is already taken.')
			return render_template('signup.html')



		# Success
		else:
			hashed_password = bcrypt.generate_password_hash(passw)

			newuser = User(name=username, password=hashed_password, email=email)
			db.session.add(newuser)
			db.session.commit()

			login_user(newuser)
			flash('You are Signed Up!!!')
			return redirect(url_for('home'))


	else:
		if current_user.is_authenticated:
			flash('You are already logged in!')
			return redirect(url_for('home'))
		return render_template('signup.html')



@app.route('/logout')
def logout():
	if current_user.is_authenticated:
		logout_user()
		flash('Logged Out Successfully!')
		return redirect(url_for('login'))
	else:
		flash('Already Logged Out!')
		return redirect(url_for('login'))





if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run()
	
