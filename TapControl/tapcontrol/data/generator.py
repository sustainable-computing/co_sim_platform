from collections import deque
from rdflib import Graph
import re 
import SmartGrid
import argparse
import json
import csv

g = Graph()

parser = argparse.ArgumentParser(description = "Convert turtle files to OpenDSS")
parser.add_argument('--freq', default=60, type=int, help="The frequency of the grid")
parser.add_argument('--outfile', default="outfile.dss", help="The filename of the OpenDSS file")
parser.add_argument('--infile', default="SmartGrid.ttl", help="The filename of the ontology to convert")
parser.add_argument('--nodes_file', default="gen_nodes.json", help="The filename of the nodes json file to be used by the network sim")
parser.add_argument('--device_file', default="gen_devices.csv", help="The filename of the device file to be used by the network sim")
parser.add_argument('--error', default=0.00001667, help="The error margin")
parser.add_argument('--period', default=20, help="The period time for the sensor")


buses = {}
# Get the child of the bus
buses_child = {}
# Get the parent of the bus
buses_parent = {}
lines = {}
loads = {}
capacitors = {}
linecode = {}
transformers = {}
regcontrols = {}
generator = None

def query_generator():
    global generator
    query_str = """
SELECT *
WHERE {
    ?gen a :Generator .
    ?gen :primaryAttachsTo ?bus1 .
    ?gen :MVAsc1 ?MVAsc1 .
    ?gen :MVAsc3 ?MVAsc3 .
    ?gen :pu ?pu .
    ?gen :angle ?angle .
    ?gen :kV_secondary ?kv_sec .
    ?gen :num_phases ?num_phases
}    
"""
    res = g.query(query_str)

    opendss = "!--- Genereted circuit\n"
    for row in res:
        gen = SmartGrid.Generator(
            gen = row['gen'],
            bus1 = row['bus1'],
            kv_sec = row['kv_sec'],
            pu = row['pu'],
            num_phases = row['num_phases'],
            MVAsc1 = row['MVAsc1'],
            MVAsc3 = row['MVAsc3'],
            angle = row['angle']
        )   
        opendss += gen.get_opendss()
        generator = gen
        # There should only be one generator
        break
    opendss += '\n\n'
    return opendss

def query_transformers():
    query_str = """
SELECT *
WHERE {
    ?trans a :Transformer .
    ?trans :primaryAttachsTo ?prim_bus .
    ?trans :attachsTo ?sec_bus .
    ?trans :num_phases ?num_phases .
    ?trans :Kva ?Kva .
    ?trans :XHL ?xhl .
    ?trans :connection_primary ?conn_prim .
    ?trans :connection_secondary ?conn_sec .
    ?trans :kV_primary ?kv_prim .
    ?trans :kV_secondary ?kv_sec .
    ?trans :percent_R ?percent_R .
    OPTIONAL {
        ?trans :XHT ?xht .
        ?trans :XLT ?xlt .
    }
}
    """
    res = g.query(query_str)

    opendss = "!--- Generated Transformers\n"

    for row in res:
        trans = SmartGrid.Transformer(
            trans = row['trans'],
            num_phases = row['num_phases'],
            bus_primary = row['prim_bus'],
            bus_secondary = row['sec_bus'],
            kva = row['Kva'],
            XHL= row['xhl'],
            XHT = row['xht'],
            XLT = row['xlt'],
            connection_primary = row['conn_prim'],
            connection_secondary = row['conn_sec'],
            kv_primary = row['kv_prim'],
            kv_secondary = row['kv_sec'],
            percent_r = row['percent_R']
        )
        opendss += trans.get_opendss() + '\n'
    opendss += '\n\n'
    return opendss 

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
    opendss = "!--- Generated Capacitors\n"
    for row in res:
        cap = SmartGrid.Capacitor(
            cap = row['cap'],
            bus = row['bus'],
            kv = row['kv'],
            nodes_primary = row['prim_bus'],
            num_phases = row['num_phases'],
            kvar = row['kvar']
        )
        opendss += cap.get_opendss() + '\n'
    opendss += '\n\n'
    return opendss 

def query_buses():
    """
    Get all the buses from the power grid
    """
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
            'connections': set()
        }
        buses[row['bus'].split('#')[1].split('_')[1]] = node
        buses_child[row['bus'].split('#')[1].split('_')[1]] = set()
        buses_parent[row['bus'].split('#')[1].split('_')[1]] = set()

