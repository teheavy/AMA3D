#TODO
	# Setup a email account for agent.


#Version 1.0.0
# agent.py's assumption/ preconditions	
# db set up. Including tables with the following info:
	# a list of available machines (uername + passwords + host + abs path 
	# of where the AMA3D folder is saved)
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
                G.DB = MySQLdb.connect(host="142.150.40.189", user=user, passwd=password, db=dbname)
                return 0
        except Exception, err:
                mins = 0
                while mins < 5:
                        DB = MySQLdb.connect(host="142.150.40.189", user=user, passwd=password, db=dbname)
                        time.sleep(60)
                        mins+=1

                record_log_activity(str(err))
                notify_admin(str(err))

                # Rollback in case there is any error
                DB.rollback()
                return 1


def notify_admin(m):
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

        with open(ADMINFILE, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")
            for line in reader:
                msg = MIMEText("Dear " + line[0] + ",\n" + m  + "\n" + "All the best, \nAMA3D Happy Agent (ID: " + G.AGENT_ID + " )")
                msg['Subject'] = "AMA3D - Error"
                msg['From'] = MYEMAIL
                msg['To'] = line[1]

                print msg.as_string()
                # sending message through localhost
                s = smtplib.SMTP('localhost')
                s.sendmail(MYEMAIL, line[1], msg.as_string())
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
                cursor = DB.cursor(MySQLdb.cursors.DictCursor)

                try:

                        #check for number of TC
                        cursor.execute("""SELECT count(*) as numTC FROM TriggeringCondition WHERE Status ='open'""")
                        numTC = cursor.fetchall()[0]['numTC']
                        print "numTC is: " + str(numTC)

                        if numTC == 0: #no open TC => idle
                                count += 1
                                if count > 5 and not isOnly():
                                        print "count greater than 5, killing agent."
                                        #if idling more than five times and this is not the last agent: terminate
                                        terminate_self(False)
                                else:
                                        time.sleep(seconds)
                                        print "trying again in " + str(seconds) + " seconds."
                        else:
                                if numTC > threshold: #number of open TC greater than threshold => spawn one agent
                                        print "There are: " + str(numTC) + " triggering conditions."
                                        print "Busy threshold is: " + str(threshold)
                                        machineID = find_resources()

                                        while machineID == -1: #while no machine available
                                                time.sleep(3)
                                                s = spawn(machineID)
                                                print "spawn status: " + str(s)
                                                print "Trying to spawn agent at: machine " + str(machineID)

                                        #if spawn fails, notify admin (done by spawn) and continue the work.


                        #pick the first open task 
                        #Future implementation: can make agent smarter by choosing a task by type
                        cursor.execute("""SELECT (id, idTaskResource, Parameters, IsLast) \
                                                FROM TriggeringCondition WHERE Status ='open'""")
                        results = cursor.fetchall()[0]

                        idTC = results['id']
                        idTaskResource = results['idTaskResource']
                        IsLast = results['IsLast']
                        print "idTC: " + str(idTC)
                        print "idTaskResource: " + str(idTaskResource)
                        print "IsLast: " + str(IsLast)

                        #globally stores parameters for to be used by load_methods
                        #so that the agent can spawn more agents with preloaded methods
                        #and just update PARAM
                        G.PARAM = results['Parameters']
                        print str(G.PARAM)

                        #update TriggeringCondition table
                        cursor.execute("""INSERT INTO TriggeringCondition(idAgent, Status) \
                                                VALUES (%d, 'in_progress') WHERE id = %d"""  %  (AGENT_ID, idTC))
                        #update Agent table
                        cursor.execute("""UPDATE Agent SET \
                                                StartTime = %s \
                                                Status = 'busy' \
                                                Priority = %d \
                                                WHERE id = %d"""  %  (datetime.datetime.now(), calculate_priority(idTC), AGENT_ID))

                        #load and execute methods
                        status = load_methods(idTaskResource)

                        #update priority
                        cursor.execute("""UPDATE Agent SET \
                                                Priority = %d \
                                                WHERE id = %d"""  %  (calculate_priority(idTC), AGENT_ID))

                        if status == 0:
                                # successfully completed the task
                                # remove TC and write to log file
                                # addition of new TC will be taken care of by program executed
                                cursor.execute("""DELETE FROM TriggeringCondition \
                                                WHERE id = %d"""  %  (idTC))
                                record_log_activity("Task %d sucessfully completed." %idTC, G.MACHINE_ID, False)
                        else:
                                # fail
                                # reset TC 
                                cursor.execute("""UPDATE TriggeringCondition SET \
                                                Status = 'open' \
                                                WHERE id = %d"""  %  (idTC))
                                record_log_activity("Executing method failed: %d, error number: %d." % (idTC, status), G.MACHINE_ID, True)
                                # if task failed, reset TC to open and log the errors
                                # limit the number of times to attempt the TC?

                        DB.commit()
                except Exception as err:
                        DB.rollback()
                        record_log_activity("decide_next: failure. " + str(err), G.MACHINE_ID, True)
                        terminate_self(False)
       

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
        cursor = DB.cursor(MySQLdb.cursors.DictCursor)

        try:
                cursor.execute("""SELECT * FROM Machines WHERE idMachine = %d""" % machineID)
                machine_info = cursor.fetchall()[0]

                port = machine_info['Port']
                agent_path = machine_info['Path'] + "/agent.py" #software folder
                host_addr = machine_info['User'] + "@" + machine_info['Host'] #user@host

                # Find a way to connect remote computer using password
                if port == "":
                        status = subprocess.call(['ssh', str(host_addr), 'python', str(agent_path)])
                else:
                        status = subprocess.call(['ssh', '-p', str(port), str(host_addr), 'python', str(agent_path)])

                return status
        except Exception as err:
                record_log_activity("spawn: db failure or unsuccessful remote subprocess call. " + str(err), G.MACHINE_ID, True)
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
        cursor = DB.cursor(MySQLdb.cursors.DictCursor)

        try:
                cursor.execute("""SELECT * FROM Machines""")
                machine_info = cursor.fetchall()


                for i in range(0, len(machine_info)):
                        #ssh into the machine
                        port = machine_info[i]["Port"]
                        #agent_path = machine_info[i]['Path'] + "/agent.py" #software folder
                        host_addr = machine_info[i]["User"] + "@" + machine_info[i]["Host"] #user@host

                        #find FreeMem   
                        if port == "":
                                output = subprocess.check_output(['ssh', str(host_addr), 'cat /proc/meminfo | grep "MemFree:" | sed \'s/\s\+/\*/g\' | cut -d "*" -f 2'])
                        else:
                                output = subprocess.check_output(['ssh', '-p', str(port), str(host_addr), 'cat /proc/meminfo | grep "MemFree:" | sed \'s/\s\+/\*/g\' | cut -d "*" -f 2'])
                        pport = "-p %s " % port

                        #do NOT use shell=True... but why???! (We spent a decade debugging this!!!!! Grrrrrrrrrr.... Hate)

                        cursor.execute("""UPDATE Machines SET FreeMem = %d WHERE idMachine = %d""" % (int(output), int(machine_info[i]['idMachine'])))
                DB.commit()
                        #can restructure codes and factor out duplications
                        #can also add in codes to update info about machine's CPU.... or not

                return 0
        except Exception as err:
                record_log_activity("update_machine: db failure or unsuccessful remote subprocess call." + str(err), G.MACHINE_ID, True)
                print str(err)
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
        cursor = DB.cursor(MySQLdb.cursors.DictCursor)

        idBest = -1

        try:
                cursor.execute("""SELECT idMachine, FreeMem FROM Machines ORDER BY FreeMem DESC""")
                result = cursor.fetchall()

                if result[0]["FreeMem"] != 0:
                        idBest = result[0]["idMachine"]

                return idBest

        except Exception as err:
                record_log_activity("find_resources: db failure. " + str(err), G.MACHINE_ID, True)
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
        cursor = DB.cursor(MySQLdb.cursors.DictCursor)

        try:
                # retrieve basepath where AMA3D is installed
                cursor.execute("""SELECT Path FROM Machines WHERE\
                idMachine = %d""" % G.MACHINE_ID)
                base_path = cursor.fetchall()[0]["Path"]

                #retrive the relative path and the program in which the module has been written
                cursor.execute("""SELECT Codepath, Program FROM TaskResource WHERE\
                id = %d""" % idTR)
                stuff = cursor.fetchall()

                rel_path = stuff[0]["Codepath"]
                program = stuff[0]["Program"]

                code_path = base_path + "/" + rel_path

                # execute the program
                status = subprocess.call([program, code_path, G.PARAM])

                return status

        except Exception as err:
                record_log_activity("load_methods: db failure or unsuccessful subprocess call. " + str(err), G.MACHINE_ID, True)
                return 4444



def record_log_activity(activity, machineID, notify):
        """
        (str, int, boolea~) -> ()
        Write activity summary of the agent to table 'LogActivity' in database AMA3D.
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
                cursor = DB.cursor()
                time = datetime.datetime.now()

                # Insert and update LogActivity in the database which has 5 attributes:
                # id    AgentID      MachineID    TimeStamp    Activity
                # --    -------      ---------    --------     --------
                # --    -------      ---------    --------     --------

                # replace single quotes that breaks our query
                # note: might want take care of other metacharacters to prevent SQL injections          
                activity = re.sub('\'', '\"',activity)

                cursor.execute("""INSERT INTO LogActivity(AgentID, MachineID, TimeStamp, Activity) \
                         VALUES (%s, %s, '%s', '%s')"""  % (G.AGENT_ID, machineID, time, activity))

                DB.commit()

                if notify == True:
                        notify_admin(activity + "\nAgent ID: " + str(G.AGENT_ID) + "\nMachine ID: " + str(machineID) + "\nAMA3D Time: " + str(time))

                return True

        except Exception as err:
                notify_admin("record_log_activity: " + str(err))
                return False


#agent terminates itself
def terminate_self(wait):
        '''
        (boolean) -> ()
        Input: whether to wait for agent to finish its task or not.
        If wait == true, check if current agent has finish its job.
                if finished, delete the agent from status table and exit the program.
        If wait == false, force quit the program. 
        '''
        try:
                DB = G.DB
                cursor = DB.cursor()
                if wait == True:
                        status = [1]
                        while status is not None and status[0] == 1:
                                cursor.execute( "SELECT Status FROM Agent WHERE id = %s"  %  G.AGENT_ID)
                                # If Status = 0
                                # the agent is not processing any task
                                # terminate it
                                # else, wait
                                status = cursor.fetchone()
                                time.sleep(2)

                cursor.execute( "DELETE FROM Agent WHERE id = %s"  %  G.AGENT_ID)
                DB.commit()
                DB.close()
                exit(1)
        except Exception as err:
                DB.rollback()
                DB.close()
                record_log_activity("terminate_self: " + str(err), G.MACHINE_ID, True) #try this error msg 
                exit(1)
                # just kill the agent.... Admin might have to manually fix the db. Too bad so sad~~~~ :(


def register():
        """() -> boolean
        Register agent information to the database. Update global variable AGENT_ID
        from database. Return the completion status.

        : param: none
        : effects: global AGENT_ID is set to autoincremented AGENT table id
        : returns: True for successful database insert, False otherwise.
        """
        DB = G.DB
        cursor = DB.cursor()

        registerTime = datetime.datetime.now()

        try:
                cursor.execute("""INSERT INTO Agent \
                (RegisterTime, Status, NumTaskDone, Priority) \
                VALUES ('%s', 1, 0, 0)""" % registerTime) #registertime and starttime are set by default
                AGENT_ID = G.AGENT_ID
                AGENT_ID = DB.insert_id()
                DB.commit() #might not need this?
                return True
        except Exception as err:
        	notify_admin(str(err))
                #print "register error"
                return False


def die():
        """
        ()->(boolean)
        Listen for die signal and return true iff die signal is present.
        :param: none
        """
        #if 
        #return True
        #else
        return False



#acting as the main function
def essehozaibashsei():

	# May change these to global variables
	TIME = 2
	THRESHOLD = 4

	# Parse File
	file = open("Account", "r")
	parsed = file.readline().split()
	
	if connect_db(parsed[0], parsed[1], parsed[2]): 
		register()
		#check DIE here instead of in decide_next?
		#while !DIE
		decide_next(TIME, THRESHOLD)
	
	# Setup the email account, ask user for Adminfile location.
	# Add code for listen for die signal from user

# files on machines (a AMA3D directory with agent.py... etc)

if __name__ == '__main__':
	essehozaibashsei()
	
