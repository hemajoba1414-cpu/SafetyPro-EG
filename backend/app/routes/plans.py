from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Plan
from app.schemas import PlanCreate, PlanUpdate, PlanResponse

router = APIRouter(prefix="/plans", tags=["plans"])

@router.get("/", response_model=List[PlanResponse])
def get_plans(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    plans = db.query(Plan).filter(Plan.user_id == user_id).all()
    return plans

@router.post("/", response_model=PlanResponse)
def create_plan(plan: PlanCreate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    db_plan = Plan(
        user_id=user_id,
        title=plan.title,
        description=plan.description,
        steps=json.dumps([step.dict() for step in plan.steps])
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    db_plan.steps = json.loads(db_plan.steps)
    return db_plan

@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan.steps = json.loads(plan.steps)
    return plan

@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, plan_update: PlanUpdate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan_update.title:
        plan.title = plan_update.title
    if plan_update.description:
        plan.description = plan_update.description
    if plan_update.steps:
        plan.steps = json.dumps([step.dict() for step in plan_update.steps])
    if plan_update.status:
        plan.status = plan_update.status
    
    db.commit()
    db.refresh(plan)
    plan.steps = json.loads(plan.steps)
    return plan

@router.delete("/{plan_id}")
def delete_plan(plan_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db.delete(plan)
    db.commit()
    return {"detail": "Plan deleted successfully"}
