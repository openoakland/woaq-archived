import csv
import pynmea2
from datetime import datetime, timedelta
from more_itertools import peekable
from pytz import timezone, utc


class AqGpsJoiner:
    """Joins air quality data (as CSV) and GPS data (as NMEA sentences) into CSV output"""

    def __init__(self, aq_data, gps_data):
        """
        :param aq_data: Air quality data, should be passed as an iterable containing as lines of CSV text
        :param gps_data: GPS data, should be passed as an iterable containing NMEA sentences
        """

        # Assume Pacific timezone
        self.timezone = timezone('America/Los Angeles')

        # Read metadata from start of air quality data as lines of {attribute},{value} pairs
        self.metadata = {}

        fieldnames = ['attribute', 'value']
        metadata_reader = csv.DictReader(aq_data, fieldnames=fieldnames, delimiter=',')
        metadata_row = metadata_reader.next()
        while metadata_row['attribute']:  # AQ metadata is terminated by a blank line
            attribute = metadata_row['attribute']
            value = metadata_row['value']
            self.metadata[attribute] = value
            metadata_row = metadata_reader.next()

        # E.g. '07/17/2014'
        aq_start_date = datetime.strptime(self.metadata['Test Start Date'], '%m/%d/%Y').date()

        # E.g. 12:40:35 PM
        aq_start_time =\
            datetime.strptime(self.metadata['Test Start Time'], '%I:%M:%S %p').time().replace(tzinfo=self.timezone)

        # Starting datetime used for matching GPS records with AQ records
        self._aq_start_datetime = datetime.combine(aq_start_date, aq_start_time)

        self._gps_date = None
        self._gps_time = None
        self._gps_datetime = None
        self._gps_peekable = peekable(gps_data)

        # Churn through GPS data until we have established the date and time, and caught up with the AQ start time
        while self._gps_datetime is None or self._gps_datetime < self._aq_start_datetime:
            gps = pynmea2.parse(self._gps_peekable.peek())
            if hasattr(gps, 'datestamp'):
                self._gps_date = gps.datestamp
            if hasattr(gps, 'timestamp'):
                self._gps_time = gps.timestamp
            if self._gps_date is not None and self._gps_time is not None:
                self._gps_datetime = datetime.combine(self._gps_date, self._gps_time).replace(tzinfo=utc)
            if self._gps_datetime is None or self._gps_datetime < self._aq_start_datetime:
                self._gps_peekable.next()

        # AQ metadata (and terminal blank line) should be followed by normal CSV header
        self._aq_peekable = peekable(csv.DictReader(aq_data, delimiter=','))

        # Churn through AQ data until caught up with GPS start time
        self._aq_datetime = self._aq_start_datetime
        while self._aq_datetime < self._gps_datetime:
            aq = self._aq_peekable.peek()
            self._aq_datetime = self._aq_datetime + timedelta(seconds=aq['Elapsed Time [s]'])
            if self._aq_datetime < self._gps_datetime:
                self._aq_peekable.next()

    def __iter__(self):
        return self

    def header(self):
        return "timestamp,mass,latitude,longitude"

    def next(self):
        """
        :return: Combined air quality and GPS data as a line of CSV text
        """
        # TODO(smcclellan): Implement
