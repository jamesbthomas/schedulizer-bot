# Test-Driven Development for the Server class

import pytest, sys, os, pickledb, datetime, hashlib, logging
project_root = os.path.split(os.path.dirname(__file__))[0]
print(project_root)
sys.path.append(os.path.join(project_root,"classes"))

# Import modules for testing
import server
import player
import event

def test_SchedClient():
  """
  GIVEN the SchedClient subclass of discord.ext.commands.Bot
  WHEN a new Schedulizer Client is initialized
  THEN a correctly formatted SchedClient object is created for all active DB files, ready to connect to the Discord server
  """
  # Get active DBs
  dbs = os.listdir(path=os.path.join(project_root,"databases"))

  # Initiate test
  client = server.SchedClient(command_prefix='!')

  # Test necessary inherited options
  assert client.command_prefix == '!'
  # Test tracking variable instantiation
  assert client.servers == []
  assert client.server_ids == []

  # Run function
  client.setup()

  # grab new DBs and make sure they havent changed
  assert os.listdir(path=os.path.join(project_root,"databases")) == dbs

  # Test DB functions
  ## make sure it read all available databases
  for f in dbs:
    try:
      id = int(f.split(".")[0])
      s = client.servers[client.server_ids.index(id)]
      assert id in client.server_ids
      ## Validate that databases had correct info
      db = pickledb.load(os.path.join(project_root,"databases",f,"server.db"),False)
      assert db.get('owner') == s.owner
      assert db.get('id') == s.id
      assert db.get('name') == s.name
    except ValueError:
      continue
  

def test_addServer():
    """
    GIVEN server.addServer method with valid inputs
    WHEN the method is called
    THEN a new Server object should be created and added to the Client object's list of servers; the Server objects track more detailed information than the Guild objects provided by discord
    """
    
    client = server.SchedClient(command_prefix='!')
    
    # Add first server
    s1 = client.addServer(
        id = "test1",
        name = "name for test",
        owner = "ServerOwner#1"
    )
    
    # Add second server
    s2 = client.addServer(
        id = "test2",
        name = "name for second",
        owner = "ServerOwner#2"
    )
    try:
      assert s1.id == "test1"
      assert s1.name == "name for test"
      assert s1.owner == "ServerOwner#1"
      assert client.servers[0].id == "test1"
      assert client.servers[0].name == "name for test"
      assert client.servers[0].owner == "ServerOwner#1"
      assert s2.id == "test2"
      assert s2.name == "name for second"
      assert s2.owner == "ServerOwner#2"
      assert client.servers[1].id == "test2"
      assert client.servers[1].name == "name for second"
      assert client.servers[1].owner == "ServerOwner#2"
      
      # Add server with same id (should raise exception)
      with pytest.raises(FileExistsError,match="Server already known"):
          client.addServer(id = "test1",name = "third test",owner = "Owner")

      # Check for database creation
      assert s1.db_path == os.path.join(project_root,"databases","test1.db")
      assert s1.db.get('owner') == "ServerOwner#1"
      assert s1.db.get('id') == "test1"
      assert s1.db.get('name') == "name for test"
      assert client.servers[0].db_path == os.path.join(project_root,"databases","test1.db")
      assert client.servers[0].db.get('owner') == "ServerOwner#1"
      assert client.servers[0].db.get('id') == "test1"
      assert client.servers[0].db.get('name') == "name for test"
      assert s2.db_path == os.path.join(project_root,"databases","test2.db")
      assert s2.db.get('owner') == "ServerOwner#2"
      assert s2.db.get('id') == "test2"
      assert s2.db.get('name') == "name for second"
      assert client.servers[1].db_path == os.path.join(project_root,"databases","test2.db")
      assert client.servers[1].db.get('owner') == "ServerOwner#2"
      assert client.servers[1].db.get('id') == "test2"
      assert client.servers[1].db.get('name') == "name for second"

    finally:
      # clear out DBs from this test
      os.remove(os.path.join(project_root,"databases","test2.db",'server.db'))
      os.remove(os.path.join(project_root,"databases","test1.db",'server.db'))
      os.remove(os.path.join(project_root,"databases","test2.db",'roster.db'))
      os.remove(os.path.join(project_root,"databases","test1.db",'roster.db'))
      os.remove(os.path.join(project_root,"databases","test2.db",'events.db'))
      os.remove(os.path.join(project_root,"databases","test1.db",'events.db'))
      os.rmdir(os.path.join(project_root,"databases","test1.db"))
      os.rmdir(os.path.join(project_root,"databases","test2.db"))
      client.servers.pop(client.server_ids.index("test1"))
      client.server_ids.pop(client.server_ids.index("test1"))
      client.servers.pop(client.server_ids.index("test2"))
      client.server_ids.pop(client.server_ids.index("test2"))

