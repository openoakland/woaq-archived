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


```bash
docker-compose up

#creates a directory called 'shifts' and writes CSVs to it
python scripts/get_shifts.py
```


The name of each CSV file designates the device name (A, B, etc) and the expected range of readings, for reference. Columns include timestamp, lat/long, the filter size used on this shift, and PM (particulate matter) reading.

Orphaned PM and GPS data is *not* included. That is, only readings that contain both PM and lat/long will be present in these files.



```bash
# merges shifts from the same month into the shift_by_month directory
scripts/get_shift_by_month.sh

# Generates markdown pages for jekyll. Writes them to _posts
scripts/make_markdown.sh
```

