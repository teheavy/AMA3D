# Script Version: 1.0
# Author: Te Chen
# Project: AMA3D
# Task Step: 4

# This script use information from PDB to select the best CATH topology representative among all homologous domains.
# CathDomainList File format: CLF format 2.0, to find more info, please visit www.cathdb.info

# R observed - Residual factor R for reflections that satisfy the resolution and observation limits. This quantity includes reflections set aside for cross-validation in a "free" R-factor set. Residual factor R for reflections that satisfy the resolution and observation limits. 
# R all - Residual factor R for all reflections that satisfy the limits established by high and low resolution cut-offs. It includes reflections which do not satisfy the sigma cutoff criteria as well as those set aside for cross-validation in a "free" R-factor set. 
# R work - Residual factor R for reflections that satisfy the resolution and observation limits and that were used as the working reflections in the refinement. This quantity does not include reflections set aside for cross-validation in a "free" R-factor set. 
# R free - Residual factor R for reflections that satisfy the resolution and observation limits and that were excluded from refinement to be used for cross validation in a "free" R factor set. R free is a less biased metric, and is typically higher than an R work. If R free is significantly higher than the R work, the structural model may be over fitted. 


import MySQLdb
import sys
import urllib2
import xml.etree.ElementTree as ET

R_CUT = 0.20
RESO_CUT = 2.0
CHAIN_LEN = 80

def filter_pdb(pdb_id, topo):
	try:
		
		pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/rest/customReport.xml?pdbids=' + pdb_id +
			'&customReportColumns=experimentalTechnique,rObserved,rAll,rFree,refinementResolution,chainLength')
		retrived_pdb_xml = pdb_info.read()
		root = ET.fromstring(retrived_pdb_xml)

		method = root[0][2].text
		R = float((root[0][5].text if root[0][4].text == 'null' else root[0][4].text) if root[0][3].text == 'null' else root[0][3].text)
		reso = float(root[0][6].text)
		chain_len = int(root[0][7].text)

		if method == 'X-RAY DIFFRACTION' and R <= R_CUT and reso <= RESO_CUT and chain_len >= CHAIN_LEN:
			score = motif_score(R, reso)
			# Write result to a tab delimited file.
			with open("Domain_Result", "a") as f:
				f.write("%s\t%s\t%.3f\t%.2f\t%d\t%f\n" % (topo, pdb_id, R, reso, chain_len, score))
			return score
		else:
			with open("Domain_Result", "a") as f:
				f.write("%s\t%s\t%.3f\t%.2f\t%d\tnull\n" % (topo, pdb_id, R, reso, chain_len))
			return -1

	except Exception, err:
		with open("Domain_Result", "a") as f:
			f.write("%s\t%s\t%s\t%s\t%s\tnull\n" % (topo, pdb_id, root[0][5].text, root[0][6].text, root[0][7].text))
		return -1


def motif_score(R, reso):
	rfc = (R_CUT - R) * 0.9
	res = (RESO_CUT - reso) * 0.2
	return (rfc + res) / 2.0

# Read system input.
topo_list = sys.argv[1:]

# Connect to Database by reading Account File.
file = open("Account", "r")
parsed = file.readline().split()
DB = MySQLdb.connect(host=parsed[0], user=parsed[1], passwd=parsed[2], db=parsed[3])
cursor = DB.cursor()

# Find the best representative for each topology node.
for topo in topo_list:
	print "Working on Topology: " + topo

	best_representative, best_score = "", 0
	cursor.execute("""SELECT Name FROM Domain WHERE TopoNode = \'%s\' """%(topo))

	domain_list = cursor.fetchall()
	for domain_name in domain_list:
		pdb_id = domain_name[0][:4]

		# Find R-factor, Resolution of a domain.
		print "Working on PDB: " + pdb_id

		cur_score = filter_pdb(pdb_id, topo)
		if cur_score > best_score:
			best_score = cur_score
			best_representative = domain_name[0]

	if best_representative != "":
		with open("Domain_Result", "a") as f:
			f.write("BEST REPRESENTATIVE\t%s\t%s\n" % (topo, best_representative[:4]))
		cursor.execute("""UPDATE Topology SET Representative = \'%s\', Score = \'%.3f\' WHERE Node = \'%s\'"""%(best_representative, best_score, topo))
	else:
		print "Cannot find a representative"

# Wrap up and close connection.
DB.commit()
DB.close()