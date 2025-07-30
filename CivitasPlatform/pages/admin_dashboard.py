import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database.db_manager import DatabaseManager
from utils.payment_manager import PaymentManager
from utils.trust_score import TrustScoreManager

def show_admin_dashboard(db: DatabaseManager, user_id: str):
    """Display admin dashboard with enhanced UI"""
    
    st.title("👑 Admin Dashboard")
    
    # Get admin committees
    admin_committees = [c for c in db.get_user_committees(user_id) if c.admin_id == user_id]
    
    if not admin_committees:
        st.info("🎯 You are not an admin of any committees yet. Create a committee to access admin features.")
        if st.button("🏛️ Create Committee", type="primary"):
            st.session_state.page = "committee_management"
            st.rerun()
        return
    
    # Committee selector
    committee_options = {c.title: c for c in admin_committees}
    selected_committee_title = st.selectbox(
        "📋 Select Committee to Manage",
        list(committee_options.keys()),
        key="admin_committee_selector"
    )
    
    selected_committee = committee_options[selected_committee_title]
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "👥 Members", 
        "💰 Finances", 
        "📅 Schedule",
        "⚙️ Management"
    ])
    
    with tab1:
        show_admin_overview(db, selected_committee)
    
    with tab2:
        show_member_management(db, selected_committee)
    
    with tab3:
        show_financial_management(db, selected_committee)
    
    with tab4:
        show_schedule_management(db, selected_committee)
    
    with tab5:
        show_committee_settings(db, selected_committee)

