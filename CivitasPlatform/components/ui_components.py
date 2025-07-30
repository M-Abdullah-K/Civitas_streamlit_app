import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional

def apply_custom_css():
    """Apply enhanced Pakistani-themed CSS styling"""

    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        /* Main container styling with gradient background */
        .stApp {
            background: linear-gradient(135deg, #e6f3f7 0%, #f0f8ff 50%, #ffffff 100%);
            background-attachment: fixed;
            font-family: 'Poppins', sans-serif;
        }

        /* Sidebar styling with glassmorphism effect */
        .css-1d391kg, .css-17eq0hr {
            background: linear-gradient(180deg, rgba(46, 79, 102, 0.9) 0%, rgba(74, 107, 128, 0.9) 100%);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Header styling with enhanced effects */
        .main-header {
            background: linear-gradient(135deg, #1a4d5c 0%, #2e6b7a 50%, #4a8ca3 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 30px;
            margin: 1rem 0 2rem 0;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 
                        0 15px 30px rgba(46, 107, 122, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(20px);
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
            animation: shimmer 3s ease-in-out infinite;
        }

        @keyframes shimmer {
            0%, 100% { transform: translateX(-100%); }
            50% { transform: translateX(100%); }
        }

        /* Responsive design for mobile and tablets */
        @media (max-width: 1024px) {
            .main-header {
                padding: 2rem 1rem;
            }
        }

        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2rem !important;
            }
            .main-header p {
                font-size: 1rem !important;
            }

            /* Fix input field responsiveness */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stNumberInput > div > div > input,
            .stTextArea > div > div > textarea {
                min-width: 200px !important;
                max-width: 100% !important;
                font-size: 16px !important; /* Prevents zoom on iOS */
            }

            /* Mobile column adjustments */
            .element-container {
                margin-bottom: 1rem;
            }
        }

        @media (max-width: 480px) {
            .main-header {
                padding: 1.5rem 1rem;
                margin: 0.5rem 0 1rem 0;
            }
            .main-header h1 {
                font-size: 1.5rem !important;
            }
        }

        /* Enhanced card styling with glassmorphism */
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-left: 4px solid #2e6b7a;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            transition: left 0.5s ease;
        }

        .metric-card:hover::before {
            left: 100%;
        }

        .metric-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border-left-color: #4a8ca3;
        }

        /* Enhanced button styling */
        .stButton > button {
            border-radius: 30px;
            border: none;
            padding: 0.875rem 2rem;
            font-weight: 600;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            background: linear-gradient(135deg, #1a4d5c 0%, #2e6b7a 100%);
            color: white;
            position: relative;
            overflow: hidden;
        }

        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.3s ease;
        }

        .stButton > button:hover::before {
            left: 100%;
        }

        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
        }

        .stButton > button:active {
            transform: translateY(-1px);
        }

        /* Form styling with glassmorphism */
        .stForm {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 3rem;
            border-radius: 25px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Enhanced input styling */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: 15px;
            border: 2px solid rgba(46, 107, 122, 0.3);
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
        }

        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stNumberInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #2e6b7a;
            box-shadow: 0 0 0 3px rgba(46, 107, 122, 0.1);
            transform: translateY(-2px);
        }

        /* Enhanced message styling */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border: none;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .stSuccess {
            background: linear-gradient(135deg, rgba(72, 187, 120, 0.9), rgba(56, 178, 172, 0.9));
            color: white;
        }

        .stError {
            background: linear-gradient(135deg, rgba(245, 101, 101, 0.9), rgba(220, 38, 127, 0.9));
            color: white;
        }

        .stWarning {
            background: linear-gradient(135deg, rgba(246, 173, 85, 0.9), rgba(255, 154, 0, 0.9));
            color: white;
        }

        .stInfo {
            background: linear-gradient(135deg, rgba(26, 77, 92, 0.9), rgba(46, 107, 122, 0.9));
            color: white;
        }

        /* Enhanced table styling */
        .dataframe {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.95);
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 0.5rem;
            backdrop-filter: blur(10px);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 15px;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #1a4d5c, #2e6b7a) !important;
            color: white !important;
        }

        /* Metric styling */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }

        [data-testid="metric-container"]:hover {
            transform: translateY(-5px);
        }

        /* Container styling */
        .element-container {
            transition: all 0.3s ease;
        }

        /* Loading animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .loading {
            animation: pulse 2s ease-in-out infinite;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #1a4d5c, #2e6b7a);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #0f3d4a, #245561);
        }

        /* Chatbot Widget Styles */
        .chatbot-widget {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 9999 !important;
            background: linear-gradient(135deg, #1a4d5c, #2e6b7a) !important;
            border-radius: 50% !important;
            width: 60px !important;
            height: 60px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            box-shadow: 0 4px 20px rgba(26, 77, 92, 0.4) !important;
            transition: all 0.3s ease !important;
        }

        .chatbot-widget:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 6px 25px rgba(26, 77, 92, 0.6) !important;
        }

        .chat-popup {
            position: fixed !important;
            bottom: 100px !important;
            right: 30px !important;
            width: 350px !important;
            max-height: 500px !important;
            background: white !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2) !important;
            z-index: 9998 !important;
            border: 1px solid rgba(26, 77, 92, 0.2) !important;
            overflow: hidden !important;
        }

        @media (max-width: 768px) {
            .chat-popup {
                width: 300px !important;
                max-height: 400px !important;
                right: 20px !important;
                bottom: 90px !important;
            }
            
            .chatbot-widget {
                bottom: 20px !important;
                right: 20px !important;
                width: 50px !important;
                height: 50px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)

def show_header():
    """Display the enhanced main header with Civitas logo and Pakistani cultural theme"""

    # Try to display logo, fallback to custom logo if not found
    try:
        # Use proper image path that works in Streamlit
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            # Display the new logo using st.image for better compatibility
            st.image("assets/civitas_new_logo.png", width=150, caption=None)

        # Enhanced header text with visible styling
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2E4F66, #4A6B80, #FFD700); padding: 2rem; border-radius: 25px; margin: 1rem 0 2rem 0; text-align: center; box-shadow: 0 12px 24px rgba(46, 79, 102, 0.25); position: relative; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.1);">
            <h1 style="margin: 0; font-size: 3rem; font-weight: bold; color: white !important; text-shadow: 3px 3px 6px rgba(0,0,0,0.7);">
                🏛️ Civitas
            </h1>
            <p style="margin: 0.5rem 0; font-size: 1.4rem; color: white !important; font-weight: 600; text-shadow: 2px 2px 4px rgba(0,0,0,0.6);">
                Digital Committee Platform for Pakistan
            </p>
            <p style="font-size: 1.1rem; color: white !important; margin-top: 0.5rem; font-weight: 500; opacity: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.6);">
                🌙 Shariah-Compliant • 🤝 Community-Driven • 🛡️ Trustworthy
            </p>
        </div>
        """, unsafe_allow_html=True)

    except:
        # Enhanced fallback header with better logo design and visible text
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a4d5c, #2e6b7a, #b8860b); padding: 2rem; border-radius: 25px; margin: 1rem 0 2rem 0; text-align: center; box-shadow: 0 12px 24px rgba(26, 77, 92, 0.25); position: relative; overflow: hidden; border: 1px solid rgba(184, 134, 11, 0.3);">
            <div class="logo-container">
                <div class="enhanced-logo-symbol">
                    <div class="logo-cross">
                        <div class="logo-segment blue-segment"></div>
                        <div class="logo-segment gold-segment"></div>
                        <div class="logo-segment blue-segment"></div>
                        <div class="logo-segment gold-segment"></div>
                    </div>
                </div>
                <h1 style="margin-top: 1.5rem; font-size: 3rem; font-weight: bold; color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                    Civitas
                </h1>
            </div>
            <p style="margin: 1rem 0; font-size: 1.4rem; color: white !important; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                Digital Committee Platform for Pakistan
            </p>
            <p style="font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem; color: white !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                🌙 Shariah-Compliant • 🤝 Community-Driven • 🛡️ Trustworthy
            </p>
        </div>
        <style>
            .logo-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 1rem;
            }
            .enhanced-logo-symbol {
                width: 100px;
                height: 100px;
                position: relative;
                margin-bottom: 1rem;
                background: radial-gradient(circle, rgba(255,215,0,0.2), rgba(46,79,102,0.2));
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            }
            .logo-cross {
                width: 80px;
                height: 80px;
                position: relative;
                transform: rotate(45deg);
            }
            .logo-segment {
                position: absolute;
                width: 35px;
                height: 35px;
                border-radius: 50%;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                transition: transform 0.3s ease;
            }
            .enhanced-logo-symbol:hover .logo-segment {
                transform: scale(1.1);
            }
            .blue-segment {
                background: linear-gradient(45deg, #2E4F66, #4A6B80);
            }
            .gold-segment {
                background: linear-gradient(45deg, #FFD700, #DAA520);
            }
            .logo-segment:nth-child(1) { top: 0; left: 22.5px; }
            .logo-segment:nth-child(2) { top: 22.5px; right: 0; }
            .logo-segment:nth-child(3) { bottom: 0; left: 22.5px; }
            .logo-segment:nth-child(4) { top: 22.5px; left: 0; }
        </style>
        """, unsafe_allow_html=True)

