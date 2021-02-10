# Test-Driven Development for the Event class
import pytest
import sys
import os
import re
import datetime
project_root = os.path.split(os.path.dirname(__file__))[0]
sys.path.append(os.path.join(project_root,"classes"))

# Import module for testing
import event, player

def test_makeEvent():
  """
  GIVEN Event constructor and appropriate inputs
  WHEN the method is called
  THEN create and return a correctly structured Event object
  """
  # Test expected use
  ## Datetime constructor: year, month, day, hour, minute, second
  d = datetime.datetime(1970,1,1,0,0,0)
  recurring = event.Event(d,True,"recurring event","weekly")
  once = event.Event(d,False,"event that occurs once")

  assert recurring.date == d
  assert recurring.recurring == True
  assert recurring.description == "recurring event"
  assert recurring.frequency == "weekly"
  assert once.date == d
  assert once.recurring == False
  assert once.description == "event that occurs once"
  assert once.frequency == None
  # Test bad datatypes
  ## bad date
  with pytest.raises(TypeError):
    badDate = event.Event("1970-01-01 00:00:00",True,"has a bad date")
  ## bad recurring
  with pytest.raises(TypeError):
    badRecurring = event.Event(d,"true","has bad recurring")
  ## bad description
  with pytest.raises(TypeError):
    badDescription = event.Event(d,True,123)
  with pytest.raises(TypeError):
    badFreq = event.Event(d,True,"123",123)

def test_makeRaid():
  """
  GIVEN Raid constructor and appropriate inputs
  WHEN the method is called
  THEN create and return a correctly structured Event object
  """

  d = datetime.datetime(1970,1,1,0,0,0)
  recurring = event.Raid(d,True,"recurring raid","weekly")
  once = event.Raid(d,False,"raid occurs once")
  comps = [[2,2,6],[2,3,10],[2,4,14],[2,5,18],[2,6,22]]

  assert recurring.date == d
  assert recurring.recurring == True
  assert recurring.description == "recurring raid"
  assert recurring.frequency == "weekly"
  assert recurring.comps == comps
  assert once.date == d
  assert once.recurring == False
  assert once.description == "raid occurs once"
  assert once.comps == comps

