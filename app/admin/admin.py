from typing import List, Optional
from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..public.schema import Generation, Challenge, Model, User
from .settings import SessionLocal
from .auth import create_user, get_current_user
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
import logging

log = logging.getLogger("admin")

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def admin_root(request: Request):
    with SessionLocal() as session:
        model_name_alias = aliased(Model, name="model_name")
        query = select(Challenge.id, Challenge.name, Challenge.description, Challenge.preprompt, Challenge.enabled).add_columns(model_name_alias.name).join(model_name_alias)
        challenges = session.execute(query).all()
        final_challenges = []
        for challenge in challenges:
            num_generations = session.query(func.count(Generation.id)).filter(Generation.challenge_id == challenge[0]).scalar()
            num_submissions = session.query(func.count(Generation.id)).filter(Generation.challenge_id == challenge[0]).filter(Generation.submitted).scalar()
            final_challenges.append({
                "id": challenge[0],
                "name": challenge[1],
                "description": challenge[2],
                "preprompt": challenge[3],
                "enabled": challenge[4],
                "model": challenge[5],
                "num_generations": num_generations,
                "num_submissions": num_submissions,
            })
    return templates.TemplateResponse("admin.html", {"request": request, "challenges": final_challenges})


class ChallengeForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.preprompt: Optional[str] = None
        self.model: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.description = form.get("description")
        self.preprompt = form.get("preprompt")
        self.model = form.get("model")


@router.get("/challenge/new")
async def new_challenge(request: Request):
    return templates.TemplateResponse("new_challenge.html", {"request": request})

@router.post("/challenge/new")
async def new_challenge(request: Request):
    form = ChallengeForm(request)
    await form.load_data()
    try:
        with SessionLocal() as session:
            model = session.query(Model).first()
            challenge = Challenge(name=form.name, description=form.description, preprompt=form.preprompt, model=model)
            session.add(challenge)
            session.commit()
        response = RedirectResponse("/admin/", status.HTTP_302_FOUND)
        return response
    except:
        form.__dict__.update(msg="")
        form.__dict__.get("errors").append("I don't know what happened.")
        return templates.TemplateResponse("new_challenge.html", {"request": request})

def get_generations(session: SessionLocal, request: Request, challenge_id: Optional[int] = None):
    filter = {}
    if request.query_params.get("submitted", None) == "True":
        filter["submitted"] = True
    elif request.query_params.get("submitted", None) == "False":
        filter["submitted"] = False

    if request.query_params.get("reported", None) == "True":
        filter["reported"] = True
    elif request.query_params.get("reported", None) == "False":
        filter["reported"] = False
    query = select(
        Generation.id,
        Generation.prompt,
        Generation.generation,
        Generation.reason,
        Generation.submitted,
        Generation.reported,
        Challenge.name
    ).filter_by(**filter).add_columns(Challenge.name).join(Challenge)
    if challenge_id is not None:
        query = query.where(Generation.challenge_id == challenge_id)
    generations = session.execute(query).all()
    final_generations = []
    for generation in generations:
        final_generations.append({
            "id": generation[0],
            "prompt": generation[1],
            "generation": generation[2],
            "reason": generation[3],
            "submitted": generation[4],
            "reportd": generation[5],
            "challenge": generation[6],
        })
    return final_generations

@router.get("/generations/")
async def view_generations(request: Request):
    with SessionLocal() as session:
        final_generations = get_generations(session, request)

    return templates.TemplateResponse("generations.html", {"request": request, "challenge": None, "generations": final_generations})

@router.get("/generations/{challenge_id}")
async def challenge_generations(challenge_id: int, request: Request):
    with SessionLocal() as session:
        # gets all generations for all challenges
        final_generations = get_generations(session, request, challenge_id=challenge_id)
            
        model_name_alias = aliased(Model, name="model_name")
        query = select(Challenge.id, Challenge.name, Challenge.description, Challenge.preprompt, Challenge.enabled).add_columns(model_name_alias.name).join(model_name_alias).where(Challenge.id == challenge_id)
        challenge = session.execute(query).first()
        num_generations = session.query(func.count()).filter(Generation.challenge_id == challenge_id).scalar()
        num_submissions = session.query(func.count()).filter(Generation.challenge_id == challenge_id).filter(Generation.submitted == True).scalar()
            
        final_challenge = {
            "id": challenge[0],
            "name": challenge[1],
            "description": challenge[2],
            "preprompt": challenge[3],
            "enabled": challenge[4],
            "model": challenge[5],
            "num_generations": num_generations,
            "num_submissions": num_submissions,
        }        
    return templates.TemplateResponse("generations.html", {"request": request, "challenges": [final_challenge], "generations": final_generations})

@router.get("/toggle_challenge/{challenge_id}")
async def toggle_challenge(challenge_id: int):
    with SessionLocal() as session:
        challenge = session.query(Challenge).filter(Challenge.id == challenge_id).first()
        challenge.enabled = not challenge.enabled
        session.commit()
    return RedirectResponse(f"/admin/", status.HTTP_302_FOUND)
