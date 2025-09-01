"""
Multi-Agent Marketing System - User Management Routes
Flask blueprint for user authentication and management
"""

import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash
from functools import wraps
import logging

from models.user import db, User, UserSession, UserActivity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
user_bp = Blueprint('user', __name__)

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            current_user = User.verify_token(token)
            if not current_user:
                return jsonify({'message': 'Token is invalid or expired'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@user_bp.route('/register', methods=['POST'])
@cross_origin()
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data.get('role', 'user')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log activity
        activity = UserActivity(
            user_id=user.id,
            activity_type='user_registration',
            description='New user registration',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity)
        db.session.commit()
        
        # Generate token
        token = user.generate_token()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'token': token
        }), 201
        
    except Exception as e:
        logger.error(f"Error in user registration: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@user_bp.route('/login', methods=['POST'])
@cross_origin()
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = user.generate_token()
        
        # Create session
        session = UserSession(
            user_id=user.id,
            session_token=token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.session.add(session)
        db.session.commit()
        
        # Log activity
        activity = UserActivity(
            user_id=user.id,
            activity_type='user_login',
            description='User login successful',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        })
        
    except Exception as e:
        logger.error(f"Error in user login: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@user_bp.route('/logout', methods=['POST'])
@cross_origin()
@token_required
def logout(current_user):
    """User logout endpoint"""
    try:
        # Get token from header
        auth_header = request.headers['Authorization']
        token = auth_header.split(" ")[1]
        
        # Deactivate session
        session = UserSession.query.filter_by(
            session_token=token,
            user_id=current_user.id
        ).first()
        
        if session:
            session.is_active = False
            db.session.commit()
        
        # Log activity
        activity = UserActivity(
            user_id=current_user.id,
            activity_type='user_logout',
            description='User logout',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'message': 'Logout successful'})
        
    except Exception as e:
        logger.error(f"Error in user logout: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@user_bp.route('/profile', methods=['GET'])
@cross_origin()
@token_required
def get_profile(current_user):
    """Get user profile endpoint"""
    try:
        return jsonify({
            'status': 'success',
            'user': current_user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@user_bp.route('/profile', methods=['PUT'])
@cross_origin()
@token_required
def update_profile(current_user):
    """Update user profile endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email']
        for field in allowed_fields:
            if field in data:
                setattr(current_user, field, data[field])
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        activity = UserActivity(
            user_id=current_user.id,
            activity_type='profile_update',
            description='User profile updated',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Profile update failed'}), 500

@user_bp.route('/change-password', methods=['POST'])
@cross_origin()
@token_required
def change_password(current_user):
    """Change user password endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        # Verify current password
        if not current_user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        current_user.set_password(data['new_password'])
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        activity = UserActivity(
            user_id=current_user.id,
            activity_type='password_change',
            description='User password changed',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Password change failed'}), 500

@user_bp.route('/users', methods=['GET'])
@cross_origin()
@token_required
@admin_required
def get_users(current_user):
    """Get all users endpoint (admin only)"""
    try:
        users = User.query.all()
        users_data = [user.to_dict() for user in users]
        
        return jsonify({
            'status': 'success',
            'users': users_data,
            'count': len(users_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({'error': 'Failed to get users'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@cross_origin()
@token_required
@admin_required
def get_user(current_user, user_id):
    """Get specific user endpoint (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({'error': 'Failed to get user'}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@cross_origin()
@token_required
@admin_required
def update_user(current_user, user_id):
    """Update user endpoint (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email', 'role', 'is_active', 'agent_id', 'agent_type', 'permissions']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        activity = UserActivity(
            user_id=current_user.id,
            activity_type='user_update',
            description=f'Updated user {user.username}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            activity_metadata={'target_user_id': user_id}
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'User update failed'}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@cross_origin()
@token_required
@admin_required
def delete_user(current_user, user_id):
    """Delete user endpoint (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        # Log activity before deletion
        activity = UserActivity(
            user_id=current_user.id,
            activity_type='user_deletion',
            description=f'Deleted user {user.username}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            activity_metadata={'deleted_user_id': user_id}
        )
        db.session.add(activity)
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'User deletion failed'}), 500

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for user service"""
    return jsonify({
        'status': 'healthy',
        'service': 'user_management',
        'timestamp': datetime.utcnow().isoformat()
    })
