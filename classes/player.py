# Defines the Player class to track members of the raid team

class Player(object):

  def updatePlayer(self,sched=None,roles=None):
    if sched != None:
      self.sched = sched
    if roles != None:
      self.roles = roles
    if sched == None and roles == None:
      raise TypeError("No options provided")

  def __str__(self):
    try:
      return "Name: "+self.name+"; Sched: "+self.sched+"; Roles: "+" > ".join(self.roles)
    except:
      return "Name: {0}; Sched: {1}; Roles: {2}".format(self.name,self.sched,self.roles)

  def __init__(self,name,sched=None,roles=None):
    self.name = name
    self.sched = sched
    self.roles = roles
    return