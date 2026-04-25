"""
Utility and helper functions module.

Contains common utilities for ID generation, validation,
error handling, and other cross-cutting concerns.
"""

import uuid
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_loan_id() -> str:
    """
    Generate unique loan identifier.
    
    Returns:
        Loan ID in format: LOAN-{uuid}
    """
    return f"LOAN-{str(uuid.uuid4())[:12].upper()}"


def generate_log_id() -> str:
    """
    Generate unique log identifier.
    
    Returns:
        Log ID in format: LOG-{uuid}
    """
    return f"LOG-{str(uuid.uuid4())[:12].upper()}"


def generate_transaction_id() -> str:
    """
    Generate unique transaction identifier.
    
    Returns:
        Transaction ID in format: TXN-{uuid}
    """
    return f"TXN-{str(uuid.uuid4())[:12].upper()}"


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_loan_amount(amount: float, min_amount: float = 100, max_amount: float = 500_000) -> bool:
    """
    Validate loan amount within acceptable range.
    
    Args:
        amount: Loan amount to validate
        min_amount: Minimum acceptable amount
        max_amount: Maximum acceptable amount
    
    Returns:
        True if amount is valid, False otherwise
    """
    return min_amount <= amount <= max_amount


def validate_duration(duration_months: int, min_months: int = 1, max_months: int = 120) -> bool:
    """
    Validate loan duration.
    
    Args:
        duration_months: Loan duration to validate
        min_months: Minimum duration in months
        max_months: Maximum duration in months
    
    Returns:
        True if duration is valid, False otherwise
    """
    return min_months <= duration_months <= max_months


def calculate_monthly_payment(
    principal: float,
    annual_rate: float,
    months: int
) -> float:
    """
    Calculate monthly payment using amortization formula.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate (as decimal, e.g., 0.065 for 6.5%)
        months: Loan duration in months
    
    Returns:
        Monthly payment amount
    """
    if months <= 0:
        return 0.0
    
    monthly_rate = annual_rate / 12
    
    if monthly_rate == 0:
        return principal / months
    
    monthly_payment = principal * (
        monthly_rate * (1 + monthly_rate) ** months
    ) / ((1 + monthly_rate) ** months - 1)
    
    return round(monthly_payment, 2)


def calculate_total_interest(
    principal: float,
    monthly_payment: float,
    months: int
) -> float:
    """
    Calculate total interest over loan term.
    
    Args:
        principal: Loan principal amount
        monthly_payment: Monthly payment amount
        months: Loan duration in months
    
    Returns:
        Total interest amount
    """
    total_paid = monthly_payment * months
    return round(total_paid - principal, 2)


def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use
    
    Returns:
        Formatted currency string (e.g., "$1,234.56")
    """
    return f"{currency_symbol}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage string.
    
    Args:
        value: Value to format (as decimal, e.g., 0.065 for 6.5%)
        decimals: Number of decimal places
    
    Returns:
        Formatted percentage string (e.g., "6.50%")
    """
    return f"{value * 100:.{decimals}f}%"


def get_timestamp_string(dt: datetime = None) -> str:
    """
    Get ISO format timestamp string.
    
    Args:
        dt: Datetime object (uses current time if None)
    
    Returns:
        ISO format timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    
    return dt.isoformat()


def create_error_response(
    error_code: str,
    error_message: str,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error_code: Error code identifier
        error_message: Human-readable error message
        details: Additional error details
    
    Returns:
        Error response dictionary
    """
    return {
        "error": {
            "code": error_code,
            "message": error_message,
            "details": details or {},
            "timestamp": get_timestamp_string()
        }
    }


def create_success_response(
    data: Dict[str, Any] = None,
    message: str = "Success"
) -> Dict[str, Any]:
    """
    Create standardized success response.
    
    Args:
        data: Response data
        message: Success message
    
    Returns:
        Success response dictionary
    """
    return {
        "success": True,
        "message": message,
        "data": data or {},
        "timestamp": get_timestamp_string()
    }


class RequestValidator:
    """Utility class for request validation."""
    
    @staticmethod
    def validate_loan_request(request_data: Dict[str, Any]) -> tuple:
        """
        Validate loan request data.
        
        Args:
            request_data: Request data to validate
        
        Returns:
            Tuple of (is_valid: bool, errors: list)
        """
        errors = []
        
        if not request_data.get("borrower_id"):
            errors.append("borrower_id is required")
        
        if not request_data.get("amount"):
            errors.append("amount is required")
        elif not validate_loan_amount(request_data["amount"]):
            errors.append("amount must be between $100 and $500,000")
        
        if not request_data.get("duration_months"):
            errors.append("duration_months is required")
        elif not validate_duration(request_data["duration_months"]):
            errors.append("duration_months must be between 1 and 120")
        
        if not request_data.get("purpose"):
            errors.append("purpose is required")
        
        return len(errors) == 0, errors


logger = logging.getLogger(__name__)
