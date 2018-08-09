#!/usr/bin/env python2

import calendar
import csv
import getopt
import sys
from datetime import datetime, timedelta
from itertools import takewhile

import pynmea2
from pytz import timezone, utc


class AqGpsJoiner:
    """Joins air quality data (as CSV) and GPS data (as NMEA sentences) into CSV output"""

    def __init__(self, aq_data, gps_data, tdiff_tolerance_secs=1, filter_size='2.5', time_zone='America/Los_Angeles'):
        """
        :param aq_data: Air quality data, should be passed as an iterable containing as lines of CSV text
        :param gps_data: GPS data, should be passed as an iterable containing NMEA sentences
        :param tdiff_tolerance_secs: Air quality readings that are not close in time to any GPS datum will be thrown
               out, where 'close' is defined as within a number of seconds specified by this parameter.
        :param filter_size: The filter size used for air quality measurement
        """

        # Assume AQ data uses Pacific timezone
        aq_timezone = timezone(time_zone)

        self._tolerance = timedelta(seconds=tdiff_tolerance_secs)
        self._filter_size = filter_size

        # Read metadata from start of air quality data as lines of {attribute},{value} pairs
        self._metadata = {}
        #self._metadata = AqGpsJoiner.meta_generate(metadata_lines)
        aq_itr = iter(aq_data)
        metadata_lines = takewhile(lambda x: x.strip(), aq_itr)  # AQ metadata is terminated by a blank line
        for ml in metadata_lines:
            sp = ml.split(',')
            attribute = sp[0].strip()
            value = sp[1].strip()
            self._metadata[attribute] = value

        # E.g. '07/17/2014'
        aq_start_date = datetime.strptime(self._metadata['Test Start Date'], '%m/%d/%Y').date()

        # E.g. 12:40:35 PM
        aq_start_time = \
            datetime.strptime(self._metadata['Test Start Time'], '%I:%M:%S %p').time()

        # Starting datetime used for matching GPS records with AQ records
        self._aq_start_datetime = \
            aq_timezone.normalize(aq_timezone.localize(datetime.combine(aq_start_date, aq_start_time))).astimezone(utc)

        self._gps_datetime = None
        self._gps_lat = None
        self._gps_lon = None

        self._gps_last_datetime = None
        self._gps_last_lat = None
        self._gps_last_lon = None

        self._gps_data = iter(gps_data)

        # Churn through GPS data until we have established the date and time, and caught up with the AQ start time
        while self._gps_datetime is None or self._gps_datetime < self._aq_start_datetime:
            self._gps_last_datetime = self._gps_datetime
            self._gps_last_lat = self._gps_lat
            self._gps_last_lon = self._gps_lon
            gps = self._parse_next_gps()
            self._gps_datetime = utc.normalize(utc.localize(datetime.combine(gps.datestamp, gps.timestamp)))
            self._gps_lat = gps.latitude
            self._gps_lon = gps.longitude

        # AQ metadata (and terminal blank line) should be followed by normal CSV header
        self._aq_data = csv.DictReader(aq_itr, delimiter=',')

        self._output_header = True
    @staticmethod
    def meta_generate(self):
        aq_itr = iter(self.aq_data)
        metadata_lines = takewhile(lambda x: x.strip(), aq_itr)  # AQ metadata is terminated by a blank line
        for ml inက metadata_lines:
            sp = ml.split(',')
            attribute = sp[0].strip()
            value = sp[1].strip()
            self._metadata[attribute] = value
        return

    def __iter__(self):
        return self

    def next(self):
        """
        :return: Combined air quality and GPS data as a line of CSV text
        """
        if self._output_header:
            self._output_header = False
            return 'utc,filter,pm,lat,lon,device'

        line = None
        while line is None:
            aq = self._aq_data.next()
            aq_datetime = utc.normalize(self._aq_start_datetime + timedelta(seconds=int(aq['Elapsed Time [s]'])))

            utc_timestamp = calendar.timegm(aq_datetime.utctimetuple())
            mass = aq['Mass [mg/m3]']
            errors = aq['Errors']

            # TODO(smcclellan): How should this be defined?
            device = errors or 'A'

            while self._gps_datetime < aq_datetime:
                self._gps_last_datetime = self._gps_datetime
                self._gps_last_lat = self._gps_lat
                self._gps_last_lon = self._gps_lon
                gps = self._parse_next_gps()
                self._gps_datetime = utc.normalize(utc.localize(datetime.combine(gps.datestamp, gps.timestamp)))
                self._gps_lat = gps.latitude
                self._gps_lon = gps.longitude

            aq_gps_tdiff = abs(self._gps_datetime - aq_datetime)
            aq_gps_last_tdiff = abs(aq_datetime - self._gps_last_datetime)

            if aq_gps_tdiff <= aq_gps_last_tdiff and aq_gps_tdiff <= self._tolerance:
                # The air quality timestamp is closer to the current GPS measurement, and within tolerance
                line = '{utc},{filter},{pm},{lat:.6f},{lon:.6f},{device}'.format(
                    utc=utc_timestamp,
                    filter=self._filter_size,
                    pm=mass,
                    lat=self._gps_lat,
                    lon=self._gps_lon,
                    device=device)
            elif aq_gps_last_tdiff <= aq_gps_tdiff and aq_gps_last_tdiff <= self._tolerance:
                # The air quality timestamp is closer to the previous GPS measurement, and within tolerance
                line = '{utc},{filter},{pm},{lat:.6f},{lon:.6f},{device}'.format(
                    utc=utc_timestamp,
                    filter=self._filter_size,
                    pm=mass,
                    lat=self._gps_last_lat,
                    lon=self._gps_last_lon,
                    device=device)
                # Otherwise the air quality measurement is not tolerably close to the current or previous GPS
                # GPS measurement and should be skipped

        return line

    def _parse_next_gps(self):
        gps = None
        while not gps:
            try:
                gps = pynmea2.parse(self._gps_data.next().strip())
            except pynmea2.nmea.SentenceTypeError:
                # Throw out unknown GPS sentence types
                gps = None
            if not getattr(gps, 'is_valid', True):
                # Throw out invalid GPS sentences
                gps = None
            if not (getattr(gps, 'datestamp', None) and
                    getattr(gps, 'timestamp', None) and
                    getattr(gps, 'latitude', None) and
                    getattr(gps, 'longitude', None)):
                # Throw out GPS sentences without datestamp, timestamp, latitude, longitude
                gps = None
        return gps


"""if __name__ == "__main__":
    aq_file = ''
    gps_file = ''
    output_file = ''
    tolerance = 1
    filt = '2.5'
    try:
        opts, args = \
            getopt.getopt(sys.argv[1:], 'ha:g:o:t:f:', ['help', 'aq=', 'gps=', 'out=', 'tolerance=', 'filter='])
    except getopt.GetoptError:
        print 'Expected usage: joiner.py -a <air-quality-file.csv> -g <gps-file.log> -o <output.csv> -t 1 -f 2.5'
        raise
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'joiner.py -a <air-quality-file.csv> -g <gps-file.log> -o <output.csv> -t 1 -f 2.5'
            sys.exit()
        elif opt in ('-a', '--aq'):
            aq_file = arg
        elif opt in ('-g', '--gps'):
            gps_file = arg
        elif opt in ('-o', '--out'):
            output_file = arg
        elif opt in ('-t', '--tolerance'):
            tolerance = int(arg)
        elif opt in ('-f', '--filter'):
            filt = arg

    with open(aq_file, 'r') as a:
        with open(gps_file, 'r') as g:
            with open(output_file, 'wb') as o:"""
                #o.writelines("%s\n" % l for l in AqGpsJoiner(a, g, tolerance, filt))
