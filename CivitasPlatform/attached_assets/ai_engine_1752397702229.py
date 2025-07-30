import random
from datetime import datetime, timedelta

def get_financial_advice(financial_profile):
    """Generate AI-powered financial advice based on user profile"""
    
    advice = {
        'Emergency Planning': [],
        'Committee Strategy': [],
        'Savings Optimization': [],
        'Risk Management': [],
        'Goal Achievement': []
    }
    
    monthly_income = financial_profile['monthly_income']
    monthly_expenses = financial_profile['monthly_expenses']
    disposable_income = monthly_income - monthly_expenses
    current_savings = financial_profile['current_savings']
    debt_amount = financial_profile['debt_amount']
    dependents = financial_profile['dependents']
    age = financial_profile['age']
    
    # Emergency Planning Advice
    emergency_fund_target = monthly_expenses * 6
    if current_savings < emergency_fund_target:
        shortage = emergency_fund_target - current_savings
        advice['Emergency Planning'].append({
            'priority': 'high',
            'message': f'Build emergency fund: You need Rs. {shortage:,} more to reach 6 months of expenses. Target: Rs. {emergency_fund_target:,}'
        })
    else:
        advice['Emergency Planning'].append({
            'priority': 'low',
            'message': f'Excellent! Your emergency fund of Rs. {current_savings:,} covers {current_savings/monthly_expenses:.1f} months of expenses.'
        })
    
    # Committee Strategy Advice
    safe_committee_amount = max(0, int(disposable_income * 0.3))  # 30% of disposable income
    
    if disposable_income < 5000:
        advice['Committee Strategy'].append({
            'priority': 'high',
            'message': 'Avoid committees until you increase your disposable income. Focus on reducing expenses or increasing income first.'
        })
    elif disposable_income < 15000:
        advice['Committee Strategy'].append({
            'priority': 'medium',
            'message': f'Start with small committees: Maximum Rs. {safe_committee_amount:,}/month. Join 1-2 committees maximum.'
        })
    else:
        advice['Committee Strategy'].append({
            'priority': 'low',
            'message': f'You can safely commit Rs. {safe_committee_amount:,}/month to committees. Consider diversifying across 2-3 different committees.'
        })
    
    # Savings Optimization
    savings_rate = (disposable_income / monthly_income) * 100 if monthly_income > 0 else 0
    
    if savings_rate < 10:
        advice['Savings Optimization'].append({
            'priority': 'high',
            'message': f'Low savings rate ({savings_rate:.1f}%). Target 20% of income. Review expenses and find Rs. {int(monthly_income * 0.2 - disposable_income):,} to cut.'
        })
    elif savings_rate < 20:
        advice['Savings Optimization'].append({
            'priority': 'medium',
            'message': f'Good savings rate ({savings_rate:.1f}%). Try to reach 20% by saving an additional Rs. {int(monthly_income * 0.2 - disposable_income):,}/month.'
        })
    else:
        advice['Savings Optimization'].append({
            'priority': 'low',
            'message': f'Excellent savings rate ({savings_rate:.1f}%)! Consider investing surplus in halal investment options.'
        })
    
    # Risk Management
    debt_to_income_ratio = (debt_amount / (monthly_income * 12)) * 100 if monthly_income > 0 else 0
    
    if debt_amount > 0:
        if debt_to_income_ratio > 40:
            advice['Risk Management'].append({
                'priority': 'high',
                'message': f'High debt burden ({debt_to_income_ratio:.1f}% of annual income). Prioritize debt repayment before joining committees.'
            })
        elif debt_to_income_ratio > 20:
            advice['Risk Management'].append({
                'priority': 'medium',
                'message': f'Moderate debt ({debt_to_income_ratio:.1f}% of annual income). Limit committee participation and accelerate debt repayment.'
            })
        else:
            advice['Risk Management'].append({
                'priority': 'low',
                'message': f'Manageable debt level ({debt_to_income_ratio:.1f}% of annual income). Continue regular payments while participating in committees.'
            })
    
    # Age-based advice
    if age < 30:
        advice['Risk Management'].append({
            'priority': 'low',
            'message': 'Young professional: You can take moderate risks. Focus on building wealth through committees and halal investments.'
        })
    elif age < 50:
        advice['Risk Management'].append({
            'priority': 'medium',
            'message': 'Mid-career: Balance growth with stability. Mix of short and long-term committees recommended.'
        })
    else:
        advice['Risk Management'].append({
            'priority': 'medium',
            'message': 'Pre-retirement: Focus on capital preservation. Choose stable, shorter-duration committees.'
        })
    
    # Dependents consideration
    if dependents > 0:
        dependent_buffer = dependents * 5000  # Rs. 5000 buffer per dependent
        advice['Risk Management'].append({
            'priority': 'medium',
            'message': f'With {dependents} dependents, maintain Rs. {dependent_buffer:,} additional buffer before committing to committees.'
        })
    
    # Goal Achievement
    financial_goals = financial_profile.get('financial_goals', [])
    if financial_goals:
        if 'House Purchase' in financial_goals:
            advice['Goal Achievement'].append({
                'priority': 'medium',
                'message': 'House purchase goal: Consider joining high-value, long-term committees (18-24 months) to accumulate down payment.'
            })
        
        if 'Hajj/Umrah' in financial_goals:
            advice['Goal Achievement'].append({
                'priority': 'medium',
                'message': 'Hajj/Umrah goal: Target committees worth Rs. 20,000-30,000/month for 12-18 months to cover expenses.'
            })
        
        if 'Children\'s Education' in financial_goals:
            advice['Goal Achievement'].append({
                'priority': 'high',
                'message': 'Education planning: Start early with consistent committees. Consider education-specific committees if available.'
            })
        
        if 'Retirement Planning' in financial_goals:
            advice['Goal Achievement'].append({
                'priority': 'low',
                'message': 'Retirement planning: Combine committees with halal retirement investments. Target 15-20% of income for retirement.'
            })
    
    return advice

