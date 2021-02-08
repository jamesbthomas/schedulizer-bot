# Defines the Server class and extends the Discord.Client class to track it

import discord, pickledb, os, player
from discord.ext import commands

class Server(object):
    # Class for tracking properties by server
    
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