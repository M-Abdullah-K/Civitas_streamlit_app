import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import DatabaseManager

def show_data_viewer(db: DatabaseManager):
    """Administrative data viewer for inspecting database contents"""
    
    st.title("🔍 Database Data Viewer")
    st.markdown("*Administrative interface for viewing stored data*")
    
    # Add security check for data viewer mode
    if not st.session_state.get('data_viewer_mode', False):
        st.error("🚫 Access denied. This interface requires data viewer authentication.")
        return
    
    # Data viewing tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Users", 
        "🏛️ Committees", 
        "💰 Payments", 
        "📊 Payouts",
        "🔍 Raw Query"
    ])
    
    with tab1:
        show_users_data(db)
    
    with tab2:
        show_committees_data(db)
    
    with tab3:
        show_payments_data(db)
    
    with tab4:
        show_payouts_data(db)
    
    with tab5:
        show_raw_query_interface(db)

def show_users_data(db: DatabaseManager):
    """Display users data"""
    
    st.subheader("👥 Users Data")
    
    try:
        conn = db.get_connection()
        if conn:
            # Get users data
            query = """
            SELECT id, username, full_name, email, phone, role, cnic, 
                   trust_score, created_date, last_login, is_active
            FROM users 
            ORDER BY created_date DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                st.write(f"**Total Users:** {len(df)}")
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    role_filter = st.selectbox("Filter by Role", 
                                             ["All"] + list(df['role'].unique()),
                                             key="user_role_filter")
                
                with col2:
                    active_filter = st.selectbox("Filter by Status", 
                                               ["All", "Active", "Inactive"],
                                               key="user_active_filter")
                
                with col3:
                    search_term = st.text_input("Search by name/username", 
                                              key="user_search")
                
                # Apply filters
                filtered_df = df.copy()
                
                if role_filter != "All":
                    filtered_df = filtered_df[filtered_df['role'] == role_filter]
                
                if active_filter == "Active":
                    filtered_df = filtered_df[filtered_df['is_active'] == True]
                elif active_filter == "Inactive":
                    filtered_df = filtered_df[filtered_df['is_active'] == False]
                
                if search_term:
                    filtered_df = filtered_df[
                        filtered_df['username'].str.contains(search_term, case=False, na=False) |
                        filtered_df['full_name'].str.contains(search_term, case=False, na=False)
                    ]
                
                # Display data
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Users Data as CSV",
                    data=csv,
                    file_name=f"users_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.info("No users found in database.")
        else:
            st.error("Failed to connect to database.")
            
    except Exception as e:
        st.error(f"Error retrieving users data: {str(e)}")

def show_committees_data(db: DatabaseManager):
    """Display committees data"""
    
    st.subheader("🏛️ Committees Data")
    
    try:
        conn = db.get_connection()
        if conn:
            # Get committees data with admin info
            query = """
            SELECT c.id, c.title, c.description, c.monthly_amount, 
                   c.total_members, c.current_members, c.duration,
                   c.committee_type, c.category, c.payment_frequency,
                   c.status, c.created_date, c.start_date, c.next_payout_date,
                   u.username as admin_username, u.full_name as admin_name
            FROM committees c
            LEFT JOIN users u ON c.admin_id = u.id
            ORDER BY c.created_date DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                st.write(f"**Total Committees:** {len(df)}")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    active_count = len(df[df['status'] == 'active'])
                    st.metric("Active Committees", active_count)
                
                with col2:
                    total_amount = df['monthly_amount'].sum()
                    st.metric("Total Monthly Amount", f"Rs. {total_amount:,}")
                
                with col3:
                    avg_members = df['current_members'].mean()
                    st.metric("Avg Members", f"{avg_members:.1f}")
                
                with col4:
                    public_count = len(df[df['committee_type'] == 'public'])
                    st.metric("Public Committees", public_count)
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status_filter = st.selectbox("Filter by Status", 
                                               ["All"] + list(df['status'].unique()),
                                               key="committee_status_filter")
                
                with col2:
                    type_filter = st.selectbox("Filter by Type", 
                                             ["All"] + list(df['committee_type'].unique()),
                                             key="committee_type_filter")
                
                with col3:
                    category_filter = st.selectbox("Filter by Category", 
                                                 ["All"] + list(df['category'].unique()),
                                                 key="committee_category_filter")
                
                # Apply filters
                filtered_df = df.copy()
                
                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df['status'] == status_filter]
                
                if type_filter != "All":
                    filtered_df = filtered_df[filtered_df['committee_type'] == type_filter]
                
                if category_filter != "All":
                    filtered_df = filtered_df[filtered_df['category'] == category_filter]
                
                # Display data
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Committees Data as CSV",
                    data=csv,
                    file_name=f"committees_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.info("No committees found in database.")
        else:
            st.error("Failed to connect to database.")
            
    except Exception as e:
        st.error(f"Error retrieving committees data: {str(e)}")

