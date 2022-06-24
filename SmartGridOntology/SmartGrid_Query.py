"""
This will contain helper SPARQL queries for the smartgrid ontology. 
The resulting queries will be of course python data structure friendly
"""

from rdflib import Graph 
from collections import deque

from .SmartGrid import *


class SmartGridGraph:
    def __init__(self, file):
        self.g = Graph().parse(file)
        self.circuit = None
        self.generators = {}
        self.buses = {}
        self.nodes = {}
        # Get the child of the bus
        self.buses_child = {}
        # Get the parent of the bus
        self.buses_parent = {}
        self.lines = {}
        self.loads = {}
        self.capacitors = {}
        self.linecode = {}
        self.transformers = {}
        self.regcontrols = {}

    # There should be only one but in reality there could be multiple circuits
    def query_circuit(self):
        query_str = """
        SELECT *
        WHERE {
            ?circuit a SmartGrid:Circuit .
            ?circuit SmartGrid:primaryAttachsTo ?bus1 .
            ?circuit SmartGrid:MVAsc1 ?MVAsc1 .
            ?circuit SmartGrid:MVAsc3 ?MVAsc3 .
            ?circuit SmartGrid:angle ?angle .
            ?circuit SmartGrid:kV_primary ?kv_sec .
            ?circuit SmartGrid:num_phases ?num_phases .
            ?circuit SmartGrid:pu ?pu .
        }    
        """

        res = self.g.query(query_str)
        for row in res:
            circuit = Circuit(
                circuit = row['circuit'],
                bus1 = row['bus1'],
                kv_sec = row['kv_sec'],
                pu = row['pu'],
                num_phases = row['num_phases'],
                MVAsc1 = row['MVAsc1'],
                MVAsc3 = row['MVAsc3'],
                angle = row['angle']
            )
            self.circuit = circuit

        return self.circuit

    def query_generator(self):
        query_str = """
        SELECT *
        WHERE {
            ?gen a SmartGrid:Generator .
            ?gen SmartGrid:primaryAttachsTo ?bus1 .
            ?gen SmartGrid:MVAsc1 ?MVAsc1 .
            ?gen SmartGrid:MVAsc3 ?MVAsc3 .
            ?gen SmartGrid:pu ?pu .
            ?gen SmartGrid:angle ?angle .
            ?gen SmartGrid:kV_secondary ?kv_sec .
            ?gen SmartGrid:num_phases ?num_phases
        }    
        """

        res = self.g.query(query_str)
        generators = []
        for row in res:
            gen = Generator(
                gen = row['gen'],
                bus1 = row['bus1'],
                kv_sec = row['kv_sec'],
                pu = row['pu'],
                num_phases = row['num_phases'],
                MVAsc1 = row['MVAsc1'],
                MVAsc3 = row['MVAsc3'],
                angle = row['angle']
            )
            generators.append(gen)
        
        return generators

    def query_transformers(self):
        query_str = """
        SELECT *
        WHERE {
            ?trans a SmartGrid:Transformer .
            ?trans SmartGrid:primaryAttachsTo ?prim_bus .
            ?trans SmartGrid:attachsTo ?sec_bus .
            ?trans SmartGrid:num_phases ?num_phases .
            ?trans SmartGrid:Kva ?Kva .
            ?trans SmartGrid:XHL ?xhl .
            ?trans SmartGrid:connection_primary ?conn_prim .
            ?trans SmartGrid:connection_secondary ?conn_sec .
            ?trans SmartGrid:kV_primary ?kv_prim .
            ?trans SmartGrid:kV_secondary ?kv_sec .
            ?trans SmartGrid:percent_R ?percent_R .
            OPTIONAL {
                ?trans SmartGrid:XHT ?xht .
                ?trans SmartGrid:XLT ?xlt .
            }
        }
        """
        res = self.g.query(query_str)

        transformers = []
        for row in res:
            trans = Transformer(
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
            transformers.append(trans)
        return transformers 

    def query_capacitors(self):
        query_str = """
        SELECT *
        WHERE {
            ?cap a SmartGrid:Capacitor .
            ?cap SmartGrid:primaryAttachsTo ?bus .
            ?cap SmartGrid:kV_primary ?kv .
            ?cap SmartGrid:kvar ?kvar .
            ?cap SmartGrid:num_phases ?num_phases .
            ?cap SmartGrid:kvar ?kvar .
            OPTIONAL {
                ?cap SmartGrid:nodes_primary ?prim_bus .
            }
        }    
        """
        res = self.g.query(query_str)
        capacitors = []
        for row in res:
            cap = Capacitor(
                cap = row['cap'],
                bus = row['bus'],
                kv = row['kv'],
                nodes_primary = row['prim_bus'],
                num_phases = row['num_phases'],
                kvar = row['kvar']
            )
            capacitors.append(cap)
        return capacitors 

    def query_buses(self):
        """
        Get all the buses from the power grid
        """
        query_str = """
        SELECT *
        WHERE {
            ?bus a SmartGrid:Bus .
            ?bus SmartGrid:locatedAt ?loc .
            ?loc SmartGrid:coord_x ?x .
            ?loc SmartGrid:coord_y ?y .
        }    
        """
        res = self.g.query(query_str)
        
        for row in res: 
            node = {
                'x': int(row['x']),
                'y': int(row['y']),
                'connections': set()
            }
            self.buses[row['bus'].split('#')[1].split('_')[1]] = node
            self.buses_child[row['bus'].split('#')[1].split('_')[1]] = set()
            self.buses_parent[row['bus'].split('#')[1].split('_')[1]] = set()
        
        return self.buses

    def query_double_buses(self):
        """
        This will get all electrical equipment that is connected to two buses
        """
        query_str = """
        SELECT *
        WHERE {
            ?entity rdf:type ?type .
            ?type rdfs:subClassOf* SmartGrid:Electrical_Equipment .
            ?entity SmartGrid:primaryAttachsTo ?bus1 .
            ?entity SmartGrid:attachsTo ?bus2 .
        } 
        """
        res = self.g.query(query_str)
        for row in res:
            bus_in = row['bus1'].split('#')[1].split('_')[1]
            bus_out = row['bus2'].split('#')[1].split('_')[1]
            self.buses[bus_in]['connections'].add(bus_out)
            self.buses[bus_out]['connections'].add(bus_in)
            self.buses_child[bus_in].add(bus_out)
            self.buses_parent[bus_out].add(bus_in)
        
        return self.buses
    def query_nodes(self):
        """
        This will get all network nodes including buses that has a connectsTo relationship
        """
        query_str = """
        SELECT DISTINCT ?node ?x ?y ?neighbor ?neighbor_x ?neighbor_y
        WHERE {
            {
                ?node a SmartGrid:Bus .
                ?node SmartGrid:connectsTo ?neighbor .
            } UNION {
                ?node a SmartGrid:Communication_Node .
                ?node SmartGrid:connectsTo ?neighbor .
            }   
            ?node SmartGrid:locatedAt ?loc .
            ?loc SmartGrid:coord_x ?x .
            ?loc SmartGrid:coord_y ?y .
            ?neighbor SmartGrid:locatedAt ?neighbor_loc .
            ?neighbor_loc SmartGrid:coord_x ?neighbor_x .
            ?neighbor_loc SmartGrid:coord_y ?neighbor_y .
        }
        """
        res = self.g.query(query_str)
        for row in res:
            node_name = row['node'].split('#')[1].split('_')[1]
            neighbor_node_name = row['neighbor'].split('#')[1].split('_')[1]
            if node_name not in self.nodes.keys():
                self.nodes[node_name] = {
                    'x': int(row['x']),
                    'y': int(row['y']),
                    'connections': set()
                }
            if neighbor_node_name not in self.nodes.keys():
                self.nodes[neighbor_node_name] = {
                    'x': int(row['neighbor_x']),
                    'y': int(row['neighbor_y']),
                    'connections': set()
                }
            self.nodes[node_name]['connections'].add(neighbor_node_name)
            self.nodes[neighbor_node_name]['connections'].add(node_name)
            
        return self.nodes      

    def query_lines(self):
        # Because the orientation of the bus connection does not matter 
        query_str = """
        SELECT *
        WHERE {
            ?line a SmartGrid:Line .
            ?line SmartGrid:primaryAttachsTo ?bus1 .
            ?line SmartGrid:attachsTo ?bus2 .
            ?line SmartGrid:LineCode ?linecode .
            ?line SmartGrid:length ?length .
            ?line SmartGrid:nodes_primary ?n_prim .
            ?line SmartGrid:nodes_secondary ?n_sec .
            ?line SmartGrid:num_phases ?num_phases .
            ?line SmartGrid:unit ?unit .
        }
        """
        res = self.g.query(query_str)
        lines = []
        for row in res:
            line = Line(
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
            lines.append(line)
        return lines

    def query_loads(self):
        # Write the query
        query_str = """
        SELECT *
        WHERE {
            ?load a SmartGrid:Load .
            ?load SmartGrid:primaryAttachsTo ?bus1 .
            ?load SmartGrid:connection_primary ?conn .
            ?load SmartGrid:kV_primary ?kv_prim .
            ?load SmartGrid:kW ?kW .
            ?load SmartGrid:kvar ?kvar .
            ?load SmartGrid:model ?model .
            ?load SmartGrid:nodes_primary ?n_prim .
            ?load SmartGrid:num_phases ?num_phases . 
            OPTIONAL {
                ?load SmartGrid:nodes_secondary ?n_sec .
            }
        }
        """
        # Get the query
        res = self.g.query(query_str)
        loads = []
        for row in res:
            load = Load(
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
            loads.append(load)

        return loads

    def query_linecodes(self):
        query_str = """
        SELECT *
        WHERE {
            ?linecode a SmartGrid:LineCode .
            ?linecode SmartGrid:freq ?freq .
            ?linecode SmartGrid:num_phases ?num_phases .
            ?linecode SmartGrid:rmat ?rmat .
            ?linecode SmartGrid:xmat ?xmat .
            ?linecode SmartGrid:unit ?unit .
            OPTIONAL {
                ?linecode SmartGrid:cmat ?cmat .
            }
        }    
        """
        res = self.g.query(query_str)

        linecodes = []

        for row in res:
            linecode = LineCode(
                linecode = row['linecode'],
                freq = row['freq'],
                num_phases = row['num_phases'],
                rmat = row['rmat'],
                xmat = row['xmat'],
                unit = row['unit'],
                cmat = row['cmat']
            )
            linecodes.append(linecode)
        return linecodes

    def query_switches(self):
        query_str = """
        SELECT *
        WHERE {
            ?switch a SmartGrid:Switch .
            ?switch SmartGrid:primaryAttachsTo ?bus1 .
            ?switch SmartGrid:attachsTo ?bus2 .
            ?switch SmartGrid:num_phases ?num_phases .
            ?switch SmartGrid:c0 ?c0 .
            ?switch SmartGrid:c1 ?c1 .
            ?switch SmartGrid:r0 ?r0 .
            ?switch SmartGrid:r1 ?r1 .
            ?switch SmartGrid:x0 ?x0 .
            ?switch SmartGrid:x1 ?x1 .
        }    
        """
        res = self.g.query(query_str)
        switches = []
        for row in res:
            switch = Switch(
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
            switches.append(switch)
        return switches

    def query_regcontrol(self):
        query_str = """
        SELECT *
        WHERE {
            ?reg a SmartGrid:regcontrol .
            ?reg SmartGrid:primaryAttachsTo ?bus1 .
            ?reg SmartGrid:attachsTo ?bus2 .
            ?reg SmartGrid:Kva ?kva .
            ?reg SmartGrid:R ?R .
            ?reg SmartGrid:X ?X.
            ?reg SmartGrid:XHL ?XHL .
            ?reg SmartGrid:band ?band .
            ?reg SmartGrid:bank ?bank . 
            ?reg SmartGrid:ctprim ?ctprim .
            ?reg SmartGrid:kV_primary ?kv_prim .
            ?reg SmartGrid:kV_secondary ?kv_sec .
            ?reg SmartGrid:tap_primary ?tap_prim .
            ?reg SmartGrid:tap_secondary ?tap_sec .
            ?reg SmartGrid:max_tap ?max_tap .
            ?reg SmartGrid:min_tap ?min_tap .
            ?reg SmartGrid:nodes_primary ?nodes_primary .
            ?reg SmartGrid:nodes_secondary ?nodes_secondary .
            ?reg SmartGrid:num_phases ?num_phases .
            ?reg SmartGrid:num_taps ?num_taps .
            ?reg SmartGrid:percent_Load_Loss ?percent_load_loss .
            ?reg SmartGrid:ptratio ?ptratio .
            ?reg SmartGrid:vreg ?vreg .
        }    
        """
        res = self.g.query(query_str)
        reg_controls = []
        for row in res:
            reg_control = VoltageRegulator(
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
            self.regcontrols[str(reg_control)] = reg_control
            reg_controls.append(reg_control)
        return reg_controls

    def query_actuators(self):
        query_str = """
        SELECT *
        WHERE {
            ?act rdf:type ?type .
            ?type rdfs:subClassOf* SmartGrid:Actuator .
            ?act SmartGrid:connectsTo ?dst_node .
            ?act SmartGrid:controls ?controls .
            ?act SmartGrid:isFedBy ?fedby .
            ?act SmartGrid:phase ?phase .
            ?act SmartGrid:bus_terminal ?bus .
            ?controls SmartGrid:primaryAttachsTo ?bus1 .
            ?fedby SmartGrid:connectsTo ?src_node .
            OPTIONAL {
                ?controls SmartGrid:attachsTo ?bus2 .
            }
        }    
        """
        res = self.g.query(query_str)
        actuators = []
        for row in res:
            if '1' in row['bus'] and row['bus1'] is not None:
                dst = row['bus1']
            elif '2' in row['bus'] and row['bus2'] is not None:
                dst = row['bus2']
            else:
                dst = row['bus1']
            act = Actuator(
                actuator = row['act'],
                dst = dst,
                src = row['src_node'],
                controls = row['controls'],
                controller = row['fedby'],
                phase = row['phase'],
                bus = row['bus']
            )
            actuators.append(act)
        
        return actuators

    def query_sensors(self):
        query_str = """
        SELECT *
        WHERE {
            ?sen rdf:type ?type .
            ?type rdfs:subClassOf* SmartGrid:Sensor .
            ?sen SmartGrid:connectsTo ?src_node .
            ?sen SmartGrid:feeds ?controller .
            ?sen SmartGrid:measures ?measures . 
            ?sen SmartGrid:monitor ?monitor .
            ?monitor SmartGrid:primaryAttachsTo ?bus1 .
            ?sen SmartGrid:rate ?rate .
            ?sen SmartGrid:phase ?phase .
            ?sen SmartGrid:bus_terminal ?bus .
            ?controller SmartGrid:connectsTo ?dst_node .
            OPTIONAL {
                ?monitor SmartGrid:attachsTo ?bus2 .
            }
        }    
        """
        res = self.g.query(query_str)
        sensors = []
        for row in res:
            if '1' in row['bus']:
                src = row['bus1']
            elif '2' in row['bus'] and row['bus2'] is not None:
                src = row['bus2']
            else:
                src = row['bus1']
            sensor = Sensor(
                sensor = row['sen'],
                connects_to = row['src_node'],
                controller = row['controller'],
                measures = row['measures'],
                monitor = row['monitor'],
                src = src,
                rate = row['rate'],
                dst = row['dst_node'],
                phase = row['phase'],
                bus = row['bus']
            )
            sensors.append(sensor)

        return sensors

    def query_controllers(self):
        """
        This will return the list of controllers in the graph    
        """
        query_str = """
        SELECT DISTINCT *
        WHERE {
            ?entity rdf:type ?type .
            ?type rdfs:subClassOf* SmartGrid:Controller .
            ?entity SmartGrid:connectsTo ?connects_to .
            ?connects_to SmartGrid:locatedAt ?bus .
        }    
        """
        res = self.g.query(query_str)
        controllers = []
        for row in res:
            control = Controller(
                control = row['entity'],
                bus = row['bus']
            )
            controllers.append(control)
        
        return controllers
    
    def query_transformers_voltages(self):
        query_str = """ 
        SELECT DISTINCT ?kv
        WHERE {
            ?trans a SmartGrid:Transformer . 
            {
                ?trans SmartGrid:kV_primary ?kv.

            }
            UNION 
            {
                ?trans SmartGrid:kV_secondary ?kv    
            }
        }
            """
        res = self.g.query(query_str)
        voltages = []
        for row in res:
            voltages.append(float(row['kv']))

        opendss_str = f"Set VoltageBases={voltages} \n"
        opendss_str += "calcv \nSolve \n"
        return opendss_str

    def query_neighbours(self, origin, dist = 0):
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
                ?type rdfs:subClassOf* SmartGrid:Electrical_Equipment .
                {
                    ?entity SmartGrid:primaryAttachsTo ?prim .
                    FILTER regex(str(?prim),  '""" + bus + """') .
                    OPTIONAL {
                        ?entity a SmartGrid:Line .
                        ?entity SmartGrid:primaryAttachsTo ?n1 .
                        ?entity SmartGrid:attachsTo ?n2 .
                    }
                }
                UNION
                {
                    ?entity SmartGrid:attachsTo ?sec .
                    FILTER regex(str(?sec), '""" + bus + """') . 
                    OPTIONAL {
                        ?entity a SmartGrid:Line .
                        ?entity SmartGrid:primaryAttachsTo ?n1 .
                        ?entity SmartGrid:attachsTo ?n2 .
                    }
                }
            } 
            """
            res = self.g.query(query_str)
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
    
    def traverse_grid(self, root_bus = None):
        """
        BFS tree traversal of the grid starting from the root node

        Returns a dict of buses and their properties w.r.t to the graph
        """
        if root_bus is None:
            root_bus = self.generator.bus1
        visited = {bus: False for bus in self.buses.keys()}
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
            if len(self.buses_child[bus]) == 0:
                traversed_buses[bus]['child'] = True
                continue
            traversed_buses[bus]['child'] = False
            for neighbor in self.buses_child[bus]:
                if not visited[neighbor]:
                    q.append(neighbor)
                    traversed_buses[neighbor] = {'depth': traversed_buses[bus]['depth'] + 1}

        return traversed_buses