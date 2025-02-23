from dependency_injector import containers, providers
from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository
from map.application.map_service import MapService
from map.infra.repository.map_repo import MapRepository
from utils.crypto import Crypto



class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["user", "map"],
    )

    crypto = providers.Factory(Crypto)
    user_repo = providers.Factory(UserRepository)
    
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        crypto=crypto,
    )

    # "map"
    map_repo = providers.Factory(MapRepository)
    map_service = providers.Factory(
        MapService,
        map_repo=map_repo,
    )
