import logging
from logging import getLogger
import time
from typing import List, Optional
import random

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi_limiter.depends import RateLimiter

from .schema import Challenge, Generation, Model
from .settings import SessionLocal, public_settings
from .remote_llm import generate_text
router = APIRouter()
log = getLogger("generator")
log.setLevel(logging.DEBUG)


class GenerateRequest(BaseModel):
    prompt: str
    model: str


class GenerateResponse(BaseModel):
    generation: str = ""
    id: int = -1 
    error: Optional[str] = None 


class ChallengeResponse(BaseModel):
    id: int
    name: str
    description: str
    error: Optional[str] = None

async def global_identifier(_request):
    return "global"


async def user_identifier(request):
    log.info(f"Getting user identifier")
    if request.cookies.get("uuid") is None:
        log.error(f"UUID not found in cookies!")
        return "global"
    return request.cookies.get("uuid")

@router.post("/generate/{challenge_id}", dependencies=[Depends(RateLimiter(times=public_settings.GEN_REQUESTS_PER_MINUTE, minutes=1, identifier=global_identifier))])
async def generate(challenge_id: int, request: GenerateRequest) -> GenerateResponse:
    log.info(f"Generating with prompt.")
    log.debug(challenge_id, request)
    log.debug(request.model)

    with SessionLocal() as session:
        # Check this isn't a duplicate across challenge, prompt, and model
        generation = (session.query(Generation)
                     .filter(Generation.challenge_id == challenge_id)
                     .filter(Generation.prompt == request.prompt)
                     .filter(Generation.model.has(Model.name == request.model))
                     .first()
                    )

        if generation:
            log.info("Duplicate generation found")
            return GenerateResponse(error="Duplicate prompt found, try something else.")

        # Check that the model is active
        model = session.query(Model).filter(Model.name == request.model).first()
        if model is not None and not model.active:
            log.error(f"Model {model.name} is not active!")
            return GenerateResponse(error="Model not active!")
 
        challenge = session.query(Challenge).filter(Challenge.id == challenge_id).first()
        if challenge is None:
            log.error(f"Challenge {challenge_id} not found!")
            return GenerateResponse(error="Challenge not found!")
        
        generation = await generate_text(challenge.preprompt, request.prompt, request.model)
        log.info(f"Generated: {generation}")
        generation = Generation(
            challenge_id=challenge_id,
            model_id=model.id,
            prompt=request.prompt,
            generation=generation,
        )
        session.add(generation)
        session.commit()
        return GenerateResponse(generation=generation.generation, id=generation.id)

    
@router.get("/challenge", dependencies=[Depends(RateLimiter(times=public_settings.CHALLENGE_REQUESTS_PER_MINUTE, minutes=1, identifier=user_identifier))])
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
    is_report: bool = False

class SubmitResponse(BaseModel):
    message: str
    accepted: bool = True
    
@router.post("/submit/", dependencies=[Depends(RateLimiter(times=public_settings.SUBMISSIONS_PER_MINUTE, minutes=1, identifier=user_identifier))])
async def submit(request: SubmitRequest) -> SubmitResponse:
    log.info(f"Submitting generation {request.generation_id}")
    with SessionLocal() as session:
        generation = session.query(Generation).filter(Generation.id == request.generation_id).first()
        if generation is None:
            return SubmitResponse(message="Generation not found!", accepted=False)

        if generation.submitted:
            return SubmitResponse(message="Already submitted!", accepted=False)

        if request.is_report:
            generation.reported = True
            response_msg = "Thanks for reporting!"
        else:
            generation.submitted = True
            response_msg = "Thanks for submitting!"

        generation.reason = request.reason
        session.commit()
    return SubmitResponse(message=response_msg)

@router.post("/report/", dependencies=[Depends(RateLimiter(times=public_settings.SUBMISSIONS_PER_MINUTE, minutes=1, identifier=user_identifier))])
async def submit(request: SubmitRequest) -> SubmitResponse:
    log.info(f"Reporting generation {request.generation_id}")

    with SessionLocal() as session:
        generation = session.query(Generation).filter(Generation.id == request.generation_id).first()

        if generation is None:
            return SubmitResponse(message="Generation not found!", accepted=False)
        generation.reported = True
        generation.reason = request.reason
        session.commit()

    return SubmitResponse(message="Thanks for reporting!")