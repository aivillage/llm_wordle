from typing import Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.engine.url import URL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from logging import getLogger
from requests import post
log = getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Generation(Base):
    __tablename__ = "generation"
    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenge.id"))
    prompt: Mapped[str] = mapped_column(String(4000))
    generation: Mapped[str] = mapped_column(String(4000))
    challenge: Mapped["Challenge"] = relationship()
    submitted: Mapped[bool] = mapped_column(default=False)
    reason: Mapped[Optional[str]] = mapped_column(String(4000))
    reported: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Generation(id={self.id!r}, challenge={self.challenge!r}, prompt={self.prompt!r})"


class Challenge(Base):
    __tablename__ = "challenge"
    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("model.id"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(4000))
    preprompt: Mapped[str] = mapped_column(String(4000))
    enabled: Mapped[bool] = mapped_column(default=True)
    model: Mapped["Model"] = relationship()

    def __repr__(self) -> str:
        return f"Challenge(id={self.id!r}, name={self.name!r})"
    
    def generate(self, prompt: str) -> Generation:
        full_prompt = self.model.full_prompt(self.preprompt, prompt)
        parameters = json.loads(self.model.parameters)
        log.info(f"Generating with prompt: {full_prompt}")
        raw_response = post(url=self.model.url,
                        headers={'Authorization': f'Bearer {self.model.key}'},
                        json={'inputs': full_prompt, "parameters" : parameters, "stream:": False})
        json_response = raw_response.json()
        print(json_response)
        generated_text = json_response[0]['generated_text']
        return Generation(prompt=prompt, generation=generated_text, challenge=self)


class Model(Base):
    __tablename__ = "model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(200))
    key: Mapped[str] = mapped_column(String(200))
    parameters: Mapped[str] = mapped_column(String(200))
    prompt_format: Mapped[str] = mapped_column(String(200))

    def __repr__(self) -> str:
        return f"Model(id={self.id!r}, name={self.name!r}), url={self.url!r}"
    
    def full_prompt(self, preprompt: str, prompt: str) -> str:
        return self.prompt_format.replace("{preprompt}", preprompt).replace("{prompt}", prompt)


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    disabled: Mapped[bool]


def empty_str_cast(value, default=None):
    if value == "":
        return default
    return value


def connect_db(config: dict):
    DATABASE_URL = URL.create(
        empty_str_cast(config["DATABASE_PROTOCOL"]) or "mysql",
        username=empty_str_cast(config["DATABASE_USER"]) or "llm_wordle",
        password=empty_str_cast(config["DATABASE_PASSWORD"]) or "llm_wordle",
        host=empty_str_cast(config["DATABASE_HOST"]),
        port=empty_str_cast(config["DATABASE_PORT"]),
        database=empty_str_cast(config["DATABASE_NAME"]) or "llm_wordle",
    )
    print(DATABASE_URL)
    engine = create_engine(DATABASE_URL)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    return SessionLocal