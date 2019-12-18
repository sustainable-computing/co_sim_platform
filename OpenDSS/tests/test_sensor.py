import unittest

from SimDSS import SimDSS
import Sensor


class TestSensor(unittest.TestCase):
    dssObj = SimDSS("examples/example_01.dss", "examples/example_01_nwl.csv")
    

    #--- Sensor superclass

    cktElement  = 'Line.LINE1'
    cktTerminal = 'RCVBUS'
    cktPhase    = 'PHASE_1'

    objSensor = Sensor.Sensor('Sensor_01', 
                              1, 
                              dssObj, 
                              cktElement, 
                              0.1, 
                              1)

    objSmartmeter = Sensor.SmartMeter(cktTerminal, 
                                      cktPhase,
                                      'Smartmeter_01', 
                                      1, 
                                      dssObj, 
                                      cktElement, 
                                      0.1, 
                                      1)    

    def test_getLastValue(self):
        (value, time) = self.objSensor.getLastValue()
        self.assertEqual(value, None)
        self.assertEqual(time, None)
        

    #--- Phasor class

    cktTerminal = 'RCVBUS'
    cktPhase    = 'PHASE_1'
    objPhasor1 = Sensor.Phasor(cktTerminal, 
                              cktPhase,
                              'Phasor_01', 
                              1, 
                              dssObj, 
                              cktElement, 
                              0.1, 
                              0)
    
    def test_phasor_01(self):
        self.objPhasor1.updateValues(1)
        phasorMsg = self.objPhasor1.priorValue
        self.assertEqual(phasorMsg['VA'][0], 7517.248296295411)
        self.assertEqual(phasorMsg['VA'][1],   -0.5326051414173263)
        self.assertEqual(phasorMsg['IA'][0],   46.6767991467258)
        self.assertEqual(phasorMsg['IA'][1],   2.2914279686787746)
    
    cktPhase    = 'PHASE_2'
    objPhasor2 = Sensor.Phasor(cktTerminal, 
                              cktPhase,
                              'Phasor_02', 
                              1, 
                              dssObj, 
                              cktElement, 
                              0.1, 
                              0)    
        
    def test_phasor_02(self):
        self.objPhasor2.updateValues(1)
        phasorMsg = self.objPhasor2.priorValue        
        self.assertEqual(phasorMsg['VB'][0], 7517.2482970443)
        self.assertEqual(phasorMsg['VB'][1],   -2.627000243752136)
        self.assertEqual(phasorMsg['IB'][0],   46.67679914207967)
        self.assertEqual(phasorMsg['IB'][1],   0.19703286634394332)    

    cktPhase    = 'PHASE_3'
    objPhasor3 = Sensor.Phasor(cktTerminal, 
                              cktPhase,
                              'Phasor_03', 
                              1, 
                              dssObj, 
                              cktElement, 
                              0.1, 
                              0)    
        
    def test_phasor_03(self):
        self.objPhasor3.updateValues(1)
        phasorMsg = self.objPhasor3.priorValue        
        self.assertEqual(phasorMsg['VC'][0], 7517.248297039038)
        self.assertEqual(phasorMsg['VC'][1],    1.5617899609222368)
        self.assertEqual(phasorMsg['IC'][0],   46.67679914210987)
        self.assertEqual(phasorMsg['IC'][1],   -1.8973622361613016)
        
    cktPhase    = 'PHASE_123'
    objPhasor123 = Sensor.Phasor(cktTerminal, 
                              cktPhase,
                              'Phasor_04', 
                              1, 
                              dssObj, 
                              cktElement, 
                              0.1, 
                              0)
    
    def test_phasor_04(self):
        self.objPhasor123.updateValues(1)
        phasorMsg = self.objPhasor123.priorValue        
        self.assertEqual(phasorMsg['VA'][0], 7517.248296295411)
        self.assertEqual(phasorMsg['VA'][1],   -0.5326051414173263)
        self.assertEqual(phasorMsg['IA'][0],   46.6767991467258)
        self.assertEqual(phasorMsg['IA'][1],   2.2914279686787746)  
        self.assertEqual(phasorMsg['VB'][0], 7517.2482970443)
        self.assertEqual(phasorMsg['VB'][1],   -2.627000243752136)
        self.assertEqual(phasorMsg['IB'][0],   46.67679914207967)
        self.assertEqual(phasorMsg['IB'][1],   0.19703286634394332)                        
        self.assertEqual(phasorMsg['VC'][0], 7517.248297039038)
        self.assertEqual(phasorMsg['VC'][1],    1.5617899609222368)
        self.assertEqual(phasorMsg['IC'][0],   46.67679914210987)
        self.assertEqual(phasorMsg['IC'][1],   -1.8973622361613016)
        

    #--- SmatMeter class

    cktElement  = 'Load.LOAD1'
    cktTerminal = 'SNDBUS'
    cktPhase    = 'PHASE_1'
    objSmartmeter1 = Sensor.SmartMeter(cktTerminal, 
                              cktPhase,
                              'Smartmeter_01', 
                              1, 
                              dssObj, 
                              cktElement, 
                              0.1, 
                              0)

    def test_smartmeter_01(self):
        self.objSmartmeter1.updateValues(1)
        smartmeterMsg = self.objSmartmeter1.priorValue
        self.assertEqual(smartmeterMsg['VA'][0], 7517.248296295411)
        self.assertEqual(smartmeterMsg['VA'][1],   -0.5326051414173263)
        self.assertEqual(smartmeterMsg['PA'][0],  333.33402792149394)
        self.assertEqual(smartmeterMsg['PA'][1],  109.56522430366196)

    cktPhase    = 'PHASE_123'
    objSmartmeter123 = Sensor.SmartMeter(cktTerminal, 
                              cktPhase,
                              'SmartMeter_02', 
                              1, 
                              dssObj, 
                              cktElement, 
                              0.1, 
                              0)

    def test_smartmeter_02(self):
        self.objSmartmeter123.updateValues(1)
        smartmeterMsg = self.objSmartmeter123.priorValue        
        self.assertEqual(smartmeterMsg['VA'][0], 7517.248296295411)
        self.assertEqual(smartmeterMsg['VA'][1],   -0.5326051414173263)
        self.assertEqual(smartmeterMsg['PA'][0],  333.33402792149394)
        self.assertEqual(smartmeterMsg['PA'][1],  109.56522430366196)  
        self.assertEqual(smartmeterMsg['VB'][0], 7517.2482970443)
        self.assertEqual(smartmeterMsg['VB'][1],   -2.627000243752136)
        self.assertEqual(smartmeterMsg['PB'][0],  333.3340279214997)
        self.assertEqual(smartmeterMsg['PB'][1],  109.56522430368236)                        
        self.assertEqual(smartmeterMsg['VC'][0], 7517.248297039038)
        self.assertEqual(smartmeterMsg['VC'][1],    1.5617899609222368)
        self.assertEqual(smartmeterMsg['PC'][0],  333.3340279214919)
        self.assertEqual(smartmeterMsg['PC'][1],  109.56522430367765)


    #--- Prober class

    cktElement  = 'Line.LINE1'
    cktTerminal = 'RCVBUS'
    cktPhase    = 'PHASE_1'
    cktProperty = 'VA'
    
    objProber1 = Sensor.Prober(cktTerminal, 
                                      cktPhase,
                                      cktProperty,
                                      'Prober_01', 
                                      1, 
                                      dssObj, 
                                      cktElement, 
                                      0.1, 
                                      1)
     
    def test_prober_01(self):
        self.objProber1.updateValues(1)
        proberMsg = self.objProber1.priorValue
        self.assertEqual(proberMsg[0], 7517.248296295411)
    
    cktProperty = 'PC'
    objProber2 = Sensor.Prober(cktTerminal, 
                                      cktPhase,
                                      cktProperty,
                                      'Prober_02', 
                                      1, 
                                      dssObj, 
                                      cktElement, 
                                      0.1, 
                                      1)
    
    def test_prober_02(self):
        self.objProber2.updateValues(1)
        proberMsg = self.objProber2.priorValue
        #--- Compare Q from phase C (3)
        self.assertEqual(proberMsg[1], 109.56228961176494)


                    
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()




    
