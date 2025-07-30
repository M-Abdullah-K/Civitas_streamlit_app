import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
from utils.auth import initialize_session_state, login_user, register_user, logout_user
from utils.data_manager import initialize_data, get_user_committees

# Page configuration
st.set_page_config(
    page_title="Civitas - Digital Committee Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Pakistani theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #228B22, #FFD700);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .committee-card {
        background: #F0F8F0;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #228B22;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #228B22, #32CD32);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
    .status-paid {
        background: #228B22;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .status-unpaid {
        background: #DC143C;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .trust-score {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state and data
    initialize_session_state()
    initialize_data()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Civitas</h1>
        <p style="color: white; font-size: 1.2rem; margin: 0;">Digital Committee Platform for Pakistan</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication check
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

def show_auth_page():
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Civitas")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if login_user(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Create Account")
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            user_role = st.selectbox("Account Type", ["Member", "Admin"])
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("Register", use_container_width=True)
            
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif register_user(username, password, full_name, email, phone, user_role.lower()):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")

def show_browse_committees():
    st.header("🔍 Browse Public Committees")
    
    # Get only public committees that user hasn't joined
    all_committees = st.session_state.get('committees', [])
    public_committees = [c for c in all_committees 
                        if c['type'] == 'public' and 
                        st.session_state.current_user not in c['members'] and
                        c['current_members'] < c['total_members']]
    
    if not public_committees:
        st.info("No public committees available to join at the moment.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_amount = st.number_input("Min Amount (PKR)", value=0, step=1000)
    with col2:
        max_amount = st.number_input("Max Amount (PKR)", value=100000, step=1000)
    with col3:
        category_filter = st.selectbox("Category", ["All", "General", "Business", "Family", "Friends", "Investment"])
    
    # Apply filters
    filtered_committees = []
    for committee in public_committees:
        if (committee['monthly_amount'] >= min_amount and 
            committee['monthly_amount'] <= max_amount and
            (category_filter == "All" or committee.get('category', 'General') == category_filter)):
            filtered_committees.append(committee)
    
    if not filtered_committees:
        st.info("No committees match your criteria.")
        return
    
    for committee in filtered_committees:
        with st.container():
            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 1rem; margin: 1rem 0; border-radius: 8px; background: #f9f9f9;">
                <h4>{committee['title']}</h4>
                <p><strong>Amount:</strong> Rs. {committee['monthly_amount']:,}/month</p>
                <p><strong>Members:</strong> {committee['current_members']}/{committee['total_members']}</p>
                <p><strong>Duration:</strong> {committee['duration']} months</p>
                <p><strong>Category:</strong> {committee.get('category', 'General')}</p>
                <p>{committee.get('description', 'No description provided.')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Join Committee", key=f"join_browse_{committee['id']}"):
                    committee['members'].append(st.session_state.current_user)
                    committee['current_members'] += 1
                    st.success(f"Successfully joined '{committee['title']}'!")
                    st.rerun()

def show_main_app():
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_data['full_name']}!")
        st.markdown(f"**Role:** {st.session_state.user_data['role']}")
        
        # Navigation - different for admin vs member
        if st.session_state.user_data['role'] == 'admin':
            pages = {
                "🏠 Dashboard": "dashboard",
                "🏛️ Committee Management": "committee_management",
                "👑 Admin Dashboard": "admin_dashboard",
                "🤖 AI Financial Advice": "ai_advice",
                "👤 Profile": "profile"
            }
        else:
            pages = {
                "🏠 Dashboard": "dashboard",
                "🔍 Browse Committees": "browse_committees",
                "👤 Member Dashboard": "member_dashboard",
                "🤖 AI Financial Advice": "ai_advice",
                "👤 Profile": "profile"
            }
        
        selected_page = st.selectbox("Navigate to:", list(pages.keys()))
        current_page = pages[selected_page]
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Main content area
    if current_page == "dashboard":
        show_dashboard()
    elif current_page == "committee_management":
        show_committee_management()
    elif current_page == "admin_dashboard":
        from pages.admin_dashboard import show_admin_dashboard
        show_admin_dashboard()
    elif current_page == "browse_committees":
        show_browse_committees()
    elif current_page == "member_dashboard":
        from pages.member_dashboard import show_member_dashboard
        show_member_dashboard()
    elif current_page == "ai_advice":
        show_ai_advice()
    elif current_page == "profile":
        show_profile()

def show_dashboard():
    user_committees = get_user_committees(st.session_state.current_user)
    
    if not user_committees:
        st.info("You haven't joined any committees yet. Visit Committee Management to create or join one!")
        return
    
    st.header("📊 Your Dashboard")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_committees = len(user_committees)
    total_contribution = sum([c['monthly_amount'] for c in user_committees])
    active_committees = len([c for c in user_committees if c['status'] == 'active'])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_committees}</h3>
            <p>Total Committees</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Rs. {total_contribution:,}</h3>
            <p>Monthly Contribution</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{active_committees}</h3>
            <p>Active Committees</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        trust_score = st.session_state.user_data.get('trust_score', 85)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{trust_score}%</h3>
            <p>Trust Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Committee details
    st.subheader("Your Committees")
    
    for committee in user_committees:
        with st.container():
            st.markdown(f"""
            <div class="committee-card">
                <h4>{committee['title']}</h4>
                <p><strong>Monthly Amount:</strong> Rs. {committee['monthly_amount']:,}</p>
                <p><strong>Members:</strong> {committee['current_members']}/{committee['total_members']}</p>
                <p><strong>Duration:</strong> {committee['duration']} months</p>
                <p><strong>Status:</strong> <span class="status-{'paid' if committee.get('payment_status') == 'paid' else 'unpaid'}">{committee.get('payment_status', 'unpaid').upper()}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.user_data['role'] == 'admin' and committee['admin_id'] == st.session_state.current_user:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Manage {committee['title']}", key=f"manage_{committee['id']}"):
                        st.session_state.selected_committee = committee['id']
                        show_admin_dashboard(committee)
                with col2:
                    if st.button(f"View Members", key=f"members_{committee['id']}"):
                        show_committee_members(committee)

def show_committee_management():
    st.header("🏛️ Committee Management")
    
    # Different tabs for admin vs member
    if st.session_state.user_data['role'] == 'admin':
        tab1, tab2, tab3 = st.tabs(["📋 My Committees", "➕ Create Committee", "🔍 Join Committee"])
    else:
        tab1, tab3 = st.tabs(["📋 My Committees", "🔍 Join Committee"])
        tab2 = None
    
    with tab1:
        user_committees = get_user_committees(st.session_state.current_user)
        if user_committees:
            for committee in user_committees:
                with st.expander(f"{committee['title']} - Rs. {committee['monthly_amount']:,}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {committee['type'].title()}")
                        st.write(f"**Members:** {committee['current_members']}/{committee['total_members']}")
                        st.write(f"**Duration:** {committee['duration']} months")
                    with col2:
                        st.write(f"**Status:** {committee['status'].title()}")
                        st.write(f"**Created:** {committee['created_date']}")
                        if committee['admin_id'] == st.session_state.current_user:
                            st.write("**Role:** Admin")
                        else:
                            st.write("**Role:** Member")
        else:
            st.info("You haven't joined any committees yet.")
    
    if tab2 is not None:  # Only show for admins
        with tab2:
            st.subheader("Create New Committee")
            with st.form("create_committee"):
                title = st.text_input("Committee Title")
                monthly_amount = st.number_input("Monthly Amount (PKR)", min_value=1000, step=500)
                total_members = st.number_input("Total Members", min_value=2, max_value=50, value=10)
                duration = st.number_input("Duration (months)", min_value=1, max_value=60, value=12)
                committee_type = st.selectbox("Committee Type", ["public", "private"])
                description = st.text_area("Description")
                
                submitted = st.form_submit_button("Create Committee")
                
                if submitted and title:
                    committee_id = str(uuid.uuid4())
                    new_committee = {
                        'id': committee_id,
                        'title': title,
                        'monthly_amount': monthly_amount,
                        'total_members': total_members,
                        'current_members': 1,
                        'duration': duration,
                        'type': committee_type,
                        'description': description,
                        'admin_id': st.session_state.current_user,
                        'status': 'active',
                        'created_date': datetime.now().strftime("%Y-%m-%d"),
                        'members': [st.session_state.current_user]
                    }
                    
                    if 'committees' not in st.session_state:
                        st.session_state.committees = []
                    st.session_state.committees.append(new_committee)
                    
                    st.success(f"Committee '{title}' created successfully!")
                    st.rerun()
    
    with tab3:
        st.subheader("Join Public Committees")
        public_committees = [c for c in st.session_state.get('committees', []) 
                           if c['type'] == 'public' and 
                           st.session_state.current_user not in c['members'] and
                           c['current_members'] < c['total_members']]
        
        if public_committees:
            for committee in public_committees:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{committee['title']}**")
                        st.write(f"Rs. {committee['monthly_amount']:,}/month • {committee['current_members']}/{committee['total_members']} members")
                        st.write(f"{committee['description']}")
                    with col2:
                        if st.button("Join", key=f"join_{committee['id']}"):
                            committee['members'].append(st.session_state.current_user)
                            committee['current_members'] += 1
                            st.success("Joined successfully!")
                            st.rerun()
        else:
            st.info("No public committees available to join.")



def show_admin_dashboard(committee):
    st.subheader(f"Admin Dashboard - {committee['title']}")
    
    # Member management
    members_data = []
    for member_id in committee['members']:
        member_info = next((u for u in st.session_state.users if u['username'] == member_id), None)
        if member_info:
            members_data.append({
                'Name': member_info['full_name'],
                'Username': member_info['username'],
                'Trust Score': member_info.get('trust_score', 85),
                'Payment Status': 'Paid' if member_id == committee['admin_id'] else 'Unpaid',
                'Join Date': committee['created_date']
            })
    
    df = pd.DataFrame(members_data)
    st.dataframe(df, use_container_width=True)
    
    # Payout management
    st.subheader("Payout Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Simulate Payout"):
            st.success("Payout of Rs. 50,000 scheduled for next cycle!")
    
    with col2:
        payout_type = st.selectbox("Payout Type", ["Cash", "Halal Product Rewards"])

def show_committee_members(committee):
    st.subheader(f"Members of {committee['title']}")
    
    for member_id in committee['members']:
        member_info = next((u for u in st.session_state.users if u['username'] == member_id), None)
        if member_info:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{member_info['full_name']}**")
                st.write(f"@{member_info['username']}")
            with col2:
                trust_score = member_info.get('trust_score', 85)
                st.markdown(f'<div class="trust-score">{trust_score}% Trust</div>', unsafe_allow_html=True)
            with col3:
                if member_id == committee['admin_id']:
                    st.write("👑 Admin")
                else:
                    st.write("👤 Member")

def show_ai_advice():
    st.header("🤖 AI Financial Advisor")
    
    # User financial profile
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Financial Profile")
        monthly_income = st.number_input("Monthly Income (PKR)", value=50000, step=5000)
        monthly_expenses = st.number_input("Monthly Expenses (PKR)", value=30000, step=2000)
        savings_goal = st.number_input("Monthly Savings Goal (PKR)", value=10000, step=1000)
    
    with col2:
        st.subheader("Committee Commitments")
        user_committees = get_user_committees(st.session_state.current_user)
        total_committee_amount = sum([c['monthly_amount'] for c in user_committees])
        st.metric("Total Monthly Commitments", f"Rs. {total_committee_amount:,}")
        
        disposable_income = monthly_income - monthly_expenses - total_committee_amount
        st.metric("Remaining Income", f"Rs. {disposable_income:,}")
    
    # AI Recommendations
    st.subheader("💡 Personalized Recommendations")
    
    if disposable_income < 0:
        st.error("⚠️ Risk Alert: Your committee commitments exceed your disposable income!")
        st.write("**Recommendations:**")
        st.write("- Consider reducing monthly expenses by Rs. " + f"{abs(disposable_income):,}")
        st.write("- Look for additional income sources")
        st.write("- Consider leaving some committees if necessary")
    
    elif disposable_income < 5000:
        st.warning("⚡ Low Buffer: You have limited financial cushion")
        st.write("**Recommendations:**")
        st.write("- Build an emergency fund of Rs. 15,000")
        st.write("- Avoid taking on new committee commitments")
        st.write("- Consider increasing your income")
    
    else:
        st.success("✅ Good Financial Health!")
        st.write("**Recommendations:**")
        st.write(f"- You can safely save Rs. {min(disposable_income-2000, savings_goal):,} per month")
        st.write("- Consider joining 1-2 more committees for diversification")
        st.write("- Explore halal investment options with your surplus")
    
    # Savings projection
    st.subheader("📈 Savings Projection")
    
    months = list(range(1, 13))
    projected_savings = []
    monthly_saving = max(0, disposable_income - 2000)  # Keep 2000 as buffer
    
    for month in months:
        projected_savings.append(monthly_saving * month)
    
    chart_data = pd.DataFrame({
        'Month': months,
        'Projected Savings': projected_savings
    })
    
    st.line_chart(chart_data.set_index('Month'))
    
    # Committee recommendations
    st.subheader("🏛️ Committee Recommendations")
    
    if disposable_income > 10000:
        st.write("**Recommended Committee Types:**")
        st.write("- High-value committees (Rs. 8,000-15,000/month)")
        st.write("- Medium-term duration (12-18 months)")
        st.write("- Mix of public and private committees")
    elif disposable_income > 5000:
        st.write("**Recommended Committee Types:**")
        st.write("- Medium-value committees (Rs. 3,000-7,000/month)")
        st.write("- Short to medium-term (6-12 months)")
        st.write("- Focus on public committees for flexibility")
    else:
        st.write("**Recommended Committee Types:**")
        st.write("- Low-value committees (Rs. 1,000-3,000/month)")
        st.write("- Short-term duration (3-6 months)")
        st.write("- Start with one committee only")

def show_profile():
    st.header("👤 Profile Management")
    
    user_data = st.session_state.user_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        st.write(f"**Full Name:** {user_data['full_name']}")
        st.write(f"**Username:** {user_data['username']}")
        st.write(f"**Email:** {user_data['email']}")
        st.write(f"**Phone:** {user_data['phone']}")
        st.write(f"**Role:** {user_data['role']}")
        
        trust_score = user_data.get('trust_score', 85)
        st.markdown(f'**Trust Score:** <div class="trust-score">{trust_score}%</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Account Statistics")
        user_committees = get_user_committees(st.session_state.current_user)
        
        st.metric("Committees Joined", len(user_committees))
        st.metric("Committees as Admin", len([c for c in user_committees if c['admin_id'] == st.session_state.current_user]))
        
        total_contribution = sum([c['monthly_amount'] for c in user_committees])
        st.metric("Monthly Commitments", f"Rs. {total_contribution:,}")
        
        # Account activity
        st.write(f"**Account Created:** {user_data.get('created_date', 'N/A')}")
        st.write(f"**Last Login:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
