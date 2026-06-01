from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


# --- Schémas d'Authentification ---

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    first_name: str
    last_name: str
    email: str


# --- Schémas Utilisateur ---

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    subscription: str = "basic"


class UserResponse(UserBase):
    id: int
    role: str
    is_active: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Schémas Patient ---

class PatientRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    subscription: str = "premium"


class PatientResponse(UserResponse):
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None


# --- Schémas Profil Dermatologique ---

class DermatologyProfileCreate(BaseModel):
    skin_conditions: Optional[str] = None
    drug_allergies: Optional[str] = None
    current_treatments: Optional[str] = None
    skin_type: Optional[str] = None
    fitzpatrick_phototype: Optional[str] = None
    chronic_diseases: Optional[str] = None
    family_history: Optional[str] = None
    smoking_alcohol: Optional[str] = None
    occupational_exposure: Optional[str] = None


class DermatologyProfileResponse(DermatologyProfileCreate):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Schémas Médecin ---

class DoctorRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    medical_license: str
    specialization: str
    years_of_experience: Optional[int] = None
    subscription: str = "professional"


class DoctorResponse(UserResponse):
    medical_license: str
    specialization: str
    years_of_experience: Optional[int] = None
    rating: Optional[float] = None


# --- Schémas Réception ---

class ReceptionistRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    employee_id: str
    department: Optional[str] = None
    shift: Optional[str] = "morning"
    subscription: str = "professional"


class ReceptionistResponse(UserResponse):
    employee_id: str
    department: Optional[str] = None
    shift: Optional[str] = None


# --- Schémas Admin ---

class AdminRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    admin_code: str
    admin_level: str
    subscription: str = "professional"


class AdminResponse(UserResponse):
    admin_code: str
    admin_level: str


# --- Schémas de Rendez-vous ---

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: str
    reason: Optional[str] = None
    priority: str = "normal"


class AppointmentResponse(AppointmentCreate):
    id: int
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Schémas de Chat ---

class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    response: str
    timestamp: Optional[datetime] = None


# --- Message Générique ---

class Message(BaseModel):
    detail: str
