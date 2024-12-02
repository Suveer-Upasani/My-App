from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/suveer/Desktop/Tooler/users.db'  # Correct full path to SQLite DB
app.config['SECRET_KEY'] = 'your_secret_key'  # Secret key for sessions
db = SQLAlchemy(app)

# User model with first name, last name, email, and password (no hashing for simplicity)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Home route
@app.route('/')
def home_page():
    return render_template('index.html')

# Sign Up route
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', category='success')
            return redirect(url_for('login'))
        except:
            flash('Email already exists!', category='error')
            return redirect(url_for('sign_up'))
    
    return render_template('sign_up.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            flash('Login successful!', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Login failed. Check your credentials and try again.', category='error')
    
    return render_template('login.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates the database and tables if they do not exist
    app.run(debug=True)
