# Defines the Player class to track members of the raid team

class Player(object):

  def updatePlayer(self,sched=None,roles=None):
    if sched != None:
      self.sched = sched
    if roles != None:
      self.roles = roles
    if sched == None and roles == None:
      raise TypeError("No options provided")

  def __init__(self,name,sched=None,roles=None):
    self.name = name
    self.sched = sched
    self.roles = roles
    return