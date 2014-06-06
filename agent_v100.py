#TODO
#-Write ERROR Number Handbook



#Version 1.0.0
#Spawn linearly: After spawning, the parent agent picks up a task. 

#!/usr/bin/python
import MySQLdb
import subprocess # for running commands from command line
import pprint
import os.path
import traceback
import datetime
import time
import csv # for parsing csv files
import smtplib # for sending email messages
from email.mime.text import MIMEText

import AMA_globals as G # importing global variables

#connect to database with connectinfo
def connect_db(user, password, dbname):
	"""
	(str, int, str) -> int
	Given user information, try to connect database.
	Return 0 when success, if the first connection is not successful, try connect 5 times, if failed, return 1 and notify user. 
	Input arguments:
	user: your username
	password: your password
	dbname: the database we are going to log in
	"""
	try:
		file = open
		DB = G.DB
		DB = MySQLdb.connect(G.HOST, user, password, dbname)
		return 0
	except Exception, err:
		mins = 0
		while mins < 5:
			DB = MySQLdb.connect(G.HOST, user, password, dbname)
			time.sleep(60)
			mins+=1

		record_log_activity(str(err))
		notify_admin(str(err))

		# Rollback in case there is any error
		DB.rollback()
		return 1


def notify_admin(msg):
	"""
	(str) -> ()
	Send an email including the message string to the admin(s).
	
	Keyword arguments:
	msg -- the message to be sent
	"""
	
	ADMINFILE = G.ADMINFILE
	MYEMAIL = G.MYEMAIL
	
	# assume admin info are stored in a file in the following format
	# Admin Name\tAdmin Email\tAdmin Cell \tOther Info\n
	msg = MIMEText(msg);
	msg['Subject'] = "AMA3D - Error"
	msg['From'] = MYEMAIL	

	file = open(ADMINFILE, "r")
	parsed = csv.reader(file, delimiter="\t")
	listAdmin = list(parsed)
	count = 0

	for line in parsed:
		count+=1
		admin = listAdmin[count][1] 
		msg['To'] = admin
		msg = "Dear " + listAdmin[count][0] + ",\n" + msg + "\n" + "All the best, \nAMA3D"
		# sending message through localhost
		s = smtplib.SMTP('localhost')
		s.sendmail(MYEMAIL, admin, msg.as_string())
		s.quit() 


def decide_next(seconds, threshold):
	"""
	(int, int) -> ()
	Decide what to do next (brain of the agent).
	
	Keyword arguments:
	time -- how long, in seconds, the agent will sleep when there is nothing to do
	threshold -- an integer defining "busy" (spawn if and only if the number of TC is greater than this integer)
	"""
	
	count = 0
	
	while not die():
		
		AGENT_ID = G.AGENT_ID
		DB = G.DB
		cursor = DB.cursor()
		
		try:
			
			#check for number of TC
			cursor.execute("""SELECT count(*) FROM TriggeringCondition WHERE Status = open""")
			results = cursor.fetchall
		except Exception as err:
			notify_admin(str(err))
			terminate_self()
			
		if results[0][0] == 0: #no open TC => idle
			count += 1
			if count > 5 and not isOnly(): 
				#if idling more than five times and this is not the last agent: terminate
				terminate_self(False)
			else:
				time.sleep(seconds)
		else:
			if results[0][0] > threshold: #number of open TC greater than threshold => spawn one agent
				
				machineID = find_resources()
				
				while machineID == -1: #while no machine available
					time.sleep(3)
					spawn(machineID)
				
				#if spawn fails, notify admin (done by spawn) and continue the work.
					
			#0 < number of TC < threshold => work (note: impossible to have negative number of TC)
		
			try:
				#pick the first open task 
				#Future implementation: can make agent smarter by choosing a task by type
				cursor.execute("""SELECT (id, idTaskResource, Parameters, IsLast) \
						FROM TriggeringCondition WHERE Status = open""")
				results = cursor.fetchall
			except Exception as err:
				notify_admin(str(err))
				terminate_self()
			
			idTC = results[0][0]
			idTaskResource = results[0][1]
			IsLast = results[0][3]

			#globally stores parameters for to be used by load_methods
			#so that the agent can spawn more agents with preloaded methods
			#and just update PARAM
			PARAM = G.PARAM
			PARAM = results[0][2]
			
			try: 
				#update TriggeringCondition table
				cursor.execute("""INSERT INTO TriggeringCondition(idAgent, Status) \
						VALUES (%d, 'in_progress') WHERE id = %d"""  %  (AGENT_ID, idTC))
				#update Agent table
				cursor.execute("""UPDATE Agent SET \
						StartTime = %s \
						Status = 'busy' \
						Priority = %d \
						WHERE id = %d"""  %  (datetime.datetime.now(), calculate_priority(idTC), AGENT_ID))
				DB.commit()
			except Exception as err:
				DB.rollback()
				notify_admin(str(err))
				terminate_self()
			
			try:
				#load and execute methods
				status = load_methods(idTaskResource)
				
				#update priority
				cursor.execute("""UPDATE Agent SET \
						Priority = %d \
						WHERE id = %d"""  %  (101, AGENT_ID))
				DB.commit()
			except Exception as err:
				DB.rollback()
				notify_admin(str(err))
				terminate_self()
			
			try:
				if status == 0:
					# successfully completed the task
					# remove TC and write to log file
					# addition of new TC will be taken care of by program executed
					cursor.execute("""DELETE FROM TriggeringCondition \
						WHERE id = %d"""  %  (idTC))
				
				else:
					# fail
					# reset TC 
						cursor.execute("""UPDATE TriggeringCondition SET \
						Status = 'open' \
						WHERE id = %d"""  %  (idTC))
						record_log_activity("Executing method failed: %d, error number: %d." % (idTC, status), G.MACHINE_ID)
					# if task failed, reset TC to open and log the errors
					# limit the number of times to attempt the TC?
				DB.commit()
			except Exception as err:
				DB.rollback()
				notify_admin(str(err))
				terminate_self()

	#if a die signal is present: self terminate
	terminate_self()

