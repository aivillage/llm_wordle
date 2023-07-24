from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi import FastAPI
from pydantic import BaseModel

from schema import Base, Generation, Challenge, Model
from logger import initialize_loggers

initialize_loggers("llm_wordle")

engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)
parameters='''{
    "max_new_tokens": 1024,
    "repetition_penalty": 1.2,
    "return_full_text": false,
    "top_p": 0.95,
    "temperature": 0.9,
    "stop": ["<|endoftext|>"]
}'''

with Session(engine) as session:
    model = Model(
        name="pythia-12b",
        url="https://api-inference.huggingface.co/models/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",
        key="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",
        parameters=parameters,
        prompt_format="{preprompt}<|prompter|>{prompt}<|endoftext|><|assistant|>",
    )
    challenge = Challenge(name="Test", description="Test", preprompt="This is a test", model=model)
    generation = challenge.generate("This is a test prompt")
    session.add(generation)
    session.commit()
    print(session.query(Generation).all())

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generation/{challenge_id}")
async def generate(challenge_id: int, request: GenerateRequest):
    with Session(engine) as session:
        challenge = session.query(Challenge).filter(Challenge.id == challenge_id).first()
        generation = challenge.generate(request.prompt)
        session.add(generation)
        session.commit()
        return generation.generation