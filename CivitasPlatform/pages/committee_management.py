import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database.db_manager import DatabaseManager

def show_committee_management(db: DatabaseManager, user_id: str, user_role: str):
    """Display committee management interface with role-based permissions"""

    st.title("🏛️ Committee Management")

    # Create tabs based on user role
    if user_role == 'admin':
        tab1, tab2, tab3 = st.tabs(["📋 My Committees", "➕ Create Committee", "🔍 Browse Committees"])
    else:
        # Members can only see their committees and browse/join others
        tab1, tab3 = st.tabs(["📋 My Committees", "🔍 Browse Committees"])
        tab2 = None

    with tab1:
        show_my_committees(db, user_id, user_role)

    if tab2:  # Only available for admins
        with tab2:
            show_create_committee(db, user_id, user_role)

    with tab3:
        show_browse_committees(db, user_id)

def show_my_committees(db: DatabaseManager, user_id: str, user_role: str):
    """Show user's committees with enhanced UI"""

    st.subheader("📋 My Committees")

    user_committees = db.get_user_committees(user_id)

    if not user_committees:
        st.info("🎯 You haven't joined any committees yet.")

        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🔍 Browse Committees", use_container_width=True, type="primary"):
                st.session_state.current_page = "browse_committees"
                st.rerun()
        return

    # Committee overview metrics
    col1, col2, col3, col4 = st.columns(4)

    total_committees = len(user_committees)
    active_committees = len([c for c in user_committees if c.status == 'active'])
    total_contribution = sum([c.monthly_amount for c in user_committees])
    admin_committees = len([c for c in user_committees if c.admin_id == user_id])

    with col1:
        st.metric("Total Committees", total_committees)
    with col2:
        st.metric("Active Committees", active_committees)
    with col3:
        st.metric("Monthly Contribution", f"Rs. {total_contribution:,}")
    with col4:
        st.metric("Admin Of", admin_committees)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display committees
    for committee in user_committees:
        with st.container():
            # Determine user's role in this committee
            user_committee_role = "Admin" if committee.admin_id == user_id else "Member"
            member_position = db.get_member_position_in_committee(committee.id, user_id)

            # Calculate progress and status
            progress_percentage = (committee.current_members / committee.total_members) * 100

            # Status color coding
            status_colors = {
                'active': '#228B22',
                'paused': '#FFA500', 
                'completed': '#20B2AA',
                'cancelled': '#DC143C'
            }

            status_color = status_colors.get(committee.status, '#666666')

            # Create committee card using native Streamlit components
            col1, col2 = st.columns([4, 1])

            with col1:
                # Add committee type indicator
                committee_type_icon = "🔒" if committee.committee_type == 'private' else "🌐"
                committee_type_text = "Private" if committee.committee_type == 'private' else "Public"

                st.markdown(f"### {committee_type_icon} {committee.title}")
                if committee.description:
                    st.markdown(f"*{committee.description}*")
                st.markdown(f"**Type:** {committee_type_text}")

            with col2:
                if committee.status == 'active':
                    st.success(committee.status.upper())
                elif committee.status == 'paused':
                    st.warning(committee.status.upper())
                else:
                    st.info(committee.status.upper())

            # Committee metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label="💰 Monthly Amount",
                    value=f"Rs. {committee.monthly_amount:,}",
                    delta=None
                )

            with col2:
                st.metric(
                    label="👥 Members", 
                    value=f"{committee.current_members}/{committee.total_members}",
                    delta=f"{progress_percentage:.1f}% filled"
                )

            with col3:
                st.metric(
                    label="⏰ Duration",
                    value=f"{committee.duration} months"
                )

            with col4:
                st.metric(
                    label="📍 Your Position",
                    value=f"#{member_position}"
                )

            # Additional info
            col1, col2, col3 = st.columns(3)

            with col1:
                if user_committee_role == "Admin":
                    st.markdown("**Role:** 👑 Admin")
                else:
                    st.markdown("**Role:** 👤 Member")

            with col2:
                st.markdown(f"**Payment:** 🔄 {committee.payment_frequency.title()}")

            with col3:
                st.markdown(f"**Created:** 📅 {committee.created_date.strftime('%Y-%m-%d')}")

            st.markdown("---")

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button(f"📊 View Details", key=f"details_{committee.id}", use_container_width=True):
                    st.session_state.selected_committee = committee.id
                    if user_committee_role == "Admin":
                        st.session_state.current_page = "admin_dashboard"
                    else:
                        st.session_state.current_page = "member_dashboard"
                    st.rerun()

            with col2:
                if st.button(f"💰 Make Payment", key=f"payment_{committee.id}", use_container_width=True, type="primary"):
                    show_payment_modal(committee)

            with col3:
                if user_committee_role == "Admin":
                    if st.button(f"👑 Manage", key=f"manage_{committee.id}", use_container_width=True):
                        st.session_state.selected_committee = committee.id
                        st.session_state.current_page = "admin_dashboard"
                        st.rerun()
                else:
                    if st.button(f"📞 Contact Admin", key=f"contact_{committee.id}", use_container_width=True):
                        st.info("Admin contact functionality would be implemented here")

            with col4:
                if committee.status == 'active' and user_committee_role != "Admin":
                    if st.button(f"🚪 Leave", key=f"leave_{committee.id}", use_container_width=True, type="secondary"):
                        show_leave_committee_modal(committee)

            st.markdown("---")

    # Invitation management for private committees (only for admins)
    if user_role == 'admin':
        admin_committees = [c for c in user_committees if c.admin_id == user_id and c.committee_type == 'private']

        if admin_committees:
            st.subheader("📨 Private Committee Invitations")

            # Committee selector for invitation management
            committee_options = {f"{c.title} ({c.current_members}/{c.total_members} members)": c for c in admin_committees}

            if committee_options:
                selected_committee_title = st.selectbox(
                    "Select Private Committee to Manage Invitations",
                    list(committee_options.keys()),
                    key="invitation_committee_selector"
                )

                selected_committee = committee_options[selected_committee_title]

                # Send new invitations
                with st.expander("➕ Send New Invitation", expanded=False):
                    st.markdown("### 👥 Invite Members to Private Committee")

                    # Get all users for invitation
                    available_users = db.get_all_users_for_invitation(user_id)

                    if available_users:
                        # Search functionality
                        search_term = st.text_input(
                            "🔍 Search Users", 
                            placeholder="Type username to search...",
                            help="Search for users by username"
                        )

                        # Filter users based on search term
                        if search_term:
                            filtered_users = [
                                user for user in available_users 
                                if search_term.lower() in user['username'].lower()
                            ]
                        else:
                            filtered_users = available_users

                        if filtered_users:
                            st.markdown(f"**Found {len(filtered_users)} user(s)**")

                            # Display users in a nice format
                            for user in filtered_users:
                                with st.container():
                                    col1, col2, col3 = st.columns([2, 1, 1])

                                    with col1:
                                        st.write(f"👤 **{user['username']}**")

                                    with col2:
                                        st.write(f"🎯 Trust: {user['trust_score']}%")

                                    with col3:
                                        if st.button(f"📤 Invite", key=f"invite_{user['id']}", use_container_width=True):
                                            # Show invitation form for this user
                                            st.session_state[f'show_invite_form_{user["id"]}'] = True
                                            st.rerun()

                            # Show invitation forms for selected users
                            for user in filtered_users:
                                if st.session_state.get(f'show_invite_form_{user["id"]}', False):
                                    with st.form(f"invite_form_{user['id']}"):
                                        st.markdown(f"### 📨 Send Invitation to **{user['username']}**")

                                        # Committee selection within the form
                                        committee_options_form = {f"{c.title} ({c.current_members}/{c.total_members} members)": c for c in admin_committees}
                                        
                                        selected_committee_for_invite = st.selectbox(
                                            "📋 Select Committee to Invite To",
                                            list(committee_options_form.keys()),
                                            help="Choose which private committee to invite this user to",
                                            key=f"committee_select_{user['id']}"
                                        )

                                        invitation_message = st.text_area(
                                            "Personal Message (Optional)",
                                            placeholder="Add a personal message to make your invitation more appealing...",
                                            help="This message will be sent along with the invitation",
                                            key=f"message_{user['id']}"
                                        )

                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if st.form_submit_button("📤 Send Invitation", use_container_width=True, type="primary"):
                                                selected_committee_obj = committee_options_form[selected_committee_for_invite]
                                                success = db.send_committee_invitation(
                                                    selected_committee_obj.id, 
                                                    user['id'], 
                                                    user_id,
                                                    invitation_message
                                                )

                                                if success:
                                                    st.success(f"✅ Invitation sent to {user['username']} for '{selected_committee_obj.title}'!")
                                                    # Clear the form state
                                                    if f'show_invite_form_{user["id"]}' in st.session_state:
                                                        del st.session_state[f'show_invite_form_{user["id"]}']
                                                    st.rerun()
                                                else:
                                                    st.error("❌ Failed to send invitation. User may already be invited or in committee.")

                                        with col2:
                                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                                # Clear the form state
                                                if f'show_invite_form_{user["id"]}' in st.session_state:
                                                    del st.session_state[f'show_invite_form_{user["id"]}']
                                                st.rerun()
                        else:
                            st.warning("🔍 No users found matching your search.")
                            if search_term:
                                st.info("💡 Try a different search term or clear the search to see all users.")
                    else:
                        st.info("📭 No other users found in the database to invite.")
                        st.write("💡 To test invitations:")
                        st.write("• Register additional users through the signup process")
                        st.write("• Have other people create accounts on the platform")

                # Show existing invitations
                st.markdown("### 📋 Invitation Status")

                committee_invitations = db.get_committee_invitations(selected_committee.id)

                if committee_invitations:
                    for invitation in committee_invitations:
                        with st.container():
                            # Status color coding
                            status_colors = {
                                'pending': '#FFA500',
                                'accepted': '#228B22',
                                'rejected': '#DC143C',
                                'cancelled': '#808080'
                            }

                            status_color = status_colors.get(invitation['status'], '#666666')
                            status_icon = {
                                'pending': '⏳',
                                'accepted': '✅',
                                'rejected': '❌',
                                'cancelled': '🚫'
                            }.get(invitation['status'], '❓')

                            # Use Streamlit native components instead of HTML
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"**👤 {invitation['invited_username']}**")
                                    st.caption(f"📅 Invited: {invitation['invitation_date'].strftime('%Y-%m-%d %H:%M')}")
                                    if invitation['response_date']:
                                        st.caption(f"📝 Responded: {invitation['response_date'].strftime('%Y-%m-%d %H:%M')}")
                                
                                with col2:
                                    if invitation['status'] == 'pending':
                                        st.warning(f"⏳ {invitation['status'].title()}")
                                    elif invitation['status'] == 'accepted':
                                        st.success(f"✅ {invitation['status'].title()}")
                                    elif invitation['status'] == 'rejected':
                                        st.error(f"❌ {invitation['status'].title()}")
                                    else:
                                        st.info(f"🚫 {invitation['status'].title()}")
                                
                                st.markdown("---")
                else:
                    st.info("📭 No invitations sent yet. Use the form above to invite members.")

    

