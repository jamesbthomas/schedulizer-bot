# Required to interface with the discord API
import discord
# Required to read the token from the environment file
import os

# Build the Intents object for the client
intents = discord.Intents.default()
intents.members = True
# Create an instance of the discord client
client = discord.Client(intents=intents)

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
    print("\tName: ",guild.name,";\tID: ",guild.id,";\tOwner: ",guild.owner)
    # Check to see if we know this server
    if guild.id not in client.servers:
      
    else:
    
    
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
        await message.channe.send("Usage: new [player]")
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
client.run(os.getenv('TOKEN'))