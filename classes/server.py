# Defines the Server class and extends the Discord.Client class to track it

import discord

class Server(object):
    # Class for tracking properties by server
    
    def __init__(self,id,name,owner):
        self.id = id
        self.name = name
        self.owner = owner
  

class SchedClient(discord.Client):
    #Extending the Discord.Client class so that I can track connected servers independently

    servers = []
    server_ids = []

    def __init__(self):
        self = discord.Client()
        self.servers = []

    def addServer(self,id,name,owner):
        if id in self.server_ids:
            raise FileExistsError("Server already known")
        else:
            server = Server(id,name,owner)
            self.servers.append(server)
            self.server_ids.append(id)
            return