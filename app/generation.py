from logging import getLogger
from typing import Optional
from fastapi.templating import Jinja2Templates

from fastapi import APIRouter, Request
from pydantic import BaseModel
import random, os, json

from .schema import Challenge, Generation
from .settings import SessionLocal
router = APIRouter()
log = getLogger(__name__)
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def root(request: Request):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "static/manifest.json")) as f:
        assets = json.load(f)
    js_path = assets["assets/js/index.js"]["file"]

    return templates.TemplateResponse("index.html", {"request": request, "js_path": js_path})


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    generation: str = ""
    id: int = -1 
    error: Optional[str] = None 


class ChallengeResponse(BaseModel):
    id: int
    name: str
    description: str
    error: Optional[str] = None


@router.post("/generate/{challenge_id}")
async def generate(challenge_id: int, request: GenerateRequest) -> GenerateResponse:
    print(f"Generating with prompt: {request.prompt}")
    with SessionLocal() as session:
        # Check this isn't a duplicate
        generation = session.query(Generation).filter(Generation.challenge_id == challenge_id).filter(Generation.prompt == request.prompt).first()
        if generation:
            print("Duplicate generation found")
            return GenerateResponse(error="Duplicate prompt found, try something else.")
        challenge = session.query(Challenge).filter(Challenge.id == challenge_id).first()
        generation = challenge.generate(request.prompt)
        session.add(generation)
        session.commit()
        print(generation.generation)
        return GenerateResponse(generation=generation.generation, id=generation.id)
    
@router.get("/challenge")
async def get_challenge():
    with SessionLocal() as session:
        enabled_challenge_count = session.query(Challenge).filter(Challenge.enabled).count()
        if enabled_challenge_count == 0:
            return ChallengeResponse(
                id=-1,
                name="No challenges available",
                description="Check back later!",
                error="No challenges available",
            )
        rand = random.randrange(0, enabled_challenge_count)
        challenge = session.query(Challenge).filter(Challenge.enabled)[rand]

        return ChallengeResponse(
            id=challenge.id,
            name=challenge.name,
            description=challenge.description,
        )
    
class SubmitRequest(BaseModel):
    generation_id: int
    reason: str

class SubmitResponse(BaseModel):
    message: str
    accepted: bool = True
    
@router.post("/submit/")
async def submit(request: SubmitRequest) -> SubmitResponse:
    with SessionLocal() as session:
        generation = session.query(Generation).filter(Generation.id == request.generation_id).first()
        if generation.submitted:
            return SubmitResponse(message="Already submitted!", accepted=False)
        generation.submitted = True
        generation.reason = request.reason
        session.commit()
    return SubmitResponse(message="Thanks for submitting!")

@router.post("/report/")
async def submit(request: SubmitRequest) -> SubmitResponse:
    with SessionLocal() as session:
        generation = session.query(Generation).filter(Generation.id == request.generation_id).first()
        generation.reported = True
        generation.reason = request.reason
        session.commit()
    return SubmitResponse(message="Thanks for reporting!")