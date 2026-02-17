"""Patient profile and health summary endpoints."""

from fastapi import APIRouter, Depends

from patient_portal.auth import get_current_user
from patient_portal.models import User

router = APIRouter()


@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get the current patient's profile."""
    return {
        "id": current_user.patient_id,
        "email": current_user.email,
        "mfa_enabled": current_user.mfa_enabled,
    }


@router.get("/me/health-summary")
async def get_health_summary(current_user: User = Depends(get_current_user)):
    """Get the patient's health dashboard data from EHR."""
    # TODO: Fetch from Epic FHIR API
    return {"message": "Not yet implemented"}