def analyze_risk_profile(financial_profile):
    """Analyze user's financial risk profile"""
    
    monthly_income = financial_profile['monthly_income']
    monthly_expenses = financial_profile['monthly_expenses']
    disposable_income = monthly_income - monthly_expenses
    current_savings = financial_profile['current_savings']
    debt_amount = financial_profile['debt_amount']
    dependents = financial_profile['dependents']
    age = financial_profile['age']
    
    risk_factors = {}
    risk_scores = []
    
    # Income Stability Risk
    if monthly_income < 25000:
        risk_factors['Income Stability'] = {
            'level': 'High',
            'score': 80,
            'description': 'Low income increases financial vulnerability'
        }
        risk_scores.append(80)
    elif monthly_income < 50000:
        risk_factors['Income Stability'] = {
            'level': 'Medium',
            'score': 50,
            'description': 'Moderate income provides some stability'
        }
        risk_scores.append(50)
    else:
        risk_factors['Income Stability'] = {
            'level': 'Low',
            'score': 20,
            'description': 'Good income provides financial stability'
        }
        risk_scores.append(20)
    
    # Emergency Fund Risk
    emergency_fund_months = current_savings / monthly_expenses if monthly_expenses > 0 else 0
    if emergency_fund_months < 3:
        risk_factors['Emergency Preparedness'] = {
            'level': 'High',
            'score': 90,
            'description': f'Only {emergency_fund_months:.1f} months of expenses saved'
        }
        risk_scores.append(90)
    elif emergency_fund_months < 6:
        risk_factors['Emergency Preparedness'] = {
            'level': 'Medium',
            'score': 60,
            'description': f'{emergency_fund_months:.1f} months of expenses saved - building up'
        }
        risk_scores.append(60)
    else:
        risk_factors['Emergency Preparedness'] = {
            'level': 'Low',
            'score': 25,
            'description': f'Good emergency fund: {emergency_fund_months:.1f} months covered'
        }
        risk_scores.append(25)
    
    # Debt Risk
    if debt_amount > 0:
        debt_to_income_ratio = (debt_amount / (monthly_income * 12)) * 100
        if debt_to_income_ratio > 40:
            risk_factors['Debt Burden'] = {
                'level': 'High',
                'score': 85,
                'description': f'High debt: {debt_to_income_ratio:.1f}% of annual income'
            }
            risk_scores.append(85)
        elif debt_to_income_ratio > 20:
            risk_factors['Debt Burden'] = {
                'level': 'Medium',
                'score': 55,
                'description': f'Moderate debt: {debt_to_income_ratio:.1f}% of annual income'
            }
            risk_scores.append(55)
        else:
            risk_factors['Debt Burden'] = {
                'level': 'Low',
                'score': 30,
                'description': f'Manageable debt: {debt_to_income_ratio:.1f}% of annual income'
            }
            risk_scores.append(30)
    else:
        risk_factors['Debt Burden'] = {
            'level': 'Low',
            'score': 10,
            'description': 'No outstanding debt - excellent position'
        }
        risk_scores.append(10)
    
    # Cash Flow Risk
    cash_flow_ratio = (disposable_income / monthly_income) * 100 if monthly_income > 0 else 0
    if cash_flow_ratio < 10:
        risk_factors['Cash Flow'] = {
            'level': 'High',
            'score': 95,
            'description': f'Very tight cash flow: {cash_flow_ratio:.1f}% disposable income'
        }
        risk_scores.append(95)
    elif cash_flow_ratio < 20:
        risk_factors['Cash Flow'] = {
            'level': 'Medium',
            'score': 65,
            'description': f'Limited cash flow: {cash_flow_ratio:.1f}% disposable income'
        }
        risk_scores.append(65)
    else:
        risk_factors['Cash Flow'] = {
            'level': 'Low',
            'score': 30,
            'description': f'Healthy cash flow: {cash_flow_ratio:.1f}% disposable income'
        }
        risk_scores.append(30)
    
    # Dependent Risk
    if dependents > 3:
        risk_factors['Dependency Risk'] = {
            'level': 'High',
            'score': 75,
            'description': f'{dependents} dependents increase financial responsibility'
        }
        risk_scores.append(75)
    elif dependents > 0:
        risk_factors['Dependency Risk'] = {
            'level': 'Medium',
            'score': 45,
            'description': f'{dependents} dependents require financial planning'
        }
        risk_scores.append(45)
    else:
        risk_factors['Dependency Risk'] = {
            'level': 'Low',
            'score': 20,
            'description': 'No dependents - greater financial flexibility'
        }
        risk_scores.append(20)
    
    # Age Risk
    if age > 55:
        risk_factors['Age Risk'] = {
            'level': 'Medium',
            'score': 60,
            'description': 'Approaching retirement - need stable income'
        }
        risk_scores.append(60)
    elif age < 25:
        risk_factors['Age Risk'] = {
            'level': 'Medium',
            'score': 40,
            'description': 'Young career - income may be unstable'
        }
        risk_scores.append(40)
    else:
        risk_factors['Age Risk'] = {
            'level': 'Low',
            'score': 25,
            'description': 'Prime earning years - stable career expected'
        }
        risk_scores.append(25)
    
    # Calculate overall risk score
    overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 50
    
    return {
        'overall_risk_score': round(overall_risk_score, 1),
        'risk_factors': risk_factors,
        'risk_level': 'High' if overall_risk_score > 70 else 'Medium' if overall_risk_score > 40 else 'Low',
        'recommendations': generate_risk_recommendations(overall_risk_score, risk_factors)
    }

