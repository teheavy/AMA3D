--Test Script for AMA3D Framework
-- When something terrible happen, call this:
-- ps aux | grep -ie python | awk '{print $2}' | xargs kill -9

--1. Check all the tables exists.
TRUNCATE table Agent;
TRUNCATE table TriggeringCondition;
TRUNCATE table LogActivity;


--2. Load some test cases.
TRUNCATE table TaskResource;
TRUNCATE table Machines;
TRUNCATE table User;

INSERT INTO TaskResource(Codepath, Version, Program) VALUES ('./Nh3D/1_AMA3D_start.py', '1.0', 'python');
INSERT INTO TaskResource(Codepath, Version, Program) VALUES ('./Nh3D/2_CathDomainList_filter.py', '1.0', 'python');
INSERT INTO TaskResource(Codepath, Version, Program) VALUES ('./Nh3D/3_CathTopo_uploader.py', '1.0', 'python');
INSERT INTO TaskResource(Codepath, Version, Program) VALUES ('./Nh3D/4_CathBestTopo_filter.py', '1.0', 'python');
INSERT INTO TaskResource(Codepath, Version, Program) VALUES ('', '1.0', 'pwd');
INSERT INTO TaskResource(Codepath, Version, Program) VALUES ('lol.py', '1.0', 'python');

INSERT INTO TriggeringCondition(Parameters ,idTaskResource, isLast, Status) VALUES ('', 1, 0, 0);
INSERT INTO TriggeringCondition(Parameters ,idTaskResource, isLast, Status) VALUES ('', 2, 0, 0);
INSERT INTO TriggeringCondition(Parameters ,idTaskResource, isLast, Status) VALUES ('', 3, 0, 0);

INSERT INTO Machines(User, Path, Host) VALUES ('hsueh', '/home/hsueh/AMA3D', '142.150.40.189');
INSERT INTO Machines(User, Path, Host) VALUES ('chen', '/home/chen/AMA3D', '142.150.40.189');

INSERT INTO User(Username, Email) VALUES ('Fred', 'te.chen@outlook.com');

INSERT INTO Agent(Machine, RegisterTime, StartTime, Status) VALUES ('chen', '2015-03-02 22:46:27', '2015-03-02 22:46:52', 0);

--3. Test Nh3D Table Status.
INSERT INTO Topology(Node, Name) VALUES ('1.10.10', 'Arc Repressor Mutant, subunit A');
INSERT INTO Domain(Name, TopoNode, PDB_ID) VALUES ('1oaiA00', 1, '1oai');

--4. Check all the table info.
SELECT * FROM Machines;
SELECT * FROM TaskResource;
SELECT * FROM Agent;
SELECT * FROM TriggeringCondition;
SELECT * FROM LogActivity;

--5. Check Nh3D Info.
TRUNCATE table Domain;
TRUNCATE table Topology;

SELECT * FROM Domain;
SELECT * FROM Topology;

--0. Reset database.6