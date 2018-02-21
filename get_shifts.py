import csv
from distutils.dir_util import mkpath

import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='woiep',
                             cursorclass=pymysql.cursors.DictCursor)

# create the output directory
mkpath('shifts')

try:
    shifts = []
    with connection.cursor() as cursor:
        # shifts have start/end timestamps that correspond
        # to discrete collection shifts with a specific device.
        # we need those to grab matching readings from another table
        sql = "select * from shift"
        cursor.execute(sql)
        for shift in cursor.fetchall():
            shifts.append(shift)

        # we want filter size and reading along with time/geo
        fieldnames=['utc', 'filter', 'pm', 'lat', 'lon',]

        for shift in shifts:
            # get the readings that just correspond to this shift
            sql = """
                select utc, filter, pm, lat, lon
                from pmgpsinnerview
                where device=%s
                and utc >= %s
                and utc <= %s
                """
            cursor.execute(sql, (shift['device'], shift['utcstart'], shift['utcend']))

            # output one CSV per shift
            with open('shifts/{}.csv'.format(shift['name']), 'w') as outfile:
                writer = csv.DictWriter(
                    outfile, 
                    fieldnames=fieldnames)
                writer.writeheader()
                for row in cursor.fetchall():
                    writer.writerow(row)

finally:
    connection.close()

