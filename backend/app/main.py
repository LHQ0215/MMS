from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, SessionLocal
from .routers import auth, users, patients, doctors, departments, appointments, ai_diagnosis, diagnosis_records, prescriptions, medicines, admin, notifications
from .utils.security import get_password_hash

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于AI问诊的医疗管理系统 API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(departments.router)
app.include_router(appointments.router)
app.include_router(ai_diagnosis.router)
app.include_router(diagnosis_records.router)
app.include_router(prescriptions.router)
app.include_router(medicines.router)
app.include_router(admin.router)
app.include_router(notifications.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Seed initial data if needed
    db = SessionLocal()
    try:
        from .models.user import User
        from .models.department import Department
        from .models.medicine import Medicine
        from .models.notification import Notification
        from .models.appointment import Appointment
        from .models.patient import Patient
        from .models.doctor import Doctor

        if db.query(User).count() == 0:
            admin_user = User(
                username="admin", real_name="系统管理员", role="admin",
                password_hash=get_password_hash("admin123"), is_active=True
            )
            db.add(admin_user)
            db.flush()

            test_patient = User(
                username="patient1", real_name="测试患者", role="patient",
                password_hash=get_password_hash("123456"), is_active=True
            )
            db.add(test_patient)
            db.flush()

            test_doctor = User(
                username="doctor1", real_name="张医生", role="doctor",
                password_hash=get_password_hash("123456"), is_active=True
            )
            db.add(test_doctor)
            db.flush()

        if db.query(Department).count() == 0:
            depts = [
                Department(id=1, name="内科", description="内科是临床医学的综合性科室"),
                Department(id=2, name="外科", description="外科主要处理需要手术治疗的疾病"),
                Department(id=3, name="儿科", description="儿科专门诊治儿童疾病"),
                Department(id=4, name="妇产科", description="妇产科专门处理女性生殖系统疾病"),
                Department(id=5, name="眼科", description="眼科专门诊治眼部疾病"),
                Department(id=6, name="耳鼻喉科", description="耳鼻喉科专门诊治耳鼻喉疾病"),
                Department(id=7, name="皮肤科", description="皮肤科专门诊治皮肤疾病"),
                Department(id=8, name="神经内科", description="神经内科专门诊治神经系统疾病", parent_id=1),
                Department(id=9, name="心血管内科", description="心血管内科专门诊治心血管疾病", parent_id=1),
                Department(id=10, name="骨科", description="骨科专门诊治骨骼肌肉系统疾病"),
                Department(id=11, name="急诊科", description="急诊科处理急危重症"),
                Department(id=12, name="中医科", description="中医科提供中医药诊疗服务"),
            ]
            for d in depts:
                db.add(d)
            db.flush()

        if db.query(Medicine).count() == 0:
            meds = [
                Medicine(name="阿莫西林胶囊", generic_name="Amoxicillin", category="抗生素",
                         specification="0.5g*24粒", manufacturer="华北制药", unit="盒", price=12.50, stock=500),
                Medicine(name="布洛芬缓释胶囊", generic_name="Ibuprofen", category="解热镇痛",
                         specification="0.3g*20粒", manufacturer="中美史克", unit="盒", price=18.90, stock=800, requires_prescription=False),
                Medicine(name="奥美拉唑肠溶胶囊", generic_name="Omeprazole", category="消化系统",
                         specification="20mg*14粒", manufacturer="丽珠集团", unit="盒", price=25.00, stock=300),
                Medicine(name="氯雷他定片", generic_name="Loratadine", category="抗过敏",
                         specification="10mg*12片", manufacturer="先灵葆雅", unit="盒", price=15.00, stock=400, requires_prescription=False),
                Medicine(name="盐酸二甲双胍片", generic_name="Metformin", category="降糖药",
                         specification="0.5g*60片", manufacturer="施贵宝", unit="盒", price=22.00, stock=200),
                Medicine(name="硝苯地平控释片", generic_name="Nifedipine", category="降压药",
                         specification="30mg*28片", manufacturer="拜耳", unit="盒", price=35.00, stock=250),
                Medicine(name="阿托伐他汀钙片", generic_name="Atorvastatin", category="降脂药",
                         specification="20mg*28片", manufacturer="辉瑞", unit="盒", price=45.00, stock=180),
                Medicine(name="维生素C片", generic_name="Vitamin C", category="维生素",
                         specification="100mg*100片", manufacturer="东北制药", unit="瓶", price=5.00, stock=1000, requires_prescription=False),
                Medicine(name="头孢克肟胶囊", generic_name="Cefixime", category="抗生素",
                         specification="100mg*6粒", manufacturer="广州白云山", unit="盒", price=28.00, stock=350),
                Medicine(name="蒙脱石散", generic_name="Montmorillonite", category="消化系统",
                         specification="3g*10袋", manufacturer="博福-益普生", unit="盒", price=12.00, stock=600, requires_prescription=False),
            ]
            for m in meds:
                db.add(m)

        if db.query(Doctor).count() == 0:
            doc_user = db.query(User).filter(User.username == "doctor1").first()
            if doc_user and doc_user.id:
                doctor = Doctor(
                    user_id=doc_user.id, title="副主任医师",
                    specialization="内科常见病、多发病的诊治",
                    department_id=1, license_number="MED20240001",
                    consultation_fee=20.00, max_daily_patients=40,
                    introduction="从事内科临床工作15年，擅长呼吸系统、消化系统疾病的诊治。",
                    is_approved=True
                )
                db.add(doctor)

        if db.query(Patient).count() == 0:
            pat_user = db.query(User).filter(User.username == "patient1").first()
            if pat_user and pat_user.id:
                patient = Patient(
                    user_id=pat_user.id, gender="male",
                    birth_date=None, allergies="无已知过敏史"
                )
                db.add(patient)

        db.commit()
        print("Seed data initialized")
    except Exception as e:
        db.rollback()
        print(f"Seed data error: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "欢迎使用AI医疗管理系统API", "version": settings.APP_VERSION}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