def show_create_committee(db: DatabaseManager, user_id: str, user_role: str):
    """Show committee creation form with role-based permissions"""

    st.subheader("➕ Create New Committee")

    if user_role != 'admin':
        st.info("ℹ️ As a member, you can create public committees. Only administrators can create private committees.")
        committee_type_options = ["public"]
    else:
        st.info("ℹ️ As an admin, you can create both public and private committees.")
        committee_type_options = ["public", "private"]

    with st.form("create_committee_form", clear_on_submit=False):
        st.markdown("### 📋 Committee Details")

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Committee Title *", placeholder="Enter committee name")
            monthly_amount = st.number_input("Monthly Amount (PKR) *", 
                                           min_value=1000, 
                                           max_value=100000,
                                           value=5000, 
                                           step=500,
                                           help="Amount each member pays per cycle")
            total_members = st.number_input("Total Members *", 
                                          min_value=2, 
                                          max_value=50, 
                                          value=10,
                                          help="Total number of members in committee")

        with col2:
            duration = st.number_input("Duration (months) *", 
                                     min_value=2, 
                                     max_value=60, 
                                     value=12,
                                     help="How many months the committee will run")

            # Committee type - based on user role
            committee_type = st.selectbox("Committee Type *", 
                                        committee_type_options,
                                        help="Public: Anyone can join, Private: Admin approval required")

            payment_frequency = st.selectbox("Payment Frequency *", 
                                           ["monthly", "bi_monthly"],
                                           help="How often members make payments")

        category = st.selectbox("Category", 
                              ["General", "Business", "Family", "Friends", "Investment", "Education", "Healthcare"],
                              help="Committee category for easy browsing")

        description = st.text_area("Description", 
                                 placeholder="Describe the purpose and goals of this committee...",
                                 help="Provide details about committee purpose, rules, and expectations")

        # Committee rules and terms
        st.markdown("### 📜 Committee Terms")

        col1, col2 = st.columns(2)

        with col1:
            late_payment_penalty = st.number_input("Late Payment Penalty (%)", 
                                                  min_value=0, 
                                                  max_value=10, 
                                                  value=2,
                                                  help="Penalty percentage for late payments")

        with col2:
            grace_period = st.number_input("Grace Period (days)", 
                                         min_value=0, 
                                         max_value=15, 
                                         value=3,
                                         help="Days after due date before penalty applies")

        # Agreement checkboxes
        st.markdown("### ✅ Agreements")

        col1, col2 = st.columns(2)

        with col1:
            terms_agreement = st.checkbox("I agree to the platform terms and conditions *")
            admin_responsibility = st.checkbox("I understand my responsibilities as committee admin *")

        with col2:
            sharia_compliance = st.checkbox("I confirm this committee follows Shariah principles *")
            member_commitment = st.checkbox("I commit to fair and transparent management *")

        # Submit button
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🏛️ Create Committee", 
                                            use_container_width=True, 
                                            type="primary")

        if submitted:
            # Validation
            if not all([title, monthly_amount, total_members, duration]):
                st.error("❌ Please fill all required fields marked with *")
            elif not all([terms_agreement, admin_responsibility, sharia_compliance, member_commitment]):
                st.error("❌ Please accept all required agreements")
            elif len(title.strip()) < 3:
                st.error("❌ Committee title must be at least 3 characters long")
            elif monthly_amount < 1000:
                st.error("❌ Minimum monthly amount is Rs. 1,000")
            elif total_members < 2:
                st.error("❌ Committee must have at least 2 members")
            else:
                # Create committee
                success = db.create_committee(
                    title=title.strip(),
                    description=description.strip() if description else None,
                    monthly_amount=monthly_amount,
                    total_members=total_members,
                    duration=duration,
                    committee_type=committee_type,
                    category=category,
                    payment_frequency=payment_frequency,
                    admin_id=user_id
                )

                if success:
                    st.success(f"✅ Committee '{title}' created successfully!")
                    st.balloons()
                    st.info("📝 You have been automatically added as the first member and admin.")

                    # Show next steps
                    st.markdown("### 🎯 Next Steps:")
                    st.write("1. 📢 Share committee details with potential members")
                    st.write("2. 👥 Monitor member applications (for private committees)")
                    st.write("3. 💰 Set up payment reminders and schedules")
                    st.write("4. 🏆 Manage payouts when committee is full")

                    # Auto-refresh after a delay
                    st.rerun()
                else:
                    st.error("❌ Failed to create committee. Please try again.")

