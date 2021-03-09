# Defines the Player class to track members of the raid team

class Player(object):

  def updatePlayer(self,sched=None,roles=[]):
    if sched != None:
      self.sched = sched
    if roles != []:
      self.roles = roles
    if sched == None and roles == []:
      raise TypeError("No options provided")

  def __str__(self):
    if self.roles != []:
      return "Name: "+self.name+"; Sched: "+self.sched+"; Roles: "+" > ".join(self.roles)
    else:
      return "Name: {0}; Sched: {1}; Roles: None".format(self.name,self.sched)

  def __init__(self,name,sched=None,roles=[]):
    self.name = name
    self.sched = sched
    self.roles = roles
    return