def test_mapRoles():
  """
  GIVEN server.mapRoles method with template inputs (constructing a discord.Role object manually is annoying and I don't have a good reason to extend it)
  WHEN the method is called
  THEN the Server attributes for each schedulizer role should be mapped to the role for that server
  """

  client = None
  client = server.SchedClient(command_prefix='!')

  # Add Test Server
  s = client.addServer(
    id = "rolesTest",
    name = "Server for mapRoles test",
    owner = "TestOwner"
  )
  client.setup()

  # Create test Role based on discord.Role but only with features that I might care about checking later
  class Role(object):
    def __init__(self,name,guild,mention,id):
      self.name = name
      self.guild = guild
      self.mention = mention
      self.id = id

  testRaider = Role("testRaider",s.name,"@testRaider",1111)
  testSocial = Role("testSocial",s.name,"@testSocial",2222)
  testMember = Role("testMember",s.name,"@testMember",3333)
  testPUG = Role("testPUG",s.name,"@testPUG",4444)
  testAdmin = Role("testAdmin",s.name,"@testAdmin",5555)

  s.mapRole(testRaider,"Raider")
  s.mapRole(testSocial,"Social")
  s.mapRole(testMember,"Member")
  s.mapRole(testPUG,"PUG")
  s.mapRole(testAdmin,"Admin")

  try:
    # Tests
    assert s.Raider == testRaider
    assert s.Social == testSocial
    assert s.Member == testMember
    assert s.PUG == testPUG
    assert s.Admin == testAdmin
    # Exception handling
    with pytest.raises(AttributeError,match="Unknown Schedule option"):
      s.mapRole(testRaider,"bad")
    # Test DB writes
    assert s.db.get("Raider") == testRaider.id
    assert s.db.get("Social") == testSocial.id
    assert s.db.get("Member") == testMember.id
    assert s.db.get("PUG") == testPUG.id
    assert s.db.get("Admin") == testAdmin.id
  finally:
    # clear out DBs
    os.remove(os.path.join(project_root,"databases","rolesTest.db","server.db"))
    os.remove(os.path.join(project_root,"databases","rolesTest.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","rolesTest.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","rolesTest.db"))
    client.servers.pop(client.server_ids.index("rolesTest"))
    client.server_ids.pop(client.server_ids.index("rolesTest"))

def test_updateRoster():
  """
  GIVEN properly constructed Server object and appropriate inputs
  WHEN function is called
  THEN update the player object for the provided player, or insert if new
  """

  client = None
  client = server.SchedClient(command_prefix='!')

  # Add Test Server
  s = client.addServer(
    id = "rosterTest",
    name = "Server for updateRoster test",
    owner = "TestOwner"
  )
  

  # Make a test Player object
  fullPlayer = player.Player("testPlayer#1111",sched="Social",roles=["Tank","DPS"])
  schedPlayer = player.Player("testPlayer#2222",sched="Raider")
  rolesPlayer = player.Player("testPlayer#3333",roles=["Healer","DPS"])
  roster = [fullPlayer,schedPlayer,rolesPlayer]
  
  try:
    # Tests
    ## Add to empty roster
    s.updateRoster(fullPlayer)
    assert s.roster[0] == fullPlayer
    assert s.roster_db.get(fullPlayer.name) == [fullPlayer.sched,fullPlayer.roles]
    s.updateRoster(schedPlayer)
    assert s.roster[1] == schedPlayer
    assert s.roster_db.get(schedPlayer.name) == [schedPlayer.sched,schedPlayer.roles]
    s.updateRoster(rolesPlayer)
    assert s.roster[2] == rolesPlayer
    assert s.roster_db.get(rolesPlayer.name) == [rolesPlayer.sched,rolesPlayer.roles]
    assert s.roster == roster
    ## Capture the database at this stage so we can reset to it later
    db = s.roster_db
    ## Change/Add schedules
    newFull = player.Player("testPlayer#1111",sched="Raider",roles=["Tank","DPS"])
    newSched = player.Player("testPlayer#2222",sched="Social")
    newRoles = player.Player("testPlayer#3333",sched="Member",roles=["Healer","DPS"])
    newRoster = [newFull,newSched,newRoles]
    s.updateRoster(newFull)
    assert s.roster[0] == newFull
    assert s.roster_db.get(newFull.name) == [newFull.sched,newFull.roles]
    s.updateRoster(newSched)
    assert s.roster[1] == newSched
    assert s.roster_db.get(newSched.name) == [newSched.sched,newSched.roles]
    s.updateRoster(newRoles)
    assert s.roster[2] == newRoles
    assert s.roster_db.get(newRoles.name) == [newRoles.sched,newRoles.roles]
    assert s.roster == newRoster
    ### Reset for next battery
    s.roster = roster
    s.roster_db = db
    ## Change/add Roles
    newerFull = player.Player("testPlayer#1111",sched="Raider",roles=["Tank"])
    newerSched = player.Player("testPlayer#2222",sched="Social",roles=["DPS"])
    newerRoles = player.Player("testPlayer#3333",roles=["Tank","Healer","DPS"])
    newerRoster = [newerFull,newerSched,newerRoles]
    s.updateRoster(newerFull)
    assert s.roster[0] == newerFull
    assert s.roster_db.get(newerFull.name) == [newerFull.sched,newerFull.roles]
    s.updateRoster(newerSched)
    assert s.roster[1] == newerSched
    assert s.roster_db.get(newerSched.name) == [newerSched.sched,newerSched.roles]
    s.updateRoster(newerRoles)
    assert s.roster[2] == newerRoles
    assert s.roster_db.get(newerRoles.name) == [newerRoles.sched,newerRoles.roles]
    assert s.roster == newerRoster
    ### reset for next battery
    s.roster = roster
    s.roster_db = db
    ## Remove sched
    fullSched = player.Player("testPlayer#1111",roles=["Tank","DPS"])
    schedSched = player.Player("testPlayer#2222")
    rolesSched = player.Player("testPlayer#3333",roles=["Healer","DPS"])
    schedRoster = [fullSched,schedSched,rolesSched]
    s.updateRoster(fullSched)
    assert s.roster[0] == fullSched
    assert s.roster_db.get(fullSched.name) == [fullSched.sched,fullSched.roles]
    s.updateRoster(schedSched)
    assert s.roster[1] == schedSched
    assert s.roster_db.get(schedSched.name) == [schedSched.sched,schedSched.roles]
    s.updateRoster(rolesSched)
    assert s.roster[2] == rolesSched
    assert s.roster_db.get(rolesSched.name) == [rolesSched.sched,rolesSched.roles]
    assert s.roster == schedRoster
    ### reset for next battery
    s.roster = roster
    s.roster_db = db
    ## Remove roles
    fullRoles = player.Player("testPlayer#1111",sched="Social")
    schedRoles = player.Player("testPlayer#2222",sched="Raider")
    rolesRoles = player.Player("testPlayer#3333")
    rolesRoster = [fullRoles,schedRoles,rolesRoles]
    s.updateRoster(fullRoles)
    assert s.roster[0] == fullRoles
    assert s.roster_db.get(fullRoles.name) == [fullRoles.sched,fullRoles.roles]
    s.updateRoster(schedRoles)
    assert s.roster[1] == schedRoles
    assert s.roster_db.get(schedRoles.name) == [schedRoles.sched,schedRoles.roles]
    s.updateRoster(rolesRoles)
    assert s.roster[2] == rolesRoles
    assert s.roster_db.get(rolesRoles.name) == [rolesRoles.sched,rolesRoles.roles]
    assert s.roster == rolesRoster
  finally:
    # clear out DBs
    os.remove(os.path.join(project_root,"databases","rosterTest.db","server.db"))
    os.remove(os.path.join(project_root,"databases","rosterTest.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","rosterTest.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","rosterTest.db"))
    client.servers.pop(client.server_ids.index("rosterTest"))
    client.server_ids.pop(client.server_ids.index("rosterTest"))
  
