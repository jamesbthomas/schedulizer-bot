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
    THEN a new Server object should be created and added to the Client object's list of servers
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