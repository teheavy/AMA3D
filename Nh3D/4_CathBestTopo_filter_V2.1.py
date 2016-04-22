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


import re
import sys
import urllib2
import subprocess
import xmltodict
import xml.etree.ElementTree as ET
from Domain import domain
from Domain import segment
import time
import math
import requests

R_CUT = 0.20
RESO_CUT = 2.0
CHAIN_LEN = 80

file_name = "CathDomainDescriptionFile"

#return a score to help in ranking the domain
def filter_pdb(domain, topo):
	""" (Domain, String) -> int
	This function takes an domain object (prepared by setup_domain) and a String (the name of topology).
	It returns a score for the domain that is used for future ranking and also writes the result to the
	Domain_Result file.
	"""
	try:	
		pdb_id = domain.pdb_id
		R = domain.r
		reso = domain.reso
		mutation = domain.mutation
			
		if passCutOff(domain):
			print "The domain passed the cutoff "
			score = motif_score(domain)
			print "The score of this domain is: %f" %(score)
			# Write result to a tab delimited file.
			with open("Domain_Result", "a") as f:
				f.write("%s\t%s\t%.3f\t%.2f\t%d\t%.2f\n" % (topo, pdb_id, R, reso, mutation, score))
			return score
		else:
			print "The domain did not pass the cutoff "
			with open("Domain_Result", "a") as f:
				f.write("%s\t%s\t%.3f\t%.2f\t%d\tnull\n" % (topo, pdb_id, R, reso, mutation))
			return -1

	except Exception, err:
		pdb_id = domain.pdb_id
		print err
		print "Error! Exiting filter_pdb"
		with open("Domain_Result", "a") as f:
			f.write("%s\t%s\t%.3f\t%.2f\t%d\tnull\n" % (topo, pdb_id, R, reso, mutation))
		return -1

#Return a new domain class object that includes the info we need for calculating the score		
def setup_domain(domain_name):
	"""String -> Domain
	This function will take a String (the name of the domain), set up an Domain class object and return it.

	A domain class object will contain the following information: 1) domain name, 2) PDB ID, 3) Chain Character, 
	4) number of segments, 5) the starting position and end position of each segment, 6) experiment method, 
	7) R value, 8) Resolution, 9) Length of Domain, 10) number of mutations, 11) Contains prosthetic group or not

	The above information are found in the following sources: 1) PDB Custom Report, 2) CATH Domain Description File,
	3) PDB Website
	"""
	print "setting up protein domain %s" %(domain_name)
	try:
		counter = 0
		#create new domain object
		d = domain.newdomain(domain_name)

		pdb_id = d.pdb_id

		#get data from PDB, store as an xml
		print "getting information of experimental technique, R value and resolution"
		pdb_info = requests.get('http://www.rcsb.org/pdb/rest/customReport.xml?pdbids=' + pdb_id +
		                        '&customReportColumns=experimentalTechnique,rObserved,rAll,rFree,refinementResolution,chainLength')
		check_Requests(pdb_info)

		dictionary = xmltodict.parse(pdb_info.text)

		info_dataset = dictionary['dataset']['record']

		#This means the protein has multiple chains
		if type(info_dataset) is list:
			#here we don't care which chain to look into since method, R value and resolution are the same for all chains
			info = info_dataset[0]
		#this means the protein has only one chain
		else:
			info = info_dataset


		method = info['dimStructure.experimentalTechnique']

		if (info['dimStructure.rFree'] == 'null'):
			if (info['dimStructure.rAll'] == 'null'):
				if (info['dimStructure.rObserved'] == 'null'):
					R = None
				else:
					R = float(info['dimStructure.rObserved'])*1.25
			else:
				R = float(info['dimStructure.rAll'])*1.25
		else:
			R = float(info['dimStructure.rFree'])

		if (info['dimStructure.refinementResolution'] == 'null'):
			reso = None
		else:
			reso = float(info['dimStructure.refinementResolution'])


		d.setMethod(method)
		d.setR(R)
		d.setReso(reso) 

		print "getting information of domain length and segments"
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
		print "getting information of mutation and prosthetic group"
		d.setMutation(mutation)
		d.sethasProstheticGrp(has_prosthetic_grp(d))

		print "setup is completed"
		return d


	except Exception, err:
		print "Error! %s" %(err)
		#create new domain object
		d = domain.newdomain(domain_name)
		pdb_id = d.pdb_id		
		return d

#--------------------- Helper functions for filter_pdb ---------------------------------------

#check if the domain pass all the cutoffs
def passCutOff(domain):
	"""Domain -> Boolean
	This function takes a Domain Class Object and evaluate it to check if the domain passes the
	cut off in order for it to be included for ranking. 
	"""
	if domain.method != 'X-RAY DIFFRACTION':
		print "method does not meet cutoff"
		return False
	elif domain.r > 0.25:
		print "R value does not meet cutoff"
		return False
	elif domain.reso > 2.2:
		print "Resolution does not meet cutoff"
		return False
	elif domain.length < 80:
		print "Domain Length does not meet cutoff"
		return False		
	elif domain.mutation > 5:
		print "Number of mutations does not meet cutoff"
		return False	
	else:
		return True
	
