from asyncio import BoundedSemaphore
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

from cashews import Cache, cache
from environs import Env
from openrouteservice import Client

__all__ = ["Config", "load_config"]


@dataclass(slots=True)
class Bot:
    token: str
    cache: Cache
    semaphore: BoundedSemaphore
    process_pool: ProcessPoolExecutor
    openrouteservice: Client
    geoapify: str


@dataclass(slots=True)
class PostgresConfig:
    driver: str
    user: str
    password: str
    host: str
    port: int
    database: str


@dataclass(slots=True)
class RedisConfig:
    host: str
    port: int


@dataclass(slots=True)
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    bot: Bot
    postgres: PostgresConfig
    redis: RedisConfig


def load_config():
    env: Env = Env()
    env.read_env()
    redis_host = env("REDIS_HOST")
    redis_port = int(env("REDIS_PORT"))

    cache.setup(f"redis://{redis_host}:{redis_port}/1", client_side=True)

    return Config(
        bot=Bot(
            token=env("BOT_TOKEN"),
            cache=cache,
            semaphore=BoundedSemaphore(20),
            process_pool=ProcessPoolExecutor(5),
            openrouteservice=Client(key=env("ORS_KEY")),
            geoapify=env("GA_KEY"),
        ),
        postgres=PostgresConfig(
            driver=env("POSTGRES_DRIVER"),
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
            host=env("POSTGRES_HOST"),
            port=int(env("POSTGRES_PORT")),
            database=env("POSTGRES_DB"),
        ),
        redis=RedisConfig(host=redis_host, port=redis_port),
    )
