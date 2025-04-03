import sqlite3, time
from pathlib import Path
from contextlib import closing

path_db = Path('EVE.db')

def search_system(str_input: str) -> list[dict]:
    str_input = str_input.lower() + '%'
    with closing(sqlite3.connect(str(path_db))) as connection:
        with closing(connection.cursor()) as cursor:
            query = 'SELECT * FROM systems '\
                    'WHERE LOWER(systems.name) like ? '\
                    'ORDER BY systems.name'
            rows = cursor.execute(query, (str_input,)).fetchall()
            if len(rows) == 0:
                return None
            systems = []
            for row in rows:
                system = {}
                system['pk'] = row[1]
                system['name'] = row[2]
                system['x'] = row[3]
                system['y'] = row[4]
                system['z'] = row[5]
                system['security'] = row[6]
                pk_constellation = row[0]
                system['constellation'] = get_constellation(pk_constellation)
                system['stargates'] = get_stargates(system['pk'])
                systems.append(system)
    return systems

def get_system(pk: int) -> dict:
    system = {}
    with closing(sqlite3.connect(str(path_db))) as connection:
        with closing(connection.cursor()) as cursor:
            query = 'SELECT * FROM systems ' \
                    'WHERE systems.system_id = ?'
            rows = cursor.execute(query, (pk,)).fetchall()
            db_entry = rows[0]
            system['pk'] = db_entry[1]
            system['name'] = db_entry[2]
            system['x'] = db_entry[3]
            system['y'] = db_entry[4]
            system['z'] = db_entry[5]
            system['security'] = db_entry[6]
            pk_constellation = db_entry[0]
            system['constellation'] = get_constellation(pk_constellation)
            system['stargates'] = get_stargates(system['pk'])
    return system

def get_constellation(pk: int) -> dict:
    constellation = {}
    with closing(sqlite3.connect(str(path_db))) as connection:
        with closing(connection.cursor()) as cursor:
            query = 'SELECT constellations.name, constellations.region_id '\
                    'FROM constellations WHERE constellations.constellation_id = ?'
            rows = cursor.execute(query, (pk,)).fetchall()
            db_entry = rows[0]
            constellation['pk'] = pk
            constellation['name'] = db_entry[0]
            region_pk = db_entry[1]
            constellation['region'] = get_region(region_pk)
    return constellation

def get_region(pk: int) -> dict:
    region = {}
    with closing(sqlite3.connect(str(path_db))) as connection:
        with closing(connection.cursor()) as cursor:
            query = 'SELECT regions.name FROM regions WHERE regions.region_id = ?'
            rows = cursor.execute(query, (pk,)).fetchall()
            db_entry = rows[0]
            region['pk'] = pk
            region['name'] = db_entry[0]
    return region

def get_stargates(pk: int) -> list[int]:
    stargates = []
    with closing(sqlite3.connect(str(path_db))) as connection:
        with closing(connection.cursor()) as cursor:
            query ='SELECT stargates.to_system_id FROM stargates WHERE stargates.from_system_id = ?'
            rows = cursor.execute(query, (pk,)).fetchall()
            for row in rows:
                stargates.append(row[0])
    return stargates

def get_systems(galaxy_pk: int, verbose: bool = False) -> list[dict]:
    systems = []
    with closing(sqlite3.connect(str(path_db))) as connection:
        with closing(connection.cursor()) as cursor:
            query = 'SELECT ' \
                        'regions.region_id, ' \
                        'regions.name, ' \
                        'constellations.constellation_id, ' \
                        'constellations.name, ' \
                        'systems.system_id, ' \
                        'systems.name, ' \
                        'systems.x, ' \
                        'systems.y, ' \
                        'systems.z, ' \
                        'systems.security ' \
                    'FROM systems ' \
                    'INNER JOIN constellations ON systems.constellation_id = constellations.constellation_id ' \
                    'INNER JOIN regions ON constellations.region_id = regions.region_id ' \
                    'WHERE regions.galaxy_id = ?'
            rows = cursor.execute(query, (galaxy_pk, )).fetchall()
            if verbose:
                i = 1
                start_time = time.time()
            for row in rows:
                if verbose:
                    print(f' Loading data: {i}/{len(rows)}', end='\r')
                    i += 1
                region = {}
                region['region_id'] = row[0]
                region['name'] = row[1]
                constellation = {}
                constellation['constellation_id'] = row[2]
                constellation['name'] = row[3]
                constellation['region'] = region
                system = {}
                system['system_id'] = row[4]
                system['name'] = row[5]
                system['x'] = row[6]
                system['y'] = row[7]
                system['z'] = row[8]
                system['security'] = row[9]
                system['stargates'] = get_stargates(system['system_id'])
                system['constellation'] = constellation
                systems.append(system)
            if verbose:
                exectime = round(time.time() - start_time, 2)
                print('                                                                             ', end='\r')
                print(f'Loading data: {i-1}/{len(rows)}\texec time: {exectime}s')
    return systems