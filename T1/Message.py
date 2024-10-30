"""TMail Message Library"""
import GmailFetcher
import base64
import dateutil.parser as parser
import logging
from datetime import datetime
logger = logging.getLogger(__name__)
logging.basicConfig(filename='msg.log', encoding='utf-8', level=logging.DEBUG)
logger.info(" App started at " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


class Gmail_Message:
    def __init__(self, id: str, srv: GmailFetcher.GmailService):
        self.MessageId = id
        self.srv = srv
        self.full_message_loaded = False
        self.Message = self.srv.service.users().messages().get(userId='me', id=id, format='metadata').execute()
        self.labels = self.Message['labelIds']
        if 'UNREAD' in self.labels:
            self.unread = True
        else:
            self.unread = False

    def getBody(self) -> str:
        """
        Returns the body of the message
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
    def hasAttachment(self) -> bool:
        """
        Returns True if the message has attachments , False otherwise
        :rtype: bool
        :return: If the message has attachments
        """
        if not self.full_message_loaded:
            self.Message = self.srv.service.users().messages().get(userId='me', id=self.MessageId).execute()
            self.full_message_loaded = True
        payload = self.Message['payload']
        to_return = False
        if 'parts' in payload:
            for part in payload['parts']:
                if 'filename' in part:
                    if len(part['filename']) > 0:
                        to_return = True
                    else:
                        pass
                else:
                    pass
        return to_return
    def downloadAttachments(self) -> None:
        """
        Download the attachments if they exist
        :return: None
        :rtype: None
        """
        if not self.full_message_loaded:
            self.Message = self.srv.service.users().messages().get(userId='me', id=self.MessageId).execute()
            self.full_message_loaded = True
        if self.hasAttachment():
            payload = self.Message['payload']
            if 'parts' in payload:
                for part in payload['parts']:
                    file_name = part['filename']
                    body = part['body']
                    if 'attachmentId' in body:
                        attachmentId = body['attachmentId']
                        att_resp = self.srv.service.users().messages().attachments().get(userId='me',messageId=self.MessageId,id=attachmentId).execute()
                        att_data = base64.urlsafe_b64decode(att_resp['data'].encode('UTF-8'))
                        with open(file_name, 'wb') as f:
                            f.write(att_data)







    def getHeading(self) -> str:
        """
        Returns the subject of the message
        :rtype: str
        :return: The subject of the message
        """
        payload = self.Message['payload']
        headers = payload['headers']
        for field in headers:
            if field['name'] == 'Subject':
                return field['value']

    def getFrom(self) -> str:
        """
        Returns details about the sender of the message
        :rtype: str
        :return: The sender of the message
        """
        payload = self.Message['payload']
        headers = payload['headers']
        for field in headers:
            if field['name'] == 'From':
                return field['value']
    def getDate(self) -> str:
        """
        Returns details about the sender of the message
        :rtype: str
        :return: The sender of the message
        """
        payload = self.Message['payload']
        headers = payload['headers']
        for field in headers:
            if field['name'] == 'Date':
                d_obj = parser.parse(field['value'])
                return str(d_obj.date())
    def markasRead(self) -> None:
        """
        Marks the message as read
        :rtype: None
        :return: None
        """
        self.srv.service.users().messages().modify(userId='me', id=self.MessageId,
                                                   body={'removeLabelIds': ['UNREAD']}).execute()

    def markasUnRead(self) -> None:
        """
        Marks the message as unread
        :rtype: None
        :return: None
        """
        self.srv.service.users().messages().modify(userId='me', id=self.MessageId,
                                                   body={'addLabelIds': ['UNREAD']}).execute()
    def getMarkAsUnReadQuery(self) -> None:
        """
        Marks the message as unread
        :rtype: None
        :return: Returns the mark as unread query
        """
        return self.srv.service.users().messages().modify(userId='me', id=self.MessageId,
                                                   body={'addLabelIds': ['UNREAD']})
    def getMarkAsReadQuery(self) -> None:
        """
        Marks the message as unread
        :rtype: None
        :return: Returns the mark as read query
        """
        return self.srv.service.users().messages().modify(userId='me', id=self.MessageId,
                                                   body={'removeLabelIds': ['UNREAD']})
    def moveToTrash(self) -> None:
        """
        Moves the message to trash
        :rtype: None
        :return: None
        """
        self.srv.service.users().messages().trash(userId='me', id=self.MessageId).execute()

    def getMoveToTrashQuery(self):
        """
        Moves the message to trash
        :rtype: None
        :return: Returns the move to trash query
        """
        return self.srv.service.users().messages().trash(userId='me', id=self.MessageId)
    def markAsSpam(self) -> None:
        """
        Moves the message to spam
        :rtype: None
        :return: None
        """
        self.srv.service.users().messages().modify(userId='me', id=self.MessageId, body={'addLabelIds': ['SPAM'],
                                                                                         'removeLabelIds': [
                                                                                             'INBOX']}).execute()
