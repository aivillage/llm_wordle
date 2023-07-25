from logging import getLogger

from fastapi import APIRouter
from pydantic import BaseModel
import random

from .schema import Challenge, Generation, SessionLocal
router = APIRouter()
log = getLogger(__name__)


class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    generation: str
    id: int

class ChallengeResponse(BaseModel):
    id: int
    name: str
    description: str

@router.post("/generate/{challenge_id}")
async def generate(challenge_id: int, request: GenerateRequest) -> GenerateResponse:
    print(f"Generating with prompt: {request.prompt}")
    with SessionLocal() as session:
        challenge = session.query(Challenge).filter(Challenge.id == challenge_id).first()
        generation = challenge.generate(request.prompt)
        session.add(generation)
        session.commit()
        print(generation.generation)
        return GenerateResponse(generation=generation.generation, id=generation.id)
    
@router.get("/challenge")
async def get_challenge():
    with SessionLocal() as session:
        rand = random.randrange(0, session.query(Challenge).count())
        challenge = session.query(Challenge)[rand]

        return ChallengeResponse(
            id=challenge.id,
            name=challenge.name,
            description=challenge.description,
        )
    
class SubmitRequest(BaseModel):
    generation_id: str

class SubmitResponse(BaseModel):
    message: str
    
@router.post("/submit/")
async def submit(request: SubmitRequest) -> SubmitResponse:
    with SessionLocal() as session:
        generation = session.query(Generation).filter(Generation.id == request.generation_id).first()
        generation.submitted = True
    return SubmitResponse(message="Thanks for submitting!")
