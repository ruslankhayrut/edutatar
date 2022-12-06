import os.path
from xml.etree import ElementTree

from gmail_api import gmail_attachments
from vkrepost.eduauth import EdutatarSession
from edutatar.settings import EDU_LOGIN
from edutatar.settings import EDU_PASSWORD


class MenuUploader:
    def __init__(self, edu_session: EdutatarSession, gmail_session):
        self.ed_session = edu_session
        self.gmail_session = gmail_session
        self.data = self.get_data_from_gmail(["Label_7", "UNREAD"])

    def get_data_from_gmail(self, labels=list()):
        return gmail_attachments.get_attachments(
            self.gmail_session, {"labels": labels}
        )

    def post_page(self, page_id, data):
        self.ed_session.get("https://edu.tatar.ru")
        url = f"https://edu.tatar.ru/admin/page/simple_page/edit/{page_id}"
        h = {"Referer": url, "Content-Type": "application/x-www-form-urlencoded"}

        file_links = ""
        for file in data:
            file_links = (
                    f'<p><a href="/upload/storage/org1505/files/food/{file[0]}">{file[0]}</a></p>\n'
                    + file_links
            )
        text = file_links
        self.ed_session.post(
            url=url,
            headers=h,
            data={
                "simple_page[title]": "Ежедневные Меню",
                "simple_page[description]": "",
                "simple_page[data]": text,
                "simple_page[organization_id]": 1505,
            },
        )

    def get_files_from_edu(self, from_folder="food"):
        url = "https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php"
        params = {
            "command": "GetFiles",
            "type": "Files",
            "currentFolder": f"/{from_folder}/",
        }
        res = self.ed_session.get(url, params=params)
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

    def upload_file(self, file_path, target_folder):
        data = {}
        img = open(file_path, mode="rb")
        filename = img.name.split("\\")[-1]
        data[filename] = img
        f = self.upload_files(data, target_folder)
        img.close()
        return f

    def upload_files(self, files, target_folder="food"):
        h = {
            "Referer": "https://edu.tatar.ru/",
        }
        url = "https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php"
        params = {
            "command": "FileUpload",
            "type": "Files",
            "currentFolder": f"/{target_folder}/",
        }
        f = []
        for file in files:
            f.append(self.ed_session.post(url=url, headers=h, params=params, files=[file]))

        return f

    def upload_multiple_files(self, files_list):
        for filename in files_list:
            print(self.upload_file(filename, "food"))

    def upload_menus(self):
        list_of_filenames = []
        for i in range(1, 31):
            day = str(i // 10) + str(i % 10)
            filename = f"D:\\Downloads\\2021-09-{day}-sm.xlsx"
            if os.path.exists(filename):
                list_of_filenames.append(filename)

        self.upload_multiple_files(list_of_filenames)

    @staticmethod
    def normalize_filenames(files_dict):
        res = {}
        for key in files_dict.keys():
            new_key = key[: key.find("sm") + 2] + key[key.find("."):]
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
