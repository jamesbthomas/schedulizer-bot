# Test-Driven Development for the Server class

import pytest, sys, os, pickledb
project_root = os.path.split(os.path.dirname(__file__))[0]
print(project_root)
sys.path.append(os.path.join(project_root,"classes"))

# Import modules for testing
import server
import player

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
  client.addServer(
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

  testRaider = Role("testRaider",client.servers[0].name,"@testRaider",1111)
  testSocial = Role("testSocial",client.servers[0].name,"@testSocial",2222)
  testMember = Role("testMember",client.servers[0].name,"@testMember",3333)
  testPUG = Role("testPUG",client.servers[0].name,"@testPUG",4444)

  client.servers[0].mapRole(testRaider,"Raider")
  client.servers[0].mapRole(testSocial,"Social")
  client.servers[0].mapRole(testMember,"Member")
  client.servers[0].mapRole(testPUG,"PUG")

  try:
    # Tests
    assert client.servers[0].Raider == testRaider
    assert client.servers[0].Social == testSocial
    assert client.servers[0].Member == testMember
    assert client.servers[0].PUG == testPUG
    # Exception handling
    with pytest.raises(AttributeError,match="Unknown Schedule option"):
      client.servers[0].mapRole(testRaider,"bad")
    # Test DB writes
    assert client.servers[0].db.get("Raider") == testRaider.id
    assert client.servers[0].db.get("Social") == testSocial.id
    assert client.servers[0].db.get("Member") == testMember.id
    assert client.servers[0].db.get("PUG") == testPUG.id
  finally:
    # clear out DBs
    os.remove(os.path.join(project_root,"databases","rolesTest.db","server.db"))
    os.remove(os.path.join(project_root,"databases","rolesTest.db","roster.db"))
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
    os.rmdir(os.path.join(project_root,"databases","0001.db"))
    client.servers.pop(client.server_ids.index("0001"))
    client.server_ids.pop(client.server_ids.index("0001"))