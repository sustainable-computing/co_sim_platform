'''
@file    example_01.py
@author  Evandro de Souza
@date    2019.10.26  
@company University of Alberta - Computing Science
'''

from SimDSS import SimDSS
from LoadGenerator import LoadGenerator
import math

#--- Instatiate class to operate openDSS
#--- with inelastic load
#dssObj = SimDSS("examples/example_01.dss", "examples/example_01_nwl.csv", "examples/example_01_ilpq.csv")
#--- without inelastic load
dssObj = SimDSS("examples/example_01.dss", "examples/example_01_nwl.csv")

#-- Show the first circuit solution
print('Show initial parameters and solution:')
dssObj.showLoads()
dssObj.showVNodes()
dssObj.showIinout()
dssObj.showYMatrix()

#-- create object for load generator
objLoadGen = LoadGenerator("examples/example_01_nwl.csv",
                        PFLimInf   =  0.95,
                        PFLimSup   =  0.99,
                        LoadLimInf =  0.10,
                        LoadLimSup =  0.80,
                        AmpGain    =  3.25,
                        Freq       =  1./(100*1.25),
                        PhaseShift = math.pi)

#-- define the number of iteractions
itr = 100

#-- iteraction time
k = 0

#-- select an circuit, terminal and phase to monitor
cktElement = 'Line.LINE1'
cktTerminal = 2
cktPhase    = 2


print('')
print('-----------------------------')
print('Start simulation for', itr , 'steps')
print('-----------------------------')

#-- main simulation loop
while k < itr:
    #-- get a new sample of loads
    ePQ = objLoadGen.createLoads()
    
    #-- execute processing of the the new elastic load
    dssObj.setLoads(ePQ)

    #-- Extract circuit element values
    (V, I, P) = dssObj.getCktElementState(cktElement, cktTerminal, cktPhase)

    #-- Print V, I results after new circuit state is calculated
    print('Time:', '{:>3}'.format(k), 
          '  - Elem:', cktElement, 
          ' Term:', cktTerminal, 
          'Ph:',    cktPhase,
          ' - V = ',  
          "({0.real:15.4f} + {0.imag:15.4f}i)".format(V,4),
          'I = ',  
          "({0.real:15.4f} + {0.imag:15.4f}i)".format(I,4)          
          )    
   
    k += 1

#-- Show the final circuit solution
print('\nShow final parameters and solution:')
dssObj.showLoads()
dssObj.showVNodes()
dssObj.showIinout()
