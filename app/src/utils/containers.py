from dependency_injector import containers, providers
from user.application.user_service import UserService
from user.infra.repository.user_repo import UserRepository
from utils.crypto import Crypto


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["user"],
    )

    crypto = providers.Factory(Crypto)
    user_repo = providers.Factory(UserRepository)
    
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        crypto=crypto,
    )
