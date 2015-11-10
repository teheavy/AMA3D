class newsegment(object):
    
    def __init__(self):
        self.num = 0
        self.startpos = 0
        self.endpos = 0
        self.startres = ""
        self.endres = ""
    
    def setNum (num):
        self.num = num
        
    def __repr__(self):
        return "Segment Number: %d \n Start Position: %d \n Start Residue: %s \n End Position: %d \n End Residue: %s \n" %(self.num, self.startpos, self.startres, self.endpos, self.endres) 