# Test-Driven Development

import pytest
import sys
import os
project_root = os.path.split(os.path.dirname(__file__))[0]
print(project_root)
sys.path.append(os.path.join(project_root,"classes"))

# Import modules for testing
import server

def test_addServer():
    """
    GIVEN server.addServer method with valid inputs
    WHEN the method is called
    THEN a new Server object should be created and added to the Client object's list of servers; the Server objects track more detailed information than the Guild objects provided by discord
    """
    
    client = server.SchedClient()
    
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

def test_mapRoles():
  """
  GIVEN server.mapRoles method with template inputs (constructing a discord.Role object manually is annoying and I don't have a good reason to extend it)
  WHEN the method is called
  THEN the Server attributes for each schedulizer role should be mapped to the role for that server
  """

  client = server.SchedClient()

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
