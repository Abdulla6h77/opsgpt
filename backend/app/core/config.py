import secrets
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal
from typing import Annotated

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # General                                                              #
    # ------------------------------------------------------------------ #
    env: Literal["development", "production"] = Field(
        default="development",
        validation_alias=AliasChoices("ENV"),
    )
    database_url: str = Field(
        default="",
        validation_alias=AliasChoices("DATABASE_URL"),
    )
    security_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("SECURITY_API_KEY", "API_KEY"),
    )
    jwt_secret: str = Field(
        default="",
        validation_alias=AliasChoices("JWT_SECRET"),
    )
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        validation_alias=AliasChoices("CORS_ORIGINS"),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL"),
    )

    # ------------------------------------------------------------------ #
    # Legacy / generic LLM fields (kept for backwards compat)             #
    # ------------------------------------------------------------------ #
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY"),
    )
    groq_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GROQ_API_KEY"),
    )
    supabase_service_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SERVICE_KEY"),
    )
    llm_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GROQ_API_KEY", "OPENAI_API_KEY", "LLM_API_KEY"),
    )
    llm_model: str = Field(
        default="gpt-4o-mini",
        validation_alias=AliasChoices("LLM_MODEL"),
    )
    llm_base_url: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_BASE_URL"),
    )

    # ------------------------------------------------------------------ #
    # DigitalOcean Gradient™ AI                                           #
    # ------------------------------------------------------------------ #
    gradient_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GRADIENT_API_KEY"),
        description="API key for DigitalOcean Gradient AI inference endpoint",
    )
    gradient_inference_url: str = Field(
        default="",
        validation_alias=AliasChoices("GRADIENT_INFERENCE_URL"),
        description=(
            "Base URL of your Gradient AI inference endpoint. "
            "Example: https://api.gradient.ai/v1"
        ),
    )
    gradient_model: str = Field(
        default="llama-3-70b-instruct",
        validation_alias=AliasChoices("GRADIENT_MODEL"),
        description="Model ID deployed on Gradient AI (e.g. llama-3-70b-instruct)",
    )

    # ------------------------------------------------------------------ #
    # Validators                                                           #
    # ------------------------------------------------------------------ #
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("[") and stripped.endswith("]"):
                return [
                    item.strip().strip("'\"")
                    for item in stripped[1:-1].split(",")
                    if item.strip()
                ]
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value

    # ------------------------------------------------------------------ #
    # Properties                                                           #
    # ------------------------------------------------------------------ #
    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def has_gradient_ai(self) -> bool:
        """True when Gradient AI credentials are fully configured."""
        return bool(self.gradient_api_key.strip() and self.gradient_inference_url.strip())

    @property
    def has_groq(self) -> bool:
        """True when Groq credentials are configured."""
        return bool(self.groq_api_key.strip())

    @property
    def active_llm_provider(self) -> str:
        """Returns the name of the LLM provider that will be used."""
        if self.has_gradient_ai:
            return "gradient_ai"
        if self.has_groq:
            return "groq"
        return "fallback"

    # ------------------------------------------------------------------ #
    # Runtime secret generation                                            #
    # ------------------------------------------------------------------ #
    def ensure_runtime_secrets(self) -> None:
        """Generate ephemeral secrets only when missing to avoid boot failures."""
        if not self.security_api_key.strip():
            self.security_api_key = secrets.token_urlsafe(48)
        if not self.jwt_secret.strip():
            self.jwt_secret = secrets.token_urlsafe(48)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def validate_required_settings() -> None:
    missing = []
    if not settings.database_url.strip():
        missing.append("DATABASE_URL")

    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variables: {joined}")

    if "*" in settings.cors_origins or not settings.cors_origins:
        raise RuntimeError("CORS_ORIGINS must be explicitly configured without wildcard.")

    disallowed_public = ["NEXT_PUBLIC_GROQ_API_KEY", "NEXT_PUBLIC_SUPABASE_KEY"]
    found = [name for name in disallowed_public if os.getenv(name)]
    if found:
        raise RuntimeError(
            f"Disallowed public secret variables configured: {', '.join(found)}"
        )

    # Log which LLM provider will be active at startup
    import logging
    logging.getLogger(__name__).info(
        "Active LLM provider: %s", settings.active_llm_provider
    )