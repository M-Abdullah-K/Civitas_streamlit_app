import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
from database.db_manager import DatabaseManager
from components.civitas_chatbot import show_chatbot_widget

def show_ai_advice(db: DatabaseManager, user_id: str):
    """Display AI-powered financial advice with enhanced Pakistani context"""
    
    st.title("🤖 AI Financial Advisor")
    st.markdown("*Shariah-compliant financial guidance tailored for Pakistan*")
    
    # Main tabs - AI Chatbot first
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🤖 AI Chatbot",
        "💡 Personal Advice", 
        "⚖️ Risk Analysis", 
        "📊 Budget Planning", 
        "🎯 Goal Setting"
    ])
    
    with tab1:
        show_ai_chatbot_tab()
    
    with tab2:
        show_personal_advice(db, user_id)
    
    with tab3:
        show_risk_analysis(db, user_id)
    
    with tab4:
        show_budget_planning(db, user_id)
    
    with tab5:
        show_goal_setting(db, user_id)

def show_personal_advice(db: DatabaseManager, user_id: str):
    """Show personalized financial advice based on user profile"""
    
    st.subheader("💡 Personalized Financial Advice")
    
    # Check if user has existing financial profile
    if 'financial_profile' not in st.session_state:
        st.info("📝 Please complete your financial profile to receive personalized advice.")
    
    # Financial profile input form
    with st.form("financial_profile_form"):
        st.markdown("### 📋 Your Financial Profile")
        st.write("*All information is kept confidential and used only for generating advice*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💰 Income & Expenses**")
            monthly_income = st.number_input("Monthly Income (PKR)", 
                                           value=st.session_state.get('financial_profile', {}).get('monthly_income', 50000),
                                           step=5000,
                                           help="Your total monthly income from all sources")
            
            monthly_expenses = st.number_input("Monthly Fixed Expenses (PKR)", 
                                             value=st.session_state.get('financial_profile', {}).get('monthly_expenses', 25000),
                                             step=2000,
                                             help="Rent, utilities, groceries, transportation, etc.")
            
            existing_debt = st.number_input("Outstanding Debt (PKR)", 
                                          value=st.session_state.get('financial_profile', {}).get('existing_debt', 0),
                                          step=5000,
                                          help="Total debt including credit cards, loans, etc.")
        
        with col2:
            st.markdown("**👨‍👩‍👧‍👦 Personal Details**")
            age = st.number_input("Your Age", 
                                value=st.session_state.get('financial_profile', {}).get('age', 30),
                                min_value=18, 
                                max_value=80,
                                help="Used for retirement planning calculations")
            
            dependents = st.number_input("Number of Dependents", 
                                       value=st.session_state.get('financial_profile', {}).get('dependents', 2),
                                       min_value=0,
                                       help="Spouse, children, parents you financially support")
            
            current_savings = st.number_input("Current Savings (PKR)", 
                                            value=st.session_state.get('financial_profile', {}).get('current_savings', 100000),
                                            step=10000,
                                            help="Total savings in bank accounts, investments, etc.")
        
        # Financial goals and risk tolerance
        st.markdown("**🎯 Financial Goals & Preferences**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            financial_goals = st.multiselect("Primary Financial Goals", [
                "🏠 House Purchase/Down Payment",
                "🚗 Vehicle Purchase", 
                "🎓 Children's Education",
                "💒 Wedding Expenses",
                "🕋 Hajj/Umrah Fund",
                "💼 Business Investment",
                "🏥 Healthcare Emergency Fund",
                "👴 Retirement Planning",
                "📈 Wealth Building"
            ], default=st.session_state.get('financial_profile', {}).get('financial_goals', []))
        
        with col2:
            risk_tolerance = st.selectbox("Risk Tolerance", 
                                        ["Conservative (Safety First)", "Moderate (Balanced)", "Aggressive (Growth Focus)"],
                                        index=1)
            
            investment_knowledge = st.selectbox("Investment Knowledge Level", [
                "Beginner (New to investing)",
                "Intermediate (Some experience)", 
                "Advanced (Experienced investor)"
            ])
            
            islamic_finance_pref = st.selectbox("Islamic Finance Preference", [
                "Strictly Halal only",
                "Prefer Halal but flexible",
                "No specific preference"
            ])
        
        # Submit button
        submitted = st.form_submit_button("🎯 Get AI Financial Advice", 
                                        use_container_width=True, 
                                        type="primary")
        
        if submitted:
            # Store profile data
            financial_profile = {
                'monthly_income': monthly_income,
                'monthly_expenses': monthly_expenses,
                'existing_debt': existing_debt,
                'age': age,
                'dependents': dependents,
                'current_savings': current_savings,
                'financial_goals': financial_goals,
                'risk_tolerance': risk_tolerance,
                'investment_knowledge': investment_knowledge,
                'islamic_finance_pref': islamic_finance_pref,
                'last_updated': datetime.now()
            }
            
            st.session_state.financial_profile = financial_profile
            st.success("✅ Financial profile updated! Generating personalized advice...")
    
    # Display AI advice if profile exists
    if 'financial_profile' in st.session_state:
        profile = st.session_state.financial_profile
        
        # Calculate key financial metrics
        disposable_income = profile['monthly_income'] - profile['monthly_expenses']
        debt_to_income_ratio = (profile['existing_debt'] / (profile['monthly_income'] * 12)) * 100 if profile['monthly_income'] > 0 else 0
        emergency_fund_months = profile['current_savings'] / profile['monthly_expenses'] if profile['monthly_expenses'] > 0 else 0
        
        # Financial health score calculation
        health_score = calculate_financial_health_score(profile)
        
        # Display financial health overview
        st.markdown("### 🩺 Your Financial Health Score")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score_color = get_health_score_color(health_score)
            st.markdown(f"""
            <div style="background: {score_color}; color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
                <h2 style="margin: 0; color: white;">{health_score}/100</h2>
                <p style="margin: 0; opacity: 0.9;">Health Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            surplus_color = "#228B22" if disposable_income > 0 else "#DC143C"
            st.markdown(f"""
            <div style="background: {surplus_color}; color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
                <h2 style="margin: 0; color: white;">Rs. {abs(disposable_income):,}</h2>
                <p style="margin: 0; opacity: 0.9;">{'Surplus' if disposable_income > 0 else 'Deficit'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            committee_capacity = max(0, int(disposable_income * 0.3)) if disposable_income > 0 else 0
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FFD700, #FFA500); color: #333; padding: 1.5rem; border-radius: 15px; text-align: center;">
                <h2 style="margin: 0; color: #333;">Rs. {committee_capacity:,}</h2>
                <p style="margin: 0; opacity: 0.8;">Committee Capacity</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            emergency_color = "#228B22" if emergency_fund_months >= 6 else "#FFA500" if emergency_fund_months >= 3 else "#DC143C"
            st.markdown(f"""
            <div style="background: {emergency_color}; color: white; padding: 1.5rem; border-radius: 15px; text-align: center;">
                <h2 style="margin: 0; color: white;">{emergency_fund_months:.1f}</h2>
                <p style="margin: 0; opacity: 0.9;">Emergency Months</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Generate and display AI recommendations
        advice_categories = generate_ai_advice(profile, health_score, disposable_income, debt_to_income_ratio, emergency_fund_months)
        
        st.markdown("### 🎯 AI-Generated Recommendations")
        
        for category, recommendations in advice_categories.items():
            with st.expander(f"📋 {category}", expanded=True):
                for rec in recommendations:
                    priority_colors = {
                        'high': '#DC143C',
                        'medium': '#FFA500', 
                        'low': '#228B22'
                    }
                    
                    priority_icons = {
                        'high': '🚨',
                        'medium': '⚠️',
                        'low': '💡'
                    }
                    
                    color = priority_colors.get(rec['priority'], '#666')
                    icon = priority_icons.get(rec['priority'], '💡')
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid {color}; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; align-items: start; gap: 1rem;">
                            <span style="font-size: 1.5rem;">{icon}</span>
                            <div style="flex: 1;">
                                <h5 style="margin: 0; color: #333;">{rec['title']}</h5>
                                <p style="margin: 0.5rem 0; color: #666;">{rec['message']}</p>
                                {f'<p style="margin: 0; color: {color}; font-weight: bold;">💰 Potential Savings: Rs. {rec["savings_potential"]:,}/month</p>' if rec.get('savings_potential') else ''}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def show_risk_analysis(db: DatabaseManager, user_id: str):
    """Show comprehensive risk analysis"""
    
    st.subheader("⚖️ Risk Profile Analysis")
    
    if 'financial_profile' not in st.session_state:
        st.warning("📝 Please complete your financial profile in the Personal Advice tab first.")
        return
    
    profile = st.session_state.financial_profile
    
    # Calculate various risk factors
    risk_analysis = analyze_risk_factors(profile)
    overall_risk_score = risk_analysis['overall_risk_score']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Risk Score", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': get_risk_color(overall_risk_score)},
                'steps': [
                    {'range': [0, 30], 'color': "#90EE90"},    # Low risk
                    {'range': [30, 60], 'color': "#FFFF99"},   # Medium risk
                    {'range': [60, 100], 'color': "#FFB6C1"}  # High risk
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**🔍 Risk Factors Breakdown**")
        
        for factor, details in risk_analysis['risk_factors'].items():
            risk_level = details['level']
            description = details['description']
            
            if risk_level == "Low":
                color = "#228B22"
                icon = "🟢"
            elif risk_level == "Medium":
                color = "#FFA500"
                icon = "🟡"
            else:
                color = "#DC143C"
                icon = "🔴"
            
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {color}; margin: 0.5rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span>{icon}</span>
                    <strong>{factor}</strong>
                    <span style="background: {color}; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem;">
                        {risk_level}
                    </span>
                </div>
                <p style="margin: 0.5rem 0 0 2rem; color: #666; font-size: 0.9rem;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Committee recommendations based on risk profile
    st.markdown("### 🏛️ Committee Recommendations Based on Your Risk Profile")
    
    recommendations = get_committee_recommendations_by_risk(risk_analysis, profile)
    
    for rec_type, committees in recommendations.items():
        with st.expander(f"📊 {rec_type}", expanded=True):
            for committee_rec in committees:
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1rem; align-items: center;">
                        <div>
                            <h5 style="margin: 0; color: #228B22;">{committee_rec['type']}</h5>
                            <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">{committee_rec['description']}</p>
                        </div>
                        <div style="text-align: center;">
                            <strong>Amount:</strong> {committee_rec['amount']}<br>
                            <strong>Duration:</strong> {committee_rec['duration']}
                        </div>
                        <div style="text-align: center;">
                            <span style="background: {'#228B22' if committee_rec['recommended'] else '#FFA500'}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                                {'✅ Recommended' if committee_rec['recommended'] else '⚠️ Consider Carefully'}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def show_budget_planning(db: DatabaseManager, user_id: str):
    """Show AI-powered budget planning"""
    
    st.subheader("📊 AI Budget Planning")
    
    if 'financial_profile' not in st.session_state:
        st.warning("📝 Please complete your financial profile in the Personal Advice tab first.")
        return
    
    profile = st.session_state.financial_profile
    
    # Generate budget recommendations
    budget_recommendations = generate_budget_recommendations(profile)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Current Budget Allocation")
        
        current_budget = {
            'Fixed Expenses': profile['monthly_expenses'],
            'Available Income': max(0, profile['monthly_income'] - profile['monthly_expenses']),
            'Debt Payments': min(profile['existing_debt'] // 12, profile['monthly_income'] * 0.2) if profile['existing_debt'] > 0 else 0
        }
        
        # Remove zero values
        current_budget = {k: v for k, v in current_budget.items() if v > 0}
        
        if current_budget:
            fig1 = px.pie(
                values=list(current_budget.values()),
                names=list(current_budget.keys()),
                title="Current Monthly Budget",
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )
            fig1.update_layout(height=350)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 AI Recommended Budget")
        
        recommended_budget = budget_recommendations['recommended_allocation']
        
        fig2 = px.pie(
            values=list(recommended_budget.values()),
            names=list(recommended_budget.keys()),
            title="AI Optimized Budget",
            color_discrete_sequence=['#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD']
        )
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Budget optimization suggestions
    st.markdown("### 💡 Budget Optimization Suggestions")
    
    for category, suggestion in budget_recommendations['suggestions'].items():
        impact_colors = {
            'high': '#DC143C',
            'medium': '#FFA500',
            'low': '#228B22'
        }
        
        impact_icons = {
            'high': '🔥',
            'medium': '⚡',
            'low': '💡'
        }
        
        color = impact_colors.get(suggestion['impact'], '#666')
        icon = impact_icons.get(suggestion['impact'], '💡')
        
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid {color}; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: start; gap: 1rem;">
                <span style="font-size: 2rem;">{icon}</span>
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: #333;">{category}</h4>
                    <p style="margin: 0.5rem 0; color: #666; line-height: 1.5;">{suggestion['message']}</p>
                    {f'<div style="background: {color}; color: white; padding: 0.5rem 1rem; border-radius: 8px; margin-top: 1rem; display: inline-block;"><strong>💰 Potential Monthly Savings: Rs. {suggestion["savings_potential"]:,}</strong></div>' if suggestion.get('savings_potential') else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Committee budget integration
    st.markdown("### 🏛️ Committee Budget Integration")
    
    user_committees = db.get_user_committees(user_id)
    total_committee_commitment = sum([c.monthly_amount for c in user_committees]) if user_committees else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Current Committee Spending", f"Rs. {total_committee_commitment:,}")
    
    with col2:
        recommended_committee_budget = int(profile['monthly_income'] * 0.15)  # 15% of income
        st.metric("🎯 Recommended Committee Budget", f"Rs. {recommended_committee_budget:,}")
    
    with col3:
        remaining_capacity = max(0, recommended_committee_budget - total_committee_commitment)
        st.metric("📈 Additional Capacity", f"Rs. {remaining_capacity:,}")
    
    # Committee budget analysis
    if total_committee_commitment > recommended_committee_budget:
        over_commitment = total_committee_commitment - recommended_committee_budget
        st.error(f"⚠️ **Over-committed by Rs. {over_commitment:,}**")
        
        st.markdown("**📋 Recommendations:**")
        suggestions = [
            "Consider reducing participation in some committees",
            "Focus on higher-return committees only", 
            "Increase your income before taking on more commitments",
            "Look for committees with shorter duration",
            "Consider bi-monthly payment options to reduce monthly burden"
        ]
        
        for suggestion in suggestions:
            st.write(f"• {suggestion}")
            
    elif remaining_capacity > 5000:
        st.success(f"✅ **You can safely join additional committees worth Rs. {remaining_capacity:,}/month**")
        
        st.markdown("**🎯 Opportunities:**")
        opportunities = [
            "Look for committees with good return potential",
            "Consider diversifying across different committee types",
            "Maintain emergency fund before expanding",
            "Focus on committees aligned with your financial goals"
        ]
        
        for opportunity in opportunities:
            st.write(f"• {opportunity}")

def show_goal_setting(db: DatabaseManager, user_id: str):
    """Show intelligent goal setting and planning"""
    
    st.subheader("🎯 Smart Financial Goal Setting")
    
    # Goal input form
    with st.form("goal_setting_form"):
        st.markdown("### 📋 Set Your Financial Goals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            goal_type = st.selectbox("🎯 Goal Type", [
                "🏠 House Down Payment",
                "🚗 Vehicle Purchase",
                "🎓 Children's Education",
                "💒 Wedding Expenses",
                "🕋 Hajj/Umrah Fund",
                "💼 Business Investment",
                "👴 Retirement Fund",
                "🏥 Healthcare Emergency",
                "📚 Custom Goal"
            ])
            
            if goal_type == "📚 Custom Goal":
                goal_name = st.text_input("Goal Name", placeholder="Enter your custom goal")
            else:
                goal_name = goal_type
            
            target_amount = st.number_input("Target Amount (PKR)", 
                                          value=500000, 
                                          step=50000,
                                          help="Total amount needed for this goal")
        
        with col2:
            timeline_years = st.number_input("Timeline (Years)", 
                                           value=3, 
                                           min_value=1, 
                                           max_value=30,
                                           help="When do you want to achieve this goal?")
            
            priority = st.selectbox("Priority Level", 
                                  ["🔴 High (Essential)", "🟡 Medium (Important)", "🟢 Low (Desired)"])
            
            current_progress = st.number_input("Current Progress (PKR)", 
                                             value=0, 
                                             step=10000,
                                             help="Amount you've already saved for this goal")
        
        # Goal preferences
        st.markdown("**🛠️ Goal Preferences**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            savings_approach = st.selectbox("Savings Approach", [
                "Conservative (Low risk, steady growth)",
                "Balanced (Moderate risk and returns)",
                "Aggressive (Higher risk for faster growth)"
            ])
        
        with col2:
            funding_method = st.selectbox("Preferred Funding Method", [
                "Regular monthly savings",
                "Committee participation",
                "Investment portfolio",
                "Mixed approach"
            ])
        
        submitted = st.form_submit_button("🎯 Create Goal Plan", use_container_width=True, type="primary")
        
        if submitted and target_amount > 0 and timeline_years > 0:
            # Store goal and generate plan
            goal_data = {
                'name': goal_name,
                'target_amount': target_amount,
                'timeline_years': timeline_years,
                'priority': priority,
                'current_progress': current_progress,
                'savings_approach': savings_approach,
                'funding_method': funding_method,
                'created_date': datetime.now()
            }
            
            # Initialize goals list if not exists
            if 'financial_goals' not in st.session_state:
                st.session_state.financial_goals = []
            
            st.session_state.financial_goals.append(goal_data)
            st.success(f"✅ Goal '{goal_name}' created successfully!")
    
    # Display existing goals and plans
    if 'financial_goals' in st.session_state and st.session_state.financial_goals:
        st.markdown("### 📊 Your Financial Goals")
        
        for i, goal in enumerate(st.session_state.financial_goals):
            # Calculate goal metrics
            remaining_amount = goal['target_amount'] - goal['current_progress']
            monthly_savings_needed = remaining_amount / (goal['timeline_years'] * 12)
            progress_percentage = (goal['current_progress'] / goal['target_amount']) * 100
            
            # Goal card
            priority_colors = {
                "🔴 High (Essential)": "#DC143C",
                "🟡 Medium (Important)": "#FFA500",
                "🟢 Low (Desired)": "#228B22"
            }
            
            color = priority_colors.get(goal['priority'], "#666")
            
            with st.container():
                # Goal header with priority color styling
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, {color}, {color}30); padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{goal['name']}</h3>
                            <p style="margin: 0.5rem 0; color: white; opacity: 0.9;">{goal['priority']}</p>
                        </div>
                        <div style="text-align: right; color: white;">
                            <div style="font-size: 1.8rem; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Rs. {goal['target_amount']:,}</div>
                            <div style="opacity: 0.9;">Target Amount</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Progress bar using Streamlit's progress component
                st.subheader("📊 Progress")
                col_prog1, col_prog2 = st.columns([3, 1])
                with col_prog1:
                    st.progress(min(progress_percentage / 100, 1.0))
                with col_prog2:
                    st.metric("Progress", f"{progress_percentage:.1f}%")
                
                # Metrics using Streamlit's metric component
                st.subheader("📈 Key Metrics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="💰 Remaining",
                        value=f"Rs. {remaining_amount:,}",
                        help="Amount still needed to reach your goal"
                    )
                
                with col2:
                    st.metric(
                        label="📅 Monthly Savings",
                        value=f"Rs. {monthly_savings_needed:,.0f}",
                        help="Amount you need to save each month"
                    )
                
                with col3:
                    st.metric(
                        label="⏱️ Timeline",
                        value=f"{goal['timeline_years']} years",
                        help="Time frame to achieve this goal"
                    )
                
                # Goal action buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("📈 Update Progress", key=f"update_{i}", use_container_width=True):
                        st.session_state[f"update_goal_{i}"] = True
                
                with col2:
                    if st.button("🏛️ Find Committees", key=f"committees_{i}", use_container_width=True):
                        show_goal_committees(goal, monthly_savings_needed)
                
                with col3:
                    if st.button("📊 Strategy", key=f"strategy_{i}", use_container_width=True):
                        show_goal_strategy(goal, monthly_savings_needed)
                
                with col4:
                    if st.button("🗑️ Remove", key=f"remove_{i}", use_container_width=True, type="secondary"):
                        st.session_state.financial_goals.pop(i)
                        st.rerun()
                
                # Show update progress form if button was clicked
                if st.session_state.get(f"update_goal_{i}", False):
                    with st.form(f"update_form_{i}"):
                        st.markdown(f"**Update Progress for: {goal['name']}**")
                        
                        new_amount = st.number_input(
                            "Current Amount Saved",
                            value=goal['current_progress'],
                            step=1000,
                            min_value=0,
                            max_value=goal['target_amount'],
                            key=f"new_amount_{i}"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Update Progress", type="primary"):
                                st.session_state.financial_goals[i]['current_progress'] = new_amount
                                st.session_state[f"update_goal_{i}"] = False
                                st.success("✅ Progress updated!")
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"update_goal_{i}"] = False
                                st.rerun()

def calculate_financial_health_score(profile: Dict) -> int:
    """Calculate overall financial health score"""
    
    score = 0
    
    # Income vs Expenses (30 points)
    disposable_income = profile['monthly_income'] - profile['monthly_expenses']
    if disposable_income > 0:
        disposable_ratio = disposable_income / profile['monthly_income']
        score += min(30, int(disposable_ratio * 100))
    
    # Emergency Fund (25 points)
    if profile['monthly_expenses'] > 0:
        emergency_months = profile['current_savings'] / profile['monthly_expenses']
        if emergency_months >= 6:
            score += 25
        elif emergency_months >= 3:
            score += 15
        elif emergency_months >= 1:
            score += 10
    
    # Debt Management (25 points)
    if profile['existing_debt'] == 0:
        score += 25
    else:
        debt_ratio = profile['existing_debt'] / (profile['monthly_income'] * 12)
        if debt_ratio < 0.2:
            score += 20
        elif debt_ratio < 0.4:
            score += 10
        elif debt_ratio < 0.6:
            score += 5
    
    # Age and Planning (20 points)
    if profile['age'] < 30:
        score += 20  # Young with time to build
    elif profile['age'] < 50:
        score += 15  # Middle-aged, good planning time
    else:
        score += 10  # Older, need more aggressive planning
    
    return min(100, max(0, score))

def get_health_score_color(score: int) -> str:
    """Get color based on health score"""
    if score >= 80:
        return "#228B22"
    elif score >= 60:
        return "#FFD700"
    elif score >= 40:
        return "#FFA500"
    else:
        return "#DC143C"

def generate_ai_advice(profile: Dict, health_score: int, disposable_income: float, debt_ratio: float, emergency_months: float) -> Dict:
    """Generate AI-powered financial advice"""
    
    advice = {
        "Emergency Planning": [],
        "Debt Management": [],
        "Committee Strategy": [],
        "Investment Opportunities": [],
        "Lifestyle Optimization": []
    }
    
    # Emergency fund advice
    if emergency_months < 3:
        advice["Emergency Planning"].append({
            'priority': 'high',
            'title': 'Build Emergency Fund',
            'message': f'You have only {emergency_months:.1f} months of expenses saved. Aim for 6 months (Rs. {profile["monthly_expenses"] * 6:,}). Start with Rs. 5,000/month.',
            'savings_potential': 5000
        })
    elif emergency_months < 6:
        advice["Emergency Planning"].append({
            'priority': 'medium',
            'title': 'Strengthen Emergency Fund',
            'message': f'Good start! Increase your emergency fund from {emergency_months:.1f} to 6 months of expenses.',
            'savings_potential': 3000
        })
    
    # Debt management advice
    if profile['existing_debt'] > 0:
        if debt_ratio > 0.4:
            advice["Debt Management"].append({
                'priority': 'high',
                'title': 'Urgent Debt Reduction',
                'message': f'Your debt-to-income ratio is {debt_ratio:.1f}%. Focus on paying down high-interest debt first. Consider debt consolidation.',
                'savings_potential': int(profile['existing_debt'] * 0.02)
            })
        else:
            advice["Debt Management"].append({
                'priority': 'medium',
                'title': 'Accelerate Debt Payoff',
                'message': 'Your debt levels are manageable. Consider the avalanche method: pay minimums on all debts, then extra on highest interest debt.',
                'savings_potential': int(profile['existing_debt'] * 0.01)
            })
    
    # Committee strategy
    if disposable_income > 10000:
        advice["Committee Strategy"].append({
            'priority': 'medium',
            'title': 'Committee Participation Opportunity',
            'message': f'With Rs. {disposable_income:,} surplus, you can safely participate in committees up to Rs. {int(disposable_income * 0.3):,}/month.',
            'savings_potential': int(disposable_income * 0.1)
        })
    
    # Investment advice based on Islamic finance preference
    if profile.get('islamic_finance_pref') == 'Strictly Halal only':
        advice["Investment Opportunities"].append({
            'priority': 'low',
            'title': 'Shariah-Compliant Investments',
            'message': 'Consider Islamic mutual funds, gold investments, or real estate. These align with your Halal preference and offer good returns.',
            'savings_potential': int(disposable_income * 0.15)
        })
    
    # Lifestyle optimization
    if profile['monthly_expenses'] / profile['monthly_income'] > 0.7:
        advice["Lifestyle Optimization"].append({
            'priority': 'high',
            'title': 'Reduce Fixed Expenses',
            'message': 'Your expenses are 70%+ of income. Review subscriptions, utilities, and discretionary spending. Target 50-60% expense ratio.',
            'savings_potential': int(profile['monthly_expenses'] * 0.1)
        })
    
    return advice

def analyze_risk_factors(profile: Dict) -> Dict:
    """Analyze various risk factors"""
    
    risk_factors = {}
    
    # Income stability risk
    if profile['monthly_income'] < 30000:
        risk_factors['Income Stability'] = {
            'level': 'High',
            'description': 'Low income increases financial vulnerability'
        }
    elif profile['monthly_income'] < 50000:
        risk_factors['Income Stability'] = {
            'level': 'Medium', 
            'description': 'Moderate income provides reasonable stability'
        }
    else:
        risk_factors['Income Stability'] = {
            'level': 'Low',
            'description': 'Good income level provides financial stability'
        }
    
    # Debt burden risk
    debt_ratio = (profile['existing_debt'] / (profile['monthly_income'] * 12)) * 100 if profile['monthly_income'] > 0 else 0
    
    if debt_ratio > 40:
        risk_factors['Debt Burden'] = {
            'level': 'High',
            'description': f'Debt is {debt_ratio:.1f}% of annual income - unsustainable level'
        }
    elif debt_ratio > 20:
        risk_factors['Debt Burden'] = {
            'level': 'Medium',
            'description': f'Debt at {debt_ratio:.1f}% of income - manageable but needs attention'
        }
    else:
        risk_factors['Debt Burden'] = {
            'level': 'Low',
            'description': 'Low debt levels provide financial flexibility'
        }
    
    # Emergency preparedness
    emergency_months = profile['current_savings'] / profile['monthly_expenses'] if profile['monthly_expenses'] > 0 else 0
    
    if emergency_months < 3:
        risk_factors['Emergency Preparedness'] = {
            'level': 'High',
            'description': f'Only {emergency_months:.1f} months emergency fund - vulnerable to shocks'
        }
    elif emergency_months < 6:
        risk_factors['Emergency Preparedness'] = {
            'level': 'Medium',
            'description': f'{emergency_months:.1f} months emergency fund - needs improvement'
        }
    else:
        risk_factors['Emergency Preparedness'] = {
            'level': 'Low',
            'description': 'Adequate emergency fund provides good protection'
        }
    
    # Calculate overall risk score
    risk_scores = {'High': 80, 'Medium': 50, 'Low': 20}
    overall_risk = sum(risk_scores.get(factor['level'], 50) for factor in risk_factors.values()) / len(risk_factors)
    
    return {
        'overall_risk_score': int(overall_risk),
        'risk_factors': risk_factors
    }

def get_committee_recommendations_by_risk(risk_analysis: Dict, profile: Dict) -> Dict:
    """Get committee recommendations based on risk profile"""
    
    overall_risk = risk_analysis['overall_risk_score']
    monthly_capacity = max(0, (profile['monthly_income'] - profile['monthly_expenses']) * 0.3)
    
    recommendations = {
        "Low Risk Committees": [],
        "Medium Risk Committees": [],
        "High Risk Committees": []
    }
    
    # Low risk recommendations
    recommendations["Low Risk Committees"].extend([
        {
            'type': 'Small Amount Committee (Rs. 2-5k)',
            'description': 'Perfect for beginners, low commitment, quick turnover',
            'amount': 'Rs. 2,000-5,000',
            'duration': '3-6 months',
            'risk_level': 'Low',
            'recommended': True
        },
        {
            'type': 'Monthly Committee',
            'description': 'Regular monthly payments, predictable schedule',
            'amount': f'Rs. {min(5000, int(monthly_capacity)):,}',
            'duration': '6-12 months',
            'risk_level': 'Low',
            'recommended': overall_risk < 60
        }
    ])
    
    # Medium risk recommendations
    if overall_risk < 70:
        recommendations["Medium Risk Committees"].extend([
            {
                'type': 'Standard Committee (Rs. 10-25k)',
                'description': 'Good balance of risk and returns for stable income',
                'amount': 'Rs. 10,000-25,000',
                'duration': '12-18 months',
                'risk_level': 'Medium',
                'recommended': monthly_capacity > 10000
            },
            {
                'type': 'Bi-Monthly Committee',
                'description': 'Less frequent payments, suitable for irregular income',
                'amount': f'Rs. {min(15000, int(monthly_capacity * 2)):,}',
                'duration': '12-24 months',
                'risk_level': 'Medium',
                'recommended': profile['monthly_income'] > 40000
            }
        ])
    
    # High risk recommendations (only for low-risk profiles)
    if overall_risk < 40:
        recommendations["High Risk Committees"].extend([
            {
                'type': 'Large Amount Committee (Rs. 50k+)',
                'description': 'High returns but requires strong financial position',
                'amount': 'Rs. 50,000+',
                'duration': '18-36 months',
                'risk_level': 'High',
                'recommended': monthly_capacity > 25000 and profile['current_savings'] > 200000
            }
        ])
    
    return recommendations

def generate_budget_recommendations(profile: Dict) -> Dict:
    """Generate AI budget recommendations"""
    
    income = profile['monthly_income']
    
    # Recommended allocation based on financial best practices
    recommended_allocation = {
        'Fixed Expenses': min(profile['monthly_expenses'], income * 0.5),
        'Emergency Savings': income * 0.1,
        'Committee Savings': income * 0.15,
        'Investment/Retirement': income * 0.15,
        'Discretionary': income * 0.1
    }
    
    suggestions = {}
    
    # Expense optimization
    if profile['monthly_expenses'] > income * 0.6:
        suggestions['Expense Reduction'] = {
            'impact': 'high',
            'message': 'Your fixed expenses are too high. Review rent, utilities, and subscriptions. Aim for 50% of income maximum.',
            'savings_potential': int(profile['monthly_expenses'] - (income * 0.5))
        }
    
    # Savings optimization
    current_savings_rate = (income - profile['monthly_expenses']) / income if income > 0 else 0
    if current_savings_rate < 0.2:
        suggestions['Savings Rate'] = {
            'impact': 'high',
            'message': 'Increase your savings rate to at least 20% of income. This provides financial security and growth.',
            'savings_potential': int(income * 0.2 - (income - profile['monthly_expenses']))
        }
    
    # Committee optimization
    user_committees_spending = 0  # Would get from database in real implementation
    if user_committees_spending > income * 0.2:
        suggestions['Committee Spending'] = {
            'impact': 'medium',
            'message': 'Committee commitments should not exceed 20% of income. Consider reducing participation.',
            'savings_potential': int(user_committees_spending - (income * 0.2))
        }
    
    return {
        'recommended_allocation': recommended_allocation,
        'suggestions': suggestions
    }

def get_risk_color(score: int) -> str:
    """Get color for risk score"""
    if score < 30:
        return "#228B22"  # Low risk - Green
    elif score < 60:
        return "#FFD700"  # Medium risk - Yellow
    else:
        return "#DC143C"  # High risk - Red

def show_ai_chatbot_tab():
    """Show AI chatbot in its own tab within AI advice"""
    st.subheader("🤖 Civitas AI Financial Assistant")
    st.markdown("*Get personalized financial advice and committee guidance*")
    
    # Auto-open the chatbot when this tab is accessed
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = True
    else:
        st.session_state.chat_open = True
    
    # Display the chatbot widget in full-screen mode
    show_chatbot_widget()

def show_goal_committees(goal: Dict, monthly_needed: float):
    """Show committees that could help achieve the goal"""
    st.info(f"**Committee Options for: {goal['name']}**")
    
    st.write(f"To reach your goal, you need to save **Rs. {monthly_needed:,.0f}/month**")
    
    # Mock committee suggestions
    committees = [
        {"amount": int(monthly_needed * 0.7), "duration": 12, "type": "Conservative"},
        {"amount": int(monthly_needed), "duration": 8, "type": "Balanced"},
        {"amount": int(monthly_needed * 1.3), "duration": 6, "type": "Aggressive"}
    ]
    
    for committee in committees:
        st.write(f"• **{committee['type']}**: Rs. {committee['amount']:,}/month for {committee['duration']} months")

def show_goal_strategy(goal: Dict, monthly_needed: float):
    """Show strategy recommendations for achieving the goal"""
    st.info(f"**Strategy for: {goal['name']}**")
    
    strategies = [
        f"💰 Save Rs. {monthly_needed:,.0f} monthly in a high-yield savings account",
        f"🏛️ Join a committee with Rs. {int(monthly_needed * 0.8):,} monthly payments",
        f"📈 Invest Rs. {int(monthly_needed * 0.6):,} monthly in Shariah-compliant funds",
        f"🎯 Combine: 50% savings + 50% committee participation"
    ]
    
    for strategy in strategies:
        st.write(f"• {strategy}")
