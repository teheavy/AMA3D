#!/usr/bin/python
import MySQLdb
import pprint
import imp # for dynamically loading py codes
import datetime
import time
import csv # for parsing csv files
import smtplib # for sending email messages
from email.mime.text import MIMEText

VERSION = "1.0.0"
AGENT_ID
DIE = False #
ADMINFILE # file storing admin info
MYEMAIL # email account of AMA3D
PARAM # the data this agent is using right now

#connect to database with connectinfo
def connect_db(dbinfopath):

	try:
		file = open
		db = MySQLdb.connect(host=localhost, user, password, dbname)
	except Exception, err:
		mins = 0
		while mins < 5
			db = MySQLdb.connect(host=localhost, user, password, dbname)
			time.sleep(60)
			mins++

		record_log_activity(str(err))
		notify_admin(str(err))

		# Rollback in case there is any error
		bd.rollback()
		return 1

#send an email including the error msg to admin(s)
def notify_admin(error):
	# assume admin info are stored in a file in the following format
	# Admin Name\tAdmin Email\tAdmin Cell \tOther Info\n
	msg = MIMEText(error);
	msg['Subject'] = "AMA3D - Error"
	msg['From'] = MYEMAIL	

	file = open(ADMINFILE, "r")
	parsed = csv.reader(file, delimiter="\t")
	listAdmin = list(parsed)
	count = 0

	for line in parsed:
		count++
		admin = listAdmin[count][1] 
		msg['To'] = admin
		msg = "Dear " + listAdmin[count][0] + ",\n" + msg + "\n" + "----AMA3D"
		# sending message through localhost
		s = smtplib.SMTP('localhost')
		s.sendmail(MYEMAIL, admin, msg.as_string())
		s.quit() 

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
			cursor.execute("""SELECT (id, idTaskResource, Parameters, IsLast) \
					FROM TriggeringCondition WHERE Status = open""")
			results = cursor.fetchall
			idTC = results[0][0]
			idTaskResource = results[0][1]
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

			#stores parameters for to be used by load_methods
			#we won't pass param directly to load_methods
			#so that the agent can spawn more agents with preloaded methods
			#and just update param
			global PARAM = param	
			#load and execute methods
			load_methods(idTaskResource)
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
def load_methods(idTR):
	
	try: 
	    sqlText = """SELECT Codepath FROM TaskResource WHERE idTaskResource == %d""",idTR
	    cursor.execute(sqlText)
	    code_path = cursor.fetchall		
	    code_dir = os.path.dirname(code_path)
	    file = open(code_path, 'rb')
	    module= imp.load_source(md5.new(code_path).hexdigest(), code_path, file)
            file.close()	    
       except ImportError, x:
        traceback.print_exc(file = sys.stderr)
        raise

#We need to know the methods then run them by module.<method name()>
# for example mod=load_methods(idTR) then mod.play()
	

#terminate task
def terminate_task():

#write activity summary to log file
# input: 
# 	str activity: contains the activity description to be added to log file.
#	int agentID: the unique agent identifier
def record_log_activity(activity, agentID):

	timestamp = get_date_time(time.localtime())

	log_activity = open("log_file.txt", "a+")  # creates a file object called log_file.txt
	log_activity.write(timestamp "\n" + agentID + ": " + activity + "\n")
	log_activity.close()

# helper function for record_log_activty. converts the struct time.localtime()
# to workable date and time string. input: list with the date and time info
def get_date_time(datetime):

	date = str(datetime[0])+ "-" + str(datetime[1]) + "-" + str(datetime[2])
	time = str(datetime[3])+ "-" + str(datetime[4]) + "-" + str(datetime[5])
	return (date+','+time)

#agent terminates itself
def terminate_self():

	try:
		cursor = db.cursor()
		sql1 = "SELECT Status FROM Agent WHERE AGENT_ID = %d", AGENT_ID
		cursor.execute(sql1)
		status = cursors.fetchall()[0]

		if status == 0:
			sql2 = "DELETE FROM Agent WHERE AGENT_ID = %d", AGENT_ID
			cursor.execute(sql1)
		return true

	except Exception as err:
		record_log_activity(str(err))
		return false 

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
		global AGENT_ID = results[0]
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
	
