# Required to interface with the discord API
import discord
# Required to read the token from the environment file
import os
# Required to add classes subpackage to the path
import sys
# Add project_root to the path so we can import from subpackages
project_root = os.path.dirname(__file__)
sys.path.append(os.path.join(project_root,"classes"))

# Import subpackages
import server, player

# Build the Intents object for the client
intents = discord.Intents.default()
intents.members = True
# Create an instance of the schedClient
client = server.SchedClient(intents=intents,command_prefix='!')
client.setup()

# Asynchronous function calls inherited from the client class (i think)
# when the client class runs (using the token to authenticate) it sends events back to the bot like on_ready and on_message
#@client.event signifies the following function as based on the results of a client event

# Actions to take after the client successfully authenticates and reports the ready status
# TODO add some more verbose logging maybe?
@client.event
async def on_ready():
  print('Logged on as: {0.user}'.format(client))
  print('Connected to ' + str(len(client.guilds)) + " servers")
  for guild in client.guilds:
    print("Name: ",guild.name,";\tID: ",guild.id,";\tOwner: ",guild.owner)
    server = client.addServer(guild.id,guild.name,guild.owner)
    # Identify Role objects for schedulizer-based roles
    server.mapRole(discord.utils.find(lambda r: r.name == "Raider",guild.roles),"Raider")
    server.mapRole(discord.utils.find(lambda r: r.name == "Social",guild.roles),"Social")
    server.mapRole(discord.utils.find(lambda r: r.name == "Member",guild.roles),"Member")
    server.mapRole(discord.utils.find(lambda r: r.name == "Pug",guild.roles),"PUG")
    try:
      print("\tRoles: RAIDER/"+server.Raider.name,"SOCIAL/"+server.Social.name,"MEMBER/"+server.Member.name,"PUG/"+server.PUG.name)
      # Create user objects for each player with a valid schedule role
      for member in guild.members:
        try:
          p = player.Player(member.name,sched=discord.utils.find(lambda r: r == server.Raider or r == server.Social or r == server.Member or r == server.PUG,member.roles).name)
          server.updateRoster(p)
        except AttributeError:
          continue
    except AttributeError:
      print("\tNo mapped roles")
  # TODO - spin off new thread to handle command line args from the bot side

@client.command(name="hello",help="Prints 'Hello World!'")
async def helloWorld(context):
  await context.send("Hello World!")

@client.command(name="show",help="Displays different information. Usage: !show [roster|events]")
async def show(context,opt: str):
  server = client.servers[client.server_ids.index(context.guild.id)]
  if opt == "roster":
    roster = []
    for p in server.roster:
      if p.sched != "Pug":
        roster.append(str(p))
      else:
        continue
    await context.send("\n".join(roster))
    # TODO
  elif opt == "events":
    await context.send("STUB: !show events")
    # TODO
  else:
    await context.send_help(context.command)

@client.event
async def on_command_error(context,error):
  if isinstance(error,discord.ext.commands.errors.CheckFailure):
    await context.send('You do not have the correct role for this command.')
  elif isinstance(error,discord.ext.commands.errors.MissingRequiredArgument):
    await context.send_help(context.command)
  else:
    await context.send_help()

# Call the client run method of the previously created discord client, using the value of the TOKEN key in the current directory's environment file, .env
TOKEN = os.getenv('TOKEN')
client.run(TOKEN)