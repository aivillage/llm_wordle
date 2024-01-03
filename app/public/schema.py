from dataclasses import dataclass
import os
from typing import Optional
from sqlalchemy import MetaData
from sqlalchemy import JSON, ForeignKey, String, Text, text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.engine.url import URL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logging import getLogger
log = getLogger("public")

metadata_obj = MetaData(schema="llm_wordle")

class Base(DeclarativeBase):
    metadata = metadata_obj


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
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    preprompt: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"Challenge(id={self.id!r}, name={self.name!r})"


class Model(Base):
    __tablename__ = "model"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"Model(id={self.id!r}, name={self.name!r}), url={self.url!r}, description={self.description!r}, active={self.active!r})"


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


def connect_db(config: DatabaseSettings, admin: bool = False):
    DATABASE_URL = URL.create(
        empty_str_cast(config.DATABASE_PROTOCOL),
        username=empty_str_cast(config.DATABASE_USER),
        password=empty_str_cast(config.DATABASE_PASSWORD),
        host=empty_str_cast(config.DATABASE_HOST),
        port=empty_str_cast(config.DATABASE_PORT),
        database=empty_str_cast(config.DATABASE_NAME),
    )
    engine = create_engine(DATABASE_URL, pool_recycle=3600)
    conn = engine.connect()
    conn.execute(text("CREATE DATABASE IF NOT EXISTS llm_wordle;"))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if admin:
        Base.metadata.create_all(engine)
    log.info("Database connected")
    return SessionLocal