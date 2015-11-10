# Script Version: 1.0
# Author: Te Chen
# Project: AMA3D
# Task Step: 1

import sys
import urllib2
import time
VERSION = '4.0.0'

def prepare_cath():
	ver = VERSION.replace('.', '_')
	download_file(ver, 'CathDomainList')
	download_file(ver, 'CathNames')
	download_file(ver, 'CathDomainDescriptionFile')

def download_file(ver, file_name):
	url = "ftp://ftp.biochem.ucl.ac.uk/pub/cath/v%s/%s" % (ver, file_name)

	file_name = url.split('/')[-1]
	u = urllib2.urlopen(url)
	f = open('C:/AMA3D/Nh3D/' + file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break

	    file_size_dl += len(buffer)
	    f.write(buffer)
	    
	f.close()
	print "Downloaded file" + file_name

if __name__ == '__main__':
	# Download necessary files when start
	prepare_cath()

	# This part triggers all the tasks afterwards.

	print "trigger\t%s\t%d\t%d"%('', 2, 1)
	sys.stdout.flush()

	print "trigger\t%s\t%d\t%d"%('', 3, 1)
	sys.stdout.flush()

	# Write result to a file as well just for testing
	with open("Domain_Result", "w") as f:
			f.write("Topology\tPDB ID\tR\tResolution\tChain Length\tScore\n")