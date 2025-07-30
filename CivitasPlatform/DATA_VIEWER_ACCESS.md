# Data Viewer Access Instructions

## Overview
The Data Viewer is a separate administrative interface that allows you to inspect all database contents without affecting the regular committee platform functionality.

## Access Method

### Step 1: Navigate to Login Page
- Open the Civitas application
- You'll see the main login interface

### Step 2: Use Data Viewer Login
- Click the **"🔍 Data Viewer"** button (red/secondary button)
- Enter the following credentials:
  - **Username:** `dataviewer`
  - **Password:** `viewdata123`

### Step 3: Explore Database Contents
Once logged in as Data Viewer, you'll have access to:

#### Available Tabs:
1. **👥 Users** - View all registered users with filtering options
2. **🏛️ Committees** - Browse all committees with detailed information
3. **💰 Payments** - Inspect all payment records and transactions
4. **📊 Payouts** - Review payout history and status
5. **🔍 Raw Query** - Execute custom SQL queries for advanced inspection

#### Features Available:
- **Filtering:** Filter data by status, type, date ranges, etc.
- **Search:** Search through records using various criteria
- **Export:** Download filtered data as CSV files
- **Custom Queries:** Execute SQL queries for specific data needs
- **Schema View:** Inspect database table structures

## Key Differences from Regular Access

### Data Viewer Mode:
- **Purpose:** Database inspection and data analysis only
- **Access Level:** Full read access to all database contents
- **Interface:** Specialized data exploration tools
- **Users:** Separate from committee members/admins

### Regular Committee Platform:
- **Purpose:** Committee management, payments, member interactions
- **Access Level:** Role-based (admin/member) with specific permissions
- **Interface:** Committee-focused functionality
- **Users:** Platform members participating in committees

## Security Notes

- Data Viewer access is completely separate from regular user accounts
- No committee management functions are available in Data Viewer mode
- This is a read-only interface for data inspection
- Regular users cannot access this interface

## Changing Credentials

To change the Data Viewer credentials, modify these values in `app.py`:
```python
DATA_VIEWER_USERNAME = "dataviewer"
DATA_VIEWER_PASSWORD = "viewdata123"
```

Consider using environment variables for production deployment.

## Sample Use Cases

1. **User Analysis:** Check user registration patterns and trust scores
2. **Committee Performance:** Analyze committee success rates and member engagement
3. **Payment Tracking:** Monitor payment completion rates and methods
4. **Data Export:** Extract data for external analysis or reporting
5. **Database Health:** Verify data integrity and relationships

## Exit Data Viewer

To exit Data Viewer mode:
- Click **"🚪 Exit Data Viewer"** in the sidebar
- You'll be returned to the main login screen
- You can then log in as a regular user if needed