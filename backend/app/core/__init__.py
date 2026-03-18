from .config import get_settings, settings, validate_required_settings
from .logging import configure_logging

# database is imported lazily to avoid crashing at startup if DATABASE_URL
# is not yet available (e.g. during testing or cold-start before env vars load).
# Routes import get_db directly from .database when needed.