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
    dss_load += load['load'].split("#")[1].split('_')[1]
    dss_load += f"Bus={load['bus'].split('#')[1].split('_')[1]}"
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

def query_generator():
    query_str = """
SELECT *
WHERE {
    ?gen a :Generator .
    ?gen :primaryAttachsTo ?bus1 .
    ?gen :MVAsc1 ?MVAsc1 .
    ?gen :MVAsc3 ?MVAsc3 .
    ?gen :angle ?angle .
    ?gen :kV_secondary ?kv_sec .
    ?gen :num_phases ?num_phases
}    
"""
    res = g.query(query_str)
    for row in res:
        gen = SmartGrid.Generator(
            gen = row['gen'],
            bus1 = row['bus1'],
            kv_sec = row['kv_sec'],
            num_phases = row['num_phases'],
            MVAsc1 = row['MVAsc1'],
            MVAsc3 = row['MVAsc3'],
            angle = row['angle']
        )   
        print(gen.get_opendss())
        # There should only be one generator
        break


def query_transformers():
    query_str = """
SELECT *
WHERE {
    ?trans a :Transformer .
    ?trans :primaryAttachsTo ?prim_bus .
    ?trans :attachsTo ?sec_bus .
    ?trans :num_phases ?num_phases .
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
            num_phases = row['num_phases'],
            bus_primary = row['prim_bus'],
            bus_secondary = row['sec_bus'],
            kva = row['Kva'],
            connection_primary = row['conn_prim'],
            connection_secondary = row['conn_sec'],
            kv_primary = row['kv_prim'],
            kv_secondary = row['kv_sec'],
            percent_r = row['percent_R']
        )
        print(trans.get_opendss())

def query_capacitors():
    query_str = """
SELECT *
WHERE {
    ?cap a :Capacitor .
    ?cap :attachsTo ?bus .
    ?cap :kV_primary ?kv .
    ?cap :kvar ?kvar .
    ?cap :num_phases ?num_phases .
    ?cap :kvar ?kvar .
    OPTIONAL {
        ?cap :nodes_primary ?prim_bus .
    }
}    
"""
    res = g.query(query_str)
    for row in res:
        cap = SmartGrid.Capacitor(
            cap = row['cap'],
            bus = row['bus'],
            kv = row['kv'],
            nodes_primary = row['prim_bus'],
            num_phases = row['num_phases'],
            kvar = row['kvar']
        )
        print(cap.get_opendss())

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

def query_lines():
    # Because the orientation of the bus connection does not matter 
    query_str = """
SELECT *
WHERE {
    ?line a :Line .
    ?line :primaryAttachsTo ?bus1 .
    ?line :attachsTo ?bus2 .
    ?line :hasComponent ?linecode .
    ?line :length ?length .
    ?line :nodes_primary ?n_prim .
    ?line :nodes_secondary ?n_sec .
    ?line :num_phases ?num_phases .
    ?line :unit ?unit .
}
"""
    res = g.query(query_str)
    for row in res:
        line = SmartGrid.Line(
            line = row['line'],
            bus1 = row['bus1'],
            bus2 = row['bus2'],
            linecode = row['linecode'],
            length = row['length'],
            length_unit = row['unit'],
            nodes_primary = row['n_prim'],
            nodes_secondary = row['n_sec'],
            num_phases = row['num_phases']
        )
        print(line.get_opendss())

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

def query_linecode():
    query_str = """
SELECT *
WHERE {
    ?linecode a :LineCode .
    ?linecode :freq ?freq .
    ?linecode :num_phases ?num_phases .
    ?linecode :rmat ?rmat .
    ?linecode :xmat ?xmat .
    ?linecode :unit ?unit .
    OPTIONAL {
        ?linecode :cmat ?cmat .
    }
}    
"""
    res = g.query(query_str)

    for row in res:
        linecode = SmartGrid.LineCode(
            linecode = row['linecode'],
            freq = row['freq'],
            num_phases = row['num_phases'],
            rmat = row['rmat'],
            xmat = row['xmat'],
            unit = row['unit'],
            cmat = row['cmat'] if 'cmat' in row else None
        )
        print(linecode.get_opendss())

def query_switches():
    query_str = """
