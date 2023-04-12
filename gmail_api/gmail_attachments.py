import base64
from pathlib import Path
from pprint import pprint

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


gmail_dir = Path(settings.BASE_DIR) / "gmail_api"

TOKEN_FILE = gmail_dir / "token.json"
SECRETS_FILE = gmail_dir / "secret.json"


def update_creds(creds):
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())


def connect():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if TOKEN_FILE.is_file():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(str(SECRETS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        update_creds(creds)
    elif not creds.valid:
        creds.refresh(Request())
        update_creds(creds)

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        print("Gmail connected")
        return service
    except HttpError as error:
        # Handle errors from gmail API.
        print(f"An error occurred: {error}")


def GetAttachments(service, user_id, msg_id):
    """Get and store attachment from Message with given id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: ID of Message containing attachment.
    prefix: prefix which is added to the attachment filename on saving
    """
    files = None
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        files = {}
        for part in message["payload"]["parts"]:
            if part["filename"]:
                if "data" in part["body"]:
                    data = part["body"]["data"]
                else:
                    att_id = part["body"]["attachmentId"]
                    att = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId=user_id, messageId=msg_id, id=att_id)
                        .execute()
                    )
                    data = att["data"]
                file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
                files[part["filename"]] = file_data
                # при необходимости сохранить локально раскомментировать следующие строчки
                # path = prefix + part['filename']
                # with open(path, 'wb') as f:
                #     f.write(file_data)
                #     files_paths.append(path)
    except HttpError as error:
        print("An error occurred: %s" % error)
    return files


def get_labelId_by_name(service, user_id, label_name):
    try:
        results = service.users().labels().list(userId=user_id).execute()
        labels = results.get("labels", [])
        if not labels:
            print("No labels found.")
            return
        for label in labels:
            if label["name"] == label_name:
                return label["id"]
    except HttpError as error:
        # Handle errors from gmail API.
        print(f"An error occurred: {error}")


def label_modify(service, user_id, msg_id, labels_to_remove=[], labels_to_add=[]):
    try:
        requset_body = {
            "addLabelIds": labels_to_add,
            "removeLabelIds": labels_to_remove,
        }
        result = (
            service.users()
            .messages()
            .modify(userId=user_id, id=msg_id, body=requset_body)
            .execute()
        )
        return result
    except HttpError as error:
        # Handle errors from gmail API.
        print(f"An error occurred: {error}")


def get_attachments(service: build, params):
    """Returns all attachments from messages filtered by params
    (label ids for now)
    """
    labels_list = params.get("labels", [])
    try:
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=100, labelIds=labels_list)
            .execute()
        )
        pprint(results.get("messages", []))
        files_by_message = {}
        for message_id in results.get("messages", []):
            files_by_message[message_id["id"]] = GetAttachments(
                service, "me", message_id["id"]
            )
        return files_by_message
    except HttpError as error:
        # Handle errors from gmail API.
        print(f"An error occurred: {error}")
