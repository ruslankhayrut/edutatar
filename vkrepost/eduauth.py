import requests


def edu_auth(login, password, proxy=None):
    s = requests.Session()
    if proxy:
        s.proxies.update(proxy)
    s.headers.update(
        {
            "Host": "edu.tatar.ru",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 "
            "Mobile Safari/537.36",
        }
    )
    h = {
        "Referer": "https://edu.tatar.ru/start/logon",
    }

    r = s.post(
        "https://edu.tatar.ru/logon",
        headers=h,
        data={"main_login2": login, "main_password2": password},
    )

    if "Личный кабинет" in r.text:
        print("Login successful")
    else:
        print(
            "Не удалось войти в аккаунт. "
            "Убедитесь, что вы верно ввели логин/пароль и двухфакторная аутентификация отключена."
        )
        raise PermissionError

    return s
