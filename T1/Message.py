"""TMail Message Library"""
import GmailFetcher
import base64
from bs4 import BeautifulSoup
class Gmail_Message:
    def __init__(self,id :str,srv : GmailFetcher.GmailService):
        self.MessageId = id
        self.srv = srv
        self.full_message_loaded = False
        self.Message = self.srv.service.users().messages().get(userId='me', id=id,format='metadata').execute()
        self.labels = self.Message['labelIds']
        if 'UNREAD' in self.labels:
            self.unread = True
        else:
            self.unread = False
    def getBody(self) -> str:
        """Returns the body of the message
           :rtype: str
           :return: The body of the message
        """
        if not self.full_message_loaded:
            self.Message = self.srv.service.users().messages().get(userId='me', id=self.MessageId).execute()
            self.full_message_loaded = True
        payload = self.Message['payload']
        if 'parts' in payload:
            parts = payload['parts']
            body_data = ""
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    body_data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'multipart/alternative':
                    subparts = part['parts']
                    for sub_sub_part in subparts:
                        if sub_sub_part['mimeType'] == 'text/plain':
                            body_data = base64.urlsafe_b64decode(sub_sub_part['body']['data']).decode('utf-8')
        else:
            body_data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')



        return body_data
    def getHeading(self) -> str:
        """Returns the subject of the message
           :rtype: str
           :return: The subject of the message
        """
        payload = self.Message['payload']
        headers = payload['headers']
        for field in headers:
            if field['name'] == 'Subject':
                return field['value']
    def getFrom(self) -> str:
        """Returns details about the sender of the message
           :rtype: str
           :return: The sender of the message
        """
        payload = self.Message['payload']
        headers = payload['headers']
        for field in headers:
            if field['name'] == 'From':
                return field['value']
    def markasRead(self) -> None:
        """Marks the message as read
           :rtype: None
           :return: None
        """
        self.srv.service.users().messages().modify(userId='me', id=self.MessageId,body={'removeLabelIds': ['UNREAD']}).execute()
    def markasUnRead(self) -> None:
        """Marks the message as unread
           :rtype: None
           :return: None
        """
        self.srv.service.users().messages().modify(userId='me', id=self.MessageId,body={'addLabelIds': ['UNREAD']}).execute()
    def moveToTrash(self) -> None:
        """Moves the message to trash
           :rtype: None
           :return: None
        """
        self.srv.service.users().messages().trash(userId='me', id=self.MessageId).execute()
    def markAsSpam(self) -> None:
        """Moves the message to spam
           :rtype: None
           :return: None
        """
        self.srv.service.users().messages().modify(userId='me', id=self.MessageId,body={'addLabelIds': ['SPAM'],'removeLabelIds': ['INBOX']}).execute()