def create_metric_card(title: str, value: str, subtitle: str = "", color_scheme: str = "blue"):
    """Create an enhanced metric card with animations"""

    color_schemes = {
        "blue": "linear-gradient(135deg, #2E4F66, #4A6B80)",
        "gold": "linear-gradient(135deg, #FFD700, #DAA520)",
        "teal": "linear-gradient(135deg, #20B2AA, #48D1CC)",
        "purple": "linear-gradient(135deg, #9370DB, #BA55D3)",
        "green": "linear-gradient(135deg, #228B22, #32CD32)"  # Keep for cultural elements
    }

    background = color_schemes.get(color_scheme, color_schemes["blue"])

    return st.markdown(f"""
    <div style="background: {background}; color: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.15); transition: transform 0.3s ease; margin: 0.5rem 0;">
        <h2 style="margin: 0; color: white; font-size: 2rem;">{value}</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem; font-weight: 600;">{title}</p>
        {f'<p style="margin: 0; opacity: 0.7; font-size: 0.9rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_committee_card(committee: Dict[str, Any], user_role: str = "member", 
                         show_actions: bool = True, member_position: Optional[int] = None):
    """Create an enhanced committee card with Pakistani styling using Streamlit components"""

    # Status color mapping
    status_colors = {
        'active': '#228B22',
        'paused': '#FFA500', 
        'completed': '#20B2AA',
        'cancelled': '#DC143C'
    }

    status_color = status_colors.get(committee.get('status', 'active'), '#228B22')
    progress_percentage = (committee.get('current_members', 0) / committee.get('total_members', 1)) * 100

    # Use Streamlit container with border styling
    with st.container():
        # Header with status - responsive layout
        col_header1, col_header2 = st.columns([4, 1])
        with col_header1:
            st.markdown(f"### 🏛️ {committee.get('title', 'Unknown Committee')}")
            description = committee.get('description', 'No description provided')
            if len(description) > 100:
                description = description[:100] + "..."
            st.markdown(f"*{description}*")
        with col_header2:
            status = committee.get('status', 'active').upper()
            if status == 'ACTIVE':
                st.success(f"✅ {status}")
            elif status == 'PAUSED':
                st.warning(f"⏸️ {status}")
            elif status == 'COMPLETED':
                st.info(f"🏁 {status}")
            else:
                st.error(f"❌ {status}")

        # Committee metrics using responsive columns
        # Use 2 columns on mobile, 3-4 on desktop
        metrics_cols = []
        if member_position:
            # Show 2 columns on mobile, 4 on desktop
            if st._get_option('client.isEmbedded'):  # Mobile detection workaround
                metrics_cols = st.columns(2)
            else:
                metrics_cols = st.columns([1, 1, 1, 1])
        else:
            # Show 2 columns on mobile, 3 on desktop
            metrics_cols = st.columns([1, 1, 1])

        # First row of metrics
        with metrics_cols[0]:
            st.metric(
                label="💰 Amount",
                value=f"Rs. {committee.get('monthly_amount', 0):,}",
                help="Monthly payment amount"
            )

        with metrics_cols[1]:
            st.metric(
                label="👥 Members",
                value=f"{committee.get('current_members', 0)}/{committee.get('total_members', 0)}",
                help="Current members vs total capacity"
            )
            # Progress bar for member fill rate
            st.progress(min(progress_percentage / 100, 1.0))

        # Second row or continue first row based on available space
        if len(metrics_cols) >= 3:
            with metrics_cols[2]:
                st.metric(
                    label="⏰ Duration",
                    value=f"{committee.get('duration', 0)} months",
                    help="Committee duration"
                )

        if len(metrics_cols) >= 4 and member_position:
            with metrics_cols[3]:
                st.metric(
                    label="📍 Position",
                    value=f"#{member_position}",
                    help="Your position in payout queue"
                )

        # If we don't have enough columns, show remaining metrics in a new row
        if len(metrics_cols) < 3:
            col_extra1, col_extra2 = st.columns(2)
            with col_extra1:
                st.metric(
                    label="⏰ Duration",
                    value=f"{committee.get('duration', 0)} months",
                    help="Committee duration"
                )
            if member_position:
                with col_extra2:
                    st.metric(
                        label="📍 Position",
                        value=f"#{member_position}",
                        help="Your position in payout queue"
                    )

        # Committee details - responsive
        st.markdown("---")
        col_details1, col_details2 = st.columns(2)

        with col_details1:
            st.markdown(f"📂 **Category:** {committee.get('category', 'General')}")
            st.markdown(f"🔄 **Payment:** {committee.get('payment_frequency', 'monthly').title()}")

        with col_details2:
            created_date = committee.get('created_date', 'Unknown')
            if hasattr(created_date, 'strftime'):
                created_date = created_date.strftime('%Y-%m-%d')
            st.markdown(f"📅 **Created:** {created_date}")
            # Role indicator
            role_text = '👑 Admin' if user_role == 'admin' else '👤 Member'
            st.markdown(f"**Role:** {role_text}")

        st.markdown("---")

def create_status_badge(status: str, custom_text: str = None):
    """Create a status badge with appropriate styling"""

    display_text = custom_text or status

    status_styles = {
        'paid': 'background: #228B22; color: white;',
        'unpaid': 'background: #DC143C; color: white;',
        'pending': 'background: #FFA500; color: white;',
        'active': 'background: #228B22; color: white;',
        'completed': 'background: #20B2AA; color: white;',
        'admin': 'background: #FFD700; color: #333;',
        'member': 'background: #E6E6FA; color: #4B0082;'
    }

    style = status_styles.get(status.lower(), 'background: #666; color: white;')

    return st.markdown(f"""
    <span class="status-badge" style="{style}">
        {display_text.upper()}
    </span>
    """, unsafe_allow_html=True)

def create_trust_score_display(score: int, size: str = "normal"):
    """Create an enhanced trust score display with animations"""

    # Determine trust level and color
    if score >= 95:
        level = "Excellent"
        color = "#228B22"
        icon = "🌟"
    elif score >= 85:
        level = "Very Good"  
        color = "#32CD32"
        icon = "⭐"
    elif score >= 75:
        level = "Good"
        color = "#FFD700"
        icon = "✨"
    elif score >= 60:
        level = "Fair"
        color = "#FFA500"
        icon = "💫"
    else:
        level = "Needs Improvement"
        color = "#DC143C"
        icon = "📈"

    if size == "large":
        font_size = "2rem"
        padding = "1.5rem 2rem"
    else:
        font_size = "1.2rem"
        padding = "0.8rem 1.5rem"

    css_animation = """
    <style>
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
    </style>
    """

    return st.markdown(f"""
    <div style="background: linear-gradient(45deg, {color}, {color}CC); color: white; 
                padding: {padding}; border-radius: 25px; text-align: center; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.2); margin: 1rem 0;
                display: inline-block; position: relative; overflow: hidden;">
        <span style="font-size: {font_size}; font-weight: bold;">
            {icon} {score}% - {level}
        </span>
        <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%; 
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                    animation: shimmer 2s infinite;"></div>
    </div>
    {css_animation}
    """, unsafe_allow_html=True)

def show_loading_state(message: str = "Loading..."):
    """Show an enhanced loading state with Pakistani styling"""

    return st.markdown(f"""
    <div style="text-align: center; padding: 3rem; color: #228B22;">
        <div class="loading-spinner" style="margin: 0 auto 1rem auto;"></div>
        <h4 style="color: #228B22; margin: 0;">{message}</h4>
        <p style="color: #666; margin: 0.5rem 0;">Please wait while we process your request...</p>
    </div>
    """, unsafe_allow_html=True)

def create_progress_bar(current: int, total: int, label: str = "", color: str = "#228B22"):
    """Create an enhanced progress bar with Pakistani styling"""

    percentage = (current / total) * 100 if total > 0 else 0

    progress_css = """
    <style>
        @keyframes progress-shine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
    </style>
    """

    return st.markdown(f"""
    <div style="margin: 1rem 0;">
        {f'<p style="margin-bottom: 0.5rem; color: #333; font-weight: 600;">{label}</p>' if label else ''}
        <div style="background: #f0f0f0; border-radius: 10px; height: 12px; position: relative; overflow: hidden;">
            <div style="background: linear-gradient(90deg, {color}, {color}CC); 
                        border-radius: 10px; height: 12px; width: {percentage}%; 
                        transition: width 0.5s ease; position: relative;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                            animation: progress-shine 1.5s infinite;"></div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.9rem; color: #666;">
            <span>{current} of {total}</span>
            <span>{percentage:.1f}%</span>
        </div>
    </div>
    {progress_css}
    """, unsafe_allow_html=True)

def create_notification_card(title: str, message: str, notification_type: str = "info", 
                           timestamp: str = None, show_action: bool = False):
    """Create a notification card with Pakistani styling"""

    type_styles = {
        'success': {'color': '#228B22', 'bg': '#d4edda', 'icon': '✅'},
        'error': {'color': '#DC143C', 'bg': '#f8d7da', 'icon': '❌'},
        'warning': {'color': '#FFA500', 'bg': '#fff3cd', 'icon': '⚠️'},
        'info': {'color': '#20B2AA', 'bg': '#d1ecf1', 'icon': 'ℹ️'}
    }

    style = type_styles.get(notification_type, type_styles['info'])

    return st.markdown(f"""
    <div style="background: {style['bg']}; border-left: 4px solid {style['color']}; 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: start; gap: 1rem;">
            <span style="font-size: 1.5rem;">{style['icon']}</span>
            <div style="flex: 1;">
                <h5 style="margin: 0; color: {style['color']};">{title}</h5>
                <p style="margin: 0.5rem 0; color: #333; line-height: 1.4;">{message}</p>
                {f'<small style="color: #666;">{timestamp}</small>' if timestamp else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_feature_highlight(icon: str, title: str, description: str, color: str = "#228B22"):
    """Create a feature highlight card for showcasing platform benefits"""

    return st.markdown(f"""
    <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center;
                border: 2px solid {color}20; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transition: transform 0.3s ease; margin: 1rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <h4 style="color: {color}; margin: 0 0 1rem 0;">{title}</h4>
        <p style="color: #666; margin: 0; line-height: 1.5;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

def show_empty_state(title: str, message: str, action_text: str = None, action_key: str = None):
    """Show an empty state with Pakistani cultural elements"""

    empty_state_html = f"""
    <div style="text-align: center; padding: 4rem 2rem; color: #666;">
        <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.6;">🏛️</div>
        <h3 style="color: #228B22; margin-bottom: 1rem;">{title}</h3>
        <p style="margin-bottom: 2rem; line-height: 1.5; max-width: 500px; margin-left: auto; margin-right: auto;">
            {message}
        </p>
    </div>
    """

    st.markdown(empty_state_html, unsafe_allow_html=True)

    if action_text and action_key:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            return st.button(action_text, key=action_key, use_container_width=True, type="primary")

    return False

def create_stats_grid(stats: List[Dict[str, Any]], columns: int = 4):
    """Create a responsive stats grid with enhanced styling"""

    cols = st.columns(columns)

    for i, stat in enumerate(stats):
        with cols[i % columns]:
            color_scheme = stat.get('color_scheme', 'green')
            create_metric_card(
                title=stat.get('title', ''),
                value=stat.get('value', ''),
                subtitle=stat.get('subtitle', ''),
                color_scheme=color_scheme
            )

def show_success_message(message: str, auto_hide: bool = True):
    """Show a success message with enhanced styling and optional auto-hide"""

    slide_css = """
    <style>
        @keyframes slideIn {
            from { transform: translateY(-20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
    """

    success_html = f"""
    <div style="background: linear-gradient(135deg, #d4edda, #c3e6cb); 
                border-left: 6px solid #228B22; padding: 1.5rem; border-radius: 15px; 
                margin: 1rem 0; box-shadow: 0 4px 12px rgba(34, 139, 34, 0.2);
                animation: slideIn 0.5s ease;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="font-size: 2rem;">🎉</span>
            <div>
                <h5 style="margin: 0; color: #228B22;">Success!</h5>
                <p style="margin: 0; color: #155724;">{message}</p>
            </div>
        </div>
    </div>
    {slide_css}
    """

    return st.markdown(success_html, unsafe_allow_html=True)