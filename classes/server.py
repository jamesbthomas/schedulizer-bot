# Defines the Server class and extends the Discord.Client class to track it

import discord

class Server(object):
    # Class for tracking properties by server
    ## For tracking the discord.Role objects on this server that correspond to our schedules
    Raider = None
    Social = None
    Member = None
    PUG = None

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
    
    def __init__(self,id,name,owner):
        self.id = id
        self.name = name
        self.owner = owner

class SchedClient(discord.Client):

    servers = []
    server_ids = []

    def setup(self):
        # Initialize attributes
        self.servers = []
        self.server_ids = []
        # Read in from database

    def addServer(self,id,name,owner):
        if id in self.server_ids:
            raise FileExistsError("Server already known")
        else:
            server = Server(id,name,owner)
            self.servers.append(server)
            self.server_ids.append(id)
            return server