def generate_risk_recommendations(risk_score, risk_factors):
    """Generate recommendations based on risk analysis"""
    recommendations = []
    
    if risk_score > 70:
        recommendations.extend([
            "Focus on building emergency fund before joining committees",
            "Start with very small committee amounts (Rs. 2,000-5,000)",
            "Avoid long-term commitments until financial stability improves",
            "Consider increasing income through side work or skills development"
        ])
    elif risk_score > 40:
        recommendations.extend([
            "Join moderate committees (Rs. 5,000-15,000) with caution",
            "Maintain strict budget discipline",
            "Build emergency fund while participating in committees",
            "Diversify across 2-3 small committees rather than one large one"
        ])
    else:
        recommendations.extend([
            "You can safely participate in larger committees",
            "Consider diversifying across multiple committee types",
            "Good candidate for admin roles in committees",
            "Explore investment-focused committees for wealth building"
        ])
    
    # Specific recommendations based on risk factors
    for factor, details in risk_factors.items():
        if details['level'] == 'High':
            if factor == 'Emergency Preparedness':
                recommendations.append("Priority: Build 6-month emergency fund before major committee commitments")
            elif factor == 'Debt Burden':
                recommendations.append("Priority: Reduce debt before expanding committee participation")
            elif factor == 'Cash Flow':
                recommendations.append("Priority: Improve monthly cash flow through expense reduction or income increase")
    
    return recommendations

