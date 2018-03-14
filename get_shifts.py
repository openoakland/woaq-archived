import csv
import yaml
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
mkpath('yml_template')

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
        fieldnames=['utc', 'filter', 'pm', 'lat', 'lon', 'device']

        for shift in shifts:
            # get the readings that just correspond to this shift
            sql = """
                select utc, filter, pm, lat, lon, device
                from pmgpsinnerview
                where device=%s
                and utc >= %s
                and utc <= %s
                """
            cursor.execute(sql, (shift['device'], shift['utcstart'], shift['utcend']))
            filters = set()

            # output one CSV per shift
            with open('shifts/{}.csv'.format(shift['name']), 'w') as outfile:
                writer = csv.DictWriter(
                    outfile,
                    fieldnames=fieldnames)
                writer.writeheader()
                for row in cursor.fetchall():
                    filters.add(str(row["filter"]))
                    writer.writerow(row)

            with open("yml_template/{}.yml".format(shift['name']), 'w') as outfile:
                data = {
                    "start_time": shift['utcstart'],
                    "end_time": shift['utcend'],
                    "device": shift['device'],
                    "filter": list(filters)
                }
                yaml.dump(data, outfile, default_flow_style=False)

finally:
    connection.close()

