from logging import getLogger
from typing import Optional
import random, json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from fastapi_limiter.depends import RateLimiter
import aiohttp

from .schema import Challenge, Generation
from .settings import SessionLocal, public_settings
router = APIRouter()
log = getLogger("generator")


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


async def global_identifier(request):
    return "global"


async def challenge_generate(challenge, prompt: str) -> Generation:
    full_prompt = challenge.model.full_prompt(challenge.preprompt, prompt)
    parameters = json.loads(challenge.model.parameters)
    log.info(f"Generating with prompt: {full_prompt}")
    async with aiohttp.ClientSession() as session:
        async with session.post(url=challenge.model.url,
                        headers={'Authorization': f'Bearer {challenge.model.key}'},
                        json={'inputs': full_prompt, "parameters" : parameters, "stream:": False}) as raw_response:
            json_response = await raw_response.json()
            if 'error' in json_response:
                log.error(f"Error generating: {json_response['error']}")
                raise HTTPException(
                    HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(1000)}
                )
    generated_text = json_response[0]['generated_text']
    return Generation(prompt=prompt, generation=generated_text, challenge=challenge)


@router.post("/generate/{challenge_id}", dependencies=[Depends(RateLimiter(times=public_settings.GEN_REQUESTS_PER_MINUTE, minutes=1, identifier=global_identifier))])
async def generate(challenge_id: int, request: GenerateRequest) -> GenerateResponse:
    log.info(f"Generating with prompt.")
    with SessionLocal() as session:
        # Check this isn't a duplicate
        generation = session.query(Generation).filter(Generation.challenge_id == challenge_id).filter(Generation.prompt == request.prompt).first()
        if generation:
            log.info("Duplicate generation found")
            return GenerateResponse(error="Duplicate prompt found, try something else.")
        challenge = session.query(Challenge).filter(Challenge.id == challenge_id).first()
        generation = await challenge_generate(challenge, request.prompt)
        session.add(generation)
        session.commit()
        return GenerateResponse(generation=generation.generation, id=generation.id)

    
@router.get("/challenge", dependencies=[Depends(RateLimiter(times=public_settings.CHALLENGE_REQUESTS_PER_MINUTE, minutes=1))])
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