def query_double_buses():
    """
    This will get all electrical equipment that is connected to two buses
    """
    query_str = """
SELECT *
WHERE {
    ?entity rdf:type ?type .
    ?type rdfs:subClassOf* :Electrical_Equipment .
    ?entity :primaryAttachsTo ?bus1 .
    ?entity :attachsTo ?bus2 .
} 
"""
    res = g.query(query_str)
    for row in res:
        bus_in = row['bus1'].split('#')[1].split('_')[1]
        bus_out = row['bus2'].split('#')[1].split('_')[1]
        buses[bus_in]['connections'].add(bus_out)
        buses[bus_out]['connections'].add(bus_in)
        buses_child[bus_in].add(bus_out)
        buses_parent[bus_out].add(bus_in)


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
    opendss = "!--- Generated Lines\n"
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
        opendss += line.get_opendss() + '\n'
    opendss += '\n\n'
    return opendss

def query_loads():
    # Write the query
    query_str = """
SELECT *
WHERE {
    ?load a :Load .
    ?load :attachsTo ?bus1 .
    ?load :connection_primary ?conn .
    ?load :kV_primary ?kv_prim .
    ?load :kW ?kW .
    ?load :kvar ?kvar .
    ?load :model ?model .
    ?load :nodes_primary ?n_prim .
    ?load :num_phases ?num_phases . 
    OPTIONAL {
        ?load :nodes_secondary ?n_sec .
    }
}
"""
    # Get the query
    res = g.query(query_str)
    opendss = "!--- Generated Loads\n"
    for row in res:
        load = SmartGrid.Load(
            load = row['load'],
            bus1 = row['bus1'],
            conn = row['conn'],
            kv_primary = row['kv_prim'],
            kw = row['kW'],
            kvar = row['kvar'],
            model = row['model'],
            nodes_primary = row['n_prim'],
            nodes_secondary = row['n_sec'],
            num_phases = row['num_phases']
        )
        opendss += load.get_opendss() + '\n'
    opendss += '\n\n'

    return opendss

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
    opendss = "!--- Generated Linecodes\n"
    for row in res:
        linecode = SmartGrid.LineCode(
            linecode = row['linecode'],
            freq = row['freq'],
            num_phases = row['num_phases'],
            rmat = row['rmat'],
            xmat = row['xmat'],
            unit = row['unit'],
            cmat = row['cmat']
        )
        opendss += linecode.get_opendss() + '\n'
    opendss += '\n\n'
    return opendss

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
    opendss = "!--- Generated Switches\n"
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
        opendss += switch.get_opendss() +'\n'
    opendss += '\n\n'
    return opendss

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
    ?reg :tap_primary ?tap_prim .
    ?reg :tap_secondary ?tap_sec .
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
    opendss = "!--- Generated Reg Control\n"
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
            tap_primary = row['tap_prim'],
            secondary_kv = row['kv_sec'],
            nodes_secondary = row['nodes_secondary'],
            tap_secondary = row['tap_sec'],
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
        opendss += reg_control.get_opendss() + '\n'
        regcontrols[str(reg_control)] = reg_control
    opendss += '\n\n'
    return opendss

def query_actuators():
    query_str = """
SELECT *
WHERE {
    ?act rdf:type ?type .
    ?type rdfs:subClassOf* :Actuator .
    ?act :connectsTo ?conn_to .
    ?act :controls ?controls .
    ?act :isFedBy ?fedby .
    ?act :phase ?phase .
    ?act :bus_terminal ?bus .
    ?controls :primaryAttachsTo ?bus1 .
    ?fedby :connectsTo ?endpoint .
    ?endpoint :locatedAt ?src .
    OPTIONAL {
        ?controls :attachsTo ?bus2 .
    }
}    
"""
    res = g.query(query_str)
    actuators = []
    for row in res:
        if '1' in row['bus'] and row['bus1'] is not None:
            dst = row['bus1']
        elif '2' in row['bus'] and row['bus2'] is not None:
            dst = row['bus2']
        else:
            dst = row['bus1']
        act = SmartGrid.Actuator(
            actuator = row['act'],
            dst = dst,
            src = row['src'],
            controls = row['controls'],
            controller = row['fedby'],
            phase = row['phase'],
            bus = row['bus']
        )
        actuators.append(act)
    
    return actuators


