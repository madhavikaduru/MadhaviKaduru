from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

# Define the single blueprint instance
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        user = User.query.filter_by(user_id=user_id).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        
        flash('Invalid username or password.', 'danger')

    return render_template('login.html')




@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user_name = request.form.get('user_name')
        print("--------------user_name----------")
        role = request.form.get('role')
        password_hash = request.form.get('password')
        
        # Prevent passing None to generate_password_hash
        if not password_hash:
            flash('password is required!', 'danger')
            return render_template('register.html')

        # Check for duplicate user
        if User.query.filter_by(user_id=user_id).first():
            flash('UserID already exists.', 'danger')
            return render_template('register.html')

        # Create new user object
        new_user = User(
            user_id=user_id,
            user_name=user_name,
            role=role,
            password_hash=generate_password_hash(password_hash),
            active=True,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('User registered successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

