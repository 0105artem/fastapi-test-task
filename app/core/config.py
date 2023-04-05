from pydantic import BaseSettings


class EnvVar(BaseSettings):
    HOSTNAME: str = 'localhost'
    PORT: str = '8000'

    class Config:
        env_file = ".env"


env = EnvVar()