#Calculate the score for the Domain used for furture ranking
def motif_score(domain):
	"""Domain -> int
	This function takes a Domain Class Object, run a few calculations and return the score of the
	domain for future ranking.
	"""
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
	"""(String, int) -> list of Segments
	This function takes a String (domain name) and an int (counter = number of segments). It returns 
	a list of Segment Class Objects. 
	
	A segment class object containts the following: 1) segment number, 2) start residue position, 
	3) start residue, 4) end residue position, 5) end residue
	
	The above information are collected from CATH Domain Description File
	"""
	file = open(file_name, 'r')
	segmentlist = []
	print "setting up segments"
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
					
					sequence = getDomainSequence(domain_name)
					seg.startres = sequence[0]
					seg.endres = sequence[-1]
					segmentlist.append(seg)
					counter = counter - 1	
				if counter == 0:
					break			
	return segmentlist

#Helper function to get Domain Sequence based on the domain name
#require the exact domain name (i.e. 3h3uA01)
def getDomainSequence(name):
	"""String -> String
	This function takes the domain name and return the sequence of the domain in String
	"""
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
	"""Domain -> int
	This function takes a Domain Class object and returns the number of mutation that the domain contains
	"""
	pdb_info = requests.get('http://www.rcsb.org/pdb/files/' + domain.pdb_id +'.pdb')
	check_Requests(pdb_info)
	num = 0
	for line in pdb_info.iter_lines():
		if ('COMPND' in line and 'MUTATION' in line):
			mutationpos = getmutpos(domain.pdb_id)
			for segment in domain.segment:
				for mut in mutationpos:
					if ((int(mut) >= segment.startpos) and (int(mut) <= segment.endpos)):
						num = num + 1

	return num

#return the sequence number where the mutation occur
def getmutpos (pdb_id):
	"""String -> list of int
	This function takes the PDB ID of the domain and returns a list of sequence number where 
	a mutation occurs
	"""
	pdb_info = requests.get('http://www.rcsb.org/pdb/explore.do?structureId='+ pdb_id)
	check_Requests(pdb_info)
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
	"""Domain -> boolean
	This function takes a Domain class object and returns a boolean that indicates
	whether the domain has prosthetic group
	"""
	pdb_info = requests.get('http://www.rcsb.org/pdb/files/' + domain.pdb_id +'.pdb')
	check_Requests(pdb_info)
	
	reach = 0
	for line in pdb_info.iter_lines():
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
	"""Domain -> int
	This function is responsible for calculating the score of the BFactor using logistic function
	"""
	factor_total = 0
	pdbID = domain.pdb_id
	pdb_info = requests.get('http://www.rcsb.org/pdb/files/'+ pdbID+'.pdb')
	check_Requests(pdb_info)
	for line in pdb_info.iter_lines():
		if (line[0:4] == 'ATOM'):
			serial_num = int(line[22:26].strip())
			for segment in domain.segment:
				if (serial_num >= segment.startpos and serial_num <= segment.endpos):
					BFactor = float(line[60:66].strip())
					factor_total = factor_total + (1 - logisticFunction(-0.22, BFactor, 45))
					
	return factor_total		

def logisticFunction_Reso(domain):
	"""Domain -> int
	This function is responsible for calculating the score of resolution using logistic function
	"""	
	reso = domain.reso
	score = logisticFunction(-7.324, reso, 2.1)
	
	return score

def logisticFunction_Rvalue(domain):
	"""Domain -> int
	This function is responsible for calculating the score of R value using logistic function
	"""	
	r = domain.r
	reso = domain.reso
	x = (10*r)/reso
	score = logisticFunction(-10.986, x, 1.5)
	
	return score

def logisticFunction(k, x, mid):
	""" (int, int, int) -> int
	This function is performs the calculation of a logistic function
	"""	
	#k is positive because we are looking for the portion that we can't trust
	exponent = -k*(x - mid)
	result = 1/(1+ math.exp(exponent))
	return result

def occupancyTest (domain):
	"""Domain -> int
	This function is responsible for performing the occupancy test. Residue with occupancy less
	than 1 should get discarded. This function will return number of residues that should be discarded
	"""
	pdbID = domain.pdb_id
	pdb_info = requests.get('http://www.rcsb.org/pdb/files/'+ pdbID+'.pdb')
	check_Requests(pdb_info)	
	occupancy_serial_num = []
	for line in pdb_info.iter_lines():
		if (line[0:4] == 'ATOM'):	
			serial_num = int(line[22:26].strip())
			for segment in domain.segment:
				if (serial_num >= segment.startpos and serial_num <= segment.endpos):
					occupancy = float(line[55:60].strip())
					if (occupancy != 1.0 and serial_num not in occupancy_serial_num):
						occupancy_serial_num.append(serial_num)
			
	return len(occupancy_serial_num)
#------------------------ Other Helper Function----------------------------

#This is a helper function to cut out all whitespaces and \n in a line
def trim(string):
	"""String -> String
	This function cuts all the whitespaces and \n in a line
	"""
	concat = string.split(" ")[-1]
	concat.strip()
	formedString = concat.split("\n")[0]
	
	return formedString

def check_Requests(result):
	"""int -> null
	This function takes the response code returns by request. If the response code
	is not 200, than it raises an exception and exits the program
	"""
	print result
	if not (result == 200):
		try:
			result.raise_for_status()
		except requests.exceptions.RequestException as e:
			print e
			print 'exiting program'
			sys.exit()
	
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
		newdomain = setup_domain(domain_name)
		
		print "Calculating score for %s "%(domain_name)

		cur_score = filter_pdb(newdomain, topo)
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