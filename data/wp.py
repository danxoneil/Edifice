import os
import psycopg2
import json

class AutoVivification(dict):
	""" Implementation of Perl's Autovivification feature.
	Shamelessly stolen from http://stackoverflow.com/questions/651794/whats-the-best-way-to-initialize-a-dict-of-dicts-in-python """
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value

conn = psycopg2.connect(dbname='chicago')
cur = conn.cursor()
buildings = AutoVivification()

hood = 'Lincoln Park'


cur.execute("SELECT b.bldg_gid, trim(b.est_value), trim(b.lotsize), trim(d.description) FROM county_temp b JOIN assessed.propclass d USING (property_class) JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['bldgData']['estimatedValue'] = i[1]
		buildings[i[0]]['bldgData']['lotsize'] = i[2]
		buildings[i[0]]['bldgData']['propertyDescription'] = i[3]

cur.execute("SELECT b.bldg_gid, b.address FROM full_address b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))
if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['bldgData']['address'] = i[1]

cur.execute("SELECT b.bldg_gid, b.sqft::int FROM sqft b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['bldgData']['sqft'] = i[1]

cur.execute("SELECT b.bldg_gid, b.stories FROM stories b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['bldgData']['stories'] = i[1]

cur.execute("SELECT b.bldg_gid, b.year_built FROM year_built b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['bldgData']['yearBuilt'] = i[1]


cur.execute("SELECT b.bldg_gid FROM multiple_addresses b JOIN full_address a USING(bldg_gid) JOIN address_list c USING(bldg_gid) JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE a.address != c.address AND y.pri_neigh = %s", (hood,))	

# This should work...
# Also rather inelegant
if cur.rowcount > 0:
	ma_ids = [x[0] for x in cur.fetchall()]
	
	for i in ma_ids:
		cur.execute("SELECT c.address FROM address_list c JOIN full_address a USING(bldg_gid) WHERE a.address != c.address AND c.bldg_gid = %s", (i,))
		buildings[i]['bldgData']['alternateAddresses'] = [z[0] for z in cur.fetchall()]


# Just need the unit number from the address field
cur.execute("SELECT b.bldg_gid, trim(b.unit), trim(b.mkt_val_2012) FROM assessed.condos_temp b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['residential']['condominium']['unit'] = i[1]
		buildings[i[0]]['residential']['condominium']['marketValue'] = i[2]
	# Cross-check with buildings.sqft once we have more PINs - have every reason to believe county is more accurate/up-to-date
cur.execute("SELECT b.bldg_gid, trim(b.bldg_units), trim(b.bldg_sqft) FROM assessed.apts_temp b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['residential']['largeApartmentBldg']['units'] = i[1]
		buildings[i[0]]['residential']['largeApartmentBldg']['sqft'] = i[2]

cur.execute("SELECT b.bldg_gid, trim(b.mkt_val_2012), trim(b.res_apts), trim(b.ext_const), trim(b.full_bath), trim(b.half_bath), trim(b.basement), trim(b.attic), trim(b.central_air), trim(b.fireplace), trim(b.garage) FROM assessed.res202_temp b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE trim(b.res_use) = 'Multi Family' AND y.pri_neigh = %s", (hood,))	
if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['residential']['smallApartmentBldg']['marketValue'] = i[1]
		buildings[i[0]]['residential']['smallApartmentBldg']['units'] = i[2]
		buildings[i[0]]['residential']['smallApartmentBldg']['extConstruction'] = i[3]
		buildings[i[0]]['residential']['smallApartmentBldg']['fullBaths'] = i[4]
		buildings[i[0]]['residential']['smallApartmentBldg']['halfBaths'] = i[5]
		buildings[i[0]]['residential']['smallApartmentBldg']['basement'] = i[6]
		buildings[i[0]]['residential']['smallApartmentBldg']['attic'] = i[7]
		buildings[i[0]]['residential']['smallApartmentBldg']['centralAir'] = i[8]
		buildings[i[0]]['residential']['smallApartmentBldg']['fireplace'] = i[9]
		buildings[i[0]]['residential']['smallApartmentBldg']['garage'] = i[10]
		
cur.execute("SELECT b.bldg_gid, trim(b.mkt_val_2012), trim(b.ext_const), trim(b.full_bath), trim(b.half_bath), trim(b.basement), trim(b.attic), trim(b.central_air), trim(b.fireplace), trim(b.garage) FROM assessed.res202_temp b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE trim(b.res_use) = 'Single Family' AND y.pri_neigh = %s", (hood,))

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['residential']['singleFamilyHouse']['marketValue'] = i[1]
		buildings[i[0]]['residential']['singleFamilyHouse']['extConstruction'] = i[2]
		buildings[i[0]]['residential']['singleFamilyHouse']['fullBaths'] = i[3]
		buildings[i[0]]['residential']['singleFamilyHouse']['halfBaths'] = i[4]
		buildings[i[0]]['residential']['singleFamilyHouse']['basement'] = i[5]
		buildings[i[0]]['residential']['singleFamilyHouse']['attic'] = i[6]
		buildings[i[0]]['residential']['singleFamilyHouse']['centralAir'] = i[7]
		buildings[i[0]]['residential']['singleFamilyHouse']['fireplace'] = i[8]
		buildings[i[0]]['residential']['singleFamilyHouse']['garage'] = i[9]

cur.execute("SELECT b.bldg_gid, b.name, b.hours, b.phone FROM community_centers b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['civic']['communityCenter']['name'] = i[1]
		buildings[i[0]]['civic']['communityCenter']['hours'] = i[2]
		#TODO: parse out hours for "Open Now" feature
		buildings[i[0]]['civic']['communityCenter']['phone'] = i[3]
cur.execute("SELECT b.bldg_gid, b.anno_name, b.factype FROM cook_co_facilities_in_chicago b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['civic']['cookCountyFacility']['name'] = i[1]
		buildings[i[0]]['civic']['cookCountyFacility']['facilityType'] = i[2]
cur.execute("SELECT b.bldg_gid, b.name, b.architect, b.status_date FROM landmarks b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['civic']['landmark']['name'] = i[1]
		buildings[i[0]]['civic']['landmark']['architect'] = i[2]
		buildings[i[0]]['civic']['landmark']['designationDate'] = i[3]
cur.execute("SELECT b.bldg_gid, b.name || ' Library', b.hours, b.cybernavigator, b.teacher_in_library FROm libraries_locations_hours b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['civic']['library']['name'] = i[1]
		buildings[i[0]]['civic']['library']['hours'] = i[2]
		buildings[i[0]]['civic']['library']['cybernavigator'] = i[3]
		buildings[i[0]]['civic']['library']['teacherInLibrary'] = i[4]
cur.execute("SELECT b.bldg_gid, b.facility || ' ' || b.type, b.phone, b.website, b.hours, b.appt, b.internet, b.wifi, b.training FROM public_tech_resources b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE b.type IN ('Community Technology Center', 'City Colleges of Chicago', 'Wireless Internet Zone') AND y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['civic']['publicTechResource']['name'] = i[1]
		buildings[i[0]]['civic']['publicTechResource']['phone'] = i[2]
		buildings[i[0]]['civic']['publicTechResource']['website'] = i[3]
		buildings[i[0]]['civic']['publicTechResource']['hours'] = i[4]
		buildings[i[0]]['civic']['publicTechResource']['appointmentRequired'] = i[5]
		buildings[i[0]]['civic']['publicTechResource']['internet'] = i[6]
		buildings[i[0]]['civic']['publicTechResource']['wifi'] = i[7]
		buildings[i[0]]['civic']['publicTechResource']['training'] = i[8]
cur.execute("SELECT b.bldg_gid, b.full_name, b.hours, b.phone FROM senior_centers b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))		
if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['civic']['seniorCenter']['name'] = i[1]
		buildings[i[0]]['civic']['seniorCenter']['hours'] = i[2]
		buildings[i[0]]['civic']['seniorCenter']['phone'] = i[3]
cur.execute("SELECT b.bldg_gid, b.name, b.hours, b.phone FROM workforce_centers b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	
if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['civic']['workforceCenter']['name'] = i[1]
		buildings[i[0]]['civic']['workforceCenter']['hours'] = i[2]
		buildings[i[0]]['civic']['workforceCenter']['phone'] = i[3]
cur.execute("SELECT b.bldg_gid, b.agency_name || ' ' || b.project || ' Youth Center', b.phone, b.fax FROM youth_centers b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	
if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['civic']['youthCenter']['name'] = i[1]
		buildings[i[0]]['civic']['youthCenter']['phone'] = i[2]
		buildings[i[0]]['civic']['youthCenter']['fax'] = i[3]

cur.execute("SELECT b.bldg_gid, b.name, b.grades_served FROM private_schools b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))
if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['education']['privateSchool']['name'] = i[1]
		buildings[i[0]]['education']['privateSchool']['gradesServed'] = i[2]


cur.execute("SELECT b.bldg_gid, b.name, b.grades_served FROM public_schools b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))
if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['education']['publicSchool']['name'] = i[1]
		buildings[i[0]]['education']['publicSchool']['gradesServed'] = i[2]

cur.execute("SELECT b.bldg_gid, b.name, b.phone FROM ewaste_collection_sites b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['environment']['eWasteCollection']['name'] = i[1]
		buildings[i[0]]['environment']['eWasteCollection']['phone'] = i[2]

cur.execute("SELECT b.bldg_gid, b.name, b.venue_type FROM condom_distribution_sites b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['health']['freeCondoms']['name'] = i[1]
		buildings[i[0]]['health']['freeCondoms']['venueType'] = i[2]
cur.execute("SELECT b.bldg_gid, b.facility, b.type2, b.parentorg FROM hospitals b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['health']['hospital']['name'] = i[1]
		buildings[i[0]]['health']['hospital']['affiliation'] = i[2]
		buildings[i[0]]['health']['hospital']['parentOrg'] = i[3]
cur.execute("SELECT b.bldg_gid, b.name, b.hours, b.phone FROM mental_health_clinics b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['health']['mentalHealthClinic']['name'] = i[1]
		buildings[i[0]]['health']['mentalHealthClinic']['hours'] = i[2]
		buildings[i[0]]['health']['mentalHealthClinic']['phone'] = i[3]
cur.execute("SELECT b.bldg_gid, b.name, b.hours, b.phone, b.website, b.adult, b.children, b.family_case_mgmt, b.immigration_physical, b.medication_assistance, b.pregnancy_testing, b.pregnant_women, b.refugee, b.women_seeking_birth_control FROM neighborhood_health_clinics b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['health']['neighborhoodHealthClinic']['name'] = i[1]
		buildings[i[0]]['health']['neighborhoodHealthClinic']['hours'] = i[2]
		buildings[i[0]]['health']['neighborhoodHealthClinic']['phone'] = i[3]
		buildings[i[0]]['health']['neighborhoodHealthClinic']['website'] = i[4]
		buildings[i[0]]['health']['neighborhoodHealthclinic']['services'] = {
				'adults': i[5],
				'children': i[6],
				'familyCaseManagement': i[7],
				'immigrationPhysical': i[8],
				'medicationAssistance': i[9],
				'pregnancyTesting': i[10],
				'pregnantWomen': i[11],
				'refugees': i[12],
				'womenSeekingBirthControl': i[13]
				}
	
	
			


cur.execute("SELECT b.bldg_gid, b.name, b.hours, b.phone, b.fax FROM sti_specialty_clinics b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['health']['stiSpecialtyClinic']['name'] = i[1]
		buildings[i[0]]['health']['stiSpecialtyClinic']['hours'] = i[2]
		buildings[i[0]]['health']['stiSpecialtyClinic']['phone'] = i[3]
		buildings[i[0]]['health']['stiSpecialtyClinic']['fax'] = i[4]
cur.execute("SELECT b.bldg_gid, b.name, b.hours, b.phone1, b.fax1 FROM wic_offices b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['health']['wicOffice']['name'] = i[1]
		buildings[i[0]]['health']['wicOffice']['hours'] = i[2]
		buildings[i[0]]['health']['wicOffice']['phone'] = i[3]
		buildings[i[0]]['health']['wicOffice']['fax'] = i[4]
cur.execute("SELECT b.bldg_gid, 'Chicago Fire Department - Engine ' || b.engine FROM fire_stations b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['safety']['fireStation']['name'] = i[1]

cur.execute("SELECT b.bldg_gid, CASE WHEN b.district = 'Headquarters' THEN 'Chicago Police Department - ' || b.district ELSE 'Chicago Police Department - ' || b.district || b.dist_suffix || ' District Station' END, b.phone, b.fax, b.tty, b.website FROM police_stations b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['safety']['policeStation']['name'] = i[1]
		buildings[i[0]]['safety']['policeStation']['phone'] = i[2]
		buildings[i[0]]['safety']['policeStation']['fax'] = i[3]
		buildings[i[0]]['safety']['policeStation']['tty'] = i[4]
		buildings[i[0]]['safety']['policeStation']['website'] = i[5]

cur.execute("SELECT b.bldg_gid, b.longname || ' Metra Station', b.lines, b.farezone FROM metra_stations b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE b.bldg_gid IS NOT NULL AND y.pri_neigh = %s", (hood,))		

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['transportation']['metra']['name'] = i[1]
		buildings[i[0]]['transportation']['metra']['lines'] = [x.strip() for x in list(i[2].split(','))]
		buildings[i[0]]['transportation']['metra']['farezone'] = i[3]
cur.execute("SELECT b.bldg_gid, b.name || ' CTA Rail Station', b.lines, b.ada, b.gtfs::int FROM rail_stations b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['transportation']['ctaRailStation']['name'] = i[1]
		buildings[i[0]]['transportation']['ctaRailStation']['lines'] = [x.strip() for x in list(i[2].split(','))]
		buildings[i[0]]['transportation']['ctaRailStation']['ada'] = i[3]
		buildings[i[0]]['transportation']['ctaRailStation']['gtfs'] = i[4]




# Businesses in buildings will have to be accessed by their business id
# (in this case a simple auto-incrementing integer in the database)
# due to a multitude of issues (duplicates, chain stores, multiple licenses
# for one business, etc.)
# though this is probably for the better now that we're associating
# twitter ids with building and business ids
cur.execute("SELECT b.bldg_gid, b.id, b.dba_name, b.license_desc, b.floor, b.suite FROM current_active b JOIN buildings u USING (bldg_gid) JOIN neighborhoods y ON ST_Intersects(y.the_geom, u.the_geom) WHERE y.pri_neigh = %s", (hood,))	

if cur.rowcount > 0:
	for i in cur:
		buildings[i[0]]['business'][i[1]] = { 
			i[2]: { #dba_name
					'licenseType': i[3],
					'floor': i[4],
					'suite': i[5]
				}
			}

f = open(hood.lower().replace(' ','_')+'_pretty.json', 'w')
json.dump(buildings, f, indent=4)
f.close()
cur.close()
conn.close()
