import argparse
import json
import csv
import sys 
import os.path
import git 
import os

# Setup path to search for custom modules at the git root level
repo = git.Repo('.', search_parent_directories=True)
repo_root_path = repo.working_tree_dir
sys.path.insert(1, repo_root_path)

from SmartGridOntology import SmartGrid_Query as query

parser = argparse.ArgumentParser(description = "Convert turtle files to OpenDSS")
parser.add_argument('--freq', default=60, type=int, help="The frequency of the grid")
parser.add_argument('--infile', help="The filename of the ontology to convert", required=True)
parser.add_argument('--outdir', help="The output directory for the generated files", default="generated_files")
parser.add_argument('--outfile', default="outfile.dss", help="The filename of the OpenDSS file")
parser.add_argument('--nodes_file', default="gen_nodes.json", help="The filename of the nodes json file to be used by the network sim")
parser.add_argument('--device_file', default="IEEE33_SimDSE_Devices.csv", help="The filename of the device file to be used by the network sim")
parser.add_argument('--error', default=0.00001667, help="The error margin")
parser.add_argument('--period', default=20, help="The period time for the sensor")



def pre_object_opendss(freq = 60):
    """
    This will produce the pre-object definition 
    """
    opendss_str = f"Clear \nSet DefaultBaseFrequency={freq} \n\n"
    return opendss_str

def set_taps(graph):
    """
    This will produce the initial tap settings for the regulator
    """
    regcontrols = graph.regcontrols
    openstr = ""
    for reg, obj in regcontrols.items():
        openstr += f"Transformer.{reg}.Taps=[1 1] \n"

    return openstr

def main():
    args = parser.parse_args()
    
    outdir = args.outdir
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

    graph.query_nodes()

    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    controllers = [str(controller) for controller in graph.query_controllers()]
    sensors = graph.query_sensors()
    actuators = graph.query_actuators()
    with open(f'{outdir}/{device_filename}', 'w') as csv_file:
        fieldnames = ['type','src','dst','cidx','didx','period','error','cktElement','cktTerminal','cktPhase','cktProperty']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        # This will keep track of all the devices located at the same src
        device_counter = {}
        
        for sensor in sensors:
            didx_key = f'Sensor-{sensor.src}'
            if didx_key not in device_counter.keys():
                device_counter[didx_key] = 0
            cidx = controllers.index(sensor.controller)
            equipment_name = sensor.equipment.replace('_','.',1)
            if 'Phasor' in sensor.name:
                equipment_name = equipment_name.lower()
            if 'SmartMeter' in sensor.name:
                equipment_name = equipment_name + '.' + sensor.phase
            writer.writerow({
                    'type': 'Phasor' if 'Phasor' in sensor.name else 'SmartMeter', 'src': sensor.src, 'dst': sensor.dst, 'cidx': cidx, 'didx': device_counter[didx_key], 
                    'period': 2000 if 'Phasor' in sensor.name else 15000 , 'error': error, 
                    'cktElement': f'{equipment_name}', 'cktTerminal': f'BUS{sensor.bus}', 'cktPhase': f'PHASE_{sensor.phase}', 'cktProperty': 'None'
            })

            device_counter[didx_key] += 1

    # Generate the opendss file
    with open(f'{outdir}/{outfilename}', 'wt') as outfile:
        outfile.write('!---- pre object declareation\n')
        outfile.write(pre_object_opendss())
        outfile.write('!---- Generated Circuit\n')
        outfile.write(graph.query_circuit().get_opendss())
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
        outfile.write("Set ControlMode=OFF")
        outfile.write('\n!---- Generated Transformer Voltages\n')
        outfile.write(graph.query_transformers_voltages())
        outfile.write(set_taps(graph))

    # Generate the node connections file
    with open(f'{outdir}/{nodes_filename}', 'wt') as nodes_file:
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
            conn_list = list(graph.nodes[node]['connections'])
            graph.nodes[node]['connections'] = [value for value in sorted(conn_list, key=lambda item: int(item))]
            nodes_dict['nodes'][node] = graph.nodes[node]
        
        for node in graph.nodes.keys():
            conn_list = list(graph.nodes[node]['connections'])
            graph.nodes[node]['connections'] = [value for value in sorted(conn_list, key=lambda item: int(item))]
            nodes_dict['nodes'][node] = graph.nodes[node]

        unordered_nodes = nodes_dict['nodes']
        ordered_nodes = {key:value for key, value in sorted(unordered_nodes.items(), key=lambda item: int(item[0]))}
        nodes_dict['nodes'] = ordered_nodes
        nodes_file.write(json.dumps(nodes_dict, indent=2, sort_keys=False))


       

if __name__ == "__main__":
    main()