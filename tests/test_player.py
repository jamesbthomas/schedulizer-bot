# Test-Driven Development for the Player class

import pytest
import sys
import os
project_root = os.path.split(os.path.dirname(__file__))[0]
print(project_root)
sys.path.append(os.path.join(project_root,"classes"))

# Import module for testing
import player

def test_makePlayer():
    """
    GIVEN Player constructor and appropriate inputs
    WHEN the method is called
    THEN create and return a correctly structured Player object; should be able to handle when provided with a list of roles and when not
    """

    named = player.Player("testPlayer#1111","Raider")
    roled = player.Player("testPlayer#2222",sched="Social",roles=["Tank","DPS"])

    assert named.name == "testPlayer#1111"
    assert named.sched == "Raider"
    assert named.roles == []
    assert roled.name == "testPlayer#2222"
    assert roled.sched == "Social"
    assert roled.roles == ["Tank","DPS"]

def test_updatePlayer():
  """
  GIVEN constructed Player and appropriate inputs
  WHEN the method is called
  THEN update the attributed of the Player object based on whatever is provided
  """
  p = player.Player("testPlayer#1111")

  # Update schedule from None
  assert p.sched == None
  p.updatePlayer(sched="Raider")
  assert p.sched == "Raider"
  # Update schedule from set value
  p.updatePlayer(sched="Social")
  assert p.sched == "Social"

  # Update roles from None
  assert p.roles == []
  p.updatePlayer(roles=["Tank"])
  assert p.roles == ["Tank"]
  # Update roles from set value
  p.updatePlayer(roles=["Tank","DPS"])
  assert p.roles == ["Tank","DPS"]

  # Graceful error if no options provided
  with pytest.raises(TypeError,match="No options provided"):
    p.updatePlayer()
  assert p.name == "testPlayer#1111"
  assert p.sched == "Social"
  assert p.roles == ["Tank","DPS"]