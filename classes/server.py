# Defines the Server class and extends the Discord.Client class to track it

import discord, pickledb, os, player, event, datetime, hashlib
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
      ## make sure we dont already have this event
      if e in self.events:
        raise ValueError("Event exists")
      # Turn the event into a list for storage in the DB
      eList = [t,str(e.date),e.name,e.recurring,e.frequency]
      ## make sure we dont already have a recurring event with this name
      if e.name in self.events_db.getall() and e.recurring:
        raise ValueError("Recurring event with this name exists; mark event as not recurring or select a unique name")
      # add event to list of events
      self.events.append(e)
      # generate a unique identifier
      ## repeating events dont get an identifier
      if e.recurring:
        id = e.name
      ## one-time events are identified by the unique hash of the event name and date
      else:
        id_str = "{0}{1}".format(e.name,str(e.date))
        id = hashlib.md5(id_str.encode("utf-8")).hexdigest()
      self.events_db.set(id,eList)
      self.events_db.dump()
      return True

    def deleteEvent(self,name,type = None,date = None, time = None):
      ## get the number of events the name corresponds to
      es = list(filter(lambda e: e.name == name,self.events))
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
        if e.recurring:
          id = e.name
        else:
          id_str = "{0}{1}".format(e.name,str(e.date))
          id = hashlib.md5(id_str.encode("utf-8")).hexdigest()
        self.events_db.rem(id)
      self.events_db.dump()
      ### from the list
      self.events = list(filter(lambda e: e not in es,self.events))

    def setEvent(self,type,name,prop,val,d = None):
      ## get total number of events to change
      es = list(filter(lambda e: e.name == name,self.events))
      numEvents = len(es)
      if numEvents < 1:
        raise ValueError("Unknown Event")
      ## type checking
      if type == "one" and (d == None):
        if numEvents > 1:
          raise ValueError("Operation type \'one\' must have a unique name OR inputs for \'date\' and \'time\'")
      elif type == "one":
        es = list(filter(lambda e: e.date == d,es))
        numEvents = len(es)
        if numEvents < 1:
          raise ValueError("Matching event found with incorrect inputs \'date\' or \'time\'")
      elif type == "all":
        if prop == "recurring":
          raise ValueError("Operation \'all\' cannot be used to change event \'recurring\' status")
        elif prop == "frequency":
          raise ValueError("Operation \'all\' cannot be used to change event frequency")
      ## iterate through list of events to change (es)
      for e in es:
        ## pull out the event we're modifying
        index = self.events.index(e)
        if e.recurring:
          id = e.name
        else:
          id_str = "{0}{1}".format(e.name,str(e.date))
          id = hashlib.md5(id_str.encode("utf-8")).hexdigest()
        e_db = self.events_db.get(id)
        ## modify event based on the value of prop
        if prop == "date":
          e.date = e.date.replace(year=val.year,month=val.month,day=val.day)
        elif prop == "time":
          e.date = e.date.replace(hour=val.hour,minute=val.minute)
        elif prop == "name":
          e.name = val
        elif prop == "recurring":
          e.recurring = val
          if not e.recurring:
            e.frequency = None
        elif prop == "frequency":
          if not e.recurring:
            raise ValueError("Cannot change frequency for one-time event")
          e.frequency = val
        else:
          raise ValueError("Unknown property")
        self.events_db.rem(id)
        ## build the list for storing in the database
        eList = [e_db[0],str(e.date),e.name,e.recurring,e.frequency]
        ## rebuild the id for the event
        if e.recurring:
          id = e.name
        else:
          id_str = "{0}{1}".format(e.name,str(e.date))
          id = hashlib.md5(id_str.encode("utf-8")).hexdigest()
        # add the event to the database
        self.events_db.set(id,eList)

    def getEvents(self):
      self.events_db = pickledb.load(os.path.join(self.db_path,"events.db"),False)
      keys = self.events_db.getall()
      for k in keys:
        dbevent = self.events_db.get(k)
        if dbevent[0] == "raid":
          e = event.Raid(datetime.datetime.fromisoformat(dbevent[1]),dbevent[2],dbevent[3],dbevent[4])
        elif dbevent[0] == "event":
          e = event.Event(datetime.datetime.fromisoformat(dbevent[1]),dbevent[2],dbevent[3],dbevent[4])
        else:
          continue
        self.events.append(e)
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