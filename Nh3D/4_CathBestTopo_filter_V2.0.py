# Script Version: 2.0
# Author: Tsz Kwong Lee (Samuel)
# Project: AMA3D
# Task Step: 4


import urllib2
import subprocess
import xml.etree.ElementTree as ET
from Domain import domain
from Domain import segment

R_CUT = 0.20
RESO_CUT = 2.0
CHAIN_LEN = 80
file_name = "CathDomainDescriptionFile"

def filter_pdb(domain, topo):
	try:
		R = domain.r
		reso = domain.reso
		
		if domain.method == 'X-RAY DIFFRACTION' and R <= R_CUT and reso <= RESO_CUT and chain_len >= CHAIN_LEN:
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

#Calculate the score for the protein
def motif_score(R, reso):
	rfc = (R_CUT - R) * 0.9
	res = (RESO_CUT - reso) * 0.2
	return (rfc + res) / 2.0
		
def setup_domain(domain_name):
	""" (str) -> domain.newdomain
	
	    Return a class object of newdomain based on the domain_name given
	    It obtain the domain info from PDB and CathDomainDescriptionFile
	    
	    >>>domain = setup_domain('2zwnB01')
	    >>>Domain: 2zwnB01 
	         PDB_ID: 2zwn 
	         Chain: B 
		 Number of Segment: 2 
		 [Segment Number: 1 
		 Start Position: 2 
		 Start Residue:  
		 End Position: 129 
		 End Residue:  
		 , Segment Number: 2 
		 Start Position: 292 
		 Start Residue:  
		 End Position: 317 
		 End Residue:  
		 ] 
		 Method: X-RAY DIFFRACTION 
		 R-value: 0.16 
		 Resolution: 1.70 
		 Domain Length: 154 
		 B-Factor: 11.18 
	"""
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
		R = float((root[0][5].text if root[0][4].text == 'null' else root[0][4].text) if root[0][3].text == 'null' else root[0][3].text)
		reso = float(root[0][6].text)
		chain_len = int(root[0][7].text)
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
		return d	
	except Exception, err:
		print "Error!"
		return -1	

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

#This is a helper function to cut out all whitespaces and \n in a line
def trim(string):
	concat = string.split(" ")[-1]
	concat.replace(" ", "")
	formedString = concat.split("\n")[0]
	
	return formedString

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

#check if 'MUTATION' is anontated in the pdb file of the 
def hasMutation (pdb_id):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/' + pdb_id +'.pdb')	
	for line in pdb_info:
		if ('COMPND' in line and 'MUTATION' in line):
			return True
	
	return False

#check if 'ENGINEERED' is anontated in the pdb file
def hasEngineered (pdb_id):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/' + pdb_id +'.pdb')	
	for line in pdb_info:
		if ('COMPND' in line and 'ENGINEERED' in line):
			return True
	return False	

def removed_prosthetic_grp (pdb_id):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/' + pdb_id +'.pdb')	
	for line in pdb_info:
		if ('TITLE' in line and 'APO' in line):
			return True
	return False		

#return the sequence number where the mutation occur
def getmutpos (pdb_id):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/' + pdb_id +'.pdb')
	mutation = []
	for line in pdb_info:	
		if ('SEQADV' in line):
			if 'MUTATION' in line[49:70]:
				mutation.append(line[19:22])
	return mutation

#return the sequence number where the engineer occur
def getengpos (pdb_id):
	pdb_info = urllib2.urlopen('http://www.rcsb.org/pdb/files/' + pdb_id +'.pdb')
	engineer = []
	for line in pdb_info:	
		if ('SEQADV' in line):
			if 'ENGINEERED' in line[49:70]:
				engineer.append(line[19:22])
	return engineer



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
	
	#Find the best representative from domain_list
	for domain_name in domain_list:
		pdb_id = domain_name[0][:4]

		# Find R-factor, Resolution of a domain.
		print "Working on PDB: " + pdb_id
		domain = setup_domain(domain_name)
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


#lines for testing
#if __name__ == '__main__':
	#domain = setup_domain('2zwnB01')
	#print domain
	
	#print removed_prosthetic_grp ('1oai')
		
	#mutation = hasMutation('3q8g')
	#print mutation
	#print getmutpos('3q8g')
	
	#engineered = hasEngineered(pdb_id)
	#print engineered
	#print getengpos('3q8g')
	
	#sequence = getDomainSequence("2mcpL01")	
	#print sequence
	




