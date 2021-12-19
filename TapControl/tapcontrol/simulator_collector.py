'''
Created on Jun. 01, 2019
Data collector to print results and save data in file for later analysis

@file    simulator_collector.py
@author  Evandro de Souza
@date    2019.06.01  
@version 0.1
@company University of Alberta - Computing Science
'''

import collections
import mosaik_api
import numpy as np
import warnings
import pandas as pd
import sys

META = {
	'api-version': '3.0',
	'type': 'event-based',
	'models': {
		'Monitor': {
			'public': True,
			'any_inputs': True,
			'params': ['verbose'],
			'attrs': [],
		},
	},
}


class Collector(mosaik_api.Simulator):
	def __init__(self):
		super().__init__(META)
		self.eid = None
		self.data = collections.defaultdict(lambda:collections.defaultdict(list))
		self.step_size = None
		self.time_list=[]


	def init(self, sid, time_resolution, eid_prefix=None, verbose=0, out_list = True, 
			h5_save=True, h5_panelname = None, h5_storename='collectorname'):
		if eid_prefix is not None:
			self.eid_prefix = eid_prefix
		self.sid          = sid
		self.verbose      = verbose
		self.out_list     = out_list
		self.h5_save      = h5_save
		self.h5_storename = h5_storename
		self.h5_panelname = h5_panelname

		return self.meta


	def create(self, num, model):
		if num > 1 or self.eid is not None:
			raise RuntimeError('Can only create one instance of Monitor.')
		self.eid = '%s%s' % (self.eid_prefix, num)
		if self.h5_panelname is None: self.h5_panelname = self.eid
		sys.stdout.flush()
		return [{'eid': self.eid, 'type': model}]

	
	def step(self, time, inputs, max_advance):
		if (self.verbose > 0):  print('Collector::step time ', time, ' Max Advance ', max_advance)
		if (self.verbose > 1): 	print('Collector::step inputs: ', inputs)
		data = inputs[self.eid]
		for attr, values in data.items():
			for src, value in values.items():
				if (value not in ['None',  None]):
					# For now, only using the latest data to plot and avoid overlapping data
					value = value[len(value)-1]
					if isinstance(value, np.float64) or isinstance(value, float):
						value = np.around(value, decimals = 6)
					if isinstance(value, str):
						value = int(value)
					self.data[src][attr].append(value)
#  				self.data[src][attr].append(value)
# 				else:
# 					self.data[src][attr].append(np.NaN)					
		self.time_list.append(time)
		sys.stdout.flush()
		
			
	def finalize(self):
		if self.out_list:
			print('Collected data:')
			for sim, sim_data in sorted(self.data.items()):
				print('- %s:' % sim)
				for attr, values in sorted(sim_data.items()):
					print(' - %s(%i): %s' % (attr, len(values), values))
		if self.h5_save:
			with warnings.catch_warnings():
				warnings.filterwarnings( 'ignore', category=Warning )
				store = pd.HDFStore(self.h5_storename)
				store[self.h5_panelname] = pd.DataFrame(self.data)
				store.close()
		sys.stdout.flush()


if __name__ == '__main__':
	mosaik_api.start_simulation(Collector())
