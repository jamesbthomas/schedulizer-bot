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
client = server.SchedClient(intents=intents)
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
    for role in guild.roles:
      if role.name == "Raider":
        # Map Role object to the Raider schedule
        server.mapRole(role,"Raider")
      elif role.name == "Social":
        # Map Role object to the Social schedule
        server.mapRole(role,"Social")
      elif role.name == "Member":
        # Map Role object to the Member schedule
        server.mapRole(role,"Member")
      elif role.name == "Pug":
        # Map Role object to the PUG schedule
        server.mapRole(role,"PUG")
      else:
        continue
    try:
      print("\tRoles: RAIDER/"+server.Raider.name,"SOCIAL/"+server.Social.name,"MEMBER/"+server.Member.name,"PUG/"+server.PUG.name)
      # Create user objects for each player with a valid schedule role
      for member in guild.members:
        if server.Raider in member.roles:
          sched = "Raider"
        elif server.Social in member.roles:
          sched = "Social"
        elif server.Member in member.roles:
          sched = "Member"
        elif server.PUG in member.roles:
          sched = "PUG"
        else:
          continue
        p = player.Player(member.name,sched=sched)
        server.updateRoster(p)
    except AttributeError:
      print("\tNo mapped roles")
  # TODO - spin off new thread to handle command line args from the bot side
    
# Actions to take after the client reports a new message
@client.event
async def on_message(message):
  # Auto break if the message is from this bot
  if message.author == client.user:
    return
  # Check if message starts with this bot's imperative operator
  elif message.content.startswith('!') and len(message.content)>2:
    # Split the message into arguments a la shells
    args = message.content.split('!')[1].split()
    # Case switch (but python so not a case switch) on the command
    # Generic hello response because everyone should be friendly
    if args[0] == "hello":
      await message.channel.send('Hello!')
    # Control sequence for the new command used to generate new objects
    elif args[0] == "new":
      if len(args) < 2:
        await message.channel.send("Usage: new [player]")
      # New Player command to create a Player object for tracking
      ## Potentially automate based on member roles and using the Armory API?
      elif args[1] == "player":
        await message.channel.send("Placeholder for \'new player\' command")
      # Unknown option, print usage
      else:
        await message.channel.send("Usage: new [player]")
    # Control sequence for the sched command used to control attendance
    elif args[0] == "sched":
      if len(args) < 2:
        await message.channel.send("Usage: sched [confirm|deny|tentative]")
      # Sign up for this raid
      elif args[1] == "confirm":
        await message.channel.send("Placeholder for \'sched confirm\' command")
      # Do not sign up for this raid
      elif args[1] == "deny":
        await message.channel.send("Placeholder for \'sched deny\' command")
      # Sign up as tentative
      elif args[1] == "tentative":
        await message.channel.send("Placeholder for \'sched tentative\' command")
      # Print usage information
      else:
        await message.channel.send("Usage: sched [confirm|deny|tentative]")
    # Command not recognized
    ## TODO: error message to the server or just error locally? Probably need user testing
    else:
      return
  # Break if message does not have any imperatives
  else:
    return

# Call the client run method of the previously created discord client, using the value of the TOKEN key in the current directory's environment file, .env
TOKEN = os.getenv('TOKEN')
client.run(TOKEN)