def show_browse_committees(db: DatabaseManager, user_id: str):
    """Show browsable public committees with enhanced filtering"""

    st.subheader("🔍 Browse Public Committees")

    # Get public committees that user hasn't joined
    public_committees = db.get_public_committees_for_user(user_id)

    if not public_committees:
        st.info("🎯 No public committees available to join at the moment.")
        st.markdown("### 💡 What you can do:")
        st.write("• Check back later for new committees")
        st.write("• Ask friends to create committees")
        st.write("• Contact support for assistance")
        return

    # Enhanced filter section
    st.markdown("### 🔧 Filter Options")

    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            min_amount = st.number_input("Min Amount (PKR)", 
                                       value=0, 
                                       step=1000,
                                       help="Minimum monthly payment amount")

        with col2:
            max_amount = st.number_input("Max Amount (PKR)", 
                                       value=50000, 
                                       step=1000,
                                       help="Maximum monthly payment amount")

        with col3:
            category_filter = st.selectbox("Category", 
                                         ["All", "General", "Business", "Family", "Friends", "Investment", "Education", "Healthcare"])

        with col4:
            payment_freq_filter = st.selectbox("Payment Frequency",
                                             ["All", "monthly", "bi_monthly"])

        # Additional filters
        col1, col2, col3 = st.columns(3)

        with col1:
            duration_filter = st.selectbox("Duration", 
                                         ["All", "Short (2-6 months)", "Medium (7-12 months)", "Long (13+ months)"])

        with col2:
            availability_filter = st.selectbox("Availability",
                                             ["All", "Almost Full (90%+)", "Half Full (50-90%)", "Just Started (<50%)"])

        with col3:
            sort_by = st.selectbox("Sort By",
                                 ["Newest First", "Amount (Low to High)", "Amount (High to Low)", "Most Available"])

    # Apply filters
    filtered_committees = apply_committee_filters(
        public_committees, min_amount, max_amount, category_filter, 
        payment_freq_filter, duration_filter, availability_filter
    )

    # Sort committees
    filtered_committees = sort_committees(filtered_committees, sort_by)

    if not filtered_committees:
        st.warning("🔍 No committees match your filter criteria. Try adjusting your filters.")
        return

    # Display results summary
    st.markdown(f"### 📋 Available Committees ({len(filtered_committees)} found)")

    # Display committees in enhanced cards
    for committee in filtered_committees:
        with st.container():
            # Calculate metrics
            fill_percentage = (committee.current_members / committee.total_members) * 100
            estimated_payout = committee.monthly_amount * committee.total_members

            # Determine urgency and status
            if fill_percentage >= 90:
                urgency_color = "#DC143C"
                urgency_text = "🔥 Almost Full!"
            elif fill_percentage >= 70:
                urgency_color = "#FFA500" 
                urgency_text = "⚡ Filling Fast"
            else:
                urgency_color = "#228B22"
                urgency_text = "✅ Available"

            # Committee card header with status
            col_header1, col_header2 = st.columns([3, 1])
            with col_header1:
                # Add committee type indicator
                committee_type_icon = "🔒" if committee.committee_type == 'private' else "🌐"
                committee_type_text = "Private" if committee.committee_type == 'private' else "Public"

                st.markdown(f"### {committee_type_icon} {committee.title}")
                st.markdown(f"*{committee.description or 'No description provided.'}*")
                st.markdown(f"**Type:** {committee_type_text}")
            with col_header2:
                if urgency_color == "#DC143C":
                    st.error(urgency_text)
                elif urgency_color == "#FFA500":
                    st.warning(urgency_text)
                else:
                    st.success(urgency_text)

            # Committee metrics using Streamlit columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label="💰 Monthly Payment",
                    value=f"Rs. {committee.monthly_amount:,}",
                    help="Amount you pay each month"
                )

            with col2:
                st.metric(
                    label="👥 Members",
                    value=f"{committee.current_members}/{committee.total_members}",
                    help="Current members vs total capacity"
                )
                # Progress bar for member fill rate
                st.progress(fill_percentage / 100)

            with col3:
                st.metric(
                    label="⏰ Duration",
                    value=f"{committee.duration} months",
                    help="Committee duration in months"
                )

            with col4:
                st.metric(
                    label="💎 Est. Payout",
                    value=f"Rs. {estimated_payout:,}",
                    help="Estimated total payout"
                )

            # Committee details and badges
            st.markdown("---")
            col_details1, col_details2, col_details3 = st.columns(3)

            with col_details1:
                st.markdown(f"📂 **Category:** {committee.category}")

            with col_details2:
                st.markdown(f"🔄 **Payment:** {committee.payment_frequency.title()}")

            with col_details3:
                st.markdown(f"📅 **Created:** {committee.created_date.strftime('%Y-%m-%d')}")

            # Action buttons
            col1, col2, col3 = st.columns([2, 1, 1])

            with col2:
                if st.button("ℹ️ View Details", key=f"view_{committee.id}", use_container_width=True):
                    show_committee_details_modal(committee)

            with col3:
                if committee.current_members < committee.total_members:
                    if st.button("🚀 Join Committee", key=f"join_{committee.id}", use_container_width=True, type="primary"):
                        if db.join_committee(committee.id, user_id):
                            st.success(f"✅ Successfully joined '{committee.title}'!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Failed to join committee. You may already be a member.")
                else:
                    st.info("Committee Full")

