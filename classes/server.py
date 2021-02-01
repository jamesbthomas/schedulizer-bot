# Defines the Server class and extends the Discord.Client class to track it

import discord

class Server(object):
    # Class for tracking properties by server
    
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

    def addServer(self,id,name,owner):
        if id in self.server_ids:
            raise FileExistsError("Server already known")
        else:
            server = Server(id,name,owner)
            self.servers.append(server)
            self.server_ids.append(id)
            return