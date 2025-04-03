from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import json
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

genai.configure(api_key='AIzaSyBxzpPJEw7iWhCZ1RtVOXq-MSf6wbraYMg')
model = genai.GenerativeModel('gemini-1.5-flash')

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Career Assessment Model
class CareerAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skills = db.Column(db.String(500))
    interests = db.Column(db.String(500))
    education_level = db.Column(db.String(100))
    experience = db.Column(db.String(100))
    work_life_balance = db.Column(db.Integer)
    salary_importance = db.Column(db.Integer)
    location_preference = db.Column(db.String(100))
    recommendations = db.Column(db.String(2000))  # Increased size for AI responses
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            full_name=full_name
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['email'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access dashboard', 'warning')
        return redirect(url_for('login'))
    
    # Get user's career assessments if any
    assessments = CareerAssessment.query.filter_by(user_id=session['user_id']).order_by(CareerAssessment.created_at.desc()).all()
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         full_name=session['full_name'],
                         email=session['email'],
                         assessments=assessments)

@app.route('/career-assessment', methods=['GET', 'POST'])
def career_assessment():
    if 'user_id' not in session:
        flash('Please login to take assessment', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Process form data
            education_level = request.form['education']
            experience = request.form['experience']
            skills = request.form.getlist('skills')
            interests = request.form['interests']
            work_life_balance = request.form['workLifeBalance']
            salary_importance = request.form['salaryImportance']
            location_preference = request.form['location']
            
            # Generate AI recommendations
            recommendations = generate_ai_recommendations(
                education_level,
                experience,
                skills,
                interests,
                work_life_balance,
                salary_importance,
                location_preference
            )
            
            # Save assessment to database
            new_assessment = CareerAssessment(
                user_id=session['user_id'],
                skills=",".join(skills),
                interests=interests,
                education_level=education_level,
                experience=experience,
                work_life_balance=work_life_balance,
                salary_importance=salary_importance,
                location_preference=location_preference,
                recommendations=json.dumps(recommendations)  # Store as JSON string
            )
            
            db.session.add(new_assessment)
            db.session.commit()
            
            flash('Career assessment completed successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            flash(f'Error generating recommendations: {str(e)}', 'danger')
            return redirect(url_for('dashboard'))
    
    return render_template('dashboard.html')

def clean_json_response(text):
    """Clean and extract JSON from potentially malformed AI response"""
    try:
        # Try to find JSON in the text
        json_str = re.search(r'\{.*\}', text, re.DOTALL).group(0)
        # Remove markdown code blocks if present
        json_str = json_str.replace('```json', '').replace('```', '')
        return json.loads(json_str)
    except (AttributeError, json.JSONDecodeError):
        # If extraction fails, try parsing the whole text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError("Unable to parse AI response as JSON")

def generate_ai_recommendations(education, experience, skills, interests, work_life, salary, location):
    """Generate career recommendations using Gemini AI"""
    try:
        prompt = f"""Act as a professional career counselor. Based on the following profile:
- Education: {education}
- Experience: {experience}
- Skills: {', '.join(skills)}
- Interests: {interests}
- Work-Life Balance Importance: {work_life}/10
- Salary Importance: {salary}/10
- Location Preference: {location}

Provide 3 detailed career recommendations in JSON format with these fields for each:
- title: Career title
- match_score: Match percentage (70-100)
- description: Detailed explanation of why this career fits
- salary_range: Typical salary range
- growth_outlook: Job market outlook
- required_skills: Key skills needed
- learning_resources: List of resources to acquire needed skills
- next_steps: Actionable steps to pursue this career

Return only valid JSON with a 'recommendations' array containing the 3 career options. 
Example format:
{{
  "recommendations": [
    {{
      "title": "Software Engineer",
      "match_score": 85,
      "description": "This career matches well because...",
      "salary_range": "$80,000 - $120,000",
      "growth_outlook": "Excellent growth potential",
      "required_skills": ["Programming", "Problem Solving"],
      "learning_resources": ["Codecademy", "LeetCode"],
      "next_steps": "Build 2-3 portfolio projects"
    }}
  ]
}}
"""
        
        response = model.generate_content(prompt)
        print("Raw AI Response:", response.text)  # Debugging
        
        # Parse the response
        try:
            result = clean_json_response(response.text)
            return result.get('recommendations', [])
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Fallback to simple recommendations if JSON parsing fails
            return generate_simple_recommendations(skills)
            
    except Exception as e:
        print(f"AI Error: {str(e)}")
        # Fallback to simple recommendations if AI fails
        return generate_simple_recommendations(skills)

def generate_simple_recommendations(skills):
    """Fallback recommendation system when AI fails"""
    recommendations = []
    
    if any(skill.lower() in ['programming', 'coding', 'software', 'developer'] for skill in skills):
        recommendations.append({
            'title': 'Software Developer',
            'match_score': 90,
            'description': 'Develop software applications and systems based on requirements.',
            'salary_range': '$70,000 - $150,000',
            'growth_outlook': 'Excellent (22% growth projected)',
            'required_skills': ['Programming languages', 'Problem solving', 'Algorithms'],
            'learning_resources': ['Codecademy', 'freeCodeCamp', 'The Odin Project'],
            'next_steps': 'Build 2-3 portfolio projects and contribute to open source'
        })
    
    if any(skill.lower() in ['design', 'art', 'creative', 'ui', 'ux'] for skill in skills):
        recommendations.append({
            'title': 'UX/UI Designer',
            'match_score': 85,
            'description': 'Design user interfaces and experiences for digital products.',
            'salary_range': '$65,000 - $120,000',
            'growth_outlook': 'Strong (15% growth projected)',
            'required_skills': ['User research', 'Wireframing', 'Prototyping'],
            'learning_resources': ['Figma tutorials', 'Google UX Design Certificate'],
            'next_steps': 'Create a portfolio with 3 case studies'
        })
    
    if any(skill.lower() in ['writing', 'communication', 'content'] for skill in skills):
        recommendations.append({
            'title': 'Content Writer',
            'match_score': 80,
            'description': 'Create written content for websites, blogs, and marketing materials.',
            'salary_range': '$45,000 - $90,000',
            'growth_outlook': 'Steady (8% growth projected)',
            'required_skills': ['Writing', 'Research', 'SEO'],
            'learning_resources': ['Grammarly', 'HubSpot Content Marketing Course'],
            'next_steps': 'Start a blog and create writing samples'
        })
    
    # Ensure we always return 3 recommendations
    while len(recommendations) < 3:
        recommendations.append({
            'title': 'Career Counselor',
            'match_score': 75,
            'description': 'Help others navigate career choices and professional development.',
            'salary_range': '$45,000 - $80,000',
            'growth_outlook': 'Stable (6% growth projected)',
            'required_skills': ['Active listening', 'Assessment tools', 'Career coaching'],
            'learning_resources': ['NCDA certification programs', 'Career Development Handbook'],
            'next_steps': 'Volunteer for career counseling services'
        })
    
    return recommendations[:3]  # Return exactly 3 recommendations

# API endpoint for AJAX requests
@app.route('/api/assess-career', methods=['POST'])
def api_assess_career():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        recommendations = generate_ai_recommendations(
            data.get('education'),
            data.get('experience'),
            data.get('skills', []),
            data.get('interests'),
            data.get('workLifeBalance'),
            data.get('salaryImportance'),
            data.get('location')
        )
        
        return jsonify({'recommendations': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
