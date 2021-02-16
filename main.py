# Required to interface with the discord API
import discord
# Required to read the token from the environment file
import os
# Required to add classes subpackage to the path
import sys
# Required for using regex matching
import re
# Required for working with datetime objects
import datetime
# Required for reading the auth token from the environment file (not included in git repo)
from dotenv import load_dotenv
# Add project_root to the path so we can import from subpackages
project_root = os.path.dirname(__file__)
sys.path.append(os.path.join(project_root,"classes"))

# Import subpackages
import server, player
from event import *

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
    if guild.id not in client.server_ids:
      print("NEW\t\t-\tName: ",guild.name,";\tID: ",guild.id,";\tOwner: ",guild.owner)
      server = client.addServer(guild.id,guild.name,guild.owner)
      # Identify Role objects for schedulizer-based roles
      server.mapRole(discord.utils.find(lambda r: r.name == "Raider",guild.roles),"Raider")
      server.mapRole(discord.utils.find(lambda r: r.name == "Social",guild.roles),"Social")
      server.mapRole(discord.utils.find(lambda r: r.name == "Member",guild.roles),"Member")
      server.mapRole(discord.utils.find(lambda r: r.name == "Pug",guild.roles),"PUG")
      # Create user objects for each player with a valid schedule role
      for member in guild.members:
        try:
          p = player.Player(member.name,sched=discord.utils.find(lambda r: r == server.Raider or r == server.Social or r == server.Member or r == server.PUG,member.roles).name)
          server.updateRoster(p)
        except AttributeError:
          continue
    else:
      print("KNOWN\t-\tName: ",guild.name,";\tID: ",guild.id,";\tOwner: ",guild.owner)
      server = client.servers[client.server_ids.index(guild.id)]
      server.getRoles(guild.roles)
      server.getRoster()
      server.getEvents()
    try:
      print("\tRoles: RAIDER/"+server.Raider.name,"SOCIAL/"+server.Social.name,"MEMBER/"+server.Member.name,"PUG/"+server.PUG.name)
    except AttributeError:
      print("No mapped roles")
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
  elif opt == "events":
    events = []
    for event in server.events:
      events.append("Type: "+("raid" if isinstance(event,Raid) else "event" if isinstance(event,Event) else "ERROR")+"\tName: "+event.description+"\tDate: "+str(event.date))
    if len(events) > 0:
      await context.send("\n".join(events))
    else:
      await context.send("No events currently scheduled for this server")
  else:
    await context.send_help(context.command)

