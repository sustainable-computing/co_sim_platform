"""
This is a helper program that will convert all the different config files for IEEE33 into a SmartGrid ontology model.
"""

import re

buses = {}
coord = {}
bus_idx = []

with open('../models/IEEE33_SimDSE.ttl', "w+") as outfile:

    # Write out the prefix, headers, and annotated properties
    prefix_info = """
@prefix : <http://www.semanticweb.org/phoenix/ontologies/2022/0/IEEE33#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix SmartGrid: <http://www.semanticweb.org/phoenix/ontologies/2022/0/SmartGrid#> .
@base <http://www.semanticweb.org/phoenix/ontologies/2022/0/IEEE33> .
"""
    outfile.write(prefix_info)

    import_info = """
<http://www.semanticweb.org/phoenix/ontologies/2022/0/IEEE33> rdf:type owl:Ontology ;
                                                               owl:imports <http://www.semanticweb.org/phoenix/ontologies/2022/0/SmartGrid> ;
                                                               rdfs:comment "This will model the IEEE33" .


#################################################################
#    Classes
#################################################################

:Phasor rdf:type owl:Class ;
        rdfs:subClassOf SmartGrid:Sensor .

:SmartMeter rdf:type owl:Class ;
            rdfs:subClassOf SmartGrid:Sensor .

:Estimator rdf:type owl:Class ;
           rdfs:subClassOf SmartGrid:Controller .

#################################################################
#    Individuals
#################################################################
"""
    outfile.write(import_info)

    with open('../../SmartGridMain/IEEE33/IEEE33_BusXYFull.csv') as bus_coord_file:
        for line in bus_coord_file.readlines():
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
        for idx, row in enumerate(adj_mat_file.readlines()):
            values = row.split()
            src_node = bus_idx[idx]
            # Get all the indices where there is 1 the row
            dst_idx = [i for i,r in enumerate(values) if r == '1']
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
            
            # Check if bus1 and bus2 is the dict of buses
            if bus1 not in buses.keys():
                buses[bus1] = {
                    'connectsTo': set()
                }
            if bus2 not in buses.keys():
                buses[bus2] = {
                    'connectsTo': set()
                }
    
            line_instance = """
:Line_{name} rdf:type owl:NamedIndividual ,
                    SmartGrid:Line ;
            SmartGrid:primaryAttachsTo :Bus_{bus1} ;
            SmartGrid:attachsTo :Bus_{bus2} ;
            SmartGrid:x1 {x1} ;
            SmartGrid:r1 {r1} .

""".format(name=name, bus1=bus1, bus2=bus2, r1=r1, x1=x1)
            outfile.write(line_instance)

    # Write out the transformer data
    with open('../../SmartGridMain/IEEE33/transData33Full.dss') as transfile:
        for line in transfile.readlines():
            items = line.split()
            if items[0] != 'New':
                continue
            name = items[1].split('.')[1]
            bus1 = items[2].split('[')[1]
            bus2 = items[3][:-1]
            conn_primary = items[4].split('[')[1]
            conn_secondary = items[5][:-1]
            kv_primary = items[6].split('[')[1]
            kv_secondary = items[7][:-1]
            kva = items[8].split('[')[1]
            xhl = items[10].split('=')[1]
            sub = items[11].split('=')[1]

            # Check if bus1 and bus2 is the dict of buses
            if bus1 not in buses.keys():
                buses[bus1] = {
                    'connectsTo': set()
                }
            if bus2 not in buses.keys():
                buses[bus2] = {
                    'connectsTo': set()
                }           

            transformer_instance = """
:Transformer_{name} rdf:type owl:NamedIndividual ,
                             SmartGrid:Transformer ;
                    SmartGrid:primaryAttachsTo :Bus_{bus1} ;
                    SmartGrid:attachsTo :Bus_{bus2} ;
                    SmartGrid:connection_primary "{conn_primary}" ;
                    SmartGrid:connection_secondary "{conn_secondary}" ;
                    SmartGrid:kV_primary {kv_primary} ;
                    SmartGrid:kV_secondary {kv_secondary} ;
                    SmartGrid:Kva {kva} ;
                    SmartGrid:XHL {xhl} ;
                    SmartGrid:sub "{sub}" .

""".format(name=name, bus1=bus1, bus2=bus2, conn_primary=conn_primary, conn_secondary=conn_secondary,
           kv_primary=kv_primary, kv_secondary=kv_secondary, kva=kva, xhl=xhl, sub=sub)

            outfile.write(transformer_instance)
    
    # Write out the load to the file
    with open('../../SmartGridMain/IEEE33/loadData33Full.dss') as loadfile:
        for line in loadfile.readlines():
            items = line.split() 
            if items[0] != 'New':
                continue
            name = items[1].split('.')[1]
            node_secondary = items[1].split('.')[2]
            num_phases = items[2].split('=')[1]
            bus1 = items[3].split('=')[1].split('.')[0]
            node_primary = items[3].split('=')[1].split('.')[1]
            kw = items[4].split('=')[1]
            kvar = items[5].split('=')[1]
            kv = items[6].split('=')[1]
            vminpu = items[7].split('=')[1]
            vmaxpu = items[8].split('=')[1]
            

            # Check if bus1 is the dict of buses
            if bus1 not in buses.keys():
                buses[bus1] = {
                    'connectsTo': set()
                }
         
            load_instance = """
:Load_{name} rdf:type owl:NamedIndividual ,
                      SmartGrid:Load ;
             SmartGrid:nodes_secondary "{nodes_secondary}" ;
             SmartGrid:nodes_primary "{nodes_primary}" ;
             SmartGrid:num_phases {num_phases} ;
             SmartGrid:primaryAttachsTo :Bus_{bus1} ;
             SmartGrid:kW {kw} ;
             SmartGrid:kvar {kvar} ;
             SmartGrid:kV_primary {kv} ;
             SmartGrid:vminpu {vminpu} ;
             SmartGrid:vmaxpu {vmaxpu} .

""".format(name=name, nodes_secondary=node_secondary, nodes_primary=node_primary, num_phases=num_phases,
           bus1=bus1, kw=kw, kvar=kvar, kv=kv, vminpu=vminpu, vmaxpu=vmaxpu)
            outfile.write(load_instance)

    # Write out the buses
    # Do this at the end
    for bus, value in buses.items():
        bus_instance = """
:Bus_{name} rdf:type owl:NamedIndividual ,
                     SmartGrid:Bus ; """.format(name=bus)
        if "locatedAt" in value.keys():
            bus_instance += "SmartGrid:locatedAt :{bus_coord} ;\n".format(bus_coord=value['locatedAt'])
        
        # If there are any connectsTo relations for the node/bus then we write it out
        if len(buses[bus]['connectsTo']) > 0:
            bus_instance += """SmartGrid:connectsTo """
            for connection in buses[bus]['connectsTo']:
                bus_instance += """:Bus_{} ,\n""".format(connection)
            bus_instance = bus_instance[:-2] + '.'
        else:
            # end with a .
            bus_instance += ".\n"
        bus_instance += "\n\n"

        outfile.write(bus_instance)

    with open("../../SmartGridMain/IEEE33/IEEE33_Devices_Test.csv") as device_file:
        for device in device_file.readlines():
            device_info = device.split(',')
            idn = device_info[0]
            device_type = device_info[1]
            src = device_info[2]
            dst = device_info[3]
            period = device_info[4]
            error = device_info[5]
            cktElement = device_info[6]
            cktTerminal = device_info[7][-1]
            cktPhase = device_info[8].split('_')
            cktProperty = device_info[9]
            
            device_instance = ""
            if device_type.lower() == "phasor":
                device_instance += """
:Phasor_{name} rdf:type owl:NamedIndividual ,
                        :Phasor ;
                SmartGrid:bus_terminal {bus_term} ;
                SmartGrid:connectsTo {src} ;
                SmartGrid:phase {phase} ;
                SmartGrid:monitor {monitor} ;
                SmartGrid:feeds :Estimator .
""".format(name=idn, bus_term=cktTerminal,src=src, phase=cktPhase[1], monitor=cktElement)
            if device_type.lower() == "smartmeter":
                device_instance += """
:SmartMeter_{name} rdf:type owl:NamedIndividual ,
                            :SmartMeter ;
                    SmartGrid:bus_terminal {bus_term} ;
                    SmartGrid:connectsTo :Bus_{src} ;
                    SmartGrid:phase {phase} ;
                    SmartGrid:monitor :{monitor} ;
                    SmartGrid:feeds :Estimator .                 
""".format(name=idn, bus_term=cktTerminal,src=src, phase=cktPhase[1], monitor=cktElement)

            # outfile.write(device_instance)