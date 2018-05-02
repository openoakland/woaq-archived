`pm.mysql` drops and re-creates all of the the database tables and views.

`pmload.mysql` loads the tables from the dump files.


To download everything, run

```
curl -L http://secure-web.cisco.com/1SOJrTG5gCruIHqvn9NInzNUzgeqcmipc24MaNMtt_lHUghxqbS1AM74xmJBKbWk9l2sUqg7VcpeBmmcn4t8Rj5wo5FWwgrvhmFnkq76nYGcuHuAln-HuoVX67fJBlBoSNJg-QYaFbFJPMAosrg9XdvXpmJhfpRpxeRuqjFlHZa_p1eWV2x7sb2ktYVztRDdckNb6NPh_TOQPJKObX-9oefwoVc_v_kmoUbZh-LR-8qRPZDoXhpTMLBsJ7CAzH96obUh5lSRmgfhBXUv3w26OT7IyyfAdvc2hAKKRHEeIxaUj5vVGyeAMMg0M7FBvqEAXDB7XLosYBNI_fcTV1tfTDjhgy6ltBUpSv1Quvd-IcgSHIogp0cFrisFBaaCj8dpxUnHa8dndqHfUyyhLFH9CnOmSutWPe6zJC7Ci85NiZtg68rJV28OWbNiDWZ549O9lED857JYS6Sg5w0eGljoC3A/http%3A%2F%2Fwww.paulaoki.com%2Ftmp%2F130614-woeipload.tgz | tar -xvz
```

## Splitting data into shifts

This data was collected in a series of surveyor shifts in which a surveyor collected readings with a particular Dusttrak device with a particular filter equipped. You can query the DB for this, but we also have a Python script called `get_shifts.py` that will split the data into one flat file per shift.


### Dependencies

- python 2.7.x (probably works with 3.x but not tested)
- pymysql (install via `pip`)
- a running MySQL server, with the data from above loaded into a database called `woiep`, listening on default port 3306. (the docker-compose file in this repo will get you started toward that)

### Generating the files

Simply run `python get_shifts.py`. It will create a directory called "shifts" and then save a bunch of CSV files in it.

The name of each CSV file designates the device name (A, B, etc) and the expected range of readings, for reference. Columns include timestamp, lat/long, the filter size used on this shift, and PM (particulate matter) reading.

Orphaned PM and GPS data is *not* included. That is, only readings that contain both PM and lat/long will be present in these files.

### Joining Air Quality Data with GPS Data

The files/joiner.py script can be used to join air quality data with GPS data. The air quality data should be a CSV, as produced by a DustTrak II device. (See examples/8530C_2-5_002.csv) The GPS data should be a log file containing NMEA sentences. (See examples/GPS_20140717_193858_8530C.log)

The output of the script will be a CSV file containing both GPS and air quality data. (See examples/joiner-output.csv)

The script can be run as `files/joiner.py --aq <air-quality-file.csv> --gps <gps-file.log> --out <output.csv> --tolerance 1 --filter 2.5`

The command line options are as follows:

- `-a`/`--aq` : the path to the CSV file containing air quality data
- `-g`/`--gps` : the path to the log file containing GPS data
- `-o`/`--out` : the path to where the output file will be created
- `-t`/`--tolerance` : this parameter is the maximum difference (in seconds) between an air quality datum and a GPS datum for the two data to be joined. In other words, if there is an air quality datum at 12:00:00, but the closest GPS datum is at 12:00:02, then the output will include a row combining those two data if the value of -t is >= 2, otherwise that air quality datum will be dropped.
- `-f`/`--filter` : this is the size of the filter used to collect the air quality data. (2.5 is most common, 10 may also be used.) Often this is embedded in the filename. E.g., for 8530C_2-5_002.csv, the filter size was 2.5.

