"""
This is a helper program that will convert all the different config files for IEEE33 into a SmartGrid ontology model.

Note: This is only for IEEE33 Bus network, secondary network is not involved
"""

import re

buses = {}
coord = {}
bus_idx = []

with open('../models/IEEE33_base.ttl', "w+") as outfile:

    # Write out the prefix, headers, and annotated properties
    prefix_info = """
@prefix : <http://www.semanticweb.org/phoenix/ontologies/2022/0/IEEE33_base#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix SmartGrid: <http://www.semanticweb.org/phoenix/ontologies/2022/0/SmartGrid#> .
@base <http://www.semanticweb.org/phoenix/ontologies/2022/0/IEEE33_base> .
"""
    outfile.write(prefix_info)

    import_info = """
<http://www.semanticweb.org/phoenix/ontologies/2022/0/IEEE33_base> rdf:type owl:Ontology ;
                                                               owl:imports <http://www.semanticweb.org/phoenix/ontologies/2022/0/SmartGrid> ;
                                                               rdfs:comment "This will model the IEEE33 primary nodes only" .


#################################################################
#    Individuals
#################################################################
"""
    outfile.write(import_info)

    # Write out the circuit information
    circuit_instance = """
:Circuit_Master33 rdf:type owl:NamedIndividual ,
                           SmartGrid:Circuit ;
                  SmartGrid:primaryAttachesTo :Bus_1 ;
                  SmartGrid:MVAsc1 5000000 ;
                  SmartGrid:MVAsc3 5000000 ;
                  SmartGrid:kV_primary 12.66 ;
                  SmartGrid:num_phases 3 ;
                  SmartGrid:pu 1 .
    """
    outfile.write(circuit_instance)
    

    substation_instance = """
:Transformer_Sub rdf:type owl:NamedIndividual ,
                          SmartGrid:Transformer ;
                 SmartGrid:primaryAttachsTo :Bus_1 ;
                 SmartGrid:attachsTo :Bus_2 ;
                 SmartGrid:connection_primary "Delta" ;
                 SmartGrid:connection_secondary "Wye" ;
                 SmartGrid:kV_primary 12.66 ;
                 SmartGrid:kV_secondary 0.416 ;
                 SmartGrid:Kva 3000 ;
                 SmartGrid:XHL 4 ;
                 SmartGrid:num_phases 3 ;
                 rdfs:comment "This the substation transformer, based on the European Low Voltage Feeder" .
"""

    outfile.write(substation_instance)


    with open('../../SmartGridMain/IEEE33/IEEE33_BusXYFull.csv') as bus_coord_file:
        # We only want the first 33 (primary) nodes of the network
        for line in bus_coord_file.readlines()[:33]:
            items = re.split(',|\n', line)
            coord_name = f"Coord_{items[1]}_{items[2]}"
            coord[coord_name] = {
                'x': int(items[1]),
                'y': int(items[2])
            }
            buses[items[0]] = {
                'locatedAt': coord_name,
                'connectsTo': set()
            }
            bus_idx.append(items[0])

    with open('../../SmartGridMain/IEEE33/IEEE33_AdjMatrixFull.txt') as adj_mat_file:
        # We only want the first 33 coordinates for the primary nodes
        for idx, row in enumerate(adj_mat_file.readlines()[:33]):
            values = row.split()
            src_node = bus_idx[idx]
            # Get all the indices where there is 1 the row
            dst_idx = [i for i,r in enumerate(values[:33]) if r == '1']
            for col_idx in dst_idx:
                dst_node = bus_idx[col_idx]
                buses[src_node]['connectsTo'].add(dst_node)
                buses[dst_node]['connectsTo'].add(src_node)    


    # Write out the coordinates
    for coord, value in coord.items():
        coord_instance = """
:{name} rdf:type owl:NamedIndividual ,
                       SmartGrid:Coordinates ;
              SmartGrid:coord_x {x} ;
              SmartGrid:coord_y {y} .

""".format(name=coord, x=value['x'], y=value['y'])
        outfile.write(coord_instance)

    # Write out the line data
    with open('../../SmartGridMain/IEEE33/lineData33Full.dss') as linefile:
        for line in linefile.readlines():
            items = line.split()
            if items[0] != 'New':
                continue
            name = items[1].split('.')[1]
            bus1 = items[2].split('=')[1]
            bus2 = items[3].split('=')[1]
            r1 = items[4].split('=')[1]
            x1 = items[5].split('=')[1]
            
            # Check if bus1 and bus2 are in the primary bus network
            if bus1 not in buses.keys() or bus2 not in buses.keys():
                continue
                
            line_instance = """
:Line_{name} rdf:type owl:NamedIndividual ,
                    SmartGrid:Line ;
            SmartGrid:primaryAttachsTo :Bus_{bus1} ;
            SmartGrid:attachsTo :Bus_{bus2} ;
            SmartGrid:x1 {x1} ;
            SmartGrid:r1 {r1} .

""".format(name=name, bus1=bus1, bus2=bus2, r1=r1, x1=x1)
            outfile.write(line_instance)

    # Write out the buses
    # Do this at the end
    for bus, value in buses.items():
        bus_instance = """
:Bus_{name} rdf:type owl:NamedIndividual ,
                     SmartGrid:Bus """.format(name=bus)
        if "locatedAt" in value.keys():
            bus_instance += ";\nSmartGrid:locatedAt :{bus_coord} ".format(bus_coord=value['locatedAt'])
        
        # If there are any connectsTo relations for the node/bus then we write it out
        if len(buses[bus]['connectsTo']) > 0:
            bus_instance += """;\nSmartGrid:connectsTo """
            for connection in buses[bus]['connectsTo']:
                bus_instance += """:Bus_{} ,\n""".format(connection)
            bus_instance = bus_instance[:-2] + '.'
        else:
            # end with a .
            bus_instance += ".\n"
        bus_instance += "\n"

        outfile.write(bus_instance)

    # Write out the loads
    # These are the real and reactive loads from https://www.researchgate.net/figure/Line-data-of-the-IEEE-33-bus-radial-distribution-system-20_tbl1_319906918
    for idx, bus in enumerate(buses.keys()):
        if idx == 0:
            continue
        terminal = (idx % 3) + 1
        load_instance = """
:Load_{bus}_{terminal} rdf:type owl:NamedIndividual ,
                     SmartGrid:Load ;
            SmartGrid:kV_primary 0.240 ;
            SmartGrid:kW 0 ;
            SmartGrid:kvar 0 ;
            SmartGrid:nodes_primary "{terminal}" ;
            SmartGrid:nodes_secondary "{terminal}" ;
            SmartGrid:num_phases 1 ;
            SmartGrid:primaryAttachsTo :Bus_{bus} .
""".format(bus=bus,terminal=terminal)
        outfile.write(load_instance)