def calculate_priority(idTC):
	"""
	(int) -> (int)
	Calculate a priority number for current task.
	Return priority (an integer in [0,100], 0 being the highest priority.)
	"""	
	#dummy function
	return 0

#spawn another agent: 
#create an agent by using this agent as template	
def spawn(machineID):
	"""
	(int) -> (int)
	Spawn a new agent on the machine represented by the given machineID.
	"""
	
	DB = G.DB
	cursor = DB.cursor()
	
	try:
		machine_info = cursor.execute("""SELECT * FROM Machines WHERE idMachine == %d""" % G.MACHINE_ID).fetchall()[0]

		port = machine_info['Port']
		agent_path = machine_info['Path'] + "/agent.py" #software folder
		host_addr = machine_info['User'] + "@" + machine_info['Host'] #user@host

		# Find a way to connect remote computer using password
		if port == "":
			status = subprocess.call(['ssh', host_addr, 'python', agent_path], shell=True)
		else:
			status = subprocess.call(['ssh', '-p', port, host_addr, 'python', agent_path], shell=True)

		return status
	except:
		record_log_activity("spawn: db failure or unsuccessful remote subprocess call.", G.DB.MACHINE_ID, True)
		return 4444	
		
#update machine availabilities
#helper function for find_resources
def update_machine():
	"""
	() -> (int)
	For every machine in the Machine table, update the machine information. \
	Return 0 upon success, 1 otherwise.
	"""
	
	DB = G.DB
	cursor = DB.cursor()
	
	try:
		machine_info = cursor.execute("""SELECT * FROM Machines""").fetchall()

		
		
		for i in range(0, len(machine_info)):
			#ssh into the machine
			port = machine_info[i]['Port']
			agent_path = machine_info[i]['Path'] + "/agent.py" #software folder
			host_addr = machine_info[i]['User'] + "@" + machine_info[i]['Host'] #user@host
	
			#find FreeMem 
			if port == "":
				output = subprocess.check_output(['ssh', host_addr, 'cat /proc/meminfo | grep "MemFree:" | sed \'s/\s\+/\*/g\' | cut -d "*" -f 2'], shell=True)
			else:
				output = subprocess.check_output(['ssh', '-p', port, host_addr, 'cat /proc/meminfo | grep "MemFree:" | sed \'s/\s\+/\*/g\' | cut -d "*" -f 2'], shell=True)
			
			
			cursor.execute("""UPDATE Machines SET FreeMem = %d WHERE idMachine = %d""" % (int(output), int(machine_info[i]['idMachine'])))
			DB.commit()
		return 0
	except:
		record_log_activity("update_machine: db failure or unsuccessful remote subprocess call.", G.DB.MACHINE_ID, True)
		return 4444

#return a list of available machines by their machineID 
#in order of non-increasing availablity (most free first)
def find_resources():
	"""
	() -> (int)
	Return the machineID of the "best" machine, -1 if no machine is free or 4444 if db failure.
	"""
	#In version 1.0.0, best machine = the machine with the biggest FreeMem
	update_machine()
	
	DB = G.DB
	cursor = DB.cursor()
	
	idBest = -1
	
	try:
		result = cursor.execute("""SELECT idMachine, FreeMem FROM Machines ORDER BY FreeMem DESC""").fetchall()
		if result[0]["FreeMem"] != 0:
			idBest = result[0]["idMachine"]
		return idBest
		
	except:
		record_log_activity("find_resources: db failure.", G.DB.MACHINE_ID, True)
		return 4444
	
	
