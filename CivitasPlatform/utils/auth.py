import hashlib
import streamlit as st
from typing import Optional, Dict, Any
from database.db_manager import DatabaseManager

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user and set session state"""
        user_data = self.db.authenticate_user(username, password)
        
        if user_data:
            st.session_state.authenticated = True
            st.session_state.user_id = user_data['id']
            st.session_state.user_data = user_data
            return True
        
        return False
    
    def register(self, username: str, password: str, full_name: str, 
                email: str, phone: str, role: str, cnic: Optional[str] = None) -> bool:
        """Register new user"""
        return self.db.create_user(username, password, full_name, email, phone, role, cnic)
    
    def logout(self):
        """Clear session state and logout user"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_data = {}
        st.session_state.selected_committee = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def get_current_user_id(self) -> Optional[str]:
        """Get current user ID"""
        return st.session_state.get('user_id')
    
    def get_current_user_data(self) -> Dict[str, Any]:
        """Get current user data"""
        return st.session_state.get('user_data', {})
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        user_data = self.get_current_user_data()
        return user_data.get('role') == 'admin'
    
    def can_create_private_committee(self) -> bool:
        """Check if user can create private committees (admin only)"""
        return self.is_admin()
    
    def refresh_user_data(self):
        """Refresh user data from database"""
        if self.is_authenticated():
            user_id = self.get_current_user_id()
            updated_data = self.db.get_user_by_id(user_id)
            if updated_data:
                st.session_state.user_data = updated_data