def generate_budget_recommendations(financial_profile):
    """Generate AI-powered budget recommendations"""
    
    monthly_income = financial_profile['monthly_income']
    monthly_expenses = financial_profile['monthly_expenses']
    current_savings = financial_profile['current_savings']
    debt_amount = financial_profile['debt_amount']
    dependents = financial_profile['dependents']
    
    # Islamic/Pakistani budgeting principles
    # 50% needs, 30% wants, 20% savings/investments (modified for Pakistani context)
    
    recommended_allocation = {}
    suggestions = {}
    
    # Essential expenses (50-60% of income)
    essential_target = monthly_income * 0.55
    recommended_allocation['Essential Expenses'] = int(essential_target)
    
    if monthly_expenses > essential_target:
        excess = monthly_expenses - essential_target
        suggestions['Essential Expenses'] = {
            'message': f'Your fixed expenses are Rs. {excess:,} above recommended 55% of income. Review and cut unnecessary expenses.',
            'impact': 'high',
            'savings_potential': excess
        }
    else:
        savings_potential = essential_target - monthly_expenses
        suggestions['Essential Expenses'] = {
            'message': f'Good control over expenses. You have Rs. {savings_potential:,} buffer in your essential budget.',
            'impact': 'low'
        }
    
    # Debt payments (if applicable)
    if debt_amount > 0:
        debt_payment = min(monthly_income * 0.2, debt_amount / 12)  # Max 20% of income or monthly amount to clear in 1 year
        recommended_allocation['Debt Payments'] = int(debt_payment)
        
        suggestions['Debt Payments'] = {
            'message': f'Allocate Rs. {debt_payment:,}/month for debt repayment to clear debt faster.',
            'impact': 'high'
        }
    
    # Emergency fund building
    emergency_fund_target = monthly_expenses * 6
    if current_savings < emergency_fund_target:
        emergency_saving = min(monthly_income * 0.1, (emergency_fund_target - current_savings) / 12)
        recommended_allocation['Emergency Fund'] = int(emergency_saving)
        
        suggestions['Emergency Fund'] = {
            'message': f'Build emergency fund with Rs. {emergency_saving:,}/month until you reach Rs. {emergency_fund_target:,}.',
            'impact': 'high'
        }
    
    # Committee participation
    remaining_income = monthly_income - sum(recommended_allocation.values())
    committee_budget = max(0, int(remaining_income * 0.4))  # 40% of remaining income
    
    if committee_budget > 0:
        recommended_allocation['Committee Participation'] = committee_budget
        suggestions['Committee Participation'] = {
            'message': f'You can safely allocate Rs. {committee_budget:,}/month to committees.',
            'impact': 'medium'
        }
    else:
        suggestions['Committee Participation'] = {
            'message': 'Focus on debt repayment and emergency fund before joining committees.',
            'impact': 'high'
        }
    
    # Halal investments
    remaining_after_committee = remaining_income - committee_budget
    investment_budget = max(0, int(remaining_after_committee * 0.6))
    
    if investment_budget > 5000:
        recommended_allocation['Halal Investments'] = investment_budget
        suggestions['Halal Investments'] = {
            'message': f'Consider Rs. {investment_budget:,}/month in halal investments (mutual funds, gold, real estate).',
            'impact': 'medium'
        }
    
    # Discretionary spending
    discretionary = remaining_income - committee_budget - investment_budget
    if discretionary > 0:
        recommended_allocation['Discretionary Spending'] = discretionary
        suggestions['Discretionary Spending'] = {
            'message': f'Rs. {discretionary:,}/month available for personal wants and family activities.',
            'impact': 'low'
        }
    
    # Zakat consideration
    if monthly_income * 12 > 400000:  # Approx nisab in PKR
        zakat_amount = int(monthly_income * 12 * 0.025 / 12)  # 2.5% annually
        recommended_allocation['Zakat & Charity'] = zakat_amount
        suggestions['Zakat & Charity'] = {
            'message': f'Don\'t forget your Zakat obligation: approximately Rs. {zakat_amount:,}/month.',
            'impact': 'medium'
        }
    
    return {
        'recommended_allocation': recommended_allocation,
        'suggestions': suggestions,
        'total_allocated': sum(recommended_allocation.values()),
        'budget_balance': monthly_income - sum(recommended_allocation.values())
    }

