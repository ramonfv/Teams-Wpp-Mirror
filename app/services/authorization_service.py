from app.repositories.user_repository import UserRepository


class AuthorizationService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def assert_can_send_to_whatsapp(self, teams_user_email: str) -> dict:
        user = self.user_repository.get_active_user_by_email(
            teams_user_email=teams_user_email,
        )

        if user is None:
            raise PermissionError(
                f"Usuário '{teams_user_email}' não está autorizado."
            )

        if not user["can_send_to_whatsapp"]:
            raise PermissionError(
                f"Usuário '{teams_user_email}' não tem permissão de envio."
            )

        return user