def test_getRoles():
  """
  GIVEN properly constructed Server object and list of Role objects
  WHEN function is called
  THEN get the identifiers for the Role objects from the database
  """
  
  # Create test Role based on discord.Role but only with features that I might care about checking later
  class Role(object):
    def __init__(self,name,guild,id):
      self.name = name
      self.guild = guild
      self.id = id
  # Make the list of roles to use as input
  raider = Role("Raider","0001",1111)
  social = Role("Social","0001",2222)
  member = Role("Member","0001",3333)
  pug = Role("Pug","0001",4444)
  nonce = Role("Other","0001",5555)
  roles = [raider,social,member,pug,nonce]
  
  # Make the client and create the databases
  client = None
  client = server.SchedClient(command_prefix='!')
  s = client.addServer(
    id = "0001",
    name = "Server for getRoles test",
    owner = "TestOwner"
  )
  ## Map the role objects for this server
  s.mapRole(raider,"Raider")
  s.mapRole(social,"Social")
  s.mapRole(member,"Member")
  s.mapRole(pug,"PUG")
  
  # Clear the client and remake the same server
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  try:
    # Make sure everything got built correctly
    assert "0001" in client.server_ids
    
    # Tests
    s = client.servers[client.server_ids.index("0001")]
    ## Make sure setup got everything
    assert s.Raider == 1111
    assert s.Social == 2222
    assert s.Member == 3333
    assert s.PUG == 4444
    ## All roles exist
    s.getRoles(roles)
    assert s.Raider == raider
    assert s.Social == social
    assert s.Member == member
    assert s.PUG == pug
  finally:    
    # clear out DBs
    os.remove(os.path.join(project_root,"databases","0001.db","server.db"))
    os.remove(os.path.join(project_root,"databases","0001.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","0001.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","0001.db"))
    client.servers.pop(client.server_ids.index("0001"))
    client.server_ids.pop(client.server_ids.index("0001"))

  # Roles aren't found

  # Make the client and create the databases
  client = None
  client = server.SchedClient(command_prefix='!')
  s = client.addServer(
    id = "0002",
    name = "Server for getRoles second test",
    owner = "TestOwner"
  )
  ## Map the role objects for this server
  ### Doesn't have a mapping for PUGs
  s.mapRole(raider,"Raider")
  s.mapRole(social,"Social")
  s.mapRole(member,"Member")
  
  # Clear the client and remake the same server
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  try:
    # Make sure everything got built correctly
    assert "0002" in client.server_ids
    
    # Tests
    s = client.servers[client.server_ids.index("0002")]
    ## Make sure setup got everything
    assert s.Raider == 1111
    assert s.Social == 2222
    assert s.Member == 3333
    assert s.PUG == None
    ## PUG does not exist
    s.getRoles(roles)
    assert s.Raider == raider
    assert s.Social == social
    assert s.Member == member
    assert s.PUG == None
  finally:    
    # clear out DBs
    os.remove(os.path.join(project_root,"databases","0002.db","server.db"))
    os.remove(os.path.join(project_root,"databases","0002.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","0002.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","0002.db"))
    client.servers.pop(client.server_ids.index("0002"))
    client.server_ids.pop(client.server_ids.index("0002"))
 
def test_getRoster():
  """
  GIVEN properly constructed Server object and appropriate inputs
  WHEN function is called
  THEN get the roster from the database
  """

  # Make the client and create the databases
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  s = client.addServer(
    id = "0001",
    name = "Server for getRoster test",
    owner = "TestOwner"
  )
  ## Create the player objects for this server
  fullPlayer = player.Player("testPlayer#1111",sched="Social",roles=["Tank","DPS"])
  schedPlayer = player.Player("testPlayer#2222",sched="Raider")
  rolesPlayer = player.Player("testPlayer#3333",roles=["Healer","DPS"])
  s.updateRoster(fullPlayer)
  s.updateRoster(schedPlayer)
  s.updateRoster(rolesPlayer)
  
  # Clear the client and remake the same server
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  try:
    # Make sure everything got built correctly
    assert "0001" in client.server_ids
    # Tests
    s = client.servers[client.server_ids.index("0001")]
    s.getRoster()
    ## Check database
    assert s.roster_db.get(fullPlayer.name) == [fullPlayer.sched,fullPlayer.roles]
    assert s.roster_db.get(schedPlayer.name) == [schedPlayer.sched,schedPlayer.roles]
    assert s.roster_db.get(rolesPlayer.name) == [rolesPlayer.sched,rolesPlayer.roles]
    ## Check server attribute
    assert s.roster[0].name == fullPlayer.name or s.roster[0].name == schedPlayer.name or s.roster[0].name == rolesPlayer.name
    assert s.roster[1].name == fullPlayer.name or s.roster[1].name == schedPlayer.name or s.roster[1].name == rolesPlayer.name
    assert s.roster[2].name == fullPlayer.name or s.roster[2].name == schedPlayer.name or s.roster[2].name == rolesPlayer.name
    assert s.roster[0].sched == fullPlayer.sched or s.roster[0].sched == schedPlayer.sched or s.roster[0].sched == rolesPlayer.sched
    assert s.roster[1].sched == fullPlayer.sched or s.roster[1].sched == schedPlayer.sched or s.roster[1].sched == rolesPlayer.sched
    assert s.roster[2].sched == fullPlayer.sched or s.roster[2].sched == schedPlayer.sched or s.roster[2].sched == rolesPlayer.sched
    assert s.roster[0].roles == fullPlayer.roles or s.roster[0].roles == schedPlayer.roles or s.roster[0].roles == rolesPlayer.roles
    assert s.roster[1].roles == fullPlayer.roles or s.roster[1].roles == schedPlayer.roles or s.roster[1].roles == rolesPlayer.roles
    assert s.roster[2].roles == fullPlayer.roles or s.roster[2].roles == schedPlayer.roles or s.roster[2].roles == rolesPlayer.roles
  finally:
    # clear out DBs
    os.remove(os.path.join(project_root,"databases","0001.db","server.db"))
    os.remove(os.path.join(project_root,"databases","0001.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","0001.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","0001.db"))
    client.servers.pop(client.server_ids.index("0001"))
    client.server_ids.pop(client.server_ids.index("0001"))

