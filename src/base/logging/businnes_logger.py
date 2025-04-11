"""
Business Logger
"""
import logging
import uuid
from typing import Dict, Any, Optional

business_logger = logging.getLogger("business")

class BusinessLogger:
    """Logger for tracking important business transactions"""
    
    @staticmethod
    def log_transaction(
        transaction_type: str,
        user_id: Optional[str],
        data: Dict[str, Any],
        status: str = "success",
        transaction_id: Optional[str] = None
    ):
        """Log a business transaction with structured data"""
        if not transaction_id:
            transaction_id = str(uuid.uuid4())
            
        business_logger.info(
            f"Business transaction: {transaction_type}",
            extra={
                "transaction_type": transaction_type,
                "transaction_id": transaction_id,
                "user_id": user_id,
                "status": status,
                "data": data
            }
        )
        
        return transaction_id
        
    @staticmethod
    def log_transaction_error(
        transaction_type: str,
        user_id: Optional[str],
        error: str,
        data: Dict[str, Any],
        transaction_id: Optional[str] = None
    ):
        """Log a failed business transaction"""
        if not transaction_id:
            transaction_id = str(uuid.uuid4())
            
        business_logger.error(
            f"Business transaction error: {transaction_type}",
            extra={
                "transaction_type": transaction_type,
                "transaction_id": transaction_id,
                "user_id": user_id,
                "status": "error",
                "error": error,
                "data": data
            }
        )
        
        return transaction_id