def predict_committee_success(committee_data, user_profile):
    """Predict likelihood of committee success for a user"""
    
    success_factors = []
    risk_factors = []
    
    # User financial health
    disposable_income = user_profile['monthly_income'] - user_profile['monthly_expenses']
    commitment_ratio = committee_data['monthly_amount'] / disposable_income if disposable_income > 0 else 1
    
    if commitment_ratio < 0.3:
        success_factors.append("Low financial commitment ratio - sustainable")
    elif commitment_ratio < 0.5:
        success_factors.append("Moderate commitment ratio - manageable")
    else:
        risk_factors.append("High commitment ratio - may strain finances")
    
    # Committee characteristics
    if committee_data['type'] == 'private':
        success_factors.append("Private committee - better member screening")
    
    if committee_data['duration'] <= 12:
        success_factors.append("Short duration - lower long-term risk")
    elif committee_data['duration'] > 18:
        risk_factors.append("Long duration - higher commitment risk")
    
    if committee_data['total_members'] <= 10:
        success_factors.append("Small group - easier management")
    elif committee_data['total_members'] > 20:
        risk_factors.append("Large group - coordination challenges")
    
    # Calculate success probability
    base_probability = 75  # Base success rate
    
    # Adjust based on factors
    for factor in success_factors:
        base_probability += 5
    
    for factor in risk_factors:
        base_probability -= 10
    
    success_probability = max(10, min(95, base_probability))
    
    return {
        'success_probability': success_probability,
        'success_factors': success_factors,
        'risk_factors': risk_factors,
        'recommendation': get_committee_recommendation(success_probability)
    }

def get_committee_recommendation(success_probability):
    """Get recommendation based on success probability"""
    if success_probability >= 80:
        return "Highly recommended - excellent fit for your financial profile"
    elif success_probability >= 65:
        return "Recommended - good alignment with your finances"
    elif success_probability >= 50:
        return "Consider carefully - moderate risk involved"
    else:
        return "Not recommended - high risk of financial strain"

def generate_savings_projections(user_profile, committee_commitments):
    """Generate savings projections with different scenarios"""
    
    monthly_income = user_profile['monthly_income']
    monthly_expenses = user_profile['monthly_expenses']
    current_savings = user_profile['current_savings']
    
    committee_total = sum(c['monthly_amount'] for c in committee_commitments)
    disposable_income = monthly_income - monthly_expenses - committee_total
    
    scenarios = {}
    
    # Conservative scenario (save 50% of remaining disposable income)
    conservative_saving = max(0, disposable_income * 0.5)
    scenarios['Conservative'] = {
        'monthly_saving': conservative_saving,
        'annual_saving': conservative_saving * 12,
        'five_year_total': current_savings + (conservative_saving * 60)
    }
    
    # Moderate scenario (save 70% of remaining disposable income)
    moderate_saving = max(0, disposable_income * 0.7)
    scenarios['Moderate'] = {
        'monthly_saving': moderate_saving,
        'annual_saving': moderate_saving * 12,
        'five_year_total': current_savings + (moderate_saving * 60)
    }
    
    # Aggressive scenario (save 90% of remaining disposable income)
    aggressive_saving = max(0, disposable_income * 0.9)
    scenarios['Aggressive'] = {
        'monthly_saving': aggressive_saving,
        'annual_saving': aggressive_saving * 12,
        'five_year_total': current_savings + (aggressive_saving * 60)
    }
    
    return scenarios

