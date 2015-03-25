# Trigger function in AMA3D. Call this file to invoke and create a new triggering condition that can be processed by AMA3D

#!/usr/bin/python
import MySQLdb
import sys
import traceback
import AMA_globals as G


def connect_db(host, user, password, dbname):
    try:
            G.DB = MySQLdb.connect(host=host, user=user, passwd=password, db=dbname)
            print "Database Connected!"
            return 0
    except Exception, err:
            print traceback.format_exc()
            # Rollback in case there is any error
            G.DB.rollback()
            return 1


if len(sys.argv) != 4:
	print "trigger Usage: python trigger parameter idTaskResource isLast"
    print "Create a new TriggeringCondition so that some Agent can pick up"
	print "See documentation for more info."

else:

    file = open("Account", "r")
    parsed = file.readline().split()
    if connect_db(parsed[0], parsed[1], parsed[2], parsed[3])==0: 
        DB = G.DB
    	cursor = DB.cursor()
    	cursor.execute( "INSERT INTO TriggeringCondition(Parameters ,idTaskResource, isLast, Status) VALUES (\"%s\", %d, %d, 0)"%(sys.argv[1], int(sys.argv[2]), int(sys.argv[3])) )
    	DB.commit()
    else:
    	print "Fail to create a trigger"
    