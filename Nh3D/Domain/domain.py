class newdomain(object):
    
    def __init__(self, name):
        self.name = name
        self.pdb_id = self.name[:4]
        self.method = ""
        self.r = 0
        self.reso = 0
        self.chain = self.name[4]
        self.num_segment = 0
        self.segment = None
        self.length = 0
        self.bfactor = 0
        self.hasMutation = False
        self.hasProstheticGrp = True
    
    def setMethod(self, m):
        self.method = m
        
    def setR(self, r):
        self.r = r
        
    def setReso(self, reso):
        self.reso = reso
    
    def setLength(self, length):
        self.length = length
    
    def setBFactor(self, bfactor):
        self.bfactor = bfactor
        
    def sethasMutation(self, mutation):
        self.hasMutation = mutation
        
    def sethasProstheticGrp(self, prostheticgrp):
        self.hasProstheticGrp = prostheticgrp
    
        
    def __repr__(self):
        return "Domain: %s \n PDB_ID: %s \n Chain: %s \n Number of Segment: %d \n %s \n Method: %s \n R-value: %.2f \n Resolution: %.2f \n Domain Length: %d \n B-Factor: %.2f \n" %(self.name, self.pdb_id, self.chain, self.num_segment, self.segment, self.method, self.r, self.reso, self.length,self.bfactor)
                  
    