def test_addEvent():
  """
  GIVEN the addEvent function and an appropriately constructed Event object
  WHEN the function is called
  THEN add the Event to the database and list of local event objects
  """

  # build the client for this test
  client = None
  client = server.SchedClient(command_prefix='!')
  s = client.addServer(
    id = "addEvent",
    name = "Server for addEvent test",
    owner = "TestOwner"
  )
  # build the event objects for this test
  d = datetime.datetime.now()
  rec = event.Event("addEventRecOwner",d,"recurring event",True,"weekly")
  rec1 = event.Event("addEventRecOneOwner",d+datetime.timedelta(0,60),"recurring event",True,"weekly")
  once = event.Event("addEventOnceOwner",d,"occurs once",False)
  once_str = "{0}{1}".format(once.name,str(once.date))
  once_id = hashlib.md5(once_str.encode("utf-8")).hexdigest()
  raid = event.Raid("addEventRaidOwner",d,"recurring raid",True,"monthly")
  # build a roster for this server so we can make sure raids get auto-created correctly
  ## roles arent important, schedules are important
  p1 = player.Player("testPlayer#1111",sched="Social")
  s.updateRoster(p1)
  p2 = player.Player("testPlayer#2222",sched="Raider")
  s.updateRoster(p2)
  p3 = player.Player("testPlayer#3333",sched="Raider",roles=["Tank"])
  s.updateRoster(p3)

  try:
    # run Tests
    ## add first event
    s.addEvent(rec)
    s.event_lock.acquire()
    assert rec.name in s.events_db.getall()
    rec_db = s.events_db.get(rec.name)
    assert rec_db
    assert rec_db[0] == "event"
    assert rec.owner == rec_db[1]
    assert rec.date == datetime.datetime.fromisoformat(rec_db[2])
    assert rec.name == rec_db[3]
    assert rec.recurring == rec_db[4]
    assert rec.frequency == rec_db[5]
    s.event_lock.release()
    ## add second event
    s.addEvent(once)
    s.event_lock.acquire()
    assert rec.name in s.events_db.getall()
    rec_db = s.events_db.get(rec.name)
    assert rec_db
    assert rec_db[0] == "event"
    assert rec_db[1] == rec.owner
    assert rec.date == datetime.datetime.fromisoformat(rec_db[2])
    assert rec.name == rec_db[3]
    assert rec.recurring == rec_db[4]
    assert rec.frequency == rec_db[5]
    assert once_id in s.events_db.getall()
    once_db = s.events_db.get(once_id)
    assert once_db
    assert once_db[0] == "event"
    assert once_db[1] == once.owner
    assert once.date == datetime.datetime.fromisoformat(once_db[2])
    assert once.name == once_db[3]
    assert once.recurring == once_db[4]
    assert once.frequency == once_db[5]
    s.event_lock.release()
    ## add third event
    s.addEvent(raid)
    s.event_lock.acquire()
    assert rec.name in s.events_db.getall()
    rec_db = s.events_db.get(rec.name)
    assert rec_db
    assert rec_db[0] == "event"
    assert rec_db[1] == rec.owner
    assert rec.date == datetime.datetime.fromisoformat(rec_db[2])
    assert rec.name == rec_db[3]
    assert rec.recurring == rec_db[4]
    assert rec.frequency == rec_db[5]
    assert once_id in s.events_db.getall()
    once_db = s.events_db.get(once_id)
    assert once_db
    assert once_db[0] == "event"
    assert once_db[1] == once.owner
    assert once.date == datetime.datetime.fromisoformat(once_db[2])
    assert once.name == once_db[3]
    assert once.recurring == once_db[4]
    assert once.frequency == once_db[5]
    assert raid.name in s.events_db.getall()
    raid_db = s.events_db.get(raid.name)
    assert raid_db
    assert raid_db[0] == "raid"
    assert raid_db[1] == raid.owner
    assert raid.date == datetime.datetime.fromisoformat(raid_db[2])
    assert raid.name == raid_db[3]
    assert raid.recurring == raid_db[4]
    assert raid.frequency == raid_db[5]
    ## adding a raid should setup the roster with all players on the Raider schedule and auto-cook as appopriate
    ### composition
    assert raid_db[6] == [2,2,6]
    ### overall roster
    assert raid_db[7] == [p2.name,p3.name]
    ### tanks
    assert raid_db[8] == [p3.name]
    ### healers
    assert raid_db[9] == []
    ### dps
    assert raid_db[10] == []
    s.event_lock.release()
    ## Throw error if event with that name FileExistsError
    with pytest.raises(ValueError,match="Event exists"):
      s.addEvent(once)
    ## throw error if we try to add a recurring event with the same name
    with pytest.raises(ValueError,match="Recurring event with this name exists; mark event as not recurring or select a unique name"):
      s.addEvent(rec1)
    ## but allow it if its the same name but not recurring
    one_ev = event.Event("raidOwner",d,"recurring raid",False)
    one_ev_str = "{0}{1}".format(one_ev.name,str(one_ev.date))
    one_ev_id = hashlib.md5(one_ev_str.encode("utf-8")).hexdigest()
    s.addEvent(one_ev)
    s.event_lock.acquire()
    assert one_ev_id in s.events_db.getall()
    one_ev_db = s.events_db.get(one_ev_id)
    assert one_ev_db[0] == "event"
    assert one_ev_db[1] == one_ev.owner
    assert datetime.datetime.fromisoformat(one_ev_db[2]) == one_ev.date
    assert one_ev_db[3] == one_ev.name
    assert one_ev_db[4] == one_ev.recurring
    assert one_ev_db[5] == one_ev.frequency
    s.event_lock.release()

  finally:
    # release the lock
    try:
      s.event_lock.release()
    except RuntimeError as e:
      if str(e) != "release unlocked lock":
        raise
      else:
        None
    # clear out DBs
    os.remove(os.path.join(project_root,"databases","addEvent.db","server.db"))
    os.remove(os.path.join(project_root,"databases","addEvent.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","addEvent.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","addEvent.db"))
    client.servers.pop(client.server_ids.index("addEvent"))
    client.server_ids.pop(client.server_ids.index("addEvent"))

