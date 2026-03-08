from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/dailystarter"
    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    max_pokemon_id: int = 1025
    app_timezone: str = "UTC"
    cookie_secure: bool = False

    model_config = {"env_prefix": "APP_"}


settings = Settings()
