# Script Version: 1.0
# Author: Tsz Kwong Lee
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
import re
from Domain import domain
from Domain import segment
import time
import math

R_CUT = 0.20
RESO_CUT = 2.0
CHAIN_LEN = 80

file_name = "CathDomainDescriptionFile"

#return a score to help in ranking the domain
def filter_pdb(domain, topo):
	try:	
		print "filtering domain"
		pdb_id = domain.pdb_id
		R = domain.r
		reso = domain.reso
		mutation = domain.mutation
			
		if passCutOff(domain):
			score = motif_score(domain)
					
			# Write result to a tab delimited file.
			with open("Domain_Result", "a") as f:
				f.write("%s\t%s\t%.3f\t%.2f\t%d\t%.2f\n" % (topo, pdb_id, R, reso, mutation, score))
			return score
		else:
			with open("Domain_Result", "a") as f:
				f.write("%s\t%s\t%.3f\t%.2f\t%d\tnull\n" % (topo, pdb_id, R, reso, mutation))
			return -1

	except Exception, err:
		print "Error! Exiting filter_pdb"
		with open("Domain_Result", "a") as f:
			f.write("%s\t%s\t%.3f\t%.2f\t%d\tnull\n" % (topo, pdb_id, R, reso, mutation))
		return -1

#Return a new domain class object that includes the info we need for calculating the score		
def setup_domain(domain_name):
	try:
		counter = 0
		#create new domain object
		d = domain.newdomain(domain_name)
		pdb_id = d.pdb_id
		
		#get data from PDB, store as an xml
		pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/rest/customReport.xml?pdbids=' + pdb_id +
	                '&customReportColumns=experimentalTechnique,rObserved,rAll,rFree,refinementResolution,chainLength,averageBFactor')
		
		retrived_pdb_xml = pdb_info.read()
		root = ET.fromstring(retrived_pdb_xml)
		
		method = root[0][2].text
		
		if (root[0][5].text == 'null'):
			if (root[0][4].text == 'null'):
				if (root[0][3].text == 'null'):
					R = None
				else:
					R = float(root[0][3].text)*1.25
			else:
				R = float(root[0][4].text)*1.25
		else:
			R = float(root[0][5].text)
		
		if (root[0][6].text == 'null'):
			reso = None
		else:
			reso = float(root[0][6].text)
		
		if (root[0][8].text == 'null'):
			b_factor = None
		else:
			b_factor = float(root[0][8].text)
		
		d.setMethod(method)
		d.setR(R)
		d.setReso(reso) 
		d.setBFactor(b_factor)	
		
		#get data from Cath Domain Description File
		file = open(file_name, 'r')
		for line in file:
			#Search for domain name that starts with the PDB_id 
			if "DOMAIN" in line and d.name in line:	
				#Search for the line that contains the domain length
				for line in file:
					if "DLENGTH" in line:
						domainLength = trim(line)
						d.setLength(int(domainLength))
						break				
				
				#Search for the number of segments and append to the domain info
				for line in file:
					if "NSEGMENTS" in line:
						numSegments = int(trim(line))
						d.num_segment = numSegments
						counter = numSegments
						break
				
				segment_list = setupSegmentList(domain_name, counter)
				d.segment = segment_list
				
		mutation = hasMutation(d)
		
		d.setMutation(mutation)
		d.sethasProstheticGrp(has_prosthetic_grp(d))
		
		return d
	

	except Exception, err:
		print "Error!"
		return -1	

#--------------------- Helper functions for filter_pdb ---------------------------------------

#check if the domain pass all the cutoffs
def passCutOff(domain):
	if domain.method != 'X-RAY DIFFRACTION' or domain.r < 0.25 or domain.reso > 2.2 or domain.length < 80 or domain.mutation > 5:
		return True
	else:
		return True
	
#Calculate the score for the Domain used for furture ranking
def motif_score(domain):
	print "Calculating the score for the domain"
	length = domain.length	
	bFactorAdjust = logisticFunction_BFactor(domain)	
	mutationAdjust = domain.mutation*5
	
	if domain.hasProstheticGrp == False:
		pAdjust = 20
	else:
		pAdjust = 0
	
	resoAdjust = logisticFunction_Reso(domain)	
	rAdjust = logisticFunction_Rvalue(domain)
	occupancyAdjust = occupancyTest(domain)
	
	score = (length - bFactorAdjust - mutationAdjust - pAdjust - occupancyAdjust) * resoAdjust * rAdjust
	
	return score
#----------------- Helper functions for Setting up the Domain----------------------

