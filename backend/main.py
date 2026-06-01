from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import database
import models
import schemas
import auth
from routers import patients, doctors, appointments, chatbot

app = FastAPI(title="DermaFlow AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(chatbot.router)


@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=database.engine)


@app.get("/")
def root():
    return {"message": "DermaFlow AI Backend est en cours d'exécution", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "sain"}


# --- Points de terminaison d'authentification unifiés ---

@app.post("/auth/forgot-password")
def forgot_password(data: dict, db: Session = Depends(database.get_db)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email requis")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"message": "Si cet email existe dans notre système, un lien de récupération a été envoyé."}

    from datetime import timedelta
    reset_token = auth.create_access_token(
        data={"sub": str(user.id), "purpose": "password_reset"}, 
        expires_delta=timedelta(minutes=15)
    )
    
    return {"message": "Lien de récupération envoyé", "token": reset_token}


@app.post("/auth/reset-password")
def reset_password(data: dict, db: Session = Depends(database.get_db)):
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token et nouveau mot de passe requis")

    payload = auth.decode_access_token(token)
    if payload is None or payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user.password_hash = auth.hash_password(new_password)
    db.commit()

    return {"message": "Mot de passe réinitialisé avec succès"}


@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: dict, db: Session = Depends(database.get_db)):
    role = user_data.get("role")
    if role != "patient":
        raise HTTPException(status_code=403, detail="Seuls les patients peuvent s'inscrire via le site.")

    if role not in ["patient", "doctor", "receptionist", "admin", "infermier"]:
        raise HTTPException(status_code=400, detail="Rôle invalide. Doit être : patient, doctor, receptionist, admin, ou infermier")

    email = user_data.get("email")
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    user = models.User(
        email=email,
        password_hash=auth.hash_password(user_data.get("password")),
        role=role,
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
        phone=user_data.get("phone"),
        gender=user_data.get("gender"),
        city=user_data.get("city"),
        address=user_data.get("address"),
        subscription=user_data.get("subscription", "basic"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if role == "patient":
        from datetime import datetime as dt
        dob = user_data.get("date_of_birth")
        patient = models.Patient(
            user_id=user.id,
            date_of_birth=dt.strptime(dob, "%Y-%m-%d").date() if dob else None,
        )
        db.add(patient)

    elif role == "doctor":
        doctor = models.Doctor(
            user_id=user.id,
            medical_license=user_data.get("medical_license", ""),
            specialization=user_data.get("specialization", "dermatologie_clinique"),
            years_of_experience=user_data.get("years_of_experience"),
        )
        db.add(doctor)

    elif role == "receptionist":
        receptionist = models.Receptionist(
            user_id=user.id,
            employee_id=user_data.get("employee_id", ""),
            department=user_data.get("department"),
            shift=user_data.get("shift", "morning"),
        )
        db.add(receptionist)

    elif role == "admin":
        admin = models.Admin(
            user_id=user.id,
            admin_code=user_data.get("admin_code", ""),
            admin_level=user_data.get("admin_level", "support"),
        )
        db.add(admin)

    elif role == "infermier":
        infermier = models.Nurse(
            user_id=user.id,
            employee_id=user_data.get("employee_id", ""),
            department=user_data.get("department"),
            shift=user_data.get("shift", "morning"),
            specialization=user_data.get("specialization"),
        )
        db.add(infermier)

    db.commit()

    access_token = auth.create_access_token(data={"sub": str(user.id), "role": user.role})
    return {
        "message": "Compte créé avec succès",
        "user_id": user.id,
        "role": user.role,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "gender": user.gender,
        "city": user.city,
        "address": user.address,
        "subscription": user.subscription,
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.post("/auth/login")
def login_user(login_data: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe invalide")

    if not auth.verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe invalide")

    if user.role != login_data.role:
        raise HTTPException(status_code=403, detail=f"Ce compte n'est pas un compte {login_data.role}")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")

    access_token = auth.create_access_token(data={"sub": str(user.id), "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "subscription": user.subscription,
    }


@app.get("/auth/me")
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "gender": current_user.gender,
        "city": current_user.city,
        "address": current_user.address,
        "subscription": current_user.subscription,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }


@app.get("/users/stats")
def get_user_stats(db: Session = Depends(database.get_db)):
    total = db.query(models.User).count()
    patients_count = db.query(models.User).filter(models.User.role == "patient").count()
    doctors_count = db.query(models.User).filter(models.User.role == "doctor").count()
    receptionists_count = db.query(models.User).filter(models.User.role == "receptionist").count()
    admins_count = db.query(models.User).filter(models.User.role == "admin").count()
    infermiers_count = db.query(models.User).filter(models.User.role == "infermier").count()
    return {
        "total_users": total,
        "patients": patients_count,
        "doctors": doctors_count,
        "receptionists": receptionists_count,
        "admins": admins_count,
        "infermiers": infermiers_count,
    }
