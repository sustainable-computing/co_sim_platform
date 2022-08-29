from xmlrpc.client import Fault
import opendssdirect as dss
import argparse
import random

parser = argparse.ArgumentParser(description="Generate labelled event data from a power topology")
parser.add_argument('--topo_file', help='The filename of the power topology to generate data from', required=True)
parser.add_argument('--seed', help='The seed to use for generating the initial load values', default=None)
topo_file = None
line_list = []
pmu_list = []

class PMU():
    def __init__(self, element, terminal=1):
        self.name = f"PMU_{element.replace('.','_')}"
        self.element = element
        self.terminal = terminal

    def init_opendss(self):
        dss.run_command(f'New Monitor.{self.name} element={self.element}')
    
    def show_data(self):
        dss.Monitors.Name(self.name)
        res_mat = dss.Monitors.AsMatrix()
        res_dict = {
            'TS':[],
            'V1':[],
            'VA1':[],
            'V2':[],
            'VA2':[],
            'V3':[],
            'VA3':[],
            'I1':[],
            'IA1':[],
            'I2':[],
            'IA2':[],
            'I3':[],
            'IA3':[],
        }
        for row in res_mat:
            res_dict['TS'].append(row[1])
            res_dict['V1'].append(row[2])
            res_dict['VA1'].append(row[3])
            res_dict['V2'].append(row[4])
            res_dict['VA2'].append(row[5])
            res_dict['V3'].append(row[6])
            res_dict['VA3'].append(row[7])
            res_dict['I1'].append(row[8])
            res_dict['IA1'].append(row[9])
            res_dict['I2'].append(row[10])
            res_dict['IA2'].append(row[11])
            res_dict['I3'].append(row[12])
            res_dict['IA3'].append(row[13])
        dss.Monitors.Show()
        return res_dict
    
class Event():
    def __init__(self, element):
        self.name = f'Event_{element}'
        self.element = element
    
    def init_event(self):
        raise NotImplementedError('You need to define a init_event method!')
    
    def enable_event(self):
        raise NotImplementedError('You need to define a enable_event method!')

    def disable_event(self):
        raise NotImplementedError('You need to define a disable_event method!')
        

class FaultEvent(Event):
    def __init__(self, bus, phases=[1,2,3]):
        super().__init__(f'Bus_{bus}')

        if len(phases) == 0:
            raise RuntimeError('phases cannot be empty')
        self.name = f'Fault_{bus}_{"".join(map(str,phases))}'
        self.bus = bus
        self.phases = phases

    def init_event(self):
        dss.run_command(f'New Fault.{self.name} bus1={self.bus}.{".".join(map(str,self.phases))} phases={len(self.phases)}')
        # Disable the fault
        self.disable_event()

    def enable_event(self):
        dss.run_command(f'{self.element}.enabled=True')

    def disable_event(self):
        dss.run_command(f'{self.element}.enabled=False')

class SwitchEvent(Event):
    def __init__(self, line, direction=1):
        """
        The direction determines what kind of switch event 
        direction=0 on to off
        direction=1 off to on
        """
        super().__init__(f'Switch_{line}')
        lines = dss.Lines.AllNames()
        if 'tie' not in line:
            raise RuntimeError(f"line: {line} is not a tie switch")
        if line not in lines:
            raise RuntimeError(f"line: {line} is not in circuit")
        if direction not in [0,1]:
            raise RuntimeError(f"direction: {direction} is not valid, should be either 0 or 1")
        self.name = f"Switch_{line}"
        self.line = line
        self.direction = direction

    def init_event(self):
        # On to Off
        if self.direction == 0:
            dss.run_command(f"Close object=Line.{self.line} term=1")
        # Off to On
        if self.direction == 1:
            dss.run_command(f"Open object=Line.{self.line} term=1")

    def enable_event(self):
        if self.direction == 0:
            dss.run_command(f"Open object=Line.{self.line} term=1")
        if self.direction == 1:
            dss.run_command(f"Close object=Line.{self.line} term=1")
    
    def disable_event(self):
        pass

class TapEvent(Event):
    def __init__(self, reg_control, direction=0, unit=1):
        super().__init__(f'Tap_{reg_control}')

        trafoList = dss.Transformers.AllNames()
        if reg_control.lower() not in trafoList:
            raise Exception('cktTrafo:', reg_control, ' not in the circuit')

        if direction not in [-1, 0, 1]:
            raise RuntimeError(f'tap value: {direction} not valid')

        self.name = f"Tap_{reg_control}"
        self.reg_control = reg_control
        self.direction = direction
        self.unit = unit

    def init_event(self):
        pass

    def enable_event(self):
        dss.Transformers.Name(self.reg_control)
        maxtap  = dss.Transformers.MaxTap()
        mintap  = dss.Transformers.MinTap()
        numtaps = dss.Transformers.NumTaps()
        curtap  = dss.Transformers.Tap()    
            
        newtap  = curtap + self.direction * ((maxtap - mintap)/numtaps) * self.unit        

        if(newtap > mintap and newtap < maxtap):        
            dss.Transformers.Tap(newtap)
            curtap  = dss.Transformers.Tap()

    def disable_event(self):
        pass

