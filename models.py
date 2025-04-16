import time
from enum import Enum
import EVE_DAO.orm as db

class Galaxy(Enum):
    NEW_EDEN = 1
    ANOIKIS = 2
    ABYSSAL_SPACE = 3
    VOID_SPACE  = 4
    DEATHLESS_SPACE = 5
    JOVIAN_SPACE = 6
    POCHVEN_SPACE = 7

class Region:
    def __init__(self, pk: int, name: str):
        self.pk = pk
        self.name = name
    def __eq__(self, obj):
        if not isinstance(obj, Region): return False
        return (self.pk == obj.pk)
    def __repr__(self):
        return (f'{self.name} [{self.pk}]')

class Constellation:
    def __init__(self, pk: int, name: str, region: Region):
        self.pk = pk
        self.name = name
        self.region = region
    def __eq__(self, obj):
        if not isinstance(obj, Constellation): return False
        return (self.pk == obj.pk)
    def __repr__(self):
        return (f'{self.name} [{self.pk}] | '\
                f'{self.region.name} [{self.region.pk}]')

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
        return (f'{self.name} [{self.pk}] | '\
                f'{self.constellation.name} [{self.constellation.pk}] | '\
                f'{self.constellation.region.name} [{self.constellation.region.pk}]')

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
    if verbose:
        i = 1
        start_time = time.time()
    for system_dict in systems_dict:
        if verbose:
            print(f' Building systems objects: {i}/{len(systems_dict)}', end='\r')
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
    if verbose:
        exectime = round(time.time() - start_time, 2)
        print('                                                                             ', end='\r')
        print(f'Building systems objects: {i-1}/{len(systems_dict)}\texec time: {exectime}s')
    return systems

def get_regions(galaxy: Galaxy) -> list[Region]:
    regions = []
    region_dicts = db.get_regions(galaxy.value)
    if len(region_dicts) == 0: return regions
    for region_dict in region_dicts:
        regions.append(Region(region_dict['pk'], region_dict['name']))
    return regions

class Category:
    def __init__(self, pk: int, name: str):
        self.pk = pk
        self.name = name
    def __eq__(self, obj):
        if not isinstance(obj, Category): return False
        return (self.pk == obj.pk)
    def __repr__(self):
        return (f'{self.group.category.name} [{self.group.category.pk}]')

class Group:
    def __init__(self, pk: int, name: str, category: Category):
        self.pk = pk
        self.name = name
        self.category = category
    def __eq__(self, obj):
        if not isinstance(obj, Group): return False
        return (self.pk == obj.pk)
    def __repr__(self):
        return (f'{self.group.name} [{self.group.pk}] | '\
                f'{self.group.category.name} [{self.group.category.pk}]')

class Item:
    def __init__(self, pk: int, name: str, description: str, group: Group):
        self.pk = pk
        self.name = name
        self.description = description
        self.group = group
    def __eq__(self, obj):
        if not isinstance(obj, Item): return False
        return (self.pk == obj.pk)
    def __repr__(self):
        return (f'{self.name} [{self.pk}] | '\
                f'{self.group.name} [{self.group.pk}] | '\
                f'{self.group.category.name} [{self.group.category.pk}]')

class ItemNotFoundError(Exception):
    pass

def get_item(search_item) -> Item:
    item: Item = None
    item_dict = db.get_item(search_item)
    if item_dict is None: raise ItemNotFoundError
    group_dict = item_dict['group']
    category_dict = group_dict['category']
    category = Category(category_dict['pk'], category_dict['name'])
    group = Group(group_dict['pk'], group_dict['name'], category)
    item = Item(item_dict['pk'], item_dict['name'],
                item_dict['description'], group)
    return item

def get_items_from_group(search_group) -> list[Item]:
    items: list[Item] = []
    item_dicts = db.get_items_from_group(search_group)
    if len(item_dicts) == 0: raise ItemNotFoundError
    for item_dict in item_dicts:
        group_dict = item_dict['group']
        category_dict = group_dict['category']
        category = Category(category_dict['pk'], category_dict['name'])
        group = Group(group_dict['pk'], group_dict['name'], category)
        item = Item(item_dict['pk'], item_dict['name'],
                    item_dict['description'], group)
        items.append(item)
    return items

def get_items_from_category(search_category) -> list[Item]:
    items: list[Item] = []
    item_dicts = db.get_items_from_category(search_category)
    if len(item_dicts) == 0: raise ItemNotFoundError
    for item_dict in item_dicts:
        group_dict = item_dict['group']
        category_dict = group_dict['category']
        category = Category(category_dict['pk'], category_dict['name'])
        group = Group(group_dict['pk'], group_dict['name'], category)
        item = Item(item_dict['pk'], item_dict['name'],
                    item_dict['description'], group)
        items.append(item)
    return items