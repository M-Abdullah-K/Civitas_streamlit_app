
import streamlit as st
import random
from datetime import datetime
from typing import Dict, List

class CivitasChatbot:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {}
        self.current_context = None
        self.initialize_knowledge_base()
    
    def initialize_knowledge_base(self):
        """Initialize chatbot knowledge base with contextual responses"""
        self.knowledge_base = {
            "greetings": [
                "Assalam-u-Alaikum! Welcome to Civitas AI Assistant! 🏛️\n\nI'm here to provide personalized financial advice for your committee journey. Civitas is Pakistan's premier digital committee platform that operates on Shariah-compliant principles, helping you achieve your financial goals through community-based savings.\n\n💡 I can help you with:\n• Committee financial analysis\n• Personal budget planning\n• Risk assessment\n• Investment strategies\n• Goal achievement planning\n\nHow can I assist you today? Please share your financial situation or committee details for personalized advice! 😊"
            ],
            "committee_analysis_keywords": ["committee", "position", "monthly", "amount", "continue", "talia", "financial capacity"],
            "financial_planning_keywords": ["income", "budget", "expenses", "family", "age", "strategy", "goals"],
            "general_help_keywords": ["help", "advice", "guidance", "recommend", "suggest"]
        }
    
    def extract_financial_info(self, message: str) -> Dict:
        """Extract financial information from user message"""
        info = {}
        message_lower = message.lower()
        
        # Extract age with multiple patterns
        import re
        age_patterns = [
            r'age[:\s]*(\d+)',
            r'i\s+am\s+(\d+)',
            r'(\d+)\s*years?\s*old',
            r'(\d+)\s*year\s*old',
            r'age\s*is\s*(\d+)'
        ]
        for pattern in age_patterns:
            age_match = re.search(pattern, message_lower)
            if age_match:
                info['age'] = int(age_match.group(1))
                break
        
        # Extract income with more flexible patterns
        income_patterns = [
            r'monthly\s*income[:\s]*pkr?\s*(\d+[,\d]*)',
            r'income[:\s]*pkr?\s*(\d+[,\d]*)',
            r'earn(?:ed)?[:\s]*pkr?\s*(\d+[,\d]*)',
            r'salary[:\s]*pkr?\s*(\d+[,\d]*)',
            r'i\s+earned?\s+(\d+[,\d]*)',
            r'make[:\s]*pkr?\s*(\d+[,\d]*)',
            r'pkr\s*(\d+[,\d]*)'
        ]
        for pattern in income_patterns:
            match = re.search(pattern, message_lower)
            if match:
                income_str = match.group(1).replace(',', '')
                info['monthly_income'] = int(income_str)
                break
        
        # Extract expenses
        expense_patterns = [
            r'expenses?[:\s]*(?:around\s*)?pkr?\s*(\d+[,\d]*)',
            r'spend[:\s]*(?:around\s*)?pkr?\s*(\d+[,\d]*)',
            r'costs?\s*(?:around\s*)?pkr?\s*(\d+[,\d]*)'
        ]
        for pattern in expense_patterns:
            match = re.search(pattern, message_lower)
            if match:
                expense_str = match.group(1).replace(',', '')
                info['monthly_expenses'] = int(expense_str)
                break
        
        # Extract committee details
        committee_match = re.search(r'committee\s*(?:is\s*)?(\w+)', message_lower)
        if committee_match:
            info['committee_name'] = committee_match.group(1)
        
        # Extract committee amounts (k format and direct amounts)
        amount_patterns = [
            r'committee\s+amount\s+is\s+(\d+[,\d]*)',
            r'monthly\s+committee\s+amount\s+is\s+(\d+[,\d]*)',
            r'(\d+)k',
            r'amount[:\s]*(?:pkr?\s*)?(\d+[,\d]*)',
            r'monthly[:\s]*(?:pkr?\s*)?(\d+[,\d]*)'
        ]
        for pattern in amount_patterns:
            amount_match = re.search(pattern, message_lower)
            if amount_match:
                if 'k' in pattern:
                    info['monthly_amount'] = int(amount_match.group(1)) * 1000
                else:
                    amount_str = amount_match.group(1).replace(',', '')
                    info['monthly_amount'] = int(amount_str)
                break
        
        position_match = re.search(r'position\s*(\d+)', message_lower)
        if position_match:
            info['position'] = int(position_match.group(1))
        
        # Check for family status with more patterns
        family_keywords = ['family', 'married', 'wife', 'children', 'kids', 'supporting parents', 'dependents']
        if any(word in message_lower for word in family_keywords):
            info['has_family'] = True
        
        # Check for single status
        if any(word in message_lower for word in ['single', 'unmarried']):
            info['is_single'] = True
        
        return info
    
    def get_response(self, user_message: str) -> str:
        """Generate contextual AI-powered response"""
        user_message_lower = user_message.lower()
        financial_info = self.extract_financial_info(user_message)
        
        # Update user profile with extracted info
        self.user_profile.update(financial_info)
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Check for greeting (only if it's actually a greeting, not just first message)
        if any(greeting in user_message_lower for greeting in ["hello", "hi", "assalam", "salam"]):
            response = self.knowledge_base["greetings"][0]
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # Check for goodbye
        if any(goodbye in user_message_lower for goodbye in ["bye", "goodbye", "thanks", "thank you"]):
            response = "Jazak Allah Khair! It was my pleasure helping you with your financial planning. Remember, consistent committee participation and smart financial planning lead to success. Feel free to ask me anytime for more advice! 🌟\n\nMay Allah bless your financial journey! 🤲"
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # Check if user provided comprehensive information (age, income, goals) - prioritize financial strategy
        has_comprehensive_info = (
            (financial_info.get('age') or 'years' in user_message_lower or 'old' in user_message_lower) and
            (financial_info.get('monthly_income') or 'income' in user_message_lower or 'earn' in user_message_lower) and
            (any(word in user_message_lower for word in ['goal', 'want', 'need', 'strategy', 'investment', 'car', 'house', 'save']))
        )
        
        # If comprehensive info provided, go to financial strategy regardless of keywords
        if has_comprehensive_info:
            response = self.provide_financial_strategy(user_message, financial_info)
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # Analyze committee situation (only if specific committee keywords without comprehensive info)
        if any(keyword in user_message_lower for keyword in self.knowledge_base["committee_analysis_keywords"]) and not has_comprehensive_info:
            response = self.analyze_committee_situation(user_message, financial_info)
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # Financial planning advice (fallback for financial keywords)
        if any(keyword in user_message_lower for keyword in self.knowledge_base["financial_planning_keywords"]):
            response = self.provide_financial_strategy(user_message, financial_info)
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # Goal-related queries
        if any(word in user_message_lower for word in ["goal", "goals", "target", "objective"]):
            response = self.provide_goal_advice(user_message, financial_info)
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # Default contextual response
        response = self.get_contextual_response(user_message, financial_info)
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def analyze_committee_situation(self, message: str, info: Dict) -> str:
        """Provide specific committee analysis"""
        committee_name = info.get('committee_name', 'your committee')
        monthly_amount = info.get('monthly_amount', 0)
        position = info.get('position', 0)
        
        response = f"📊 **Committee Analysis for {committee_name.title()}**\n\n"
        
        if monthly_amount and position:
            # Calculate committee details
            total_amount = monthly_amount * 12  # Assuming 12 members typically
            position_payout = total_amount
            months_to_wait = position - 1
            
            response += f"💰 **Your Committee Details:**\n"
            response += f"• Monthly Contribution: Rs. {monthly_amount:,}\n"
            response += f"• Your Position: #{position}\n"
            response += f"• Expected Payout: Rs. {position_payout:,}\n"
            response += f"• Waiting Period: {months_to_wait} months\n\n"
            
            # Provide specific advice based on position
            if position <= 3:
                response += f"✅ **RECOMMENDATION: CONTINUE**\n\n"
                response += f"🎯 **Why this is a good decision:**\n"
                response += f"• Early position (#{position}) means shorter wait time\n"
                response += f"• You'll receive Rs. {position_payout:,} in just {months_to_wait} months\n"
                response += f"• ROI: You'll get back {position_payout/monthly_amount:.1f}x your monthly contribution\n"
                response += f"• Low risk due to early position\n\n"
                
                if monthly_amount <= 20000:
                    response += f"💡 **Additional Advice:**\n"
                    response += f"• Amount (Rs. {monthly_amount:,}) is manageable for most budgets\n"
                    response += f"• Consider this as forced savings with guaranteed return\n"
                    response += f"• Keep emergency fund separate from committee money\n"
            else:
                response += f"⚠️ **PROCEED WITH CAUTION**\n\n"
                response += f"🤔 **Consider these factors:**\n"
                response += f"• Late position (#{position}) means longer wait\n"
                response += f"• {months_to_wait} months commitment required\n"
                response += f"• Ensure stable income for {months_to_wait} months\n"
        
        else:
            response += "To provide specific analysis, I need more details:\n"
            response += "• What's your monthly committee amount?\n"
            response += "• What position are you in?\n"
            response += "• What's your monthly income?\n"
            response += "• Do you have other financial commitments?\n\n"
            response += "Please share these details for personalized advice!"
        
        return response
    
    def provide_financial_strategy(self, message: str, info: Dict) -> str:
        """Provide financial strategy based on user profile"""
        age = info.get('age', 0)
        income = info.get('monthly_income', 0)
        expenses = info.get('monthly_expenses', 0)
        has_family = info.get('has_family', False)
        is_single = info.get('is_single', False)
        monthly_amount = info.get('monthly_amount', 0)
        position = info.get('position', 0)
        
        # If user mentioned goals, extract them
        message_lower = message.lower()
        goals = []
        if 'car' in message_lower:
            goals.append('car purchase')
        if 'house' in message_lower or 'home' in message_lower:
            goals.append('home purchase')
        if 'investment' in message_lower:
            goals.append('investment strategy')
        
        response = f"💼 **Personalized Financial Strategy**\n\n"
        
        # If we have basic info (age and income), provide advice
        if age or income:
            response += f"👤 **Your Profile:**\n"
            if age:
                response += f"• Age: {age} years\n"
            if income:
                response += f"• Monthly Income: Rs. {income:,}\n"
            if expenses:
                response += f"• Monthly Expenses: Rs. {expenses:,}\n"
            
            family_status = "With Family" if has_family else ("Single" if is_single else "Not specified")
            response += f"• Family Status: {family_status}\n"
            if goals:
                response += f"• Goals: {', '.join(goals).title()}\n"
            response += "\n"
            
            # If committee details provided, analyze them first
            if monthly_amount and position:
                response += f"📊 **Your Current Committee Analysis:**\n"
                response += f"• Monthly Contribution: Rs. {monthly_amount:,}\n"
                response += f"• Your Position: #{position}\n"
                
                # Calculate committee ROI and waiting period
                total_members = 12  # Assume 12 members
                position_payout = monthly_amount * total_members
                months_to_wait = position - 1
                
                response += f"• Expected Payout: Rs. {position_payout:,}\n"
                response += f"• Waiting Period: {months_to_wait} months\n"
                
                # Committee recommendation
                committee_percentage = (monthly_amount / income) * 100 if income > 0 else 0
                if position <= 3 and committee_percentage <= 20:
                    response += f"✅ **EXCELLENT COMMITTEE CHOICE!**\n"
                    response += f"• Early position (#{position}) = Low risk\n"
                    response += f"• Only {committee_percentage:.1f}% of your income\n"
                    response += f"• Great for your car goal!\n\n"
                elif committee_percentage > 30:
                    response += f"⚠️ **Committee amount seems high** ({committee_percentage:.1f}% of income)\n"
                    response += f"• Consider reducing to max 20% of income\n"
                    response += f"• Current safe limit: Rs. {int(income * 0.2):,}\n\n"
                else:
                    response += f"👍 **Good committee choice** ({committee_percentage:.1f}% of income)\n\n"
            
            # Use provided income or estimate if not provided
            working_income = income if income > 0 else 50000  # Default estimate
            disposable_income = working_income - expenses if expenses > 0 else working_income * 0.6
            if monthly_amount:
                disposable_income -= monthly_amount
            
            # Calculate recommended amounts
            if has_family or (age and age > 25 and not is_single):
                safe_committee_amount = working_income * 0.15  # 15% for family person
                emergency_fund = working_income * 6  # 6 months for family
                expense_ratio = 70
                discretionary = 5
            else:
                safe_committee_amount = working_income * 0.25  # 25% for single person
                emergency_fund = working_income * 3  # 3 months for single
                expense_ratio = 50
                discretionary = 20
            
            response += f"🎯 **Recommended Strategy:**\n\n"
            response += f"**1. Emergency Fund First:**\n"
            response += f"• Build Rs. {emergency_fund:,} emergency fund\n"
            response += f"• Keep in savings account (not committee)\n\n"
            
            response += f"**2. Committee Investment:**\n"
            response += f"• Safe monthly limit: Rs. {safe_committee_amount:,.0f}\n"
            response += f"• Start with 1-2 committees maximum\n"
            response += f"• Choose positions 1-4 for lower risk\n\n"
            
            response += f"**3. Portfolio Diversification:**\n"
            if age and age < 30:
                response += f"• You're young - can take moderate risks\n"
                response += f"• Mix early and mid positions\n"
                response += f"• Consider business/investment committees\n"
            elif age:
                response += f"• Focus on safer, early positions\n"
                response += f"• Prioritize stability over high returns\n"
                response += f"• Avoid positions beyond #6\n"
            else:
                response += f"• Start conservative with early positions\n"
                response += f"• Build experience before taking risks\n"
            
            # Specific advice for car goal
            if 'car purchase' in goals:
                response += f"\n**🚗 Car Purchase Strategy:**\n"
                if monthly_amount and position:
                    car_fund_from_committee = monthly_amount * 12  # Expected payout
                    response += f"• Your committee will give you Rs. {car_fund_from_committee:,} in {position-1} months\n"
                    response += f"• This covers a good portion of car down payment\n"
                    response += f"• Save additional Rs. 5,000-10,000 monthly for car expenses\n"
                    response += f"• Consider 2-3 year car financing for the remaining amount\n"
                else:
                    response += f"• For a car, consider joining early position committees\n"
                    response += f"• Target: Rs. 200,000-400,000 down payment\n"
                    response += f"• Monthly car fund: 15-20% of income\n"
                response += "\n"
            
            if working_income > 0:
                response += f"**4. Monthly Budget Breakdown:**\n"
                current_committee_percent = (monthly_amount/working_income)*100 if monthly_amount else (safe_committee_amount/working_income)*100
                response += f"• Committee Investment: {current_committee_percent:.0f}%\n"
                response += f"• Emergency Savings: 10%\n"
                response += f"• Living Expenses: {expense_ratio}%\n"
                response += f"• Discretionary: {discretionary}%\n"
            
            # Add specific advice based on income level
            if income > 0:
                if income >= 100000:
                    response += f"\n**💡 High Income Advice:**\n"
                    response += f"• Consider multiple committees (2-3 max)\n"
                    response += f"• Diversify with different amounts and positions\n"
                    response += f"• Explore investment committees\n"
                elif income >= 50000:
                    response += f"\n**💡 Medium Income Advice:**\n"
                    response += f"• Start with one reliable committee\n"
                    response += f"• Focus on building emergency fund first\n"
                    response += f"• Choose early positions for safety\n"
                else:
                    response += f"\n**💡 Lower Income Advice:**\n"
                    response += f"• Start small with Rs. 5,000-10,000 committees\n"
                    response += f"• Priority: Emergency fund over committees\n"
                    response += f"• Only join if position 1-3 available\n"
            
        else:
            response += "To create your personalized strategy, please share:\n"
            response += "• Your age\n"
            response += "• Monthly income\n"
            response += "• Family situation\n"
            response += "• Current expenses\n"
            response += "• Financial goals\n\n"
            response += "This will help me give you specific, actionable advice!"
        
        return response
    
    def provide_goal_advice(self, message: str, info: Dict) -> str:
        """Provide goal-specific advice"""
        response = "🎯 **Goal Achievement Through Committees**\n\n"
        
        response += "I see you've set financial goals! Here's how to align them with committee strategy:\n\n"
        
        response += "**🏠 For Home/Property Goals:**\n"
        response += "• Use early positions (1-3) for down payment\n"
        response += "• Choose 12-month committees for predictable timing\n"
        response += "• Amount: 15-20% of monthly income\n\n"
        
        response += "**👶 For Family Goals (Marriage/Children):**\n"
        response += "• Plan 6-12 months ahead\n"
        response += "• Multiple small committees better than one large\n"
        response += "• Keep some money liquid for unexpected costs\n\n"
        
        response += "**🚗 For Vehicle Purchase:**\n"
        response += "• Position 1-2 for immediate need\n"
        response += "• Position 6-8 if planning ahead\n"
        response += "• Consider 50% committee, 50% savings\n\n"
        
        response += "**📚 For Education/Skill Development:**\n"
        response += "• Smaller, shorter committees\n"
        response += "• Priority positions for time-sensitive courses\n"
        response += "• Budget 5-10% of income\n\n"
        
        response += "**🤲 For Hajj/Umrah:**\n"
        response += "• Long-term planning (2-3 years)\n"
        response += "• Mid positions acceptable due to timeline\n"
        response += "• Separate committee just for this goal\n\n"
        
        response += "💡 **Pro Tip:** Match committee positions with your goal timeline. Need money soon? Choose early positions. Planning ahead? Mid positions offer better returns!"
        
        return response
    
    def get_contextual_response(self, message: str, info: Dict) -> str:
        """Provide contextual response based on conversation"""
        responses = [
            f"I understand you're looking for specific financial guidance. Let me help you make the best decision for your situation.\n\nTo give you personalized advice, could you share:\n• Your monthly income\n• Current committee details (if any)\n• Your main financial goals\n• Family situation\n\nThis will help me provide tailored recommendations! 💡",
            
            f"Great question! I'm here to provide specific, actionable advice based on your unique situation.\n\nFor the most helpful response, please tell me:\n• What's your current financial situation?\n• Are you considering joining a committee or already in one?\n• What are your main concerns or goals?\n\nThe more details you share, the better advice I can give! 🎯",
            
            f"I want to make sure I give you the most relevant advice for your specific situation.\n\nCould you help me understand:\n• Your monthly budget/income\n• Any existing committee commitments\n• Your risk tolerance and goals\n• Timeline for your financial objectives\n\nWith these details, I can provide much more valuable guidance! 📊"
        ]
        
        return random.choice(responses)

def show_chatbot_widget():
    """Display the floating chatbot widget with enhanced functionality"""
    
    # Initialize chatbot in session state
    if 'civitas_chatbot' not in st.session_state:
        st.session_state.civitas_chatbot = CivitasChatbot()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    
    # Enhanced CSS for better mobile responsiveness
    st.markdown("""
    <style>
        .chat-button {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #1a4d5c, #2e6b7a);
            border-radius: 50%;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(26, 77, 92, 0.4);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
            transition: all 0.3s ease;
        }
        
        .chat-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(26, 77, 92, 0.6);
        }
        
        .chat-window {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            z-index: 999;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid rgba(26, 77, 92, 0.2);
        }
        
        .chat-header {
            background: linear-gradient(135deg, #1a4d5c, #2e6b7a);
            color: white;
            padding: 1rem;
            text-align: center;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1rem 1.25rem;
            border-radius: 20px 20px 5px 20px;
            margin: 0.75rem 0;
            margin-left: 2rem;
            text-align: right;
            word-wrap: break-word;
            box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
        }
        
        .bot-message {
            background: white;
            color: #333;
            padding: 1rem 1.25rem;
            border-radius: 20px 20px 20px 5px;
            margin: 0.75rem 0;
            margin-right: 2rem;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
            line-height: 1.6;
            white-space: pre-line;
        }
        
        .chat-input-area {
            padding: 1rem;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        @media (max-width: 768px) {
            .chat-window {
                width: calc(100vw - 40px);
                height: 70vh;
                right: 20px;
                bottom: 90px;
                left: 20px;
            }
            
            .chat-button {
                bottom: 20px;
                right: 20px;
                width: 55px;
                height: 55px;
                font-size: 20px;
            }
            
            .user-message, .bot-message {
                margin-left: 1rem;
                margin-right: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Chat toggle button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("🤖", key="chat_toggle", help="Open Civitas AI Financial Advisor"):
            st.session_state.chat_open = not st.session_state.chat_open
    
    # Chat window
    if st.session_state.chat_open:
        with st.container():
            st.markdown("""
            <div class="chat-header">
                🏛️ Civitas AI Financial Advisor
            </div>
            """, unsafe_allow_html=True)
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                if not st.session_state.chat_history:
                    # Show welcome message automatically (without adding to history)
                    welcome_message = st.session_state.civitas_chatbot.knowledge_base["greetings"][0]
                    st.markdown(f"""
                    <div class="bot-message">
                        {welcome_message}
                    </div>
                    """, unsafe_allow_html=True)
                
                for message in st.session_state.chat_history:
                    if message['type'] == 'user':
                        st.markdown(f"""
                        <div class="user-message">
                            {message['content'].replace('<', '&lt;').replace('>', '&gt;')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Properly escape HTML content but preserve line breaks
                        escaped_content = message['content'].replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                        st.markdown(f"""
                        <div class="bot-message">
                            {escaped_content}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Chat input
            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_area(
                    "Type your message...", 
                    placeholder="e.g., 'I'm 28, earn 60k monthly, have a family. What committee strategy do you recommend?'",
                    height=68,
                    key="chat_input"
                )
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    send_button = st.form_submit_button("📤 Send", use_container_width=True, type="primary")
                
                if send_button and user_input.strip():
                    # Add user message
                    st.session_state.chat_history.append({
                        'type': 'user',
                        'content': user_input,
                        'timestamp': datetime.now()
                    })
                    
                    # Get bot response
                    bot_response = st.session_state.civitas_chatbot.get_response(user_input)
                    
                    # Add bot response
                    st.session_state.chat_history.append({
                        'type': 'bot',
                        'content': bot_response,
                        'timestamp': datetime.now()
                    })
                    
                    st.rerun()
            
            # Clear chat button
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", key="clear_chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            with col2:
                if st.button("❌ Close", key="close_chat", use_container_width=True):
                    st.session_state.chat_open = False
                    st.rerun()
