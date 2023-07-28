from dataclasses import dataclass
import os
from typing import Optional
from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.engine.url import URL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



class Base(DeclarativeBase):
    pass


class Generation(Base):
    __tablename__ = "generation"
    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenge.id"))
    prompt: Mapped[str] = mapped_column(Text)
    generation: Mapped[str] = mapped_column(Text)
    challenge: Mapped["Challenge"] = relationship()
    submitted: Mapped[bool] = mapped_column(default=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    reported: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Generation(id={self.id!r}, challenge={self.challenge!r}, prompt={self.prompt!r})"


class Challenge(Base):
    __tablename__ = "challenge"
    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("model.id"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    preprompt: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(default=True)
    model: Mapped["Model"] = relationship()

    def __repr__(self) -> str:
        return f"Challenge(id={self.id!r}, name={self.name!r})"


class Model(Base):
    __tablename__ = "model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(200))
    key: Mapped[str] = mapped_column(String(200))
    parameters: Mapped[str] = mapped_column(Text)
    prompt_format: Mapped[dict] = mapped_column(JSON)

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


@dataclass
class DatabaseSettings():
    DATABASE_HOST: str 
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PROTOCOL: str

    def __init__(self):
        self.DATABASE_HOST = os.getenv("DATABASE_HOST")
        self.DATABASE_PORT = os.getenv("DATABASE_PORT")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME")
        self.DATABASE_USER = os.getenv("DATABASE_USER")
        self.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
        self.DATABASE_PROTOCOL = os.getenv("DATABASE_PROTOCOL")


def connect_db(config: DatabaseSettings):
    DATABASE_URL = URL.create(
        empty_str_cast(config.DATABASE_PROTOCOL),
        username=empty_str_cast(config.DATABASE_USER),
        password=empty_str_cast(config.DATABASE_PASSWORD),
        host=empty_str_cast(config.DATABASE_HOST),
        port=empty_str_cast(config.DATABASE_PORT),
        database=empty_str_cast(config.DATABASE_NAME),
    )
    engine = create_engine(DATABASE_URL, pool_recycle=3600)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    return SessionLocal