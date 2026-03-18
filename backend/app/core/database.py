import socket
import ssl
from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


def _to_asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


raw_database_url = settings.database_url
if not raw_database_url:
    raise RuntimeError("DATABASE_URL is not set in environment variables.")

DATABASE_URL = _to_asyncpg_url(raw_database_url)
parsed_url = urlparse(DATABASE_URL)
query_params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
connect_args: dict[str, object] = {}

# asyncpg does not accept "sslmode"; translate to asyncpg's "ssl" option.
sslmode = query_params.pop("sslmode", "").lower()
if sslmode:
    if sslmode == "require":
        # libpq `sslmode=require` means "encrypt, but don't verify cert chain/host".
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx
    elif sslmode in {"verify-ca", "verify-full"}:
        connect_args["ssl"] = ssl.create_default_context()
    elif sslmode in {"disable", "allow", "prefer"}:
        connect_args["ssl"] = False

# Support accidental ssl=<value> in URL as well.
ssl_value = query_params.pop("ssl", "").lower()
if ssl_value and "ssl" not in connect_args:
    if ssl_value in {"1", "true", "yes", "on", "require"}:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx
    else:
        connect_args["ssl"] = False

# Supabase Session Pooler (PgBouncer transaction mode) is not compatible with
# asyncpg prepared statement caching.
connect_args.setdefault("statement_cache_size", 0)

DATABASE_URL = urlunparse(parsed_url._replace(query=urlencode(query_params)))

engine = create_async_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def init_models() -> None:
    from ..models import anomaly, incident, log_batch  # noqa: F401

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except socket.gaierror as exc:
        host = urlparse(DATABASE_URL).hostname or "<unknown-host>"
        raise RuntimeError(
            "Failed to resolve database host "
            f"'{host}'. If you are using Supabase direct host (db.<project-ref>.supabase.co), "
            "switch to the Supabase Session Pooler connection string (IPv4-compatible), "
            "for example: postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require"
        ) from exc
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Database initialization failed: {exc}") from exc
