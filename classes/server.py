# Defines the Server class and extends the Discord.Client class to track it

import discord, pickledb, os
from discord.ext import commands

class Server(object):
    # Class for tracking properties by server

    def mapRole(self,role,sched):
      if sched == "Raider":
        self.Raider = role
      elif sched == "Social":
        self.Social = role
      elif sched == "Member":
        self.Member = role
      elif sched == "PUG":
        self.PUG = role
      else:
        raise AttributeError("Unknown Schedule option")
      return

    def updateRoster(self,player):
      try:
        i = self.roster_names.index(player.name)
        self.roster.pop(i)
        self.roster.insert(i,player)
      except ValueError:
        self.roster.append(player)
        self.roster_names.append(player.name)
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
        self.db.dump()


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
          db = pickledb.load(os.path.join(project_root,"databases",f,"server.db"),False)
          id = db.get('id')
          server = Server(id,db.get('name'),db.get('owner'))
          self.servers.append(server)
          self.servers.append(id)

    def addServer(self,id,name,owner):
        if id in self.server_ids:
            raise FileExistsError("Server already known")
        else:
            server = Server(id,name,owner)
            self.servers.append(server)
            self.server_ids.append(id)
            return server