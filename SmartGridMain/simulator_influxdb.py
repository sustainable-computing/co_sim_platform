from datetime import datetime, timezone

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS


import collections
import mosaik_api
import numpy as np
import warnings
import pandas as pd
import sys

META = {
	'type': 'event-based',
	'models': {
		'InfluxDB_Connection': {
			'public': True,
			'any_inputs': True,
			'params': ['verbose','url','token','org','bucket'],
			'attrs': [],
		},
	},
}

class InfluxDB(mosaik_api.Simulator):
	def __init__(self):
		super().__init__(META)
		self.eid_prefix = 'InfluxDB_'
		self.eid = None

    # We don't use the sid nor the time_resolution
	def init(self, sid, time_resolution, url, token, org, bucket, verbose=0):
		self.verbose      = verbose
		self.sid = sid
        # You can generate an API token from the "API Tokens Tab" in the UI
		self.url = url
		self.token = token
		self.org = org
		self.bucket = bucket
		self.start_time_ms = datetime.utcnow().timestamp()*1000
		self.sequence = []
		return self.meta


	def create(self, num, model):
		if num > 1 or self.eid is not None:
			raise RuntimeError('Can only create one instance of InfluxDB_Connection.')
		self.eid = '%s%s' % (self.eid_prefix, num)
		sys.stdout.flush()
		# Create a InfluxDB client to connect to the database
		self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
		self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
		return [{'eid': self.eid, 'type': model}]

	
	def step(self, time, inputs, max_advance):
		if (self.verbose > 0):  print('InfluxDB::step time ', time, ' Max Advance ', max_advance)
		if (self.verbose > 1): 	print('InfluxDB::step inputs: ', inputs)
		data = inputs[self.eid]
		# Assume that it's only values and times
		values = data['v']
		times = data['t']
		for equipment, value in values.items():
			equipment_time = times[equipment][0]
			if value not in ['None', None]:
				# For now, only using the latest data to plot and avoid overlapping data
				value = value[len(value)-1]
				if isinstance(value, np.float64) or isinstance(value, float):
					value = np.around(value, decimals = 6)
				if isinstance(value, str):
					value = int(value)
				# print("Equipment:",equipment, "Value:", value, "Time", equipment_time)
				timestamp = datetime.fromtimestamp((self.start_time_ms + equipment_time)/1000.0)
				data_point = Point('my_measurement')\
								  .tag('equipment', equipment)\
								  .field('output',float(value))\
								  .time(timestamp, WritePrecision.MS)
				self.sequence.append(data_point)
		# If the number of entries exceed 1000 then we write to influx and clear
		if len(self.sequence) > 500:
			self.write_api.write(self.bucket,self.org,self.sequence)
			self.sequence = []
		sys.stdout.flush()
			
	def finalize(self):
		# Write out the remaining data points to influx
		if len(self.sequence) > 0:
			self.write_api.write(self.bucket,self.org,self.sequence)

		self.client.close()
		sys.stdout.flush()


if __name__ == '__main__':
	mosaik_api.start_simulation(InfluxDB())