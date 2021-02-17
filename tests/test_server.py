# Test-Driven Development for the Server class

import pytest, sys, os, pickledb, datetime, hashlib
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
    client.addServer(
        id = "test1",
        name = "name for test",
        owner = "ServerOwner#1"
    )
    
    # Add second server
    client.addServer(
        id = "test2",
        name = "name for second",
        owner = "ServerOwner#2"
    )
    try:
      assert client.servers[0].id == "test1"
      assert client.servers[0].name == "name for test"
      assert client.servers[0].owner == "ServerOwner#1"
      assert client.servers[1].id == "test2"
      assert client.servers[1].name == "name for second"
      assert client.servers[1].owner == "ServerOwner#2"
      
      # Add server with same id (should raise exception)

      with pytest.raises(FileExistsError,match="Server already known"):
          client.addServer(id = "test1",name = "third test",owner = "Owner")

      # Check for database creation
      assert client.servers[0].db_path == os.path.join(project_root,"databases","test1.db")
      assert client.servers[0].db.get('owner') == "ServerOwner#1"
      assert client.servers[0].db.get('id') == "test1"
      assert client.servers[0].db.get('name') == "name for test"
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

  s.mapRole(testRaider,"Raider")
  s.mapRole(testSocial,"Social")
  s.mapRole(testMember,"Member")
  s.mapRole(testPUG,"PUG")

  try:
    # Tests
    assert s.Raider == testRaider
    assert s.Social == testSocial
    assert s.Member == testMember
    assert s.PUG == testPUG
    # Exception handling
    with pytest.raises(AttributeError,match="Unknown Schedule option"):
      s.mapRole(testRaider,"bad")
    # Test DB writes
    assert s.db.get("Raider") == testRaider.id
    assert s.db.get("Social") == testSocial.id
    assert s.db.get("Member") == testMember.id
    assert s.db.get("PUG") == testPUG.id
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
  rec = event.Event(d,"recurring event",True,"weekly")
  rec1 = event.Event(d+datetime.timedelta(0,60),"recurring event",True,"weekly")
  once = event.Event(d,"occurs once",False)
  once_str = "{0}{1}".format(once.name,str(once.date))
  once_id = hashlib.md5(once_str.encode("utf-8")).hexdigest()
  raid = event.Raid(d,"recurring raid",True,"monthly")

  try:
    # run Tests
    ## add first event
    s.addEvent(rec)
    assert s.events[0] == rec
    rec_db = s.events_db.get(rec.name)
    assert rec_db
    assert rec_db[0] == "event"
    assert s.events[0].date == datetime.datetime.fromisoformat(rec_db[1])
    assert s.events[0].name == rec_db[2]
    assert s.events[0].recurring == rec_db[3]
    assert s.events[0].frequency == rec_db[4]
    ## add second event
    s.addEvent(once)
    assert s.events[0] == rec
    rec_db = s.events_db.get(rec.name)
    assert rec_db
    assert rec_db[0] == "event"
    assert s.events[0].date == datetime.datetime.fromisoformat(rec_db[1])
    assert s.events[0].name == rec_db[2]
    assert s.events[0].recurring == rec_db[3]
    assert s.events[0].frequency == rec_db[4]
    assert s.events[1] == once
    once_db = s.events_db.get(once_id)
    assert once_db
    assert once_db[0] == "event"
    assert s.events[1].date == datetime.datetime.fromisoformat(once_db[1])
    assert s.events[1].name == once_db[2]
    assert s.events[1].recurring == once_db[3]
    assert s.events[1].frequency == once_db[4]
    ## add third event
    s.addEvent(raid)
    assert s.events[0] == rec
    rec_db = s.events_db.get(rec.name)
    assert rec_db
    assert rec_db[0] == "event"
    assert s.events[0].date == datetime.datetime.fromisoformat(rec_db[1])
    assert s.events[0].name == rec_db[2]
    assert s.events[0].recurring == rec_db[3]
    assert s.events[0].frequency == rec_db[4]
    assert s.events[1] == once
    once_db = s.events_db.get(once_id)
    assert once_db
    assert once_db[0] == "event"
    assert s.events[1].date == datetime.datetime.fromisoformat(once_db[1])
    assert s.events[1].name == once_db[2]
    assert s.events[1].recurring == once_db[3]
    assert s.events[1].frequency == once_db[4]
    assert s.events[2] == raid
    raid_db = s.events_db.get(raid.name)
    assert raid_db
    assert raid_db[0] == "raid"
    assert s.events[2].date == datetime.datetime.fromisoformat(raid_db[1])
    assert s.events[2].name == raid_db[2]
    assert s.events[2].recurring == raid_db[3]
    assert s.events[2].frequency == raid_db[4]
    ## Throw error of event with that name FileExistsError
    with pytest.raises(ValueError,match="Event exists"):
      s.addEvent(raid)
    ## throw error if we try to add a recurring event with the same name
    with pytest.raises(ValueError,match="Recurring event with this name exists; mark event as not recurring or select a unique name"):
      s.addEvent(rec1)
    ## but allow it if its the same name but not recurring
    one_raid = event.Raid(d,"recurring raid",False)
    one_raid_str = "{0}{1}".format(one_raid.name,str(one_raid.date))
    one_raid_id = hashlib.md5(one_raid_str.encode("utf-8")).hexdigest()
    s.addEvent(one_raid)
    assert one_raid in s.events
    one_raid_db = s.events_db.get(one_raid_id)
    assert one_raid_db[0] == "raid"
    assert datetime.datetime.fromisoformat(one_raid_db[1]) == one_raid.date
    assert one_raid_db[2] == one_raid.name
    assert one_raid_db[3] == one_raid.recurring
    assert one_raid_db[4] == one_raid.frequency

  finally:
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
  e = event.Event(d,"test event",True,"weekly")
  # add event to the server
  s.addEvent(e)
  # recreate the client
  newClient = server.SchedClient(command_prefix='!')
  newClient.setup()

  # test
  try:
    newS = newClient.servers[newClient.server_ids.index("getEvents")]
    # run the function
    newS.getEvents()
    assert len(newS.events) == 1
    assert newS.events[0].date == e.date
    assert newS.events[0].name == e.name
    assert newS.events[0].recurring == e.recurring
    assert newS.events[0].frequency == e.frequency
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
    owner = "TestOwner"
  )
  # create an event
  d = datetime.datetime.now()
  rec = event.Event(d,"test event",True,"weekly")
  rec1 = event.Event(d+datetime.timedelta(0,60),"test event",True,"weekly")
  rec2 = event.Event(d+datetime.timedelta(0,60),"test event",False)
  one = event.Raid(d,"second event",False)

  try:
    s.addEvent(rec)
    ## Delete only event
    s.deleteEvent(rec.name)
    assert s.events == []
    assert len(s.events_db.getall()) == 0
    ## Delete one of multiple events
    ### a recurring event
    s.addEvent(rec)
    s.addEvent(one)
    s.deleteEvent(rec.name)
    assert s.events == [one]
    assert len(s.events_db.getall()) == 1
    ### a one-time event
    s.addEvent(rec)
    s.deleteEvent(one.name)
    assert s.events == [rec]
    assert len(s.events_db.getall()) == 1
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
    assert rec1 not in s.events
    assert rec in s.events
    ## delete all events
    s.addEvent(rec2)
    print(list(map(lambda x: [x.name,str(x.date)],s.events)))
    print(s.events_db.getall())
    s.deleteEvent(rec.name,"all")
    assert rec1 not in s.events
    assert rec not in s.events

  finally:
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
  e1 = event.Event(d,"test event",True,"weekly")
  e2 = event.Event(d,"test event2",False)
  e3 = event.Event(d2,"test event2",False)

  # add event to the server
  s.addEvent(e1)
  s.addEvent(e2)
  e1index = s.events.index(list(filter((lambda x: x.name == e1.name),s.events))[0])
  e2index = s.events.index(list(filter((lambda x: x.name == e2.name),s.events))[0])

  try:
    # change one event
    ## Change the date of the event
    s.setEvent("one",e1.name,"date",d_date.date(),d)
    assert s.events[e1index].name == e1.name
    assert s.events[e1index].date == d_date
    assert s.events[e1index].recurring == e1.recurring
    assert s.events[e1index].frequency == e1.frequency
    ## Change the time of the event
    s.setEvent("one",e1.name,"time",d_time.time(),d_date)
    assert s.events[e1index].name == e1.name
    assert s.events[e1index].date == d_time
    assert s.events[e1index].recurring == e1.recurring
    assert s.events[e1index].frequency == e1.frequency
    ## change the name of the event
    s.setEvent("one",e1.name,"name","changed test event",d_time)
    assert s.events[e1index].name == "changed test event"
    assert s.events[e1index].date == d_time
    assert s.events[e1index].recurring == e1.recurring
    assert s.events[e1index].frequency == e1.frequency
    ## change the frequency of the event
    s.setEvent("one","changed test event","frequency","monthly",d_time)
    assert s.events[e1index].name == "changed test event"
    assert s.events[e1index].date == d_time
    assert s.events[e1index].recurring == e1.recurring
    assert s.events[e1index].frequency == e1.frequency
    ## change the recurring status of the event
    s.setEvent("one","changed test event","recurring",False,d_time)
    assert s.events[e1index].name == "changed test event"
    assert s.events[e1index].date == d_time
    assert s.events[e1index].recurring == False
    assert s.events[e1index].frequency == None
    ## other events didnt change
    assert s.events[e2index].name == e2.name
    assert s.events[e2index].date == e2.date
    assert s.events[e2index].recurring == e2.recurring
    assert s.events[e2index].frequency == e2.frequency
    ## throw errors
    ### tried to change frequency but event is not recurring
    with pytest.raises(ValueError,match="Cannot change frequency for one-time event"):
      s.setEvent("one","changed test event","frequency","weekly",d_time)
    ### date and time not provided
    s.addEvent(e3)
    with pytest.raises(ValueError,match="Operation type \'one\' must have a unique name OR inputs for \'date\' and \'time\'"):
      s.setEvent("one","test event2","recurring",True)
    # change all events
    e3index = s.events.index(list(filter((lambda x: x.name == e3.name and x.date == e3.date),s.events))[0])
    ## Change the date of the events
    s.setEvent("all",e2.name,"date",d2_date.date())
    assert s.events[e2index].name == e2.name
    assert s.events[e2index].date == d2_date-datetime.timedelta(0,120)
    assert s.events[e2index].recurring == e2.recurring
    assert s.events[e2index].frequency == e2.frequency
    assert s.events[e3index].name == e3.name
    assert s.events[e3index].date == d2_date
    assert s.events[e3index].recurring == e3.recurring
    assert s.events[e3index].frequency == e3.frequency
    ## reset for next battery
    s.setEvent("one",e2.name,"date",d,s.events[e2index].date)
    ## Change the time of the events
    s.setEvent("all",e2.name,"time",d2_time.time())
    assert s.events[e2index].name == e2.name
    assert s.events[e2index].date == d2_time-datetime.timedelta(3,0)
    assert s.events[e2index].recurring == e2.recurring
    assert s.events[e2index].frequency == e2.frequency
    assert s.events[e3index].name == e3.name
    assert s.events[e3index].date == d2_time
    assert s.events[e3index].recurring == e3.recurring
    assert s.events[e3index].frequency == e3.frequency
    ## change the name of the events
    s.setEvent("all",e2.name,"name","changed "+e2.name)
    assert s.events[e2index].name == "changed test event2"
    assert s.events[e2index].date == d2_time-datetime.timedelta(3)
    assert s.events[e2index].recurring == e2.recurring
    assert s.events[e2index].frequency == e2.frequency
    assert s.events[e3index].name == "changed test event2"
    assert s.events[e3index].date == d2_time
    assert s.events[e3index].recurring == e3.recurring
    assert s.events[e3index].frequency == e3.frequency

    ## other event didnt change
    assert s.events[e1index].name == "changed test event"
    assert s.events[e1index].date == d_time
    assert s.events[e1index].recurring == False
    assert s.events[e1index].frequency == None
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
      s.setEvent("one",e1.name,"date",d_date.date(),d-datetime.timedelta(4))

    ## Last up, check the events in the database
    e1_id = hashlib.md5("{0}{1}".format(e1.name,str(e1.date)).encode("utf-8")).hexdigest()
    e2_id = hashlib.md5("{0}{1}".format(e2.name,str(e2.date)).encode("utf-8")).hexdigest()
    e3_id = hashlib.md5("{0}{1}".format(e3.name,str(e3.date)).encode("utf-8")).hexdigest()
    e1db = s.events_db.get(e1_id)
    assert e1db
    e2db = s.events_db.get(e2_id)
    assert e2db
    e3db = s.events_db.get(e3_id)
    assert e3db
    assert len(s.events_db.getall()) == 3
    assert e1db[1] == str(e1.date)
    assert e1db[2] == e1.name
    assert e1db[3] == e1.recurring
    assert e1db[4] == e1.frequency
    assert e2db[1] == str(e2.date)
    assert e2db[2] == e2.name
    assert e2db[3] == e2.recurring
    assert e2db[4] == e2.frequency
    assert e3db[1] == str(d2_time)
    assert e3db[2] == e3.name
    assert e3db[3] == e3.recurring
    assert e3db[4] == e3.frequency

  finally:
    os.remove(os.path.join(project_root,"databases","setEvent.db","server.db"))
    os.remove(os.path.join(project_root,"databases","setEvent.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","setEvent.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","setEvent.db"))
    client.servers.pop(client.server_ids.index("setEvent"))
    client.server_ids.pop(client.server_ids.index("setEvent"))