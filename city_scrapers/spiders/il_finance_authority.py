import re
import datetime
from io import BytesIO

from city_scrapers_core.constants import BOARD, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import pdfplumber
import logging

class IlFinanceAuthoritySpider(CityScrapersSpider):
    name = "il_finance_authority"
    agency = "Illinois Finance Authority"
    timezone = "America/Chicago"
    default_office_name = "Michael A. Bilandic Building"
    default_office_location = "160 North LaSalle Street, Suite S-1000, Chicago, Illinois 60601"
    homepage = "https://www.il-fa.com"
    board_meeting_name = "Board Meeting"

    def __init__(self, *args, **kwargs):
        logging.getLogger("pdfminer").setLevel(logging.INFO)
        super().__init__(*args, **kwargs)
        self.future_meetings_pdf = f"https://www.il-fa.com/sites/default/files/homepage_pdf/fy_{self.year + 1}_meeting_schedule.pdf"
        self.board_documents_this_year = f"https://www.il-fa.com/public-access/board-documents/{self.year}"
        self.board_documents_last_year = f"https://www.il-fa.com/public-access/board-documents/{self.year - 1}"
        self.start_urls = [self.future_meetings_pdf, self.board_documents_this_year, self.board_documents_last_year]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        if response.url == self.future_meetings_pdf:
            return self._parse_future_board_meetings(response)
        else:
            pass

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self):
        """Parse or generate location."""
        return {
            "address": self.default_office_location,
            "name": self.default_office_name,
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _parse_dates(self, pdf_text):
        """Parse PDF for date"""

        # Find and extract strings for month/day/year:
        regex = re.compile(r"(?P<month>[a-zA-Z]+) (?P<day>[0-9]+), (?P<year>[0-9]{4})")
        
        for m in regex.finditer(pdf_text):
            try:
                yield datetime.datetime.strptime(m.group(0), "%B %d, %Y")
            except AttributeError:  # Regex failed to match.
                return None

        return None
    
    def _parse_times(self, pdf_text):
        """Parse PDF for time"""

        # Find and extract strings for month/day/year:
        regex = re.compile(r"([0-1]?[0-9]|2[0-3]):[0-5][0-9] [a-zA-Z]{2}")
        
        for m in regex.finditer(pdf_text):
            try:
                yield datetime.datetime.strptime(m.group(0), "%I:%M %p").time()
            except AttributeError:  # Regex failed to match.
                return None

        return None

    def _parse_past_board_meetings(self, response):
        """Parse PDF with agenda for date + time and store link + date"""
        pdf_obj = pdfplumber.load(BytesIO(response.body))
        pdf_text = pdf_obj.pages[0].extract_text()
        print(pdf_text)
        time_regex = re.compile(r"(?P<hour>[0-1]?[0-9]|2[0-3]):(?P<minutes>[0-5][0-9]) (?P<ampm>[a-zA-Z]{2})")

        m = time_regex.search(pdf_text)
        try:
            time = next(self._parse_times(pdf_text))
        except AttributeError:
            time = datetime.time(9, 30)
        
        for date in self._parse_dates(pdf_text):
            meeting = Meeting(
                title=self.board_meeting_name,
                description="",  # Too inconsistent to parse accurately
                classification=BOARD,
                start=datetime.datetime.combine(date, time),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(),
                links=[{"href": self.homepage, "title": "IFA Homepage"}],
                source=response.url,
            )
            yield meeting
    
    def _parse_future_board_meetings(self, response):
        """Parse PDF with agenda for date + time and store link + date"""
        pdf_obj = pdfplumber.load(BytesIO(response.body))
        pdf_text = pdf_obj.pages[0].extract_text()
        print(pdf_text)
        time_regex = re.compile(r"(?P<hour>[0-1]?[0-9]|2[0-3]):(?P<minutes>[0-5][0-9]) (?P<ampm>[a-zA-Z]{2})")

        m = time_regex.search(pdf_text)
        try:
            time = next(self._parse_times(pdf_text))
        except AttributeError:
            time = datetime.time(9, 30)
        
        for date in self._parse_dates(pdf_text):
            meeting = Meeting(
                title=self.board_meeting_name,
                description="",  # Too inconsistent to parse accurately
                classification=BOARD,
                start=datetime.datetime.combine(date, time),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(),
                links=[{"href": self.homepage, "title": "IFA Homepage"}],
                source=response.url,
            )
            yield meeting




