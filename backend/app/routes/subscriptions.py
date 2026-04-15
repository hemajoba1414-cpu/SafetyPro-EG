from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import stripe
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models import Subscription, User, Payment
from app.schemas import SubscriptionResponse, CreateCheckoutSession

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

STRIPE_PRICES = {
    "starter": "price_starter_monthly",  # Change with your actual Stripe price IDs
    "professional": "price_professional_monthly",
    "enterprise": "price_enterprise_monthly",
}

@router.get("/pricing")
def get_pricing():
    return {
        "plans": [
            {
                "name": "Free",
                "price": 0,
                "max_plans": 3,
                "features": ["Basic safety plans", "Community support"]
            },
            {
                "name": "Starter",
                "price": 9.99,
                "max_plans": 20,
                "features": ["All Free features", "PDF export", "Email support"]
            },
            {
                "name": "Professional",
                "price": 29.99,
                "max_plans": 100,
                "features": ["All Starter features", "Advanced analytics", "Priority support"]
            },
            {
                "name": "Enterprise",
                "price": 99.99,
                "max_plans": "Unlimited",
                "features": ["All Professional features", "Dedicated support", "Custom integrations"]
            }
        ]
    }

@router.get("/current", response_model=SubscriptionResponse)
def get_current_subscription(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not sub:
        sub = Subscription(user_id=user_id, plan_type="free")
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub

@router.post("/checkout")
def create_checkout_session(data: CreateCheckoutSession, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    try:
        session = stripe.checkout.Session.create(
            customer_email=user.email,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": STRIPE_PRICES.get(data.plan_type, STRIPE_PRICES["starter"]),
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url="http://localhost:3000/subscription/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/subscription/cancelled",
            metadata={
                "user_id": user_id,
                "plan_type": data.plan_type
            }
        )
        
        return {"checkout_url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = int(session['metadata']['user_id'])
        plan_type = session['metadata']['plan_type']
        
        db = next(get_db())
        subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
        if subscription:
            subscription.stripe_subscription_id = session.get('subscription')
            subscription.stripe_customer_id = session.get('customer')
            subscription.plan_type = plan_type
            subscription.is_active = True
            db.commit()
    
    return {"status": "success"}
