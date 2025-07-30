import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

def show_committee_management():
    st.title("🏛️ Committee Management")
    
    if not st.session_state.get('authenticated', False):
        st.error("Please login to access this page")
        return
    
    tab1, tab2, tab3 = st.tabs(["📋 My Committees", "➕ Create Committee", "🔍 Browse Committees"])
    
    with tab1:
        show_my_committees()
    
    with tab2:
        show_create_committee()
    
    with tab3:
        show_browse_committees()

def show_my_committees():
    st.subheader("My Committees")
    
    user_committees = get_user_committees()
    
    if not user_committees:
        st.info("You haven't joined any committees yet.")
        return
    
    for committee in user_committees:
        with st.expander(f"{committee['title']} - Rs. {committee['monthly_amount']:,}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Type:** {committee['type'].title()}")
                st.write(f"**Members:** {committee['current_members']}/{committee['total_members']}")
                st.write(f"**Duration:** {committee['duration']} months")
                st.write(f"**Status:** {committee['status'].title()}")
            
            with col2:
                st.write(f"**Monthly Amount:** Rs. {committee['monthly_amount']:,}")
                st.write(f"**Created:** {committee['created_date']}")
                
                if committee['admin_id'] == st.session_state.current_user:
                    st.write("**Your Role:** 👑 Admin")
                    if st.button(f"Manage Committee", key=f"manage_{committee['id']}"):
                        show_admin_panel(committee)
                else:
                    st.write("**Your Role:** 👤 Member")

def show_create_committee():
    st.subheader("Create New Committee")
    
    with st.form("create_committee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Committee Title*")
            monthly_amount = st.number_input("Monthly Amount (PKR)*", min_value=1000, value=5000, step=500)
            total_members = st.number_input("Total Members*", min_value=2, max_value=50, value=10)
        
        with col2:
            duration = st.number_input("Duration (months)*", min_value=1, max_value=60, value=12)
            committee_type = st.selectbox("Committee Type*", ["public", "private"])
            category = st.selectbox("Category", ["General", "Business", "Family", "Friends", "Investment"])
        
        description = st.text_area("Description", placeholder="Describe the purpose of this committee...")
        
        terms = st.checkbox("I agree to the terms and conditions")
        
        submitted = st.form_submit_button("Create Committee", use_container_width=True)
        
        if submitted:
            if not all([title, monthly_amount, total_members, duration]):
                st.error("Please fill all required fields marked with *")
            elif not terms:
                st.error("Please agree to the terms and conditions")
            else:
                create_committee(title, monthly_amount, total_members, duration, committee_type, category, description)