SELECT *
WHERE {
    ?switch a :Switch .
    ?switch :primaryAttachsTo ?bus1 .
    ?switch :attachsTo ?bus2 .
    ?switch :num_phases ?num_phases .
    ?switch :c0 ?c0 .
    ?switch :c1 ?c1 .
    ?switch :r0 ?r0 .
    ?switch :r1 ?r1 .
    ?switch :x0 ?x0 .
    ?switch :x1 ?x1 .
}    
"""
    res = g.query(query_str)
    for row in res:
        switch = SmartGrid.Switch(
            switch = row['switch'],
            bus1 = row['bus1'],
            bus2 = row['bus2'],
            num_phases = row['num_phases'],
            c0 = row['c0'],
            c1 = row['c1'],
            r0 = row['r0'],
            r1 = row['r1'],
            x0 = row['x0'],
            x1 = row['x1']
        )
        print(switch.get_opendss())

def query_regcontrol():
    query_str = """
SELECT *
WHERE {
    ?reg a :RegControl .
    ?reg :primaryAttachsTo ?bus1 .
    ?reg :attachsTo ?bus2 .
    ?reg :Kva ?kva .
    ?reg :R ?R .
    ?reg :X ?X.
    ?reg :XHL ?XHL .
    ?reg :band ?band .
    ?reg :bank ?bank . 
    ?reg :ctprim ?ctprim .
    ?reg :kV_primary ?kv_prim .
    ?reg :kV_secondary ?kv_sec .
    ?reg :max_tap ?max_tap .
    ?reg :min_tap ?min_tap .
    ?reg :nodes_primary ?nodes_primary .
    ?reg :nodes_secondary ?nodes_secondary .
    ?reg :num_phases ?num_phases .
    ?reg :num_taps ?num_taps .
    ?reg :percent_Load_Loss ?percent_load_loss .
    ?reg :ptratio ?ptratio .
    ?reg :vreg ?vreg .
}    
"""
    res = g.query(query_str)
    for row in res:
        reg_control = SmartGrid.VoltageRegulator(
            regcontrol = row['reg'],
            bus1 = row['bus1'],
            bus2 = row['bus2'],
            num_phases = row['num_phases'],
            bank = row['bank'],
            XHL = row['XHL'],
            kva = row['kva'],
            primary_kv = row['kv_prim'],
            nodes_primary = row['nodes_primary'],
            secondary_kv = row['kv_sec'],
            nodes_secondary = row['nodes_secondary'],
            num_taps = row['num_taps'],
            max_tap = row['max_tap'], 
            min_tap = row['min_tap'],
            load_loss = row['percent_load_loss'],
            vreg = row['vreg'],
            band = row['band'],
            ptratio = row['ptratio'],
            ctprim = row['ctprim'],
            R = row['R'],
            X = row['X']
        )
        print(reg_control.get_opendss())



def post_object_opendss():
    """
    This will write code post object definition
    """
    query_str = """ 
SELECT DISTINCT ?kv
WHERE {
    ?trans a :Transformer . 
    {
        ?trans :kV_primary ?kv.

    }
    UNION 
    {
        ?trans :kV_secondary ?kv    
    }
}
"""
    res = g.query(query_str)
    voltages = []
    for row in res:
        voltages.append(float(row['kv']))

    opendss_str = f"Set VoltageBases={voltages}\n"
    opendss_str += "calcv\nSolve"
    return opendss_str


query_buses()
query_generator()
query_transformers()
query_regcontrol()
query_linecode()
query_loads()
query_capacitors()
query_lines()
query_switches()
print(post_object_opendss())