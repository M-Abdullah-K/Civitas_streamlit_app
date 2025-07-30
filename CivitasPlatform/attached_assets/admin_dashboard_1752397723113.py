import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def show_admin_dashboard():
    st.title("👑 Admin Dashboard")
    
    if not st.session_state.get('authenticated', False):
        st.error("Please login to access this page")
        return
    
    # Check if user is admin of any committee
    admin_committees = get_admin_committees()
    
    if not admin_committees:
        st.info("You are not an admin of any committees yet. Create a committee to access admin features.")
        return
    
    # Committee selector
    selected_committee_title = st.selectbox(
        "Select Committee to Manage",
        [c['title'] for c in admin_committees]
    )
    
    selected_committee = next(c for c in admin_committees if c['title'] == selected_committee_title)
    
    # Admin dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Members", "💰 Finances", "⚙️ Management"])
    
    with tab1:
        show_overview(selected_committee)
    
    with tab2:
        show_member_management(selected_committee)
    
    with tab3:
        show_financial_management(selected_committee)
    
    with tab4:
        show_committee_management(selected_committee)

def get_admin_committees():
    committees = st.session_state.get('committees', [])
    return [c for c in committees if c['admin_id'] == st.session_state.current_user]

def show_overview(committee):
    st.subheader(f"Overview - {committee['title']}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Members",
            f"{committee['current_members']}/{committee['total_members']}",
            f"{committee['current_members'] - committee['total_members']}"
        )
    
    with col2:
        monthly_collection = committee['current_members'] * committee['monthly_amount']
        st.metric(
            "Monthly Collection",
            f"Rs. {monthly_collection:,}",
            "100%" if committee['current_members'] == committee['total_members'] else f"{(committee['current_members']/committee['total_members']*100):.1f}%"
        )
    
    with col3:
        total_pool = monthly_collection * committee['duration']
        st.metric(
            "Total Pool Value",
            f"Rs. {total_pool:,}",
            "Projected"
        )
    
    with col4:
        completion_rate = (committee['current_members'] / committee['total_members']) * 100
        st.metric(
            "Fill Rate",
            f"{completion_rate:.1f}%",
            f"{committee['total_members'] - committee['current_members']} slots left"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Member growth chart
        st.subheader("Member Growth")
        
        # Generate dummy growth data
        dates = [datetime.now() - timedelta(days=30-i) for i in range(31)]
        members = [min(i//3 + 1, committee['current_members']) for i in range(31)]
        
        growth_df = pd.DataFrame({
            'Date': dates,
            'Members': members
        })
        
        fig = px.line(growth_df, x='Date', y='Members', 
                     title=f"Member Growth - {committee['title']}")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Payment status pie chart
        st.subheader("Payment Status")
        
        paid_members = committee['current_members']  # Assuming all current members paid
        unpaid_members = 0  # For simplicity in MVP
        
        fig = go.Figure(data=[go.Pie(
            labels=['Paid', 'Unpaid'],
            values=[paid_members, unpaid_members],
            hole=.3,
            marker_colors=['#228B22', '#DC143C']
        )])
        fig.update_layout(height=300, title="This Month's Payments")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    activity_data = [
        {"Date": "2024-12-20", "Activity": "New member joined", "Details": "Ahmed Khan joined the committee"},
        {"Date": "2024-12-19", "Activity": "Payment received", "Details": f"Rs. {committee['monthly_amount']:,} from Sara Ali"},
        {"Date": "2024-12-18", "Activity": "Committee updated", "Details": "Description updated"},
        {"Date": "2024-12-17", "Activity": "Payment received", "Details": f"Rs. {committee['monthly_amount']:,} from Ali Hassan"},
    ]
    
    for activity in activity_data:
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 4])
            with col1:
                st.write(activity["Date"])
            with col2:
                st.write(f"**{activity['Activity']}**")
            with col3:
                st.write(activity["Details"])

def show_member_management(committee):
    st.subheader("Member Management")
    
    # Generate member data
    users = st.session_state.get('users', [])
    members_data = []
    
    for member_id in committee['members']:
        member = next((u for u in users if u['username'] == member_id), None)
        if member:
            members_data.append({
                'Name': member['full_name'],
                'Username': member['username'],
                'Email': member['email'],
                'Phone': member['phone'],
                'Trust Score': member.get('trust_score', random.randint(75, 95)),
                'Payment Status': 'Paid' if random.random() > 0.2 else 'Unpaid',
                'Join Date': committee['created_date'],
                'Role': 'Admin' if member_id == committee['admin_id'] else 'Member'
            })
    
    if members_data:
        df = pd.DataFrame(members_data)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            payment_filter = st.selectbox("Filter by Payment", ["All", "Paid", "Unpaid"])
        with col2:
            role_filter = st.selectbox("Filter by Role", ["All", "Admin", "Member"])
        with col3:
            min_trust_score = st.slider("Min Trust Score", 0, 100, 0)
        
        # Apply filters
        filtered_df = df.copy()
        if payment_filter != "All":
            filtered_df = filtered_df[filtered_df['Payment Status'] == payment_filter]
        if role_filter != "All":
            filtered_df = filtered_df[filtered_df['Role'] == role_filter]
        filtered_df = filtered_df[filtered_df['Trust Score'] >= min_trust_score]
        
        # Display table
        st.dataframe(filtered_df, use_container_width=True)
        
        # Member actions
        st.subheader("Member Actions")
        
        if len(filtered_df) > 0:
            selected_member = st.selectbox(
                "Select Member for Actions",
                filtered_df['Username'].tolist()
            )
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("💌 Send Reminder"):
                    st.success(f"Payment reminder sent to {selected_member}")
            
            with col2:
                if st.button("📞 Contact Member"):
                    member_data = filtered_df[filtered_df['Username'] == selected_member].iloc[0]
                    st.info(f"Contact: {member_data['Phone']} | {member_data['Email']}")
            
            with col3:
                if st.button("⚠️ Issue Warning"):
                    st.warning(f"Warning issued to {selected_member}")
            
            with col4:
                if st.button("🚫 Remove Member"):
                    if st.button("Confirm Removal", key="confirm_remove"):
                        st.error(f"Member {selected_member} has been removed")
    
    # Pending join requests (for private committees)
    if committee['type'] == 'private':
        st.subheader("Pending Join Requests")
        
        # Simulate pending requests
        pending_requests = [
            {'name': 'Fatima Sheikh', 'trust_score': 88, 'mutual_connections': 3},
            {'name': 'Hassan Ali', 'trust_score': 92, 'mutual_connections': 1},
        ]
        
        if pending_requests:
            for request in pending_requests:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.write(f"**{request['name']}**")
                with col2:
                    st.write(f"Trust Score: {request['trust_score']}%")
                with col3:
                    if st.button("✅ Approve", key=f"approve_{request['name']}"):
                        st.success(f"{request['name']} approved!")
                with col4:
                    if st.button("❌ Reject", key=f"reject_{request['name']}"):
                        st.info(f"{request['name']} rejected")
        else:
            st.info("No pending join requests")

def show_financial_management(committee):
    st.subheader("Financial Management")
    
    # Financial overview
    monthly_amount = committee['monthly_amount']
    current_members = committee['current_members']
    duration = committee['duration']
    
    monthly_collection = monthly_amount * current_members
    total_expected = monthly_amount * committee['total_members'] * duration
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Monthly Collection", f"Rs. {monthly_collection:,}")
    with col2:
        st.metric("Total Expected", f"Rs. {total_expected:,}")
    with col3:
        payout_per_cycle = monthly_collection
        st.metric("Payout per Cycle", f"Rs. {payout_per_cycle:,}")
    
    # Payment tracking chart
    st.subheader("Payment Tracking")
    
    # Generate dummy payment data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    collections = [monthly_collection * random.uniform(0.8, 1.0) for _ in months]
    
    payment_df = pd.DataFrame({
        'Month': months,
        'Collection': collections,
        'Target': [monthly_collection] * len(months)
    })
    
    fig = px.bar(payment_df, x='Month', y=['Collection', 'Target'],
                title="Monthly Collection vs Target",
                barmode='group',
                color_discrete_map={'Collection': '#228B22', 'Target': '#FFD700'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Payout management
    st.subheader("Payout Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Next Payout Details**")
        next_payout_date = datetime.now() + timedelta(days=30)
        st.write(f"Date: {next_payout_date.strftime('%Y-%m-%d')}")
        st.write(f"Amount: Rs. {monthly_collection:,}")
        st.write(f"Recipient: Next in rotation")
    
    with col2:
        st.write("**Payout Options**")
        payout_method = st.selectbox("Payout Method", [
            "Bank Transfer",
            "Cash Delivery",
            "Halal Product Voucher",
            "Gold/Silver Purchase",
            "Investment in Halal Assets"
        ])
        
        if st.button("💰 Process Payout", use_container_width=True):
            st.success(f"Payout of Rs. {monthly_collection:,} via {payout_method} has been scheduled!")
            st.balloons()
    
    # Financial reports
    st.subheader("Financial Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generate Monthly Report"):
            st.download_button(
                "📥 Download Report",
                data="Committee Financial Report\nMonth: December 2024\nTotal Collection: Rs. 50,000\nMembers: 10/12",
                file_name="committee_report_dec2024.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("📈 Export Payment History"):
            st.download_button(
                "📥 Download History",
                data="Payment History CSV Data",
                file_name="payment_history.csv",
                mime="text/csv"
            )

def show_committee_management(committee):
    st.subheader("Committee Management")
    
    # Committee settings
    with st.form("committee_settings"):
        st.write("**Committee Information**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_title = st.text_input("Committee Title", value=committee['title'])
            new_description = st.text_area("Description", value=committee.get('description', ''))
            committee_status = st.selectbox("Status", 
                                          ["active", "paused", "completed", "cancelled"],
                                          index=0 if committee['status'] == 'active' else 1)
        
        with col2:
            # These should be read-only after creation for financial integrity
            st.text_input("Monthly Amount", value=f"Rs. {committee['monthly_amount']:,}", disabled=True)
            st.text_input("Total Members", value=str(committee['total_members']), disabled=True)
            st.text_input("Duration", value=f"{committee['duration']} months", disabled=True)
            st.text_input("Committee Type", value=committee['type'].title(), disabled=True)
        
        if st.form_submit_button("Update Committee Settings"):
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
    
    # Committee statistics
    st.subheader("Committee Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_active = (datetime.now() - datetime.strptime(committee['created_date'], '%Y-%m-%d')).days
        st.metric("Days Active", days_active)
    
    with col2:
        completion_percentage = (committee['current_members'] / committee['total_members']) * 100
        st.metric("Completion Rate", f"{completion_percentage:.1f}%")
    
    with col3:
        avg_trust_score = 87  # Calculated from members
        st.metric("Average Trust Score", f"{avg_trust_score}%")
    
    # Notifications and alerts
    st.subheader("Notifications & Alerts")
    
    notifications = [
        {"type": "info", "message": "2 members have pending payments for this month"},
        {"type": "success", "message": "Committee is 83% filled - only 2 more members needed"},
        {"type": "warning", "message": "Next payout is due in 5 days"},
    ]
    
    for notification in notifications:
        if notification["type"] == "info":
            st.info(notification["message"])
        elif notification["type"] == "success":
            st.success(notification["message"])
        elif notification["type"] == "warning":
            st.warning(notification["message"])
    
    # Advanced actions
    st.subheader("Advanced Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 Send Bulk Notification"):
            st.success("Notification sent to all members!")
    
    with col2:
        if st.button("🔄 Reset Payment Cycle"):
            st.warning("Payment cycle has been reset!")
    
    # Danger zone
    with st.expander("⚠️ Danger Zone"):
        st.warning("**Caution:** These actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete Committee", type="primary"):
                st.error("Committee deletion is disabled in demo mode")
        
        with col2:
            if st.button("🚫 Suspend Committee", type="primary"):
                st.warning("Committee has been suspended")

if __name__ == "__main__":
    show_admin_dashboard()
