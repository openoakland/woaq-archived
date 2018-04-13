import csv
import getopt
import sys
from datetime import datetime, timedelta
from itertools import takewhile

import pynmea2
from more_itertools import peekable
from pytz import timezone, utc


# TODO(smcclellan): Add unit tests
class AqGpsJoiner:
    """Joins air quality data (as CSV) and GPS data (as NMEA sentences) into CSV output"""

    def __init__(self, aq_data, gps_data):
        """
        :param aq_data: Air quality data, should be passed as an iterable containing as lines of CSV text
        :param gps_data: GPS data, should be passed as an iterable containing NMEA sentences
        """

        # Assume Pacific timezone
        self.timezone = timezone('America/Los_Angeles')

        # Read metadata from start of air quality data as lines of {attribute},{value} pairs
        self.metadata = {}

        aq_itr = iter(aq_data)
        metadata_lines = takewhile(lambda x: x.strip(), aq_itr)  # AQ metadata is terminated by a blank line
        for ml in metadata_lines:
            sp = ml.split(',')
            attribute = sp[0].strip()
            value = sp[1].strip()
            self.metadata[attribute] = value

        # E.g. '07/17/2014'
        aq_start_date = datetime.strptime(self.metadata['Test Start Date'], '%m/%d/%Y').date()

        # E.g. 12:40:35 PM
        aq_start_time =\
            datetime.strptime(self.metadata['Test Start Time'], '%I:%M:%S %p').time()

        # Starting datetime used for matching GPS records with AQ records
        self._aq_start_datetime = self.timezone.localize(datetime.combine(aq_start_date, aq_start_time))

        self._gps_date = None
        self._gps_time = None
        self._gps_datetime = None
        self._gps_lat = None
        self._gps_lon = None
        self._gps_peekable = peekable(gps_data)

        # Churn through GPS data until we have established the date and time, and caught up with the AQ start time
        while self._gps_datetime is None or self._gps_datetime < self._aq_start_datetime:
            gps = self._parse_peek_gps()
            if hasattr(gps, 'datestamp'):
                self._gps_date = gps.datestamp
            if hasattr(gps, 'timestamp'):
                self._gps_time = gps.timestamp
            if hasattr(gps, 'lat'):
                self._gps_lat = gps.lat
            if hasattr(gps, 'lon'):
                self._gps_lon = gps.lon
            if self._gps_date is not None and self._gps_time is not None:
                self._gps_datetime = utc.localize(datetime.combine(self._gps_date, self._gps_time))
            if self._gps_datetime is None or self._gps_datetime < self._aq_start_datetime:
                self._gps_peekable.next()

        # AQ metadata (and terminal blank line) should be followed by normal CSV header
        self._aq_peekable = peekable(csv.DictReader(aq_itr, delimiter=','))

        # Churn through AQ data until caught up with GPS start time
        aq_datetime = self._aq_start_datetime
        while aq_datetime < self._gps_datetime:
            aq = self._aq_peekable.peek()
            aq_datetime = self._aq_start_datetime + timedelta(seconds=int(aq['Elapsed Time [s]']))
            if aq_datetime < self._gps_datetime:
                self._aq_peekable.next()

        self._output_header = True

    def __iter__(self):
        return self

    def next(self):
        """
        :return: Combined air quality and GPS data as a line of CSV text
        """
        if self._output_header:
            # TODO(smcclellan): Determine correct output format
            self._output_header = False
            return 'timestamp,mass,latitude,longitude'

        aq = self._aq_peekable.next()
        timestamp = self._aq_start_datetime + timedelta(seconds=int(aq['Elapsed Time [s]']))
        mass = aq['Mass [mg/m3]']

        while self._gps_datetime < timestamp:
            gps = self._parse_peek_gps()
            if hasattr(gps, 'datestamp'):
                self._gps_date = gps.datestamp
            if hasattr(gps, 'timestamp'):
                self._gps_time = gps.timestamp
            if hasattr(gps, 'lat'):
                self._gps_lat = gps.lat
            if hasattr(gps, 'lon'):
                self._gps_lon = gps.lon
            self._gps_datetime = datetime.combine(self._gps_date, self._gps_time).replace(tzinfo=utc)
            if self._gps_datetime < timestamp:
                self._gps_peekable.next()

        return '{ts},{m},{lat},{lon}'.format(
            ts=timestamp.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            m=mass,
            lat=self._gps_lat,
            lon=self._gps_lon)

    def _parse_peek_gps(self):
        peek = None
        while not peek:
            try:
                peek = pynmea2.parse(self._gps_peekable.peek().strip())
            except pynmea2.nmea.SentenceTypeError:
                self._gps_peekable.next()
        return peek


if __name__ == "__main__":
    aq_file = ''
    gps_file = ''
    output_file = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ha:g:o:', ['aq=', 'gps=', 'out='])
    except getopt.GetoptError:
        print 'joiner.py -a <air-quality-file.csv> -g <gps-file.log> -o <output.csv>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ('-a', '--aq'):
            aq_file = arg
        elif opt in ('-g', '--gps'):
            gps_file = arg
        elif opt in ('-o', '--out'):
            output_file = arg

    with open(aq_file, 'r') as a:
        with open(gps_file, 'r') as g:
            with open(output_file, 'wb') as o:
                o.writelines("%s\n" % l for l in AqGpsJoiner(a, g))