@client.command(name="event",help="Create/Modify/Delete Event objects. Usage:\n!event create <type> <name> <date:DDMMM[YYYY]> <time:HH:MM[AM|PM]> <recurring:True|False> [frequency:weekly|monthly]\n!event delete <all|one> <name> [<date> [<time>]]\n!event set <all|one> <name> <property> <value> [<date> [<time>]]")
async def event(context, *args):
  ## Generate inputs based on number of args
  operation = args[0]
  if operation == "create":
    type, name, date, time, recurring, frequency = [None]*6
    try:
      type = args[1]
      name = args[2]
      date = args[3]
      time = args[4]
      recurring = args[5]
      frequency = args[6]
    except IndexError:
      None
    if date == None  or time == None:
      raise ValueError("Operation \'create\' requires date and time inputs")
    if recurring == None:
      raise ValueError("Operation \'create\' requires a recurring input")
    elif recurring == "true" and frequency == None:
      raise ValueError("Operation \'create\' with recurring \'true\' requires a frequency input")
  elif operation == "delete":
    type, name, date, time, force = [None]*5
    try:
      type = args[1]
      name = args[2]
      date = args[3]
      time = args[4]
    except IndexError:
      None
    if type == None:
      raise ValueError("Operation \'delete\' requires type input")
    elif name == None:
      raise ValueError("Operation \'delete\' requires name input")
    elif date != None and time == None and type != "all":
      raise ValueError("Operation \'delete\' requires time input unless using type \'all\'")
      return
  elif operation == "set":
    type, name, property, value, date, time = [None]*6
    try:
      type = args[1]
      name = args[2]
      property = args[3]
      value = args[4]
      date = args[5]
      time = args[6]
    except IndexError:
      None
    if type == None:
      raise ValueError("Operation \'set\' requires type input")
    elif name == None:
      raise ValueError("Operation \'set\' requires name input")
    elif property == None:
      raise ValueError("Operation \'set\' requires property input")
    elif value == None:
      raise ValueError("Operation \'set\' requires value input")
    elif type == "one" and (date == None or time == None):
      raise ValueError("Operation \'set\' with type \'one\' requires date and time input")
  else:
    raise ValueError("Unknown operation. Only accepts \'create\', \'set\', and \'delete\'")

  # Transform inputs into the types we need to construct the object
  ## type
  if operation.lower() == "create":
    if type.lower() != "event" and type.lower() != "raid":
      raise ValueError("Input \'type\' only supports \'event\' and \'raid\' values")
  else:
    if type.lower() != "all" and type.lower() != "one":
      raise ValueError("Operation \'{0}\' requires either \'all\' or \'one\'".format(operation))
  ## name
  if not isinstance(name,str):
    raise TypeError("Input \'name\' must be of type str")
  ### Only need to do datetime validation if type is one/event/raid
  ### DATE
  mons = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
  if (not isinstance(date,str) and date != None) or (not isinstance(time,str) and time != None):
    raise TypeError("Inputs \'date\' and \'time\' must be of type str")
  elif date != None: #turn them into a datetime object
    # First, check to make sure they conform to the format I want
    if not re.match("\d\d\w\w\w(\d\d\d\d)?",date):
      raise ValueError("Input \'date\' must be in the DDMMM or DDMMMYYY format, such as 01JAN or 01JAN1970")
    elif re.match("\d\d\w\w\w\d\d\d\d",date): # with year
      day = int(date[0:2])
      mon = date[2:5].upper()
      year = int(date[5:9])
    else: # without year
      day = int(date[0:1])
      mon = date[2:5].upper()
      year = datetime.datetime.now().year
    if mon == "JAN" or mon == "MAR" or mon == "MAY" or mon == "JUL" or mon == "AUG" or mon == "OCT" or mon == "DEC":
      # 31-day month
      if day > 31 or day < 1:
        raise ValueError("Input \'date\' has too many days; JAN/MAR/MAY/JUL/AUG/OCT/DEC can only have days between 0-31")
    elif mon == "APR" or mon == "JUN" or mon == "SEP" or mon == "NOV":
      # 30-day month
      if day > 30 or day < 1:
        raise ValueError("Input \'date\' has too many days; APR/JUN/SEP/NOV can only have days between 0-30")
    elif mon == "FEB" and year%4 != 0:
      # 28-day month
      if day > 28 or day < 1:
        raise ValueError("Input \'date\' has too many days; FEB in years not divisible by 4 can only have days between 0-28")
    elif mon == "FEB" and year%4 == 0:
      # 29-day month
      if day > 29 or day < 1:
        raise ValueError("Input \'date\' has too many days; FEB in leap years can only have days between 0-29")
    else: # unknown month
      raise ValueError("Input \'date\' must include a known month, such as JAN for January, FEB for February")
    #### check the year, TODO - not sure how to handle this error, like what if its DEC30 and i'm trying to make an event for 3 days from now?
    if year != datetime.datetime.now().year:
      await context.send("WARNING: Event date is not in the current year")
    ### TIME
    if time != None:
      if not re.match("\d{1,2}:\d\d(AM|PM)?",time):
        raise ValueError("Input \'time\' must be in the HH:MM format using 12- or 24-hour clocks, such as 10:00PM or 22:00")
      else: # Check to make sure the format is good, ie 22:00 PM is wrong
        hour, remainder = time.split(":")
        if len(remainder) == 2:
          min = remainder[0:2]
          period = None
        elif len(remainder) == 4:
          min, period = remainder[0:2],remainder[2:4]
        else: #unrecognized time format
          raise RuntimeError("Time Split Failure")
        min = int(min)
        hour = int(hour)
        if min > 60:
          raise ValueError("Input \'time\' cannot have minutes greater than 60")
        if period != None:
          # in 12-hour mode
          if period != "AM" and period != "PM":
            raise ValueError("Input \'time\' in 12-hour mode must include either AM or PM")
          if hour > 12 or hour < 0:
            raise ValueError("Input \'time\' in 12-hour mode can only have hours between 0-12")
          if period == "PM":
            hour += 12
        else: # in 24-hour mode
          if hour > 24 or hour < 0:
            raise ValueError("Input \'time\' in 24-hour mode can only have hours bettween 0-24")
      ### make the object
      d = datetime.datetime(year,mons.index(mon)+1,day,hour,min)
    else:
      d = datetime.datetime(year,mons.index(mon)+1,day)
  if operation == "create":
    ## recurring
    if recurring.lower() == "true":
      rec = True
    elif recurring.lower() == "false":
      rec = False
    else:
      raise ValueError("Input \'recurring\' must be either \'true\' or \'false\'")
    ## frequency
    if not rec and frequency == None:
      None
    elif rec and frequency == None:
      raise ValueError("Input \'recurring\' must have a value for input \'frequency\'")
    elif frequency.lower() != "weekly" and frequency.lower() != "monthly":
      raise ValueError("Input \'frequency\' must be either \'weekly\' or \'monthly\'")
  ## Done validating inputs, create the event object and store it in the server
  server = client.servers[client.server_ids.index(context.guild.id)]
  ### CREATE
  if operation == "create":
    if type == 'event':
      if not frequency:
        e = Event(d,rec,name)
      else:
        e = Event(d,rec,name,frequency)
    elif type == 'raid':
      e = Raid(d,rec,name,frequency)
    result = server.addEvent(e)
    message = ""
    if result:
      message = "Successfully added event {0}".format(e.description)
    else:
      message = "WARNING: Unable to add event"
  elif operation == "delete":
    server.deleteEvent(name,type,date,time)
    message = "Successfully deleted {0} instance(s) of event {1}".format(type,name)
  elif operation == "set":
    message = "STUB set"
  await context.send(message)

@client.event
async def on_command_error(context,error):
  if isinstance(error,discord.ext.commands.errors.CheckFailure):
    await context.send('You do not have the correct role for this command.')
  elif isinstance(error,discord.ext.commands.errors.MissingRequiredArgument):
    await context.send_help(context.command)
  else:
    await context.send(":".join(str(error).split(":")[1:]))
    await context.send_help(context.command)

# Call the client run method of the previously created discord client, using the value of the TOKEN key in the current directory's environment file, .env
load_dotenv()
TOKEN = os.getenv('TOKEN')
client.run(TOKEN)