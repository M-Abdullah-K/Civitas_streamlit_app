import streamlit as st
import hashlib
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    
    if 'users' not in st.session_state:
        # Initialize with some demo users
        st.session_state.users = [
            {
                'username': 'admin',
                'password': hash_password('admin123'),
                'full_name': 'Ahmed Ali Khan',
                'email': 'ahmed@example.com',
                'phone': '+92-300-1234567',
                'role': 'admin',
                'trust_score': 95,
                'created_date': '2024-01-15'
            },
            {
                'username': 'sara',
                'password': hash_password('sara123'),
                'full_name': 'Sara Fatima',
                'email': 'sara@example.com',
                'phone': '+92-321-9876543',
                'role': 'member',
                'trust_score': 88,
                'created_date': '2024-02-20'
            },
            {
                'username': 'hassan',
                'password': hash_password('hassan123'),
                'full_name': 'Hassan Ahmed',
                'email': 'hassan@example.com',
                'phone': '+92-333-5555555',
                'role': 'member',
                'trust_score': 92,
                'created_date': '2024-03-10'
            }
        ]

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return hash_password(password) == hashed_password

def login_user(username, password):
    """Authenticate user login"""
    users = st.session_state.get('users', [])
    
    for user in users:
        if user['username'] == username and verify_password(password, user['password']):
            st.session_state.authenticated = True
            st.session_state.current_user = username
            st.session_state.user_data = user
            
            # Update last login
            user['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return True
    
    return False

def register_user(username, password, full_name, email, phone, role='member'):
    """Register a new user"""
    users = st.session_state.get('users', [])
    
    # Check if username already exists
    if any(user['username'] == username for user in users):
        return False
    
    # Create new user
    new_user = {
        'username': username,
        'password': hash_password(password),
        'full_name': full_name,
        'email': email,
        'phone': phone,
        'role': role,  # Use provided role
        'trust_score': 75,  # Starting trust score
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'last_login': None
    }
    
    users.append(new_user)
    st.session_state.users = users
    
    return True

def logout_user():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_data = {}

def get_current_user():
    """Get current authenticated user data"""
    if st.session_state.authenticated:
        return st.session_state.user_data
    return None

def update_user_profile(username, updates):
    """Update user profile information"""
    users = st.session_state.get('users', [])
    
    for i, user in enumerate(users):
        if user['username'] == username:
            # Update user data
            for key, value in updates.items():
                if key in user:
                    users[i][key] = value
            
            # Update session state if it's current user
            if st.session_state.current_user == username:
                st.session_state.user_data.update(updates)
            
            return True
    
    return False

def change_password(username, old_password, new_password):
    """Change user password"""
    users = st.session_state.get('users', [])
    
    for i, user in enumerate(users):
        if user['username'] == username:
            if verify_password(old_password, user['password']):
                users[i]['password'] = hash_password(new_password)
                return True
            else:
                return False
    
    return False

def update_trust_score(username, new_score):
    """Update user's trust score"""
    users = st.session_state.get('users', [])
    
    for i, user in enumerate(users):
        if user['username'] == username:
            users[i]['trust_score'] = max(0, min(100, new_score))  # Ensure score is between 0-100
            
            # Update session state if it's current user
            if st.session_state.current_user == username:
                st.session_state.user_data['trust_score'] = users[i]['trust_score']
            
            return True
    
    return False

def get_user_by_username(username):
    """Get user data by username"""
    users = st.session_state.get('users', [])
    
    for user in users:
        if user['username'] == username:
            return user
    
    return None

def is_admin(username=None):
    """Check if user is admin"""
    if username is None:
        username = st.session_state.current_user
    
    user = get_user_by_username(username)
    return user and user.get('role') == 'admin'

def get_all_users():
    """Get all registered users (admin only)"""
    if not is_admin():
        return []
    
    return st.session_state.get('users', [])

def delete_user(username):
    """Delete user account (admin only)"""
    if not is_admin():
        return False
    
    users = st.session_state.get('users', [])
    
    for i, user in enumerate(users):
        if user['username'] == username:
            del users[i]
            return True
    
    return False

def require_auth():
    """Decorator function to require authentication"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated', False):
                st.error("Please login to access this feature")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """Decorator function to require admin role"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated', False):
                st.error("Please login to access this feature")
                st.stop()
            
            if not is_admin():
                st.error("Admin access required")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# User validation functions
def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Basic Pakistani phone number validation"""
    import re
    # Pakistani phone patterns: +92-XXX-XXXXXXX or 03XX-XXXXXXX
    patterns = [
        r'^\+92-\d{3}-\d{7}$',
        r'^03\d{2}-\d{7}$',
        r'^03\d{9}$'
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
    
    return True, "Password is strong"

def get_user_statistics():
    """Get user statistics for dashboard"""
    users = st.session_state.get('users', [])
    
    total_users = len(users)
    admin_users = len([u for u in users if u.get('role') == 'admin'])
    member_users = total_users - admin_users
    
    # Calculate average trust score
    trust_scores = [u.get('trust_score', 0) for u in users]
    avg_trust_score = sum(trust_scores) / len(trust_scores) if trust_scores else 0
    
    return {
        'total_users': total_users,
        'admin_users': admin_users,
        'member_users': member_users,
        'avg_trust_score': round(avg_trust_score, 1)
    }