def apply_committee_filters(committees, min_amount, max_amount, category, payment_freq, duration, availability):
    """Apply filters to committee list"""

    filtered = []

    for committee in committees:
        # Amount filter
        if committee.monthly_amount < min_amount or committee.monthly_amount > max_amount:
            continue

        # Category filter
        if category != "All" and committee.category != category:
            continue

        # Payment frequency filter
        if payment_freq != "All" and committee.payment_frequency != payment_freq:
            continue

        # Duration filter
        if duration != "All":
            if duration == "Short (2-6 months)" and not (2 <= committee.duration <= 6):
                continue
            elif duration == "Medium (7-12 months)" and not (7 <= committee.duration <= 12):
                continue
            elif duration == "Long (13+ months)" and committee.duration < 13:
                continue

        # Availability filter
        if availability != "All":
            fill_rate = committee.current_members / committee.total_members
            if availability == "Almost Full (90%+)" and fill_rate < 0.9:
                continue
            elif availability == "Half Full (50-90%)" and not (0.5 <= fill_rate < 0.9):
                continue
            elif availability == "Just Started (<50%)" and fill_rate >= 0.5:
                continue

        filtered.append(committee)

    return filtered

def sort_committees(committees, sort_by):
    """Sort committees based on selected criteria"""

    if sort_by == "Newest First":
        return sorted(committees, key=lambda c: c.created_date, reverse=True)
    elif sort_by == "Amount (Low to High)":
        return sorted(committees, key=lambda c: c.monthly_amount)
    elif sort_by == "Amount (High to Low)":
        return sorted(committees, key=lambda c: c.monthly_amount, reverse=True)
    elif sort_by == "Most Available":
        return sorted(committees, key=lambda c: c.total_members - c.current_members, reverse=True)

    return committees

