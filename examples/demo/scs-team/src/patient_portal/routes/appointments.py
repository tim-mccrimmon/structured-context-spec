"""Appointment scheduling endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from patient_portal.auth import get_current_user
from patient_portal.database import get_db
from patient_portal.models import Appointment, User


router = APIRouter()


class AppointmentCreate(BaseModel):
    provider_id: str
    datetime: str
    type: str  # in-person, telehealth
    reason: str = ""


@router.get("")
async def list_appointments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the current patient's appointments."""
    result = await db.execute(
        select(Appointment).where(Appointment.patient_id == current_user.patient_id)
    )
    return result.scalars().all()


@router.post("")
async def book_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Book a new appointment."""
    appointment = Appointment(
        patient_id=current_user.patient_id,
        provider_id=data.provider_id,
        datetime=data.datetime,
        type=data.type,
        reason=data.reason,
    )
    db.add(appointment)
    await db.commit()
    return appointment


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an appointment."""
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.patient_id == current_user.patient_id,
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = "cancelled"
    await db.commit()
    return {"status": "cancelled"}
