'''
Created on Jul. 23, 2019
Data analysis of the simulation results.

@file    analysis.py
@author  Evandro de Souza
@date    2019.07.23  
@version 0.1
@company University of Alberta - Computing Science
'''

import matplotlib.pyplot as plt
import pandas as pd
import sys


phasor = 'Phasor_1_1'
smartmeter = 'Smartmeter_6_100061'
estimator = 'Estimator_1'

#--- select dataset file
if len(sys.argv) > 1:
    storename = sys.argv[1]
else:
    storename = 'data/CollectorStore_Small.hd5'

#--- Load data
store = pd.HDFStore(storename)
df = store['Collector']
store.close()

#--- select sets
df_sets = []
df_names = []
max_t = 0
for col in df:
    df_sets.append(df[col])
    df_names.append(col)
    if (max_t < max(df[col]['t'])): max_t = max(df[col]['t'])


fig, axs = plt.subplots(7)
fig.set_size_inches(11, 18.5)
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
plt.xlabel('Time (ms)')

for i in range(len(df_sets)):
    if ((df_names[i]).find(phasor) != -1):
        #--- Plot Voltage Magnitude
        axs[0].set_title(df_names[i] + " - Voltage Magnitude -  3 Phases")
        VA = []
        VB = []
        VC = []
        keys = (df_sets[i]['v'][0]).keys()
        for j in range(len(df_sets[i]['v'])):
            VA.append(df_sets[i]['v'][j]['VA'][0])
            VB.append(df_sets[i]['v'][j]['VB'][0])
            VC.append(df_sets[i]['v'][j]['VC'][0])
        axs[0].plot(df_sets[i]['t'], VA, '.')
        axs[0].plot(df_sets[i]['t'], VB, '.')
        axs[0].plot(df_sets[i]['t'], VC, '.')
        axs[0].set_xlim(-5, max_t+5)
        axs[0].grid(b=True, which='both', axis='both')
        #--- Plot Voltage Angle
        axs[1].set_title(df_names[i] + " - Voltage Angle -  3 Phases")
        VA = []
        VB = []
        VC = []
        keys = (df_sets[i]['v'][0]).keys()
        for j in range(len(df_sets[i]['v'])):
            VA.append(df_sets[i]['v'][j]['VA'][1])
            VB.append(df_sets[i]['v'][j]['VB'][1])
            VC.append(df_sets[i]['v'][j]['VC'][1])
        axs[1].plot(df_sets[i]['t'], VA, '.')
        axs[1].plot(df_sets[i]['t'], VB, '.')
        axs[1].plot(df_sets[i]['t'], VC, '.')
        axs[1].set_xlim(-5, max_t+5)
        axs[1].grid(b=True, which='both', axis='both')        
        
        #--- Plot Current Magnitude
        axs[2].set_title(df_names[i] + " - Current Magnitude -  3 Phases")
        IA = []
        IB = []
        IC = []
        keys = (df_sets[i]['v'][0]).keys()
        for j in range(len(df_sets[i]['v'])):
            IA.append(df_sets[i]['v'][j]['IA'][0])
            IB.append(df_sets[i]['v'][j]['IB'][0])
            IC.append(df_sets[i]['v'][j]['IC'][0])
        axs[2].plot(df_sets[i]['t'], IA, '.')
        axs[2].plot(df_sets[i]['t'], IB, '.')
        axs[2].plot(df_sets[i]['t'], IC, '.')
        axs[2].set_xlim(-5, max_t+5)
        axs[2].grid(b=True, which='both', axis='both')        
        
        #--- Plot Current Angle
        axs[3].set_title(df_names[i] + " - Current Angle -  3 Phases")
        IA = []
        IB = []
        IC = []
        keys = (df_sets[i]['v'][0]).keys()
        for j in range(len(df_sets[i]['v'])):
            IA.append(df_sets[i]['v'][j]['IA'][1])
            IB.append(df_sets[i]['v'][j]['IB'][1])
            IC.append(df_sets[i]['v'][j]['IC'][1])
        axs[3].plot(df_sets[i]['t'], IA, '.')
        axs[3].plot(df_sets[i]['t'], IB, '.')
        axs[3].plot(df_sets[i]['t'], IC, '.')
        axs[3].set_xlim(-5, max_t+5)
        axs[3].grid(b=True, which='both', axis='both')       
    
    if ((df_names[i]).find(smartmeter) != -1):
        #--- Plot Real Power
        gr_title = df_names[i] + " - SM Real Power P - Phases:"
        PA = []
        PB = []
        PC = []
        keys = (df_sets[i]['v'][0]).keys()
        for j in range(len(df_sets[i]['v'])):
            if 'SPA' in (df_sets[i]['v'][j]).keys():
                PA.append(df_sets[i]['v'][j]['SPA'])
            if 'SPB' in (df_sets[i]['v'][j]).keys():   
                PB.append(df_sets[i]['v'][j]['SPB'])
            if 'SPC' in (df_sets[i]['v'][j]).keys():
                PC.append(df_sets[i]['v'][j]['SPC'])
        if(len(df_sets[i]['t']) == len(PA)):
            if 'SPA' in (df_sets[i]['v'][j]).keys():
                axs[4].plot(df_sets[i]['t'], PA, '.')
        if(len(df_sets[i]['t']) == len(PB)):        
            if 'SPB' in (df_sets[i]['v'][j]).keys():    
                axs[4].plot(df_sets[i]['t'], PB, '.')
        if(len(df_sets[i]['t']) == len(PC)):
            if 'SPC' in (df_sets[i]['v'][j]).keys():
                axs[4].plot(df_sets[i]['t'], PC, '.')
            
        if (len(PA) > 0):
            gr_title = gr_title + ' A'
        if (len(PB) > 0):
            gr_title = gr_title + ' B'
        if (len(PC) > 0):
            gr_title = gr_title + ' C'                
        axs[4].set_title(gr_title)    
        axs[4].set_xlim(-5, max_t+5)
        axs[4].grid(b=True, which='both', axis='both') 
               
        #--- Plot Voltage Magnitude
        gr_title = df_names[i] + " - SM Voltage Magnitude - Phases:"
        VA = []
        VB = []
        VC = []
        keys = (df_sets[i]['v'][0]).keys()
        for j in range(len(df_sets[i]['v'])):
            if 'VA' in (df_sets[i]['v'][j]).keys():
                VA.append(df_sets[i]['v'][j]['VA'])
            if 'VB' in (df_sets[i]['v'][j]).keys():    
                VB.append(df_sets[i]['v'][j]['VB'])
            if 'VC' in (df_sets[i]['v'][j]).keys():    
                VC.append(df_sets[i]['v'][j]['VC'])
        if 'VA' in (df_sets[i]['v'][j]).keys():
            axs[5].plot(df_sets[i]['t'], VA, '.')
        if 'VB' in (df_sets[i]['v'][j]).keys():
            axs[5].plot(df_sets[i]['t'], VB, '.')
        if 'VC' in (df_sets[i]['v'][j]).keys():
            axs[5].plot(df_sets[i]['t'], VC, '.')
        
        if (len(VA) > 0):
            gr_title = gr_title + ' A'
        if (len(VB) > 0):
            gr_title = gr_title + ' B'
        if (len(VC) > 0):
            gr_title = gr_title + ' C'  
        axs[5].set_title(gr_title)
        axs[5].set_xlim(-5, max_t+5)
        axs[5].grid(b=True, which='both', axis='both')        

    #--- Plot Amount of received messages in aperiod of time
    if ((df_names[i]).find(estimator) != -1):
        axs[6].set_title(df_names[i])
        axs[6].plot(df_sets[i]['t'], df_sets[i]['v'], '.')
        axs[6].set_xlim(-5, max_t+5)
        axs[6].grid(b=True, which='both', axis='both')
        

plt.tight_layout()
fig.savefig('data/Monitor_Small.png', dpi=100)