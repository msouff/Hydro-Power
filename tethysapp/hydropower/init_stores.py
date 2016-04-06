# Put your persistent store initializer functions in here
import os
from .model import engine, SessionMaker, Base, FlowDurationData

def init_hydropower_db(first_time):
	"""
	Initializer for the flooded addresses database
	"""
	# Create tables
	Base.metadata.create_all(engine)

	# Initial data
	if first_time:
		app_dir = os.path.dirname(__file__)
		data_path = os.path.join(app_dir, 'data', 'FlowDurationData.csv')

		lines = []

		with open(data_path, 'r') as f:
			lines = f.read().splitlines()

		lines.pop(0)

		session = SessionMaker()

		for line in lines:
			row = line.split(',')

			flow_duration_row = FlowDurationData(
				site=row[0],
				percent=row[1],
				flow=row[2],
				units=row[3]
			)

			session.add(flow_duration_row)

		session.commit()
		session.close()
