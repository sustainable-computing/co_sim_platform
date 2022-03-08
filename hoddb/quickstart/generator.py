from rdflib import Graph
import re 
import SmartGrid

node_buses = {}

g = Graph()
g.parse('SmartGrid.ttl')

def get_nodes(entity, key):
    try:
        nodes = '.' + entity[key].strip().replace(' ', '.').replace('_','.').replace('-','.')
    except:
        return None
    return nodes

def get_bus(entity, key):
    """
    This will return the bus number (bus_num) from the format Bus_<bus_num>_#_#_#_#...
    """
    bus = None
    try:
        bus = entity[key].split('#')[1].split('_')[1] 
    except:
        return None
    return bus

def parse_load_name(load):
    """
    This will parse the individual name to the object's name for the load
    """
    if bool(re.match('load_', load, re.I)):
        return load[5:].replace('_','.')
    return load.replace('_','.')

def parse_load(load):
    dss_load = "New Load."
    dss_load += parse_load_name(load['load'].split("#")[1]) + ' '
    dss_load += f"Bus1={get_bus(load,'bus')}"
    primary_nodes = get_nodes(load, 'n_prim')
    if primary_nodes != None:
        dss_load += primary_nodes + ' '
    else:
        dss_load += ' '
    dss_load += f"Phases={load['num_phases']} "
    dss_load += f"Conn={load['conn'] } "
    dss_load += f"Model={load['model']} "
    dss_load += f"kW={load['kW']} "
    dss_load += f"kvar={load['kvar']}"

    return dss_load

def parse_cap_name(load):
    """
    This will parse the individual name to the object's name for the cap
    """
    if bool(re.match('capacitor_', load, re.I)):
        return load[5:].replace('_','.')
    return load.replace('_','.')

def parse_capacitors(cap):
    dss_cap = "New Capacitor."
    dss_cap += parse_cap_name(cap['cap'].split('#')[1]) + ' '
    dss_cap += f"Bus1={get_bus(cap, 'prim_bus')} "
    primary_nodes = get_nodes(cap, 'prim_bus')
    dss_cap += f"phases={cap['num_phases']} "
    dss_cap += f"kVAR={cap['kvar']} "
    # Add voltage
    return dss_cap

def query_transformers():
    query_str = """
SELECT *
WHERE {
    ?trans a :Transformer .
    ?trans :primaryAttachsTo ?prim_bus .
    ?trans :attachsTo ?sec_bus .
    ?trans :Kva ?Kva .
    ?trans :connection_primary ?conn_prim .
    ?trans :connection_secondary ?conn_sec .
    ?trans :kV_primary ?kv_prim .
    ?trans :kV_secondary ?kv_sec .
    ?trans :percent_R ?percent_R .
    OPTIONAL {
        ?trans :XHL ?xhl .
        ?trans :XHT ?xht .
        ?trans :XLT ?xlt .
    }
}
    """
    res = g.query(query_str)

    for row in res:
        trans = SmartGrid.Transformer(
            trans = row['trans'],
            bus_primary = row['prim_bus'],
            kva = row['Kva'],
            connection_primary = row['conn_prim'],
            connection_secondary = row['conn_sec'],
            kv_primary = row['kv_prim'],
            kv_secondary = row['kv_sec'],
            percent_r = row['percent_R']
        )
        print(trans)
def query_capacitors():
    query_str = """
SELECT *
WHERE {
    ?cap a :Capacitor .
    ?cap :attachsTo ?bus .
    ?cap :kvar ?kvar .
    ?cap :nodes_primary ?prim_bus .
    ?cap :num_phases ?num_phases .
}    
"""

def query_buses():
    query_str = """
SELECT *
WHERE {
    ?bus a :Bus .
    ?bus :locatedAt ?loc .
    ?loc :coord_x ?x .
    ?loc :coord_y ?y .
}    
"""
    res = g.query(query_str)
    
    for row in res: 
        node = {
            'x': int(row['x']),
            'y': int(row['y']),
        }
        node_buses[row['bus'].split('#')[1]] = node
        bus = SmartGrid.Bus(
            bus = row['bus'],
            x = int(row['x']), 
            y = int(row['y']) 
        )
        print(bus)

def query_lines():
    query_str = """
SELECT *
WHERE {
    ?line a :Line .
    ?line :attachsTo ?bus1 .
    ?line :attachsTo ?bus2 .
    ?line :length ?length .
    ?line :nodes_primary ?n_prim .
    ?line :nodes_secondary ?n_sec .
    ?line :num_phases ?num_phases .
    ?line :unit ?unit .
}
"""
    res = g.query(query_str)
    print(len(res))
    for row in res:
        line = SmartGrid.Line(
            line = row['line'],
            length = row['length'],
            length_unit = row['unit'],
            nodes_primary = row['n_prim'],
            nodes_secondary = row['n_sec'],
            num_phases = row['num_phases']
        )
        print(line)
        print(row['bus1'], row['bus2'])

def query_loads():
    # Write the query
    query_str = """
SELECT *
WHERE {
    ?load a :Load .
    ?load :attachsTo ?bus .
    ?load :connection_primary ?conn .
    ?load :kW ?kW .
    ?load :kvar ?kvar .
    ?load :model ?model .
    ?load :nodes_primary ?n_prim .
    ?load :num_phases ?num_phases
}
"""
    # Get the query
    res = g.query(query_str)

    for row in res:
        print(parse_load(row))

# query_transformers()
# query_loads()
# query_buses()
query_lines()
# print(node_buses)