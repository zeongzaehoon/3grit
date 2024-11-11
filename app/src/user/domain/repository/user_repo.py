from abc import ABCMeta

class IUserRepository(metaclass=ABCMeta):
    """_summary_
        이름에 I를 붙인 이유는 명시적으로 인터페이스임을 나타내기 위함.
        이 인터페으스 실제 구현체는 인프라 계층에 존재함. 도메인 계층에 존재하는 이 모듈은 어느 계층에서나 사용할 수 있으며, 인프라 계층보다 고수준의 계층에서 사용할 때에는 그 의존성이 역전됨.
    """
    pass