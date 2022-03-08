class Transformer():
    def __init__(self, **kwargs):
        self.name = kwargs['trans'].split('#')[1] if kwargs['trans'].startswith("http://") else kwargs['trans'] 
        self.bus_primary = kwargs['bus_primary']
        self.kva = kwargs['kva']
        self.connection_primary = kwargs['connection_primary'],
        self.connection_secondary = kwargs['connection_secondary'],
        self.kv_primary = kwargs['kv_primary'],
        self.kv_secondary = kwargs['kv_secondary'],
        self.percent_r = kwargs['percent_r']

    def __str__(self):
        return self.name

class Bus():
    def __init__(self, **kwargs):
        self.name = kwargs['bus'].split('#')[1] if kwargs['bus'].startswith("http://") else kwargs['bus']
        self.x = kwargs['x']
        self.y = kwargs['y']
    def __str__(self):
        return self.name

class Line():
    def __init__(self,  **kwargs):
        self.name = kwargs['line'].split('#')[1] if kwargs['line'].startswith("http://") else kwargs['line']
        self.length = kwargs['length']
        self.length_unit = kwargs['length_unit']
        self.nodes_primary = kwargs['nodes_primary']
        self.nodes_secondary = kwargs['nodes_secondary']
        self.num_phases = kwargs['num_phases']
    
    def __str__(self):
        return self.name