from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
import database
import models
import schemas
import auth

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=schemas.AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appt_data: schemas.AppointmentCreate, db: Session = Depends(database.get_db)):
    patient = db.query(models.User).filter(models.User.id == appt_data.patient_id, models.User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")

    doctor = db.query(models.User).filter(models.User.id == appt_data.doctor_id, models.User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Médecin non trouvé")

    appointment = models.Appointment(
        patient_id=appt_data.patient_id,
        doctor_id=appt_data.doctor_id,
        appointment_date=appt_data.appointment_date,
        appointment_time=appt_data.appointment_time,
        reason=appt_data.reason,
        priority=appt_data.priority,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/", response_model=list[schemas.AppointmentResponse])
def list_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Appointment).offset(skip).limit(limit).all()


@router.get("/patient/{patient_id}", response_model=list[schemas.AppointmentResponse])
def get_patient_appointments(patient_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()


@router.get("/doctor/{doctor_id}", response_model=list[schemas.AppointmentResponse])
def get_doctor_appointments(doctor_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).all()


@router.get("/today", response_model=list[schemas.AppointmentResponse])
def get_today_appointments(db: Session = Depends(database.get_db)):
    today = date.today()
    return db.query(models.Appointment).filter(models.Appointment.appointment_date == today).all()


@router.put("/{appointment_id}/status", response_model=schemas.AppointmentResponse)
def update_appointment_status(appointment_id: int, status_val: str, db: Session = Depends(database.get_db)):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    appointment.status = status_val
    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(database.get_db)):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    db.delete(appointment)
    db.commit()
