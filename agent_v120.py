#Version 1.2.0
# agent.py's assumption/ preconditions	
# db set up. Including tables with the following info:
	# a list of available machines (uername + passwords + host + abs path 
	# of where the AMA3D folder is saved)
# Spawn linearly: After spawning, the parent agent picks up a task. 
# When loading method, directly read stdout from the script


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
import re
import AMA_globals as G # importing global variables
import threading
import sys
import traceback
import multiprocessing


#connect to database with connectinfo
def connect_db(host, user, password, dbname):
        """
        (str, str, int, str) -> int
        Given user information, try to connect database.
        Return 0 when success, if the first connection is not successful, try connect 5 times, if failed, return 1 and notify user. 
        Input arguments:
        user: your username
        password: your password
        dbname: the database we are going to log in
        """
        try:
                G.DB = MySQLdb.connect(host=host, user=user, passwd=password, db=dbname)
                print "Database Connected!"
                return 0
        except Exception, err:
                mins = 0
                while mins < 5:
                        DB = MySQLdb.connect(host=host, user=user, passwd=password, db=dbname)
                        time.sleep(60)
                        mins+=1
                print "Fail to connect to database"
                record_log_activity(str(err))
                notify_admin(str(err))
                print traceback.format_exc()
                # Rollback in case there is any error
                DB.rollback()
                return 1


