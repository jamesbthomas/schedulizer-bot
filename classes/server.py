# Defines the Server class and extends the Discord.Client class to track it

import discord, pickledb, sys, os, player, event, datetime, hashlib, threading, logging, logging.handlers
from discord.ext import commands

class Server(object):
    # Class for tracking properties by server

    def addPlayer(self,p,e):
      # type checking
      if not isinstance(p,player.Player):
        self.logger.error("Input \'player\' must be a properly constructed Player object")
        raise TypeError("Input \'player\' must be a properly constructed Player object")
      if not isinstance(e,event.Event) and not isinstance(e,event.Raid):
        self.logger.error("Input \'event\' must be a properly constructed Event or Raid object")
        raise TypeError("Input \'event\' must be a properly constructed Event or Raid object")
      ## grab the lock
      self.event_lock.acquire()
      ## check to see if the player is already signed up
      if p in e.roster:
        self.event_lock.release()
        self.logger.info("Player {0} already signed up for event {1}".format(p.name,e.name))
        raise ValueError("Player {0} already signed up for event {1}".format(p.name,e.name))
      # add the player to the roster of the event
      e.roster.append(p)
      # if raid, cook and return
      if isinstance(e,event.Raid):
        e.cook()
        if p in e.tanks:
          ret = "Tank"
        elif p in e.healers:
          ret = "Healer"
        elif p in e.dps:
          ret = "DPS"
        else:
          if p in e.roster and p.roles != []:
            self.event_lock.release()
            self.logger.critical("Player not added to roster because could not assign a valid role")
            raise RuntimeError("Player {0} NOT added to roster, could not assign a valid role".format(p.name))
          elif p not in e.roster:
            self.event_lock.release()
            self.logger.critical("Player not added to roster")
            raise RuntimeError("Player {0} not added to roster".format(p.name))
          elif p.roles == []:
            self.logger.info("Player added to roster but has no roles")
            ret = "None"
      else:
        ret = p in e.roster

      ## add to db and dump
      if e.recurring:
        id = e.name
      else:
        id = hashlib.md5("{0}{1}".format(e.name,str(e.date)).encode("utf-8")).hexdigest()
      self.events_db.set(id,e.dump())
      self.events_db.dump()
      ## release lock
      self.event_lock.release()

      return ret

    def removePlayer(self,p,e):
      # type checking
      if not isinstance(p,player.Player):
        self.logger.error("Input \'player\' must be a properly constructed Player object")
        raise TypeError("Input \'player\' must be a properly constructed Player object")
      if not isinstance(e,event.Event) and not isinstance(e,event.Raid):
        self.logger.error("Input \'event\' must be a properly constructed Event or Raid object")
        raise TypeError("Input \'event\' must be a properly constructed Event or Raid object")
      # remove the player from the roster
      self.event_lock.acquire()
      try:
        e.roster.remove(p)
      except ValueError as err:
        if str(err) == "list.remove(x): x not in list":
          self.logger.info("Player {0} not signed up for event {1}".format(p.name,e.name))
          ## catch this exception on the other end
          raise ValueError("Player {0} not signed up for event {1}".format(p.name,e.name))
        else:
          self.logger.critical("Unknown error: {0}".format(str(err)))
          raise err
      ## cook if its a raid
      if isinstance(e,event.Raid):
        self.logger.info("Re-Cooking event {0}".format(e.name))
        e.cook()
      # get the ID for this event
      if e.recurring:
        id = e.name
      else:
        id = hashlib.md5("{0}{1}".format(e.name,str(e.date)).encode("utf-8")).hexdigest()
      self.events_db.set(id,e.dump())
      # dump the db
      self.events_db.dump()
      self.event_lock.release()
      # do some checking for internal errors
      if p.name in e.roster:
        self.logger.critical("Failed to removed player {0} from event {1}".format(p.name,e.name))
        raise RuntimeError("Failed to removed player {0} from event {1}".format(p.name,e.name))

    def addEvent(self,e):
      self.logger.info("Adding event {0} on {1}...".format(e.name,str(e.date)))
      ## do some light error checking
      if isinstance(e,event.Raid):
        t = "raid"
      elif isinstance(e,event.Event):
        t = "event"
      else:
        self.logger.error("Input must be a properly constructed Event or Raid object")
        raise TypeError("Input must be a properly constructed Event or Raid object")
      ## make sure the db is up to date
      self.logger.debug("Waiting for lock on the event database...")
      self.event_lock.acquire()
      self.logger.debug("Got the lock on the event database")
      self.events_db._loaddb()
      ## make sure we dont already have this event
      if e.recurring:
        id = e.name
      else:
        id = hashlib.md5("{0}{1}".format(e.name,str(e.date)).encode("utf-8")).hexdigest()
      self.logger.debug("Generated unique identifier: {0}".format(id))
      if id in self.events_db.getall():
        self.event_lock.release()       
        self.logger.debug("Released the lock on the event database")
        e_db = self.events_db.get(id)
        if e_db[4]:
          raise ValueError("Recurring event with this name exists; mark event as not recurring or select a unique name")
        else:
          raise ValueError("Event exists")
      # Turn the event into a list for storage in the DB
      ##eList = [t,e.owner,str(e.date),e.name,e.recurring,e.frequency]
      # add the extra bits that only exist for raids
      if t == "raid":
        e.cook(roster = list(filter(lambda p: p.sched == "Raider",self.roster)))
