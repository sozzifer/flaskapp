from typing import Any, Dict

from app import app, db
from app.models import User, Post


@app.shell_context_processor
def make_shell_context() -> Dict[str, Any]:
    return {"db": db, "User": User, "Post": Post}