def show_payments_data(db: DatabaseManager):
    """Display payments data"""
    
    st.subheader("💰 Payments Data")
    
    try:
        conn = db.get_connection()
        if conn:
            # Get payments data with user and committee info
            query = """
            SELECT p.id, p.amount, p.payment_date, p.due_date, p.status,
                   p.payment_method, p.transaction_id, p.notes,
                   u.username, u.full_name,
                   c.title as committee_title
            FROM payments p
            LEFT JOIN users u ON p.user_id = u.id
            LEFT JOIN committees c ON p.committee_id = c.id
            ORDER BY p.payment_date DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                st.write(f"**Total Payments:** {len(df)}")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_amount = df['amount'].sum()
                    st.metric("Total Amount", f"Rs. {total_amount:,}")
                
                with col2:
                    paid_count = len(df[df['status'] == 'paid'])
                    st.metric("Successful Payments", paid_count)
                
                with col3:
                    pending_count = len(df[df['status'] == 'pending'])
                    st.metric("Pending Payments", pending_count)
                
                with col4:
                    failed_count = len(df[df['status'] == 'failed'])
                    st.metric("Failed Payments", failed_count)
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status_filter = st.selectbox("Filter by Status", 
                                               ["All"] + list(df['status'].unique()),
                                               key="payment_status_filter")
                
                with col2:
                    method_filter = st.selectbox("Filter by Method", 
                                               ["All"] + list(df['payment_method'].unique()),
                                               key="payment_method_filter")
                
                with col3:
                    date_filter = st.date_input("Filter from date", 
                                              key="payment_date_filter")
                
                # Apply filters
                filtered_df = df.copy()
                
                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df['status'] == status_filter]
                
                if method_filter != "All":
                    filtered_df = filtered_df[filtered_df['payment_method'] == method_filter]
                
                if date_filter:
                    filtered_df['payment_date'] = pd.to_datetime(filtered_df['payment_date'])
                    filtered_df = filtered_df[filtered_df['payment_date'].dt.date >= date_filter]
                
                # Display data
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Payments Data as CSV",
                    data=csv,
                    file_name=f"payments_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.info("No payments found in database.")
        else:
            st.error("Failed to connect to database.")
            
    except Exception as e:
        st.error(f"Error retrieving payments data: {str(e)}")

def show_payouts_data(db: DatabaseManager):
    """Display payouts data"""
    
    st.subheader("📊 Payouts Data")
    
    try:
        conn = db.get_connection()
        if conn:
            # Get payouts data with user and committee info
            query = """
            SELECT po.id, po.amount, po.payout_date, po.status,
                   po.payout_method, po.transaction_id, po.notes,
                   u.username, u.full_name,
                   c.title as committee_title
            FROM payouts po
            LEFT JOIN users u ON po.user_id = u.id
            LEFT JOIN committees c ON po.committee_id = c.id
            ORDER BY po.payout_date DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                st.write(f"**Total Payouts:** {len(df)}")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_amount = df['amount'].sum()
                    st.metric("Total Payout Amount", f"Rs. {total_amount:,}")
                
                with col2:
                    completed_count = len(df[df['status'] == 'paid'])
                    st.metric("Completed Payouts", completed_count)
                
                with col3:
                    pending_count = len(df[df['status'] == 'pending'])
                    st.metric("Pending Payouts", pending_count)
                
                with col4:
                    avg_amount = df['amount'].mean() if len(df) > 0 else 0
                    st.metric("Average Payout", f"Rs. {avg_amount:,.0f}")
                
                # Display data
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Payouts Data as CSV",
                    data=csv,
                    file_name=f"payouts_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.info("No payouts found in database.")
        else:
            st.error("Failed to connect to database.")
            
    except Exception as e:
        st.error(f"Error retrieving payouts data: {str(e)}")

def show_raw_query_interface(db: DatabaseManager):
    """Allow custom SQL queries for advanced data inspection"""
    
    st.subheader("🔍 Raw SQL Query Interface")
    st.warning("⚠️ This interface allows direct database access. Use with caution.")
    
    # Predefined queries
    st.markdown("### Quick Queries")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Committee Statistics"):
            query = """
            SELECT 
                status,
                COUNT(*) as count,
                AVG(monthly_amount) as avg_amount,
                SUM(current_members) as total_members
            FROM committees 
            GROUP BY status
            """
            execute_query(db, query)
    
    with col2:
        if st.button("💰 Payment Summary"):
            query = """
            SELECT 
                status,
                COUNT(*) as payment_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM payments 
            GROUP BY status
            """
            execute_query(db, query)
    
    # Custom query input
    st.markdown("### Custom Query")
    
    custom_query = st.text_area(
        "Enter your SQL query:",
        height=150,
        placeholder="""
        SELECT * FROM users LIMIT 10;
        
        -- Available tables: users, committees, committee_members, payments, payouts, payout_schedules
        """,
        key="custom_sql_query"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Execute Query", type="primary"):
            if custom_query.strip():
                execute_query(db, custom_query)
            else:
                st.error("Please enter a query.")
    
    with col2:
        if st.button("📋 Show Table Schema"):
            show_table_schema(db)

def execute_query(db: DatabaseManager, query: str):
    """Execute a custom SQL query and display results"""
    
    try:
        conn = db.get_connection()
        if conn:
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                st.success(f"Query executed successfully. {len(df)} rows returned.")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Query executed successfully but returned no results.")
        else:
            st.error("Failed to connect to database.")
            
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")

def show_table_schema(db: DatabaseManager):
    """Display database table schema information"""
    
    try:
        conn = db.get_connection()
        if conn:
            # Get table information
            schema_query = """
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
            
            df = pd.read_sql_query(schema_query, conn)
            conn.close()
            
            if not df.empty:
                st.success("Database schema retrieved successfully.")
                
                # Group by table
                for table_name in df['table_name'].unique():
                    with st.expander(f"📋 {table_name.upper()} Table"):
                        table_df = df[df['table_name'] == table_name][['column_name', 'data_type', 'is_nullable', 'column_default']]
                        st.dataframe(table_df, use_container_width=True, hide_index=True)
            else:
                st.info("No schema information found.")
        else:
            st.error("Failed to connect to database.")
            
    except Exception as e:
        st.error(f"Error retrieving schema: {str(e)}")