def show_admin_overview(db: DatabaseManager, committee):
    """Show admin overview with metrics and charts"""
    
    # Add committee type indicator
    committee_type_icon = "🔒" if committee.committee_type == 'private' else "🌐"
    committee_type_text = "Private" if committee.committee_type == 'private' else "Public"
    
    st.subheader(f"📊 Overview - {committee_type_icon} {committee.title} ({committee_type_text})")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    fill_rate = (committee.current_members / committee.total_members) * 100
    monthly_collection = committee.current_members * committee.monthly_amount
    total_pool = monthly_collection * committee.duration
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #228B22, #32CD32); color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
            <h3 style="margin: 0; color: white;">{committee.current_members}/{committee.total_members}</h3>
            <p style="margin: 0; opacity: 0.9;">Members</p>
            <small style="opacity: 0.7;">{fill_rate:.1f}% filled</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFD700, #FFA500); color: #333; padding: 1.5rem; border-radius: 15px; text-align: center;">
            <h3 style="margin: 0; color: #333;">Rs. {monthly_collection:,}</h3>
            <p style="margin: 0; opacity: 0.8;">Monthly Collection</p>
            <small style="opacity: 0.6;">Per cycle</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #20B2AA, #48D1CC); color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
            <h3 style="margin: 0; color: white;">Rs. {total_pool:,}</h3>
            <p style="margin: 0; opacity: 0.9;">Total Pool</p>
            <small style="opacity: 0.7;">Projected</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        status_color = "#228B22" if committee.status == 'active' else "#FFA500"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {status_color}, {status_color}CC); color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
            <h3 style="margin: 0; color: white;">{committee.status.title()}</h3>
            <p style="margin: 0; opacity: 0.9;">Status</p>
            <small style="opacity: 0.7;">{committee.payment_frequency}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        # Member growth chart
        st.subheader("📈 Member Growth Trend")
        
        # Generate growth data
        dates = [datetime.now() - timedelta(days=30-i) for i in range(31)]
        growth_data = []
        for i, date in enumerate(dates):
            members = min(i//3 + 1, committee.current_members)
            growth_data.append({'Date': date, 'Members': members})
        
        growth_df = pd.DataFrame(growth_data)
        
        fig = px.area(growth_df, x='Date', y='Members',
                     title=f"Member Growth - {committee.title}",
                     color_discrete_sequence=['#228B22'])
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Payment status pie chart
        st.subheader("💳 Payment Distribution")
        
        # Mock payment data
        paid_members = max(1, int(committee.current_members * 0.9))
        pending_members = committee.current_members - paid_members
        
        fig = go.Figure(data=[go.Pie(
            labels=['Paid', 'Pending'],
            values=[paid_members, pending_members],
            hole=.4,
            marker_colors=['#228B22', '#FFD700']
        )])
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            height=350,
            title="This Month's Payment Status",
            font_size=12,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity feed
    st.subheader("🔔 Recent Activity")
    
    try:
        # Get real activity data from database
        recent_activities = db.get_committee_activity(committee.id, limit=5)
        
        if recent_activities:
            for activity in recent_activities:
                activity_icon = {
                    'member_joined': '👤',
                    'payment_received': '💰',
                    'committee_created': '🏛️',
                    'payout_processed': '🎉'
                }.get(activity['activity_type'], '📋')
                
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #228B22; margin: 0.5rem 0;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">{activity_icon}</span>
                            <div>
                                <p style="margin: 0; font-weight: 600; color: #333;">{activity['description']}</p>
                                <small style="color: #666;">{activity['timestamp']}</small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📊 No recent activity to display. Activity will appear here as members join and make payments.")
            
    except Exception as e:
        st.warning("📊 Activity tracking will be displayed here once the committee becomes more active.")
        if st.session_state.user_data.get('role') == 'admin':
            st.error(f"Debug info: {str(e)}")

def show_member_management(db: DatabaseManager, committee):
    """Enhanced member management interface"""
    
    st.subheader("👥 Member Management")
    
    # Get committee members
    # This would normally query the database for actual member data
    # For now, we'll create mock data based on the committee
    
    members_data = []
    for i in range(committee.current_members):
        members_data.append({
            'Position': i + 1,
            'Name': f'Member {i + 1}',
            'Username': f'user{i + 1}',
            'Trust Score': f'{85 + (i % 10)}%',
            'Payment Status': 'Paid' if i < committee.current_members - 1 else 'Pending',
            'Join Date': (datetime.now() - timedelta(days=30-i)).strftime('%Y-%m-%d'),
            'Role': 'Admin' if i == 0 else 'Member'
        })
    
    if not members_data:
        st.info("No members found in this committee.")
        return
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        payment_filter = st.selectbox("💳 Payment Status", ["All", "Paid", "Pending"])
    with col2:
        role_filter = st.selectbox("👤 Role", ["All", "Admin", "Member"])
    with col3:
        min_trust = st.slider("📊 Min Trust Score", 0, 100, 0)
    
    # Apply filters
    filtered_members = members_data.copy()
    if payment_filter != "All":
        filtered_members = [m for m in filtered_members if m.get('Payment Status') == payment_filter]
    if role_filter != "All":
        filtered_members = [m for m in filtered_members if m.get('Role') == role_filter]
    
    # Convert to DataFrame for display
    try:
        if not filtered_members:
            st.info("No members match the current filters.")
            return
            
        df = pd.DataFrame(filtered_members)
        
        # Ensure required columns exist in the DataFrame
        if df.empty:
            st.info("No member data available to display.")
        elif 'Payment Status' not in df.columns or 'Role' not in df.columns:
            st.error("Unable to load member data properly. Please refresh the page.")
        else:
            # Style the dataframe
            def style_payment_status(val):
                if val == 'Paid':
                    return 'background-color: #90EE90; color: #006400'
                elif val == 'Pending':
                    return 'background-color: #FFE4B5; color: #FF8C00'
                return ''
            
            def style_role(val):
                if val == 'Admin':
                    return 'background-color: #E6E6FA; color: #4B0082; font-weight: bold'
                return ''
            
            styled_df = df.style.map(style_payment_status, subset=['Payment Status'])
            styled_df = styled_df.map(style_role, subset=['Role'])
            
            st.dataframe(styled_df, use_container_width=True, height=300)
            
    except Exception as e:
        st.error("Unable to load member data at this time. Please refresh the page.")
        st.info("This appears to be a temporary issue with the data display.")
        
        # Member actions
        st.subheader("🛠️ Member Actions")
        
        if len(filtered_members) > 0:
            selected_member = st.selectbox(
                "Select Member for Actions",
                [m['Username'] for m in filtered_members]
            )
            
            member_data = next(m for m in filtered_members if m['Username'] == selected_member)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("💌 Send Reminder", use_container_width=True):
                    st.success(f"✅ Payment reminder sent to {selected_member}")
            
            with col2:
                if st.button("📞 Contact Member", use_container_width=True):
                    st.info(f"📱 Contact details for {selected_member} would be displayed here")
            
            with col3:
                if st.button("⚠️ Issue Warning", use_container_width=True):
                    st.warning(f"⚠️ Warning issued to {selected_member}")
            
            with col4:
                if member_data['Role'] != 'Admin':
                    if st.button("🚫 Remove Member", use_container_width=True, type="secondary"):
                        if st.button("Confirm Removal", key="confirm_remove", type="primary"):
                            st.error(f"❌ Member {selected_member} has been removed")
    
    # Pending join requests for private committees
    if committee.committee_type == 'private':
        st.subheader("📬 Pending Join Requests")
        
        # Get actual pending requests from database
        pending_requests = db.get_pending_join_requests(committee.id)
        
        if pending_requests:
            for request in pending_requests:
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 10px; border: 1px solid #ddd; margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h5 style="margin: 0; color: #333;">{request['name']}</h5>
                                <p style="margin: 0; color: #666; font-size: 0.9rem;">
                                    Trust Score: {request['trust_score']}% | 
                                    Requested: {request['requested_date']}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col2:
                        if st.button("✅ Approve", key=f"approve_{request['name']}", use_container_width=True, type="primary"):
                            if db.approve_join_request(request['id'], committee.id):
                                st.success(f"✅ {request['name']} approved and added to committee!")
                                st.rerun()
                            else:
                                st.error("Failed to approve request")
                    with col3:
                        if st.button("❌ Reject", key=f"reject_{request['name']}", use_container_width=True):
                            if db.reject_join_request(request['id']):
                                st.info(f"❌ {request['name']} request rejected")
                                st.rerun()
                            else:
                                st.error("Failed to reject request")
        else:
            st.info("📭 No pending join requests at the moment.")

def show_financial_management(db: DatabaseManager, committee):
    """Enhanced financial management interface"""
    
    st.subheader("💰 Financial Management")
    
    # Financial metrics
    monthly_amount = committee.monthly_amount
    current_members = committee.current_members
    monthly_collection = monthly_amount * current_members
    total_expected = monthly_amount * committee.total_members * committee.duration
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Monthly Collection", f"Rs. {monthly_collection:,}")
    with col2:
        st.metric("🎯 Target Collection", f"Rs. {monthly_amount * committee.total_members:,}")
    with col3:
        st.metric("💰 Per Member Payout", f"Rs. {monthly_collection:,}")
    with col4:
        collection_rate = (current_members / committee.total_members) * 100
        st.metric("📊 Collection Rate", f"{collection_rate:.1f}%")
    
    # Financial charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Collection Trends")
        
        # Generate mock collection data
        months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
        collections = [monthly_collection * (0.8 + i * 0.05) for i in range(len(months))]
        targets = [monthly_amount * committee.total_members] * len(months)
        
        trend_df = pd.DataFrame({
            'Month': months,
            'Actual': collections,
            'Target': targets
        })
        
        fig = px.bar(trend_df, x='Month', y=['Actual', 'Target'],
                    title="Monthly Collection vs Target",
                    barmode='group',
                    color_discrete_map={'Actual': '#228B22', 'Target': '#FFD700'})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💳 Payment Methods Distribution")
        
        payment_methods = ['Bank Transfer', 'Mobile Payment', 'Cash', 'Cheque']
        method_counts = [45, 30, 15, 10]  # Mock data
        
        fig = px.pie(values=method_counts, names=payment_methods,
                    title="Payment Methods Used",
                    color_discrete_sequence=['#228B22', '#FFD700', '#20B2AA', '#9370DB'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Payout management
    st.subheader("🏆 Payout Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 Next Payout Details")
        
        next_payout_date = datetime.now() + timedelta(days=30)
        st.markdown(f"""
        <div style="background: linear-gradient(45deg, #228B22, #32CD32); color: white; padding: 1.5rem; border-radius: 10px;">
            <h4 style="margin: 0; color: white;">Upcoming Payout</h4>
            <p style="margin: 0.5rem 0;"><strong>Date:</strong> {next_payout_date.strftime('%B %d, %Y')}</p>
            <p style="margin: 0.5rem 0;"><strong>Amount:</strong> Rs. {monthly_collection:,}</p>
            <p style="margin: 0.5rem 0;"><strong>Recipient:</strong> Next in rotation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ⚙️ Payout Options")
        
        with st.form("payout_form"):
            payout_method = st.selectbox("Payout Method", [
                "🏦 Bank Transfer",
                "💵 Cash Delivery", 
                "🎫 Halal Product Voucher",
                "🥇 Gold/Silver Purchase",
                "📈 Halal Investment Fund"
            ])
            
            payout_notes = st.text_area("Payout Notes", placeholder="Any special instructions...")
            
            col1, col2 = st.columns(2)
            with col1:
                schedule_btn = st.form_submit_button("📅 Schedule Payout", use_container_width=True, type="secondary")
            with col2:
                process_btn = st.form_submit_button("💰 Process Now", use_container_width=True, type="primary")
            
            if schedule_btn:
                st.success(f"✅ Payout of Rs. {monthly_collection:,} via {payout_method} has been scheduled!")
            
            if process_btn:
                st.success(f"🎉 Payout of Rs. {monthly_collection:,} via {payout_method} has been processed!")
                st.balloons()

def show_schedule_management(db: DatabaseManager, committee):
    """Enhanced schedule management interface"""
    
    st.subheader("📅 Schedule Management")
    
    # Payout schedule
    st.markdown("### 🏆 Payout Schedule")
    
    # Generate payout schedule
    schedule_data = []
    for i in range(committee.current_members):
        payout_date = datetime.now() + timedelta(days=30 * i)
        schedule_data.append({
            'Position': i + 1,
            'Member': f'Member {i + 1}',
            'Payout Date': payout_date.strftime('%Y-%m-%d'),
            'Amount': f"Rs. {committee.monthly_amount * committee.current_members:,}",
            'Status': 'Completed' if i < 2 else 'Scheduled'
        })
    
    schedule_df = pd.DataFrame(schedule_data)
    
    # Style the schedule
    def style_status(val):
        if val == 'Completed':
            return 'background-color: #90EE90; color: #006400'
        elif val == 'Scheduled':
            return 'background-color: #E6E6FA; color: #4B0082'
        return ''
    
    styled_schedule = schedule_df.style.map(style_status, subset=['Status'])
    st.dataframe(styled_schedule, use_container_width=True)
    
    # Payment schedule
    st.markdown("### 💳 Payment Schedule")
    
    frequency_info = {
        'monthly': {'interval': 30, 'label': 'Monthly'},
        'bi_monthly': {'interval': 60, 'label': 'Bi-Monthly'}
    }
    
    freq_data = frequency_info.get(committee.payment_frequency, frequency_info['monthly'])
    
    st.info(f"📊 Payment Frequency: {freq_data['label']} (every {freq_data['interval']} days)")
    
    # Next payments due
    payment_schedule = []
    for i in range(committee.current_members):
        due_date = datetime.now() + timedelta(days=freq_data['interval'])
        payment_schedule.append({
            'Member': f'Member {i + 1}',
            'Due Date': due_date.strftime('%Y-%m-%d'),
            'Amount': f"Rs. {committee.monthly_amount:,}",
            'Status': 'Due' if i < 3 else 'Paid'
        })
    
    payment_df = pd.DataFrame(payment_schedule)
    
    def style_payment_status(val):
        if val == 'Paid':
            return 'background-color: #90EE90; color: #006400'
        elif val == 'Due':
            return 'background-color: #FFE4B5; color: #FF8C00'
        return ''
    
    styled_payments = payment_df.style.map(style_payment_status, subset=['Status'])
    st.dataframe(styled_payments, use_container_width=True)

def show_committee_settings(db: DatabaseManager, committee):
    """Enhanced committee settings interface"""
    
    st.subheader("⚙️ Committee Settings")
    
    # Committee information form
    with st.form("committee_settings_form"):
        st.markdown("### 📋 Committee Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_title = st.text_input("Committee Title", value=committee.title)
            new_description = st.text_area("Description", value=committee.description or '')
            committee_status = st.selectbox("Status", 
                                          ["active", "paused", "completed", "cancelled"],
                                          index=0 if committee.status == 'active' else 1)
        
        with col2:
            payment_frequency = st.selectbox("Payment Frequency",
                                           ["monthly", "bi_monthly"],
                                           index=0 if committee.payment_frequency == 'monthly' else 1)
            category = st.selectbox("Category", 
                                  ["General", "Business", "Family", "Friends", "Investment"],
                                  index=0)
            visibility = st.selectbox("Visibility",
                                    ["public", "private"],
                                    index=0 if committee.committee_type == 'public' else 1)
        
        # Submit button
        if st.form_submit_button("💾 Update Settings", use_container_width=True, type="primary"):
            # Validate inputs
            if not new_title.strip():
                st.error("Committee title cannot be empty")
            else:
                # Update committee in database
                try:
                    success = db.update_committee_settings(
                        committee_id=committee.id,
                        title=new_title.strip(),
                        description=new_description.strip() if new_description else None,
                        status=committee_status,
                        payment_frequency=payment_frequency,
                        category=category,
                        committee_type=visibility
                    )
                    
                    if success:
                        st.success("✅ Committee settings updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update committee settings. Please try again.")
                except Exception as e:
                    st.error("Unable to update settings at this time. Please contact support.")
    
    st.markdown("---")
    
    # Advanced settings
    st.markdown("### 🔧 Advanced Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Analytics")
        if st.button("📈 Generate Report", use_container_width=True):
            st.download_button(
                "📥 Download Committee Report",
                data=f"Committee: {committee.title}\nMembers: {committee.current_members}/{committee.total_members}\nMonthly Collection: Rs. {committee.monthly_amount * committee.current_members:,}",
                file_name=f"committee_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        if st.button("📊 Export Member Data", use_container_width=True):
            st.info("Member data export would be available here")
    
    with col2:
        st.markdown("#### 🔔 Notifications")
        auto_reminders = st.checkbox("Automatic Payment Reminders", value=True)
        payout_notifications = st.checkbox("Payout Notifications", value=True)
        member_notifications = st.checkbox("New Member Notifications", value=True)
        
        if st.button("💾 Save Notification Settings", use_container_width=True):
            st.success("✅ Notification preferences saved!")
    
    # Danger zone
    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")
    
    with st.expander("🚨 Committee Deletion", expanded=False):
        st.warning("⚠️ **Warning**: This action cannot be undone. All committee data, member information, and payment history will be permanently deleted.")
        
        deletion_reason = st.selectbox("Reason for Deletion", [
            "Committee completed successfully",
            "Insufficient member participation", 
            "Administrative decision",
            "Other"
        ])
        
        if deletion_reason == "Other":
            custom_reason = st.text_input("Please specify:")
        
        confirm_text = st.text_input("Type 'DELETE' to confirm deletion:")
        
        if confirm_text == "DELETE":
            if st.button("🗑️ Delete Committee", type="primary", use_container_width=True):
                try:
                    success = db.delete_committee(committee.id)
                    if success:
                        st.success("✅ Committee deleted successfully!")
                        st.info("Redirecting to main dashboard...")
                        # Clear the current committee from session and redirect
                        if 'current_committee' in st.session_state:
                            del st.session_state.current_committee
                        st.session_state.current_page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("Failed to delete committee. Please try again or contact support.")
                except Exception as e:
                    st.error("Unable to delete committee at this time. Please contact support.")
