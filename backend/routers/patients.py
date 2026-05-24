from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import database
import models
import schemas
import auth

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("/register", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
def register_patient(patient_data: schemas.PatientRegister, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.email == patient_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    user = models.User(
        email=patient_data.email,
        password_hash=auth.hash_password(patient_data.password),
        role="patient",
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        phone=patient_data.phone,
        subscription=patient_data.subscription,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    patient = models.Patient(
        user_id=user.id,
        date_of_birth=patient_data.date_of_birth,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "subscription": user.subscription,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "date_of_birth": patient.date_of_birth,
        "blood_group": patient.blood_group,
        "allergies": patient.allergies,
    }


@router.get("/me", response_model=schemas.PatientResponse)
def get_current_patient(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Pas un compte patient")
    patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Profil patient non trouvé")
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "subscription": current_user.subscription,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "date_of_birth": patient.date_of_birth,
        "blood_group": patient.blood_group,
        "allergies": patient.allergies,
    }


@router.get("/", response_model=list[schemas.PatientResponse])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    patients = db.query(models.Patient).offset(skip).limit(limit).all()
    result = []
    for p in patients:
        user = db.query(models.User).filter(models.User.id == p.user_id).first()
        result.append({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "subscription": user.subscription,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "date_of_birth": p.date_of_birth,
            "blood_group": p.blood_group,
            "allergies": p.allergies,
        })
    return result
