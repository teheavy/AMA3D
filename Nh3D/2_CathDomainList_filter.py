# Script Version: 1.0
# Author: Te Chen
# Project: AMA3D
# Task Step: 2

# This script is specially for loading CathDomainList file and distributing tasks of finding the best representative of topology.
# CathDomainList File format: CLF format 2.0, to find more info, please visit www.cathdb.info

import MySQLdb

# Connect to Database by reading Account File.
with open("Account", "r") as file:
    parsed = file.readline().split()
print  parsed
DB = MySQLdb.connect(host=parsed[0], user=parsed[1], passwd=parsed[2], db=parsed[3])
cursor = DB.cursor()
print 'HERERERERE'
# Read the domain list and register CATH domain into database.
domain_list = open("./Nh3D/CathDomainList_sample", "r")
line = domain_list.readline()
while line:
	if line.startswith("#") == False and line != "\n":
		domain_info = line.split()
		
		if len(domain_info) == 12 and float(domain_info[-1]) <= 2.0:
			print "Working on domain: " + domain_info[0]
			name = domain_info[0]
			comment = domain_info[-1] # Put resolution as comment
			topo_node = "%d.%d.%d"%(int(domain_info[1]), int(domain_info[2]), int(domain_info[3]))
			pdb_id = domain_info[0][:4]
			cursor.execute("""INSERT INTO Domain(Name, Comment, TopoNode, PDB_ID) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')"""
				%(name, comment, topo_node, pdb_id))

	line = domain_list.readline()

# Wrap up and close connection.
DB.commit()
DB.close()
