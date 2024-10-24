"""Main TMail App File"""
import os
from typing import List, Tuple

from textual.containers import HorizontalScroll

from UI_Elements import *
import asyncio
skip_size_checks = True

if not skip_size_checks:
    width = os.get_terminal_size().columns
    length = os.get_terminal_size().lines
    # Check terminal size
    if width <= 120 or length <= 30:
        print("Please resize terminal to at least 120cols x 30 lines to continue")
        os.system("pause")

class T_Mail_App(App):
    BINDINGS = [
        Binding("ctrl+c", "request_quit", "Quit", show=True, priority=True),
        Binding("ctrl+d", "toggle_dark", "Toggle Dark Mode", show=True),
        Binding("v", "view_mail", "View Mail", show=True),
        Binding("ctrl+t", "toggle_read_unread", "Toggle Read/Unread", show=True),
        Binding("ctrl+x", "move_to_trash", "Move to Trash", show=True),
        Binding("ctrl+l", "report_as_spam", "Report message as spam", show=True)
    ]

    def __init__(self):
        self.cur_cell = 1
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app.
        :return: ComposeResult Object
        :rtype: ComposeResult
        """
        yield Header()
        yield ProgressBar()
        yield DataTable()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """Toggles Dark Mode
        :return: None
        :rtype: None
        """
        self.dark = not self.dark

    def on_mount(self) -> None:
        """On Mount Handler
        :return: None
        :rtype: None
        """

        self.table = self.query_one(DataTable)
        self.query_one(ProgressBar).update(total=50)
        self.set_timer(0.5,self.load_rows)

    async def load_rows(self,max=50,l_interval=10):
        rows_loaded = 0
        pgt = "start"
        self.rows = []
        self.table.add_columns('From', 'Subject')
        while rows_loaded < max and len(pgt) > 1:
            if pgt == "start":
                self.lresp = load_rows()
                self.id_lst = self.lresp[0][1]
            else:
                self.lresp = load_rows(pgt=pgt,l_interval=l_interval)
            self.resp_rows = self.lresp[0][0]
            self.resp_id_lst = self.lresp[0][1]
            if pgt!="start":
                self.id_lst += self.resp_id_lst
            pgt = self.lresp[1]
            self.rows += self.resp_rows
            logger.info(str(self.rows))
            logger.info(str(self.id_lst))
            self.table.add_rows(self.resp_rows)
            self.query_one(ProgressBar).advance(l_interval)
            await asyncio.sleep(0.2)
            rows_loaded += l_interval
        await self.query_one(ProgressBar).remove()


    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        """Set the current highlighted cell
        :param event DataTable.CellHighlighted: Event when the DataTable cell is highlighted
        :return: None
        :rtype: None
        """
        global view_mdata
        logger.info(f"Current row changed to {event.coordinate.row}")
        self.cur_cell = event.coordinate.row
        self.cur_co_ord = event.coordinate

    def action_request_quit(self) -> None:
        """Confirm if user wants to quit
        :return: None
        :rtype: None
        """
        self.push_screen(Quit_Check())

    def action_view_mail(self) -> None:
        """View a particular mail
        :return: None
        :rtype: None
        """
        logger.info(self.id_lst[self.cur_cell])
        self.push_screen(
            View_Body(self.id_lst[self.cur_cell], self.rows[self.cur_cell][0], self.rows[self.cur_cell][1],
                      Message.Gmail_Message(self.id_lst[self.cur_cell], srv).getBody()))
    def action_toggle_read_unread(self) -> None:
        """Toggle if a message is read or unread
           :return: None
           :rtype: None
        """
        logger.info("Initiated toggle r/ur action ")
        msg = Message.Gmail_Message(self.id_lst[self.cur_cell], srv)
        dt = self.query_one(DataTable)
        sbj = dt.get_cell_at(Coordinate(self.cur_cell,1))
        if msg.unread:
            msg.markasRead()
            sbj = sbj[:-4]
        else:
            msg.markasUnRead()
            sbj += ' (U)'
        logger.info("Sucessfully finished toggle r/ur action ")
        dt.update_cell_at(Coordinate(self.cur_cell,1),sbj,update_width=True)
    def action_move_to_trash(self) -> None:
        """Moves the selected message to trash
           :return: None
           :rtype: None
        """
        logger.info("Initiated trash mail action ")
        msg = Message.Gmail_Message(self.id_lst[self.cur_cell], srv)
        dt = self.query_one(DataTable)
        msg.moveToTrash()
        row_key, _ = dt.coordinate_to_cell_key(self.cur_co_ord)
        dt.remove_row(row_key)
        self.rows.remove(self.rows[self.cur_cell])
        self.id_lst.remove(self.id_lst[self.cur_cell])
        logger.info("Successfully finished trash mail action ")
    def action_report_as_spam(self) -> None:
        """Moves the selected message to trash
           :return: None
           :rtype: None
        """
        logger.info("Initiated report mail as spam action ")
        msg = Message.Gmail_Message(self.id_lst[self.cur_cell], srv)
        dt = self.query_one(DataTable)
        msg.markAsSpam()
        row_key, _ = dt.coordinate_to_cell_key(self.cur_co_ord)
        dt.remove_row(row_key)
        self.rows.remove(self.rows[self.cur_cell])
        self.id_lst.remove(self.id_lst[self.cur_cell])
        logger.info("Successfully finished report mail as spam action ")







app = T_Mail_App()
app.run()
