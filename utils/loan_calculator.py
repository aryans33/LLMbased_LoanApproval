"""
Loan Approval Logic Module
Handles DTI calculation, approval decisions, and business rules
"""

from typing import Dict, Tuple, Optional
from enum import Enum


class ApprovalStatus(Enum):
    """Loan approval status enumeration"""
    APPROVED = "approved"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"
    INSUFFICIENT_DATA = "insufficient_data"


class EmploymentStatus(Enum):
    """Employment status enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"


class CreditScoreRange(Enum):
    """Credit score range categories"""
    EXCELLENT = "excellent"  # 750+
    GOOD = "good"  # 700-749
    FAIR = "fair"  # 650-699
    POOR = "poor"  # 600-649
    VERY_POOR = "very_poor"  # <600


class LoanApprovalCalculator:
    """Handles loan approval calculations and decision logic"""
    
    # DTI Ratio Thresholds
    DTI_APPROVED_MAX = 36.0
    DTI_CONDITIONAL_MAX = 43.0
    
    # Minimum requirements
    MIN_INCOME = 15000  # Minimum monthly income in rupees
    MIN_CREDIT_SCORE = 580  # FHA minimum
    
    def __init__(self):
        self.required_fields = [
            'gross_monthly_income',
            'total_monthly_debt',
            'loan_amount',
            'employment_status',
            'credit_score_range'
        ]
    
    def calculate_dti(self, gross_monthly_income: float, total_monthly_debt: float) -> float:
        """
        Calculate Debt-to-Income ratio
        
        Args:
            gross_monthly_income: Total monthly income before taxes
            total_monthly_debt: Total monthly debt payments
            
        Returns:
            DTI ratio as percentage
        """
        if gross_monthly_income <= 0:
            raise ValueError("Gross monthly income must be greater than zero")
        
        dti_ratio = (total_monthly_debt / gross_monthly_income) * 100
        return round(dti_ratio, 2)
    
    def check_data_completeness(self, applicant_data: Dict) -> Tuple[bool, list]:
        """
        Check if all required data is present
        
        Args:
            applicant_data: Dictionary of applicant information
            
        Returns:
            Tuple of (is_complete, missing_fields)
        """
        missing_fields = []
        
        for field in self.required_fields:
            if field not in applicant_data or applicant_data[field] is None:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
    
    def evaluate_application(self, applicant_data: Dict) -> Dict:
        """
        Evaluate loan application and return decision
        
        Args:
            applicant_data: Dictionary containing:
                - gross_monthly_income: float
                - total_monthly_debt: float
                - loan_amount: float
                - employment_status: str
                - credit_score_range: str
                
        Returns:
            Dictionary with decision details
        """
        # Check data completeness
        is_complete, missing_fields = self.check_data_completeness(applicant_data)
        
        if not is_complete:
            return {
                'status': ApprovalStatus.INSUFFICIENT_DATA.value,
                'decision': 'Cannot process application',
                'reason': f'Missing required information: {", ".join(missing_fields)}',
                'missing_fields': missing_fields,
                'dti_ratio': None,
                'recommendations': ['Please provide all required information to proceed']
            }
        
        # Extract data
        gross_income = float(applicant_data['gross_monthly_income'])
        monthly_debt = float(applicant_data['total_monthly_debt'])
        loan_amount = float(applicant_data['loan_amount'])
        employment_status = applicant_data['employment_status']
        credit_score = applicant_data['credit_score_range']
        
        # Calculate DTI
        try:
            dti_ratio = self.calculate_dti(gross_income, monthly_debt)
        except ValueError as e:
            return {
                'status': ApprovalStatus.REJECTED.value,
                'decision': 'Application Rejected',
                'reason': str(e),
                'dti_ratio': None,
                'recommendations': ['Income must be greater than zero']
            }
        
        # Initialize decision components
        status = None
        decision = ""
        reasons = []
        recommendations = []
        
        # Check minimum requirements
        if gross_income < self.MIN_INCOME:
            status = ApprovalStatus.REJECTED.value
            reasons.append(f'Monthly income (₹{gross_income:,.2f}) is below minimum requirement (₹{self.MIN_INCOME:,.2f})')
        
        if employment_status == EmploymentStatus.UNEMPLOYED.value:
            status = ApprovalStatus.REJECTED.value
            reasons.append('Applicant must have employment or income source')
        
        # Evaluate based on DTI ratio
        if status is None:
            if dti_ratio <= self.DTI_APPROVED_MAX:
                status = ApprovalStatus.APPROVED.value
                decision = 'Application Approved'
                reasons.append(f'Debt-to-Income ratio ({dti_ratio}%) is excellent')
                recommendations.extend([
                    'Proceed with document submission',
                    'Upload proof of income (recent pay stubs)',
                    'Upload proof of identity (driver\'s license)',
                    'Submit bank statements (last 2 months)'
                ])
                
            elif dti_ratio <= self.DTI_CONDITIONAL_MAX:
                status = ApprovalStatus.CONDITIONAL.value
                decision = 'Application Conditionally Approved'
                reasons.append(f'Debt-to-Income ratio ({dti_ratio}%) requires additional review')
                recommendations.extend([
                    'Application requires manual underwriting review',
                    'Consider reducing monthly debt obligations',
                    'Provide additional documentation of income stability',
                    'May require higher down payment',
                    'Co-signer might improve approval chances'
                ])
                
            else:
                status = ApprovalStatus.REJECTED.value
                decision = 'Application Rejected'
                reasons.append(f'Debt-to-Income ratio ({dti_ratio}%) exceeds maximum threshold (43%)')
                recommendations.extend([
                    'Reduce monthly debt payments before reapplying',
                    'Increase gross monthly income',
                    'Consider a smaller loan amount',
                    f'Target DTI ratio below 43% (currently {dti_ratio}%)',
                    'Seek credit counseling for debt management'
                ])
        
        # Add credit score considerations
        if credit_score == CreditScoreRange.POOR.value or credit_score == CreditScoreRange.VERY_POOR.value:
            if status == ApprovalStatus.APPROVED.value:
                status = ApprovalStatus.CONDITIONAL.value
                decision = 'Application Conditionally Approved'
            reasons.append('Credit score is below preferred range')
            recommendations.append('Work on improving credit score for better terms')
        
        return {
            'status': status,
            'decision': decision,
            'reason': ' | '.join(reasons) if reasons else 'Based on financial profile assessment',
            'dti_ratio': dti_ratio,
            'recommendations': recommendations,
            'applicant_summary': {
                'monthly_income': f'₹{gross_income:,.2f}',
                'monthly_debt': f'₹{monthly_debt:,.2f}',
                'loan_amount': f'₹{loan_amount:,.2f}',
                'dti_percentage': f'{dti_ratio}%',
                'employment': employment_status,
                'credit_range': credit_score
            }
        }
    
    def format_currency(self, amount: float) -> str:
        """Format number as Indian currency"""
        return f'₹{amount:,.2f}'


# Test the calculator
if __name__ == "__main__":
    calculator = LoanApprovalCalculator()
    
    test_cases = [
        {
            'name': 'Approved Application',
            'data': {
                'gross_monthly_income': 6000,
                'total_monthly_debt': 1800,
                'loan_amount': 200000,
                'employment_status': 'full_time',
                'credit_score_range': 'good'
            }
        },
        {
            'name': 'Conditional Application',
            'data': {
                'gross_monthly_income': 5000,
                'total_monthly_debt': 2000,
                'loan_amount': 180000,
                'employment_status': 'full_time',
                'credit_score_range': 'fair'
            }
        },
        {
            'name': 'Rejected Application',
            'data': {
                'gross_monthly_income': 4000,
                'total_monthly_debt': 2200,
                'loan_amount': 150000,
                'employment_status': 'part_time',
                'credit_score_range': 'poor'
            }
        }
    ]
    
    print("=== Loan Approval Calculator Tests ===\n")
    for test in test_cases:
        print(f"Test: {test['name']}")
        result = calculator.evaluate_application(test['data'])
        print(f"Decision: {result['decision']}")
        print(f"Status: {result['status']}")
        print(f"DTI Ratio: {result['dti_ratio']}%")
        print(f"Reason: {result['reason']}")
        print(f"Recommendations: {result['recommendations'][:2]}")
        print()
