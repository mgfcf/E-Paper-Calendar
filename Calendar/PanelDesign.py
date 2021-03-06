from DesignEntity import DesignEntity
from TechnicalDataDesign import TechnicalDataDesign
from settings import print_technical_data
from datetime import datetime


class PanelDesign (DesignEntity):
    """Defined general interface for panel designs."""

    def __init__(self, size):
        super(PanelDesign, self).__init__(size)
        self.start_timestamp = datetime.now()

    def add_weather(self, weather):
        pass

    def add_calendar(self, calendar):
        pass

    def add_rssfeed(self, rss):
        pass

    def add_tasks(self, tasks):
        pass

    def add_crypto(self, crypto):
        pass

    def __finish_panel__(self):
        pass

    def __finish_image__(self):
        self.__finish_panel__()

        if print_technical_data:
            td = TechnicalDataDesign(
                self.size, self.start_timestamp, datetime.now())
            td.mask = True
            self.draw_design(td)