def register(username):
        """(str) -> boolean
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
                # Update the machine info in agent file
                cursor.execute("""SELECT idMachine FROM Machines WHERE\
                User = '%s'""" % username)
                G.MACHINE_ID = cursor.fetchall()[0][0]
                print "I'm on machine #" + str(G.MACHINE_ID)

                cursor.execute("""INSERT INTO Agent \
                (Machine, RegisterTime, Status, NumTaskDone, Priority) \
                VALUES ('%s', '%s', 0, 0, 0)""" % (username, registerTime)) #registertime and starttime are set by default
                G.AGENT_ID = DB.insert_id()

                DB.commit() #might not need this?
                print "Happy Agent " + str(G.AGENT_ID) + " is here now!\n"
                return True
        except Exception as err:
                print traceback.format_exc()
                notify_admin("register: " + str(err))
                #print "register error"
                return False


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

                DB = G.DB
                cursor = DB.cursor(MySQLdb.cursors.DictCursor)

                try:

                        #check for number of TC
                        cursor.execute("""SELECT count(*) as numTC FROM TriggeringCondition WHERE Status = 0""")
                        numTC = cursor.fetchall()[0]['numTC']

                        cursor.execute("""SELECT count(*) as numFreeAG FROM Agent WHERE Status = 0""")
                        numFreeAG = cursor.fetchall()[0]['numFreeAG']

                        cursor.execute("""SELECT count(*) as numAG FROM Agent""")
                        numAG = cursor.fetchall()[0]['numAG']

                        # cursor.execute("""show variables like 'max_connections'""") 
                        # max_connections = cursor.fetchone()['Value'] / 2 # Since each task may use the connections as well
                        max_connections = 20
                        
                        if numTC == 0: #no open TC => idle
                                count += 1
                                if count > 5 and numAG > 1:
                                        print "count greater than 5, killing agent."
                                        #if idling more than five times and this is not the last agent: terminate
                                        terminate_self()
                                else:
                                        time.sleep(seconds)
                                        print "number of agents alive in the system: " + str(numAG)
                                        print "trying again in " + str(seconds) + " seconds."
                        else:
                                if numTC > threshold and numTC < max_connections and numTC > numFreeAG: #number of open TC greater than threshold => spawn one agent
                                        print "There are: " + str(numTC) + " triggering conditions."
                                        print "Busy threshold is: " + str(threshold)
                                        bestMachine = find_resources()
                                        mins = 0
                                        while bestMachine == -1 and mins < 5 and not die():
                                                bestMachine = find_resources()
                                                time.sleep(10)
                                                mins += 1

                                        s = spawn(bestMachine)
                                        # print "spawn status: " + str(s.successful())
                                        print "Trying to spawn agent at: machine " + str(bestMachine)
                                        # record_log_activity("Agent %d is spawning an agent at machine %d, spawn status: %d" %(G.AGENT_ID, bestMachine, s), False)
                                        #if spawn fails, notify admin (done by spawn) and continue the work.
                                        #IN CASE UNLIMITED SPAWN, PLEASE CALL: ps aux | grep -ie amarok | awk '{print $2}' | xargs kill -9 

                                #pick the first open task 
                                #Future implementation: can make agent smarter by choosing a task by type
                                cursor.execute("""SELECT id, idTaskResource, Parameters, isLast \
                                                      FROM TriggeringCondition WHERE Status = 0""")
                                results = cursor.fetchall()

                                if len(results) != 0:
                                    idTC = int(results[0]['id'])
                                    G.TASK_ID = results[0]['idTaskResource']
                                    G.LAST_TASK = results[0]['isLast']
                                    print "idTC: " + str(idTC)
                                    print "idTaskResource: " + str(G.TASK_ID)
                                    print "isLast: " + str(G.LAST_TASK)

                                    #globally stores parameters for to be used by load_methods
                                    #so that the agent can spawn more agents with preloaded methods
                                    #and just update PARAM
                                    G.PARAM = results[0]['Parameters']
                                    print str(G.PARAM)

                                    #update TriggeringCondition table
                                    cursor.execute("""UPDATE TriggeringCondition SET \
                                                    idAgent = %d, \
                                                    Status = 1 \
                                                    WHERE id = %d"""  %  (G.AGENT_ID, idTC))

                                    #update Agent table
                                    cursor.execute("""UPDATE Agent SET \
                                                    StartTime = '%s', \
                                                    Status = 1, \
                                                    Priority = %d \
                                                    WHERE id = %d"""  %  (datetime.datetime.now(), calculate_priority(idTC), G.AGENT_ID))

                                    #load and execute methods
                                    status = load_methods(G.TASK_ID)

                                    if status == 0:
                                            # successfully completed the task
                                            # remove TC and write to log file
                                            # addition of new TC will be taken care of by program executed

                                            # VERSION 1.2.0 REMOVE TC IS DISABLED
                                            # cursor.execute("""DELETE FROM TriggeringCondition \
                                            #         WHERE id = %d"""  %  (idTC))
                                            cursor.execute("""UPDATE TriggeringCondition SET Status = -1 WHERE id = %d""" % (idTC))

                                            cursor.execute("""SELECT NumTaskDone FROM Agent WHERE id = %d""" % G.AGENT_ID)

                                            NumTaskDone = cursor.fetchall()[0]["NumTaskDone"] + 1
                                            cursor.execute("""UPDATE Agent SET NumTaskDone = %d WHERE id = %d""" % (NumTaskDone, G.AGENT_ID))

                                            record_log_activity("Task %d sucessfully completed." %idTC, False)
                                    else:
                                            # fail
                                            # reset TC 
                                            cursor.execute("""UPDATE TriggeringCondition SET \
                                                    Status = 2 \
                                                    WHERE id = %d"""  %  (idTC))

                                            record_log_activity("Executing method failed: Triggering condition: %d, Task %d, error number: 2." % (idTC, G.TASK_ID), True)
                                            # if task failed, reset TC to open and log the errors
                                            # limit the number of times to attempt the TC?

                                    #update Agent table to 0 (for free)
                                    #agent status is not used by the system yet
                                    cursor.execute("""UPDATE Agent SET \
                                                    StartTime = '%s', \
                                                    Status = 0, \
                                                    Priority = %d \
                                                    WHERE id = %d"""  %  (datetime.datetime.now(), calculate_priority(idTC), G.AGENT_ID))

                                    DB.commit()
                                else:
                                    print "No open tasks right now, checking again..."
                                #Reset waiting times
                                count = 0
				
                except Exception as err:
                        DB.rollback()
                        print str(err)
                        print traceback.format_exc()
                        record_log_activity("decide_next: failure. " +  str(err), True)

        print "Received Die Signal\nGoodnight, my boss!"
        terminate_self()


