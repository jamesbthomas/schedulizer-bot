# Test-Driven Development for the Server class

import pytest
import sys
import os
project_root = os.path.split(os.path.dirname(__file__))[0]
print(project_root)
sys.path.append(os.path.join(project_root,"classes"))

# Import modules for testing
import server
import player

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
    assert client.servers[0].db != None
    assert client.servers[1].db_path == os.path.join(project_root,"databases","test2.db")
    assert client.servers[1].db != None

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

  # Create test Role based on discord.Role but only with features that I might care about checking later
  class Role(object):
    def __init__(self,name,guild,mention):
      self.name = name
      self.guild = guild
      self.mention = mention

  testRaider = Role("testRaider",client.servers[0].name,"@testRaider")
  testSocial = Role("testSocial",client.servers[0].name,"@testSocial")
  testMember = Role("testMember",client.servers[0].name,"@testMember")
  testPUG = Role("testPUG",client.servers[0].name,"@testPUG")

  client.servers[0].mapRole(testRaider,"Raider")
  client.servers[0].mapRole(testSocial,"Social")
  client.servers[0].mapRole(testMember,"Member")
  client.servers[0].mapRole(testPUG,"PUG")

  # Tests
  assert client.servers[0].Raider == testRaider
  assert client.servers[0].Social == testSocial
  assert client.servers[0].Member == testMember
  assert client.servers[0].PUG == testPUG
  with pytest.raises(AttributeError,match="Unknown Schedule option"):
    client.servers[0].mapRole(testRaider,"bad")
  # Test exception handling

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

  # Tests
  ## Add to empty roster
  s.updateRoster(fullPlayer)
  assert s.roster[0] == fullPlayer
  s.updateRoster(schedPlayer)
  assert s.roster[1] == schedPlayer
  s.updateRoster(rolesPlayer)
  assert s.roster[2] == rolesPlayer
  assert s.roster == roster
  ## Change/Add schedules
  newFull = player.Player("testPlayer#1111",sched="Raider",roles=["Tank","DPS"])
  newSched = player.Player("testPlayer#2222",sched="Social")
  newRoles = player.Player("testPlayer#3333",sched="Member",roles=["Healer","DPS"])
  newRoster = [newFull,newSched,newRoles]
  s.updateRoster(newFull)
  assert s.roster[0] == newFull
  s.updateRoster(newSched)
  assert s.roster[1] == newSched
  s.updateRoster(newRoles)
  assert s.roster[2] == newRoles
  assert s.roster == newRoster
  ### Reset for next battery
  s.roster = roster
  ## Change/add Roles
  newerFull = player.Player("testPlayer#1111",sched="Raider",roles=["Tank"])
  newerSched = player.Player("testPlayer#2222",sched="Social",roles=["DPS"])
  newerRoles = player.Player("testPlayer#3333",roles=["Tank","Healer","DPS"])
  newerRoster = [newerFull,newerSched,newerRoles]
  s.updateRoster(newerFull)
  assert s.roster[0] == newerFull
  s.updateRoster(newerSched)
  assert s.roster[1] == newerSched
  s.updateRoster(newerRoles)
  assert s.roster[2] == newerRoles
  assert s.roster == newerRoster
  ### reset for next battery
  s.roster = roster
  ## Remove sched
  fullSched = player.Player("testPlayer#1111",roles=["Tank","DPS"])
  schedSched = player.Player("testPlayer#2222")
  rolesSched = player.Player("testPlayer#3333",roles=["Healer","DPS"])
  schedRoster = [fullSched,schedSched,rolesSched]
  s.updateRoster(fullSched)
  assert s.roster[0] == fullSched
  s.updateRoster(schedSched)
  assert s.roster[1] == schedSched
  s.updateRoster(rolesSched)
  assert s.roster[2] == rolesSched
  assert s.roster == schedRoster
  ### reset for next battery
  s.roster = roster
  ## Remove roles
  fullRoles = player.Player("testPlayer#1111",sched="Social")
  schedRoles = player.Player("testPlayer#2222",sched="Raider")
  rolesRoles = player.Player("testPlayer#3333")
  rolesRoster = [fullRoles,schedRoles,rolesRoles]
  s.updateRoster(fullRoles)
  assert s.roster[0] == fullRoles
  s.updateRoster(schedRoles)
  assert s.roster[1] == schedRoles
  s.updateRoster(rolesRoles)
  assert s.roster[2] == rolesRoles
  assert s.roster == rolesRoster