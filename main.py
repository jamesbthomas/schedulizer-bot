# Required to interface with the discord API
import discord
# Required to read the token from the environment file
import os

# Create an instance of the discord client
client = discord.Client()

# Asynchronous function calls inherited from the client class (i think)
# when the client class runs (using the token to authenticate) it sends events back to the bot like on_ready and on_message
#@client.event signifies the following function as based on the results of a client event

# Actions to take after the client successfully authenticates and reports the ready status
# TODO add some more verbose logging maybe?
@client.event
async def on_ready():
  print('Logged on as: {0.user}'.format(client))

# Actions to take after the client reports a new message
# TODO replace all these ifs with a a case statement... much better
@client.event
async def on_message(message):
  # Auto break 
  if message.author == client.user:
    return
  elif message.content.startswith('$'):
    if message.content.startswith('$hello'):
      await message.channel.send('Hello!')
  else:
    return

# Call the client run method of the previously created discord client, using the value of the TOKEN key in the current directory's environment file, .env
client.run(os.getenv('TOKEN'))