def query_sensors():
    query_str = """
SELECT *
WHERE {
    ?sen rdf:type ?type .
    ?type rdfs:subClassOf* :Sensor .
    ?sen :connectsTo ?conn_to .
    ?sen :feeds ?feeds .
    ?sen :measures ?measures . 
    ?sen :monitor ?monitor .
    ?monitor :primaryAttachsTo ?bus1 .
    ?sen :rate ?rate .
    ?sen :phase ?phase .
    ?sen :bus_terminal ?bus .
    ?feeds :connectsTo ?endpoint .
    ?endpoint :locatedAt ?dst .
    OPTIONAL {
        ?monitor :attachsTo ?bus2 .
    }
}    
"""
    res = g.query(query_str)
    sensors = []
    for row in res:
        if '1' in row['bus'] and row['bus1'] is not None:
            src = row['bus1']
        elif '2' in row['bus'] and row['bus2'] is not None:
            src = row['bus2']
        else:
            src = row['bus1']

        sensor = SmartGrid.Sensor(
            sensor = row['sen'],
            connects_to = row['conn_to'],
            controller = row['feeds'],
            measures = row['measures'],
            monitor = row['monitor'],
            src = src,
            rate = row['rate'],
            dst = row['dst'],
            phase = row['phase'],
            bus = row['bus']
        )
        sensors.append(sensor)
    
    return sensors

def query_controllers():
    """
    This will return the list of controllers in the graph    
    """
    query_str = """
SELECT *
WHERE {
    ?entity rdf:type ?type .
    ?type rdfs:subClassOf* :Controller .
}    
"""
    res = g.query(query_str)
    controllers = []
    for row in res:
        control = SmartGrid.Controller(
            control = row['entity']
        )
        controllers.append(control)
    
    return controllers

def pre_object_opendss(freq = 60):
    """
    This will write code pre-object definition 
    """
    opendss_str = f"Clear \nSet DefaultBaseFrequency={freq} \n\n"
    return opendss_str

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

    opendss_str = f"Set VoltageBases={voltages} \n"
    opendss_str += "calcv \nSolve \n"
    return opendss_str

def set_taps():
    openstr = ""
    for reg, obj in regcontrols.items():
        openstr += f"Transformer.{reg}.Taps=[1 1] \n"

    return openstr

def query_neighbours(origin, dist = 0):
    """
    This will get all electrical equipment that is attached to a bus
    """
    results = []
    results_dist = []
    # include the start bus
    bus_to_search = [origin]
    entity_dist = {
        origin: 0
    }
    while True:
        if len(bus_to_search) == 0:
            break
        bus = bus_to_search.pop(0)
        query_str = """
        SELECT DISTINCT *
        WHERE {
            ?entity rdf:type ?type .
            ?type rdfs:subClassOf* :Electrical_Equipment .
            {
                ?entity :primaryAttachsTo ?prim .
                FILTER regex(str(?prim),  '""" + bus + """') .
                OPTIONAL {
                    ?entity a :Line .
                    ?entity :primaryAttachsTo ?n1 .
                    ?entity :attachsTo ?n2 .
                }
            }
            UNION
            {
                ?entity :attachsTo ?sec .
                FILTER regex(str(?sec), '""" + bus + """') . 
                OPTIONAL {
                    ?entity a :Line .
                    ?entity :primaryAttachsTo ?n1 .
                    ?entity :attachsTo ?n2 .
                }
            }
        } 
"""
        res = g.query(query_str)
        for row in res:
            # If the distance to this bus from the origin is greater than dist then go next
            if entity_dist[bus] > dist:
                break

            # Add the entity if not in result list
            if row['entity'] in results:
                continue
            results.append(row['entity'])
            results_dist.append(entity_dist[bus])

            if 'Line' in str(row['type']) and row['n1'] is not None and row['n2'] is not None:
                bus1 = row['n1'].split('#')[1].split('_')[1]
                bus2 = row['n2'].split('#')[1].split('_')[1]
                if bus1 not in bus_to_search:
                    bus_to_search.append(bus1)
                if bus2 not in bus_to_search:
                    bus_to_search.append(bus2)
                if bus1 != bus:
                    entity_dist[bus1] = entity_dist[bus] + 1
                if bus2 != bus:
                    entity_dist[bus2] = entity_dist[bus] + 1
                

    return zip(results, results_dist)

