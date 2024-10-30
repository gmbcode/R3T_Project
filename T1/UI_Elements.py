import logging
from datetime import datetime
from rich.markdown import Markdown
from textual.app import App, ComposeResult,SystemCommand
from textual.containers import Grid, ScrollableContainer, Center, Middle, Horizontal
from textual.widgets import Header, Footer, DataTable, Label, Button, Static, ProgressBar, Markdown
from textual.binding import Binding
from textual.color import Gradient
from textual.screen import ModalScreen,Screen
from textual.coordinate import Coordinate
from rich.text import Text
import Message
import GmailFetcher
import google.generativeai as genai
from dotenv import dotenv_values
config = dotenv_values(".env")
api_key = config['GEMINI_API_KEY']
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
logger = logging.getLogger(__name__)
logging.basicConfig(filename='t1app.log', encoding='utf-8', level=logging.DEBUG)
logger.info(" App started at " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
srv = GmailFetcher.GmailService()


def get_summary(text: str) -> str:
    if len(text) > 1000:
        text = text[:1000]
    return model.generate_content(
        "Generate a concise summary of the following email body in less than 200 words\n" + text).text


def text_sanitizer(text: str) -> str:
    """
    Sanitizes the text to prevent malicious text from being processed as a selection
    :param text: str: Input text to be sanitized
    :return: Returns sanitized text
    :rtype: str
    """
    if text[:5] == '[red]' and text[-6:] == '[/red]':
        while text[:5] == '[red]' and text[-6:] == '[/red]':
            text = text[5:-7]
        return text
    else:
        return text


def load_rows(pgt="", l_interval=5) -> tuple:
    """
    Return a tuple of row data to be loaded into the UI
    :param pgt: Next page token to load new rows
    :rtype : tuple
    :return : A tuple containing row data to be loaded into the UI
    """
    rows = []
    id_lst = []
    if len(pgt) > 1:
        msg_lst = srv.service.users().messages().list(userId='me', maxResults=l_interval, labelIds=["INBOX"],
                                                      pageToken=pgt).execute()
        if 'nextPageToken' in msg_lst:
            pgt = msg_lst['nextPageToken']
        else:
            pgt = ""
    else:
        msg_lst = srv.service.users().messages().list(userId='me', maxResults=l_interval, labelIds=["INBOX"]).execute()
        if 'nextPageToken' in msg_lst:
            pgt = msg_lst['nextPageToken']
        else:
            pgt = ""
    for msg in msg_lst['messages']:
        id_1 = msg['id']
        id_lst.append(id_1)
        G_msg = Message.Gmail_Message(id_1, srv)
        post_add = ""
        if G_msg.unread:
            logger.info(f"Message {id_1} is unread ")
            post_add += " (U)"
        else:
            logger.info(f"Message {id_1} is read ")

        rows.append((text_sanitizer(G_msg.getFrom()), G_msg.getHeading() + post_add,G_msg.getDate()))
    return (rows, id_lst), pgt


class Quit_Check(ModalScreen):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Are you sure you want to quit?", id="question")
                yield Horizontal(Button("Quit", variant="error", id="quit"),
                                 Button("Cancel", variant="primary", id="cancel"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()


class Too_Many_Selections(ModalScreen):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Too many emails selected for batch action\nCannot select more than 100",
                            id="main_dialog_text")
                yield Horizontal(Button("Ok", variant="error", id="close_dialog"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()
class No_Attachments_Exist(ModalScreen):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("No attachments exist",
                            id="main_dialog_text")
                yield Horizontal(Button("Ok", variant="error", id="close_dialog"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()
class Successfully_Downloaded_Attachments(ModalScreen):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Successfully downloaded attachments",
                            id="main_dialog_text")
                yield Horizontal(Button("Ok",id="close_dialog"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()
class View_Body_Summary(ModalScreen):
    """View Body Summary Screen"""
    BINDINGS = [
        Binding("c", "close_view", "Close", show=True, priority=True)]

    def __init__(self, id, frm, hdg, body):
        self.m_id = id
        self.frm = frm
        self.hdg = hdg
        self.body = body
        super().__init__()

    def compose(self) -> ComposeResult:
        logger.info("Composed Body Summary")
        yield ScrollableContainer(
            Label(f"From : {self.frm}", id="message_from"),
            Label(f"Subject : {self.hdg}", id="message_subject"),
            Static(f"Summary of Message : \n {self.body}", id="message_body"),
            Button("Close", variant="error", id="quit")
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Close the view on pressing close button
        :return: None
        :rtype: None
        """
        self.app.pop_screen()

    def action_close_view(self) -> None:
        """
        Close the view on appropriate action
        :return: None
        :rtype: None
        """
        self.app.pop_screen()


class View_Body(ModalScreen):
    """Custom Screen to view Body of email along with options to view email summary"""
    BINDINGS = [
        Binding("c", "close_view", "Close", show=True, priority=True),
        Binding("s", "summarize_text", "Summarize text", show=True),
        Binding("a","download_attachments","Download attachments",show=True)]

    def __init__(self, id, frm, hdg, body,msgobj :Message.Gmail_Message):
        self.m_id = id
        self.frm = frm
        self.hdg = hdg
        self.body = body
        self.msgobj = msgobj
        super().__init__()

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Label(f"From : {self.frm}", id="message_from"),
            Label(f"Subject : {self.hdg}", id="message_subject"),
            Static(f"Message : \n {self.body}", id="message_body"),
            Button("Close", variant="error", id="quit")
        )
        yield Footer()
        logger.info("Composed")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Close the view on pressing close button
        :return: None
        :rtype: None
        """
        self.app.pop_screen()

    def action_summarize_text(self) -> None:
        """
        Generate a summary of the email body
        :return: None
        :rtype: None
        """
        logger.info("Pushed Summary Screen")
        self.app.push_screen(View_Body_Summary(self.m_id, self.frm, self.hdg, get_summary(self.body)))

    def action_close_view(self) -> None:
        """
        Close the view on appropriate action
        :return: None
        :rtype: None
        """
        self.app.pop_screen()
    def action_download_attachments(self) -> None:
        """
        Download the attachments if they exist
        :return: None
        :rtype: None
        """
        if self.msgobj.hasAttachment():
            self.msgobj.downloadAttachments()
            self.app.push_screen(Successfully_Downloaded_Attachments())
            logger.info("Downloaded Attachments")
        else:
            self.app.push_screen(No_Attachments_Exist())
            logger.info("No attachments found")
class Search_Query_Selector(ModalScreen):
    def __init__(self):
        super().__init__()
    def compose(self) -> ComposeResult:
        pass