def show_browse_committees():
    st.subheader("Browse Public Committees")
    
    public_committees = get_public_committees()
    
    if not public_committees:
        st.info("No public committees available at the moment.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_amount = st.number_input("Min Amount (PKR)", value=0, step=1000)
    with col2:
        max_amount = st.number_input("Max Amount (PKR)", value=100000, step=1000)
    with col3:
        category_filter = st.selectbox("Category", ["All", "General", "Business", "Family", "Friends", "Investment"])
    
    # Filter committees
    filtered_committees = []
    for committee in public_committees:
        if (committee['monthly_amount'] >= min_amount and 
            committee['monthly_amount'] <= max_amount and
            (category_filter == "All" or committee.get('category', 'General') == category_filter) and
            st.session_state.current_user not in committee['members'] and
            committee['current_members'] < committee['total_members']):
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
                if st.button("Join Committee", key=f"join_{committee['id']}"):
                    join_committee(committee['id'])

def create_committee(title, monthly_amount, total_members, duration, committee_type, category, description):
    committee_id = str(uuid.uuid4())
    
    new_committee = {
        'id': committee_id,
        'title': title,
        'monthly_amount': monthly_amount,
        'total_members': total_members,
        'current_members': 1,
        'duration': duration,
        'type': committee_type,
        'category': category,
        'description': description,
        'admin_id': st.session_state.current_user,
        'status': 'active',
        'created_date': datetime.now().strftime("%Y-%m-%d"),
        'members': [st.session_state.current_user],
        'payment_history': [],
        'payout_schedule': []
    }
    
    if 'committees' not in st.session_state:
        st.session_state.committees = []
    
    st.session_state.committees.append(new_committee)
    st.success(f"Committee '{title}' created successfully!")
    st.balloons()
    st.rerun()

def join_committee(committee_id):
    committees = st.session_state.get('committees', [])
    
    for committee in committees:
        if committee['id'] == committee_id:
            if st.session_state.current_user not in committee['members']:
                committee['members'].append(st.session_state.current_user)
                committee['current_members'] += 1
                st.success(f"Successfully joined '{committee['title']}'!")
                st.balloons()
                st.rerun()
            else:
                st.error("You are already a member of this committee")
            break

def get_user_committees():
    committees = st.session_state.get('committees', [])
    return [c for c in committees if st.session_state.current_user in c['members']]

def get_public_committees():
    committees = st.session_state.get('committees', [])
    return [c for c in committees if c['type'] == 'public']

def show_admin_panel(committee):
    st.subheader(f"Admin Panel - {committee['title']}")
    
    tab1, tab2, tab3 = st.tabs(["👥 Members", "💰 Payments", "⚙️ Settings"])
    
    with tab1:
        show_member_management(committee)
    
    with tab2:
        show_payment_management(committee)
    
    with tab3:
        show_committee_settings(committee)

def show_member_management(committee):
    st.write("### Committee Members")
    
    members_data = []
    users = st.session_state.get('users', [])
    
    for member_id in committee['members']:
        member = next((u for u in users if u['username'] == member_id), None)
        if member:
            members_data.append({
                'Name': member['full_name'],
                'Username': member['username'],
                'Trust Score': f"{member.get('trust_score', 85)}%",
                'Status': 'Admin' if member_id == committee['admin_id'] else 'Member',
                'Payment Status': 'Paid',  # Simplified for MVP
                'Join Date': committee['created_date']
            })
    
    if members_data:
        df = pd.DataFrame(members_data)
        st.dataframe(df, use_container_width=True)
        
        # Member actions
        st.write("### Member Actions")
        selected_member = st.selectbox("Select Member", [m['Username'] for m in members_data if m['Username'] != st.session_state.current_user])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Send Reminder"):
                st.success(f"Payment reminder sent to {selected_member}")
        with col2:
            if st.button("Remove Member"):
                st.warning(f"Member {selected_member} would be removed (simulation)")

def show_payment_management(committee):
    st.write("### Payment Tracking")
    
    # Payment overview
    col1, col2, col3 = st.columns(3)
    
    total_collected = committee['current_members'] * committee['monthly_amount']
    expected_total = committee['total_members'] * committee['monthly_amount'] * committee['duration']
    
    with col1:
        st.metric("This Month Collected", f"Rs. {total_collected:,}")
    with col2:
        st.metric("Expected Total", f"Rs. {expected_total:,}")
    with col3:
        collection_rate = (committee['current_members'] / committee['total_members']) * 100
        st.metric("Collection Rate", f"{collection_rate:.1f}%")
    
    # Payout simulation
    st.write("### Payout Management")
    
    payout_amount = total_collected
    payout_type = st.selectbox("Payout Type", ["Cash Transfer", "Halal Product Vouchers", "Bank Transfer"])
    
    if st.button("Simulate Payout"):
        st.success(f"Payout of Rs. {payout_amount:,} via {payout_type} has been processed!")
        st.balloons()

def show_committee_settings(committee):
    st.write("### Committee Settings")
    
    with st.form("committee_settings"):
        new_title = st.text_input("Committee Title", value=committee['title'])
        new_description = st.text_area("Description", value=committee.get('description', ''))
        
        committee_status = st.selectbox("Status", ["active", "paused", "completed"], 
                                      index=0 if committee['status'] == 'active' else 1)
        
        if st.form_submit_button("Update Settings"):
            # Update committee in session state
            committees = st.session_state.get('committees', [])
            for i, c in enumerate(committees):
                if c['id'] == committee['id']:
                    committees[i]['title'] = new_title
                    committees[i]['description'] = new_description
                    committees[i]['status'] = committee_status
                    break
            
            st.success("Committee settings updated successfully!")
            st.rerun()
    
    # Danger zone
    st.write("### Danger Zone")
    with st.expander("⚠️ Delete Committee"):
        st.warning("This action cannot be undone. All member data will be lost.")
        if st.button("Delete Committee", type="primary"):
            st.error("Committee deletion is not available in this demo version.")

if __name__ == "__main__":
    show_committee_management()
