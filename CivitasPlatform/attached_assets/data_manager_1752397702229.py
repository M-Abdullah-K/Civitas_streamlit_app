import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random

def initialize_data():
    """Initialize sample data for the application"""
    
    # Initialize committees if not exists
    if 'committees' not in st.session_state:
        st.session_state.committees = [
            {
                'id': str(uuid.uuid4()),
                'title': 'Tech Professionals Committee',
                'monthly_amount': 15000,
                'total_members': 12,
                'current_members': 8,
                'duration': 12,
                'type': 'public',
                'category': 'Business',
                'description': 'A committee for IT professionals to save for tech equipment and professional development',
                'admin_id': 'admin',
                'status': 'active',
                'created_date': '2024-01-15',
                'members': ['admin', 'sara', 'hassan'],
                'payment_history': [],
                'payout_schedule': []
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Family Savings Circle',
                'monthly_amount': 8000,
                'total_members': 8,
                'current_members': 6,
                'duration': 8,
                'type': 'private',
                'category': 'Family',
                'description': 'Family members saving for household expenses and emergencies',
                'admin_id': 'sara',
                'status': 'active',
                'created_date': '2024-02-01',
                'members': ['sara', 'hassan'],
                'payment_history': [],
                'payout_schedule': []
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Hajj Fund Committee',
                'monthly_amount': 25000,
                'total_members': 15,
                'current_members': 10,
                'duration': 18,
                'type': 'public',
                'category': 'General',
                'description': 'Saving for Hajj pilgrimage expenses in a halal way',
                'admin_id': 'hassan',
                'status': 'active',
                'created_date': '2024-03-01',
                'members': ['hassan', 'admin'],
                'payment_history': [],
                'payout_schedule': []
            }
        ]
    
    # Initialize payment history for existing committees
    for committee in st.session_state.committees:
        if not committee.get('payment_history'):
            committee['payment_history'] = generate_payment_history(committee)
        
        if not committee.get('payout_schedule'):
            committee['payout_schedule'] = generate_payout_schedule(committee)