#dynamically load the task-specific codes
def load_methods(idTR):
	""" 
	(int) -> (int)
	Dynamically load a module that its file path is known.
    
	Keyword arguments:
	idTR -- id number of TaskResource table
	"""
	DB = G.DB		
	cursor = DB.cursor()

	try:
   		# retrieve basepath where AMA3D is installed
   		base_path = cursor.execute("""SELECT Path FROM Machines WHERE\
		idMachine == %d""" % G.MACHINE_ID).fetchall()[0][0]
		
   		#retrive the relative path and the program in which the module has been written
   		stuff = cursor.execute("""SELECT Codepath, Program FROM TaskResource WHERE\
		idTaskResource == %d""" % idTR).fetchall()
		
		rel_path = stuff[0]["Codepath"]
		program = stuff[0]["Program"]
		
		code_path = base_path + "/" + rel_path
		
		# execute the program
		status = subprocess.call([program, code_path, G.PARAM], shell=True)
		
		return status
	
	except: 
		record_log_activity("load_methods: db failure or unsuccessful subprocess call.", G.DB.MACHINE_ID, True)
		return 4444



def record_log_activity(activity, machineID, notify):
	"""
	(str, int, boolea~) -> ()
	Write activity summary of the agent to a 'LogTable' that is stored in the Database.
	This feature was added to handle the concurrency situation in which multiple agents 
	are writing to the log table at a time.
	
	Keyword arguments:
	str activity: contains the activity description to be added to log file. 
	              It could be an error message as well.
	              Error format: <function name: possible causes of failure.> 
	int agentID: the unique agent identifier
	"""
	

	try:
		DB = G.DB
		cur = DB.cursor()
		timestamp = time.asctime()
		AGENT_ID = G.AGENT_ID

		# Insert and update LogTable in the database which has 4 attributes:
		# AgentId      MachineId    TimeStamp    Activity
		# -------      ---------    --------     --------
		# -------      ---------    --------     --------

		sql = """INSERT INTO LogTable(AgentId, MachineID, TimeStamp, Activity) \
		         VALUES ( %s, %s, %s, %s)"""  % (AGENT_ID, str(machineID), timestamp, str(activity))

		cur.execute(sql)
		DB.commit()
		return True
		if notify == True:
			notify_admin(activity + "\nAgent ID: " + AGENT_ID + "\nMachine ID: " + machineID + "\nAMA3D Time: " + timestamp)
			
	except Exception as err:
		notify_admin(str(err))
		return False


#agent terminates itself
def terminate_self():
	'''
	() -> boolean
	Check if current agent has finish its job.
	If finished, delete the agent from status table and return true, otherwise return false.
	'''
	try:
		AGENT_ID = G.AGENT_ID
		DB = G.DB
		cursor = DB.cursor()
		sql1 = "SELECT Status FROM Agent WHERE AGENT_ID = %d"  %  AGENT_ID
		cursor.execute(sql1)
		status = cursors.fetchall()[0]

		if status == 0:
			sql2 = "DELETE FROM Agent WHERE AGENT_ID = %d"  %  AGENT_ID
			cursor.execute(sql2)
			return true
		DB.commit()
		DB.close()
	except Exception as err:
		DB.rollback()
		DB.close()
		record_log_activity(str(err)) #try this error msg 
		return false 


def register():
	"""() -> boolean
        Register agent information to the database. Update global variable AGENT_ID
        from database. Return the completion status.

        : param:  none
        : effects: global AGENT_ID is set to autoincremented AGENT table id
        : returns: True for successful database insert, False otherwise.
        """
	DB = G.DB
	cursor = DB.cursor()

	registerTime = datetime.datetime.now()	
	
	try: 
		cursor.execute("""INSERT INTO Agent \ 
		(RegisterTime, StartTime, Status, NumTaskDone) \
		VALUES (%s, 'not_yet_started', 1, 0)"""  %  (registerTime))
		AGENT_ID = G.AGENT_ID
		AGENT_ID = DB.insert_id()
		DB.commit() #might not need this?
		return True
	except Exception as err:
		record_log_activity(str(err)) #try this error msg 
		return False

#die
def die():
	"""
	()->()
	Listen for die signal and return true iff die signal is present.
	
	:param: none
	
	"""
	G.DIE = True


#acting as the main function
def essehozaibashsei():

	#configure some variables here? maybe better to pass in to main?
	time
	threshold
	# Setup a email account for agent.
	# Add a file in database for agent account.
	# Ask for the agent account file path.
	if connect_db(filepath): #TO-DO: add codes to open, read and parse file in connect_db or here?
		register()
		#check DIE here instead of in decide_next?
		#while !DIE
		decide_next(time, threshold)
	
	# Setup the email account, ask user for Adminfile location.
	# Add code for listen for die signal from user.

# agent.py's assumption/ preconditions	
# db set up. Including tables with the following info:
	# a list of available machines (uername + passwords + host + abs path 
	# of where the AMA3D folder is saved)
# files on machines (a AMA3D directory with agent.py... etc)

if __name__ == '__main__':
	essehozaibashsei()
	
