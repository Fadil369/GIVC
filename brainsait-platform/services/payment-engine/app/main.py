#!/usr/bin/env python3
"""
PaymentLINC - Payment Processing Engine
OID: 1.3.6.1.4.1.61026.5.1
Integrates with Stripe, Mada, and STC Pay for payment processing
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
import httpx
import os
import logging
from datetime import datetime
import hashlib
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PaymentLINC",
    description="Payment Processing Engine - Multi-Gateway Support",
    version="1.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
MADA_API_KEY = os.getenv("MADA_API_KEY", "")
STC_PAY_API_KEY = os.getenv("STC_PAY_API_KEY", "")
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://oid-registry:8000")

# Enums
class PaymentGateway(str, Enum):
    STRIPE = "stripe"
    MADA = "mada"
    STC_PAY = "stc_pay"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class Currency(str, Enum):
    SAR = "SAR"
    USD = "USD"
    EUR = "EUR"

# Models
class PaymentIntent(BaseModel):
    amount: float
    currency: Currency = Currency.SAR
    gateway: PaymentGateway
    customer_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}

class Payment(BaseModel):
    id: str
    amount: float
    currency: Currency
    gateway: PaymentGateway
    status: PaymentStatus
    customer_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    transaction_id: Optional[str] = None

class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = None  # Partial refund if specified
    reason: Optional[str] = None

class ValidationRequest(BaseModel):
    card_number: str
    exp_month: int
    exp_year: int
    cvv: str

# In-memory storage (replace with actual database in production)
payments_db: Dict[str, Payment] = {}

def generate_payment_id() -> str:
    """Generate unique payment ID"""
    return f"pay_{secrets.token_hex(16)}"

def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    return f"txn_{secrets.token_hex(12)}"

async def process_stripe_payment(intent: PaymentIntent) -> Dict[str, Any]:
    """Process payment through Stripe"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    try:
        # In production, use actual Stripe SDK
        # import stripe
        # stripe.api_key = STRIPE_SECRET_KEY
        # payment_intent = stripe.PaymentIntent.create(
        #     amount=int(intent.amount * 100),
        #     currency=intent.currency.lower(),
        #     description=intent.description,
        #     metadata=intent.metadata
        # )
        
        # Mock response for demonstration
        return {
            "transaction_id": generate_transaction_id(),
            "status": PaymentStatus.SUCCEEDED,
            "gateway_response": {
                "provider": "stripe",
                "success": True
            }
        }
    except Exception as e:
        logger.error(f"Stripe payment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stripe payment failed: {str(e)}")

async def process_mada_payment(intent: PaymentIntent) -> Dict[str, Any]:
    """Process payment through Mada (Saudi Arabia local payment)"""
    if not MADA_API_KEY:
        raise HTTPException(status_code=503, detail="Mada not configured")
    
    try:
        # Mock Mada API integration
        # In production, integrate with actual Mada gateway
        return {
            "transaction_id": generate_transaction_id(),
            "status": PaymentStatus.PROCESSING,
            "gateway_response": {
                "provider": "mada",
                "success": True
            }
        }
    except Exception as e:
        logger.error(f"Mada payment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mada payment failed: {str(e)}")

async def process_stc_pay_payment(intent: PaymentIntent) -> Dict[str, Any]:
    """Process payment through STC Pay"""
    if not STC_PAY_API_KEY:
        raise HTTPException(status_code=503, detail="STC Pay not configured")
    
    try:
        # Mock STC Pay API integration
        # In production, integrate with actual STC Pay API
        return {
            "transaction_id": generate_transaction_id(),
            "status": PaymentStatus.SUCCEEDED,
            "gateway_response": {
                "provider": "stc_pay",
                "success": True
            }
        }
    except Exception as e:
        logger.error(f"STC Pay payment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"STC Pay payment failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "paymentlinc",
        "oid": "1.3.6.1.4.1.61026.5.1",
        "version": "1.5.0",
        "gateways": {
            "stripe": bool(STRIPE_SECRET_KEY),
            "mada": bool(MADA_API_KEY),
            "stc_pay": bool(STC_PAY_API_KEY)
        },
        "payments_count": len(payments_db)
    }

