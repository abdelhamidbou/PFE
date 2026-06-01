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
        gender=patient_data.gender,
        city=patient_data.city,
        address=patient_data.address,
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
        "gender": user.gender,
        "city": user.city,
        "address": user.address,
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
        "gender": current_user.gender,
        "city": current_user.city,
        "address": current_user.address,
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
            "gender": user.gender,
            "city": user.city,
            "address": user.address,
            "subscription": user.subscription,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "date_of_birth": p.date_of_birth,
            "blood_group": p.blood_group,
            "allergies": p.allergies,
        })
    return result


# --- Endpoints Profil Dermatologique ---

@router.get("/dermatology-profile", response_model=schemas.DermatologyProfileResponse)
def get_my_dermatology_profile(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Pas un compte patient")
    profile = db.query(models.DermatologyProfile).filter(models.DermatologyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil dermatologique non trouvé")
    return profile


@router.put("/dermatology-profile", response_model=schemas.DermatologyProfileResponse)
def update_my_dermatology_profile(data: schemas.DermatologyProfileCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Pas un compte patient")
    profile = db.query(models.DermatologyProfile).filter(models.DermatologyProfile.user_id == current_user.id).first()
    if not profile:
        profile = models.DermatologyProfile(user_id=current_user.id)
        db.add(profile)
    for field in ["skin_conditions", "drug_allergies", "current_treatments", "skin_type", "fitzpatrick_phototype", "chronic_diseases", "family_history", "smoking_alcohol", "occupational_exposure"]:
        value = getattr(data, field, None)
        if value is not None:
            setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/dermatology-profile", response_model=schemas.DermatologyProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_dermatology_profile(data: schemas.DermatologyProfileCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Pas un compte patient")
    existing = db.query(models.DermatologyProfile).filter(models.DermatologyProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profil dermatologique existe déjà. Utilisez PUT pour le modifier.")
    profile = models.DermatologyProfile(
        user_id=current_user.id,
        skin_conditions=data.skin_conditions,
        drug_allergies=data.drug_allergies,
        current_treatments=data.current_treatments,
        skin_type=data.skin_type,
        fitzpatrick_phototype=data.fitzpatrick_phototype,
        chronic_diseases=data.chronic_diseases,
        family_history=data.family_history,
        smoking_alcohol=data.smoking_alcohol,
        occupational_exposure=data.occupational_exposure,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/dermatology-profile/upsert", response_model=schemas.DermatologyProfileResponse)
def upsert_my_dermatology_profile(data: schemas.DermatologyProfileCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Pas un compte patient")
    profile = db.query(models.DermatologyProfile).filter(models.DermatologyProfile.user_id == current_user.id).first()
    if not profile:
        profile = models.DermatologyProfile(user_id=current_user.id)
        db.add(profile)
    for field in ["skin_conditions", "drug_allergies", "current_treatments", "skin_type", "fitzpatrick_phototype", "chronic_diseases", "family_history", "smoking_alcohol", "occupational_exposure"]:
        value = getattr(data, field, None)
        if value is not None:
            setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{patient_id}/dermatology-profile", response_model=schemas.DermatologyProfileResponse)
def get_patient_dermatology_profile_by_doctor(patient_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Seuls les médecins et administrateurs peuvent consulter les profils dermatologiques")
    profile = db.query(models.DermatologyProfile).filter(models.DermatologyProfile.user_id == patient_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil dermatologique non trouvé pour ce patient")
    return profile


@router.get("/{patient_id}/info")
def get_patient_full_info_by_doctor(patient_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins et administrateurs")
    user = db.query(models.User).filter(models.User.id == patient_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Patient non trouvé")
    patient = db.query(models.Patient).filter(models.Patient.user_id == patient_id).first()
    profile = db.query(models.DermatologyProfile).filter(models.DermatologyProfile.user_id == patient_id).first()
    result = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "city": user.city,
        "address": user.address,
        "date_of_birth": patient.date_of_birth if patient else None,
        "blood_group": patient.blood_group if patient else None,
    }
    if profile:
        result.update({
            "skin_conditions": profile.skin_conditions,
            "drug_allergies": profile.drug_allergies,
            "current_treatments": profile.current_treatments,
            "skin_type": profile.skin_type,
            "fitzpatrick_phototype": profile.fitzpatrick_phototype,
            "chronic_diseases": profile.chronic_diseases,
            "family_history": profile.family_history,
            "smoking_alcohol": profile.smoking_alcohol,
            "occupational_exposure": profile.occupational_exposure,
        })
    return result
