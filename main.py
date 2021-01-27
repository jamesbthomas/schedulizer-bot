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

# Actions to take after the client reports a new message
# TODO replace all these ifs with a a case statement... much better
@client.event
async def on_message(message):
  # Auto break if the message is from this bot
  if message.author == client.user:
    return
  # Check if message starts with this bot's imperative operator
  elif message.content.startswith('!'):
    # Split the message into arguments a la shells
    args = message.content.split('!')[1].split()
    # Case switch (but python so not a case switch) on the command
    if args[0] == "hello":
      await message.channel.send('Hello!')
  # Break if message does not have any imperatives
  else:
    return

# Call the client run method of the previously created discord client, using the value of the TOKEN key in the current directory's environment file, .env
client.run(os.getenv('TOKEN'))
