from DataSourceInterface import DataSourceInterface
from datetime import datetime, timezone, timedelta, date
from dateutil.rrule import rrulestr
from dateutil.parser import parse
import calendar
from CalendarEvent import CalendarEvent


class CalendarInterface (DataSourceInterface):
    """Interface for fetching and processing calendar event information."""

    def __init__(self):
        self.events = []
        self.excluded_urls = []

    def reload(self):
        if self.is_available() == False:
            return
        self.events = self.__get_events__()
        self.events = self.__sort_events__(self.events)

    def exclude_calendars(self, urls=[]):
        self.excluded_urls = urls

    def __sort_events__(self, events):
        events.sort(key=lambda x: x.begin_datetime)
        return events

    def __sort_event_types__(self, events):
        multiday = [ev for ev in events if ev.multiday]
        allday = [ev for ev in events if ev.allday and ev.multiday == False]
        timed = [ev for ev in events if ev.allday ==
                 False and ev.multiday == False]
        return multiday + allday + timed

    def __get_events__(self):
        raise NotImplementedError("Functions needs to be implemented")

    def get_upcoming_events(self, timespan=None, start_time=None):
        if timespan is None:
            timespan = timedelta(31)
        if start_time == None:
            local_tzinfo = datetime.now(timezone.utc).astimezone().tzinfo
            start_time = datetime.now(local_tzinfo)
        return self.__get_events_in_range__(start_time, timespan)

    def get_today_events(self):
        return self.get_day_events(date.today())

    def get_day_events(self, day):
        if type(day) is not type(date.today()):
            raise TypeError(
                "get_day_events only takes date-objects as parameters, not \"%s\"" % str(type(day)))
        local_tzinfo = datetime.now(timezone.utc).astimezone().tzinfo
        day_start = datetime(day.year, day.month, day.day,
                             0, 0, 0, 0, local_tzinfo)
        return self.__get_events_in_range__(day_start, timedelta(1))

    def get_month_events(self, month=-1, year=-1):
        if month < 0:
            month = datetime.now().month
        if year < 0:
            year = datetime.now().year

        local_tzinfo = datetime.now(timezone.utc).astimezone().tzinfo
        month_start = datetime(year, month, 1, 0, 0, 0, 0, local_tzinfo)
        month_days = calendar.monthrange(
            month_start.year, month_start.month)[1]
        return self.__get_events_in_range__(month_start, timedelta(month_days))

    def __get_events_in_range__(self, start, duration):
        if self.events is None:
            return []

        if start.tzinfo is None:
            raise TypeError("start datetime needs to be timezone-aware")

        events_in_range = []
        for event in self.events:
            # Is excluded?
            if event.calendar_url in self.excluded_urls:
                continue

            event_occurrence = self.__get_if_event_in_range__(
                event, start, duration)
            if event_occurrence:
                events_in_range.extend(event_occurrence)

        events_in_range = self.__sort_events__(events_in_range)
        return self.__sort_event_types__(events_in_range)

    def __get_if_event_in_range__(self, event, start, duration):
        '''Returns list or None'''
        if event is None:
            return None

        if event.rrule is None:
            return self.__is_onetime_in_range__(event, start, duration)
        else:
            return self.__is_repeating_in_range__(event, start, duration)

    def __is_onetime_in_range__(self, event, start, duration):
        if event.begin_datetime > start:
            first_start = start
            first_duration = duration
            second_start = event.begin_datetime
        else:
            first_start = event.begin_datetime
            first_duration = event.duration
            second_start = start

        if (second_start - first_start) < first_duration:
            return [event]
        else:
            return None

    def __is_repeating_in_range__(self, event, start, duration):
        end = start + duration
        occurrences = []

        try:
            r_string = ""
            r_string = self.__add_timezoneawarness__(event.rrule)
            rule = rrulestr(r_string, dtstart=event.begin_datetime)
            for occurrence in rule:
                if occurrence - end > timedelta(0):
                    return occurrences
                merged_event = self.__merge_event_data__(
                    event, start=occurrence)
                if self.__is_onetime_in_range__(merged_event, start, duration):
                    occurrences.append(merged_event)
            return occurrences
        except Exception as ex:
            print("\"is_repeating_in_range\" failed while processing: dtstart="+str(event.begin_datetime) +
                  " dtstart.tzinfo="+str(event.begin_datetime.tzinfo)+" rrule="+r_string)
            raise ex

    def __merge_event_data__(self, event, start=None):
        merged_event = CalendarEvent()
        
        merged_event.begin_datetime = event.begin_datetime
        merged_event.end_datetime = event.end_datetime
        merged_event.duration = event.duration
        merged_event.allday = event.allday
        merged_event.multiday = event.multiday
        merged_event.rrule = event.rrule

        merged_event.title = event.title
        merged_event.description = event.description
        merged_event.attendees = event.attendees
        merged_event.highlight = event.highlight

        merged_event.calendar_name = event.calendar_name
        merged_event.calendar_url = event.calendar_url

        merged_event.location = event.location
        merged_event.fetch_datetime = event.fetch_datetime
        
        if start is not None:
            merged_event.begin_datetime = start
            merged_event.end_datetime = start + event.duration

        return merged_event

    def __add_timezoneawarness__(self, rrule):
        """UNTIL must be specified in UTC when DTSTART is timezone-aware (which it is)"""
        if "UNTIL" not in rrule:
            return rrule

        timezone_str = "T000000Z"
        until_template = "UNTIL=YYYYMMDD"

        until_index = rrule.index("UNTIL")

        tz_index = until_index + len(until_template)
        if until_index < 0 or (tz_index < len(rrule) and rrule[tz_index] is "T"):
            return rrule

        if tz_index == len(rrule):
            return rrule + timezone_str
        else:
            return rrule[:tz_index] + timezone_str + rrule[tz_index:]
