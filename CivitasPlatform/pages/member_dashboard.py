import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database.db_manager import DatabaseManager
from utils.payment_manager import PaymentManager
from utils.trust_score import TrustScoreManager

def show_member_dashboard(db: DatabaseManager, user_id: str):
    """Display member dashboard with enhanced UI"""

    st.title("👤 Member Dashboard")

    # Get user committees
    member_committees = db.get_user_committees(user_id)

    if not member_committees:
        st.info("🎯 You haven't joined any committees yet. Visit Committee Management to join one!")
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🔍 Browse Committees", use_container_width=True, type="primary"):
                st.session_state.current_page = "browse_committees"
                st.rerun()
        return

    # Committee selector if member has multiple committees
    if len(member_committees) > 1:
        committee_options = {c.title: c for c in member_committees}
        selected_committee_title = st.selectbox(
            "📋 Select Committee",
            list(committee_options.keys()),
            key="member_committee_selector"
        )
        selected_committee = committee_options[selected_committee_title]
    else:
        selected_committee = member_committees[0]

    # Dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "💰 Payments", 
        "📅 Schedule", 
        "🏆 Trust Score"
    ])

    with tab1:
        show_member_overview(db, selected_committee, user_id)

    with tab2:
        show_payment_history(db, selected_committee, user_id)

    with tab3:
        show_payout_schedule(db, selected_committee, user_id)

    with tab4:
        show_trust_score_details(db, user_id)