@app.post("/api/v1/payments/charge")
async def create_payment(intent: PaymentIntent, background_tasks: BackgroundTasks):
    """Create and process a payment"""
    payment_id = generate_payment_id()
    
    # Process payment based on gateway
    try:
        if intent.gateway == PaymentGateway.STRIPE:
            result = await process_stripe_payment(intent)
        elif intent.gateway == PaymentGateway.MADA:
            result = await process_mada_payment(intent)
        elif intent.gateway == PaymentGateway.STC_PAY:
            result = await process_stc_pay_payment(intent)
        else:
            raise HTTPException(status_code=400, detail="Unsupported payment gateway")
        
        # Create payment record
        payment = Payment(
            id=payment_id,
            amount=intent.amount,
            currency=intent.currency,
            gateway=intent.gateway,
            status=result["status"],
            customer_id=intent.customer_id,
            description=intent.description,
            metadata=intent.metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            transaction_id=result["transaction_id"]
        )
        
        payments_db[payment_id] = payment
        
        logger.info(f"Payment created: {payment_id} - {intent.amount} {intent.currency} via {intent.gateway}")
        
        return {
            "status": "success",
            "payment": payment,
            "gateway_response": result.get("gateway_response")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")

@app.get("/api/v1/payments/{payment_id}")
async def get_payment(payment_id: str):
    """Get payment details"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payments_db[payment_id]

@app.get("/api/v1/payments")
async def list_payments(
    status: Optional[PaymentStatus] = None,
    gateway: Optional[PaymentGateway] = None,
    limit: int = 50
):
    """List all payments with optional filters"""
    payments = list(payments_db.values())
    
    if status:
        payments = [p for p in payments if p.status == status]
    
    if gateway:
        payments = [p for p in payments if p.gateway == gateway]
    
    # Sort by created_at desc
    payments.sort(key=lambda p: p.created_at, reverse=True)
    
    return {
        "total": len(payments),
        "payments": payments[:limit]
    }

@app.post("/api/v1/payments/refund")
async def refund_payment(refund_req: RefundRequest):
    """Refund a payment (full or partial)"""
    if refund_req.payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment = payments_db[refund_req.payment_id]
    
    if payment.status != PaymentStatus.SUCCEEDED:
        raise HTTPException(status_code=400, detail="Only succeeded payments can be refunded")
    
    refund_amount = refund_req.amount or payment.amount
    
    if refund_amount > payment.amount:
        raise HTTPException(status_code=400, detail="Refund amount exceeds payment amount")
    
    try:
        # Process refund through gateway
        # In production, call actual gateway refund API
        
        # Update payment status
        payment.status = PaymentStatus.REFUNDED
        payment.updated_at = datetime.utcnow()
        payment.metadata["refund"] = {
            "amount": refund_amount,
            "reason": refund_req.reason,
            "refunded_at": datetime.utcnow().isoformat()
        }
        
        payments_db[refund_req.payment_id] = payment
        
        logger.info(f"Payment refunded: {refund_req.payment_id} - {refund_amount} {payment.currency}")
        
        return {
            "status": "refunded",
            "payment_id": refund_req.payment_id,
            "refund_amount": refund_amount,
            "payment": payment
        }
        
    except Exception as e:
        logger.error(f"Refund failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Refund failed: {str(e)}")

@app.post("/api/v1/payments/validate")
async def validate_card(validation_req: ValidationRequest):
    """Validate credit/debit card details"""
    try:
        # Basic validation
        card_number = validation_req.card_number.replace(" ", "")
        
        # Check card number length
        if len(card_number) not in [13, 14, 15, 16, 19]:
            return {
                "valid": False,
                "error": "Invalid card number length"
            }
        
        # Luhn algorithm validation
        def luhn_check(card_number):
            digits = [int(d) for d in card_number]
            checksum = 0
            for i, digit in enumerate(reversed(digits)):
                if i % 2 == 1:
                    digit *= 2
                    if digit > 9:
                        digit -= 9
                checksum += digit
            return checksum % 10 == 0
        
        if not luhn_check(card_number):
            return {
                "valid": False,
                "error": "Invalid card number (Luhn check failed)"
            }
        
        # Detect card type
        card_type = "unknown"
        if card_number.startswith("4"):
            card_type = "visa"
        elif card_number.startswith(("51", "52", "53", "54", "55")):
            card_type = "mastercard"
        elif card_number.startswith("5078"):
            card_type = "mada"
        
        # Validate expiration
        current_year = datetime.utcnow().year % 100
        current_month = datetime.utcnow().month
        
        if validation_req.exp_year < current_year:
            return {
                "valid": False,
                "error": "Card expired"
            }
        
        if validation_req.exp_year == current_year and validation_req.exp_month < current_month:
            return {
                "valid": False,
                "error": "Card expired"
            }
        
        return {
            "valid": True,
            "card_type": card_type,
            "last_four": card_number[-4:]
        }
        
    except Exception as e:
        logger.error(f"Card validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/api/v1/payments/stats")
async def get_payment_stats():
    """Get payment statistics"""
    payments = list(payments_db.values())
    
    total_amount = sum(p.amount for p in payments if p.status == PaymentStatus.SUCCEEDED)
    total_refunded = sum(
        p.metadata.get("refund", {}).get("amount", 0) 
        for p in payments if p.status == PaymentStatus.REFUNDED
    )
    
    stats_by_gateway = {}
    for gateway in PaymentGateway:
        gateway_payments = [p for p in payments if p.gateway == gateway]
        stats_by_gateway[gateway.value] = {
            "count": len(gateway_payments),
            "total": sum(p.amount for p in gateway_payments if p.status == PaymentStatus.SUCCEEDED)
        }
    
    return {
        "total_payments": len(payments),
        "total_amount": total_amount,
        "total_refunded": total_refunded,
        "by_gateway": stats_by_gateway,
        "by_status": {
            status.value: len([p for p in payments if p.status == status])
            for status in PaymentStatus
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
