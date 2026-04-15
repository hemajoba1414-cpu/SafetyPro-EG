from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import requests
import json
import os

# --- 1. الإعدادات المؤمنة (Production Ready) ---
# يقرأ من Vercel Settings وإذا لم يجد يستخدم قيمة افتراضية (للمحلي فقط)
SECRET_KEY = os.getenv("SECRET_KEY", "SAFETY_PRO_2026_DEFAULT_KEY")
ALGORITHM = "HS256"
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 

# تعديل DATABASE_URL ليتناسب مع SQLAlchemy (خاصة لو Postgres)
db_url = os.getenv("DATABASE_URL", "sqlite:///./safetypro.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
Base = declarative_base()
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 2. قاعدة البيانات ---
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    plans = relationship("PlanDB", back_populates="owner", cascade="all, delete-orphan")

class PlanDB(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    project_name = Column(String)
    plan_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserDB", back_populates="plans")

# إنشاء الجداول
Base.metadata.create_all(bind=engine)

# --- 3. النماذج (Schemas) ---
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# --- 4. تشغيل التطبيق ---
app = FastAPI(title="SafetyPro 2026 Ultimate")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. الدوال المساعدة ---
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

def verify_token(authorization: str = Header(None)):
    if not authorization: 
        raise HTTPException(status_code=401, detail="Session Expired")
    try:
        token = authorization.split(" ")[1] if " " in authorization else authorization
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except: 
        raise HTTPException(status_code=401, detail="Invalid Session")

# --- 6. المسارات الرئيسية ---
@app.get("/")
def root():
    return {"status": "Active", "service": "SafetyPro API 2026"}

@app.post("/auth/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.email == user.email).first():
        raise HTTPException(status_code=400, detail="الإيميل مسجل بالفعل")
    new_user = UserDB(full_name=user.full_name, email=user.email, hashed_password=pwd_context.hash(user.password))
    db.add(new_user)
    db.commit()
    return {"status": "success"}

@app.post("/auth/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="بيانات خاطئة")
    token = jwt.encode({"sub": db_user.email, "exp": datetime.utcnow() + timedelta(days=7)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "user": {"full_name": db_user.full_name}}

@app.post("/generate-plan")
async def generate(data: dict, db: Session = Depends(get_db), user_email: str = Depends(verify_token)):
    project = data.get('projectName', 'General Project')
    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = (
        f"قم بدور خبير سلامة وصحة مهنية محترف. أنشئ جدول JSA (Job Safety Analysis) لمشروع: {project}. "
        "الجدول يجب أن يحتوي بدقة على: (تسلسل الخطوات | المخاطر المحتملة | إجراءات التحكم والسيطرة). "
        "التنسيق: Markdown Table فقط. اللغة: العربية."
    )
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 3000
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=40)
        res_data = res.json()
        if "choices" in res_data:
            ai_text = res_data['choices'][0]['message']['content']
        else:
            ai_text = "⚠️ حدث خطأ في التواصل مع الذكاء الاصطناعي."
    except Exception as e:
        ai_text = f"❌ فشل الاتصال: {str(e)}"

    new_plan = PlanDB(project_name=project, plan_content=ai_text, user_id=user.id)
    db.add(new_plan)
    db.commit()
    return {"plan_content": ai_text, "project_name": project}

@app.get("/my-plans")
async def list_plans(db: Session = Depends(get_db), user_email: str = Depends(verify_token)):
    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    plans = db.query(PlanDB).filter(PlanDB.user_id == user.id).order_by(desc(PlanDB.created_at)).all()
    return [
        {
            "id": p.id, 
            "project_name": p.project_name, 
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"), 
            "plan_content": p.plan_content
        } for p in plans
    ]

@app.delete("/delete-plan/{plan_id}")
async def delete_plan(plan_id: int, db: Session = Depends(get_db), user_email: str = Depends(verify_token)):
    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    plan = db.query(PlanDB).filter(PlanDB.id == plan_id, PlanDB.user_id == user.id).first()
    if plan:
        db.delete(plan)
        db.commit()
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="الخطة غير موجودة")
