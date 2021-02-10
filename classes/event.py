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
    ## Helper function for picking players based on schedule
    def pickPlayer(role,players,sched):
      index = 0
      while index < len(players):
        picked = []
        p = players[index]
        if p.sched == sched:
          return p
        index += 1
      return None
    # Type checking
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
    self.tanks = []
    self.healers = []
    self.dps = []
    self.comp = []
    scheds = ["Raider","Social","Member","PUG"]
    # SELECT TANKS
    tanks_unsort = list(filter(lambda p: "Tank" in p.roles,roster))
    t = sorted(tanks_unsort,key=lambda p: p.roles.index("Tank"))
    tanks = sorted(t,key=lambda p: 0 if p.sched == "Raider" or p.sched =="Social" else 1 if p.sched == "Member" else 2)
    print("unsort",list(map(lambda p: p.name,tanks_unsort)))
    print("pref sort",list(map(lambda p: p.name,tanks)))
    print("sched sort",list(map(lambda p: p.name,tanks)))
    # If there are only two people, skip all the advanced logic
    if len(tanks) <= 2:
      self.tanks = tanks
    else: # We have more than two people who want to play tank
      # Select players who only play tank first (as long as they are not a PUG)
      index = 0
      while len(self.tanks) < 2 and index < len(tanks):
        tank = tanks[index]
        if tank.roles == ["Tank"] and tank.sched != "PUG":
          tanks.pop(index)
          self.tanks.append(tank)
        index += 1
      # Select Raider tanks, then Social tanks, then Member tanks, then PUG tanks
      index = 0
      while len(self.tanks) < 2 and index < len(scheds):
        pick = pickPlayer("Tank",tanks,scheds[index])
        if pick == None:
          index += 1
        else:
          tanks.pop(tanks.index(pick))
          self.tanks.append(pick)
    ## Remove those selected as tanks from the list of available players
    for t in self.tanks:
      roster.pop(roster.index(t))

    # SELECT HEALERS
    ## Determine composition
    ### number of healers is based on total number of players, 1x healer per 5 players
    if len(roster)+2 <= 10:
      self.comp = self.comps[0]
    elif len(roster)+2 <= 15:
      self.comp = self.comps[1]
    elif len(roster)+2 <= 20:
      self.comp = self.comps[2]
    elif len(roster)+2 <= 25:
      self.comp = self.comps[3]
    elif len(roster)+2 <= 30:
      self.comp = self.comps[4]
    else: # More than 30 people signed up for the raid
      # Filter out PUG players, then Member players, then Social players until we are under 30 people
      rev = scheds.reverse()
      index = 0
      while len(roster) > 30 and len(rev) < index:
        roster = list(filter(lambda p: p.sched != rev[index],roster))
        index += 1
      # Still too many people? throw an error
      if len(roster) > 30:
        raise ValueError("Too many Raiders")
      else:
        self.comp = self.comps[4]
    ## Pick healers
    healers = list(filter(lambda p: "Healer" in p.roles,roster))
    # If there are enough healers for the comp, skip the advanced logic
    if len(healers) <= self.comp[1]:
      self.healers = healers
    else: # We have more than two people who want to play tank
      # Select players who only play healer first (as long as they are not a PUG)
      index = 0
      while len(self.healers) < self.comp[1] and index < len(healers):
        healer = healers[index]
        if healer.roles == ["Healer"] and healer.sched != "PUG":
          healers.pop(index)
          self.healers.append(healer)
        index += 1
      # Select Raider tanks, then Social tanks, then Member tanks, then PUG tanks
      index = 0
      while len(self.healers) < 2 and index < len(scheds):
        pick = pickPlayer("Healer",healers,scheds[index])
        if pick == None:
          index += 1
        else:
          healers.pop(healers.index(pick))
          self.healers.append(pick)
    ## Remove those selected as healers from the list of available players
    for h in self.healers:
      roster.pop(roster.index(h))

    print(list(map(lambda p: p.name,roster)))
    print("TANKS - ",list(map(lambda p: p.name,self.tanks)))
    print("HEALERS - ",list(map(lambda p: p.name,self.healers)))
    # SELECT DPS
    ## already know how many we need, just gotta go by schedule priority
    dps = list(filter(lambda p: "DPS" in p.roles,roster))
    print("DPS - ",list(map(lambda p: p.name,dps)))
    # If there are enough healers for the comp, skip the advanced logic
    if len(dps) <= self.comp[2]:
      self.dps = dps
    else: # We have more than two people who want to play tank
      # Select players who only play healer first (as long as they are not a PUG)
      index = 0
      while len(self.dps) < self.comp[2] and index < len(dps):
        d = dps[index]
        if d.roles == ["DPS"] and d.sched != "PUG":
          dps.pop(index)
          self.dps.append(dps)
        index += 1
      # Select Raider tanks, then Social tanks, then Member tanks, then PUG tanks
      index = 0
      while len(self.dps) < self.comp[2] and index < len(scheds):
        pick = pickPlayer("DPS",dps,scheds[index])
        if pick == None:
          index += 1
        else:
          dps.pop(dps.index(pick))
          self.dps.append(pick)
    ## Remove those selected as healers from the list of available players
    for d in self.dps:
      roster.pop(roster.index(d))

    print("BREAKBREAKBREAK")

  def __init__(self,date: datetime,recurring: bool,description: str,frequency: str = None):
    super().__init__(date,recurring,description,frequency)
    self.comps = [[2,2,6],[2,3,10],[2,4,14],[2,5,18],[2,6,22]]
    return