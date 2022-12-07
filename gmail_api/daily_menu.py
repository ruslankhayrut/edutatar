import os.path
from xml.etree import ElementTree

from edutatar.settings import EDU_LOGIN, EDU_PASSWORD
from gmail_api import gmail_attachments
from vkrepost.eduauth import EdutatarSession


class MenuUploader:
    def __init__(self, edu_session: EdutatarSession, gmail_session):
        self.edu_session = edu_session
        self.gmail_session = gmail_session
        self.data = self.get_data_from_gmail(["Label_7", "UNREAD"])

    def get_data_from_gmail(self, labels: list) -> dict:
        return gmail_attachments.get_attachments(self.gmail_session, {"labels": labels})

    def post_page(self, page_id: int, data):
        self.edu_session.get("https://edu.tatar.ru")
        url = f"https://edu.tatar.ru/admin/page/simple_page/edit/{page_id}"
        h = {"Referer": url, "Content-Type": "application/x-www-form-urlencoded"}

        file_links = ""
        for file in data:
            file_links = (
                f'<p><a href="/upload/storage/org1505/files/food/{file[0]}">{file[0]}</a></p>\n'
                + file_links
            )
        text = file_links
        self.edu_session.post(
            url=url,
            headers=h,
            data={
                "simple_page[title]": "Ежедневные Меню",
                "simple_page[description]": "",
                "simple_page[data]": text,
                "simple_page[organization_id]": 1505,
            },
        )

    def get_files_from_edu(self, from_folder: str = "food") -> list:
        url = "https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php"
        params = {
            "command": "GetFiles",
            "type": "Files",
            "currentFolder": f"/{from_folder}/",
        }
        res = self.edu_session.get(url, params=params)
        files = ElementTree.fromstring(res.content).findall("Files")[0].findall("File")
        files_list = []
        for file in files:
            filename = file.get("name")
            files_list.append(
                (
                    filename,
                    "/".join(
                        [
                            "https://edu.tatar.ru/upload/storage/org1505/files",
                            from_folder,
                            filename,
                        ]
                    ),
                )
            )
        return files_list

    def upload_file(self, file_path: str, target_folder: str) -> list:
        data = {}
        with open(file_path, "rb") as img:
            filename = img.name.split("\\")[-1]
            data[filename] = img
            f = self.upload_files(data, target_folder)
        return f

    def upload_files(self, files: dict, target_folder: str = "food") -> list:
        h = {"Referer": "https://edu.tatar.ru/"}
        url = "https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php"
        params = {
            "command": "FileUpload",
            "type": "Files",
            "currentFolder": f"/{target_folder}/",
        }

        return [
            self.edu_session.post(url=url, headers=h, params=params, files=[file])
            for file in files
        ]

    def upload_multiple_files(self, files_list: list):
        for filename in files_list:
            self.upload_file(filename, "food")

    def upload_menus(self):
        list_of_filenames = []
        for i in range(1, 31):
            day = f"{i // 10}{i % 10}"
            filename = f"D:\\Downloads\\2021-09-{day}-sm.xlsx"
            if os.path.exists(filename):
                list_of_filenames.append(filename)

        self.upload_multiple_files(list_of_filenames)

    @staticmethod
    def normalize_filenames(files_dict: dict) -> dict:
        res = {}
        for key in files_dict.keys():
            new_key = key[: key.find("sm") + 2] + key[key.find(".") :]
            res[new_key] = files_dict[key]
        return res

    def make_it(self):
        for mail_id, attach in self.data.items():
            files = self.normalize_filenames(attach).items()
            self.upload_files(files)
            self.post_page(page_id=800107, data=self.get_files_from_edu())
            gmail_attachments.label_modify(
                self.gmail_session, "me", mail_id, labels_to_remove=["UNREAD"]
            )


if __name__ == "__main__":
    PROXY = None
    g_session = gmail_attachments.connect(proxy=PROXY)
    edu_session = EdutatarSession(EDU_LOGIN, EDU_PASSWORD, PROXY)
    uploader = MenuUploader(edu_session, g_session)
    uploader.make_it()