def test_getEvents():
  """
  GIVEN correctly constructed SchedClient, and a Server object with existing events in the database
  WHEN the SchedClient sets up
  THEN read in the database, create event objects, and store them in the appropriate Server attribute
  NOTE: there was previously a method named Server.getEvents(), but it was phased out when the database became the primary storage mechanism. This test is still valid, however, to show that events are properly preserved between restarts of the SchedClient
  """

  # Create the client
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  s = client.addServer(
    id = "getEvents",
    name = "Server for getEvents test",
    owner = "TestOwner"
  )
  # create an event
  d = datetime.datetime.now()
  e = event.Event("getEventsOwner",d,"test event",True,"weekly")
  # add event to the server
  s.addEvent(e)
  # recreate the client
  newClient = server.SchedClient(command_prefix='!')
  newClient.setup()

  # test
  try:
    newS = newClient.servers[newClient.server_ids.index("getEvents")]
    # run the function
    assert len(newS.events_db.getall()) == 1
    e_db = newS.events_db.get("test event")
    assert e_db
    assert e_db[0] == "event"
    assert e_db[1] == e.owner
    assert e_db[2] == str(e.date)
    assert e_db[3] == e.name
    assert e_db[4] == e.recurring
    assert e_db[5] == e.frequency
  finally:
    os.remove(os.path.join(project_root,"databases","getEvents.db","server.db"))
    os.remove(os.path.join(project_root,"databases","getEvents.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","getEvents.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","getEvents.db"))
    client.servers.pop(client.server_ids.index("getEvents"))
    client.server_ids.pop(client.server_ids.index("getEvents"))
    newClient.servers.pop(newClient.server_ids.index("getEvents"))
    newClient.server_ids.pop(newClient.server_ids.index("getEvents"))

def test_deleteEvent():
  """
  GIVEN correctly structued Server object, the name of an event, and at least one modifier (all/one,date,time)
  WHEN the method is called
  THEN delete instances of the object based on the modifiers
  """

  # Create the client
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  s = client.addServer(
    id = "deleteEvent",
    name = "Server for deleteEvent test",
    owner = "TestOwner",
  )
  # create an event
  d = datetime.datetime.now()
  rec = event.Event("deleteEventRecOwner",d,"test event",True,"weekly")
  rec1 = event.Event("deleteEventRecOneOwner",d+datetime.timedelta(0,60),"test event",True,"weekly")
  rec1_id = hashlib.md5("{0}{1}".format(rec1.name,str(rec1.date)).encode("utf-8")).hexdigest()
  rec2 = event.Event("deleteEventRecTwoOwner",d+datetime.timedelta(0,60),"test event",False)
  rec2_id = hashlib.md5("{0}{1}".format(rec2.name,str(rec2.date)).encode("utf-8")).hexdigest() 
  one = event.Event("deleteEventOneOwner",d,"second event",False)
  one_id = hashlib.md5("{0}{1}".format(one.name,str(one.date)).encode("utf-8")).hexdigest()

  try:
    s.addEvent(rec)
    ## Delete only event
    s.deleteEvent(rec.name)
    s.event_lock.acquire()
    assert len(s.events_db.getall()) == 0
    s.event_lock.release()
    ## Delete one of multiple events
    ### a recurring event
    s.addEvent(rec)
    s.addEvent(one)
    s.deleteEvent(rec.name)
    s.event_lock.acquire()
    assert len(s.events_db.getall()) == 1
    assert s.events_db.get(one_id) == one.dump()
    s.event_lock.release()
    ### a one-time event
    s.addEvent(rec)
    s.deleteEvent(one.name)
    s.event_lock.acquire()
    assert len(s.events_db.getall()) == 1
    assert s.events_db.get(rec.name) == rec.dump()
    s.event_lock.release()
    ## delete unknown event
    s.deleteEvent(rec.name)
    with pytest.raises(ValueError,match="Unknown Event"):
      s.deleteEvent(rec.name)
    ## delete non-unique event without date/time
    s.addEvent(rec)
    s.addEvent(rec2)
    with pytest.raises(ValueError,match="Operation type \'one\' must have a unique name OR inputs for \'date\' and \'time\'"):
      s.deleteEvent(rec.name,"one")
    ## delete unique event when multiple exist
    s.deleteEvent(rec1.name,"one",d.strftime("%d%b%Y").upper(),(d+datetime.timedelta(0,60)).strftime("%H:%M"))
    s.event_lock.acquire()
    assert rec1_id not in s.events_db.getall()
    assert rec.name in s.events_db.getall()
    s.event_lock.release()
    ## delete all events
    s.addEvent(rec2)
    s.deleteEvent(rec.name,"all")
    s.event_lock.acquire()
    assert rec1_id not in s.events_db.getall()
    assert rec2_id not in s.events_db.getall()
    assert rec.name not in s.events_db.getall()
    s.event_lock.release()

  finally:
    # release the lock
    try:
      s.event_lock.release()
    except RuntimeError as e:
      if str(e) != "release unlocked lock":
        raise
      else:
        None
    os.remove(os.path.join(project_root,"databases","deleteEvent.db","server.db"))
    os.remove(os.path.join(project_root,"databases","deleteEvent.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","deleteEvent.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","deleteEvent.db"))
    client.servers.pop(client.server_ids.index("deleteEvent"))
    client.server_ids.pop(client.server_ids.index("deleteEvent"))

