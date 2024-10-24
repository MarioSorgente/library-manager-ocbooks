from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import User, db
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')

def test_db_connection():
    """Test database connection and create tables if they don't exist."""
    try:
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('books.library'))

    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            # Input validation
            if not all([username, email, password]):
                flash('All fields are required', 'danger')
                return render_template('auth/register.html')
                
            if not password or len(password) < 8:
                flash('Password must be at least 8 characters long', 'danger')
                return render_template('auth/register.html')
            
            # Check for existing users
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return render_template('auth/register.html')
                
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return render_template('auth/register.html')
            
            # Create new user
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered successfully: {username}")
            
            flash('Registration successful! Please log in with your credentials.', 'success')
            return redirect(url_for('auth.login'))
                
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        flash('Registration failed. Please try again.', 'danger')
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('books.library'))
        
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not all([username, password]):
                logger.warning("Login attempt with missing credentials")
                flash('Username and password are required', 'danger')
                return render_template('auth/login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                # Clear any existing session before login
                session.clear()
                login_user(user)
                
                # Add session security measures
                session['user_id'] = user.id
                session['login_time'] = datetime.utcnow().isoformat()
                
                logger.info(f"User logged in successfully: {username}")
                next_page = request.args.get('next')
                
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('books.library'))
            
            logger.warning(f"Failed login attempt for username: {username}")
            flash('Invalid username or password', 'danger')
            
        except SQLAlchemyError as e:
            logger.error(f"Database error during login: {str(e)}")
            flash('Login failed. Please try again.', 'danger')
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'danger')
            
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    try:
        username = current_user.username
        
        # Clear session and log out user
        session.clear()
        logout_user()
        
        logger.info(f"User logged out successfully: {username}")
        flash('You have been logged out successfully', 'success')
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        flash('An error occurred during logout', 'danger')
    
    return redirect(url_for('auth.login'))
