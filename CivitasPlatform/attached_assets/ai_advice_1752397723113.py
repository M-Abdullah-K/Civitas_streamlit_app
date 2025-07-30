import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from utils.ai_engine import get_financial_advice, analyze_risk_profile, generate_budget_recommendations

def show_ai_advice():
    st.title("🤖 AI Financial Advisor")
    
    if not st.session_state.get('authenticated', False):
        st.error("Please login to access this page")
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💡 Personal Advice", "⚖️ Risk Analysis", "📊 Budget Planning", "🎯 Goal Setting"])
    
    with tab1:
        show_personal_advice()
    
    with tab2:
        show_risk_analysis()
    
    with tab3:
        show_budget_planning()
    
    with tab4:
        show_goal_setting()

def show_personal_advice():
    st.subheader("Personalized Financial Advice")
    
    # Financial profile input
    with st.form("financial_profile"):
        st.write("**Tell us about your financial situation:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_income = st.number_input("Monthly Income (PKR)", value=50000, step=5000)
            monthly_expenses = st.number_input("Monthly Fixed Expenses (PKR)", value=25000, step=2000)
            dependents = st.number_input("Number of Dependents", value=2, step=1, min_value=0)
        
        with col2:
            current_savings = st.number_input("Current Savings (PKR)", value=100000, step=10000)
            debt_amount = st.number_input("Outstanding Debt (PKR)", value=0, step=5000)
            age = st.number_input("Your Age", value=30, step=1, min_value=18, max_value=80)
        
        financial_goals = st.multiselect("Financial Goals", [
            "Emergency Fund", "House Purchase", "Car Purchase", "Children's Education",
            "Hajj/Umrah", "Retirement Planning", "Business Investment", "Wedding Expenses"
        ])
        
        risk_tolerance = st.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
        
        submitted = st.form_submit_button("Get AI Advice")
        
        if submitted:
            # Store financial profile in session state with a different key approach
            financial_profile_data = {
                'monthly_income': monthly_income,
                'monthly_expenses': monthly_expenses,
                'dependents': dependents,
                'current_savings': current_savings,
                'debt_amount': debt_amount,
                'age': age,
                'financial_goals': financial_goals,
                'risk_tolerance': risk_tolerance
            }
            
            # Clear existing key if it exists to avoid conflict
            if 'financial_profile' in st.session_state:
                del st.session_state['financial_profile']
            
            st.session_state['financial_profile'] = financial_profile_data
    
    # Generate advice if profile exists
    if 'financial_profile' in st.session_state:
        profile = st.session_state.financial_profile
        advice = get_financial_advice(profile)
        
        # Display AI advice
        st.subheader("🎯 Your Personalized Advice")
        
        # Financial health score
        disposable_income = profile['monthly_income'] - profile['monthly_expenses']
        debt_to_income = profile['debt_amount'] / (profile['monthly_income'] * 12) if profile['monthly_income'] > 0 else 0
        savings_ratio = profile['current_savings'] / (profile['monthly_income'] * 6) if profile['monthly_income'] > 0 else 0
        
        # Calculate financial health score
        health_score = calculate_financial_health_score(profile)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Financial Health Score", f"{health_score}/100", 
                     "Good" if health_score > 70 else "Needs Improvement")
        
        with col2:
            st.metric("Monthly Surplus", f"Rs. {disposable_income:,}", 
                     "Positive" if disposable_income > 0 else "Negative")
        
        with col3:
            committee_capacity = max(0, int(disposable_income * 0.3))
            st.metric("Committee Capacity", f"Rs. {committee_capacity:,}", "Monthly")
        
        # AI Recommendations
        for category, recommendations in advice.items():
            with st.expander(f"📋 {category}", expanded=True):
                for rec in recommendations:
                    if rec['priority'] == 'high':
                        st.error(f"🚨 **High Priority:** {rec['message']}")
                    elif rec['priority'] == 'medium':
                        st.warning(f"⚠️ **Medium Priority:** {rec['message']}")
                    else:
                        st.info(f"💡 **Suggestion:** {rec['message']}")

