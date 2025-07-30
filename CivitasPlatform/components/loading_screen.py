
import streamlit as st
import time

def show_loading_screen():
    """Display custom loading screen with spinning Civitas logo"""
    
    # Custom CSS for the loading screen
    st.markdown("""
    <style>
        .loading-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #e6f3f7 0%, #f0f8ff 50%, #ffffff 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            font-family: 'Poppins', sans-serif;
        }
        
        .logo-spinner {
            width: 120px;
            height: 120px;
            margin-bottom: 2rem;
            animation: spin 2s linear infinite;
            filter: drop-shadow(0 8px 16px rgba(46, 79, 102, 0.3));
        }
        
        .logo-fallback {
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, #4A6B80, #5A7B90);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2rem;
            animation: spin 2s linear infinite;
            box-shadow: 0 8px 25px rgba(46, 79, 102, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .new-logo-design {
            position: relative;
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .logo-circle {
            position: relative;
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #4A6B80, #5A7B90);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(74, 107, 128, 0.3);
        }
        
        .yellow-circle {
            position: absolute;
            width: 24px;
            height: 24px;
            background: #FFD700;
            border-radius: 50%;
        }
        
        .circle-top {
            top: 18px;
            left: 18px;
        }
        
        .circle-bottom {
            bottom: 18px;
            right: 18px;
        }
        
        .logo-fallback::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%);
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        @keyframes shimmer {
            0%, 100% { transform: translateX(-100%) translateY(-100%); }
            50% { transform: translateX(100%) translateY(100%); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .loading-text {
            color: #2E4F66;
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            animation: fadeIn 1s ease-out;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .loading-subtitle {
            color: #4A6B80;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            animation: fadeIn 1.5s ease-out;
            opacity: 0.8;
        }
        
        .loading-dots {
            display: flex;
            gap: 0.5rem;
        }
        
        .loading-dot {
            width: 12px;
            height: 12px;
            background: linear-gradient(135deg, #2E4F66, #4A6B80);
            border-radius: 50%;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        .loading-dot:nth-child(2) {
            animation-delay: 0.3s;
        }
        
        .loading-dot:nth-child(3) {
            animation-delay: 0.6s;
        }
        
        .progress-container {
            width: 300px;
            height: 6px;
            background: rgba(46, 79, 102, 0.1);
            border-radius: 10px;
            margin-top: 2rem;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #2E4F66, #4A6B80, #FFD700);
            border-radius: 10px;
            animation: progressLoad 3s ease-out;
        }
        
        @keyframes progressLoad {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
        }
        
        .islamic-pattern {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0.05;
            background-image: 
                radial-gradient(circle at 25% 25%, #2E4F66 2px, transparent 2px),
                radial-gradient(circle at 75% 75%, #FFD700 2px, transparent 2px);
            background-size: 50px 50px;
            background-position: 0 0, 25px 25px;
            animation: patternMove 20s linear infinite;
        }
        
        @keyframes patternMove {
            0% { transform: translateX(0) translateY(0); }
            100% { transform: translateX(50px) translateY(50px); }
        }
        
        @media (max-width: 768px) {
            .logo-spinner, .logo-fallback {
                width: 80px;
                height: 80px;
                margin-bottom: 1.5rem;
            }
            
            .loading-text {
                font-size: 1.5rem;
            }
            
            .loading-subtitle {
                font-size: 1rem;
            }
            
            .progress-container {
                width: 250px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Loading screen HTML
    loading_html = """
    <div class="loading-container">
        <div class="islamic-pattern"></div>
        
        <!-- Try to display actual logo, fallback to styled div -->
        <div id="logo-container">
            <!-- This will be populated by JavaScript -->
        </div>
        
        <div class="loading-text">Civitas</div>
        <div class="loading-subtitle">Digital Committee Platform for Pakistan</div>
        
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
        
        <div class="progress-container">
            <div class="progress-bar"></div>
        </div>
    </div>
    
    <script>
        // Try to load the actual logo image
        function loadLogo() {
            const logoContainer = document.getElementById('logo-container');
            const img = new Image();
            
            img.onload = function() {
                logoContainer.innerHTML = '<img src="assets/civitas_new_logo.png" class="logo-spinner" alt="Civitas Logo">';
            };
            
            img.onerror = function() {
                // Fallback to styled div with modern logo design matching the uploaded logo
                logoContainer.innerHTML = `
                    <div class="logo-fallback">
                        <div class="new-logo-design">
                            <div class="logo-circle">
                                <div class="yellow-circle circle-top"></div>
                                <div class="yellow-circle circle-bottom"></div>
                            </div>
                        </div>
                    </div>`;
            };
            
            img.src = 'assets/civitas_new_logo.png';
        }
        
        // Load logo when page is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadLogo);
        } else {
            loadLogo();
        }
        
        // Loading screen is now controlled by Python/Streamlit
    </script>
    """
    
    # Use HTML component to ensure proper rendering
    st.components.v1.html(loading_html, height=600, scrolling=False)

def show_loading_with_message(message="Loading...", duration=3):
    """Show loading screen with custom message for specified duration"""
    
    loading_placeholder = st.empty()
    
    with loading_placeholder.container():
        show_loading_screen()
        
        # Override the loading message
        st.markdown(f"""
        <script>
            setTimeout(function() {{
                const subtitle = document.querySelector('.loading-subtitle');
                if (subtitle) {{
                    subtitle.textContent = '{message}';
                }}
            }}, 100);
        </script>
        """, unsafe_allow_html=True)
    
    # Wait for specified duration
    time.sleep(duration)
    
    # Clear the loading screen
    loading_placeholder.empty()
