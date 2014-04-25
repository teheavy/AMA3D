# AMA global variables

VERSION = "1.0.0"
# This version assumes a specific database and relation format according to the entity-relational diagram 
# presented in AMA3D
AGENT_ID = ""
DIE = False #
ADMINFILE = "" # file storing admin info
MYEMAIL = "" # email account of AMA3D
PARAM = "" # the data this agent is using right now
DB = "" # global db connection
MACHINE_ID = 0 # the id of the machine the agent is on currently

#TODO
# 1. make machine registry table called (Machines)
# machine id (idMachine)
# abs path of where the AMA3D folder is downloaded (Path)
# CPU memory and other machine info
# username (User)
# password salted and hashed (Pw)

# 2. update relation TaskResource (add column Program)
