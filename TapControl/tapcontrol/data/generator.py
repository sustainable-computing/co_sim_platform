import argparse
import json
import csv

import SmartGrid_Query as query

parser = argparse.ArgumentParser(description = "Convert turtle files to OpenDSS")
parser.add_argument('--freq', default=60, type=int, help="The frequency of the grid")
parser.add_argument('--outfile', default="outfile.dss", help="The filename of the OpenDSS file")
parser.add_argument('--infile', default="SmartGrid.ttl", help="The filename of the ontology to convert")
parser.add_argument('--nodes_file', default="gen_nodes.json", help="The filename of the nodes json file to be used by the network sim")
parser.add_argument('--device_file', default="gen_devices.csv", help="The filename of the device file to be used by the network sim")
parser.add_argument('--error', default=0.00001667, help="The error margin")
parser.add_argument('--period', default=20, help="The period time for the sensor")



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
    # TODO replace this with the Query helper
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

def set_taps(graph):
    regcontrols = graph.regcontrols
    openstr = ""
    for reg, obj in regcontrols.items():
        openstr += f"Transformer.{reg}.Taps=[1 1] \n"

    return openstr



def main():
    args = parser.parse_args()

    outfilename = args.outfile 
    onto_filename = args.infile
    nodes_filename = args.nodes_file
    device_filename= args.device_file
    period = args.period
    error = args.error

    # import the graph query
    graph = query.SmartGridGraph(onto_filename)

    # You must query buses first
    graph.query_buses()
    # You must query double buses/connections after querying the buses
    graph.query_double_buses()
    # Before querying any further you need to query the generator after
    graph.query_generator()


    sensors = graph.query_sensors()
    actuators = graph.query_actuators()
    controllers = graph.query_controllers()


    with open(device_filename, 'w') as csv_file:
        fieldnames = ['idn','type','src','dst','period','error','cktElement','cktTerminal','cktPhase','cktProperty']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for idx, controller in enumerate(controllers):
        
            for sensor in sensors:
                # If the dst points to the controller
                if sensor.dst in controller.bus:
                    writer.writerow({
                            'idn': idx, 'type': 'sensor', 'src': sensor.src, 'dst': sensor.dst, 
                            'period': period, 'error': error, 
                            'cktElement': f'{sensor.equipment}', 'cktTerminal': f'BUS{sensor.bus}', 'cktPhase': f'PHASE_{sensor.phase}', 'cktProperty': 'None'
                        })
            for actuator in actuators:
                # If the src points to the controller
                if actuator.src in controller.bus:
                    writer.writerow({
                            'idn': idx, 'type': 'actuator', 'src': actuator.src, 'dst': actuator.dst, 
                            'period': period, 'error': error, 
                            'cktElement': f'{actuator.equipment}', 'cktTerminal': f'BUS{actuator.bus}', 'cktPhase': f'PHASE_{actuator.phase}', 'cktProperty': 'None'
                        })
    
    # Generate the opendss file
    with open(outfilename, 'wt') as outfile:
        outfile.write('!---- pre object declareation\n')
        outfile.write(pre_object_opendss())
        outfile.write('!---- Generated Circuit/generator\n')
        outfile.write(graph.query_generator().get_opendss())
        outfile.write('\n!---- Generated Transformer\n')
        outfile.write('\n'.join([trans.get_opendss() for trans in graph.query_transformers()]))
        outfile.write('\n!---- Generated RegControls\n')
        outfile.write('\n'.join([reg_control.get_opendss() for reg_control in graph.query_regcontrol()]))
        outfile.write('\n!---- Generated Line Codes\n')
        outfile.write('\n'.join([linecode.get_opendss() for linecode in graph.query_linecodes()]))
        outfile.write('\n!---- Generated Loads\n')
        outfile.write('\n'.join([load.get_opendss() for load in graph.query_loads()]))
        outfile.write('\n!---- Generated Capacitors\n')
        outfile.write('\n'.join([cap.get_opendss() for cap in graph.query_capacitors()]))
        outfile.write('\n!---- Generated Lines\n')
        outfile.write('\n'.join([line.get_opendss() for line in graph.query_lines()]))
        outfile.write('\n!---- Generated Switches\n')
        outfile.write('\n'.join([switch.get_opendss() for switch in graph.query_switches()]))
        outfile.write('\n!---- Generated Transformer Voltages\n')
        outfile.write(graph.query_transformers_voltages())
        # outfile.write(post_object_opendss())
        outfile.write(set_taps(graph))
        outfile.write("Set ControlMode=OFF ")

    # Generate the node connections file
    with open(nodes_filename, 'wt') as nodes_file:
        regcontrol_buses = []
        for regulator in graph.regcontrols.values():
            regcontrol_buses.append(regulator.bus1)
            regcontrol_buses.append(regulator.bus2)
        # remove duplicate buses
        regcontrol_buses = set(regcontrol_buses)
        nodes_dict = {
            "nodes": {}
        } 
        # The regulators must come first before the buses
        for node in regcontrol_buses:
            graph.buses[node]['connections'] = list(graph.buses[node]['connections'])
            nodes_dict['nodes'][node] = graph.buses[node]
        
        for node in graph.buses.keys():
            graph.buses[node]['connections'] = list(graph.buses[node]['connections'])
            nodes_dict['nodes'][node] = graph.buses[node]

        app_conn = []
        actuators = graph.query_actuators()
        sensors = graph.query_sensors()
        app_conn.extend([sen.get_conn_dict() for sen in sensors])
        app_conn.extend([act.get_conn_dict() for act in actuators])  

        nodes_dict['app_connections'] = app_conn

        nodes_file.write(json.dumps(nodes_dict, indent=2))


       

if __name__ == "__main__":
    main()
