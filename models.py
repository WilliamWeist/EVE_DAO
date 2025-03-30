from enum import Enum
import EVE_DAO.orm as db

class Region:
    def __init__(self, pk: int, name: str):
        self.pk = pk
        self.name = name
    def __eq__(self, obj):
        if not isinstance(obj, Region): return False
        return (self.pk == obj.pk)
    def __repr__(self):
        return (f'{self.constellation.region.name}[{self.constellation.region.pk}]')

class Constellation:
    def __init__(self, pk: int, name: str, region: Region):
        self.pk = pk
        self.name = name
        self.region = region
    def __eq__(self, obj):
        if not isinstance(obj, Constellation): return False
        return (self.pk == obj.pk)
    def __repr__(self):
        return (f'{self.constellation.name}[{self.constellation.pk}] | '\
                f'{self.constellation.region.name}[{self.constellation.region.pk}]')

class System:
    def __init__(self, pk: int, name: str, constellation: Constellation, 
                 coord_x: float, coord_y: float, coord_z: float, 
                 security: float, stargates: list[int]):
        self.pk = pk
        self.name = name
        self.constellation = constellation
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.coord_z = coord_z
        self.security = security
        self.stargates = stargates
    def __eq__(self, obj):
        if not isinstance(obj, System): return False
        return (self.pk == obj.pk)
    def __repr__(self):
        return (f'{self.name}[{self.pk}] | '\
                f'{self.constellation.name}[{self.constellation.pk}] | '\
                f'{self.constellation.region.name}[{self.constellation.region.pk}]')

class Galaxy(Enum):
    NEW_EDEN = 1
    ANOIKIS = 2
    ABYSSAL_SPACE = 3
    VOID_SPACE  = 4
    DEATHLESS_SPACE = 5
    JOVIAN_SPACE = 6
    POCHVEN_SPACE = 7

class SystemNameError(Exception):
    pass

def search_system(name: str) -> list[System]:
    systems_dict = db.search_system(name)
    systems = []
    if systems_dict is None:
        raise SystemNameError
    for system_dict in systems_dict:
        constellation_dict = system_dict["constellation"]
        region_dict = constellation_dict["region"]
        region = Region(region_dict["pk"],
                        region_dict["name"])
        constellation = Constellation(constellation_dict["pk"],
                                    constellation_dict["name"],
                                    region)
        system = System(system_dict["pk"],
                        system_dict["name"],
                        constellation,
                        system_dict["x"],
                        system_dict["y"],
                        system_dict["z"],
                        system_dict["security"],
                        system_dict["stargates"])
        systems.append(system)
    return systems

def get_systems(galaxy: Galaxy, verbose: bool = False) -> list[System]:
    systems = []
    systems_dict = db.get_systems(galaxy.value, verbose=verbose)
    i = 1
    for system_dict in systems_dict:
        if verbose:
            print(f' Building objects: {i}/{len(systems_dict)}', end='\r')
            i += 1
        constellation_dict = system_dict['constellation']
        region_dict = constellation_dict['region']
        region = Region(region_dict['region_id'],
                        region_dict['name'])
        constellation = Constellation(constellation_dict['constellation_id'],
                                      constellation_dict['name'],
                                      region)
        system = System(system_dict['system_id'],
                        system_dict['name'],
                        constellation,
                        system_dict['x'],
                        system_dict['y'],
                        system_dict['z'],
                        system_dict['security'],
                        system_dict['stargates'])
        systems.append(system)
    if verbose: print('')
    return systems