def show_payment_modal(committee):
    """Show payment processing modal"""

    with st.expander("💰 Process Payment", expanded=False):
        st.write(f"**Committee:** {committee.title}")
        st.write(f"**Amount:** Rs. {committee.monthly_amount:,}")
        st.write(f"**Payment Frequency:** {committee.payment_frequency.title()}")

        payment_method = st.selectbox("Payment Method", [
            "🏦 Bank Transfer",
            "📱 Mobile Payment (JazzCash/EasyPaisa)",
            "💳 Credit/Debit Card", 
            "💵 Cash Deposit"
        ])

        if st.button("💰 Process Payment", type="primary", use_container_width=True):
            st.success("✅ Payment processing initiated!")
            st.info("You will receive a confirmation shortly.")

def show_leave_committee_modal(committee):
    """Show leave committee confirmation modal"""

    st.warning(f"⚠️ Are you sure you want to leave '{committee.title}'?")
    st.write("**Note:** Leaving may affect your trust score and you'll lose your position in the payout queue.")

    reason = st.selectbox("Reason for leaving", [
        "Financial constraints",
        "Changed circumstances", 
        "Unsatisfied with committee management",
        "Other commitments",
        "Other"
    ])

    if reason == "Other":
        st.text_input("Please specify:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🚪 Confirm Leave", use_container_width=True, type="primary"):
            st.error("❌ Left committee successfully")
            st.rerun()

def show_committee_details_modal(committee):
    """Show detailed committee information modal"""

    st.info(f"**Committee Details: {committee.title}**")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**💰 Monthly Amount:** Rs. {committee.monthly_amount:,}")
        st.write(f"**👥 Members:** {committee.current_members}/{committee.total_members}")
        st.write(f"**⏰ Duration:** {committee.duration} months")
        st.write(f"**📂 Category:** {committee.category}")

    with col2:
        st.write(f"**🔄 Payment Frequency:** {committee.payment_frequency.title()}")
        st.write(f"**📅 Created:** {committee.created_date.strftime('%Y-%m-%d')}")
        st.write(f"**🏆 Estimated Payout:** Rs. {committee.monthly_amount * committee.total_members:,}")
        st.write(f"**📊 Fill Rate:** {(committee.current_members/committee.total_members)*100:.1f}%")

    if committee.description:
        st.write("**📝 Description:**")
        st.write(committee.description)

    st.write("**🎯 How it works:**")
    st.write("1. Join the committee and secure your position")
    st.write("2. Make monthly/bi-monthly payments as scheduled")
    st.write("3. Receive your payout when it's your turn")
    st.write("4. Continue until all members have received payouts")