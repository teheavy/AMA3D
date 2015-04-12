# Script Version: 1.0
# Author: Te Chen
# Project: AMA3D
# Task Step: 1

# This script is specially for loading CATH Node Name file and record all the topology level into database.
# CathDomainList File format: Cath Names File (CNF) Format 2.0, to find more info, please visit www.cathdb.info

import MySQLdb
import os
import sys


# Connect to Database by reading Account File.
with open("Account", "r") as file:
    parsed = file.readline().split()
DB = MySQLdb.connect(host=parsed[0], user=parsed[1], passwd=parsed[2], db=parsed[3])
cursor = DB.cursor()

# Read the node list and register CATH topology into database.
os.getcwd()
node_file = open("./Nh3D/CathNames", "r")
line = node_file.readline()

trigger = ''
while line:
	if line.startswith("#") == False and line != "":
		node_info = line.split("    ")
		
		if len(node_info) == 3:
			if node_info[0].count('.') == 2:
				print "Working on Node: " + node_info[0]
				cursor.execute("""INSERT INTO Topology(Node, Description, Comment, Representative) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')"""
					% (node_info[0], str(MySQLdb.escape_string(node_info[2][1:-1])), 'from CathNames', node_info[1]))
				# print """INSERT INTO Topology(Node, Description, Comment, Representative) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')"""\
				# 	% (node_info[0], (node_info[2][1:-1]).replace(";", ""), 'from CathNames', node_info[1])
				# Trigger a new TC
				print trigger
				sys.stdout.flush()
				trigger = "trigger\t%s\t%d\t%d"%(node_info[0], 4, 0)
			elif node_info[0].count('.') == 3:
				# Trigger a new TC but leave last flag on.
				print trigger[:-1] + "1"
				sys.stdout.flush()
				break
	line = node_file.readline()

# Wrap up and close connection.
DB.commit()
DB.close()