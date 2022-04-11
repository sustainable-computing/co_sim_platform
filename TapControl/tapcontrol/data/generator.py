from rdflib import Graph
import re 
import SmartGrid
import argparse
import json

g = Graph()

parser = argparse.ArgumentParser(description = "Convert turtle files to OpenDSS")
parser.add_argument('--freq', default=60, type=int, help="The frequency of the grid")
parser.add_argument('--outfile', default="outfile.dss", help="The filename of the OpenDSS file")
parser.add_argument('--infile', default="SmartGrid.ttl", help="The filename of the ontology to convert")
parser.add_argument('--nodes_file', default="gen_nodes.json", help="The filename of the nodes json file to be used by the network sim")


buses = {}
lines = {}
loads = {}
capacitors = {}
linecode = {}
transformers = {}
regcontrols = {}


def query_generator():
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
            'connections': []
        }
        buses[row['bus'].split('#')[1].split('_')[1]] = node
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
    ?act a :Actuator .
    ?act :connectsTo ?conn_to .
    ?act :controls ?controls .
    ?act :isFedBy ?fedby .
    ?controls :primaryAttachsTo ?dst .
    ?fedby :connectsTo ?endpoint .
    ?endpoint :locatedAt ?src .
}    
"""
    res = g.query(query_str)
    actuators = []
    for row in res:
        act = SmartGrid.Actuator(
            actuator = row['act'],
            dst = row['dst'],
            src = row['src']
        )

        actuators.append(act.get_conn_dict())
    
    return actuators


def query_sensors():
    query_str = """
SELECT *
WHERE {
    ?sen a :Voltage_Sensor .
    ?sen :connectsTo ?conn_to .
    ?sen :feeds ?feeds .
    ?sen :measures ?measures . 
    ?sen :monitor ?monitor .
    ?sen :rate ?rate .
    ?feeds :connectsTo ?endpoint .
    ?endpoint :locatedAt ?dst .
}    
"""
    res = g.query(query_str)
    sensors = []
    for row in res:
        # monitor is the src
        sensor = SmartGrid.Sensor(
            sensor = row['sen'],
            connects_to = row['conn_to'],
            feeds = row['feeds'],
            measures = row['measures'],
            src = row['monitor'],
            rate = row['rate'],
            dst = row['dst']
        )
        sensors.append(sensor.get_conn_dict())
    
    return sensors

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
        buses[bus_in]['connections'].append(bus_out)
        buses[bus_out]['connections'].append(bus_in)

def query_neighbours(origin, dist = 1):
    """
    This will get all electrical equipment that is attached to a bus
    """
    results = []
    # include the start bus
    bus_to_search = [origin]
    bus_dist = {
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
            }
            UNION
            {
                ?entity :attachsTo ?sec .
                FILTER regex(str(?sec), '""" + bus + """') . 
            }
            UNION
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
        print(len(res))
        for row in res:
            print(row)
            # If the distance to this bus from the origin is greater than dist then go next
            if bus_dist[bus] >= dist:
                break
            # Skip if the result is already in the result list
            # if row in results:
            #     continue
            results.append(row)
            if 'Line' in str(row['type']) and row['n1'] is not None and row['n2'] is not None:
                bus1 = row['n1'].split('#')[1].split('_')[1]
                bus2 = row['n2'].split('#')[1].split('_')[1]
                if row['n1'] not in results:
                    bus_to_search.append(bus1)
                    bus_dist[bus1] = bus_dist[bus] + 1
                if row['n2'] not in results:
                    bus_to_search.append(bus2)
                    bus_dist[bus2] = bus_dist[bus] + 1

    return results




def main():
    args = parser.parse_args()

    outfilename = args.outfile 
    onto_filename = args.infile
    nodes_filename = args.nodes_file
    g.parse(onto_filename)

    query_buses()
    
    query_double_buses()

    res = query_neighbours('645')
    for row in res:
        print(row['entity'])
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
        for node in regcontrol_buses:
            buses[node]['connections'] = list(set(buses[node]['connections']))
            nodes_dict['nodes'][node] = buses[node]
        
        for node in buses.keys():
            buses[node]['connections'] = list(set(buses[node]['connections']))
            nodes_dict['nodes'][node] = buses[node]

        app_conn = []
        actuators = query_actuators()
        sensors = query_sensors()
        app_conn.extend(sensors)
        app_conn.extend(actuators)  

        nodes_dict['app_connections'] = app_conn

        nodes_file.write(json.dumps(nodes_dict, indent=2))


       

if __name__ == "__main__":
    main()
