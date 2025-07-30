import streamlit as st
import hashlib
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import os
import time
from utils.auth import AuthManager
# Import all page modules
from pages.data_viewer import show_data_viewer
from pages.admin_dashboard import show_admin_dashboard
from pages.member_dashboard import show_member_dashboard
from pages.committee_management import show_committee_management
from pages.ai_advice import show_ai_advice
from components.ui_components import apply_custom_css, show_header
from components.loading_screen import show_loading_screen
# Chatbot moved to AI advice page

# Page configuration
st.set_page_config(
    page_title="Civitas - Digital Committee Platform",
    page_icon="assets/civitas_new_logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide the default page navigation and multipage tabs
st.markdown("""
<style>
    .stAppHeader {visibility: hidden;}
    header[data-testid="stHeader"] {display: none !important;}
    .css-1dp5vir {display: none !important;}
    .css-k1ih3n {display: none !important;}
    section.main > div:has(~ footer ) > div > div > div > div > div.stTabs {display: none;}

    /* Hide multipage navigation tabs */
    [data-testid="stSidebarNav"] {display: none;}
    .css-1544g2n {display: none;}
    .css-1vencpc {display: none;}
    .st-emotion-cache-1vencpc {display: none;}
    .st-emotion-cache-1544g2n {display: none;}

    /* Hide the page selector dropdown */
    [data-testid="stSidebarNavItems"] {display: none;}
    .css-17lntkn {display: none;}
    .st-emotion-cache-17lntkn {display: none;}
</style>
""", unsafe_allow_html=True)

class CivitasApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.auth = AuthManager(self.db)
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {}
        if 'selected_committee' not in st.session_state:
            st.session_state.selected_committee = None
        if 'data_viewer_mode' not in st.session_state:
            st.session_state.data_viewer_mode = False
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'

    def run(self):
        """Main application entry point"""
        # Show loading screen on first load only
        if 'app_loaded' not in st.session_state:
            # Show loading screen in full page mode
            show_loading_screen()

            # Wait for 3 seconds
            time.sleep(3)

            # Mark app as loaded and rerun to show main app
            st.session_state.app_loaded = True
            st.rerun()

        # Apply custom styling
        apply_custom_css()

        # Show header
        show_header()

        # Authentication check
        if not st.session_state.authenticated:
            self.show_auth_page()
        else:
            self.show_main_app()



    def show_auth_page(self):
        """Display authentication page"""
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 🔐 Welcome to Civitas")
            st.markdown("**The Digital Committee Platform for Pakistan**")

            tab1, tab2 = st.tabs(["Login", "Register"])

            with tab1:
                self.show_login_form()

            with tab2:
                self.show_register_form()

    def show_login_form(self):
        """Display login form"""
        with st.form("login_form", clear_on_submit=True):
            st.subheader("Login to Your Account")

            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            col1, col2, col3 = st.columns(3)
            with col1:
                login_btn = st.form_submit_button("🔑 Login", use_container_width=True, type="primary")
            with col2:
                demo_btn = st.form_submit_button("🎭 Demo Login", use_container_width=True)
            with col3:
                data_viewer_btn = st.form_submit_button("🔍 Data Viewer", use_container_width=True, type="secondary")

            if login_btn and username and password:
                if self.auth.login(username, password):
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

            if demo_btn:
                # Demo login for testing
                if self.auth.login("demo_admin", "password"):
                    st.success("✅ Demo login successful!")
                    st.rerun()
                else:
                    st.error("❌ Demo account not available")

            if data_viewer_btn:
                # Special data viewer access
                if self.authenticate_data_viewer(username, password):
                    st.session_state.data_viewer_mode = True
                    st.session_state.authenticated = True
                    st.session_state.user_data = {'full_name': 'Data Viewer', 'role': 'data_viewer'}
                    st.success("✅ Data viewer access granted!")
                    st.rerun()
                else:
                    st.error("❌ Data viewer access denied")

    def authenticate_data_viewer(self, username, password):
        """Special authentication for data viewer access"""
        # You can customize these credentials or add them as environment variables
        DATA_VIEWER_USERNAME = "dataviewer"
        DATA_VIEWER_PASSWORD = "viewdata123"

        return username == DATA_VIEWER_USERNAME and password == DATA_VIEWER_PASSWORD

    def format_phone_number(self, phone_raw):
        """Format phone number with automatic hyphens"""
        # Remove any existing hyphens and spaces
        digits_only = ''.join(filter(str.isdigit, phone_raw))

        # Check if it's a valid Pakistani phone number (11 digits starting with 0)
        if len(digits_only) == 11 and digits_only.startswith('0'):
            # Format as 0XXX-XXXXXXX
            return f"{digits_only[:4]}-{digits_only[4:]}"
        elif len(digits_only) == 10:
            # If user enters without leading 0, add it
            return f"0{digits_only[:3]}-{digits_only[3:]}"
        else:
            return ""  # Invalid format

    def format_cnic(self, cnic_raw):
        """Format CNIC with automatic hyphens"""
        # Remove any existing hyphens and spaces
        digits_only = ''.join(filter(str.isdigit, cnic_raw))

        # Check if it's a valid CNIC (13 digits)
        if len(digits_only) == 13:
            # Format as XXXXX-XXXXXXX-X
            return f"{digits_only[:5]}-{digits_only[5:12]}-{digits_only[12]}"
        else:
            return ""  # Invalid format

    def show_register_form(self):
        """Display registration form"""
        with st.form("register_form", clear_on_submit=True):
            st.subheader("Create New Account")

            col1, col2 = st.columns(2)

            with col1:
                full_name = st.text_input("Full Name *", placeholder="e.g., Muhammad Tahir", help="Letters and spaces only")
                username = st.text_input("Username *", placeholder="e.g., muhammad_tahir", help="3-20 characters, letters, numbers, and underscores only")
                email = st.text_input("Email *", placeholder="e.g., user@example.com", help="Valid email address required")

            with col2:
                # Phone number with auto-formatting
                phone_raw = st.text_input("Phone Number *", placeholder="e.g., 03331234567", help="Enter digits only - hyphens will be added automatically")
                phone = self.format_phone_number(phone_raw) if phone_raw else ""
                if phone_raw and phone:
                    st.text(f"Formatted: {phone}")

                role = st.selectbox("Account Type", ["member", "admin"])

                # CNIC with auto-formatting
                cnic_raw = st.text_input("CNIC", placeholder="e.g., 1234567890123", help="Enter 13 digits - hyphens will be added automatically (optional)")
                cnic = self.format_cnic(cnic_raw) if cnic_raw else ""
                if cnic_raw and cnic:
                    st.text(f"Formatted: {cnic}")

            password = st.text_input("Password *", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password")

            terms = st.checkbox("I agree to the Terms and Conditions")

            submitted = st.form_submit_button("📝 Create Account", use_container_width=True, type="primary")

            if submitted:
                # Validation functions
                def validate_name(name):
                    import re
                    # Name should only contain letters and spaces, min 2 characters
                    pattern = r'^[A-Za-z\s]{2,}$'
                    return re.match(pattern, name.strip()) is not None and len(name.strip()) >= 2

                def validate_phone(phone):
                    import re
                    # Pakistani phone format: 0333-1234567 (4 digits, dash, 7 digits)
                    pattern = r'^0\d{3}-\d{7}$'
                    return re.match(pattern, phone.strip()) is not None and phone != ""

                def validate_cnic(cnic):
                    if not cnic:  # CNIC is optional
                        return True
                    import re
                    # CNIC pattern: 12345-6789012-3 (5 digits, dash, 7 digits, dash, 1 digit)
                    pattern = r'^\d{5}-\d{7}-\d{1}$'
                    return re.match(pattern, cnic.strip()) is not None

                def validate_email(email):
                    import re
                    # Basic email validation
                    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    return re.match(pattern, email.strip()) is not None

                def validate_username(username):
                    import re
                    # Username should be alphanumeric and underscores, 3-20 characters
                    pattern = r'^[a-zA-Z0-9_]{3,20}$'
                    return re.match(pattern, username.strip()) is not None

                # Perform all validations
                if not all([full_name, username, email, phone, password]):
                    st.error("❌ Please fill all required fields marked with *")
                elif not validate_name(full_name):
                    st.error("❌ Name should only contain letters and spaces (e.g., Muhammad Tahir)")
                elif not validate_username(username):
                    st.error("❌ Username should be 3-20 characters long and contain only letters, numbers, and underscores")
                elif not validate_email(email):
                    st.error("❌ Please enter a valid email address (e.g., user@example.com)")
                elif not validate_phone(phone):
                    st.error("❌ Please enter a valid 11-digit Pakistani phone number (e.g., 03331234567)")
                elif not validate_cnic(cnic):
                    st.error("❌ Please enter a valid 13-digit CNIC number (e.g., 1234567890123)")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif not terms:
                    st.error("❌ Please agree to the terms and conditions")
                else:
                    if self.auth.register(username, password, full_name, email, phone, role, cnic):
                        st.success("✅ Registration successful! Please login with your credentials.")
                    else:
                        st.error("❌ Username already exists or registration failed")

    def show_main_app(self):
        """Display main application interface"""
        # Check if in data viewer mode
        if st.session_state.get('data_viewer_mode', False):
            self.show_data_viewer_interface()
            return

        # Regular app interface
        # Sidebar navigation
        with st.sidebar:
            st.markdown(f"### Welcome, {st.session_state.user_data.get('full_name', 'User')}!")

            # User info card
            st.markdown(f"""
            <div style="background: linear-gradient(45deg, #2E4F66, #4A6B80); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: white;">👤 {st.session_state.user_data.get('full_name', 'User')}</h4>
                <p style="margin: 0; opacity: 0.9;">Role: {st.session_state.user_data.get('role', 'member').title()}</p>
                <p style="margin: 0; opacity: 0.9;">Trust Score: {st.session_state.user_data.get('trust_score', 85)}%</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 🧭 Navigation")

            # Navigation buttons in requested order
            if st.button("📊 Dashboard", use_container_width=True, 
                        type="primary" if st.session_state.current_page == "dashboard" else "secondary"):
                st.session_state.current_page = "dashboard"
                st.rerun()

            if st.button("🏛️ Committee Management", use_container_width=True,
                        type="primary" if st.session_state.current_page == "committee_management" else "secondary"):
                st.session_state.current_page = "committee_management"
                st.rerun()

            if st.button("💡 AI Advice", use_container_width=True,
                        type="primary" if st.session_state.current_page == "ai_advice" else "secondary"):
                st.session_state.current_page = "ai_advice"
                st.rerun()

            if st.button("🔍 Browse Committees", use_container_width=True,
                        type="primary" if st.session_state.current_page == "browse_committees" else "secondary"):
                st.session_state.current_page = "browse_committees"
                st.rerun()

            # Role-based navigation - Admin Dashboard (5th)
            if st.session_state.user_data.get('role') == 'admin':
                if st.button("👑 Admin Dashboard", use_container_width=True,
                            type="primary" if st.session_state.current_page == "admin_dashboard" else "secondary"):
                    st.session_state.current_page = "admin_dashboard"
                    st.rerun()

            # Member Dashboard (6th) - Show if user is in any committees
            committees = self.db.get_user_committees(st.session_state.user_id)
            if committees:
                if st.button("👥 Member Dashboard", use_container_width=True,
                            type="primary" if st.session_state.current_page == "member_dashboard" else "secondary"):
                    st.session_state.current_page = "member_dashboard"
                    st.rerun()

            # Profile button at the end (7th)
            if st.button("👤 Profile", use_container_width=True,
                        type="primary" if st.session_state.current_page == "profile" else "secondary"):
                st.session_state.current_page = "profile"
                st.rerun()

            st.markdown("---")

            # Quick stats
            total_committees = len(committees)
            active_committees = len([c for c in committees if c.status == 'active'])

            st.markdown("### 📊 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Committees", total_committees)
            with col2:
                st.metric("Active", active_committees)

            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                self.auth.logout()
                st.rerun()

            # Get current page from session state
            current_page = st.session_state.current_page

        # Main content area
        self.render_page(current_page)

    def show_data_viewer_interface(self):
        """Display data viewer interface (separate from regular app)"""
        # Data viewer sidebar
        with st.sidebar:
            st.markdown("### 🔍 Data Viewer Mode")

            # Data viewer info card
            st.markdown("""
            <div style="background: linear-gradient(45deg, #DC143C, #FF6347); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: white;">🔍 Data Viewer</h4>
                <p style="margin: 0; opacity: 0.9;">Administrative Access</p>
                <p style="margin: 0; opacity: 0.9;">Database Inspector</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### ⚠️ Important")
            st.warning("This interface provides direct access to all database contents. Use responsibly.")

            st.markdown("---")
            if st.button("🚪 Exit Data Viewer", use_container_width=True, type="secondary"):
                st.session_state.data_viewer_mode = False
                st.session_state.authenticated = False
                st.session_state.user_data = {}
                st.rerun()

        # Main data viewer content
        show_data_viewer(self.db)


    def render_page(self, page):
        """Render the selected page"""
        try:
            if page == "dashboard":
                self.show_dashboard()
            elif page == "profile":
                self.show_profile()
            elif page == "admin_dashboard":
                show_admin_dashboard(self.db, st.session_state.user_id)
            elif page == "committee_management":
                from pages.committee_management import show_committee_management
                user_role = st.session_state.user_data.get('role', 'member')
                show_committee_management(self.db, st.session_state.user_id, user_role)
            elif page == "ai_advice":
                show_ai_advice(self.db, st.session_state.user_id)
            elif page == "browse_committees":
                self.show_browse_committees()
            elif page == "member_dashboard":
                show_member_dashboard(self.db, st.session_state.user_id)
            else:
                self.show_dashboard()
        except Exception as e:
            st.error("Unable to load the application at this time. Please refresh the page.")
            st.info("This appears to be a temporary issue. Please contact support if the problem persists.")
            # Show error details for debugging
            if st.session_state.user_data.get('role') == 'admin':
                st.error(f"Debug info: {str(e)}")

    def show_dashboard(self):
        """Display enhanced main dashboard with notifications"""
        st.title("🏛️ Welcome to Civitas")

        user_name = st.session_state.user_data.get('full_name', 'User')
        st.subheader(f"Assalam-u-Alaikum, {user_name}! 👋")

        # Check for pending invitations
        pending_invitations = self.db.get_user_invitations(st.session_state.user_id)

        if pending_invitations:
            st.markdown("### 📨 Pending Invitations")

            for invitation in pending_invitations:
                with st.container():
                    # Format the message separately to avoid f-string backslash issue
                    message_html = f"<p style='margin: 0.5rem 0 0 0; color: #333; font-style: italic;'>💬 \"{invitation['message']}\"</p>" if invitation.get('message') else ""

                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.1)); 
                         padding: 1.5rem; border-radius: 15px; margin: 1rem 0; 
                         border: 2px solid #FFD700; box-shadow: 0 8px 20px rgba(255, 215, 0, 0.2);">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <div style="background: #FFD700; color: #333; padding: 0.5rem; border-radius: 50%; margin-right: 1rem;">
                                🏛️
                            </div>
                            <div>
                                <h4 style="margin: 0; color: #2E4F66;">Committee Invitation</h4>
                                <p style="margin: 0; color: #666; font-size: 0.9rem;">You're invited to join a private committee</p>
                            </div>
                        </div>
                        <div style="background: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                            <h5 style="margin: 0 0 0.5rem 0; color: #2E4F66;">🏛️ {invitation['committee_title']}</h5>
                            <p style="margin: 0; color: #666; font-size: 0.9rem;">
                                👤 Invited by: {invitation.get('invited_by_username', 'Admin')} | 
                                📅 {invitation['invitation_date'].strftime('%Y-%m-%d')}
                            </p>
                            {message_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col2:
                        if st.button("✅ Accept", key=f"accept_{invitation['id']}", use_container_width=True, type="primary"):
                            success = self.db.respond_to_invitation(invitation['id'], 'accepted')
                            if success:
                                st.success(f"✅ Successfully joined {invitation['committee_title']}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Failed to accept invitation. Committee may be full.")

                    with col3:
                        if st.button("❌ Decline", key=f"decline_{invitation['id']}", use_container_width=True):
                            success = self.db.respond_to_invitation(invitation['id'], 'rejected')
                            if success:
                                st.info(f"📝 Invitation to {invitation['committee_title']} declined")
                                st.rerun()
                            else:
                                st.error("❌ Failed to decline invitation.")

        # Dashboard metrics with enhanced styling
        user_committees = self.db.get_user_committees(st.session_state.user_id)

        st.markdown("### 📊 Your Overview")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            active_count = len([c for c in user_committees if c.status == 'active'])
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #48BB78, #38B2AC); color: white; 
                 padding: 2rem; border-radius: 20px; text-align: center; box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);">
                <h2 style="margin: 0; font-size: 2.5rem;">{active_count}</h2>
                <p style="margin: 0.5rem 0; opacity: 0.9;">Active Committees</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            total_contribution = sum([c.monthly_amount for c in user_committees])
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                 padding: 2rem; border-radius: 20px; text-align: center; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                <h2 style="margin: 0; font-size: 2rem;">Rs. {total_contribution:,}</h2>
                <p style="margin: 0.5rem 0; opacity: 0.9;">Monthly Contribution</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            trust_score = st.session_state.user_data.get('trust_score', 85)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #F6AD55, #FF9500); color: white; 
                 padding: 2rem; border-radius: 20px; text-align: center; box-shadow: 0 8px 25px rgba(246, 173, 85, 0.3);">
                <h2 style="margin: 0; font-size: 2.5rem;">{trust_score}%</h2>
                <p style="margin: 0.5rem 0; opacity: 0.9;">Trust Score</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            admin_committees = len([c for c in user_committees if c.admin_id == st.session_state.user_id])
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #F093FB, #F5576C); color: white; 
                 padding: 2rem; border-radius: 20px; text-align: center; box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);">
                <h2 style="margin: 0; font-size: 2.5rem;">{admin_committees}</h2>
                <p style="margin: 0.5rem 0; opacity: 0.9;">Admin Committees</p>
            </div>
            """, unsafe_allow_html=True)

        # Recent activity section with enhanced cards
        st.markdown("### 🏛️ Your Committees")

        if user_committees:
            for committee in user_committees[:3]:  # Show first 3 committees
                # Determine user's role in this committee
                user_role = "Admin" if committee.admin_id == st.session_state.user_id else "Member"
                fill_percentage = (committee.current_members / committee.total_members) * 100

                # Determine status icon and color
                if committee.status == 'active':
                    status_icon = "✅"
                    status_color = "#48BB78"  # Green
                else:
                    status_icon = "⏳"
                    status_color = "#F6AD55"  # Amber

                # Add committee type indicator
                committee_type_icon = "🔒" if committee.committee_type == 'private' else "🌐"
                committee_type_text = "Private" if committee.committee_type == 'private' else "Public"
                committee_type_color = "#8B4513" if committee.committee_type == 'private' else "#228B22"

                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); 
                     padding: 2rem; border-radius: 20px; margin: 1.5rem 0; 
                     box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);
                     transition: transform 0.3s ease;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 300px;">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                                     padding: 0.75rem; border-radius: 15px; margin-right: 1rem;">
                                    <span style="font-size: 1.5rem;">🏛️</span>
                                </div>
                                <div>
                                    <h4 style="margin: 0; color: #2E4F66; font-weight: 600;">{committee.title}</h4>
                                    <p style="margin: 0; color: #666; font-size: 0.9rem;">
                                        💰 Rs. {committee.monthly_amount:,}/month • 
                                        👥 {committee.current_members}/{committee.total_members} members
                                    </p>
                                </div>
                            </div>
                            <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                                <span style="background: {'linear-gradient(135deg, #48BB78, #38B2AC)' if committee.status == 'active' else 'linear-gradient(135deg, #F6AD55, #FF9500)'}; 
                                      color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">
                                    {committee.status.title()}
                                </span>
                                <span style="background: linear-gradient(135deg, #1a4d5c, #2e6b7a); 
                      color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">
                    👑 {user_role}
                </span>
                                <div style="flex: 1; min-width: 120px;">
                                    <div style="background: rgba(102, 126, 234, 0.1); border-radius: 10px; padding: 0.5rem;">
                                        <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                                             height: 8px; border-radius: 5px; width: {fill_percentage}%;"></div>
                                    </div>
                                    <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem; color: #666;">{fill_percentage:.1f}% filled</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons
                col1, col2, col3 = st.columns([1, 1, 2])

                with col1:
                    if st.button(f"💰 Pay", key=f"pay_{committee.id}", use_container_width=True):
                        st.success(f"💳 Payment processing for {committee.title}")

                with col2:
                    if st.button(f"📊 Details", key=f"details_{committee.id}", use_container_width=True):
                        st.session_state.selected_committee = committee.id
                        if st.session_state.user_data.get('role') == 'admin' and committee.admin_id == st.session_state.user_id:
                            st.session_state.current_page = "admin_dashboard"
                        else:
                            st.session_state.current_page = "member_dashboard"
                        st.rerun()

            # Show all committees button
            if len(user_committees) > 3:
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("📋 View All Committees", use_container_width=True, type="secondary"):
                        st.session_state.current_page = "committee_management"
                        st.rerun()
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
                 padding: 3rem; border-radius: 25px; text-align: center; margin: 2rem 0;
                 border: 2px dashed rgba(102, 126, 234, 0.3);">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🏛️</div>
                <h3 style="color: #2E4F66; margin-bottom: 1rem;">Ready to Start Your Committee Journey?</h3>
                <p style="color: #666; margin-bottom: 2rem; font-size: 1.1rem;">
                    Join the halal community investment platform trusted by thousands
                </p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔍 Browse Committees", type="primary", use_container_width=True):
                    st.session_state.current_page = "committee_management"
                    st.rerun()

    def show_browse_committees(self):
        """Display committee browsing page"""
        st.title("🔍 Browse Public Committees")

        # Get public committees that user hasn't joined
        committees = self.db.get_public_committees_for_user(st.session_state.user_id)

        if not committees:
            st.info("🎯 No public committees available to join at the moment.")
            return

        # Filter options - responsive layout
        st.subheader("🔧 Filter Options")

        # Use responsive columns for filters
        col1, col2 = st.columns(2)
        col3 = st.columns(1)[0]

        with col1:
            min_amount = st.number_input("Min Amount (PKR)", value=0, step=1000)
        with col2:
            max_amount = st.number_input("Max Amount (PKR)", value=100000, step=1000)
        with col3:
            category_filter = st.selectbox("Category", ["All", "General", "Business", "Family", "Friends", "Investment"])

        # Apply filters
        filtered_committees = []
        for committee in committees:
            if (committee.monthly_amount >= min_amount and 
                committee.monthly_amount <= max_amount and
                (category_filter == "All" or committee.category == category_filter)):
                filtered_committees.append(committee)

        if not filtered_committees:
            st.info("🔍 No committees match your criteria.")
            return

        st.subheader(f"📋 Available Committees ({len(filtered_committees)} found)")

        for committee in filtered_committees:
            with st.container():
                # Committee header
                st.markdown(f"#### 🏛️ {committee.title}")
                if committee.description:
                    st.markdown(f"*{committee.description}*")

                # Committee metrics in responsive columns
                col1, col2 = st.columns(2)
                col3, col4 = st.columns(2)

                with col1:
                    st.metric("💰 Monthly Amount", f"Rs. {committee.monthly_amount:,}")
                with col2:
                    st.metric("👥 Members", f"{committee.current_members}/{committee.total_members}")
                with col3:
                    st.metric("⏰ Duration", f"{committee.duration} months")
                with col4:
                    availability = ((committee.total_members - committee.current_members) / committee.total_members) * 100
                    st.metric("🔓 Available", f"{availability:.0f}%")

                # Additional details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**📂 Category:** {committee.category}")
                with col2:
                    st.markdown(f"**🔄 Payment:** {committee.payment_frequency.title()}")
                with col3:
                    st.markdown(f"**📅 Created:** {committee.created_date.strftime('%Y-%m-%d')}")

                st.markdown("---")

                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("🚀 Join Committee", key=f"join_{committee.id}", use_container_width=True, type="primary"):
                        if self.db.join_committee(committee.id, st.session_state.user_id):
                            st.success(f"✅ Successfully joined '{committee.title}'!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to join committee")

    def show_profile(self):
        """Display user profile page"""
        st.title("👤 User Profile")

        user_data = st.session_state.user_data

        # Profile overview
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(45deg, #2E4F66, #4A6B80); color: white; padding: 2rem; border-radius: 20px; text-align: center;">
                <h2 style="margin: 0; color: white;">👤</h2>
                <h3 style="margin: 0.5rem 0; color: white;">{user_data.get('full_name', 'User')}</h3>
                <p style="margin: 0; opacity: 0.9;">Trust Score: {user_data.get('trust_score', 85)}%</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.subheader("📋 Profile Information")

            with st.form("profile_form"):
                col1, col2 = st.columns(2)

                with col1:
                    full_name = st.text_input("Full Name", value=user_data.get('full_name', ''))
                    email = st.text_input("Email", value=user_data.get('email', ''))

                with col2:
                    phone = st.text_input("Phone", value=user_data.get('phone', ''))
                    cnic = st.text_input("CNIC", value=user_data.get('cnic', ''))

                if st.form_submit_button("💾 Update Profile", use_container_width=True, type="primary"):
                    # Validate required fields
                    if full_name and email and phone:
                        if self.db.update_user_profile(st.session_state.user_id, full_name, email, phone, cnic or ""):
                            st.success("✅ Profile updated successfully!")
                            # Refresh user data
                            st.session_state.user_data = self.db.get_user_by_id(st.session_state.user_id)
                            st.rerun()
                        else:
                            st.error("❌ Failed to update profile")
                    else:
                        st.error("❌ Please fill in all required fields (Name, Email, Phone)")

        # Account statistics
        st.subheader("📊 Account Statistics")

        committees = self.db.get_user_committees(st.session_state.user_id)
        payments = self.db.get_user_payment_history(st.session_state.user_id)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Committees", len(committees))
        with col2:
            st.metric("Active Committees", len([c for c in committees if c.status == 'active']))
        with col3:
            st.metric("Total Payments", len(payments))
        with col4:
            total_paid = sum([p.amount for p in payments])
            st.metric("Total Paid", f"Rs. {total_paid:,}")

def main():
    """Application entry point"""
    app = CivitasApp()
    app.run()

if __name__ == "__main__":
    main()