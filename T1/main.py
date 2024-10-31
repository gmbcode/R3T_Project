"""Main TMail App File"""
# Todo : Make a LabelSelector Modal Screen (that should display current labels and labels to add / remove )
# Todo : Make a create Label Modal Screen

import os
from typing import Iterable
from textual.containers import HorizontalScroll
from textual.widgets import SelectionList

from UI_Elements import *
import asyncio

skip_size_checks = True

if not skip_size_checks:
    width = os.get_terminal_size().columns
    length = os.get_terminal_size().lines
    # Check terminal size
    if width <= 120 or length <= 30:
        print("Please resize terminal to at least 120cols x 30 lines  and restart terminal to continue")
        os.system("pause")
        quit(0)


class T_Mail_App(App):
    CSS_PATH = 'main.tcss'
    BINDINGS = [
        Binding("ctrl+d", "toggle_dark", "Toggle Dark Mode", show=True),
        Binding("v", "view_mail", "View Mail", show=True),
        Binding("ctrl+t", "toggle_read_unread", "Toggle Read/Unread", show=True),
        Binding("ctrl+x", "move_to_trash", "Move to Trash", show=True),
        Binding("ctrl+c", "request_quit", "Quit", show=True, priority=True),
        Binding("ctrl+l", "report_as_spam", "Report message as spam", show=True),
        Binding("m", "mark_for_batch_action", "Mark email", show=True),
        Binding("ctrl+r", "initiate_reload", "Reload emails"),
        Binding("ctrl+s", "initiate_search", "Search for emails", show=True)
    ]

    def __init__(self):
        self.cur_row = 1
        self.srv = GmailFetcher.GmailService()
        self.lresp = (())
        self.id_lst = []
        self.cur_co_ord = Coordinate(0, 0)
        self.table = None
        self.batch_action_count = 0
        super().__init__()

    def compose(self) -> ComposeResult:
        """
        Create child widgets for the app.
        :return: ComposeResult Object
        :rtype: ComposeResult
        """
        gradient = Gradient.from_colors(
            "#881177",
            "#aa3355",
            "#cc6666",
            "#ee9944",
            "#eedd00",
            "#99dd55",
            "#44dd88",
            "#22ccbb",
            "#00bbcc",
            "#0099cc",
            "#3366bb",
            "#663399",
        )
        yield Header()
        yield ProgressBar(gradient=gradient)
        yield DataTable()
        yield Label(id="footer_label")
        yield Footer()

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("View Mail (v)", "View the currently selected mail", self.action_view_mail)
        yield SystemCommand("Toggle Read/Unread (Ctrl+t)", "Toggle Read/Unread on currently selected / marked mails.",
                            self.action_toggle_read_unread)
        yield SystemCommand("Mark for batch action (m)", "Marks the selected mail for batch action",
                            self.action_mark_for_batch_action)
        yield SystemCommand("Move to trash (Ctrl+x)", "Moves the selected mails to trash", self.action_move_to_trash)
        yield SystemCommand("Report as spam (Ctrl+l)", "Reports the selected mails as spam", self.action_report_as_spam)
        yield SystemCommand("Search (Ctrl+s)", "Search for emails", self.action_initiate_search)
        yield SystemCommand("Reload app (Ctrl+r)", "Reload the app", self.action_initiate_reload)

    def action_toggle_dark(self) -> None:
        """
        Toggles Dark Mode
        :return: None
        :rtype: None
        """
        self.dark = not self.dark

    def on_mount(self) -> None:
        """
        On Mount Handler
        :return: None
        :rtype: None
        """
        self.title = "TMail v0.1.2"
        self.table = self.query_one(DataTable)
        self.query_one(ProgressBar).update(total=50)
        lb = self.query_one("#footer_label", Label)
        lb.styles.dock = "top"
        self.set_timer(0.5, self.load_rows)

    async def load_rows(self, r_max=50, l_interval=10) -> None:
        """
        Loads rows of emails into the UI
        :param r_max: Maximum number of rows to load
        :param l_interval: Number of rows to load in one go
        :return: None
        :rtype: None
        """
        rows_loaded = 0
        pgt = "start"
        self.rows = []
        self.table.add_columns('From', 'Subject')
        while rows_loaded < r_max and len(pgt) > 1:
            if pgt == "start":
                self.lresp = load_rows(l_interval=l_interval)
                self.id_lst = self.lresp[0][1]
            else:
                self.lresp = load_rows(pgt=pgt, l_interval=l_interval)
            resp_rows = self.lresp[0][0]
            resp_id_lst = self.lresp[0][1]
            if pgt != "start":
                self.id_lst += resp_id_lst
            pgt = self.lresp[1]
            self.rows += resp_rows
            logger.info(str(self.rows))
            logger.info(str(self.id_lst))
            for singular_row in resp_rows:
                to_add = singular_row[:2]
                self.table.add_row(*to_add, label=singular_row[2])
            self.query_one(ProgressBar).advance(l_interval)
            await asyncio.sleep(0.2)
            rows_loaded += l_interval
        logger.info(f"Total rows loaded {len(self.rows)}")
        await self.query_one(ProgressBar).remove()

    async def load_rows_sq(self, search_query, r_max=10, l_interval=1) -> None:
        """
        Loads rows of emails into the UI
        :param r_max: Maximum number of rows to load
        :param l_interval: Number of rows to load in one go
        :return: None
        :rtype: None
        """
        rows_loaded = 0
        pgt = "start"
        self.rows = []
        self.table.add_columns('From', 'Subject')
        while rows_loaded < r_max and len(pgt) > 1:
            if pgt == "start":
                self.lresp = load_rows_sq(search_query, l_interval=l_interval)
                if self.lresp is None:
                    await self.query_one(ProgressBar).remove()
                    return
                self.id_lst = self.lresp[0][1]
            else:
                self.lresp = load_rows_sq(search_query, pgt=pgt, l_interval=l_interval)
                if self.lresp is None:
                    await self.query_one(ProgressBar).remove()
                    return
            resp_rows = self.lresp[0][0]
            resp_id_lst = self.lresp[0][1]
            if pgt != "start":
                self.id_lst += resp_id_lst
            pgt = self.lresp[1]
            self.rows += resp_rows
            logger.info(str(self.rows))
            logger.info(str(self.id_lst))
            for singular_row in resp_rows:
                to_add = singular_row[:2]
                self.table.add_row(*to_add, label=singular_row[2])
            self.query_one(ProgressBar).advance(l_interval)
            await asyncio.sleep(0.2)
            rows_loaded += l_interval
        logger.info(f"Total rows loaded {len(self.rows)}")
        await self.query_one(ProgressBar).remove()

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        """
        Set the current highlighted cell
        :param event: DataTable.CellHighlighted: Event when the DataTable cell is highlighted
        :return: None
        :rtype: None
        """
        logger.info(f"Current row changed to {event.coordinate.row}")
        self.cur_row = event.coordinate.row
        self.cur_co_ord = event.coordinate

    def action_initiate_reload(self) -> None:
        """
        Reload all emails
        :return: None
        :rtype: None
        """
        dt = self.query_one(DataTable)
        dt.clear()
        self.mount(ProgressBar(), before=dt)
        self.query_one(ProgressBar).update(total=50)
        self.set_timer(0.5, self.load_rows)

    def action_initiate_search_populate(self, search_query, no_of_results) -> None:
        """
        Reload all emails
        :return: None
        :rtype: None
        """
        dt = self.query_one(DataTable)
        dt.clear()
        self.mount(ProgressBar(), before=dt)
        self.query_one(ProgressBar).update(total=no_of_results)
        loader = lambda: self.load_rows_sq(search_query, r_max=no_of_results)
        self.set_timer(0.5, loader)

    def action_request_quit(self) -> None:
        """
        Confirm if user wants to quit
        :return: None
        :rtype: None
        """
        self.push_screen(Quit_Check())

    def action_view_mail(self) -> None:
        """
        View a particular mail
        :return: None
        :rtype: None
        """
        logger.info(self.id_lst[self.cur_row])
        msg = Message.Gmail_Message(self.id_lst[self.cur_row], srv)
        body = msg.getBody()
        self.push_screen(
            View_Body(self.id_lst[self.cur_row], self.rows[self.cur_row][0], self.rows[self.cur_row][1],
                      body, msg))

    def action_toggle_read_unread(self) -> None:
        """
        Toggle if a message is read or unread
        :return: None
        :rtype: None
        """
        logger.info("Initiated toggle r/ur action ")
        dt = self.query_one(DataTable)
        row_lst = dt.get_column_at(0)
        actionable_ids = []
        actionable_indexes = []
        r_index = 0
        for singular_row in row_lst:
            if singular_row[:5] == '[red]' and singular_row[-6:] == '[/red]':
                actionable_ids.append(self.id_lst[r_index])
                actionable_indexes.append(r_index)
            r_index += 1
        if len(actionable_indexes) <= 1:
            sbj = dt.get_cell_at(Coordinate(self.cur_row, 1))
            msg = Message.Gmail_Message(self.id_lst[self.cur_row], srv)
            if msg.unread:
                msg.markasRead()
                sbj = sbj[:-4]
            else:
                msg.markasUnRead()
                sbj += ' (U)'
            dt.update_cell_at(Coordinate(self.cur_row, 1), sbj, update_width=True)
        else:
            logger.info("Successfully switched to mass read/unread toggle mode ")
            self.batch_action_count = len(actionable_indexes)
            batch_request = srv.service.new_batch_http_request()
            for singular_index in sorted(actionable_indexes, reverse=True):
                sbj0 = dt.get_cell_at(Coordinate(singular_index, 0))
                sbj = dt.get_cell_at(Coordinate(singular_index, 1))
                msg = Message.Gmail_Message(self.id_lst[singular_index], srv)
                if msg.unread:
                    batch_request.add(msg.getMarkAsReadQuery())
                    sbj = sbj[:-4]
                else:
                    batch_request.add(msg.getMarkAsUnReadQuery())
                    sbj += ' (U)'
                dt.update_cell_at(Coordinate(singular_index, 0), sbj0[5:-7])
                dt.update_cell_at(Coordinate(singular_index, 1), sbj, update_width=True)
            batch_request.execute()
            self.batch_action_count = 0

            lb = self.query_one("#footer_label", Label)
            lb.update(renderable="")

            logger.info("Successfully finished mass read/unread toggle ")
        logger.info("Successfully finished toggle r/ur action ")

    def action_move_to_trash(self) -> None:
        """
        Moves the selected message/messages to trash
        :return: None
        :rtype: None
        """
        logger.info("Initiated trash mail action ")
        dt = self.query_one(DataTable)
        row_lst = dt.get_column_at(0)
        actionable_ids = []
        actionable_indexes = []
        r_index = 0
        for singular_row in row_lst:
            if singular_row[:5] == '[red]' and singular_row[-6:] == '[/red]':
                actionable_ids.append(self.id_lst[r_index])
                actionable_indexes.append(r_index)
            r_index += 1
        if len(actionable_indexes) <= 1:
            msg = Message.Gmail_Message(self.id_lst[self.cur_row], srv)
            msg.moveToTrash()
            row_key, _ = dt.coordinate_to_cell_key(self.cur_co_ord)
            dt.remove_row(row_key)
            self.rows.remove(self.rows[self.cur_row])
            self.id_lst.remove(self.id_lst[self.cur_row])
        else:
            self.batch_action_count = len(actionable_indexes)
            logger.info("Switched to mass trash action mode")
            batch_request = srv.service.new_batch_http_request()
            for singular_index in sorted(actionable_indexes, reverse=True):
                msg = Message.Gmail_Message(self.id_lst[singular_index], srv)
                batch_request.add(msg.getMoveToTrashQuery())
                row_key, _ = dt.coordinate_to_cell_key(Coordinate(singular_index, 0))
                dt.remove_row(row_key)
                logger.info(f"Removing row at index {singular_index}")
                del self.rows[singular_index]
                del self.id_lst[singular_index]
            batch_request.execute()
            self.batch_action_count = 0
            lb = self.query_one("#footer_label", Label)
            lb.update(renderable="")
            logger.info("Successfully finished mass trash action")

        logger.info("Successfully finished trash mail action ")

    def action_report_as_spam(self) -> None:
        """
        Moves the selected message to trash
        :return: None
        :rtype: None
        """
        logger.info("Initiated report mail as spam action ")
        dt = self.query_one(DataTable)
        row_lst = dt.get_column_at(0)
        actionable_ids = []
        actionable_indexes = []
        r_index = 0
        for singular_row in row_lst:
            if singular_row[:5] == '[red]' and singular_row[-6:] == '[/red]':
                actionable_ids.append(self.id_lst[r_index])
                actionable_indexes.append(r_index)
            r_index += 1

        if len(actionable_indexes) <= 1:
            msg = Message.Gmail_Message(self.id_lst[self.cur_row], srv)
            msg.markAsSpam()
            row_key, _ = dt.coordinate_to_cell_key(self.cur_co_ord)
            dt.remove_row(row_key)
            self.rows.remove(self.rows[self.cur_row])
            self.id_lst.remove(self.id_lst[self.cur_row])
        else:
            self.batch_action_count = len(actionable_indexes)
            logger.info("Switched to mass spam report mode")
            self.srv.service.users().messages().batchModify(userId='me',
                                                            body={'ids': actionable_ids, 'addLabelIds': ['SPAM'],
                                                                  'removeLabelIds': ['INBOX']}).execute()

            for singular_index in sorted(actionable_indexes, reverse=True):
                row_key, _ = dt.coordinate_to_cell_key(Coordinate(singular_index, 0))
                dt.remove_row(row_key)
                logger.info(f"Removing row at index {singular_index}")
                del self.rows[singular_index]
                del self.id_lst[singular_index]
            self.batch_action_count = 0
            lb = self.query_one("#footer_label", Label)
            lb.update(renderable="")
            logger.info("Successfully finished mass spam report")

        logger.info("Successfully finished report mail as spam action ")

    def action_mark_for_batch_action(self) -> None:
        """
        Mark the current email for further batch commands
        :return: None
        :rtype: None
        """
        dt = self.query_one(DataTable)
        sbj = dt.get_cell_at(Coordinate(self.cur_row, 0))
        if sbj[:5] == '[red]' and sbj[-6:] == '[/red]':
            self.batch_action_count -= 1
            if self.batch_action_count > 0:
                lb = self.query_one("#footer_label", Label)
                lb.update(renderable=f"[red]Selected  ({self.batch_action_count}) emails [/red]")
            else:
                lb = self.query_one("#footer_label", Label)
                lb.update(renderable="")
            dt.update_cell_at(Coordinate(self.cur_row, 0), sbj[5:-7])
        else:
            if self.batch_action_count > 100:
                self.app.push_screen(Too_Many_Selections())
            else:
                self.batch_action_count += 1
                lb = self.query_one("#footer_label", Label)
                lb.update(renderable=f"[red]Selected  ({self.batch_action_count}) emails [/red]")
                dt.update_cell_at(Coordinate(self.cur_row, 0), f"[red]{sbj}[/red]")

    def action_initiate_search(self) -> None:
        """
        Display Search Query Selector Popup
        :return: None
        :rtype: None
        """

        def handle_search_screen(search_query_info: tuple) -> None:
            """
            Begin Search Process as soon as search query is received
            :param search_query_info: The parameter containing information about the search query
            :return: None
            :rtype: None
            """
            self.action_initiate_search_populate(*search_query_info)

        self.app.push_screen(Search_Query_Selector(), handle_search_screen)


app = T_Mail_App()
app.run()