def generate_payment_history(committee):
    """Generate payment history for a committee"""
    history = []
    start_date = datetime.strptime(committee['created_date'], '%Y-%m-%d')
    
    # Generate history for past months
    months_active = max(1, (datetime.now() - start_date).days // 30)
    
    for month in range(months_active):
        payment_date = start_date + timedelta(days=30 * month)
        
        for member_id in committee['members']:
            # Most payments are successful (90% rate)
            if random.random() < 0.9:
                history.append({
                    'member_id': member_id,
                    'amount': committee['monthly_amount'],
                    'date': payment_date.strftime('%Y-%m-%d'),
                    'status': 'paid',
                    'method': random.choice(['Bank Transfer', 'Cash', 'Mobile Payment']),
                    'transaction_id': f"TXN{random.randint(100000, 999999)}"
                })
    
    return history

def generate_payout_schedule(committee):
    """Generate payout schedule for a committee"""
    schedule = []
    start_date = datetime.strptime(committee['created_date'], '%Y-%m-%d')
    
    for i, member_id in enumerate(committee['members']):
        payout_date = start_date + timedelta(days=30 * i)
        payout_amount = committee['monthly_amount'] * committee['current_members']
        
        schedule.append({
            'member_id': member_id,
            'position': i + 1,
            'payout_date': payout_date.strftime('%Y-%m-%d'),
            'amount': payout_amount,
            'status': 'pending' if payout_date > datetime.now() else 'completed'
        })
    
    return schedule

def get_user_committees(username=None):
    """Get committees for a specific user"""
    if username is None:
        username = st.session_state.get('current_user')
    
    if not username:
        return []
    
    committees = st.session_state.get('committees', [])
    user_committees = []
    
    for committee in committees:
        if username in committee.get('members', []):
            # Add payment status for the user
            committee_copy = committee.copy()
            committee_copy['payment_status'] = get_user_payment_status(committee, username)
            user_committees.append(committee_copy)
    
    return user_committees

def get_user_payment_status(committee, username):
    """Get payment status for a user in a committee"""
    # Check if user has paid for current month
    current_month = datetime.now().strftime('%Y-%m')
    payment_history = committee.get('payment_history', [])
    
    for payment in payment_history:
        if (payment['member_id'] == username and 
            payment['date'].startswith(current_month) and 
            payment['status'] == 'paid'):
            return 'paid'
    
    return 'unpaid'

def get_committee_by_id(committee_id):
    """Get committee by ID"""
    committees = st.session_state.get('committees', [])
    
    for committee in committees:
        if committee['id'] == committee_id:
            return committee
    
    return None

def update_committee(committee_id, updates):
    """Update committee information"""
    committees = st.session_state.get('committees', [])
    
    for i, committee in enumerate(committees):
        if committee['id'] == committee_id:
            for key, value in updates.items():
                committees[i][key] = value
            return True
    
    return False

def add_member_to_committee(committee_id, username):
    """Add a member to a committee"""
    committee = get_committee_by_id(committee_id)
    
    if not committee:
        return False, "Committee not found"
    
    if username in committee['members']:
        return False, "User is already a member"
    
    if committee['current_members'] >= committee['total_members']:
        return False, "Committee is full"
    
    committee['members'].append(username)
    committee['current_members'] += 1
    
    return True, "Member added successfully"

def remove_member_from_committee(committee_id, username):
    """Remove a member from a committee"""
    committee = get_committee_by_id(committee_id)
    
    if not committee:
        return False, "Committee not found"
    
    if username not in committee['members']:
        return False, "User is not a member"
    
    if username == committee['admin_id']:
        return False, "Cannot remove admin from committee"
    
    committee['members'].remove(username)
    committee['current_members'] -= 1
    
    return True, "Member removed successfully"

def record_payment(committee_id, username, amount, method='Bank Transfer'):
    """Record a payment for a committee member"""
    committee = get_committee_by_id(committee_id)
    
    if not committee:
        return False, "Committee not found"
    
    if username not in committee['members']:
        return False, "User is not a member of this committee"
    
    payment_record = {
        'member_id': username,
        'amount': amount,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'status': 'paid',
        'method': method,
        'transaction_id': f"TXN{random.randint(100000, 999999)}"
    }
    
    if 'payment_history' not in committee:
        committee['payment_history'] = []
    
    committee['payment_history'].append(payment_record)
    
    return True, "Payment recorded successfully"

def process_payout(committee_id, member_id, amount, method='Bank Transfer'):
    """Process a payout for a committee member"""
    committee = get_committee_by_id(committee_id)
    
    if not committee:
        return False, "Committee not found"
    
    payout_record = {
        'member_id': member_id,
        'amount': amount,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'method': method,
        'status': 'processed',
        'transaction_id': f"PAY{random.randint(100000, 999999)}"
    }
    
    if 'payout_history' not in committee:
        committee['payout_history'] = []
    
    committee['payout_history'].append(payout_record)
    
    return True, "Payout processed successfully"

def get_committee_statistics(committee_id):
    """Get statistics for a committee"""
    committee = get_committee_by_id(committee_id)
    
    if not committee:
        return None
    
    payment_history = committee.get('payment_history', [])
    
    # Calculate total collected
    total_collected = sum(payment['amount'] for payment in payment_history if payment['status'] == 'paid')
    
    # Calculate collection rate
    expected_total = committee['monthly_amount'] * committee['current_members']
    months_active = max(1, (datetime.now() - datetime.strptime(committee['created_date'], '%Y-%m-%d')).days // 30)
    expected_total_all_time = expected_total * months_active
    
    collection_rate = (total_collected / expected_total_all_time * 100) if expected_total_all_time > 0 else 0
    
    # Get member payment rates
    member_stats = {}
    for member_id in committee['members']:
        member_payments = [p for p in payment_history if p['member_id'] == member_id and p['status'] == 'paid']
        member_stats[member_id] = {
            'total_paid': sum(p['amount'] for p in member_payments),
            'payment_count': len(member_payments),
            'payment_rate': (len(member_payments) / months_active * 100) if months_active > 0 else 0
        }
    
    return {
        'total_collected': total_collected,
        'collection_rate': collection_rate,
        'monthly_target': expected_total,
        'months_active': months_active,
        'member_stats': member_stats,
        'average_trust_score': calculate_committee_trust_score(committee)
    }

def calculate_committee_trust_score(committee):
    """Calculate average trust score for committee members"""
    users = st.session_state.get('users', [])
    trust_scores = []
    
    for member_id in committee['members']:
        user = next((u for u in users if u['username'] == member_id), None)
        if user:
            trust_scores.append(user.get('trust_score', 75))
    
    return sum(trust_scores) / len(trust_scores) if trust_scores else 75

def get_public_committees():
    """Get all public committees"""
    committees = st.session_state.get('committees', [])
    return [c for c in committees if c['type'] == 'public']

def get_private_committees():
    """Get all private committees"""
    committees = st.session_state.get('committees', [])
    return [c for c in committees if c['type'] == 'private']

def search_committees(query, category=None, min_amount=None, max_amount=None):
    """Search committees based on criteria"""
    committees = st.session_state.get('committees', [])
    results = []
    
    for committee in committees:
        # Text search
        if query and query.lower() not in committee['title'].lower() and query.lower() not in committee.get('description', '').lower():
            continue
        
        # Category filter
        if category and category != 'All' and committee.get('category') != category:
            continue
        
        # Amount filters
        if min_amount and committee['monthly_amount'] < min_amount:
            continue
        
        if max_amount and committee['monthly_amount'] > max_amount:
            continue
        
        results.append(committee)
    
    return results

def get_committee_analytics():
    """Get overall committee analytics"""
    committees = st.session_state.get('committees', [])
    
    if not committees:
        return {
            'total_committees': 0,
            'active_committees': 0,
            'total_members': 0,
            'total_monthly_volume': 0,
            'average_committee_size': 0,
            'committee_types': {}
        }
    
    active_committees = [c for c in committees if c['status'] == 'active']
    total_members = sum(c['current_members'] for c in committees)
    total_monthly_volume = sum(c['monthly_amount'] * c['current_members'] for c in committees)
    
    # Committee type distribution
    committee_types = {}
    for committee in committees:
        committee_type = committee['type']
        if committee_type not in committee_types:
            committee_types[committee_type] = 0
        committee_types[committee_type] += 1
    
    return {
        'total_committees': len(committees),
        'active_committees': len(active_committees),
        'total_members': total_members,
        'total_monthly_volume': total_monthly_volume,
        'average_committee_size': total_members / len(committees) if committees else 0,
        'committee_types': committee_types
    }

def export_committee_data(committee_id, format='csv'):
    """Export committee data for download"""
    committee = get_committee_by_id(committee_id)
    
    if not committee:
        return None
    
    if format == 'csv':
        # Create DataFrame from committee data
        data = {
            'Committee Title': [committee['title']],
            'Monthly Amount': [committee['monthly_amount']],
            'Total Members': [committee['total_members']],
            'Current Members': [committee['current_members']],
            'Status': [committee['status']],
            'Created Date': [committee['created_date']]
        }
        
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    return None

def validate_committee_data(committee_data):
    """Validate committee data before creation/update"""
    errors = []
    
    if not committee_data.get('title'):
        errors.append("Committee title is required")
    
    if not committee_data.get('monthly_amount') or committee_data['monthly_amount'] < 1000:
        errors.append("Monthly amount must be at least Rs. 1,000")
    
    if not committee_data.get('total_members') or committee_data['total_members'] < 2:
        errors.append("Committee must have at least 2 members")
    
    if not committee_data.get('duration') or committee_data['duration'] < 1:
        errors.append("Duration must be at least 1 month")
    
    if committee_data.get('type') not in ['public', 'private']:
        errors.append("Committee type must be either public or private")
    
    return errors

def cleanup_expired_committees():
    """Remove expired or completed committees"""
    committees = st.session_state.get('committees', [])
    active_committees = []
    
    for committee in committees:
        created_date = datetime.strptime(committee['created_date'], '%Y-%m-%d')
        end_date = created_date + timedelta(days=30 * committee['duration'])
        
        if datetime.now() < end_date and committee['status'] == 'active':
            active_committees.append(committee)
        else:
            # Mark as completed instead of removing
            committee['status'] = 'completed'
            active_committees.append(committee)
    
    st.session_state.committees = active_committees

def get_user_committee_summary(username):
    """Get summary of user's committee participation"""
    user_committees = get_user_committees(username)
    
    if not user_committees:
        return {
            'total_committees': 0,
            'active_committees': 0,
            'total_monthly_commitment': 0,
            'admin_committees': 0,
            'average_trust_score': 0
        }
    
    active_committees = [c for c in user_committees if c['status'] == 'active']
    total_monthly_commitment = sum(c['monthly_amount'] for c in user_committees)
    admin_committees = [c for c in user_committees if c['admin_id'] == username]
    
    return {
        'total_committees': len(user_committees),
        'active_committees': len(active_committees),
        'total_monthly_commitment': total_monthly_commitment,
        'admin_committees': len(admin_committees),
        'committees': user_committees
    }
