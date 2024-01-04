# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, User, ChatRoom, Message, Chat  # Import your models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Initialize the db instance with the app
db.init_app(app)

# Create necessary tables
with app.app_context():
    db.create_all()

    # Populate users from the database and initialize the chat object
    users_from_db = User.query.all()
    chat = Chat()  # Make sure to initialize your Chat class properly
    chat.initialize_users(users_from_db)


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        chat.set_user_status(username, True)
        messages = chat.get_last_messages(username)  # Pass the username to identify the chat room
        online_users = chat.get_online_users()
        chat_rooms = ChatRoom.query.all()
        return render_template('index.html', username=username, messages=messages, online_users=online_users, chat_rooms=chat_rooms)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        username = session.pop('username')
        chat.set_user_status(username, False)
        flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