def test_cookRaid():
  """
  GIVEN Raid object and a roster of unique Player objects (tests won't be unique because I don't want to build that many DPS objects)
  WHEN the method is called
  THEN select the most appropriate composition and assign Players to roles that generate the highest utility based on player preference and fewest required PUGs
  """

  ## Create Raider Schedule objects
  tankHealerDPSR = player.Player("TankHealerDPSR","Raider",["Tank","Healer","DPS"])
  healerTankDPSR = player.Player("HealerTankDPSR","Raider",["Healer","Tank","DPS"])
  tankDPSHealerR = player.Player("TankDPSHealerR","Raider",["Tank","DPS","Healer"])
  healerDPSTankR = player.Player("HealerDPSTankR","Raider",["Healer","DPS","Tank"])
  DPSTankHealerR = player.Player("DPSTankHealerR","Raider",["DPS","Tank","Healer"])
  DPSHealerTankR = player.Player("DPSHealerTankR","Raider",["DPS","Healer","Tank"])
  tankR = player.Player("TankR","Raider",["Tank"])
  healerR = player.Player("HealerR","Raider",["Healer"])
  DPSR = player.Player("DPSR","Raider",["DPS"])
  ## Create Social Schedule Objects
  tankHealerDPSS = player.Player("TankHealerDPSS","Social",["Tank","Healer","DPS"])
  healerTankDPSS = player.Player("HealerTankDPSS","Social",["Healer","Tank","DPS"])
  tankDPSHealerS = player.Player("TankDPSHealerS","Social",["Tank","DPS","Healer"])
  healerDPSTankS = player.Player("HealerDPSTankS","Social",["Healer","DPS","Tank"])
  DPSTankHealerS = player.Player("DPSTankHealerS","Social",["DPS","Tank","Healer"])
  DPSHealerTankS = player.Player("DPSHealerTankS","Social",["DPS","Healer","Tank"])
  tankS = player.Player("TankS","Social",["Tank"])
  healerS = player.Player("HealerS","Social",["Healer"])
  DPSS = player.Player("DPSS","Social",["DPS"])
  ## Create Member Player Objects
  tankHealerDPSM = player.Player("TankHealerDPSM","Member",["Tank","Healer","DPS"])
  healerTankDPSM = player.Player("HealerTankDPSM","Member",["Healer","Tank","DPS"])
  tankDPSHealerM = player.Player("TankDPSHealerM","Member",["Tank","DPS","Healer"])
  healerDPSTankM = player.Player("HealerDPSTankM","Member",["Healer","DPS","Tank"])
  DPSTankHealerM = player.Player("DPSTankHealerM","Member",["DPS","Tank","Healer"])
  DPSHealerTankM = player.Player("DPSHealerTankM","Member",["DPS","Healer","Tank"])
  tankM = player.Player("TankM","Member",["Tank"])
  healerM = player.Player("HealerM","Member",["Healer"])
  DPSM = player.Player("DPSM","Member",["DPS"])
  ## Create PUG Player Objects
  tankHealerDPSP = player.Player("TankHealerDPSP","PUG",["Tank","Healer","DPS"])
  healerTankDPSP = player.Player("HealerTankDPSP","PUG",["Healer","Tank","DPS"])
  tankDPSHealerP = player.Player("TankDPSHealerP","PUG",["Tank","DPS","Healer"])
  healerDPSTankP = player.Player("HealerDPSTankP","PUG",["Healer","DPS","Tank"])
  DPSTankHealerP = player.Player("DPSTankHealerP","PUG",["DPS","Tank","Healer"])
  DPSHealerTankP = player.Player("DPSHealerTankP","PUG",["DPS","Healer","Tank"])
  tankP = player.Player("TankP","PUG",["Tank"])
  healerP = player.Player("HealerP","PUG",["Healer"])
  DPSP = player.Player("DPSP","PUG",["DPS"])

  # Create the Raid event
  raid = event.Raid(datetime.datetime(1970,1,1,0,0,0),False,"Raid.cook() Test")

  # Tests for input types
  with pytest.raises(TypeError,match=re.escape("\'roster\' must be of type *list[Player]")):
    raid.cook("bad roster")
  with pytest.raises(TypeError,match=re.escape("\'roster\' must be of type list[*Player]")):
    raid.cook(["bad roster"])
  with pytest.raises(TypeError,match=re.escape("\'depth\' must be of type *list[list[Player]] or None")):
    raid.cook([tankR],"bad depth chart")
  with pytest.raises(TypeError,match=re.escape("\'depth\' must be of type list[*list[Player]] or None")):
    raid.cook([tankR],["bad depth chart"])
  with pytest.raises(TypeError,match=re.escape("\'depth\' must be of type list[list[*Player]] or None")):
    raid.cook([tankR],[["bad depth chart"]])

  # Tests by raid size
  ## 10 Players
  ### All Members/Social/Raiders playing only their top role
  roster = [tankR,tankM,healerR,healerS,DPSR,DPSR,DPSR,DPSR,DPSS,DPSM]
  raid.cook(roster)
  assert raid.tanks == [tankR,tankM]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,healerS].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,DPSS,DPSM].sort(key=lambda p: p.name)
  assert raid.comp == [2,2,6]
  ### Select Raiders to tank and heal before other members
  roster = [tankR,tankDPSHealerS,healerR,healerDPSTankS,DPSR,DPSR,DPSR,DPSR,DPSHealerTankR,DPSTankHealerR]
  raid.cook(roster)
  assert raid.tanks == [tankR,DPSTankHealerR]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,DPSHealerTankR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,tankDPSHealerS,healerDPSTankS].sort(key=lambda p: p.name)
  assert raid.comp == [2,2,6]
  roster = [tankR,tankDPSHealerM,healerR,healerDPSTankM,DPSR,DPSR,DPSR,DPSR,DPSHealerTankR,DPSTankHealerR]
  raid.cook(roster)
  assert raid.tanks == [tankR,DPSTankHealerR]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,DPSHealerTankR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,tankDPSHealerM,healerDPSTankM].sort(key=lambda p: p.name)
  assert raid.comp == [2,2,6]
  ## 11 Players
  ### All Members/Social/Raiders should select larger composition
  roster = [tankR,tankM,healerR,healerS,DPSR,DPSR,DPSR,DPSR,DPSS,DPSM,DPSR]
  raid.cook(roster)
  assert raid.tanks == [tankR,tankM]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,healerS].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,DPSS,DPSM,DPSR].sort(key=lambda p: p.name)
  assert raid.comp == [2,3,10]
  ### Extra PUG should select lower composition
  roster = [tankR,tankM,healerR,healerS,DPSR,DPSR,DPSR,DPSR,DPSS,DPSM,DPSP]
  raid.cook(roster)
  assert raid.tanks == [tankR,tankM]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,healerR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,DPSR,DPSR].sort(key=lambda p: p.name)
  assert raid.comp == [2,2,6]
  ### Should prefer healers instead of dps for extra
  roster = [tankR,tankM,healerR,healerS,DPSR,DPSR,DPSR,DPSR,DPSS,DPSM,DPSHealerTankR]
  raid.cook(roster)
  assert raid.tanks == [tankR,tankM]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,healerR,DPSHealerTankR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,DPSR,DPSR].sort(key=lambda p: p.name)
  assert raid.comp == [2,3,10]
  roster = [tankR,tankM,healerR,healerS,DPSR,DPSR,DPSR,DPSR,DPSS,DPSM,DPSTankHealerR]
  raid.cook(roster)
  assert raid.tanks == [tankR,tankM]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,healerR,DPSTankHealerR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,DPSR,DPSR].sort(key=lambda p: p.name)
  assert raid.comp == [2,3,10]
  ### Should prefer dps instead of tanks for extra
  roster = [tankR,tankR,healerR,healerR,DPSR,DPSR,DPSR,DPSR,DPSR,DPSR,tankDPSHealerR]
  raid.cook(roster)
  assert raid.tanks == [tankR,tankR]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,healerR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,DPSR,DPSR,tankDPSHealerR].sort(key=lambda p: p.name)
  assert raid.comp == [2,3,10]
  roster = [tankR,tankR,healerR,healerR,DPSR,DPSR,DPSR,DPSR,DPSR,DPSR,tankHealerDPSR]
  raid.cook(roster)
  assert raid.tanks == [tankR,tankR]
  assert raid.healers.sort(key=lambda p: p.name)== [healerR,healerR,tankHealerDPSR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [DPSR,DPSR,DPSR,DPSR,DPSR,DPSR].sort(key=lambda p: p.name)
  assert raid.comp == [2,3,10]
  ## 15 Players should select [2,3,10]
  roster = [tankHealerDPSR] * 15
  raid.cook(roster)
  assert raid.comp == [2,3,10]
  ## 16 Players should select [2,4,14]
  roster = [tankHealerDPSR] * 16
  raid.cook(roster)
  assert raid.comp == [2,4,14]
  ## 20 Players should select [2,4,14]
  roster = [tankHealerDPSR] * 20
  raid.cook(roster)
  assert raid.comp == [2,4,14]
  ## 21 Players should select [2,5,18]
  roster = [tankHealerDPSR] * 21
  raid.cook(roster)
  assert raid.comp == [2,5,18]
  ## 25 Players should select [2,5,18]
  roster = [tankHealerDPSR] * 25
  raid.cook(roster)
  assert raid.comp == [2,5,18]
  ## 26 Players should select [2,6,22]
  roster = [tankHealerDPSR] * 26
  raid.cook(roster)
  assert raid.comp == [2,6,22]
  ## 30 Players should select [2,6,22]
  roster = [tankHealerDPSR] * 30
  raid.cook(roster)
  assert raid.comp == [2,6,22]
  # Test for error checking
  ## 31 Players with Raider schedule throws ValueError
  roster = [tankHealerDPSR]*30
  roster += [tankHealerDPSR]
  with pytest.raises(ValueError,match="Too many Raiders"):
    raid.cook(roster)
  ## 30 Players with Raider schedule and 1 without does not throw error
  ### Social schedule
  roster = [tankHealerDPSR]*30
  roster += [tankHealerDPSS]
  raid.cook(roster)
  assert raid.tanks == [tankHealerDPSR,tankHealerDPSR]
  assert raid.healers.sort(key=lambda p: p.name)== [tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR].sort(key=lambda p: p.name)
  assert raid.comp == [2,6,22]
  ### Member schedule
  roster = [tankHealerDPSR]*30
  roster += [tankHealerDPSM]
  raid.cook(roster)
  assert raid.tanks == [tankHealerDPSR,tankHealerDPSR]
  assert raid.healers.sort(key=lambda p: p.name)== [tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR].sort(key=lambda p: p.name)
  assert raid.comp == [2,6,22]
  ### PUG schedule
  roster = [tankHealerDPSR]*30
  roster += [tankHealerDPSP]
  raid.cook(roster)
  assert raid.tanks == [tankHealerDPSR,tankHealerDPSR]
  assert raid.healers.sort(key=lambda p: p.name)== [tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR].sort(key=lambda p: p.name)
  assert raid.dps.sort(key=lambda p: p.name)== [tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR,tankHealerDPSR].sort(key=lambda p: p.name)
  assert raid.comp == [2,6,22]

  # Test for proper depth chart handling
  ## TODO - write tests