import re
class Transformer():
    def __init__(self, **kwargs):
        self.name = kwargs['trans'].split('#')[1] if kwargs['trans'].startswith("http://") else kwargs['trans'] 
        self.name = self.name.split('_')[1]
        self.num_phases = kwargs['num_phases']
        self.XHL = kwargs['XHL']
        self.XHT = kwargs['XHT']
        self.XLT = kwargs['XLT']
        self.bus_primary = kwargs['bus_primary'].split('#')[1].split('_')[1]
        self.bus_secondary = kwargs['bus_secondary'].split('#')[1].split('_')[1]
        self.kva = kwargs['kva']
        self.connection_primary = kwargs['connection_primary']
        self.connection_secondary = kwargs['connection_secondary']
        self.kv_primary = kwargs['kv_primary']
        self.kv_secondary = kwargs['kv_secondary']
        self.percent_r = kwargs['percent_r']

    def get_opendss(self):
        opendss = f"New Transformer.{self.name} "
        opendss += f"Phases={self.num_phases} "
        opendss += "Windings=2 "
        opendss += f"XHL={self.XHL}\n"
        opendss += f"~ wdg=1 bus={self.bus_primary} "
        opendss += f"conn={self.connection_primary} "
        opendss += f"kv={self.kv_primary} "
        opendss += f"kva={self.kva} "
        opendss += f"%r={self.percent_r} "
        if self.XHT is not None:
            opendss += f"XHT={self.XHT}\n"
        else:
            opendss += '\n'
        opendss += f"~ wdg=2 bus={self.bus_secondary} "
        opendss += f"conn={self.connection_secondary} "
        opendss += f"kv={self.kv_secondary} "
        opendss += f"kva={self.kva} "
        opendss += f"%r={self.percent_r} "
        if self.XLT is not None:
            opendss += f"XLT={self.XLT}"

        return opendss


    def __str__(self):
        return self.name

class Bus():
    def __init__(self, **kwargs):
        self.name = kwargs['bus'].split('#')[1] if kwargs['bus'].startswith("http://") else kwargs['bus']
        self.x = kwargs['x']
        self.y = kwargs['y']
    def __str__(self):
        return self.name

class Capacitor():
    def __init__(self, **kwargs):
        self.name = kwargs['capacitor'].split('#')[1].split('_')[1]
        self.bus1 = kwargs['bus1'].split('#')[1].split('_')[1]
        if kwargs['nodes_primary'] is not None:
            self.nodes_primary = '.' + kwargs['nodes_primary']
        else:
            self.nodes_primary = ''
        self.num_phases = kwargs['num_phases']
        self.kvar = kwargs['kwar']
        self.kv = kwargs['kv']
    
    def get_opendss(self):
        opendss = f"New Capacitor.{self.name} "
        opendss += f"Bus1={self.bus1}{self.nodes_primary} "
        opendss += f"phases={self.num_phases} "
        opendss += f"kVAR={self.kvar} "
        opendss += f"kV={self.kv}"

        return opendss
        
    def __str__(self):
        return self.name

class Line():
    def __init__(self,  **kwargs):
        self.name = kwargs['line'].split('#')[1] if kwargs['line'].startswith("http://") else kwargs['line']
        self.name = self.name.split('_')[1]
        self.bus1 = kwargs['bus1'].split('#')[1]
        self.bus1 = self.bus1.split('_')[1]
        self.bus2 = kwargs['bus2'].split('#')[1]
        self.bus2 = self.bus2.split('_')[1]
        self.linecode = kwargs['linecode'].split('#')[1].split('_')[1]
        self.length = kwargs['length']
        self.length_unit = kwargs['length_unit']
        self.nodes_primary = kwargs['nodes_primary'].strip().replace(' ','.')
        self.nodes_secondary = kwargs['nodes_secondary'].strip().replace(' ','.')
        self.num_phases = kwargs['num_phases']
    
    def get_opendss(self):
        opendss = f"New Line.{self.name} "
        opendss += f"Phases={self.num_phases} "
        opendss += f"Bus1={self.bus1}.{self.nodes_primary} "
        opendss += f"Bus2={self.bus2}.{self.nodes_secondary} "
        opendss += f"LineCode={self.linecode} "
        opendss += f"Length={self.length} "
        opendss += f"units={self.length_unit}"

        return opendss

    def __str__(self):
        return self.name

