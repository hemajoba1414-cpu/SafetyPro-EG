from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ====== User Schemas ======
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ====== Auth Schemas ======
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginResponse(TokenResponse):
    remaining_days: int
    status: str
    user: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ====== Plan Schemas ======
class Step(BaseModel):
    title: str
    description: str

class PlanCreate(BaseModel):
    title: str
    description: str
    steps: List[Step]

class PlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[Step]] = None
    status: Optional[str] = None

class PlanResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    steps: List[Step]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ====== Subscription Schemas ======
class SubscriptionPlans(BaseModel):
    plan_name: str
    price: float
    max_plans: int
    features: List[str]

class SubscriptionResponse(BaseModel):
    id: int
    plan_type: str
    is_active: bool
    current_period_end: Optional[datetime]
    
    class Config:
        from_attributes = True

class CreateCheckoutSession(BaseModel):
    plan_type: str  # starter, professional, enterprise

class WebhookEvent(BaseModel):
    type: str
    data: dict
# ====== AI Generation Schemas ======
class GeneratePlanRequest(BaseModel):
    projectName: str
    risks: List[str]