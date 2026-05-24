from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import database
import models
import schemas
import auth

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/register", response_model=schemas.DoctorResponse, status_code=status.HTTP_201_CREATED)
def register_doctor(doctor_data: schemas.DoctorRegister, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.email == doctor_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    existing_license = db.query(models.Doctor).filter(models.Doctor.medical_license == doctor_data.medical_license).first()
    if existing_license:
        raise HTTPException(status_code=400, detail="Licence médicale déjà enregistrée")

    user = models.User(
        email=doctor_data.email,
        password_hash=auth.hash_password(doctor_data.password),
        role="doctor",
        first_name=doctor_data.first_name,
        last_name=doctor_data.last_name,
        phone=doctor_data.phone,
        subscription=doctor_data.subscription,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    doctor = models.Doctor(
        user_id=user.id,
        medical_license=doctor_data.medical_license,
        specialization=doctor_data.specialization,
        years_of_experience=doctor_data.years_of_experience,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

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
        "medical_license": doctor.medical_license,
        "specialization": doctor.specialization,
        "years_of_experience": doctor.years_of_experience,
        "rating": doctor.rating,
    }


@router.get("/me", response_model=schemas.DoctorResponse)
def get_current_doctor(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Pas un compte médecin")
    doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Profil médecin non trouvé")
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
        "medical_license": doctor.medical_license,
        "specialization": doctor.specialization,
        "years_of_experience": doctor.years_of_experience,
        "rating": doctor.rating,
    }


@router.get("/", response_model=list[schemas.DoctorResponse])
def list_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    doctors = db.query(models.Doctor).offset(skip).limit(limit).all()
    result = []
    for d in doctors:
        user = db.query(models.User).filter(models.User.id == d.user_id).first()
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
            "medical_license": d.medical_license,
            "specialization": d.specialization,
            "years_of_experience": d.years_of_experience,
            "rating": d.rating,
        })
    return result


@router.get("/specialization/{spec}", response_model=list[schemas.DoctorResponse])
def get_doctors_by_specialization(spec: str, db: Session = Depends(database.get_db)):
    doctors = db.query(models.Doctor).filter(models.Doctor.specialization == spec).all()
    result = []
    for d in doctors:
        user = db.query(models.User).filter(models.User.id == d.user_id).first()
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
            "medical_license": d.medical_license,
            "specialization": d.specialization,
            "years_of_experience": d.years_of_experience,
            "rating": d.rating,
        })
    return result
