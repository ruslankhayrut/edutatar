import logging

from requests import Session

logger = logging.getLogger("django")


class EdutatarSession(Session):
    def __init__(self, proxy: str = None, *args, **kwargs):
        super(EdutatarSession, self).__init__()
        if proxy:
            self.proxies.update(proxy)
        self.headers.update(
            {
                "Host": "edu.tatar.ru",
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 "
                "Mobile Safari/537.36",
            }
        )

    def login(self, login: str, password: str):
        headers = {
            "Referer": "https://edu.tatar.ru/start/logon",
        }

        r = self.post(
            "https://edu.tatar.ru/logon",
            headers=headers,
            data={"main_login2": login, "main_password2": password},
        )

        if "Личный кабинет" not in r.text:
            raise PermissionError(
                "Не удалось войти в аккаунт. "
                "Убедитесь, что вы верно ввели логин/пароль и двухфакторная аутентификация отключена."
            )
        logger.info("Edutatar login: ok")
