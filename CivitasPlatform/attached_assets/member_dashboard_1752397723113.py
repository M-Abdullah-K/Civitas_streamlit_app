import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def show_member_dashboard():
    st.title("👤 Member Dashboard")
    
    if not st.session_state.get('authenticated', False):
        st.error("Please login to access this page")
        return
    
    member_committees = get_member_committees()
    
    if not member_committees:
        st.info("You haven't joined any committees yet. Visit Committee Management to join one!")
        return
    
    # Committee selector if member has multiple committees
    if len(member_committees) > 1:
        selected_committee_title = st.selectbox(
            "Select Committee",
            [c['title'] for c in member_committees]
        )
        selected_committee = next(c for c in member_committees if c['title'] == selected_committee_title)
    else:
        selected_committee = member_committees[0]
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Payments", "📅 Schedule", "🏆 Trust Score"])
    
    with tab1:
        show_member_overview(selected_committee)
    
    with tab2:
        show_payment_history(selected_committee)
    
    with tab3:
        show_payout_schedule(selected_committee)
    
    with tab4:
        show_trust_score_details()

def get_member_committees():
    committees = st.session_state.get('committees', [])
    return [c for c in committees if st.session_state.current_user in c['members']]

def show_member_overview(committee):
    st.subheader(f"Overview - {committee['title']}")
    
    # Key metrics for member
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate member's position in payout queue
    member_position = committee['members'].index(st.session_state.current_user) + 1
    
    with col1:
        st.metric(
            "Current Cycle",
            f"{member_position}/{committee['current_members']}",
            "Your Position"
        )
    
    with col2:
        payment_status = "Paid" if random.random() > 0.2 else "Unpaid"
        status_color = "🟢" if payment_status == "Paid" else "🔴"
        st.metric(
            "Payment Status",
            f"{status_color} {payment_status}",
            "This Month"
        )
    
    with col3:
        trust_score = st.session_state.user_data.get('trust_score', random.randint(80, 95))
        st.metric(
            "Trust Score",
            f"{trust_score}%",
            "+2 this month" if trust_score > 90 else "Stable"
        )
    
    with col4:
        # Calculate next payout date based on position
        days_to_payout = (member_position - 1) * 30
        next_payout = datetime.now() + timedelta(days=days_to_payout)
        st.metric(
            "Next Payout",
            next_payout.strftime("%b %d"),
            f"In {days_to_payout} days"
        )
    
    # Committee progress
    st.subheader("Committee Progress")
    
    progress_percentage = (committee['current_members'] / committee['total_members']) * 100
    st.progress(progress_percentage / 100)
    st.write(f"**{committee['current_members']} of {committee['total_members']} members joined** ({progress_percentage:.1f}% complete)")
    
    # Financial overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Contribution")
        
        monthly_contribution = committee['monthly_amount']
        total_contribution = monthly_contribution * committee['duration']
        
        contribution_data = {
            'Type': ['Monthly', 'Total Expected'],
            'Amount': [monthly_contribution, total_contribution]
        }
        
        fig = px.bar(contribution_data, x='Type', y='Amount',
                    title="Your Financial Commitment",
                    color='Type',
                    color_discrete_map={'Monthly': '#228B22', 'Total Expected': '#FFD700'})
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Payout Distribution")
        
        # Create payout schedule visualization
        members = committee['members']
        payout_order = list(range(1, len(members) + 1))
        member_names = [f"Member {i}" for i in payout_order]
        
        # Highlight current user
        colors = ['#228B22' if members[i] == st.session_state.current_user else '#90EE90' 
                 for i in range(len(members))]
        
        fig = go.Figure(data=[go.Bar(
            x=payout_order,
            y=[committee['monthly_amount'] * committee['current_members']] * len(members),
            marker_color=colors,
            text=[f"You" if members[i] == st.session_state.current_user else f"M{i+1}" 
                  for i in range(len(members))],
            textposition="inside"
        )])
        
        fig.update_layout(
            title="Payout Schedule (Your turn highlighted)",
            xaxis_title="Payout Order",
            yaxis_title="Amount (PKR)",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    activity_data = [
        {"Date": "2024-12-20", "Activity": "Payment Submitted", "Amount": f"Rs. {committee['monthly_amount']:,}", "Status": "✅"},
        {"Date": "2024-12-19", "Activity": "New Member Joined", "Amount": "-", "Status": "ℹ️"},
        {"Date": "2024-12-15", "Activity": "Payout Processed", "Amount": f"Rs. {committee['monthly_amount'] * committee['current_members']:,}", "Status": "💰"},
        {"Date": "2024-12-10", "Activity": "Trust Score Updated", "Amount": "+2 points", "Status": "📈"},
    ]
    
    for activity in activity_data:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        with col1:
            st.write(activity["Date"])
        with col2:
            st.write(activity["Activity"])
        with col3:
            st.write(activity["Amount"])
        with col4:
            st.write(activity["Status"])

def show_payment_history(committee):
    st.subheader("Payment History")
    
    # Payment summary
    col1, col2, col3 = st.columns(3)
    
    monthly_amount = committee['monthly_amount']
    months_active = max(1, (datetime.now() - datetime.strptime(committee['created_date'], '%Y-%m-%d')).days // 30)
    total_paid = monthly_amount * months_active
    
    with col1:
        st.metric("Monthly Amount", f"Rs. {monthly_amount:,}")
    with col2:
        st.metric("Total Paid", f"Rs. {total_paid:,}")
    with col3:
        payment_rate = 95  # Dummy high payment rate
        st.metric("Payment Rate", f"{payment_rate}%")
    
    # Payment history table
    st.subheader("Payment Records")
    
    # Generate dummy payment history
    payment_history = []
    for i in range(months_active):
        payment_date = datetime.now() - timedelta(days=30*i)
        payment_history.append({
            'Date': payment_date.strftime('%Y-%m-%d'),
            'Amount': f"Rs. {monthly_amount:,}",
            'Status': 'Paid' if i < months_active - 1 else 'Pending',
            'Method': random.choice(['Bank Transfer', 'Cash', 'Mobile Payment']),
            'Transaction ID': f"TXN{random.randint(100000, 999999)}"
        })
    
    payment_df = pd.DataFrame(payment_history)
    
    # Color code the status
    def color_status(val):
        if val == 'Paid':
            return 'color: green'
        elif val == 'Pending':
            return 'color: orange'
        else:
            return 'color: red'
    
    styled_df = payment_df.style.map(color_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Payment trends
    st.subheader("Payment Trends")
    
    # Create payment trend chart
    dates = [datetime.now() - timedelta(days=30*i) for i in range(6)][::-1]
    amounts = [monthly_amount] * 6
    
    trend_df = pd.DataFrame({
        'Date': dates,
        'Amount': amounts
    })
    
    fig = px.line(trend_df, x='Date', y='Amount',
                 title="Monthly Payment Consistency",
                 markers=True)
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Payment reminders
    st.subheader("Payment Reminders")
    
    next_payment_date = datetime.now() + timedelta(days=30 - datetime.now().day)
    days_until_payment = (next_payment_date - datetime.now()).days
    
    if days_until_payment <= 7:
        st.warning(f"⏰ Payment due in {days_until_payment} days! Amount: Rs. {monthly_amount:,}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💳 Pay Now", use_container_width=True):
                st.success("Payment gateway would open here")
        with col2:
            if st.button("📅 Set Reminder", use_container_width=True):
                st.info("Reminder set for 2 days before due date")
    else:
        st.info(f"Next payment due in {days_until_payment} days (Rs. {monthly_amount:,})")

def show_payout_schedule(committee):
    st.subheader("Payout Schedule")
    
    # Member's payout information
    member_position = committee['members'].index(st.session_state.current_user) + 1
    monthly_pool = committee['monthly_amount'] * committee['current_members']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Your Position", f"{member_position} of {committee['current_members']}")
    with col2:
        payout_amount = monthly_pool
        st.metric("Your Payout Amount", f"Rs. {payout_amount:,}")
    with col3:
        months_to_wait = member_position - 1
        payout_date = datetime.now() + timedelta(days=30 * months_to_wait)
        st.metric("Expected Payout Date", payout_date.strftime("%b %Y"))
    
    # Payout calendar
    st.subheader("Committee Payout Calendar")
    
    # Create payout schedule
    payout_schedule = []
    for i, member_id in enumerate(committee['members']):
        payout_month = datetime.now() + timedelta(days=30 * i)
        is_current_user = member_id == st.session_state.current_user
        
        payout_schedule.append({
            'Position': i + 1,
            'Month': payout_month.strftime('%b %Y'),
            'Member': 'You' if is_current_user else f'Member {i + 1}',
            'Amount': f"Rs. {monthly_pool:,}",
            'Status': '⭐' if is_current_user else '👤'
        })
    
    schedule_df = pd.DataFrame(payout_schedule)
    
    # Highlight current user's row
    def highlight_user(row):
        return ['background-color: #90EE90' if row['Member'] == 'You' else '' for _ in row]
    
    styled_schedule = schedule_df.style.apply(highlight_user, axis=1)
    st.dataframe(styled_schedule, use_container_width=True)
    
    # Payout options
    st.subheader("Payout Preferences")
    
    with st.form("payout_preferences"):
        payout_method = st.selectbox("Preferred Payout Method", [
            "Bank Transfer",
            "Cash Pickup",
            "Halal Product Vouchers",
            "Gold/Silver Purchase",
            "Investment in Halal Mutual Funds"
        ])
        
        bank_details = st.text_input("Bank Account (if applicable)", placeholder="Account number")
        
        special_instructions = st.text_area("Special Instructions", 
                                          placeholder="Any specific instructions for your payout...")
        
        if st.form_submit_button("Save Preferences"):
            st.success("Payout preferences saved successfully!")
    
    # Payout simulation
    st.subheader("Payout Simulation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cash Payout Simulation**")
        st.write(f"Amount: Rs. {monthly_pool:,}")
        st.write(f"Tax Deduction: Rs. {int(monthly_pool * 0.01):,} (1%)")
        st.write(f"Net Amount: Rs. {int(monthly_pool * 0.99):,}")
        
        if st.button("Simulate Cash Payout"):
            st.success(f"Cash payout of Rs. {int(monthly_pool * 0.99):,} would be processed!")
    
    with col2:
        st.write("**Halal Product Rewards**")
        
        product_options = [
            {"name": "Electronics Voucher", "value": monthly_pool},
            {"name": "Grocery Package", "value": monthly_pool * 1.1},
            {"name": "Gold (2 tola)", "value": monthly_pool * 0.95},
            {"name": "Hajj/Umrah Fund", "value": monthly_pool * 1.05}
        ]
        
        selected_product = st.selectbox("Choose Product Reward", 
                                       [f"{p['name']} (Rs. {p['value']:,.0f})" for p in product_options])
        
        if st.button("Simulate Product Reward"):
            st.success(f"Product reward '{selected_product}' would be arranged!")

def show_trust_score_details():
    st.subheader("Trust Score Details")
    
    # Current trust score
    trust_score = st.session_state.user_data.get('trust_score', random.randint(80, 95))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Trust score gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = trust_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Trust Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#228B22"},
                'steps': [
                    {'range': [0, 50], 'color': "#FFB6C1"},
                    {'range': [50, 80], 'color': "#FFFF99"},
                    {'range': [80, 100], 'color': "#90EE90"}
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
        st.write("**Trust Score Breakdown**")
        
        factors = {
            'Payment History': 95,
            'Committee Participation': 88,
            'Profile Completeness': 100,
            'Community Feedback': 85,
            'Account Verification': 100
        }
        
        for factor, score in factors.items():
            st.write(f"**{factor}:** {score}%")
            st.progress(score / 100)
    
    with col3:
        st.write("**Trust Level Benefits**")
        
        if trust_score >= 90:
            st.success("🌟 **Excellent Trust Level**")
            benefits = [
                "✅ Priority in committee selection",
                "✅ Lower fees and charges",
                "✅ Access to premium committees",
                "✅ Fast-track payout processing"
            ]
        elif trust_score >= 70:
            st.info("👍 **Good Trust Level**")
            benefits = [
                "✅ Standard committee access",
                "✅ Regular payout processing",
                "⚠️ Work on payment consistency",
                "⚠️ Complete profile verification"
            ]
        else:
            st.warning("⚠️ **Needs Improvement**")
            benefits = [
                "❌ Limited committee access",
                "❌ Extended payout processing",
                "❌ Higher security deposits",
                "❌ Requires guarantor"
            ]
        
        for benefit in benefits:
            st.write(benefit)
    
    # Trust score history
    st.subheader("Trust Score History")
    
    # Generate dummy trust score history
    dates = [datetime.now() - timedelta(days=30*i) for i in range(6)][::-1]
    scores = [trust_score - random.randint(-5, 5) for _ in range(6)]
    scores[-1] = trust_score  # Current score
    
    history_df = pd.DataFrame({
        'Date': dates,
        'Trust Score': scores
    })
    
    fig = px.line(history_df, x='Date', y='Trust Score',
                 title="Trust Score Trend (Last 6 Months)",
                 markers=True)
    fig.update_layout(height=300)
    fig.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="Excellent Threshold")
    fig.add_hline(y=70, line_dash="dash", line_color="orange", annotation_text="Good Threshold")
    st.plotly_chart(fig, use_container_width=True)
    
    # Improvement tips
    st.subheader("Improve Your Trust Score")
    
    tips = [
        "💰 **Make payments on time**: Consistent payments boost your score significantly",
        "👥 **Participate actively**: Engage with committee members and admin",
        "📝 **Complete your profile**: Add all required information and verification",
        "🤝 **Get positive feedback**: Maintain good relationships with committee members",
        "🔒 **Verify your account**: Complete KYC and phone/email verification"
    ]
    
    for tip in tips:
        st.write(tip)

if __name__ == "__main__":
    show_member_dashboard()
