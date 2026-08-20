from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.services.scheduling_service import SchedulingService, appointment_to_dict

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("")
def list_appointments(status: str = "SCHEDULED", db: Session = Depends(get_db)):
    service = SchedulingService(db)
    if status.upper() == "SCHEDULED":
        return service.list_scheduled()
    rows = service.appointments.list_by_status(status.upper())
    return [appointment_to_dict(row) for row in rows]


@router.post("/{appointment_id}/complete")
def complete_appointment(appointment_id: str, db: Session = Depends(get_db)):
    service = SchedulingService(db)
    appointment = service.complete(appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment_to_dict(appointment)