class LineCode():
    def __init__(self, **kwargs):
        self.name = kwargs['linecode'].split('#')[1].split('_')[1]
        self.freq = kwargs['freq']
        self.num_phases = kwargs['num_phases']
        self.rmat = kwargs['rmat']
        self.xmat = kwargs['xmat']
        self.unit = kwargs['unit']
        self.cmat = kwargs['cmat']

    def get_opendss(self):
        opendss = f"New linecode.{self.name} "
        opendss += f"nphases={self.num_phases} "
        opendss += f"BaseFreq={self.freq}\n"
        opendss += f"~ rmatrix = {self.rmat}\n"
        opendss += f"~ xmatrix = {self.xmat}\n"
        if self.cmat is not None:
            opendss += f"~ Cmatrix = {self.cmat}\n"
        opendss += f"~ units={self.unit}"
    
        return opendss

    def __str__(self):
        return self.name

class Load():
    def __init__(self, **kwargs):
        self.name = kwargs['load'].split('#')[1].split('_')[1]
        self.bus1 = kwargs['bus1'].split('#')[1].split('_')[1]
        self.conn = kwargs['conn']
        self.kv_primary = kwargs['kv_primary']
        self.kw = kwargs['kw']
        self.kvar = kwargs['kvar']
        self.model = kwargs['model']
        self.nodes_primary = kwargs['nodes_primary'].replace(' ','.')
        if kwargs['nodes_secondary'] is not None:
            self.nodes_secondary = kwargs['nodes_secondary'].replace(' ','.')
        else:
            self.nodes_secondary = None
        self.num_phases = kwargs['num_phases']

    def get_opendss(self):
        opendss = f"New Load.{self.name}"
        if self.nodes_secondary is not None:
            opendss += f".{self.nodes_secondary} "
        else:
            opendss += ' '
        opendss += f"Bus1={self.bus1}.{self.nodes_primary} "
        opendss += f"Phases={self.num_phases} "
        opendss += f"Conn={self.conn} "
        opendss += f"Model={self.model} "
        opendss += f"kV={self.kv_primary} "
        opendss += f"kW={self.kw} "
        opendss += f"kvar={self.kvar}"

        return opendss

    def __str__(self):
        return self.name

class Capacitor():
    def __init__(self, **kwargs):
        self.name = kwargs['cap'].split('#')[1].split('_')[1]
        self.bus1 = kwargs['bus'].split('#')[1].split('_')[1]
        if kwargs['nodes_primary'] is not None:
            self.nodes_primary = kwargs['nodes_primary'].strip().replace(' ','.')
        else:
            self.nodes_primary = None
        self.num_phases = kwargs['num_phases']
        self.kvar = kwargs['kvar']
        self.kv = kwargs['kv']

    def get_opendss(self):
        opendss = f"New Capacitor.{self.name} "
        opendss += f"Bus1={self.bus1}"
        if self.nodes_primary is not None:
            opendss += f".{self.nodes_primary} "
        else:
            opendss += " "
        opendss += f"phases={self.num_phases} "
        opendss += f"KVAR={self.kvar} "
        opendss += f"kV={self.kv}"
        return opendss 

    def __str__(self):
        return self.name

class Switch():
    def __init__(self, **kwargs):
        self.name = kwargs['switch'].split('#')[1].split('_')[1]
        self.bus1 = kwargs['bus1'].split('#')[1].split('_')[1]
        self.bus2 = kwargs['bus2'].split('#')[1].split('_')[1]
        self.num_phases = kwargs['num_phases']
        self.c0 = kwargs['c0']
        self.c1 = kwargs['x1']
        self.r0 = kwargs['r0']
        self.r1 = kwargs['r1']
        self.x0 = kwargs['x0']
        self.x1 = kwargs['x1']

    def get_opendss(self):
        opendss_str = f"New Line.{self.name} "
        opendss_str += f"Phases={self.num_phases} "
        opendss_str += f"Bus1={self.bus1} "
        opendss_str += f"Bus2={self.bus2} "
        opendss_str += "Switch=y "
        opendss_str += f"c0={self.c0} c1={self.c1} "
        opendss_str += f"r0={self.r0} r1={self.r1} "
        opendss_str += f"x0={self.x0} x1={self.x1} "
        return opendss_str

    def __str__(self):
        return self.name

