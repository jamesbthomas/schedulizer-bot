# Defines the Event class and associated subclasses
import datetime

class Event(object):

  def __init__(self,date: datetime.datetime,recurring: bool,description: str):
    if isinstance(date,datetime.datetime):
      self.date = date
    else:
      raise TypeError("\'date\' must be of type datetime")
    if isinstance(recurring,bool):
      self.recurring = recurring
    else:
      raise TypeError("\'recurring\' must be of type bool")
    if isinstance(description,str):
      self.description = description
    else:
      raise TypeError("\'description\' must be of type str")

class Raid(Event):
  # Used to signifiy a raid (for auto-cooking the roster)
  def __init__(self,date: datetime,recurring: bool,description: str):
    return