def setupSegmentList(domain_name, counter):
	file = open(file_name, 'r')
	segmentlist = []
	
	for line in file:	
		#Search for domain name 
		if "DOMAIN" in line and domain_name in line:
			
			#Search for Segment range and append to the Domain info
			for line in file:
				if "SRANGE" in line and counter > 0:
					seg = segment.newsegment()
					
					range = line.split("    ")[-1]
					start = line.split("    ")[-1].split("  ")[0]
					stop = line.split("    ")[-1].split("  ")[1]
					startpos = start.split("=")[-1]
					stop2 = stop.split("=")[-1]
					stoppos = stop2.replace("\n", "")
					
					seg.startpos = int(startpos)
					seg.endpos = int(stoppos)
					seg.num = len(segmentlist) + 1
					
					segmentlist.append(seg)
					counter = counter - 1	
				if counter == 0:
					break			
	return segmentlist

#Helper function to get Domain Sequence based on the domain name
#require the exact domain name (i.e. 3h3uA01)
def getDomainSequence(name):
	file = open(file_name, 'r')
	domainLength = 0
	domainSequence = ""
	for line in file:
		if "DOMAIN" in line and name in line:
			#Search for the line that contains the domain length
			for line in file:
				if "DLENGTH" in line:
					domainLength = int(trim(line))
					break	
			
			#Search for the line that contains the domain sequence	
			for line in file:
				if "DSEQS" in line and len(domainSequence) < domainLength:
					domainSequence = domainSequence + trim(line)
					continue
								
	file.close()
	return domainSequence	

#return the number of mutations located in the domain
def hasMutation (domain):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/' + domain.pdb_id +'.pdb')
	num = 0
	for line in pdb_info:
		if ('COMPND' in line and 'MUTATION' in line):
			mutationpos = getmutpos(domain.pdb_id)
			for segment in domain.segment:
				for mut in mutationpos:
					if ((int(mut) >= segment.startpos) and (int(mut) <= segment.endpos)):
						num = num + 1

	return num

#return the sequence number where the mutation occur
def getmutpos (pdb_id):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/explore.do?structureId='+ pdb_id)
	mutation = []
	for line in pdb_info:
		if '<td class="entityDetails">' in line:
			for line in pdb_info:
				if 'Mutation:' in line:
					split_line = line.split(":")[-1]
					mut_str = split_line.replace(" ","").split(",")
					for s in mut_str:
						s1 = re.sub("[^0-9]", "", s)
						mutation.append(s1)				
					break 
	return mutation

def has_prosthetic_grp (domain):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/' + domain.pdb_id +'.pdb')
	reach = 0
	for line in pdb_info:
		if not('TITLE' in line): 
			if reach != 0:
				return True
		else:
			reach = reach + 1
			if 'APO' in line:
				return False
			
	return True	

#--------Helper Functions for B-Factor, Reso, R-value correction, and Occupancy ----------------------
def logisticFunction_BFactor(domain):
	factor_total = 0
	pdbID = domain.pdb_id
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/'+ pdbID+'.pdb')
	for line in pdb_info:
		if (line[0:4] == 'ATOM'):
			serial_num = int(line[6:11].strip())
			
			for segment in domain.segment:
				if (serial_num >= segment.startpos and serial_num <= segment.endpos):
					BFactor = float(line[60:66].strip())
					factor_total = factor_total + (1 - logisticFunction(-0.22, BFactor, 45))
					
	return factor_total	

def logisticFunction_Reso(domain):
	reso = domain.reso
	score = logisticFunction(-7.324, reso, 2.1)
	
	return score

def logisticFunction_Rvalue(domain):
	r = domain.r
	reso = domain.reso
	x = (10*r)/reso
	score = logisticFunction(-10.986, x, 1.5)
	
	return score

def logisticFunction(k, x, mid):
	#k is positive because we are looking for the portion that we can't trust
	exponent = -k*(x - mid)
	result = 1/(1+ math.exp(exponent))
	return result

def occupancyTest (domain):
	pdbID = domain.pdb_id
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/'+ pdbID+'.pdb')
	discardResidue = 0	
	
	for line in pdb_info:
		if (line[0:4] == 'ATOM'):	
			serial_num = int(line[6:11].strip())
			
			for segment in domain.segment:
				if (serial_num >= segment.startpos and serial_num <= segment.endpos):
					occupancy = float(line[55:60].strip())
					if (occupancy != 1.0):
						discardResidue = discardResidue + 1
			
	return discardResidue
#------------------------ Other Helper Function----------------------------

#This is a helper function to cut out all whitespaces and \n in a line
def trim(string):
	concat = string.split(" ")[-1]
	concat.strip()
	formedString = concat.split("\n")[0]
	
	return formedString

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
		domain = setup_domain(domain_name)
		
		print "Working on domain: " + domain_name

		cur_score = filter_pdb(domain, topo)
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