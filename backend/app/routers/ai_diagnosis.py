from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from ..models.patient import Patient
from ..models.doctor import Doctor
from ..models.department import Department
from ..models.ai_consultation import AIConsultation, Severity, RiskLevel
from ..schemas.ai_consultation import AIConsultationCreate, AIConsultationResponse
from ..utils.security import get_current_user_id
from ..models.ai_chat import AIChatSession, AIChatMessage
from ..schemas.ai_chat import ChatSessionCreate, ChatSessionResponse, ChatMessageRequest, ChatMessageResponse, ChatSessionDetailResponse
from ..services.ai_service import ai_diagnosis_service, ai_chat_service
import datetime

router = APIRouter(prefix="/api/ai", tags=["AI问诊"])

@router.post("/diagnose")
def ai_diagnose(
    req: AIConsultationCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        raise HTTPException(status_code=400, detail="请先完善患者信息")
    
    severity_map = {"mild": Severity.MILD, "moderate": Severity.MODERATE, "severe": Severity.SEVERE}
    severity = severity_map.get(req.severity, Severity.MILD)
    
    consultation = AIConsultation(
        patient_id=patient.id,
        symptoms=req.symptoms,
        symptom_duration=req.symptom_duration,
        severity=severity
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    
    # Call AI service
    try:
        result = ai_diagnosis_service.diagnose(req.symptoms, req.symptom_duration, req.severity)
        consultation.ai_diagnosis = result.get("diagnosis", "")
        consultation.confidence = result.get("confidence", 0)
        consultation.suggested_department = result.get("department", "")
        consultation.risk_level = result.get("risk_level", RiskLevel.LOW)
        consultation.advice = result.get("advice", "")
        
        # Auto-refer to suggested department
        if result.get("department"):
            dept = db.query(Department).filter(Department.name.like(f"%{result['department']}%")).first()
            if dept:
                consultation.suggested_department = dept.name
                doctor = db.query(Doctor).filter(
                    Doctor.department_id == dept.id, Doctor.is_approved == True
                ).first()
                if doctor:
                    consultation.suggested_doctor_id = doctor.id
        db.commit()
        db.refresh(consultation)
    except Exception as e:
        consultation.ai_diagnosis = "AI诊断服务暂不可用，请稍后再试。"
        consultation.advice = "建议尽快就医，由专业医生进行诊断"
        consultation.risk_level = RiskLevel.LOW
        db.commit()
    
    return {
        "id": consultation.id,
        "symptoms": consultation.symptoms,
        "symptom_duration": consultation.symptom_duration,
        "severity": consultation.severity.value if hasattr(consultation.severity, "value") else consultation.severity,
        "ai_diagnosis": consultation.ai_diagnosis or "",
        "confidence": float(consultation.confidence) if consultation.confidence else 0,
        "suggested_department": consultation.suggested_department or "",
        "risk_level": consultation.risk_level.value if hasattr(consultation.risk_level, "value") else consultation.risk_level,
        "advice": consultation.advice or "",
        "is_referred": consultation.is_referred,
        "created_at": consultation.created_at
    }

@router.get("/history")
def get_ai_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.user_id == user_id).first()
    if not patient:
        return {"total": 0, "items": []}
    query = db.query(AIConsultation).filter(AIConsultation.patient_id == patient.id)
    total = query.count()
    items = query.order_by(AIConsultation.created_at.desc()).offset((page-1)*size).limit(size).all()
    result = []
    for c in items:
        result.append({
            "id": c.id, "symptoms": c.symptoms,
            "ai_diagnosis": c.ai_diagnosis or "",
            "confidence": float(c.confidence) if c.confidence else 0,
            "suggested_department": c.suggested_department or "",
            "risk_level": c.risk_level.value if hasattr(c.risk_level, "value") else c.risk_level,
            "is_referred": c.is_referred, "created_at": c.created_at
        })
    return {"total": total, "items": result}



# ==================== AI Chat (Free-form DeepSeek-style) ====================


@router.post("/chat/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    req: ChatSessionCreate = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    session = AIChatSession(user_id=user_id, title="新对话")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/chat/sessions", response_model=List[ChatSessionResponse])
def list_chat_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    sessions = db.query(AIChatSession).filter(
        AIChatSession.user_id == user_id
    ).order_by(AIChatSession.updated_at.desc()).all()
    return sessions


@router.delete("/chat/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    session = db.query(AIChatSession).filter(
        AIChatSession.id == session_id,
        AIChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(session)
    db.commit()
    return {"message": "删除成功"}


@router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    session = db.query(AIChatSession).filter(
        AIChatSession.id == session_id,
        AIChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    messages = db.query(AIChatMessage).filter(
        AIChatMessage.session_id == session_id
    ).order_by(AIChatMessage.created_at.asc()).all()
    return messages


@router.post("/chat/sessions/{session_id}/messages")
def send_chat_message(
    session_id: int,
    req: ChatMessageRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    session = db.query(AIChatSession).filter(
        AIChatSession.id == session_id,
        AIChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # Save user message
    user_msg = AIChatMessage(session_id=session_id, role="user", content=req.content)
    db.add(user_msg)
    db.commit()
    
    # Build message history for AI
    messages = db.query(AIChatMessage).filter(
        AIChatMessage.session_id == session_id
    ).order_by(AIChatMessage.created_at.asc()).all()
    
    history = [{"role": "system", "content": "你是一个乐于助人的AI助手，可以回答医疗健康问题以及各类日常问题。对于医疗问题请提供参考信息并提醒用户及时就医，但不要给出确切的诊断结论。"}]
    for m in messages:
        history.append({"role": m.role, "content": m.content})
    
    # Call AI service
    try:
        ai_response = ai_chat_service.chat(history)
    except Exception as e:
        ai_response = "抱歉，AI服务暂时不可用，请稍后再试。"
    
    # Save AI response
    assistant_msg = AIChatMessage(session_id=session_id, role="assistant", content=ai_response)
    db.add(assistant_msg)
    
    # Auto-generate title from first user message
    first_msg = db.query(AIChatMessage).filter(
        AIChatMessage.session_id == session_id,
        AIChatMessage.role == "user"
    ).order_by(AIChatMessage.created_at.asc()).first()
    if first_msg and session.title == "新对话":
        title = first_msg.content[:30]
        if len(first_msg.content) > 30:
            title += "..."
        session.title = title
    
    db.commit()
    db.refresh(assistant_msg)
    
    return {
        "user_message": {"id": user_msg.id, "role": "user", "content": user_msg.content, "created_at": user_msg.created_at.isoformat()},
        "assistant_message": {"id": assistant_msg.id, "role": "assistant", "content": assistant_msg.content, "created_at": assistant_msg.created_at.isoformat()}
    }
