#!/usr/bin/python
import MySQLdb
import pprint
import imp #for dynamically loading py codes
import datetime
import time

VERSION
AGENT_ID
DIE = False 


#connect to database with connectinfo
def connect_db(connectinf):
	# TODO: add codes here

#send an email including the error msg to admin(s)
def notify_admin(error):
	# TODO: add codes here

#decide what to do next
def decide_next(time, threshold):

	while DIE == False:
		
		#not sure if we need to check if agent is busy.... ?
		#if busy == True:
		#	sleep(time)
		#else:
		cursor = db.cursor()

		#check for number of TC
		cursor.execute("""SELECT count(*) FROM TriggeringCondition WHERE Status = open""")
		results = cursor.fetchall
		if results[0][0] == 0: #idle
			time.sleep(time)
		else if results[0][0] > 0: #spawn one agent
			freeMachines = find_resources()
			spawn(freeMachines[0])
		else: #work

			#pick the first open task 
			#(can make agent smarter by choosing a task by type)
			cursor.execute("""SELECT (id, idTaskType, Parameters, IsLast) \
					FROM TriggeringCondition WHERE Status = open""")
			results = cursor.fetchall
			idTC = results[0][0]
			idTaskType = results[0][1]
			param = results[0][2]
			IsLast = results[0][3]

			#update TriggeringCondition table
			cursor.execute("""INSERT INTO TriggeringCondition(idAgent, Status) \
					VALUES (%d, 'in_progress') WHERE id = %d""", (AGENT_ID, idTC)
			#update Agent table
			cursor.execut("""UPDATE Agent SET \
					StartTime = %s \
					Status = 'busy' \
					WHERE id = %d""", (datetime.datetime.now(), AGENT_ID))

			#load methods and data
			load_methods(idTaskType)
			load_data(param)
			#busy = True
	
	terminate_self()
	

#spawn another agent: 
#create an agent by using this agent as template	
def spawn(machineID):
	#return int

#return a list of available machines by their machineID 
#in order of non-increasing availablity (most free first)
def find_resources():
	#return list of string or vector

#dynamically load the task-specific codes
def load_methods(TC):
	#return int as status

#dynamically load the arguments for the task-specific codes
def load_data(TC):
	#return int status

#terminate task
def terminate_task():

#write activity summary to log file
def record_log_activity():
	#return status

#agent terminates itself
def terminate_self():

#register agent information to database
def register():
	rval = False
	cursor = db.cursor()
	registerTime = datetime.datetime.now()	
	sql1 = """SELECT max(id) FROM Agent"""
	sql2 = """INSERT INTO Agent \ 
		(RegisterTime, StartTime, Status, NumTaskDone) \
		VALUES (%s, 'not_yet_started', 1, 0)""", (registerTime)
	try: 
		cursor.execute(sql1)
		results = cursor.fetchall()
		AGENT_ID = results[0]
		try:
			cursor.execute(sql)
			db.commit()
			rval = True
		except:
			db.rollback()	
			rval = False
	except:
		 rval = False
	return rval

#hibernate
def hibernate():

#die
def die():
	DIE = True

#acting as the main function
def essehozaibashsei():
