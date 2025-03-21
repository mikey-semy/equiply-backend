from app.routes.base import BaseRouter
from app.routes.v1.auth import AuthRouter
from app.routes.v1.oauth import OAuthRouter
from app.routes.v1.register import RegisterRouter
from app.routes.v1.users import UserRouter
from app.routes.v1.profile import ProfileRouter
from app.routes.v1.workspaces import WorkspaceRouter
from app.routes.v1.modules.tables import TableRouter

class APIv1(BaseRouter):
    def configure_routes(self):
        self.router.include_router(AuthRouter().get_router())
        self.router.include_router(OAuthRouter().get_router())
        self.router.include_router(RegisterRouter().get_router())
        self.router.include_router(UserRouter().get_router())
        self.router.include_router(ProfileRouter().get_router())
        self.router.include_router(WorkspaceRouter().get_router())
        self.router.include_router(TableRouter().get_router())