def traverse_grid(root_bus = None):
    """
    BFS tree traversal of the grid starting from the root node

    Returns a dict of buses and their properties w.r.t to the graph
    """
    if root_bus is None:
        root_bus = generator.bus1
    visited = {bus: False for bus in buses.keys()}
    q = deque([root_bus])
    traversed_buses = {
        root_bus : {
            'depth' : 0
        }
    }

    while len(q) > 0:
        bus = q.popleft()
        visited[bus] = True
        # Set child attribute value
        if len(buses_child[bus]) == 0:
            traversed_buses[bus]['child'] = True
            continue
        traversed_buses[bus]['child'] = False
        for neighbor in buses_child[bus]:
            if not visited[neighbor]:
                q.append(neighbor)
                traversed_buses[neighbor] = {'depth': traversed_buses[bus]['depth'] + 1}

    return traversed_buses

def main():
    args = parser.parse_args()

    outfilename = args.outfile 
    onto_filename = args.infile
    nodes_filename = args.nodes_file
    device_filename= args.device_file
    period = args.period
    error = args.error

    g.parse(onto_filename)

    # You must query buses first
    query_buses()
    # You must query double buses/connections after querying the buses
    query_double_buses()
    # Before querying any further you need to query the generator after
    query_generator()

    # This will get all equipments downstream from a bus
    traversed_buses = traverse_grid('671')
    query_equipments = set()
    for bus in traversed_buses.keys():
        print(traversed_buses[bus])
        equipments = query_neighbours(bus)
        query_equipments.update([i[0] for i in equipments])
    print(query_equipments)
    print(len(query_equipments))


    sensors = query_sensors()
    actuators = query_actuators()
    controllers = query_controllers()


    # res = query_neighbours('645', 2)
    # for row in res:
    #     print(row)

    with open(device_filename, 'w') as csv_file:
        fieldnames = ['idn','type','src','dst','period','error','cktElement','cktTerminal','cktPhase','cktProperty']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        idx = 0
        for sensor in sensors:
            writer.writerow({
                    'idn': idx, 'type': 'sensing', 'src': sensor.src, 'dst': sensor.dst, 
                    'period': period, 'error': error, 
                    'cktElement': f'{sensor.equipment}', 'cktTerminal': f'BUS{sensor.bus}', 'cktPhase': f'PHASE_{sensor.phase}', 'cktProperty': 'None'
                })
            # idx += 1
        for actuator in actuators:
            writer.writerow({
                    'idn': idx, 'type': 'acting', 'src': actuator.src, 'dst': actuator.dst, 
                    'period': period, 'error': error, 
                    'cktElement': f'{actuator.equipment}', 'cktTerminal': f'BUS{actuator.bus}', 'cktPhase': f'PHASE_{actuator.phase}', 'cktProperty': 'None'
                })
            # idx += 1
    exit(1)
    
    # Generate the opendss file
    with open(outfilename, 'wt') as outfile:
        outfile.write(pre_object_opendss())
        outfile.write(query_generator())
        outfile.write(query_transformers())
        outfile.write(query_regcontrol())
        outfile.write(query_linecode())
        outfile.write(query_loads())
        outfile.write(query_capacitors())
        outfile.write(query_lines())
        outfile.write(query_switches())
        outfile.write(post_object_opendss())
        outfile.write(set_taps())
        outfile.write("Set ControlMode=OFF ")

    # Generate the node connections file
    with open(nodes_filename, 'wt') as nodes_file:
        regcontrol_buses = []
        for regulator in regcontrols.values():
            regcontrol_buses.append(regulator.bus1)
            regcontrol_buses.append(regulator.bus2)
        # remove duplicate buses
        regcontrol_buses = set(regcontrol_buses)
        nodes_dict = {
            "nodes": {}
        } 
        # The regulators must come first before the buses
        for node in regcontrol_buses:
            buses[node]['connections'] = list(buses[node]['connections'])
            nodes_dict['nodes'][node] = buses[node]
        
        for node in buses.keys():
            buses[node]['connections'] = list(buses[node]['connections'])
            nodes_dict['nodes'][node] = buses[node]

        app_conn = []
        actuators = query_actuators()
        sensors = query_sensors()
        app_conn.extend([sen.get_conn_dict() for sen in sensors])
        app_conn.extend([act.get_conn_dict() for act in actuators])  

        nodes_dict['app_connections'] = app_conn

        nodes_file.write(json.dumps(nodes_dict, indent=2))


       

if __name__ == "__main__":
    main()
