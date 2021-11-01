import mosaik_api

META = {
    'api_version': '3.0',
    'type': 'event-based',
    'models': {
        'Transporter': {
            'public': True,
            'params': ['src', 'dst'],
            'attrs': ['v', 't'],
        },
    },
}
class Transporter:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self.m_events = []

    def step(self, time):
        events = []
        if not self.m_events:
            # print("MockSim::"+self.src+'-'+self.dst+": No Messages to deliver!")
            return events

        expected_delivery = self.m_events[0]['time'] + self.m_events[0]['delay']
        if time == expected_delivery:
            # print("MockSim::"+self.src+'-'+self.dst+": ready ", self.m_events[0])
            #--- create list of messages ready for delivery
            events.append(self.m_events.pop(0))

        return events

    def insert_message(self, time, value_v, value_t, delay):
        #--- Do not insert events in the past (or duplicates)
        # if time > value_t:
        #     # print("Delayed/Duplicate v:", value_v, " t: ", value_t," at: ", time, ' ')
        #     return -1

        new_event = {}
        new_event['time'] = time
        new_event['delay'] = delay
        new_event['v'] = value_v
        new_event['t'] = value_t

        self.m_events.append(new_event)
        # print("MockSim::"+self.src+'-'+self.dst+": new event", new_event)

        return self.m_events[0]['time']+self.m_events[0]['delay']

class PktNetSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.instances = {}

    def init(self, sid, time_resolution, eid_prefix, verbose):
        self.eid_prefix = eid_prefix
        self.verbose = verbose
        self.sid = sid
        self.data = {}

        if (self.verbose > 0): print('simulator_commock::init', self.sid)

        return self.meta

    def create(self, num, model, src, dst):
        
        # dictionary list of created carrier models
        entities = []
        
        # Only one model is always created, so no need for loops
        if(model == "Transporter"):
            eid = self.eid_prefix + str(src) + '-' + str(dst)
            if(self.verbose > 0):
                print("MockSim::create() Creating new model: ", eid)

            self.instances[eid] = Transporter(src, dst)
            entities.append({'eid': eid, 'type': model})

        return entities

    def step(self, time, inputs, max_advance):
        if self.verbose > 0 : print("MockSim::step() time args = ", time)
        if self.verbose > 1 : print("MockSim::INPUT: ", inputs)
        if self.verbose > 1 : print("MockSim::Max Advance time: ", max_advance)
        
        data = {}
        next_step = max_advance+1
        
        #--- Step all the transporters to the current time and pass messages
        #--- which are ready for delivery. Message delays must be > 0
        for eid, transporter in self.instances.items():
            events = transporter.step(time)
            if(not events): continue
            data[eid] = {}
            # For now only one deliverable data is sent as message
            data[eid]['t'] = events[0]['t']
            data[eid]['v'] = events[0]['v']

        self.data = data

        # Calculate next step from received messages
        for mock_eid, attrs in inputs.items():
            voltage_dict = attrs.get('v', {})
            time_dict = attrs.get('t', {})
            value_v = list(voltage_dict.values())[0]
            value_t = list(time_dict.values())[0]

            transporter = self.instances[mock_eid]
            
            # Implement Transporter Specific delay here
            if transporter.src == '611':  delay = 65
            else:   delay = 33

            #-- Insert message into queue of transporter only once
            next_delivery = transporter.insert_message(time=time, delay=delay, value_v=value_v, value_t=value_t)
            
            if(next_delivery != -1):    next_step = min(next_step, next_delivery)
        
        if self.verbose > 1 : print("MockSim::Next Step time = ", next_step)
        if self.verbose > 2 : print("MockSim::step DATA = ", self.data)
        
        if(next_step < max_advance+1): return next_step
            
    def get_data(self, outputs):
        if(self.verbose > 0): print("MockSim::get_data()")
        if(self.verbose > 1): print("MockSim::asked output = ", outputs)

        data = {}
        for comm_eid, attrs in outputs.items():
            for attr in attrs:
                if attr != 'v' and attr != 't':
                    raise ValueError('Unknown output attribute "@s"' % attr)
                if comm_eid in self.data:
                    data.setdefault(comm_eid, {})[attr] = self.data[comm_eid][attr]

        if(self.verbose > 1): print("MockSim::returned output = ", data)
        
        return data

    def main():
        return mosaik_api.start_simulation(PktNetSim())


    if __name__ == '__main__':
        main()