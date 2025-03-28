import sqlite3
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
                system["pk"] = row[1]
                system["name"] = row[2]
                system["x"] = row[3]
                system["y"] = row[4]
                system["z"] = row[5]
                system["security"] = row[6]
                pk_constellation = row[0]
                system["constellation"] = get_constellation(pk_constellation)
                system["stargates"] = get_stargates(system["pk"])
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
            system["pk"] = db_entry[1]
            system["name"] = db_entry[2]
            system["x"] = db_entry[3]
            system["y"] = db_entry[4]
            system["z"] = db_entry[5]
            system["security"] = db_entry[6]
            pk_constellation = db_entry[0]
            system["constellation"] = get_constellation(pk_constellation)
            system["stargates"] = get_stargates(system["pk"])
    return system

def get_constellation(pk: int) -> dict:
    constellation = {}
    with closing(sqlite3.connect(str(path_db))) as connection:
        with closing(connection.cursor()) as cursor:
            query = 'SELECT constellations.name, constellations.region_id '\
                    'FROM constellations WHERE constellations.constellation_id = ?'
            rows = cursor.execute(query, (pk,)).fetchall()
            db_entry = rows[0]
            constellation["pk"] = pk
            constellation["name"] = db_entry[0]
            region_pk = db_entry[1]
            constellation["region"] = get_region(region_pk)
    return constellation

def get_region(pk: int) -> dict:
    region = {}
    with closing(sqlite3.connect(str(path_db))) as connection:
        with closing(connection.cursor()) as cursor:
            query = 'SELECT regions.name FROM regions WHERE regions.region_id = ?'
            rows = cursor.execute(query, (pk,)).fetchall()
            db_entry = rows[0]
            region["pk"] = pk
            region["name"] = db_entry[0]
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

def get_systems() -> list[dict]:
    systems = []

    return systems