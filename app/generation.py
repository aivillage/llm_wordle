from sqlalchemy.orm import Session
from fastapi import APIRouter
from pydantic import BaseModel

from app.schema import Challenge
router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str



@router.post("/generate/{challenge_id}")
async def generate(challenge_id: int, request: GenerateRequest):
    with Session() as session:
        challenge = session.query(Challenge).filter(Challenge.id == challenge_id).first()
        generation = challenge.generate(request.prompt)
        session.add(generation)
        session.commit()
        return generation.generation
    