def show_risk_analysis():
    st.subheader("Risk Profile Analysis")
    
    if 'financial_profile' not in st.session_state:
        st.warning("Please complete your financial profile in the Personal Advice tab first.")
        return
    
    profile = st.session_state.financial_profile
    risk_analysis = analyze_risk_profile(profile)
    
    # Risk assessment visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk score gauge
        risk_score = risk_analysis['overall_risk_score']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Risk Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': get_risk_color(risk_score)},
                'steps': [
                    {'range': [0, 30], 'color': "#90EE90"},  # Low risk - Green
                    {'range': [30, 70], 'color': "#FFFF99"},  # Medium risk - Yellow
                    {'range': [70, 100], 'color': "#FFB6C1"}  # High risk - Red
                ],
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Risk Factors Analysis:**")
        
        for factor, details in risk_analysis['risk_factors'].items():
            risk_level = details['level']
            color = "🟢" if risk_level == "Low" else "🟡" if risk_level == "Medium" else "🔴"
            
            st.write(f"{color} **{factor}:** {risk_level}")
            st.write(f"   {details['description']}")
    
    # Committee recommendations based on risk
    st.subheader("Committee Recommendations Based on Your Risk Profile")
    
    committee_recommendations = get_committee_recommendations_by_risk(risk_analysis)
    
    for rec_type, committees in committee_recommendations.items():
        with st.expander(f"📊 {rec_type} Committees", expanded=True):
            for committee in committees:
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.write(f"**{committee['type']}**")
                    st.write(f"{committee['description']}")
                
                with col2:
                    st.write(f"**Amount:** {committee['amount']}")
                    st.write(f"**Duration:** {committee['duration']}")
                
                with col3:
                    st.write(f"**Risk Level:** {committee['risk_level']}")
                    if committee['recommended']:
                        st.success("✅ Recommended")
                    else:
                        st.warning("⚠️ Consider carefully")