def test_setEvent():
  """
  GIVEN SchedClient object with at least one correctly formatted event and specified property and value to change
  WHEN the method is called
  THEN update the local and DB copies of the event as appropriate with the specified settings
  """

  # Create the client
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  s = client.addServer(
    id = "setEvent",
    name = "Server for setEvent test",
    owner = "TestOwner"
  )
  # create an event
  d = datetime.datetime.now()
  d_date = d +datetime.timedelta(1)
  d_time = d_date+datetime.timedelta(0,60)
  d2 = d + datetime.timedelta(2,120)
  d2_date = d2 + datetime.timedelta(1)
  d2_time = d2_date + datetime.timedelta(0,60)
  e1 = event.Event("setEventOneOwner",d,"test event",True,"weekly")
  e1_id = hashlib.md5("{0}{1}".format(e1.name,str(e1.date)).encode("utf-8")).hexdigest()
  e2 = event.Event("setEventTwoOwner",d,"test event2",False)
  e2_id = hashlib.md5("{0}{1}".format(e2.name,str(e2.date)).encode("utf-8")).hexdigest()
  e3 = event.Event("setEventThreeOwner",d2,"test event2",False)
  e3_id = hashlib.md5("{0}{1}".format(e3.name,str(e3.date)).encode("utf-8")).hexdigest()

  # add event to the server
  s.addEvent(e1)
  s.addEvent(e2)

  # create a player object for some of the owners
  p = player.Player(name="setEventOneOwner")
  p2 = player.Player(name="setEventTwoOwner")
  # add to the roster so we can compare against it later
  s.updateRoster(p)
  s.updateRoster(p2)

  try:
    # change one event
    ## Change the date of the event
    s.setEvent("one",e1.name,"date",d_date.date(),d)
    s.event_lock.acquire()
    s.events_db._loaddb()
    e_db = s.events_db.get(e1.name)
    assert e_db
    assert e_db[3] == e1.name
    assert e_db[2] == str(d_date)
    assert e_db[4] == e1.recurring
    assert e_db[5] == e1.frequency
    s.event_lock.release()
    ## Change the time of the event
    s.setEvent("one",e1.name,"time",d_time.time(),d_date)
    s.event_lock.acquire()
    s.events_db._loaddb()
    e_db = s.events_db.get(e1.name)
    assert e_db
    assert e_db[3] == e1.name
    assert e_db[2] == str(d_time)
    assert e_db[4] == e1.recurring
    assert e_db[5] == e1.frequency
    s.event_lock.release()
    ## change the name of the event
    s.setEvent("one",e1.name,"name","changed test event",d_time)
    s.event_lock.acquire()
    s.events_db._loaddb()
    e_db = s.events_db.get("changed test event")
    assert e_db
    assert e_db[3] == "changed test event"
    assert e_db[2] == str(d_time)
    assert e_db[4] == e1.recurring
    assert e_db[5] == e1.frequency
    s.event_lock.release()
    ## change the frequency of the event
    s.setEvent("one","changed test event","frequency","monthly",d_time)
    s.event_lock.acquire()
    s.events_db._loaddb()
    e_db = s.events_db.get("changed test event")
    assert e_db
    assert e_db[3] == "changed test event"
    assert e_db[2] == str(d_time)
    assert e_db[4] == e1.recurring
    assert e_db[5] == "monthly"
    s.event_lock.release()
    ## change the recurring status of the event
    s.setEvent("one","changed test event","recurring",False,d_time)
    e1_id = hashlib.md5("{0}{1}".format("changed test event",str(d_time)).encode("utf-8")).hexdigest()
    s.event_lock.acquire()
    s.events_db._loaddb()
    e_db = s.events_db.get(e1_id)
    assert e_db
    assert e_db[3] == "changed test event"
    assert e_db[2] == str(d_time)
    assert e_db[4] == False
    assert e_db[5] == None
    s.event_lock.release()
    ## change the owner of the event
    s.setEvent("one","changed test event","owner","setEventTwoOwner")
    s.event_lock.acquire()
    s.events_db._loaddb()
    e_db = s.events_db.get(e1_id)
    assert e_db
    assert e_db[0] == "event"
    assert e_db[1] == "setEventTwoOwner"
    assert e_db[2] == str(d_time)
    assert e_db[3] == "changed test event"
    assert e_db[4] == False
    assert e_db[5] == None
    ## other events didnt change
    e2_db = s.events_db.get(e2_id)
    assert e2_db
    assert e2_db[3] == e2.name
    assert e2_db[2] == str(e2.date)
    assert e2_db[4] == e2.recurring
    assert e2_db[5] == e2.frequency
    s.event_lock.release()
    ## throw errors
    ### tried to change frequency but event is not recurring
    with pytest.raises(ValueError,match="Cannot change frequency for one-time event"):
      s.setEvent("one","changed test event","frequency","weekly",d_time)
    ### date and time not provided
    s.addEvent(e3)
    with pytest.raises(ValueError,match="Operation type \'one\' must have a unique name OR inputs for \'date\' and \'time\'"):
      s.setEvent("one","test event2","recurring",True)
    # change all events
    ## Change the date of the events
    s.setEvent("all",e2.name,"date",d2_date.date())
    e2_id = hashlib.md5("{0}{1}".format("test event2",str(d+datetime.timedelta(3))).encode("utf-8")).hexdigest()
    e3_id = hashlib.md5("{0}{1}".format("test event2",str(d2+datetime.timedelta(1))).encode("utf-8")).hexdigest()
    s.event_lock.acquire()
    s.events_db._loaddb()
    e2_db = s.events_db.get(e2_id)
    assert e2_db
    assert e2_db[3] == e2.name
    assert e2_db[2] == str(d+datetime.timedelta(3))
    assert e2_db[4] == e2.recurring
    assert e2_db[5] == e2.frequency
    e3_db = s.events_db.get(e3_id)
    assert e3_db
    assert e3_db[3] == e3.name
    assert e3_db[2] == str(d2+datetime.timedelta(1))
    assert e3_db[4] == e3.recurring
    assert e3_db[5] == e3.frequency
    s.event_lock.release()
    ## reset for next battery
    s.setEvent("one",e2.name,"date",d,d+datetime.timedelta(3))
    ## Change the time of the events
    s.setEvent("all",e2.name,"time",d2_time.time())
    e2_id = hashlib.md5("{0}{1}".format(e2.name,str(d+datetime.timedelta(0,180))).encode("utf-8")).hexdigest()
    e3_id = hashlib.md5("{0}{1}".format(e3.name,str(d2+datetime.timedelta(1,60))).encode("utf-8")).hexdigest()
    s.event_lock.acquire()
    s.events_db._loaddb()
    e2_db = s.events_db.get(e2_id)
    assert e2_db
    assert e2_db[3] == e2.name
    assert e2_db[2] == str(d+datetime.timedelta(0,180))
    assert e2_db[4] == e2.recurring
    assert e2_db[5] == e2.frequency
    e3_db = s.events_db.get(e3_id)
    assert e3_db
    assert e3_db[3] == e3.name
    assert e3_db[2] == str(d2+datetime.timedelta(1,60))
    assert e3_db[4] == e3.recurring
    assert e3_db[5] == e3.frequency
    s.event_lock.release()
    ## change the name of the events
    s.setEvent("all",e2.name,"name","changed "+e2.name)
    e2_id = hashlib.md5("{0}{1}".format("changed test event2",str(d+datetime.timedelta(0,180))).encode("utf-8")).hexdigest()
    e3_id = hashlib.md5("{0}{1}".format("changed test event2",str(d+datetime.timedelta(3,180))).encode("utf-8")).hexdigest()
    s.event_lock.acquire()
    s.events_db._loaddb()
    e2_db = s.events_db.get(e2_id)
    assert e2_db
    assert e2_db[3] == "changed test event2"
    assert e2_db[2] == str(d+datetime.timedelta(0,180))
    assert e2_db[4] == e2.recurring
    assert e2_db[5] == e2.frequency
    e3_db = s.events_db.get(e3_id)
    assert e3_db
    assert e3_db[3] == "changed test event2"
    assert e3_db[2] == str(d+datetime.timedelta(3,180))
    assert e3_db[4] == e3.recurring
    assert e3_db[5] == e3.frequency
    ## other event didnt change
    e_db = s.events_db.get(e1_id)
    assert e_db
    assert e_db[3] == "changed test event"
    assert e_db[2] == str(d_time)
    assert e_db[4] == False
    assert e_db[5] == None
    s.event_lock.release()
    ## throw errors
    ### cannot change recurring of all events
    with pytest.raises(ValueError,match="Operation \'all\' cannot be used to change event \'recurring\' status"):
      s.setEvent("all","changed test event2","recurring",True)
    ### cannot change frequency of all events
    with pytest.raises(ValueError,match="Operation \'all\' cannot be used to change event frequency"):
      s.setEvent("all","changed test event2","frequency","weekly")
    # event does not exist
    ## by name
    with pytest.raises(ValueError,match="Unknown Event"):
      s.setEvent("one","bad name","date",d_date.date(),d)
    ## by time
    with pytest.raises(ValueError,match="Matching event found with incorrect inputs \'date\' or \'time\'"):
      s.setEvent("one","changed test event","date",d_date.date(),d+datetime.timedelta(4))

  finally:
    # release the lock
    try:
      s.event_lock.release()
    except RuntimeError as e:
      if str(e) != "release unlocked lock":
        raise
      else:
        None
    os.remove(os.path.join(project_root,"databases","setEvent.db","server.db"))
    os.remove(os.path.join(project_root,"databases","setEvent.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","setEvent.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","setEvent.db"))
    client.servers.pop(client.server_ids.index("setEvent"))
    client.server_ids.pop(client.server_ids.index("setEvent"))

