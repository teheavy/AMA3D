# Script Version: 1.0
# Author: Te Chen
# Project: AMA3D
# Task Step: 3

# This script use information from PDB to select the best CATH topology representative among all homologous domains.
# CathDomainList File format: CLF format 2.0, to find more info, please visit www.cathdb.info

import MySQLdb
import sys
import urllib2
import xml.etree.ElementTree as ET

def filter_pdb(pdb_id):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/rest/customReport.xml?pdbids=' + pdb_id +
		'&customReportColumns=structureId,experimentalTechnique,rObserved,rAll,rWork,rFree,refinementResolution,chainId,chainLength')
	retrived_pdb_xml = pdb_info.read()
	root = ET.fromstring(retrived_pdb_xml)
	method = root[0][2].text
	R = float(root[0][5].text) 
	reso = float(root[0][7].text)

	if method == 'X-RAY DIFFRACTION' and R < 0.2 and reso <= 2.0:
		return True, R, reso
	else:
		return False, R, reso

# Read system input.
topo_list = sys.argv[1:]


# Connect to Database by reading Account File.
file = open("Account", "r")
parsed = file.readline().split()
DB = MySQLdb.connect(host=parsed[0], user=parsed[1], passwd=parsed[2], db=parsed[3])
cursor = DB.cursor()

# Find the best representative for each topology node.
for topo in topo_list:

	best_representative, best_R, best_reso = "", 0.63, 1000.0
	cursor.execute("""SELECT Name FROM Domain WHERE TopoNode = \'%s\' """%(topo))
	domain_list = cursor.fetchall()
	print domain_list
	for domain_name in domain_list:
		pdb_id = domain_name[0][:4]
		# Find R-factor, Resolution of a domain.
		print pdb_id
		method, cur_R, cur_reso = filter_pdb(pdb_id)
		print cur_R, cur_reso
		print best_representative, best_R - cur_R, best_reso
		if method == True and cur_R <= best_R and (cur_reso <= best_reso or abs(cur_reso - best_reso) < 0.10):
			best_reso = cur_reso
			best_R = cur_R
			best_representative = domain_name[0]
	if best_representative != "":
		cursor.execute("""UPDATE Topology SET Representative = \'%s\' WHERE Node = \'%s\'"""%(best_representative, topo))

# Wrap up and close connection.
DB.commit()
DB.close()