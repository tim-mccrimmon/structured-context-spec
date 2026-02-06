"""Secure messaging endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from patient_portal.auth import get_current_user
from patient_portal.database import get_db
from patient_portal.models import Message, MessageThread, User

router = APIRouter()


class MessageCreate(BaseModel):
    thread_id: str | None = None
    recipient_id: str
    subject: str = ""
    body: str


@router.get("")
async def list_threads(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List message threads for the current patient."""
    result = await db.execute(
        select(MessageThread).where(MessageThread.patient_id == current_user.patient_id)
    )
    return result.scalars().all()


@router.post("")
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to a provider."""
    if data.thread_id:
        # Reply to existing thread
        result = await db.execute(
            select(MessageThread).where(
                MessageThread.id == data.thread_id,
                MessageThread.patient_id == current_user.patient_id,
            )
        )
        thread = result.scalar_one_or_none()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
    else:
        # New thread
        thread = MessageThread(
            subject=data.subject,
            patient_id=current_user.patient_id,
            provider_id=data.recipient_id,
        )
        db.add(thread)
        await db.flush()

    message = Message(
        thread_id=thread.id,
        sender_id=current_user.id,
        body=data.body,
    )
    db.add(message)
    await db.commit()
    return {"thread_id": thread.id, "message_id": message.id}


@router.get("/{thread_id}")
async def get_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a message thread with all messages."""
    result = await db.execute(
        select(MessageThread).where(
            MessageThread.id == thread_id,
            MessageThread.patient_id == current_user.patient_id,
        )
    )
    thread = result.scalar_one_or_none()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread
