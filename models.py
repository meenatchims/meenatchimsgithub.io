from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    """User account model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Relationship with UserProfile
    profile = db.relationship('UserProfile', uselist=False, back_populates='user')
    
    def set_password(self, password):
        """Create hashed password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password"""
        return check_password_hash(self.password_hash, password)

class UserProfile(db.Model):
    """Detailed user profile model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Profile details
    education = db.Column(db.String(200))
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    career_interests = db.Column(db.Text)
    
    # Preference metrics
    work_life_balance_priority = db.Column(db.Integer, default=5)
    salary_importance = db.Column(db.Integer, default=5)
    
    # Relationship back to User
    user = db.relationship('User', back_populates='profile')