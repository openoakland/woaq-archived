import unittest
from files.joiner import AqGpsJoiner


class TestAqGpsJoiner(unittest.TestCase):
    def test_join(self):
        aq = ['Test Start Time,11:59:58 PM',
              'Test Start Date,07/18/2017',  # 07/18/2017 11:59:58 PM Pacific = 07/19/2017 06:59:58 AM UTC (1500447599)
              'Other,',
              '',
              'Elapsed Time [s],Mass [mg/m3],Alarms,Errors',
              '1,0.001,,',
              '2,0.002,,',
              '3,0.003,,',
              '4,0.004,,',
              '5,0.005,,',
              '6,0.006,,',
              '7,0.007,,',
              '8,0.008,,',
              '9,0.009,,',
              '10,0.010,,BAD']

        # GPRMC sentence: '$GPRMC,time,status,lat,lat_dir,lon,lon_dir,speed,track_angle,date,magnetic_var,checksum'
        gps = ['$GPRMC,065957.00,A,0900.000,N,1900.000,W,1.52,155.39,190717,,,',
               '$GPRMC,065958.00,A,1000.000,N,2000.000,W,1.52,155.39,190717,,,',
               '$GPRMC,065959.00,A,1100.000,N,2100.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070000.00,A,1200.000,N,2200.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070001.00,A,1300.000,N,2300.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070002.00,A,1400.000,N,2400.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070003.00,A,1500.000,N,2500.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070004.00,V,1600.000,N,2600.000,W,1.52,155.39,190717,,,',  # Skip due to invalidity
               '$GPGGA,070005.00,1700.000,N,2700.000,W,1,04,2.4,7.8,M,-25.1,M,,',  # Skip due to absent datestamp
               '$ZYXWV,070006.00,A,1800.000,N,2800.000,W,1.52,155.39,190717,,,',  # Skip due to unknown sentence type
               '$GPRMC,070007.00,A,1900.000,N,2900.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070008.00,A,2000.000,N,3000.000,W,1.52,155.39,190717,,,']

        joiner = AqGpsJoiner(aq, gps, tdiff_tolerance_secs=1, filter_size='10')

        self.assertEqual(joiner.next(), 'utc,filter,pm,lat,lon,device')
        self.assertEqual(joiner.next(), '1500447599,10,0.001,11.000000,-21.000000,A')
        self.assertEqual(joiner.next(), '1500447600,10,0.002,12.000000,-22.000000,A')
        self.assertEqual(joiner.next(), '1500447601,10,0.003,13.000000,-23.000000,A')
        self.assertEqual(joiner.next(), '1500447602,10,0.004,14.000000,-24.000000,A')
        self.assertEqual(joiner.next(), '1500447603,10,0.005,15.000000,-25.000000,A')
        self.assertEqual(joiner.next(), '1500447604,10,0.006,15.000000,-25.000000,A')  # GPS absent, use previous GPS
        # Row skipped because neither previous GPS nor next GPS are within tolerance
        self.assertEqual(joiner.next(), '1500447606,10,0.008,19.000000,-29.000000,A')  # GPS absent, use next GPS
        self.assertEqual(joiner.next(), '1500447607,10,0.009,19.000000,-29.000000,A')
        self.assertEqual(joiner.next(), '1500447608,10,0.010,20.000000,-30.000000,BAD')
        self.assertRaises(StopIteration, joiner.next)


if __name__ == '__main__':
    unittest.main()
