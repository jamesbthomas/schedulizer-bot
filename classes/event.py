# Defines the Event class and associated subclasses
import datetime, os, sys
project_root = os.path.split(os.path.dirname(__file__))[0]
print(project_root)
sys.path.append(os.path.join(project_root,"classes"))
import player

class Event(object):

  def __init__(self,date: datetime.datetime,recurring: bool,description: str,frequency: str = None):
    if isinstance(date,datetime.datetime):
      self.date = date
    else:
      raise TypeError("\'date\' must be of type datetime")
    if isinstance(recurring,bool):
      if recurring:
        if isinstance(frequency,str):
          self.recurring = recurring
          self.frequency = frequency
        else:
          raise TypeError("\'frequency\' must be of type str")
      else:
        self.recurring = False
        self.frequency = None
    else:
      raise TypeError("\'recurring\' must be of type bool")
    if isinstance(description,str):
      self.description = description
    else:
      raise TypeError("\'description\' must be of type str")

class Raid(Event):
  # Used to signifiy a raid (for auto-cooking the roster)

  def cook(self,roster: list,depth: list = None):
    if not isinstance(roster,list):
      raise TypeError("\'roster\' must be of type *list[Player]")
    if not isinstance(roster[0],player.Player):
      raise TypeError("\'roster\' must be of type list[*Player]")
    if depth != None:
      if not isinstance(depth,list):
        raise TypeError("\'depth\' must be of type *list[list[Player]] or None")
      if not isinstance(depth[0],list):
        raise TypeError("\'depth\' must be of type list[*list[Player]] or None")
      if not isinstance(depth[0][0],player.Player):
        raise TypeError("\'depth\' must be of type list[list[*Player]] or None")

  def __init__(self,date: datetime,recurring: bool,description: str,frequency: str = None):
    super().__init__(date,recurring,description,frequency)
    self.comps = [[2,2,6],[2,3,10],[2,4,14],[2,5,18],[2,6,22]]
    return