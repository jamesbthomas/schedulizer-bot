# Test-Driven Development for the Event class
import pytest
import sys
import os
import datetime
project_root = os.path.split(os.path.dirname(__file__))[0]
print(project_root)
sys.path.append(os.path.join(project_root,"classes"))

# Import module for testing
import event

def test_makeEvent():
  """
  GIVEN Event constructor and appropriate inputs
  WHEN the method is called
  THEN create and return a correctly structured Event object
  """
  # Test expected use
  ## Datetime constructor: year, month, day, hour, minute, second
  d = datetime.datetime(1970,1,1,0,0,0)
  recurring = event.Event(d,True,"recurring event")
  once = event.Event(d,False,"event that occurs once")

  assert recurring.date == d
  assert recurring.recurring == True
  assert recurring.description == "recurring event"
  assert once.date == d
  assert once.recurring == False
  assert once.description == "event that occurs once"
  # Test bad datatypes
  ## bad date
  with pytest.raises(TypeError):
    badDate = event.Event("1970-01-01 00:00:00",True,"has a bad date")
    print(badDate.date)
    print(type(badDate.date))
  ## bad recurring
  with pytest.raises(TypeError):
    badRecurring = event.Event(d,"true","has bad recurring")
  ## bad description
  with pytest.raises(TypeError):
    badDescription = event.Event(d,True,123)

def test_makeRaid():
  """
  GIVEN Raid constructor and appropriate inputs
  WHEN the method is called
  THEN create and return a correctly structured Event object
  """

  assert True
  return