#Helper function for decide_next()
def calculate_priority(idTC):
	"""
	(int) -> (int)
	Calculate a priority number for current task.
	Return priority (an integer in [0,100], 0 being the highest priority.)
	"""	
	#dummy function
	return 0


#return a list of available machines by their machineID 
#in order of non-increasing availability (most free first)
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
                record_log_activity("find_resources: db failure. " + str(err), True)
                return 4444


#update machine availabilities
#helper function for find_resources()
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
                        if not port:
                                output = subprocess.check_output(['ssh', str(host_addr), 'cat /proc/meminfo | grep "MemFree:" | sed \'s/\s\+/\*/g\' | cut -d "*" -f 2'])
                        else:
                                output = subprocess.check_output(['ssh', '-p', str(port), str(host_addr), 'cat /proc/meminfo | grep "MemFree:" | sed \'s/\s\+/\*/g\' | cut -d "*" -f 2'])
                        pport = "-p %s " % port

                        cursor.execute("""UPDATE Machines SET FreeMem = %d WHERE idMachine = %d""" % (int(output), int(machine_info[i]['idMachine'])))
                DB.commit()
                        #can restructure codes and factor out duplications
                        #can also add in codes to update info about machine's CPU.... or not

                return 0
                
        except Exception as err:
                record_log_activity("update_machine: db failure or unsuccessful remote subprocess call." + str(err), True)
                print str(err)
                return 4444



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
                agent_path = machine_info['Path'] + "/agent_v120.py" #software folder

                host_addr = machine_info['User'] + "@" + machine_info['Host'] #user@host

                # Find a way to connect remote computer using password
                if not port:
                        status = subprocess.Popen(['ssh', str(host_addr), 'python', str(agent_path)], shell=False)
                else:
                        status = subprocess.Popen(['ssh', '-p', str(port), str(host_addr), 'python', str(agent_path)], shell=False)

                return status
        except Exception as err:
                print traceback.format_exc()
                record_log_activity("spawn: db failure or unsuccessful remote subprocess call. " + str(err), True)
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
                cursor.execute("""SELECT Codepath, Program, Prerequisite FROM TaskResource WHERE\
                id = %d""" % idTR)
                stuff = cursor.fetchall()

                rel_path = stuff[0]["Codepath"]
                program = stuff[0]["Program"]
                prerequisite = stuff[0]["Prerequisite"]

                # Check prerequisite before loading tasks.
                status = wait(prerequisite)
                
                if status == 0:
                    # execute the program
                    code_path = base_path + "/" + rel_path
                    print "Loading task: " + code_path
                    proc = subprocess.Popen([program, code_path, G.PARAM], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
                    
                    # Receiving signals from tasks, this part can be customized so that agent can response according to task.
                    for line in iter(proc.stdout.readline,''):
                        out = line.rstrip()
                        print "Output from %s: %s"%(rel_path, out)

                        if out.startswith("trigger"):
                            trigger(out)

                    err = proc.communicate()[1]
                    
                    if err != "":
                        print "An Error Occurred: " + err 
                    
                    print "\n"
                    return proc.returncode
                
                else:
                    print "Something went wrong, skipping the task... Check TaskResource and TriggeringCondition Table"
                    return status

        except Exception as err:
                print traceback.format_exc()
                record_log_activity("load_methods: db failure or unsuccessful subprocess call. " + str(err), True)
                return 4444

# Help function for load_method()
def trigger(out):
        """ 
        (str) -> ()
        When trigger signal is received, open up a new triggering condition.

        Keyword arguments:
        out -- A string that has format "trigger    Parameter   idTaskResource  isLast" that delimited by tabs.
        """
        DB = G.DB
        cursor = DB.cursor(MySQLdb.cursors.DictCursor)

        try:
            inputs = out.split("\t")
            cursor.execute( "INSERT INTO TriggeringCondition(Parameters ,idTaskResource, isLast, Status)\
             VALUES (\"%s\", %d, %d, 0)"%(inputs[1], int(inputs[2]), int(inputs[3])))

        except Exception as err:
            print traceback.format_exc()
            record_log_activity("trigger: Unable to create a triggering condition.", True)

# Help function for load_method()
def wait(prerequisite):
        """ 
        (str) -> (int)
        Check if all prerequisites are fulfilled before loading tasks.

        Keyword arguments:
        prerequisite -- A string that has format "task1 task2   task3..." that delimited by tabs.
        """
        DB = G.DB
        cursor = DB.cursor(MySQLdb.cursors.DictCursor)

        try:
            print prerequisite
            if prerequisite == None:
                return 0

            tasks = prerequisite.split("\t")
            
            # Status table will be used to track all prerequisite task status.
            status = {}

            # Track update each task status and contiune when all of tasks are done. 
            for task in tasks:
                if task.isdigit() == True:

                    # Wait for all the agents to finish specified tasks, otherwise unload task and flag error.
                    status[task] = 1
                    timeout = 0
                    while status[task] != 0 and timeout <= 2:

                        cursor.execute( "SELECT Status FROM TriggeringCondition WHERE idTaskResource = %d"%(int(task)))
                        agent_status = cursor.fetchall()

                        if len(agent_status) == 0:
                            print "Prerequisite tasks are not available yet, wait for 10 secs"
                            time.sleep(10)
                            timeout += 1

                        elif len([s for s in agent_status if 2 == s["Status"]]) > 0:
                            print "Some agents failed to finish task " + task

                            answer = raw_input('Do you want to fix problems before continue? Type "F" to stop and unload this task, Type anything else to take a break: ')
                            if answer == "F":
                                print "Unloading task..."
                                return 2
                            else:
                                print "Waiting for 30 secs..."
                                time.sleep(30)
                                raw_input('Type anything to resume: ')
                            timeout += 1
                        
                        elif len([s for s in agent_status if (1 == s["Status"]) or (0 == s["Status"])]) > 0:
                            print "Waiting for some agents to finish task " + task
                            time.sleep(10)
                            timeout += 1
                        
                        else:
                            cursor.execute( "SELECT Status FROM TriggeringCondition WHERE idTaskResource = %d AND isLast = %d" % (int(task), 1))
                            last_status = cursor.fetchall()
                            if all(s.values()[0] == -1 for s in last_status) == True:
                                status[task] = 0

            if all(v == 0 for v in status.values()) == True:
                print "Prerequisites are fulfilled!"
                return 0
            else:
                print "Timeout..."
                return 2

        except Exception as err:
            print traceback.format_exc()
            record_log_activity("wait: Something wrong with checking agent status.", True)


#agent terminates itself
def terminate_self(force=True):
        '''
        () -> ()
        Input: whether to wait for agent to finish its task or not.
        check if current agent has finish its job.
                if finished, delete the agent from status table and exit the program.
        '''
        try:
            if G.AGENT_ID != 0:

                DB = G.DB
                cursor = DB.cursor()

                if force == False:
                    cursor.execute( "SELECT Status FROM Agent WHERE id = %d"  %  G.AGENT_ID)
                    status = cursor.fetchone()[0]
                    count = 0
                    while status == 1 and count <= 20:
                        if count == 0:
                            print "Agent is still working now, will wait for 5 mins"
                        cursor.execute( "SELECT Status FROM Agent WHERE id = %d"  %  G.AGENT_ID)
                        status = cursor.fetchone()[0]
                        time.sleep(15)
                        count += 1
                cursor.execute( "DELETE FROM Agent WHERE id = %d"  %  G.AGENT_ID)
                print "\nHappy Agent " + str(G.AGENT_ID) + " is not here now\n"
                DB.commit()
                DB.close()
            exit(1)
        except Exception as err:
                DB.rollback()
                DB.close()
                print traceback.format_exc()
                record_log_activity("terminate_self: " + str(err), True) #try this error msg 
                exit(1)
                

def record_log_activity(activity, notify=True):
        """
        (str, boolea~) -> ()
        Write activity summary of the agent to table 'LogActivity' in database AMA3D.
        This feature was added to handle the concurrency situation in which multiple agents 
        are writing to the log table at a time.
        
        Keyword arguments:
        str activity: contains the activity description to be added to log file. 
                      It could be an error message as well.
                      Error format: <function name: possible causes of failure.> 
        """


        try:
                DB = G.DB
                cursor = DB.cursor()
                time = datetime.datetime.now()

                # replace single quotes that breaks our query
                # note: might want take care of other metacharacters to prevent SQL injections          
                activity = re.sub('\'', '\"', activity)

                cursor.execute("""INSERT INTO LogActivity(idAgent, idMachine, idTask, isLast, TimeStamp, Activity) \
                         VALUES (%d, %d, %d, %d, '%s', '%s')"""  % (G.AGENT_ID, G.MACHINE_ID, G.TASK_ID, G.LAST_TASK, time, activity))

                DB.commit()

                if notify == True:
                        notify_admin("Activity: \n%s\n Agent ID: %d\n Machine ID: %d\n Task ID: %d\n Last Task: %d\n Agent Time: %s\n" % (activity, G.AGENT_ID, G.MACHINE_ID, G.TASK_ID, G.LAST_TASK, str(time)))

                return True

        except Exception as err:
                notify_admin("record_log_activity: " + str(err))
                return False


def notify_admin(m):
        """
        (str) -> ()
        Send an email including the message string to the admin(s).
        
        Keyword arguments:
        msg -- the message to be sent
        """

        DB = G.DB
        cursor = DB.cursor(MySQLdb.cursors.DictCursor)

        try:

            cursor.execute("""SELECT Username, Email FROM User""")
            user_info = cursor.fetchall()

            for i in xrange(len(user_info)):
            
                msg = MIMEText("Dear " + user_info[i]["Username"] + ",\n" + str(m)  + "\n" + "All the best, \nAMA3D Happy Agent (ID: " + str(G.AGENT_ID) + " )")
                msg['Subject'] = "AMA3D - Error"
                msg['From'] = G.MYEMAIL
                msg['To'] = user_info[i]["Email"]

                # print msg.as_string()

                # sending message through localhost
                # s = smtplib.SMTP('localhost')
                # s.sendmail(MYEMAIL, line[1], msg.as_string())
                # s.quit()

        except Exception as err:
                print traceback.format_exc()
                # This could 
                # record_log_activity("notify_admin: " + str(err), False) #try this error msg 
                exit(1)


# Change the DIE file in directory to send die singal.
def die():
        """
        ()->(boolean)
        Listen for die signal and return true iff die signal is present, and delete the die signal after use.
        :param: none
        """
        with open('DIE', 'r+') as file:
            text = file.readline()
            DIE = file.readline()
            file.seek(0)
            file.write(text)
            file.truncate()
        return DIE == "T"



# Acting as the main function
def essehozaibashsei():

    # May change these to global variables
    TIME = 5
    THRESHOLD = 3

    # Parse File
    with open("Account", "r") as file:
        parsed = file.readline().split()
    if connect_db(parsed[0], parsed[1], parsed[2], parsed[3])==0: 
        register(os.popen("echo $USER").read().split("\n")[0])
        decide_next(TIME, THRESHOLD)


if __name__ == '__main__':
    path = "~/AMA3D"
    os.chdir(os.path.expanduser(path)) 
    print "Current DIR is: " + os.getcwd()
    
    t = threading.Thread(target=essehozaibashsei)
    t.start()
    t.join()