class GenEvent(Event):
    def __init__(self, generator, direction=0):
        super().__init__(f'Gen_{generator}')

        gen_list = dss.Generators.AllNames()
        if generator.lower() not in gen_list:
            raise RuntimeError(f"Generator: {generator} not in circuit")

        if direction not in [0,1]:
            raise RuntimeError(f"direction: {direction} is not valid, should be either 0 or 1")
            
        self.name = f"Gen_{generator}"
        self.generator = generator
        self.direction = direction

    def init_event(self):
        # On to Off
        if self.direction == 0:
            dss.run_command(f"Enable Generator.{self.generator}")
        # Off to On
        if self.direction == 1:
            dss.run_command(f"Disable Generator.{self.generator}")

    def enable_event(self):
        if self.direction == 0:
            dss.run_command(f"Disable Generator.{self.generator}")
        if self.direction == 1:
            dss.run_command(f"Enable Generator.{self.generator}")
    
    def disable_event(self):
        pass

class CapEvent(Event):
    def __init__(self, capacitor, direction=0):
        super().__init__(f"Cap_{capacitor}")

        cap_list = dss.Capacitors.AllNames()
        if capacitor.lower() not in cap_list:
            raise RuntimeError(f"capacitor: {capacitor} not in circuit")

        if direction not in [0,1]:
            raise RuntimeError(f"direction: {direction} is not valid, should be either 0 or 1")
        
        self.name = f"Cap_{capacitor}"
        self.capacitor = capacitor
        self.direction = direction

    def init_event(self):
        # On to Off
        if self.direction == 0:
            dss.run_command(f"Capacitor.{self.capacitor}.states=[1]")
        # Off to On
        if self.direction == 1:
            dss.run_command(f"Capacitor.{self.capacitor}.states=[0]")

    def enable_event(self):
        if self.direction == 0:
            dss.run_command(f"Capacitor.{self.capacitor}.states=[0]")
        if self.direction == 1:
            dss.run_command(f"Capacitor.{self.capacitor}.states=[1]")
    
    def disable_event(self):
        pass
        

def add_monitor(line_element=None):
    """
    Add a monitor object to monitor an line_element.
    If the line_element is not defined then it will add monitors to all lines
    """
    if line_element is None:
        for line in line_list:
            pmu = PMU(f'Line.{line}')
            pmu.init_opendss()
            pmu_list.append(pmu)
    elif line_element in line_list:
        pmu = PMU(f'Line.{line_element}')
        pmu.init_opendss()
        pmu_list.append(pmu)
    else:
        print(f'Error: Line.{line_element} is not in the topology')

def tear_down():
    """
    Tear down the simulator
    """
    global pmu_list
    pmu_list = []
    dss.run_command('Clear')

def set_up():
    """
    Setup the simulator for an event simulation
    """
    dss.run_command("Clear")
    dss.run_command(f'Compile {topo_file}')

def set_dynamics(step_size = 0.001):
    """
    Set the simulation mode to dynamic
    """
    dss.run_command(f'Set mode=dynamics h={step_size}')

def run_dynamics(steps=10):
    dss.run_command(f'Solve number={steps}')

def init_loads(min_kw=0.5, max_kw=2):
    """
    Initialize loads from a uniform randomized value between min_kw and max_kw
    """
    load_list = dss.Loads.AllNames()
    for load in load_list:
        value = random.uniform(min_kw, max_kw)
        dss.Loads.Name(load)
        dss.Loads.PF(0.95)
        dss.Loads.kW(value)

def get_randomize_event_duration(pre_event_limits=(25,51), curr_event_limits=(50,101), post_event_limits=(25,51)):
    """
    Can take in 3 pair of tuples that define the minimum and maximum number of steps 
    that can be uniformly chosen for the pre, current, and post event duration.
    """
    pre_event = random.randint(pre_event_limits[0],pre_event_limits[1])
    curr_event = random.randint(curr_event_limits[0],curr_event_limits[1])
    post_event = random.randint(post_event_limits[0],post_event_limits[1])
    return pre_event, curr_event, post_event

def main():
    # Read in command line arguments
    args = parser.parse_args()
    global topo_file
    topo_file = args.topo_file
    seed = args.seed
    # Set the seed for the random module
    random.seed(seed)

    # Clear and load the ontology file to be parsed 
    dss.run_command('Clear')
    dss.run_command(f'Compile {topo_file}')
    
    # Get all lines from the ontology
    global line_list 
    line_list = dss.Lines.AllNames()

    pmu_event_data_list = {}

    for idx in range(1):
        set_up()
        init_loads()
        add_monitor('4-5')


        # Add Events here
        # event = FaultEvent('2')
        # event = SwitchEvent('tie_9-15', 0)
        # event = TapEvent('Reg1',1,8)
        # event = GenEvent('Gen1',1)
        event = CapEvent('Cap1',0)
        event.init_event()


        # Solve the power network with the monitors and events attached to the network
        dss.run_command('Solve')
        # Set sim mode to dynamics with a step size of 0.001 (1ms)
        # Must be set after creating the faults
        set_dynamics()
        pre_event, curr_event, post_event = get_randomize_event_duration()
        print('Pre-event ', pre_event)
        run_dynamics(pre_event)
        event.enable_event()
        run_dynamics(curr_event)
        print('curr-event ', curr_event)
        event.disable_event()
        print('post-event ', post_event)
        run_dynamics(post_event)



        for pmu in pmu_list:
            pmu_data = pmu.show_data()
            pmu_name = pmu.name
            if pmu_name not in pmu_event_data_list.keys():
                pmu_event_data_list[pmu_name] = []
            pmu_event_data_list[pmu_name].append(pmu_data)


        tear_down()

    # print(pmu_event_data_list)

if __name__ == "__main__":
    main()