#        eList.extend([e.comp,list(map(lambda p: p.name,e.roster)),list(map(lambda p: p.name,e.tanks)),list(map(lambda p: p.name,e.healers)),list(map(lambda p: p.name,e.dps))])
      self.events_db.set(id,e.dump())
      self.events_db.dump()
      self.event_lock.release()
      self.logger.debug("Released the lock on the event database")
      self.logger.info("Added event {0} on {1}".format(e.name,str(e.date)))
      return self.events_db.get(id)

    def deleteEvent(self,name,type = None,date = None, time = None):
      self.logger.info("Deleting event {0}...".format(name))
      ## make sure weve got the most up to date db
      self.logger.debug("Waiting for lock on the event database...")
      self.event_lock.acquire()
      self.logger.debug("Got the lock on the event database")
      self.events_db._loaddb()
      ## get the number of events the name corresponds to
      keys = self.events_db.getall()
      es = []
      for key in keys:
        e = self.events_db.get(key)
        if e[3] == name:
          if e[0] == "raid":
            es.append(event.Raid(e[1],datetime.datetime.fromisoformat(e[2]),e[3],e[4],e[5]))
          elif e[0] == "event":
            es.append(event.Event(e[1],datetime.datetime.fromisoformat(e[2]),e[3],e[4],e[5]))
          else:
            self.event_lock.release()
            self.logger.debug("Released the lock on the event database")
            raise RuntimeError("Unknown event type")
      numEvents = len(es)
      if numEvents < 1:
        self.event_lock.release()
        self.logger.debug("Released the lock on the event database")
        raise ValueError("Unknown Event")
      ## Make sure inputs make sense
      if type == "one" and (date == None or time == None):
        if numEvents > 1:
          self.event_lock.release()
          self.logger.debug("Released the lock on the event database")
          raise ValueError("Operation type \'one\' must have a unique name OR inputs for \'date\' and \'time\'")
      ## find the item(s) to delete
      if date != None:
        es = list(filter(lambda e: e.date.strftime("%d%b%Y").upper() == date,es))
        if time != None:
          es = list(filter(lambda e: e.date.strftime("%H:%M") == time,es))
      ### from the database
      ids = []
      for e in es:
        if e.recurring:
          id = e.name
        else:
          id_str = "{0}{1}".format(e.name,str(e.date))
          id = hashlib.md5(id_str.encode("utf-8")).hexdigest()
        self.events_db.rem(id)
        ids.append(id)
      self.events_db.dump()
      self.event_lock.release()
      self.logger.debug("Released the lock on the event database")
      self.logger.info("Deleted event {0}...".format(name))
      ## return TRUE/FALSE if the operation was successful
      return not True in list(map(lambda x: x in ids,self.events_db.getall()))

    def setEvent(self,type,name,prop,val,d = None):
      self.logger.info("Updating event {0} {1} to {2}...".format(name,prop,val))
      # setup a variable to track the old value
      old = None
      ## make sure weve got the most up to date db
      self.logger.debug("Waiting for lock on the event database...")
      self.event_lock.acquire()
      self.logger.debug("Got the lock on the event database")
      self.events_db._loaddb()
      ## get total number of events to change
      keys = self.events_db.getall()
      es = []
      for key in keys:
        e = self.events_db.get(key)
        if e[3] == name:
          if e[0] == "raid":
            es.append(event.Raid(e[1],datetime.datetime.fromisoformat(e[2]),e[3],e[4],e[5]))
          elif e[0] == "event":
            es.append(event.Event(e[1],datetime.datetime.fromisoformat(e[2]),e[3],e[4],e[5]))
          else:
            self.event_lock.release()
            self.logger.debug("Released the lock on the event database")
            raise RuntimeError("Unknown event type")
      numEvents = len(es)
      if numEvents < 1:
        self.logger.debug("No events to change")
        self.event_lock.release()
        self.logger.debug("Released the lock on the event database")
        raise ValueError("Unknown Event")
      self.logger.debug("Located {0} events to change".format(numEvents))
      ## type checking
      if type == "one" and (d == None):
        if numEvents > 1:
          self.logger.debug("Input requests single change to non-unique event")
          self.event_lock.release()
          self.logger.debug("Released the lock on the event database")
          raise ValueError("Operation type \'one\' must have a unique name OR inputs for \'date\' and \'time\'")
      elif type == "one":
        es = list(filter(lambda e: e.date == d,es))
        numEvents = len(es)
        if numEvents < 1:
          self.logger.debug("Date filtering removed all applicable events")
          self.event_lock.release()
          self.logger.debug("Released the lock on the event database")
          raise ValueError("Matching event found with incorrect inputs \'date\' or \'time\'")
      elif type == "all":
        if prop == "recurring":
          self.logger.debug("Operatiaon \'all\' cannot be used to change \'recurring\'")
          self.event_lock.release()
          self.logger.debug("Released the lock on the event database")
          raise ValueError("Operation \'all\' cannot be used to change event \'recurring\' status")
        elif prop == "frequency":
          self.event_lock.release()
          self.logger.debug("Released the lock on the event database")
          raise ValueError("Operation \'all\' cannot be used to change event frequency")
      ## iterate through list of events to change (es)
      for e in es:
        ## pull out the event we're modifying
        if e.recurring:
          id = e.name
        else:
          id_str = "{0}{1}".format(e.name,str(e.date))
          id = hashlib.md5(id_str.encode("utf-8")).hexdigest()
        self.logger.info("Changing event {0} with identifier {1}".format(e.name,id))
        e_db = self.events_db.get(id)
        ## modify event based on the value of prop
        if prop == "date":
          old = e.date.date()
          e.date = e.date.replace(year=val.year,month=val.month,day=val.day)
        elif prop == "time":
          old = e.date.time()
          e.date = e.date.replace(hour=val.hour,minute=val.minute)
        elif prop == "name":
          old = e.name
          e.name = val
        elif prop == "recurring":
          old = e.recurring
          e.recurring = val
          if not e.recurring:
            e.frequency = None
        elif prop == "frequency":
          if not e.recurring:
            self.event_lock.release()
            self.logger.debug("Released the lock on the event database")
            raise ValueError("Cannot change frequency for one-time event")
          e.frequency = val
        elif prop == "owner":
          # make sure the val is a valid player identifier
          p = self.roster_db.get(val)
          if p:
            old = e.owner
            e.owner = val
          else:
            self.event_lock.release()
            self.logger.debug("Released the lock on the event database")
            raise ValueError("Cannot change owner to a non-existent user")
        else:
          self.event_lock.release()
          self.logger.debug("Released the lock on the event database")
          raise ValueError("Unknown property")
        self.events_db.rem(id)
        ## build the list for storing in the database
        ###eList = [e_db[0],e.owner,str(e.date),e.name,e.recurring,e.frequency]
        ## rebuild the id for the event
        if e.recurring:
          id = e.name
        else:
          id_str = "{0}{1}".format(e.name,str(e.date))
          id = hashlib.md5(id_str.encode("utf-8")).hexdigest()
        # add the event to the database
        self.events_db.set(id,e.dump())
        self.events_db.dump()
      self.event_lock.release()
      self.logger.debug("Released the lock on the event database")
      self.logger.info("Updated event {0} {1} to {2}".format(name,prop,val))
      return (old,val)
    
    def getRoles(self,roles):
      self.logger.info("Mapping DB information to Discord Roles...")
      self.db = pickledb.load(os.path.join(self.db_path,"server.db"), False)
      self.Raider = discord.utils.find(lambda r: r.id == self.Raider,roles)
      self.Social = discord.utils.find(lambda r: r.id == self.Social,roles)
      self.Member = discord.utils.find(lambda r: r.id == self.Member,roles)
      self.PUG = discord.utils.find(lambda r: r.id == self.PUG,roles)
      self.Admin = discord.utils.find(lambda r: r.id == self.Admin,roles)
      return
     
    def getRoster(self):
      self.logger.info("Getting roster from the DB...")
      self.roster_db = pickledb.load(os.path.join(self.db_path,"roster.db"),False)
      names = self.roster_db.getall()
      index = 0
      for name in names:
        playerSettings = self.roster_db.get(name)
        p = player.Player(name,sched=playerSettings[0],roles=playerSettings[1])
        self.roster.append(p)
        self.roster_names.append(p.name)
        self.logger.debug("Created known player {0} from database".format(name))
      self.logger.info("Pulled {0} known players from the database".format(len(self.roster)))
      return

    def changePlayer(self,player,prop,val):
      self.logger.info("Updating Player {0}'s {1} to {2}".format(player.name, prop, val))
      if prop == "sched":
        player.updatePlayer(sched=val)
      elif prop == "roles":
        player.updatePlayer(roles=val)
      else:
        raise ValueError("Unknown property")
      self.updateRoster(player)

    def mapRole(self,role,sched):
      if role == None:
        return
      else:
        self.logger.info("Mapping role {0} to schedule {1}".format(role.id,sched))

      if sched == "Raider":
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
      elif sched == "Admin":
        self.Admin = role
        self.db.set("Admin",role.id)
      else:
        raise AttributeError("Unknown Schedule option")
      self.db.dump()
      return

    def updateRoster(self,player):
      self.logger.info("Updating Player \'{0}\'".format(str(player)))
      try:
        i = self.roster_names.index(player.name)
        self.logger.debug("Found existing player")
        self.roster.pop(i)
        self.roster.insert(i,player)
        self.roster_names.pop(i)
        self.roster_names.insert(i,player.name)
      except ValueError:
        self.logger.debug("New player")
        self.roster.append(player)
        self.roster_names.append(player.name)
      self.roster_db.set(player.name,[player.sched,player.roles])
      self.roster_db.dump()
      return
    
    def __init__(self,id,name,owner):
        # Generate a child logger of the root for this server
        self.logger = logging.getLogger("schedulizer.{0}".format(name))
        self.logger.info("Creating new server for {0}".format(name))

        self.id = id
        self.name = name
        self.owner = owner
        # List of player objects in this server
        ## TODO - turn this into a dictionary, key is the name value is the object
        self.roster = []
        self.roster_names = []
        # setup thread tracking objects
        self.exitFlag = threading.Event()
        self.event_lock = threading.Lock()
        self.roster_lock = threading.Lock()
        # Create the database file for this server
        project_root = os.path.split(os.path.dirname(__file__))[0]
        try:
          self.logger.info("Creating directory for server databases")
          os.makedirs(os.path.join(project_root,"databases",str(id)+".db"))
        except FileExistsError:
          self.logger.debug("Server directory exists, this must be a known server")
          None
        self.db_path = os.path.join(project_root,"databases",str(id)+".db")
        self.logger.debug("Creating database for the server object")
        self.db = pickledb.load(os.path.join(self.db_path,"server.db"), False,sig=False)
        self.db.set('id',id)
        self.db.set('name',name)
        self.db.set('owner',str(owner))
        self.Raider = self.db.get("Raider") or None
        self.Social = self.db.get("Social") or None
        self.Member = self.db.get("Member") or None
        self.PUG = self.db.get("PUG") or None
        self.Admin = self.db.get("Admin") or None
        self.db.dump()
        # Create the database file for this server's roster
        self.logger.debug("Creating database for the roster")
        self.roster_db = pickledb.load(os.path.join(self.db_path,"roster.db"),False,sig=False)
        self.roster_db.dump()
        # Setup event tracking for this server
        ## create the database for this server's events
        self.logger.debug("Creating database for the events")
        self.events_db = pickledb.load(os.path.join(self.db_path,"events.db"),False,sig=False)
        self.events_db.dump()
        # create the timekeeper slot
        self.timekeeper = None
        self.logger.info("Server object creation complete")

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
            self.exitFlag = threading.Event()
            self.roster_lock = threading.Lock()
            self.server_lock = threading.Lock()
            self.event_lock = threading.Lock()
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