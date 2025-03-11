from app.routes.base import BaseRouter
from app.routes.v1.auth import AuthRouter
from app.routes.v1.register import RegisterRouter
from app.routes.v1.users import UserRouter
from app.routes.v1.profile import ProfileRouter

class APIv1(BaseRouter):
    def configure_routes(self):
        self.router.include_router(AuthRouter().get_router())
        self.router.include_router(RegisterRouter().get_router())
        self.router.include_router(UserRouter().get_router())
        self.router.include_router(ProfileRouter().get_router())