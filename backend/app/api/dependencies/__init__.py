# Open: app/api/dependencies/__init__.py

# Adjust the right-hand filename path string if your function lives 
# inside a specific submodule (like .database, .db, or .session)
from .database import get_db

# Explicitly add it to __all__ to expose it cleanly to package-level requests
__all__ = ["get_db"]