def analyze_committee_portfolio(user_committees):
    """Analyze user's committee portfolio for optimization"""
    
    if not user_committees:
        return {
            'portfolio_health': 'No committees',
            'recommendations': ['Consider joining 1-2 committees to start building wealth'],
            'risk_level': 'None',
            'diversification_score': 0
        }
    
    total_commitment = sum(c['monthly_amount'] for c in user_committees)
    
    # Analyze diversification
    categories = {}
    durations = []
    amounts = []
    
    for committee in user_committees:
        category = committee.get('category', 'General')
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
        
        durations.append(committee['duration'])
        amounts.append(committee['monthly_amount'])
    
    # Calculate diversification score
    category_diversity = len(categories) / max(1, len(user_committees))
    amount_variance = calculate_variance(amounts) if len(amounts) > 1 else 0
    duration_variance = calculate_variance(durations) if len(durations) > 1 else 0
    
    diversification_score = int((category_diversity * 40) + min(30, amount_variance/1000) + min(30, duration_variance))
    
    # Portfolio health assessment
    if len(user_committees) == 1:
        portfolio_health = 'Single Committee - High Concentration Risk'
        risk_level = 'High'
    elif len(user_committees) <= 3:
        portfolio_health = 'Small Portfolio - Moderate Diversification'
        risk_level = 'Medium'
    else:
        portfolio_health = 'Well Diversified Portfolio'
        risk_level = 'Low'
    
    # Generate recommendations
    recommendations = []
    
    if diversification_score < 30:
        recommendations.append("Improve diversification by joining committees in different categories")
    
    if len(set(durations)) == 1:
        recommendations.append("Mix short and long-term committees for better cash flow management")
    
    if max(amounts) > total_commitment * 0.6:
        recommendations.append("Reduce concentration risk - no single committee should exceed 60% of total commitment")
    
    if len(user_committees) > 5:
        recommendations.append("Consider reducing number of committees for better management")
    
    return {
        'portfolio_health': portfolio_health,
        'recommendations': recommendations,
        'risk_level': risk_level,
        'diversification_score': diversification_score,
        'total_commitment': total_commitment,
        'category_breakdown': categories
    }

def calculate_variance(values):
    """Calculate variance of a list of values"""
    if len(values) < 2:
        return 0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance

def generate_financial_insights(user_data, committees_data):
    """Generate comprehensive financial insights"""
    
    insights = {
        'strengths': [],
        'weaknesses': [],
        'opportunities': [],
        'threats': [],
        'overall_score': 0
    }
    
    monthly_income = user_data['monthly_income']
    monthly_expenses = user_data['monthly_expenses']
    current_savings = user_data['current_savings']
    
    # Calculate metrics
    savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100 if monthly_income > 0 else 0
    emergency_fund_months = current_savings / monthly_expenses if monthly_expenses > 0 else 0
    
    # Identify strengths
    if savings_rate > 20:
        insights['strengths'].append(f"Excellent savings rate of {savings_rate:.1f}%")
    
    if emergency_fund_months >= 6:
        insights['strengths'].append(f"Strong emergency fund covering {emergency_fund_months:.1f} months")
    
    if user_data.get('debt_amount', 0) == 0:
        insights['strengths'].append("Debt-free financial position")
    
    if monthly_income > 50000:
        insights['strengths'].append("Strong income foundation")
    
    # Identify weaknesses
    if savings_rate < 10:
        insights['weaknesses'].append(f"Low savings rate of {savings_rate:.1f}% - target 20%")
    
    if emergency_fund_months < 3:
        insights['weaknesses'].append(f"Insufficient emergency fund - only {emergency_fund_months:.1f} months covered")
    
    if (monthly_expenses / monthly_income) > 0.7:
        insights['weaknesses'].append("High expense ratio - consider expense reduction")
    
    # Identify opportunities
    committee_capacity = max(0, int((monthly_income - monthly_expenses) * 0.3))
    if committee_capacity > 5000:
        insights['opportunities'].append(f"Committee participation opportunity: Rs. {committee_capacity:,}/month capacity")
    
    if user_data.get('age', 30) < 35 and monthly_income > 30000:
        insights['opportunities'].append("Young professional advantage - time for aggressive wealth building")
    
    if len(committees_data) < 2:
        insights['opportunities'].append("Diversification opportunity - join committees in different categories")
    
    # Identify threats
    if user_data.get('dependents', 0) > 2 and emergency_fund_months < 6:
        insights['threats'].append("High dependents with low emergency fund - financial vulnerability")
    
    if savings_rate < 5:
        insights['threats'].append("Very low savings rate - risk of financial instability")
    
    total_committee_commitment = sum(c['monthly_amount'] for c in committees_data)
    if total_committee_commitment > (monthly_income - monthly_expenses) * 0.5:
        insights['threats'].append("Over-commitment to committees - cash flow risk")
    
    # Calculate overall score
    score = 50  # Base score
    score += len(insights['strengths']) * 10
    score -= len(insights['weaknesses']) * 8
    score += len(insights['opportunities']) * 5
    score -= len(insights['threats']) * 12
    
    insights['overall_score'] = max(0, min(100, score))
    
    return insights
