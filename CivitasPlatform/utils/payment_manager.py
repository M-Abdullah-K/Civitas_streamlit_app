from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from database.db_manager import DatabaseManager
import uuid

class PaymentManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def calculate_payment_schedule(self, committee_id: str, start_date: datetime, 
                                 payment_frequency: str, duration: int) -> List[Dict[str, Any]]:
        """Calculate payment schedule for committee"""
        schedule = []
        current_date = start_date
        
        if payment_frequency == 'monthly':
            interval_days = 30
        elif payment_frequency == 'bi_monthly':
            interval_days = 60
        else:
            interval_days = 30  # Default to monthly
        
        for cycle in range(duration):
            due_date = current_date + timedelta(days=interval_days * cycle)
            schedule.append({
                'cycle': cycle + 1,
                'due_date': due_date,
                'amount_per_member': None  # Will be set based on committee
            })
        
        return schedule
    
    def calculate_payout_schedule(self, committee_id: str, members: List[str], 
                                start_date: datetime, payment_frequency: str) -> List[Dict[str, Any]]:
        """Calculate payout schedule based on member positions"""
        schedule = []
        
        if payment_frequency == 'monthly':
            interval_days = 30
        elif payment_frequency == 'bi_monthly':
            interval_days = 60
        else:
            interval_days = 30
        
        for position, member_id in enumerate(members, 1):
            payout_date = start_date + timedelta(days=interval_days * (position - 1))
            schedule.append({
                'position': position,
                'member_id': member_id,
                'payout_date': payout_date,
                'is_completed': False
            })
        
        return schedule
    
    def process_payment(self, committee_id: str, user_id: str, amount: int, 
                       payment_method: str = 'bank_transfer') -> Dict[str, Any]:
        """Process a payment for committee"""
        payment_id = str(uuid.uuid4())
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{payment_id[:8]}"
        
        # In a real implementation, this would integrate with payment gateway
        # For now, we'll simulate successful payment
        
        payment_data = {
            'id': payment_id,
            'committee_id': committee_id,
            'user_id': user_id,
            'amount': amount,
            'payment_date': datetime.now(),
            'status': 'paid',
            'transaction_id': transaction_id,
            'payment_method': payment_method
        }
        
        # Update trust score based on timely payment
        self.update_trust_score_for_payment(user_id, committee_id, on_time=True)
        
        return payment_data
    
    def process_payout(self, committee_id: str, user_id: str, amount: int, 
                      payout_method: str = 'bank_transfer') -> Dict[str, Any]:
        """Process a payout to committee member"""
        payout_id = str(uuid.uuid4())
        transaction_id = f"PAYOUT{datetime.now().strftime('%Y%m%d%H%M%S')}{payout_id[:8]}"
        
        # In a real implementation, this would integrate with payout system
        # For now, we'll simulate successful payout
        
        payout_data = {
            'id': payout_id,
            'committee_id': committee_id,
            'user_id': user_id,
            'amount': amount,
            'payout_date': datetime.now(),
            'status': 'paid',
            'transaction_id': transaction_id,
            'payout_method': payout_method
        }
        
        return payout_data
    
    def update_trust_score_for_payment(self, user_id: str, committee_id: str, on_time: bool = True):
        """Update user trust score based on payment behavior"""
        current_user = self.db.get_user_by_id(user_id)
        if not current_user:
            return
        
        current_score = current_user.get('trust_score', 85)
        
        if on_time:
            # Reward for on-time payment
            new_score = min(100, current_score + 1)
            reason = "On-time payment"
        else:
            # Penalty for late payment
            new_score = max(0, current_score - 3)
            reason = "Late payment"
        
        if new_score != current_score:
            # In a real implementation, this would update the database
            # For now, we'll just calculate the new score
            pass
    
    def calculate_monthly_collection(self, committee_id: str) -> int:
        """Calculate total monthly collection for committee"""
        # This would query the database for committee details
        # and calculate based on current members and monthly amount
        pass
    
    def get_payment_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get payment reminders for user"""
        reminders = []
        
        # Get user's committees
        committees = self.db.get_user_committees(user_id)
        
        for committee in committees:
            # Check if payment is due soon
            # This is a simplified version
            next_due_date = datetime.now() + timedelta(days=7)  # Example
            
            reminders.append({
                'committee_id': committee.id,
                'committee_title': committee.title,
                'amount': committee.monthly_amount,
                'due_date': next_due_date,
                'days_until_due': 7
            })
        
        return reminders
    
    def get_payout_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get payout notifications for user"""
        notifications = []
        
        # Get user's committees where they're eligible for payout
        committees = self.db.get_user_committees(user_id)
        
        for committee in committees:
            # Check if user is next in payout queue
            position = self.db.get_member_position_in_committee(committee.id, user_id)
            
            if position == 1:  # Next in line for payout
                payout_amount = committee.monthly_amount * committee.current_members
                notifications.append({
                    'committee_id': committee.id,
                    'committee_title': committee.title,
                    'amount': payout_amount,
                    'estimated_date': datetime.now() + timedelta(days=7)
                })
        
        return notifications
    
    def validate_payment_amount(self, committee_id: str, amount: int) -> bool:
        """Validate payment amount for committee"""
        # This would check against committee's monthly amount
        # For now, just check if amount is positive
        return amount > 0
    
    def get_payment_methods(self) -> List[Dict[str, str]]:
        """Get available payment methods"""
        return [
            {'id': 'bank_transfer', 'name': 'Bank Transfer', 'icon': '🏦'},
            {'id': 'mobile_payment', 'name': 'Mobile Payment', 'icon': '📱'},
            {'id': 'cash', 'name': 'Cash Deposit', 'icon': '💵'},
            {'id': 'cheque', 'name': 'Cheque', 'icon': '📝'}
        ]
    
    def get_payout_methods(self) -> List[Dict[str, str]]:
        """Get available payout methods"""
        return [
            {'id': 'bank_transfer', 'name': 'Bank Transfer', 'icon': '🏦'},
            {'id': 'cash', 'name': 'Cash Pickup', 'icon': '💵'},
            {'id': 'halal_voucher', 'name': 'Halal Product Voucher', 'icon': '🎫'},
            {'id': 'gold_silver', 'name': 'Gold/Silver Purchase', 'icon': '🥇'},
            {'id': 'investment', 'name': 'Halal Investment', 'icon': '📈'}
        ]
