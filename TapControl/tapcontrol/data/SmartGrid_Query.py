"""
This will contain helper SPARQL queries for the smartgrid ontology. 
The resulting queries will be of course python data structure friendly
"""

from rdflib import Graph 
from SmartGrid import *

class SmartGridGraph:
    def __init__(self, file):
        self.g = Graph().parse(file)
        self.generator = None
        self.buses = {}
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

    def query_generator(self):
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

        res = self.g.query(query_str)

        opendss = "!--- Genereted circuit\n"
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
            opendss += gen.get_opendss()
            self.generator = gen
            # There should only be one generator
            break
        opendss += '\n\n'
        return opendss

    def query_transformers(self):
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
        res = self.g.query(query_str)

        opendss = "!--- Generated Transformers\n"

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
            opendss += trans.get_opendss() + '\n'
        opendss += '\n\n'
        return opendss 

    def query_capacitors(self):
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
        res = self.g.query(query_str)
        opendss = "!--- Generated Capacitors\n"
        for row in res:
            cap = Capacitor(
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

    def query_buses(self):
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

    def query_double_buses(self):
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
        res = self.g.query(query_str)
        for row in res:
            bus_in = row['bus1'].split('#')[1].split('_')[1]
            bus_out = row['bus2'].split('#')[1].split('_')[1]
            self.buses[bus_in]['connections'].add(bus_out)
            self.buses[bus_out]['connections'].add(bus_in)
            self.buses_child[bus_in].add(bus_out)
            self.buses_parent[bus_out].add(bus_in)

    def query_lines(self):
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
        res = self.g.query(query_str)
        opendss = "!--- Generated Lines\n"
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
            opendss += line.get_opendss() + '\n'
        opendss += '\n\n'
        return opendss

    def query_loads(self):
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
        res = self.g.query(query_str)
        opendss = "!--- Generated Loads\n"
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
            opendss += load.get_opendss() + '\n'
        opendss += '\n\n'

        return opendss

    def query_linecode(self):
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
        res = self.g.query(query_str)
        opendss = "!--- Generated Linecodes\n"
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
            opendss += linecode.get_opendss() + '\n'
        opendss += '\n\n'
        return opendss

    def query_switches(self):
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
        res = self.g.query(query_str)
        opendss = "!--- Generated Switches\n"
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
            opendss += switch.get_opendss() +'\n'
        opendss += '\n\n'
        return opendss

    def query_regcontrol(self):
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
        res = self.g.query(query_str)
        opendss = "!--- Generated Reg Control\n"
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
            opendss += reg_control.get_opendss() + '\n'
            self.regcontrols[str(reg_control)] = reg_control
        opendss += '\n\n'
        return opendss

    def query_actuators(self):
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
                src = row['src'],
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
        res = self.g.query(query_str)
        sensors = []
        for row in res:
            if '1' in row['bus'] and row['bus1'] is not None:
                src = row['bus1']
            elif '2' in row['bus'] and row['bus2'] is not None:
                src = row['bus2']
            else:
                src = row['bus1']

            sensor = Sensor(
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

    def query_controllers(self):
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
        res = self.g.query(query_str)
        controllers = []
        for row in res:
            control = Controller(
                control = row['entity']
            )
            controllers.append(control)
        
        return controllers