def test_changePlayer():
  """
  GIVEN server object with a roster, a player object, and a property and value combination
  WHEN the method is called
  THEN use the Player.updatePlayer() method to modify the player object and update the database
  """

  # Create the client
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  s = client.addServer(
    id = "changePlayer",
    name = "Server for changePlayer test",
    owner = "TestOwner"
  )
  # create player objects
  fullPlayer = player.Player("testPlayer#1111",sched="Social",roles=["Tank","DPS"])
  schedPlayer = player.Player("testPlayer#2222",sched="Raider")
  rolesPlayer = player.Player("testPlayer#3333",roles=["Healer","DPS"])
  roster = [fullPlayer,schedPlayer,rolesPlayer]

  try:
    # add to the roster
    s.updateRoster(fullPlayer)
    s.updateRoster(schedPlayer)
    s.updateRoster(rolesPlayer)
    assert s.roster == roster
    # TESTS
    ## add attribute to previously empty
    ### roles
    s.changePlayer(schedPlayer,"roles",["Tank","Healer"])
    #### check local
    assert schedPlayer.name == "testPlayer#2222"
    assert schedPlayer.sched == "Raider"
    assert schedPlayer.roles == ["Tank","Healer"]
    assert player.Player("testPlayer#2222",sched="Raider") not in s.roster
    #### check db
    sched_db = s.roster_db.get(schedPlayer.name)
    assert schedPlayer.sched == sched_db[0]
    assert schedPlayer.roles == sched_db[1]
    ### sched
    s.changePlayer(rolesPlayer,"sched","Social")
    #### check local
    assert rolesPlayer.name == "testPlayer#3333"
    assert rolesPlayer.sched == "Social"
    assert rolesPlayer.roles == ["Healer","DPS"]
    assert player.Player("testPlayer#3333",roles=["Healer","DPS"]) not in s.roster
    #### check db
    roles_db = s.roster_db.get(rolesPlayer.name)
    assert rolesPlayer.sched == roles_db[0]
    assert rolesPlayer.roles == roles_db[1]
    ## change existing attribute
    ### roles
    s.changePlayer(schedPlayer,"roles",["Tank","DPS"])
    #### check local
    assert schedPlayer.name == "testPlayer#2222"
    assert schedPlayer.sched == "Raider"
    assert schedPlayer.roles == ["Tank","DPS"]
    assert player.Player("testPlayer#2222",sched="Raider",roles=["Tank","Healer"]) not in s.roster
    #### check db
    sched_db = s.roster_db.get(schedPlayer.name)
    assert schedPlayer.sched == sched_db[0]
    assert schedPlayer.roles == sched_db[1]
    ### sched
    s.changePlayer(rolesPlayer,"sched","Raider")
    #### check local
    assert rolesPlayer.name == "testPlayer#3333"
    assert rolesPlayer.sched == "Raider"
    assert rolesPlayer.roles == ["Healer","DPS"]
    assert player.Player("testPlayer#3333",sched="Social",roles=["Healer","DPS"]) not in s.roster
    #### check db
    roles_db = s.roster_db.get(rolesPlayer.name)
    assert rolesPlayer.sched == roles_db[0]
    assert rolesPlayer.roles == roles_db[1]
    ## make sure other objects didnt change
    ### check local
    assert fullPlayer in s.roster
    assert fullPlayer == s.roster[s.roster.index(fullPlayer)]
    ### check db
    full_db = s.roster_db.get(fullPlayer.name)
    assert fullPlayer.sched == full_db[0]
    assert fullPlayer.roles == full_db[1]

  finally:
    os.remove(os.path.join(project_root,"databases","changePlayer.db","server.db"))
    os.remove(os.path.join(project_root,"databases","changePlayer.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","changePlayer.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","changePlayer.db"))
    client.servers.pop(client.server_ids.index("changePlayer"))
    client.server_ids.pop(client.server_ids.index("changePlayer"))