def show_budget_planning():
    st.subheader("AI-Powered Budget Planning")
    
    if 'financial_profile' not in st.session_state:
        st.warning("Please complete your financial profile in the Personal Advice tab first.")
        return
    
    profile = st.session_state.financial_profile
    budget_recommendations = generate_budget_recommendations(profile)
    
    # Current vs Recommended Budget
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Budget Breakdown**")
        
        current_budget = {
            'Fixed Expenses': profile['monthly_expenses'],
            'Available Income': profile['monthly_income'] - profile['monthly_expenses'],
            'Debt Payments': min(profile['debt_amount'] // 12, profile['monthly_income'] * 0.2),
        }
        
        fig1 = px.pie(
            values=list(current_budget.values()),
            names=list(current_budget.keys()),
            title="Current Budget Allocation",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.write("**AI Recommended Budget**")
        
        recommended_budget = budget_recommendations['recommended_allocation']
        
        fig2 = px.pie(
            values=list(recommended_budget.values()),
            names=list(recommended_budget.keys()),
            title="AI Recommended Allocation",
            color_discrete_sequence=['#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD']
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Budget recommendations
    st.subheader("💡 Budget Optimization Suggestions")
    
    for category, suggestion in budget_recommendations['suggestions'].items():
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if suggestion['impact'] == 'high':
                    st.error("🔥 High Impact")
                elif suggestion['impact'] == 'medium':
                    st.warning("⚡ Medium Impact")
                else:
                    st.info("💡 Low Impact")
            
            with col2:
                st.write(f"**{category}:** {suggestion['message']}")
                if 'savings_potential' in suggestion:
                    st.write(f"*Potential Monthly Savings: Rs. {suggestion['savings_potential']:,}*")
    
    # Committee budget planning
    st.subheader("Committee Budget Integration")
    
    user_committees = get_user_committees()
    total_committee_commitment = sum([c['monthly_amount'] for c in user_committees])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Committee Commitment", f"Rs. {total_committee_commitment:,}")
    
    with col2:
        recommended_committee_budget = int(profile['monthly_income'] * 0.15)  # 15% of income
        st.metric("Recommended Committee Budget", f"Rs. {recommended_committee_budget:,}")
    
    with col3:
        remaining_capacity = max(0, recommended_committee_budget - total_committee_commitment)
        st.metric("Additional Capacity", f"Rs. {remaining_capacity:,}")
    
    # Committee optimization suggestions
    if total_committee_commitment > recommended_committee_budget:
        st.error(f"⚠️ You're over-committed to committees by Rs. {total_committee_commitment - recommended_committee_budget:,}")
        st.write("**Suggestions:**")
        st.write("- Consider reducing participation in some committees")
        st.write("- Focus on higher-return committees")
        st.write("- Increase your income before taking on more commitments")
    elif remaining_capacity > 5000:
        st.success(f"✅ You can safely join additional committees worth Rs. {remaining_capacity:,}/month")
        st.write("**Opportunities:**")
        st.write("- Look for committees with good return potential")
        st.write("- Consider diversifying across different committee types")
        st.write("- Maintain emergency fund before expanding")

def show_goal_setting():
    st.subheader("Smart Goal Setting & Planning")
    
    # Goal input form
    with st.form("goal_setting"):
        st.write("**Set Your Financial Goals:**")
        
        goal_type = st.selectbox("Goal Type", [
            "Emergency Fund", "House Down Payment", "Car Purchase", "Children's Education",
            "Hajj/Umrah", "Wedding", "Retirement", "Business Investment", "Custom Goal"
        ])
        
        if goal_type == "Custom Goal":
            goal_name = st.text_input("Goal Name")
        else:
            goal_name = goal_type
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_amount = st.number_input("Target Amount (PKR)", value=500000, step=50000)
            timeline_years = st.number_input("Timeline (Years)", value=2, step=1, min_value=1, max_value=30)
        
        with col2:
            priority = st.selectbox("Priority Level", ["High", "Medium", "Low"])
            current_progress = st.number_input("Current Progress (PKR)", value=0, step=10000)
        
        goal_submitted = st.form_submit_button("Add Goal")
        
        if goal_submitted:
            if 'financial_goals' not in st.session_state:
                st.session_state.financial_goals = []
            
            new_goal = {
                'name': goal_name,
                'target_amount': target_amount,
                'timeline_years': timeline_years,
                'priority': priority,
                'current_progress': current_progress,
                'created_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            st.session_state.financial_goals.append(new_goal)
            st.success(f"Goal '{goal_name}' added successfully!")
    
    # Display existing goals
    if 'financial_goals' in st.session_state and st.session_state.financial_goals:
        st.subheader("Your Financial Goals")
        
        for i, goal in enumerate(st.session_state.financial_goals):
            with st.expander(f"🎯 {goal['name']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    progress_percentage = (goal['current_progress'] / goal['target_amount']) * 100
                    st.metric("Progress", f"{progress_percentage:.1f}%")
                    st.progress(progress_percentage / 100)
                
                with col2:
                    remaining_amount = goal['target_amount'] - goal['current_progress']
                    st.metric("Remaining", f"Rs. {remaining_amount:,}")
                    
                    monthly_required = remaining_amount / (goal['timeline_years'] * 12)
                    st.metric("Monthly Required", f"Rs. {monthly_required:,}")
                
                with col3:
                    st.metric("Priority", goal['priority'])
                    st.metric("Timeline", f"{goal['timeline_years']} years")
                
                # AI recommendations for this goal
                goal_advice = generate_goal_specific_advice(goal)
                
                st.write("**🤖 AI Recommendations:**")
                for advice in goal_advice:
                    if advice['type'] == 'committee':
                        st.info(f"💼 {advice['message']}")
                    elif advice['type'] == 'savings':
                        st.success(f"💰 {advice['message']}")
                    elif advice['type'] == 'investment':
                        st.warning(f"📈 {advice['message']}")
                    else:
                        st.write(f"💡 {advice['message']}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Update Progress", key=f"update_{i}"):
                        st.info("Progress update feature would open here")
                with col2:
                    if st.button(f"Modify Goal", key=f"modify_{i}"):
                        st.info("Goal modification feature would open here")
                with col3:
                    if st.button(f"Delete Goal", key=f"delete_{i}"):
                        st.session_state.financial_goals.pop(i)
                        st.rerun()
    
    # Goal achievement strategies
    if 'financial_profile' in st.session_state and 'financial_goals' in st.session_state:
        st.subheader("📈 Goal Achievement Strategy")
        
        profile = st.session_state.financial_profile
        goals = st.session_state.financial_goals
        
        total_monthly_required = sum([
            (goal['target_amount'] - goal['current_progress']) / (goal['timeline_years'] * 12)
            for goal in goals
        ])
        
        available_for_goals = max(0, profile['monthly_income'] - profile['monthly_expenses'] - 10000)  # Keep 10k buffer
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Monthly Required for All Goals", f"Rs. {total_monthly_required:,}")
            st.metric("Available Monthly Amount", f"Rs. {available_for_goals:,}")
        
        with col2:
            if total_monthly_required > available_for_goals:
                deficit = total_monthly_required - available_for_goals
                st.error(f"Monthly Deficit: Rs. {deficit:,}")
                
                st.write("**Strategies to Bridge the Gap:**")
                st.write("- Increase income through side business")
                st.write("- Extend timeline for some goals")
                st.write("- Use committee system strategically")
                st.write("- Reduce non-essential expenses")
            else:
                surplus = available_for_goals - total_monthly_required
                st.success(f"Monthly Surplus: Rs. {surplus:,}")
                
                st.write("**Optimization Opportunities:**")
                st.write("- Accelerate high-priority goals")
                st.write("- Add new financial goals")
                st.write("- Increase emergency fund")
                st.write("- Explore halal investment options")

# Helper functions
def calculate_financial_health_score(profile):
    score = 0
    
    # Income stability (25 points)
    if profile['monthly_income'] > 30000:
        score += 25
    elif profile['monthly_income'] > 15000:
        score += 15
    else:
        score += 5
    
    # Expense ratio (25 points)
    expense_ratio = profile['monthly_expenses'] / profile['monthly_income']
    if expense_ratio < 0.5:
        score += 25
    elif expense_ratio < 0.7:
        score += 15
    else:
        score += 5
    
    # Savings (25 points)
    savings_months = profile['current_savings'] / profile['monthly_expenses']
    if savings_months >= 6:
        score += 25
    elif savings_months >= 3:
        score += 15
    else:
        score += 5
    
    # Debt ratio (25 points)
    if profile['debt_amount'] == 0:
        score += 25
    else:
        debt_ratio = profile['debt_amount'] / (profile['monthly_income'] * 12)
        if debt_ratio < 0.2:
            score += 20
        elif debt_ratio < 0.4:
            score += 10
        else:
            score += 0
    
    return min(100, score)

def get_risk_color(risk_score):
    if risk_score < 30:
        return "#228B22"  # Green
    elif risk_score < 70:
        return "#FFD700"  # Yellow
    else:
        return "#DC143C"  # Red

def get_committee_recommendations_by_risk(risk_analysis):
    risk_score = risk_analysis['overall_risk_score']
    
    if risk_score < 30:  # Low risk
        return {
            "Recommended": [
                {
                    "type": "High-Value Committee",
                    "description": "Large amount, established members",
                    "amount": "Rs. 15,000-25,000/month",
                    "duration": "12-18 months",
                    "risk_level": "Medium",
                    "recommended": True
                },
                {
                    "type": "Business Committee",
                    "description": "Professional network, business purpose",
                    "amount": "Rs. 20,000-50,000/month",
                    "duration": "18-24 months",
                    "risk_level": "Medium-High",
                    "recommended": True
                }
            ],
            "Alternative": [
                {
                    "type": "Conservative Committee",
                    "description": "Low amounts, short duration",
                    "amount": "Rs. 5,000-10,000/month",
                    "duration": "6-12 months",
                    "risk_level": "Low",
                    "recommended": True
                }
            ]
        }
    elif risk_score < 70:  # Medium risk
        return {
            "Recommended": [
                {
                    "type": "Standard Committee",
                    "description": "Moderate amounts, mixed membership",
                    "amount": "Rs. 8,000-15,000/month",
                    "duration": "12 months",
                    "risk_level": "Medium",
                    "recommended": True
                }
            ],
            "Caution": [
                {
                    "type": "High-Value Committee",
                    "description": "Large commitments, longer duration",
                    "amount": "Rs. 20,000+/month",
                    "duration": "18+ months",
                    "risk_level": "High",
                    "recommended": False
                }
            ]
        }
    else:  # High risk
        return {
            "Start Small": [
                {
                    "type": "Mini Committee",
                    "description": "Small amounts, proven track record needed",
                    "amount": "Rs. 2,000-5,000/month",
                    "duration": "6 months",
                    "risk_level": "Low",
                    "recommended": True
                }
            ],
            "Not Recommended": [
                {
                    "type": "Any Large Committee",
                    "description": "High financial commitment",
                    "amount": "Rs. 10,000+/month",
                    "duration": "Any",
                    "risk_level": "High",
                    "recommended": False
                }
            ]
        }

def generate_goal_specific_advice(goal):
    advice = []
    
    monthly_required = (goal['target_amount'] - goal['current_progress']) / (goal['timeline_years'] * 12)
    
    if goal['name'] in ['House Down Payment', 'Car Purchase']:
        advice.append({
            'type': 'committee',
            'message': f"Consider joining a committee worth Rs. {int(monthly_required * 1.2):,}/month to build this fund faster"
        })
    
    if goal['name'] == 'Emergency Fund':
        advice.append({
            'type': 'savings',
            'message': "Keep emergency funds in easily accessible savings accounts, not committees"
        })
    
    if goal['name'] in ['Hajj/Umrah', 'Wedding']:
        advice.append({
            'type': 'investment',
            'message': "Consider halal investment options to grow your savings for this religious/cultural goal"
        })
    
    if monthly_required > 10000:
        advice.append({
            'type': 'general',
            'message': f"This goal requires Rs. {monthly_required:,}/month. Consider extending timeline or increasing income."
        })
    
    return advice

def get_user_committees():
    if 'committees' not in st.session_state:
        return []
    return [c for c in st.session_state.committees if st.session_state.current_user in c['members']]

if __name__ == "__main__":
    show_ai_advice()
