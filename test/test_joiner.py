import unittest
from files.joiner import AqGpsJoiner


class TestAqGpsJoiner(unittest.TestCase):
    def test_join(self):
        aq = ['Test Start Time,11:59:58 PM',
              'Test Start Date,07/18/2017',
              'Errors,',
              '',
              'Elapsed Time [s],Mass [mg/m3],Alarms,Errors',
              '1,0.001,,',
              '2,0.002,,',
              '3,0.003,,',
              '4,0.004,,BAD']

        gps = ['$GPRMC,065957.00,A,0900.000,N,1900.000,W,1.52,155.39,190717,,,',
               '$GPRMC,065958.00,A,1000.000,N,2000.000,W,1.52,155.39,190717,,,',
               '$GPRMC,065959.00,A,1100.000,N,2100.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070000.00,A,1200.000,N,2200.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070001.00,E,1300.000,N,2300.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070002.00,A,1400.000,N,2400.000,W,1.52,155.39,190717,,,']

        joiner = AqGpsJoiner(aq, gps)

        self.assertEqual(joiner.next(), 'utc,filter,pm,lat,lon,device')
        self.assertEqual(joiner.next(), '1500447599,,0.001,11.0,-21.0,A')
        self.assertEqual(joiner.next(), '1500447600,,0.002,12.0,-22.0,A')
        self.assertEqual(joiner.next(), '1500447601,,0.003,13.0,-23.0,E')
        self.assertEqual(joiner.next(), '1500447602,,0.004,14.0,-24.0,E')
        self.assertRaises(StopIteration, joiner.next)


if __name__ == '__main__':
    unittest.main()
