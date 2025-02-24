from fastapi import APIRouter
from typing import List, Optional

class BaseRouter:
    def __init__(self, prefix: str = "", tags: Optional[List[str]] = None):
        self.router = APIRouter(prefix=f"/{prefix}" if prefix else "", tags=tags or [])
        self.configure()

    def configure(self):
        """Переопределяется в дочерних классах для настройки роутов"""
        pass

    def get_router(self) -> APIRouter:
        return self.router