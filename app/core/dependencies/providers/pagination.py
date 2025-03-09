from dishka import Provider, provide, Scope

from app.schemas.v1.pagination import PaginationParams

class PaginationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def pagination_params(self) -> PaginationParams:
        return PaginationParams()