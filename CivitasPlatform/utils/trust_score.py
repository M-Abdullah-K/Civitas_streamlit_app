from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from database.db_manager import DatabaseManager

class TrustScoreManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def calculate_trust_score(self, user_id: str) -> int:
        """Calculate trust score based on payment history and committee participation"""
        
        # Get user's payment history
        payments = self.db.get_user_payment_history(user_id)
        committees = self.db.get_user_committees(user_id)
        
        if not payments and not committees:
            return 85  # Default trust score for new users
        
        # Base score
        base_score = 50
        
        # Payment consistency (40 points max)
        payment_score = self._calculate_payment_score(payments)
        
        # Committee completion rate (30 points max)
        completion_score = self._calculate_completion_score(committees)
        
        # Tenure bonus (20 points max)
        tenure_score = self._calculate_tenure_score(user_id)
        
        total_score = base_score + payment_score + completion_score + tenure_score
        
        # Cap at 100
        return min(100, max(0, total_score))
    
    def _calculate_payment_score(self, payments: List[Any]) -> int:
        """Calculate score based on payment consistency"""
        if not payments:
            return 0
        
        paid_payments = [p for p in payments if p.status == 'paid']
        total_payments = len(payments)
        
        if total_payments == 0:
            return 0
        
        payment_ratio = len(paid_payments) / total_payments
        
        # On-time payment bonus
        on_time_payments = 0
        for payment in paid_payments:
            if hasattr(payment, 'due_date') and hasattr(payment, 'payment_date'):
                if payment.payment_date <= payment.due_date:
                    on_time_payments += 1
        
        on_time_ratio = on_time_payments / len(paid_payments) if paid_payments else 0
        
        return int(payment_ratio * 25 + on_time_ratio * 15)
    
    def _calculate_completion_score(self, committees: List[Any]) -> int:
        """Calculate score based on committee completion"""
        if not committees:
            return 0
        
        completed_committees = [c for c in committees if c.status == 'completed']
        total_committees = len(committees)
        
        completion_ratio = len(completed_committees) / total_committees
        
        # Active participation bonus
        active_committees = [c for c in committees if c.status == 'active']
        active_bonus = min(10, len(active_committees) * 2)
        
        return int(completion_ratio * 20 + active_bonus)
    
    def _calculate_tenure_score(self, user_id: str) -> int:
        """Calculate bonus points based on account age"""
        user_data = self.db.get_user_by_id(user_id)
        
        if not user_data or not hasattr(user_data, 'created_date'):
            return 0
        
        account_age = datetime.now() - user_data.created_date
        months_active = account_age.days / 30
        
        # 1 point per month, max 20 points
        return min(20, int(months_active))
    
    def update_trust_score(self, user_id: str, reason: str, committee_id: Optional[str] = None) -> int:
        """Update user's trust score and log the change"""
        
        old_score = self.get_current_trust_score(user_id)
        new_score = self.calculate_trust_score(user_id)
        
        # Log the change if there's a significant difference
        if abs(new_score - old_score) >= 1:
            self._log_trust_score_change(user_id, old_score, new_score, reason, committee_id)
        
        return new_score
    
    def get_current_trust_score(self, user_id: str) -> int:
        """Get current trust score from user data"""
        user_data = self.db.get_user_by_id(user_id)
        if user_data and hasattr(user_data, 'trust_score'):
            return user_data.trust_score
        return 85  # Default score
    
    def _log_trust_score_change(self, user_id: str, old_score: int, new_score: int, 
                               reason: str, committee_id: Optional[str] = None):
        """Log trust score changes for audit trail"""
        # This would integrate with the database to log changes
        # For now, we'll implement a simple logging mechanism
        pass
    
    def get_trust_level_description(self, score: int) -> Dict[str, str]:
        """Get trust level description and recommendations"""
        
        if score >= 95:
            return {
                "level": "Excellent",
                "description": "Outstanding payment history and committee participation",
                "benefits": "Access to premium committees, lower fees, priority support",
                "color": "#228B22"
            }
        elif score >= 85:
            return {
                "level": "Very Good",
                "description": "Reliable member with consistent payments",
                "benefits": "Access to most committees, good rates",
                "color": "#32CD32"
            }
        elif score >= 75:
            return {
                "level": "Good",
                "description": "Generally reliable with occasional delays",
                "benefits": "Access to standard committees",
                "color": "#FFD700"
            }
        elif score >= 60:
            return {
                "level": "Fair",
                "description": "Some payment issues, room for improvement",
                "benefits": "Limited committee access, higher fees",
                "color": "#FFA500"
            }
        else:
            return {
                "level": "Needs Improvement",
                "description": "Significant payment issues requiring attention",
                "benefits": "Restricted access, mandatory monitoring",
                "color": "#DC143C"
            }
    
    def get_improvement_recommendations(self, user_id: str) -> List[str]:
        """Get personalized recommendations to improve trust score"""
        
        score = self.get_current_trust_score(user_id)
        recommendations = []
        
        if score < 85:
            recommendations.append("Make all payments on time to improve payment consistency")
        
        if score < 75:
            recommendations.append("Complete current committee commitments to boost completion rate")
            recommendations.append("Consider joining smaller committees to build trust gradually")
        
        if score < 60:
            recommendations.append("Focus on resolving any outstanding payment issues")
            recommendations.append("Communicate with committee admins about any payment difficulties")
        
        # Always include positive reinforcement
        if score >= 85:
            recommendations.append("Maintain your excellent payment record")
        
        return recommendations