import csv
import yaml
from distutils.dir_util import mkpath

from datetime import datetime
import pymysql.cursors

import getopt

def get_shifts(csv_dir, yml_dir):

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='password',
                                 db='woiep',
                                 cursorclass=pymysql.cursors.DictCursor)

    # create the output directory
    mkpath(csv_dir)
    mkpath(yml_dir)

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

            d = datetime.now()

            for shift in shifts:
                shift["name"] = shift["name"].replace(" ", "_").replace(",", "_")
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
                with open('{}/{}.csv'.format(csv_dir, shift['name']), 'w') as outfile:
                    writer = csv.DictWriter(
                        outfile,
                        fieldnames=fieldnames)
                    writer.writeheader()
                    for row in cursor.fetchall():
                        filters.add(str(row["filter"]))
                        writer.writerow(row)

                with open("{}/{}.yml".format(yml_dir, shift['name']), 'w') as outfile:
                    data = {
                        "layout": "post",
                        "title": shift['name'],
                        "category": "citizen science",
                        "date": d.strftime("%Y-%m-%d %H:%M:%S"),
                        "start_time": shift['utcstart'],
                        "end_time": shift['utcend'],
                        "device": shift['device'],
                        "filter": list(filters)
                    }
                    yaml.dump(data, outfile, default_flow_style=False)
    finally:
        connection.close()

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hc:y:', ['help', 'csv=', 'yml='])

except getopt.GetoptError:
    print 'scripts/get_shifts.py -csv <csv_output_path> -yml <yml_output_path>'
    sys.exit(2)

for opt, args in opts:
    if opt in ('-h', '--h'):
        print 'scripts/get_shifts.py -csv <csv_output_path> -yml <yml_output_path>'
        sys.exit()
    elif opt in ('-c', '-csv'):
        csv_output = arg
    elif opt in ('-y', '-yml'):
        yml_output = arg

get_shifts(csv_output, yml_output)