class VoltageRegulator():
    """
    A Voltage Regular is a transformer with regcontrol as a component.
    An instance of VoltageRegulator will produce a new transformer and a new regcontrol
    """

    def __init__(self, **kwargs):
        self.name = kwargs['regcontrol'].split('#')[1].split('_')[1]
        self.bus1 = kwargs['bus1'].split('#')[1].split('_')[1]
        self.bus2 = kwargs['bus2'].split('#')[1].split('_')[1]
        self.num_phases = kwargs['num_phases']
        self.bank = kwargs['bank']
        self.XHL = kwargs['XHL']
        self.kva = kwargs['kva']
        self.primary_kv = kwargs['primary_kv']
        self.nodes_primary = kwargs['nodes_primary'].strip().replace(' ','.')
        self.tap_primary = kwargs['tap_primary']
        self.secondary_kv = kwargs['secondary_kv']
        self.nodes_secondary = kwargs['nodes_secondary'].strip().replace(' ','.')
        self.tap_secondary = kwargs['tap_secondary']
        self.num_taps = kwargs['num_taps']
        self.max_tap = kwargs['max_tap']
        self.min_tap = kwargs['min_tap']
        self.load_loss = kwargs['load_loss']
        self.vreg = kwargs['vreg']
        self.band = kwargs['band'] 
        self.ptratio = kwargs['ptratio']
        self.ctprim = kwargs['ctprim']
        self.R = kwargs['R']
        self.X = kwargs['X']
    
    def __str__(self):
        return self.name

    def get_opendss(self):
        opendss_str = f"New Transformer.{self.name} "
        opendss_str += f"phases={self.num_phases} "
        opendss_str += f"bank={self.bank} "
        opendss_str += f"XHL={self.XHL} "
        opendss_str += f"kVAs=[{self.kva} {self.kva}] "
        opendss_str += f"NumTaps={self.num_taps} "
        opendss_str += f"maxtap={self.max_tap} "
        opendss_str += f"mintap={self.min_tap}\n"
        opendss_str += f"~ Buses=[{self.bus1}.{self.nodes_primary} {self.bus2}.{self.nodes_secondary}] "
        opendss_str += f"kVs=[{self.primary_kv} {self.secondary_kv}] "
        opendss_str += f"%LoadLoss={self.load_loss}\n"
        # The winding is always 2
        opendss_str += f"new regcontrol.{self.name} transformer={self.name} winding=2 "
        opendss_str += f"vreg={self.vreg} "
        opendss_str += f"band={self.band} "
        opendss_str += f"ptratio={self.ptratio} "
        opendss_str += f"ctprim={self.ctprim} "
        opendss_str += f"R={self.R} "
        opendss_str += f"X={self.X} "
        return opendss_str

class Generator():
    def __init__(self, **kwargs):
        self.name = kwargs['gen'].split('#')[1].split('_')[1]
        self.basekv = kwargs['kv_sec']
        self.bus1 = kwargs['bus1'].split('#')[1].split('_')[1]
        self.pu = kwargs['pu']
        self.num_phases = kwargs['num_phases']
        self.MVAsc1 = kwargs['MVAsc1']
        self.MVAsc3 = kwargs['MVAsc3']
        self.angle = kwargs['angle']
        

    def __str__(self):
        return self.name

    def get_opendss(self):
        opendss = f"new circuit.{self.name}\n"
        opendss += f"~ basekv={self.basekv} "
        opendss += f"pu={self.pu} "
        opendss += f"phases={self.num_phases} "
        opendss += f"bus1={self.bus1}\n"
        opendss += f"~ Angle={self.angle}\n"
        opendss += f"~ MVAsc3={self.MVAsc3} MVAsc1={self.MVAsc1}"
        return opendss