def show_member_overview(db: DatabaseManager, committee, user_id: str):
    """Show member overview with position and metrics"""

    st.subheader(f"📊 Overview - {committee.title}")

    # Get member position in payout queue
    member_position = db.get_member_position_in_committee(committee.id, user_id)

    # Key metrics for member
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #228B22, #32CD32); color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
            <h3 style="margin: 0; color: white;">{member_position}</h3>
            <p style="margin: 0; opacity: 0.9;">Your Position</p>
            <small style="opacity: 0.7;">in payout queue</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Mock payment status - in real app would check actual payment records
        payment_status = "Paid"
        status_color = "#228B22" if payment_status == "Paid" else "#DC143C"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {status_color}, {status_color}CC); color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
            <h3 style="margin: 0; color: white;">✓</h3>
            <p style="margin: 0; opacity: 0.9;">{payment_status}</p>
            <small style="opacity: 0.7;">This Month</small>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        user_data = db.get_user_by_id(user_id)
        trust_score = user_data.get('trust_score', 85) if user_data else 85
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFD700, #FFA500); color: #333; padding: 1.5rem; border-radius: 15px; text-align: center;">
            <h3 style="margin: 0; color: #333;">{trust_score}%</h3>
            <p style="margin: 0; opacity: 0.8;">Trust Score</p>
            <small style="opacity: 0.6;">Excellent</small>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # Calculate next payout date based on position and payment frequency
        if committee.payment_frequency == 'bi_monthly':
            days_multiplier = 60
        else:
            days_multiplier = 30

        days_to_payout = (member_position - 1) * days_multiplier
        next_payout = datetime.now() + timedelta(days=days_to_payout)

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #20B2AA, #48D1CC); color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
            <h3 style="margin: 0; color: white;">{next_payout.strftime('%b %d')}</h3>
            <p style="margin: 0; opacity: 0.9;">Next Payout</p>
            <small style="opacity: 0.7;">in {days_to_payout} days</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Committee progress
    st.subheader("🏛️ Committee Progress")

    progress_percentage = (committee.current_members / committee.total_members) * 100
    st.progress(progress_percentage / 100)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Members:** {committee.current_members} of {committee.total_members} joined")
    with col2:
        st.write(f"**Completion:** {progress_percentage:.1f}% ({committee.total_members - committee.current_members} slots left)")

    # Financial overview charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Your Financial Commitment")

        monthly_contribution = committee.monthly_amount
        total_contribution = monthly_contribution * committee.duration

        commitment_data = {
            'Type': ['Monthly Payment', 'Total Commitment'],
            'Amount': [monthly_contribution, total_contribution]
        }

        fig = px.bar(commitment_data, x='Type', y='Amount',
                    title="Your Financial Overview",
                    color='Type',
                    color_discrete_map={'Monthly Payment': '#228B22', 'Total Commitment': '#FFD700'})
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🏆 Payout Queue Visualization")

        # Create payout queue visualization
        queue_data = []
        for pos in range(1, committee.current_members + 1):
            is_current_user = pos == member_position
            queue_data.append({
                'Position': pos,
                'Amount': committee.monthly_amount * committee.current_members,
                'Type': 'You' if is_current_user else 'Other'
            })

        queue_df = pd.DataFrame(queue_data)

        fig = px.bar(queue_df, x='Position', y='Amount', color='Type',
                    title="Payout Queue (Your Position Highlighted)",
                    color_discrete_map={'You': '#228B22', 'Other': '#90EE90'})
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Recent activity
    st.subheader("🔔 Recent Activity")

    # Check for real committee activities from database
    try:
        activities = db.get_committee_activities(committee.id, user_id) if hasattr(db, 'get_committee_activities') else []
    except AttributeError:
        activities = []

    if activities:
        for activity in activities:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid #228B22; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span style="font-size: 1.5rem;">{activity.get('icon', '📊')}</span>
                        <div>
                            <h5 style="margin: 0; color: #333;">{activity.get('activity', 'Committee activity')}</h5>
                            <p style="margin: 0; color: #666; font-size: 0.9rem;">{activity.get('details', 'Activity details')}</p>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.2rem;">{activity.get('status', '📊')}</span>
                        <p style="margin: 0; color: #999; font-size: 0.8rem;">{activity.get('date', 'Recent')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activities to display. Activities will appear here as you and other members participate in the committee.")

def show_payment_history(db: DatabaseManager, committee, user_id: str):
    """Show payment history and management"""

    st.subheader("💰 Payment History")

    # Payment summary metrics
    col1, col2, col3 = st.columns(3)

    monthly_amount = committee.monthly_amount
    # Calculate months active based on creation date
    months_active = max(1, (datetime.now() - committee.created_date).days // 30)
    total_paid = monthly_amount * min(months_active, committee.duration)

    with col1:
        st.metric("💵 Monthly Amount", f"Rs. {monthly_amount:,}")
    with col2:
        st.metric("💰 Total Paid", f"Rs. {total_paid:,}")
    with col3:
        payment_rate = 95  # Mock high payment rate
        st.metric("📊 Payment Rate", f"{payment_rate}%")

    # Payment frequency info
    freq_label = "Bi-Monthly" if committee.payment_frequency == 'bi_monthly' else "Monthly"
    freq_days = 60 if committee.payment_frequency == 'bi_monthly' else 30

    st.info(f"📅 Payment Frequency: {freq_label} (every {freq_days} days)")

    # Payment history table
    st.subheader("📋 Payment Records")

    # Generate payment history based on committee data
    payment_history = []
    for i in range(min(months_active, 6)):  # Show last 6 payments
        payment_date = datetime.now() - timedelta(days=freq_days * i)
        payment_history.append({
            'Date': payment_date.strftime('%Y-%m-%d'),
            'Amount': f"Rs. {monthly_amount:,}",
            'Status': 'Paid' if i > 0 else 'Pending',
            'Method': 'Bank Transfer',
            'Reference': f"TXN{payment_date.strftime('%Y%m%d')}{i:03d}"
        })

    if payment_history:
        payment_df = pd.DataFrame(payment_history)

        # Style the payment status
        def style_payment_status(row):
            if row['Status'] == 'Paid':
                return ['background-color: #90EE90'] * len(row)
            elif row['Status'] == 'Pending':
                return ['background-color: #FFE4B5'] * len(row)
            else:
                return [''] * len(row)

        styled_df = payment_df.style.apply(style_payment_status, axis=1)
        st.dataframe(styled_df, use_container_width=True)

    # Payment trends chart
    st.subheader("📈 Payment Consistency")

    if payment_history:
        # Create consistency chart
        dates = [datetime.now() - timedelta(days=freq_days * i) for i in range(len(payment_history))][::-1]
        amounts = [monthly_amount] * len(dates)

        trend_df = pd.DataFrame({
            'Date': dates,
            'Amount': amounts,
            'Status': ['Paid'] * len(dates)
        })

        fig = px.line(trend_df, x='Date', y='Amount',
                     title=f"{freq_label} Payment Consistency",
                     markers=True,
                     color_discrete_sequence=['#228B22'])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Next payment reminder
    st.subheader("⏰ Upcoming Payments")

    next_payment_date = datetime.now() + timedelta(days=freq_days)
    days_until_payment = freq_days - (datetime.now().day % freq_days)

    if days_until_payment <= 7:
        st.warning(f"⏰ **Payment Due Soon!** Next payment due in {days_until_payment} days")
        st.write(f"**Amount:** Rs. {monthly_amount:,}")
        st.write(f"**Due Date:** {next_payment_date.strftime('%B %d, %Y')}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💳 Pay Now", use_container_width=True, type="primary"):
                st.success("✅ Payment gateway integration would open here")
        with col2:
            if st.button("📅 Set Reminder", use_container_width=True):
                st.info("📱 Reminder set for 2 days before due date")
        with col3:
            if st.button("📞 Contact Admin", use_container_width=True):
                st.info("📧 Admin contact information would be displayed")
    else:
        st.info(f"📅 Next payment due in {days_until_payment} days (Rs. {monthly_amount:,})")

def show_payout_schedule(db: DatabaseManager, committee, user_id: str):
    """Show payout schedule and preferences"""

    st.subheader("📅 Payout Schedule")

    # Member's payout information
    member_position = db.get_member_position_in_committee(committee.id, user_id)
    monthly_pool = committee.monthly_amount * committee.current_members

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📍 Your Position", f"{member_position} of {committee.current_members}")
    with col2:
        st.metric("💰 Your Payout Amount", f"Rs. {monthly_pool:,}")
    with col3:
        # Calculate payout date based on position and frequency
        freq_days = 60 if committee.payment_frequency == 'bi_monthly' else 30
        months_to_wait = member_position - 1
        payout_date = datetime.now() + timedelta(days=freq_days * months_to_wait)
        st.metric("📅 Expected Date", payout_date.strftime("%b %Y"))

    # Payout calendar
    st.subheader("🗓️ Committee Payout Calendar")

    # Create payout schedule for all members
    payout_schedule = []
    for position in range(1, committee.current_members + 1):
        payout_month = datetime.now() + timedelta(days=freq_days * (position - 1))
        is_current_user = position == member_position

        payout_schedule.append({
            'Position': position,
            'Month': payout_month.strftime('%b %Y'),
            'Member': 'You' if is_current_user else f'Member {position}',
            'Amount': f"Rs. {monthly_pool:,}",
            'Status': '⭐ Your Turn' if is_current_user else '👤 Other Member'
        })

    schedule_df = pd.DataFrame(payout_schedule)

    # Highlight current user's row
    def highlight_user_row(row):
        if 'You' in row['Member']:
            return ['background-color: #90EE90; font-weight: bold'] * len(row)
        return [''] * len(row)

    styled_schedule = schedule_df.style.apply(highlight_user_row, axis=1)
    st.dataframe(styled_schedule, use_container_width=True, height=300)

    # Payout preferences
    st.subheader("⚙️ Payout Preferences")

    col1, col2 = st.columns(2)

    with col1:
        with st.form("payout_preferences"):
            st.markdown("**Set Your Payout Preferences**")

            payout_method = st.selectbox("Preferred Payout Method", [
                "🏦 Bank Transfer",
                "💵 Cash Pickup",
                "🎫 Halal Product Vouchers", 
                "🥇 Gold/Silver Purchase",
                "📈 Halal Investment Fund"
            ])

            bank_details = st.text_input("Bank Account Details", 
                                       placeholder="Account number (if applicable)")

            contact_preference = st.selectbox("Contact Method", [
                "📱 WhatsApp",
                "📞 Phone Call", 
                "📧 Email",
                "💬 SMS"
            ])

            special_instructions = st.text_area("Special Instructions",
                                              placeholder="Any specific requirements for your payout...")

            if st.form_submit_button("💾 Save Preferences", use_container_width=True, type="primary"):
                st.success("✅ Payout preferences saved successfully!")

    with col2:
        st.markdown("**Payout Method Benefits**")

        benefits = {
            "🏦 Bank Transfer": "Instant, secure, no fees",
            "💵 Cash Pickup": "Immediate access, convenient locations",
            "🎫 Halal Product Vouchers": "10% bonus value, wide acceptance",
            "🥇 Gold/Silver Purchase": "Inflation protection, Shariah compliant",
            "📈 Halal Investment Fund": "5% additional returns, auto-reinvest"
        }

        for method, benefit in benefits.items():
            st.markdown(f"**{method}**")
            st.write(f"• {benefit}")
            st.write("")

    # Payout simulation
    st.subheader("🧮 Payout Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Standard Cash Payout**")
        gross_amount = monthly_pool
        tax_deduction = int(gross_amount * 0.01)  # 1% tax
        net_amount = gross_amount - tax_deduction

        st.write(f"Gross Amount: Rs. {gross_amount:,}")
        st.write(f"Tax Deduction (1%): Rs. {tax_deduction:,}")
        st.write(f"**Net Amount: Rs. {net_amount:,}**")

        if st.button("📊 Simulate Cash Payout", use_container_width=True):
            st.success(f"💰 You would receive Rs. {net_amount:,} via cash payout")

    with col2:
        st.markdown("**Halal Product Rewards**")

        product_options = [
            {"name": "Electronics Bundle", "value": gross_amount * 1.1, "bonus": "10%"},
            {"name": "Grocery Package", "value": gross_amount * 1.15, "bonus": "15%"},
            {"name": "Gold Investment", "value": gross_amount * 1.05, "bonus": "5%"},
            {"name": "Education Voucher", "value": gross_amount * 1.2, "bonus": "20%"}
        ]

        selected_product = st.selectbox("Choose Reward Option",
                                      [f"{p['name']} (+{p['bonus']} bonus)" for p in product_options])

        if st.button("🎁 Simulate Product Reward", use_container_width=True):
            selected = product_options[0]  # Simplified selection
            st.success(f"🎉 You would receive {selected['name']} worth Rs. {selected['value']:,.0f}")

def show_trust_score_details(db: DatabaseManager, user_id: str):
    """Show detailed trust score breakdown and improvement tips"""

    st.subheader("🏆 Trust Score Details")

    user_data = db.get_user_by_id(user_id)
    trust_score = user_data.get('trust_score', 85) if user_data else 85

    # Trust score overview
    col1, col2 = st.columns([1, 2])

    with col1:
        # Trust score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=trust_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Trust Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': get_trust_color(trust_score)},
                'steps': [
                    {'range': [0, 60], 'color': "#FFB6C1"},   # Poor - Light Red
                    {'range': [60, 75], 'color': "#FFFF99"},  # Fair - Yellow  
                    {'range': [75, 85], 'color': "#98FB98"},  # Good - Light Green
                    {'range': [85, 95], 'color': "#90EE90"},  # Very Good - Green
                    {'range': [95, 100], 'color': "#228B22"} # Excellent - Dark Green
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Trust score breakdown
        st.markdown("**Trust Score Breakdown**")

        # Mock breakdown data - in real app would come from TrustScoreManager
        components = {
            'Payment Consistency': {'score': 92, 'weight': 40, 'color': '#228B22'},
            'Payment Timeliness': {'score': 88, 'weight': 30, 'color': '#32CD32'},
            'Committee Completion': {'score': 85, 'weight': 20, 'color': '#FFD700'},
            'Community Reputation': {'score': 80, 'weight': 10, 'color': '#20B2AA'}
        }

        for component, data in components.items():
            progress_val = data['score'] / 100
            st.write(f"**{component}** ({data['weight']}% weight)")
            st.progress(progress_val)
            st.write(f"Score: {data['score']}/100")
            st.write("")

    # Trust level benefits
    st.subheader("🎁 Trust Level Benefits")

    trust_level = get_trust_level(trust_score)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**Current Level: {trust_level}**")

        benefits = get_trust_benefits(trust_score)
        for benefit in benefits:
            st.write(f"✅ {benefit}")

    with col2:
        st.markdown("**Next Level Requirements**")

        next_thresholds = {
            85: "Excellent (95+)",
            75: "Very Good (85+)", 
            60: "Good (75+)",
            0: "Fair (60+)"
        }

        for threshold, level in next_thresholds.items():
            if trust_score < threshold + 10:
                points_needed = (threshold + 10) - trust_score
                st.write(f"🎯 {points_needed} points to reach {level}")
                break

    with col3:
        st.markdown("**Improvement Tips**")

        tips = [
            "💰 Make payments on time",
            "🏆 Complete committee cycles", 
            "🤝 Get positive community feedback",
            "📅 Maintain payment consistency",
            "🌟 Participate actively in committees"
        ]

        for tip in tips:
            st.write(tip)

    # Trust score history
    st.subheader("📈 Trust Score History")

    # Get real trust score history from database
    try:
        history_data = db.get_user_trust_score_history(user_id) if hasattr(db, 'get_user_trust_score_history') else []
    except AttributeError:
        history_data = []

    if history_data:
        history_df = pd.DataFrame(history_data)

        fig = px.line(history_df, x='Date', y='Trust Score',
                     title="Trust Score Trend",
                     markers=True,
                     color_discrete_sequence=['#228B22'])
        fig.update_layout(height=300)
        fig.update_yaxes(range=[70, 100])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trust score history will appear here as you participate in committees and build your reputation.")

    # Recent trust score activities
    st.subheader("🔔 Recent Trust Score Activities")

    # Check if the database method exists for trust score activities
    try:
        activities = db.get_user_trust_score_activities(user_id) if hasattr(db, 'get_user_trust_score_activities') else []
    except AttributeError:
        activities = []

    if activities:
        for activity in activities:
            change_color = "#228B22" if activity.get('change', 0) > 0 else "#DC143C"
            change_text = f"+{activity.get('change', 0)}" if activity.get('change', 0) > 0 else str(activity.get('change', 0))

            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid {change_color}; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span style="font-size: 1.5rem;">{activity.get('icon', '📊')}</span>
                        <div>
                            <h5 style="margin: 0; color: #333;">{activity.get('reason', 'Trust score update')}</h5>
                            <p style="margin: 0; color: #666; font-size: 0.9rem;">{activity.get('date', 'Recent')}</p>
                        </div>
                    </div>
                    <span style="color: {change_color}; font-weight: bold; font-size: 1.2rem;">{change_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent trust score activities to display. Activities will appear here as you participate in committees and make payments.")

def get_trust_color(score: int) -> str:
    """Get color based on trust score"""
    if score >= 95:
        return "#228B22"  # Excellent - Dark Green
    elif score >= 85:
        return "#32CD32"  # Very Good - Green
    elif score >= 75:
        return "#FFD700"  # Good - Gold
    elif score >= 60:
        return "#FFA500"  # Fair - Orange
    else:
        return "#DC143C"  # Poor - Red

def get_trust_level(score: int) -> str:
    """Get trust level name"""
    if score >= 95:
        return "Excellent"
    elif score >= 85:
        return "Very Good"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Fair"
    else:
        return "Poor"

def get_trust_benefits(score: int) -> List[str]:
    """Get benefits for trust level"""
    if score >= 95:
        return [
            "Create private committees",
            "Priority payout processing",
            "50% reduced fees",
            "Exclusive investment opportunities",
            "Higher committee limits (Rs. 100k+)"
        ]
    elif score >= 85:
        return [
            "Create private committees",
            "Priority support",
            "30% reduced fees", 
            "Special promotions",
            "Committee limits up to Rs. 75k"
        ]
    elif score >= 75:
        return [
            "Standard committee access",
            "Regular support",
            "Committee limits up to Rs. 50k"
        ]
    else:
        return [
            "Basic committee access",
            "Limited committee amounts",
            "Standard processing times"
        ]
    
def show_member_dashboard(db: DatabaseManager, user_id: str):
    """Display member dashboard with enhanced UI"""

    st.title("👤 Member Dashboard")

    # Get user committees
    member_committees = db.get_user_committees(user_id)

    if not member_committees:
        st.info("🎯 You haven't joined any committees yet. Visit Committee Management to join one!")
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🔍 Browse Committees", use_container_width=True, type="primary"):
                st.session_state.current_page = "browse_committees"
                st.rerun()
        return

    # Committee selector if member has multiple committees
    if len(member_committees) > 1:
        committee_options = {c.title: c for c in member_committees}
        selected_committee_title = st.selectbox(
            "📋 Select Committee",
            list(committee_options.keys()),
            key="member_committee_selector"
        )
        selected_committee = committee_options[selected_committee_title]
    else:
        selected_committee = member_committees[0]

    # Add committee type indicator
    committee_type_icon = "🔒" if selected_committee.committee_type == 'private' else "🌐"
    committee_type_text = "Private" if selected_committee.committee_type == 'private' else "Public"

    st.title(f"👤 Member Dashboard - {committee_type_icon} {selected_committee.title} ({committee_type_text})")

    # Dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "💰 Payments", 
        "📅 Schedule", 
        "🏆 Trust Score"
    ])

    with tab1:
        show_member_overview(db, selected_committee, user_id)

    with tab2:
        show_payment_history(db, selected_committee, user_id)

    with tab3:
        show_payout_schedule(db, selected_committee, user_id)

    with tab4:
        show_trust_score_details(db, user_id)