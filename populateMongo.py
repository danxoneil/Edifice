import psycopg2
from pymongo import Connection

conn = psycopg2.connect(dbname='chicago')
cur = conn.cursor()

c = Connection()
dbh = c.chicago

cur.execute("SELECT bldg_gid FROM buildings;")
for i in cur:
	dbh.buildings.insert({"_id": i[0]})

cur.execute("SELECT bldg_gid, address FROM full_address;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"bldgData": {"address": i[1]}}})

cur.execute("SELECT bldg_gid, sqft::int FROM sqft;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"bldgData.sqft": i[1]}})

cur.execute("SELECT * FROM stories;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"bldgData.stories": i[1]}})

cur.execute("SELECT * FROM year_built;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"bldgData.yearBuilt": i[1]}})

cur.execute("SELECT bldg_gid FROM multiple_addresses;")
ma_ids = [z[0] for z in cur.fetchall()]
for i in ma_ids:
	cur.execute("SELECT address FROM multiple_addresses WHERE bldg_gid = %s", (i,))
	dbh.buildings.update({"_id": i}, {"$set": {"bldgData.alternateAddresses": [z[0] for z in cur.fetchall()]}})

cur.execute("SELECT bldg_gid, name FROM buildings_bldg_name;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"bldgData.bldgName": i[1]}})

cur.execute("SELECT bldg_gid, name FROM cbd_bldg_names;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"bldgData.bldgName": i[1]}})

cur.execute("SELECT c.bldg_gid, d.shortdesc FROM county_temp c JOIN assessed.propclass d USING(property_class) WHERE c.property_class IS NOT NULL AND c.property_class != '' AND c.bldg_gid IS NOT NULL;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"bldgType": i[1]}})

cur.execute("SELECT bldg_gid, name, hours, phone FROM community_centers;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"civic": [{"type": 'Community Center', "properties": {"name": i[1], "hours": i[2], "phone": i[3]}}]}})

cur.execute("SELECT bldg_gid, name, hours, phone FROM senior_centers;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"civic": {"type": "Senior Center", "properties": {"name": i[1], "hours": i[2], "phone": i[3]}}}})

cur.execute("SELECT bldg_gid, name, hours, phone FROM workforce_centers;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"civic": {"type": "Workforce Center", "properties": {"name": i[1], "hours": i[2], "phone": i[3]}}}})

cur.execute("SELECT bldg_gid, agency_name, project, phone FROM youth_centers;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"civic": {"type": "Youth Center", "properties": {"name": i[1], "category": i[2], "phone": i[3]}}}})

cur.execute("SELECT bldg_gid, anno_name, factype FROM cook_co_facilities_in_chicago;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"civic": {"type": "Cook County Facility", "properties": {"name": i[1], "department": i[2]}}}})

cur.execute("SELECT bldg_gid, ward::int, alderman, ward_phone FROM wards;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"civic": {"type": "Ward Office", "properties": {"ward": i[1], "alderman": i[2], "phone": i[3]}}}})

cur.execute("SELECT bldg_gid, name, grades_served FROM private_schools;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"education": [{"type": "Private School", "properties": {"name": i[1], "gradesServed": i[2]}}]}})

cur.execute("SELECT bldg_gid, label, grades, cps_type, phone, type_, boundary FROM public_schools;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"education": {"type": "Public School", "properties": {"name": i[1], "gradesServed": [x.strip() for x in list(i[2].split(','))], "cpsType": i[3], "category": i[4], "attendanceBoundary": i[5]}}}})

cur.execute("SELECT bldg_gid, name, hours, cybernavigator, teacher_in_library FROM libraries_locations_hours;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"education": {"type": "Library", "properties": {"name": i[1], "hours": i[2], "cybernavigator": i[3], "teacherInLibrary": i[4]}}}})

cur.execute("SELECT bldg_gid, name, name2 FROM university_bldg_names;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"education": {"type": "University", "properties": {"university": i[2], "bldgName": i[1]}}}})


cur.execute("SELECT bldg_gid, name, phone FROM ewaste_collection_sites;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"environment": [{"type": "E-Waste Collection Site", "properties": {"name": i[1], "phone": i[2]}}]}})

cur.execute("SELECT bldg_gid, name, venue_type FROM condom_distribution_sites;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"health": [{"type": "Condom Distribution Site", "properties": {"name": i[1], "venueType": i[2]}}]}})

cur.execute("SELECT bldg_gid, facility, type2, parentorg FROM hospitals;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"health": {"type": "Hospital", "properties": {"name": i[1], "affiliation": i[2], "parentOrg": i[3]}}}})

cur.execute("SELECT bldg_gid, name, hours, phone FROM mental_health_clinics;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"health": {"type": "Mental Health Clinic", "properties": {"name": i[1], "hours": i[2], "phone": i[3]}}}})

cur.execute("SELECT bldg_gid, name, hours, phone, website, adult, children, family_case_mgmt, immigration_physical, medication_assistance, pregnancy_testing, pregnant_women, refugee, women_seeking_birth_control FROM neighborhood_health_clinics;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"health": {"type": "Neighborhood Health Clinic", "properties": {"name": i[1], "hours": i[2], "phone": i[3], "website": i[4], "servicesOffered": {"adult": i[5], "children": i[6], "familyCaseManagement": i[7], "immigrationPhysical": i[8], "medicationAssistance": i[9], "pregnancyTesting": i[10], "pregnatnWomen": i[11], "refugees": i[12], "womenSeekingBirthControl": i[13]}}}}})

cur.execute("SELECT bldg_gid, name, hours, phone FROM sti_specialty_clinics;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"health": {"type": "STI Specialty Clinic", "properties": {"name": i[1], "hours": i[2], "phone": i[3]}}}})

cur.execute("SELECT bldg_gid, name, hours, phone1 FROM wic_offices;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"health": {"type": "WIC Office", "properties": {"name": i[1], "hours": i[2], "phone": i[3]}}}})

cur.execute("SELECT bldg_gid, landmarkna, startyear, endyear, decade, yearnotes FROM history.historic_resources WHERE bldg_gid NOT IN ((SELECT bldg_gid FROM history.landmarks)) AND bldg_gid IS NOT NULL;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"history": [{"type": "Historic Resource", "properties": {"name": i[1], "startYear": i[2], "endYear": i[3], "decade": i[4], "yearNotes": i[5]}}]}})

cur.execute("SELECT bldg_gid, name, date_built, architect, designation_date::varchar FROM history.landmarks;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"history": {"type": "Landmark", "properties": {"name": i[1], "dateBuilt": i[2], "architect": i[3], "designationDate": i[4]}}}})

cur.execute("SELECT bldg_gid, engine FROM fire_stations;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"safety": [{"type": "Fire Station", "properties": {"engine": i[1]}}]}})

cur.execute("SELECT bldg_gid, district, phone, fax, tty, website, label FROM police_stations;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"safety": {"type": "Police Station", "properties": {"name": i[6], "district": i[1], "phone": i[2], "fax": i[3], "tty": i[4], "website": i[5]}}}})

#TODO: Incorporate crime data if crime happened in a building


cur.execute("SELECT bldg_gid, longname, lines, farezone FROM metra_stations WHERE bldg_gid IS NOT NULL;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$set": {"transportation": [{"type": "Metra Station", "properties": {"name": i[1], "lines": [x.strip() for x in list(i[2].split(','))], "farezone": i[3]}}]}})

cur.execute("SELECT bldg_gid, name, lines, ada, gtfs::int FROM rail_stations WHERE bldg_gid IS NOT NULL;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"transportation": {"type": "CTA Rail Station", "properties": {"name": i[1], "lines": [x.strip() for x in list(i[2].split(','))], "ada": i[3], "gtfs": i[4]}}}})

#TODO: Decide which other fields to include
cur.execute("SELECT DISTINCT bldg_gid, account_num, dba_name, floor, suite FROM business_licenses WHERE bldg_gid IS NOT NULL;")
bldata = cur.fetchall()
for i in bldata:
	cur.execute("SELECT DISTINCT license_desc FROM business_licenses WHERE bldg_gid = %s AND account_num = %s AND dba_name = %s", (i[0], i[1], i[2]))
	dbh.buildings.update({"_id": i[0]}, {"$push": {"business": {"properties": {"accountNum": i[1], "dbaName": i[2], "floor": i[3], "suite": i[4], "licenses": [z[0] for z in cur.fetchall()]}}}})

#Might need to have nested ilke above - type: permit, properties: {}
cur.execute("SELECT bldg_gid, permit_num, permit_type, issue_date::varchar, est_cost, work FROM building_permits WHERE bldg_gid IS NOT NULL;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"bldgPermits": {"type": i[2], "properties": {"permitNum": i[1], "issueDate": i[3], "estCost": i[4], "work": i[5]}}}})

cur.execute("SELECT bldg_gid, v_last_mod_date::varchar, v_date::varchar, v_status, v_status_date, v_desc, v_loc, v_insp_comments, insp_status, insp_cat, dept FROM building_violations WHERE bldg_gid IS NOT NULL;")
for i in cur:
	dbh.buildings.update({"_id": i[0]}, {"$push": {"violation": {"type": i[8], "properties": {"lastModDate": i[1], "date": i[2], "status": i[3], "statusDate": i[4], "description": i[5], "location": i[6], "inspectorComments": i[7], "inspectionCategory": i[9], "dept": i[10]}}}})
# Full version
#cur.execute("SELECT bldg_gid, id, v_last_mod_date, v_date, v_code, v_status, v_status_date, v_desc, v_loc, v_insp_comments, insp_id, insp_num, insp_status, insp_waived, insp_cat, dept, prop_group FROM building_violations WHERE bldg_gid IS NOT NULL;")
#for i in cur:
#	dbh.buildings.update({"_id": i[0]}, {"$push": {"violations": {"id": i[1], "lastModifiedDate": i[2], "date": i[3], "code": i[4], "status": i[5], "statusDate": i[6], "description": i[7], "location": i[8], "inspectorComments": i[9], "inspectorId": i[10], "inspectorNum": i[11], "inspectorStatus": i[12], "inspectorWaived": i[13], "inspectorCategory": i[14], "dept": i[15], "propertyGroup": i[16]}}})



cur.close()
conn.close()
c.close()
