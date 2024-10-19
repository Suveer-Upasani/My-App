from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/suveer/Desktop/planetary-api/planets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = db.Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(100), nullable=False)
    planet_type = db.Column(db.String(100), nullable=False)
    home_star = db.Column(db.String(100), nullable=False)
    mass = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/planet/<int:planet_id>')
def planet_details(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return render_template('planet_details.html', planet=planet)

@app.route("/add")
def add():
        return render_template('add_planets.html')

@app.route('/add_planet', methods=['POST', 'GET'])
@jwt_required()
def add_planet():
    if request.method == 'POST':
        planet_name = request.json.get('planet_name')
        planet_type = request.json.get('planet_type')
        home_star = request.json.get('home_star')
        mass = float(request.json.get('mass'))
        radius = float(request.json.get('radius'))
        distance = float(request.json.get('distance'))
        
        new_planet = Planet(planet_name=planet_name,
                            planet_type=planet_type,
                            home_star=home_star,
                            mass=mass,
                            radius=radius,
                            distance=distance)

        db.session.add(new_planet)
        db.session.commit()

        app.logger.info(f'Planet added: {new_planet.planet_name} (ID: {new_planet.planet_id})')
        
        return jsonify({'planet_id': new_planet.planet_id}), 201  

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return jsonify(message='Invalid email format.'), 400

        test = User.query.filter_by(email=email).first()
        
        if test:
            return jsonify(message='That email already exists.'), 409
        else:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            password = request.form['password']
            hashed_password = generate_password_hash(password)
            user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
            
            db.session.add(user)
            db.session.commit()
            
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity={'email': user.email})
            return jsonify(access_token=access_token, redirect_url=url_for('add'))
        else:
            return jsonify(message='Invalid credentials'), 401

    return render_template('login.html')

@app.route('/planets', methods=['GET'])
def list_planets():
    planets = Planet.query.all()
    return render_template('planets.html', planets=planets)

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
