# Defines the Server class and extends the Discord.Client class to track it

import discord, pickledb, os, player, event, datetime
from discord.ext import commands

class Server(object):
    # Class for tracking properties by server

    def addEvent(self,e):
      ## do some light error checking
      if isinstance(e,event.Raid):
        t = "raid"
      elif isinstance(e,event.Event):
        t = "event"
      else:
        raise TypeError("Input must be a propertly constructed Event or Raid object")
      ## make sure we dont already have an event with this name
      if e in self.events:
        raise ValueError("Event exists")
      ## Adds an event object to this instance and the database
      index = len(self.events)
      self.events.insert(index,e)
      # Turn the event into a list for storage in the DB
      eList = [t,str(e.date),e.description,e.recurring,e.frequency]
      self.events_db.set(str(index),eList)
      self.events_db.dump()
      return True

    def deleteEvent(self,name,type = None,date = None, time = None):
      ## get the number of events the name corresponds to
      es = list(filter(lambda e: e.description == name,self.events))
      numEvents = len(es)
      if numEvents < 1:
        raise ValueError("Unknown Event")
      ## Make sure inputs make sense
      if type == "one" and (date == None or time == None):
        if numEvents > 1:
          raise ValueError("Operation type \'one\' must have a unique name OR inputs for \'date\' and \'time\'")
      ## find the item(s) to delete
      if date != None:
        es = list(filter(lambda e: e.date.strftime("%d%b%Y").upper() == date,es))
        if time != None:
          es = list(filter(lambda e: e.date.strftime("%H:%M") == time,es))
      ### from the database
      for e in es:
        i = self.events.index(e)
        self.events_db.rem(str(i))
      self.events_db.dump()
      ### from the list
      self.events = list(filter(lambda e: e not in es,self.events))

      ## TODO - need better keys for the event db

    def getEvents(self):
      self.events_db = pickledb.load(os.path.join(self.db_path,"events.db"),False)
      events = self.events_db.getall()
      for i in events:
        dbevent = self.events_db.get(i)
        if dbevent[0] == "raid":
          e = event.Raid(datetime.datetime.fromisoformat(dbevent[1]),dbevent[3],dbevent[2],dbevent[4])
        elif dbevent[0] == "event":
          e = event.Event(datetime.datetime.fromisoformat(dbevent[1]),dbevent[3],dbevent[2],dbevent[4])
        else:
          continue
        self.events.insert(int(i),e)
      return
    
    def getRoles(self,roles):
      self.db = pickledb.load(os.path.join(self.db_path,"server.db"), False)
      self.Raider = discord.utils.find(lambda r: r.id == self.Raider,roles)
      self.Social = discord.utils.find(lambda r: r.id == self.Social,roles)
      self.Member = discord.utils.find(lambda r: r.id == self.Member,roles)
      self.PUG = discord.utils.find(lambda r: r.id == self.PUG,roles)
      return
     
    def getRoster(self):
      self.roster_db = pickledb.load(os.path.join(self.db_path,"roster.db"),False)
      names = self.roster_db.getall()
      for name in names:
        playerSettings = self.roster_db.get(name)
        p = player.Player(name,sched=playerSettings[0],roles=playerSettings[1])
        self.roster.append(p)
      return

    def mapRole(self,role,sched):
      ## TODO - handle this more gracefully
      if role == None:
        return
      elif sched == "Raider":
        self.Raider = role
        self.db.set("Raider",role.id)
      elif sched == "Social":
        self.Social = role
        self.db.set("Social",role.id)
      elif sched == "Member":
        self.Member = role
        self.db.set("Member",role.id)
      elif sched == "PUG":
        self.PUG = role
        self.db.set("PUG",role.id)
      else:
        raise AttributeError("Unknown Schedule option")
      self.db.dump()
      return

    def updateRoster(self,player):
      try:
        i = self.roster_names.index(player.name)
        self.roster.pop(i)
        self.roster.insert(i,player)
      except ValueError:
        self.roster.append(player)
        self.roster_names.append(player.name)
      self.roster_db.set(player.name,[player.sched,player.roles])
      self.roster_db.dump()
      return
    
    def __init__(self,id,name,owner):
        self.id = id
        self.name = name
        self.owner = owner
        # List of player objects in this server
        ## TODO - turn this into a dictionary, key is the name value is the object
        self.roster = []
        self.roster_names = []
        # For tracking the discord.Role objects on this server that correspond to our schedules
        self.Raider = None
        self.Social = None
        self.Member = None
        self.PUG = None
        # Create the database file for this server
        project_root = os.path.split(os.path.dirname(__file__))[0]
        try:
          os.makedirs(os.path.join(project_root,"databases",str(id)+".db"))
        except FileExistsError:
          None
        self.db_path = os.path.join(project_root,"databases",str(id)+".db")
        self.db = pickledb.load(os.path.join(self.db_path,"server.db"), False)
        self.db.set('id',id)
        self.db.set('name',name)
        self.db.set('owner',str(owner))
        self.Raider = self.db.get("Raider") or None
        self.Social = self.db.get("Social") or None
        self.Member = self.db.get("Member") or None
        self.PUG = self.db.get("PUG") or None
        self.db.dump()
        # Create the database file for this server's roster
        self.roster_db = pickledb.load(os.path.join(self.db_path,"roster.db"),False)
        self.roster_db.dump()
        # Setup event tracking for this server
        ## List of Event objects that will occur at some point in the future
        ### List includes instances of recurring events, not the recurring events themselves
        self.events = []
        ## create the database for this server's events
        self.events_db = pickledb.load(os.path.join(self.db_path,"events.db"),False)
        self.events_db.dump()


class SchedClient(commands.Bot):

    ## TODO - turn this into a dictionary, key is the server_id value is the object
    servers = []
    server_ids = []

    def setup(self):
        # Initialize attributes
        self.servers = []
        self.server_ids = []
        # Read in pickledb databases from database
        project_root = os.path.split(os.path.dirname(__file__))[0]
        ## TODO do some startup logging here for if this is a brand new install or if there are db files to read in and load
        for f in os.listdir(path=os.path.join(project_root,"databases")):
          if f != "README.md":
            db = pickledb.load(os.path.join(project_root,"databases",f,"server.db"),False)
            id = db.get('id')
            server = Server(id,db.get('name'),db.get('owner'))
            self.servers.append(server)
            self.server_ids.append(id)
          else:
            continue

    def addServer(self,id,name,owner):
        if id in self.server_ids:
            raise FileExistsError("Server already known")
        else:
            server = Server(id,name,owner)
            self.servers.append(server)
            self.server_ids.append(id)
            return server