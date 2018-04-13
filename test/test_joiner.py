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
              '3,0.003,,']

        gps = ['$GPRMC,065957.00,A,0999.000,N,1999.000,W,1.52,155.39,190717,,,',
               '$GPRMC,065958.00,A,1000.000,N,2000.000,W,1.52,155.39,190717,,,',
               '$GPRMC,065959.00,A,1001.000,N,2001.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070000.00,A,1002.000,N,2002.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070001.00,A,1003.000,N,2003.000,W,1.52,155.39,190717,,,',
               '$GPRMC,070002.00,A,1004.000,N,2004.000,W,1.52,155.39,190717,,,']

        joiner = AqGpsJoiner(aq, gps)

        self.assertEqual(joiner.next(), 'timestamp,mass,latitude,longitude')
        self.assertEqual(joiner.next(), '07/18/2017 11:59:59 PM PDT,0.001,1001.000,2001.000')
        self.assertEqual(joiner.next(), '07/19/2017 12:00:00 AM PDT,0.002,1002.000,2002.000')
        self.assertEqual(joiner.next(), '07/19/2017 12:00:01 AM PDT,0.003,1003.000,2003.000')
        self.assertRaises(StopIteration, joiner.next)


if __name__ == '__main__':
    unittest.main()
