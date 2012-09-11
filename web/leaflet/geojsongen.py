import psycopg2

conn = psycopg2.connect(dbname='chicago')
cur = conn.cursor()

f = open('wp_4326_buildings.json', 'w')
f.write('{"type": "FeatureCollection", "features":[')

cur.execute("SELECT b.bldg_gid, ST_AsGeoJSON(ST_Transform(b.geom_rotated_scaled,4326)) FROM buildings b JOIN neighborhoods n ON ST_Intersects(n.the_geom, b.the_geom) WHERE n.pri_neigh = 'Wicker Park';")
rows = cur.fetchall()
for i, data in enumerate(rows):
	if i == len(rows) - 1:
		f.write('{"type": "Feature", "geometry":' +data[1]+', "properties": {"bldg_gid": "'+str(data[0])+'"}}]}')
	else:
		f.write('{"type": "Feature", "geometry":' +data[1]+', "properties": {"bldg_gid": "'+str(data[0])+'"}},')

f.close()
f = open('wp_4326_walls.json', 'w')
f.write('{"type": "FeatureCollection", "features":[')

cur.execute("SELECT b.bldg_gid, ST_AsGeoJSON(ST_Transform(b.wall,4326)) FROM walls b JOIN buildings u USING(bldg_gid) JOIN neighborhoods n ON ST_Intersects(n.the_geom, u.the_geom) WHERE n.pri_neigh = 'Wicker Park';")
rows = cur.fetchall()
for i, data in enumerate(rows):
	if i == len(rows) - 1:
		f.write('{"type": "Feature", "geometry":' +data[1]+', "properties": {"bldg_gid": "'+str(data[0])+'"}}]}')
	else:
		f.write('{"type": "Feature", "geometry":' +data[1]+', "properties": {"bldg_gid": "'+str(data[0])+'"}},')

f.close()
f = open('wp_4326_streets.json', 'w')
f.write('{"type": "FeatureCollection", "features":[')

cur.execute("SELECT b.gid, ST_AsGeoJSON(ST_Transform(b.geom_rotated_scaled,4326)) FROM wicker_park.streets b;")
rows = cur.fetchall()
for i, data in enumerate(rows):
	if i == len(rows) - 1:
		f.write('{"type": "Feature", "geometry":' +data[1]+', "properties": {"gid": "'+str(data[0])+'"}}]}')
	else:
		f.write('{"type": "Feature", "geometry":' +data[1]+', "properties": {"gid": "'+str(data[0])+'"}},')

f.close()
f = open('wp_4326_curbs.json', 'w')
f.write('{"type": "FeatureCollection", "features":[')

cur.execute("SELECT b.gid, ST_AsGeoJSON(ST_Transform(b.geom_rotated_scaled,4326)) FROM curbs b JOIN neighborhoods n ON ST_Intersects(n.the_geom, b.the_geom) WHERE n.pri_neigh = 'Wicker Park';")
rows = cur.fetchall()
for i, data in enumerate(rows):
	if i == len(rows) - 1:
		f.write('{"type": "Feature", "geometry":' +data[1]+', "properties": {"gid": "'+str(data[0])+'"}}]}')
	else:
		f.write('{"type": "Feature", "geometry":' +data[1]+', "properties": {"gid": "'+str(data[0])+'"}},')

f.close()
cur.close()
conn.close()