def test_addPlayer():
  """
  GIVEN SchedClient object with a correctly structured Player and Event object
  WHEN the method is called
  THEN add the player to the roster for the event
  """
  
  # Create the client
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  s = client.addServer(
    id = "addPlayer",
    name = "Server for addPlayer test",
    owner = "TestOwner"
  )
  # create player objects
  p1 = player.Player("testPlayer#1111",sched="Raider",roles=["Tank"])
  p2 = player.Player("testPlayer#2222",sched="Social",roles=["Healer"])
  s.updateRoster(p1)
  # create an event
  d = datetime.datetime.now()
  e = event.Event("event owner",d,"test event",False)
  e_id = hashlib.md5("{0}{1}".format(e.name,str(e.date)).encode("utf-8")).hexdigest()
  r = event.Raid("raid owner",d,"test raid",True,"weekly")
  s.addEvent(e)
  s.addEvent(r)

  try:
    ## sign up for an event
    e_out = s.addPlayer(p1,e)
    ## sign up for a raid
    r_out = s.addPlayer(p2,r)
    ## reload the db
    s.event_lock.acquire()
    s.events_db._loaddb()
    ## grab the modified events
    e_db = s.events_db.get(e_id)
    assert e_db
    r_db = s.events_db.get(r.name)
    assert r_db
    s.event_lock.release()

    ## check return values
    ### events just return true or false
    assert e_out
    ### raids return the role that player was selected for
    assert r_out == "Healer"

    ## check attributes
    ### event
    assert e_db[0] == "event"
    assert e_db[1] == e.owner
    assert e_db[2] == str(e.date)
    assert e_db[3] == e.name
    assert e_db[4] == e.recurring
    assert e_db[5] == e.frequency
    assert e_db[6] == [p1.name]
    ### raid
    assert r_db[0] == "raid"
    assert r_db[1] == r.owner
    assert r_db[2] == str(r.date)
    assert r_db[3] == r.name
    assert r_db[4] == r.recurring
    assert r_db[5] == r.frequency
    assert r_db[6] == [2,2,6]
    assert r_db[7] == [p1.name,p2.name]
    assert r_db[8] == [p1.name]
    assert r_db[9] == [p2.name]
    assert r_db[10] == []

    ## check errors
    ### player is already signed up
    with pytest.raises(ValueError,match="Player {0} already signed up for event {1}".format(p1.name,e.name)):
      s.addPlayer(p1,e)
    ### TODO - future version, if more than max number of players signed up for raid, do a waiting list

  finally:
    # release the lock
    try:
      s.event_lock.release()
    except RuntimeError as e:
      if str(e) != "release unlocked lock":
        raise
      else:
        None
    os.remove(os.path.join(project_root,"databases","addPlayer.db","server.db"))
    os.remove(os.path.join(project_root,"databases","addPlayer.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","addPlayer.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","addPlayer.db"))
    client.servers.pop(client.server_ids.index("addPlayer"))
    client.server_ids.pop(client.server_ids.index("addPlayer"))