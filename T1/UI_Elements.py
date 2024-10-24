import logging
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Grid, ScrollableContainer, Center, Middle, Horizontal
from textual.widgets import Header, Footer, DataTable, Label, Button, Static,ProgressBar
from textual.binding import Binding
from textual.screen import ModalScreen
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
def get_summary(text : str) -> str:
    if len(text) > 600:
        text = text[:600]
    return model.generate_content("Generate a concise summary of the following email body in less than 200 words\n"+text).text
def load_rows(pgt="",l_interval=5) -> tuple:
    rows = []
    id_lst = []
    if len(pgt) > 1:
        msg_lst = srv.service.users().messages().list(userId='me', maxResults=l_interval, labelIds=["INBOX"],pageToken=pgt).execute()
        if 'nextPageToken' in msg_lst:
            pgt = msg_lst['nextPageToken']
        else :
            pgt = ""
    else:
        msg_lst = srv.service.users().messages().list(userId='me', maxResults=l_interval, labelIds=["INBOX"]).execute()
        if 'nextPageToken' in msg_lst:
            pgt = msg_lst['nextPageToken']
        else :
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

        rows.append((G_msg.getFrom(), G_msg.getHeading() + post_add))
    return (rows, id_lst),pgt
class Quit_Check(ModalScreen):
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield Label("Are you sure you want to quit?", id="question")
                yield Horizontal( Button("Quit", variant="error", id="quit"),
                            Button("Cancel", variant="primary", id="cancel") )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
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
        logger.info("Composed VB Summary")
        yield ScrollableContainer(
            Label(f"From : {self.frm}", id="message_from"),
            Label(f"Subject : {self.hdg}", id="message_subject"),
            Static(f"Summary of Message : \n {self.body}", id="message_body"),
            Button("Close", variant="error", id="quit")
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close the view on pressing close button
           :return: None
           :rtype: None
        """
        self.app.pop_screen()

    def action_close_view(self) -> None:
        """Close the view on appropriate action
        :return: None
        :rtype: None
        """
        self.app.pop_screen()
class View_Body(ModalScreen):
    BINDINGS = [
        Binding("c", "close_view", "Close", show=True, priority=True),
        Binding("s","summarize_text","Summarize text",show=True)]

    def __init__(self, id, frm, hdg, body):
        self.m_id = id
        self.frm = frm
        self.hdg = hdg
        self.body = body
        super().__init__()

    def compose(self) -> ComposeResult:
        logger.info("Composed")
        yield ScrollableContainer(
            Label(f"From : {self.frm}", id="message_from"),
            Label(f"Subject : {self.hdg}", id="message_subject"),
            Static(f"Message : \n {self.body}", id="message_body"),
            Button("Close", variant="error", id="quit")
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close the view on pressing close button
           :return: None
           :rtype: None
        """
        self.app.pop_screen()
    def action_summarize_text(self) -> None:
        """Generate a summary of the email body
                   :return: None
                   :rtype: None
        """
        logger.info("Pushed Summary Screen")
        self.app.push_screen(View_Body_Summary(self.m_id, self.frm, self.hdg, get_summary(self.body)))
    def action_close_view(self) -> None:
        """Close the view on appropriate action
        :return: None
        :rtype: None
        """
        self.app.pop_screen()
