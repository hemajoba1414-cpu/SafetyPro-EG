from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Plan

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/pdf/{plan_id}")
def export_plan_to_pdf(plan_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f2937'
    )
    elements.append(Paragraph(plan.title, title_style))
    elements.append(Spacer(1, 0.2 * 72))
    
    # Add description
    elements.append(Paragraph(plan.description, styles['Normal']))
    elements.append(Spacer(1, 0.2 * 72))
    
    # Add steps
    elements.append(Paragraph("Safety Steps:", styles['Heading2']))
    steps = json.loads(plan.steps)
    for i, step in enumerate(steps, 1):
        elements.append(Paragraph(f"<b>{i}. {step['title']}</b>", styles['Normal']))
        elements.append(Paragraph(step['description'], styles['Normal']))
        elements.append(Spacer(1, 0.1 * 72))
    
    doc.build(elements)
    buffer.seek(0)
    
    return {
        "pdf": buffer.getvalue().hex(),
        "filename": f"{plan.title.replace(' ', '_')}.pdf"
    }
