# EDIFICE database README

The Edifice database is an attempt to create a data model for an entire city, based on open data. It currently lives in a PostgreSQL 9.2 database with the PostGIS 2.0.1 extension. This README assumes intermediate to advanced knowledge of SQL and is intended to get you up an running and poking around the data to see if anything interesting turns up. It is not intended to be an exhaustive guide on relational databases, SQL, or geospatial information systems. I highly recommend (nay, insist) the reader to go through the excellent [Introduction to PostGIS workshop](http://workshops.opengeo.org/postgis-intro) from OpenGeo first before exploring the Edifice database. Some additional resources:

- [PostgreSQL official documentation](http://www.postgresql.org/docs/9.2/static/index.html)
- [PostGIS official documentation](http://www.postgis.org/documentation/manual-2.0/)
- [Postgres guide](http://www.postgresguide.com)
- [PostgreSQL: Up and Running](http://shop.oreilly.com/product/0636920025061.do)
- [PostGIS In Action](http://www.manning.com/obe)

## Connecting to the database

## Schema

The Edifice schemas are broad, general civic categories. They are effectively directories for tables and can be viewed in psql with

    \dn

All tables in a given schema can be viewed with

    \dt schema.

(notice the trailing .)

By default, only the public schema is in the database search path. If you want to reference a table in a schema not in the search path, you must include its schema, such as

    SELECT * FROM schema.table;

If you have the proper privileges, you can change the database search path with

    ALTER DATABASE database SET search_path TO schema1,schema2,schema3;

You will have to quit with `\q` and re-connect for the changes to take effect.

## Tables

Where data lives.

    \d table

describes the table, showing its schema, column names and data types, indices, constraints, and foreign-key relationships. 

## Querying

Tables can be queried with the SELECT statement. To SELECT all rows from a table, use

    SELECT * FROM table;

Usually, though, you'll want to only select some a few columns. For example, the business licenses table has 33 columns, but you may only want the name and address. In that case, you'd use:

    SELECT dba_name, address FROM business_licenses;

You can further filter your results with the WHERE clause. Say you want the name and address of every business that has a "Late Hour" license:

    SELECT dba_name, address FROM business_licenses WHERE license_desc = 'Late Hour';

## Spatial Queries

Writing spatial queries is the heart of PostGIS. Have a look at the [PostGIS Reference](http://www.postgis.org/documentation/manual-2.0/reference.html) to get a sense of just what you can do with a spatial database. For example, in a standard database loaded with data from the [American Community Survey](http://www.census.gov/acs), we can find the number of households in Chicago headed by a single mother with an own child under the age of 6:

    SELECT sum(related_own_child_under_6) FROM demographics.census_blocks_families_single_mother;
    sum
    -------
    15555
    (1 row)

With a spatial database, we can find the number of those households within a half-mile of a [WIC Office](http://www.cityofchicago.org/city/en/depts/cdph/provdrs/clinic/svcs/apply_for_wic.html):

    SELECT sum(b.related_own_child_under_6) FROM demographics.census_blocks_families_single_mother b JOIN census_blocks c USING(gid) JOIN buildings u ON ST_DWithin(u.the_geom, c.the_geom, 2640) JOIN wic_offices w USING (bldg_gid);
    sum
    -------
    1829
    (1 row)

Phew. Let's step through this.

    SELECT sum(b.related_own_child_under_6) FROM demographics.census_blocks_families_single_mother b

We SELECT a sum of households headed by single mothers with a related own child under 6 FROM the census_blocks_families_single_mother table in the demographics schema. `related_own_child_under_6` is a column in that table. We alias the table to `b`, mostly for our own sanity so that we don't have to type out that verbose table name again. We could have done this with AS (`SELECT sum(b.related_own_child_under_6) FROM demographics.census_blocks_families_single_mother AS b`) but the AS is not required.

    JOIN census_blocks c USING(gid)

Our first JOIN. The ACS data has no geospatial component to it, only a unique gid that we can then join to its corresponding geography data table (census_blocks) in the boundaries schema. The `USING(gid)` is a shortcut for `JOIN census_blocks c ON c.gid = b.gid`. We are telling the database to join this ACS data to this geographic data if their gids match. We again alias the table to a single character

    JOIN buildings u ON ST_DWithin(u.the_geom, c.the_geom, 2640)

Our first spatial join. Get used to writing stuff like this, because everything in Edifice revolves around buildings. Here we are saying to JOIN (in essence, give me only) these buildings that are a half-mile (2640 feet, the units of the geometry's projected coordinate system, beyond the scope of this README) of those census blocks. The ST_DWithin function is a PostGIS function that takes two geometries and a distance and returns TRUE if the second geometry given is within the distance of the first geometry given. If the query stopped here, it would likely give us the same result as our first, non-spatial query of just summing all the households because almost all census blocks are within a half-mile of at least one building. So, we need to...

    JOIN wic_offices w USING(bldg_gid)

Here is another feature of Edifice. Anything that can be somehow related to a building, is. In this case, the `wic_offices` table has a foreign key bldg_gid field that references the buildings table. We are telling the database to only factor a building in to its calculation if that building has a WIC office in it.

To summarize, our query could be read as "Give me a sum of households headed by a single mother with a related child under the age of 6 using this ACS data joined with this Census block geographic data if it is within a half-mile of a building with a WIC Office in it."

## SCHEMA/TABLE REFERENCE

### boundaries

#### census_block_groups
* gid: unique primary key
* geoid10: FIPS code
* the_geom: geometry

#### census_blocks
* gid: unique primary key
* geoid10: FIPS code
* the_geom: geometry

#### census_tracts
* gid: unique primary key
* geoid10: FIPS code
* the_geom: geometry

#### central_business_district
* gid: unique primary key
* the_geom: geometry

#### comm_areas
Official [Community Areas](http://www.encyclopedia.chicagohistory.org/pages/1760.html) of the City of Chicago
* gid1: unique primary key
* area_num: community area number
* community: community area name
* the_geom: geometry

#### congress
U.S. House of Representatives legislative districts in Chicago
* gid: unique primary key
* name: representative name
* district: Illinois district number
* the_geom: geometry

#### conservation_areas
[Conservation Areas](http://www.encyclopedia.chicagohistory.org/pages/329.html)
* gid: unique primary key
* name:
* ref: reference string
* status: whether the conservation area is still active
* date: designation date
* the_geom: geometry

#### empowerment_zones
(http://en.wikipedia.org/wiki/Empowerment_zone)
* gid: unique primary key
* name:
* the_geom: geometry

#### enterprise community
* gid: unique primary key
* name:
* the_geom: geometry

#### enterprise zone
(http://en.wikipedia.org/wiki/Urban_Enterprise_Zone)
* gid: unique primary key
* name:
* the_geom: geometry

#### industrial_corridors
* gid: unique primary key
* no: number
* name:
* region:
* miles: length in miles
* the_geom: geometry

#### neighborhoods
* gid: unique primary key
* pri_neigh: primary neighborhood name
* sec_neigh: secondary neighborhood name (often used for the containing neighborhood in the case of "landlocked" neighborhoods like Palmer Square, Wrigleyville, etc.
* the_geom: geometry

#### new_wards
New wards that will take in effect in 2015
* gid: unique primary key
* ward:
* the_geom: geometry

#### planning_districts
* gid: unique primary key
* district:
* name:
* the_geom: geometry

#### planning_regions
* gid: unique primary key
* district:
* name:
* the_geom: geometry

#### police_districts
* gid: unique primary key
* dist_label: district label
* dist_num: district number
* the_geom: geometry

#### precincts
voting precincts
* gid: unique primary key
* ward:
* precinct:
* the_geom: geometry

#### special_service_areas
(http://www.cityofchicago.org/city/en/depts/dcd/supp_info/special_service_areassaprogram.html)
* gid: unique primary key
* ref_no
* name:
* status:

#### sweeping
street sweeping grid
* gid: unique primary key
* sweep: sweep number
* month_4: days of the month sweeping will occur (continues to month_11)
* the_geom: geometry

#### wards
current wards
* gid: unique primary key
* ward:
* alderman:
* ward_phone:
* hall_phone:
* hall_offic:
* address:
* the_geom: geometry
* bldg_gid: foreign key references buildings

#### winterovernightparkingrestrictions
* gid: unique primary key
* on_street: the street on which overnight winter parking is restricted
* from_stree: the from cross street
* to_street: the to cross street
* the_geom: geometry

#### zip_codes
* gid: unique primary key
* zip: zip code
* the_geom: geometry

#### zoning_aug2012
* gid: unique primary key
* zone_type:
* zone_class:
* pd_prefix
* ordinance_: reference to city ordinance relating to this zoning
* ordinance1: the date the ordinance was ratified

### Business

#### business_licenses
* id: unique primary key
* account_num:
* site_num:
* legal_name
* dba_name:
* address:
* license_desc:
* bldg_gid: foreign key references buildings
* floor: 
* suite:


### CTA

#### bus_stops
* gid: unique primary key
* systemstop: CTA internal reference
* street:
* cross_st: cross street
* dir: the bus heading at this particular stop
* pos: unknown
* routesstpg: other routes that stop here
* owlroutes: owl (late night) routes that stop here

#### cta_bus_stops_routes
Many-to-many junction table for bus_stops and bus_routes

#### cta_rail_stations_lines
Many-to-many junction table for rail_lines and rail_stations

#### cta_rail_lines_iso
#### rail_lines_prejct

These are broken, ignore these for now

### Demographics

#### births_and_birth_rates
* ca_num: community area number
* ca: community area
* lower_ci and upper_ci: lower and upper confidence intervals


