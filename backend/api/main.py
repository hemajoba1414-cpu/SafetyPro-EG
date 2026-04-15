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

# --- 1. الإعدادات النهائية (Production Settings) ---
SECRET_KEY = "SAFETY_PRO_2026_EGY_ULTIMATE"
ALGORITHM = "HS256"
# مفتاح Groq الخاص بك (مؤمن وجاهز)
GROQ_API_KEY = "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" 

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
Base = declarative_base()
engine = create_engine("sqlite:///./safetypro.db", connect_args={"check_same_thread": False})
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

Base.metadata.create_all(bind=engine)

# --- 3. النماذج ---
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
    allow_origins=["*"], # مهم جداً للوصول من الموبايل أو أي دومين خارجي
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. الدوال المساعدة ---
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def verify_token(authorization: str = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Session Expired")
    try:
        token = authorization.split(" ")[1] if " " in authorization else authorization
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except: raise HTTPException(status_code=401, detail="Invalid Session")

# --- 6. المسارات (Authentication) ---
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
    token = jwt.encode({"sub": db_user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "user": {"full_name": db_user.full_name}}

# --- 7. توليد الخطط (The Engine) ---
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
        "model": "llama-3.1-8b-instant", # الموديل الأحدث والمستقر حالياً
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 3000
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=40)
        res_data = res.json()
        
        # معالجة ذكية للرد لتجنب أخطاء المفاتيح المفقودة
        if "choices" in res_data and len(res_data["choices"]) > 0:
            ai_text = res_data['choices'][0]['message']['content']
        elif "error" in res_data:
            ai_text = f"⚠️ خطأ من الذكاء الاصطناعي: {res_data['error'].get('message', 'خطأ غير معروف')}"
        else:
            ai_text = "⚠️ لم يتم استلام رد صحيح من السيرفر."
            
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
async def delete_plan(plan_id: int, db: Session = Depends(get_db), user_uvicorn api.main:app --reloademail: str = Depends(verify_token)):
    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    plan = db.query(PlanDB).filter(PlanDB.id == plan_id, PlanDB.user_id == user.id).first()
    if plan:
        db.delete(plan)
        db.commit()
    return {"status": "deleted"}