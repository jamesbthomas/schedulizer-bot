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
# Required to handle logging on the script side
import logging, logging.handlers
# Add project_root to the path so we can import from subpackages
project_root = os.path.dirname(__file__)
sys.path.append(os.path.join(project_root,"classes"))

# Import subpackages
import server, timekeeper
from event import *
from player import *

client = None

# wrap the logger setup in a function so that the messaging shows up the way I want it to in the log file
def setup(client):
  # setup the logging module
  ## default log level is INFO
  log_level = logging.INFO
  log_level_str = "INFO"
  ## check for command line arguments like setting the logging level
  if __name__ == "__main__":
    if len(sys.argv) > 1:
      # iterate through arguments, build out the attributes we need to use later
      for arg in sys.argv[1:]:
        # switch based on known arguments
        ## Start with all of the help based ones
        if arg == "-h":
          print("usage: python3 main.py [level=logging_level]")
          exit()
        elif arg == "--help":
          print("usage: python3 main.py [level=logging_level]")
          exit()
        elif arg == "help":
          print("usage: python3 main.py [level=logging_level]")
          exit()
        # catch arguments using the key=value format
        elif re.match("\w+=\w+",arg):
          key, value = arg.split('=')
          # check for known keywords and act appropriately
          ## keyword == "level"
          if key == "level":
            if value.upper() == "DEBUG":
              print("INFO - startup - schedulizer - Setting log level to DEBUG")
              log_level = logging.DEBUG
              log_level_str = "DEBUG"
            elif value.upper() == "INFO":
              print("INFO - startup - schedulizer - Setting log level to INFO (default)")
              log_level = logging.INFO
              log_level_str = "INFO"
            elif value.upper() == "WARNING":
              print("WARNING - startup - schedulizer - Setting log level to WARNING (default is INFO)")
              log_level = logging.WARNING
              log_level_str = "WARNING"
            elif value.upper() == "ERROR":
              print("WARNING - startup - schedulizer - Setting log level to ERROR (default is INFO)")
              log_level = logging.ERROR
              log_level_str = "ERROR"
            elif value.upper() == "CRITICAL":
              print("WARNING - startup - schedulizer - Setting log level to CRITICAL (default is INFO)")
              log_level = logging.CRITICAL
              log_level_str = "CRITICAL"
            else:
              print("WARNING - startup - schedulizer - Unrecognized value \'{0}\', log level will be set to {1}".format(value,log_level))
          # unrecognized keyword
          else:
            print("ERROR - startup - schedulizer - Unrecognized Keyword \'{0}\'".format(key))
            print("usage: python3 main.py [level=logging_level]")
            exit()
        else:
          print("ERROR - startup - schedulizer - Unrecognized Argument \'{0}\'".format(arg))
          print("usage: python3 main.py [level=logging_level]")
          exit()
    else:
      # no arguments provided
      None
  # create the Logger object
  main_logger = logging.getLogger("schedulizer")
  ## create the handlers for the log file and the console
  ### active filename = project_root\logs\schedulizer.log
  ### rolled filename(s) = project_root\logs\schedullizer.log.%Y-%m-%d_%H-%M-%S
  ### rollover interval = every Tuesday, keep 10 log files
  file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(project_root,"logs","{0}.log".format("schedulizer")),when='W1',backupCount=10)
  console_handler = logging.StreamHandler()
  ## set the log level
  file_handler.setLevel(log_level)
  console_handler.setLevel(log_level)
  main_logger.setLevel(log_level)
  ## set the format for messages
  ### format: <timestamp>: <log_level> - <component hierarchy> - <function name> - <message>
  #### to reduce the number of times we need to create/recreate the logger, the MESSAGE passed as input will include the component issuing the log message
  format = logging.Formatter("%(asctime)s: %(levelname)-8s - %(name)s - %(funcName)s - %(message)s")
  file_handler.setFormatter(format)
  console_handler.setFormatter(format)
  ## add completed handlers to the logger
  main_logger.addHandler(file_handler)
  main_logger.addHandler(console_handler)

  # log the startup
  main_logger.info("Start up initiated with log level {0}".format(log_level_str))

  main_logger.info("Setting up known servers...")
  client.setup()
  main_logger.info("Known server setup complete")

  return main_logger

# Build the Intents object for the client
intents = discord.Intents.default()
intents.members = True
# Create an instance of the schedClient
client = server.SchedClient(intents=intents,command_prefix='!')
main_logger = setup(client)

# Asynchronous function calls inherited from the client class (i think)
# when the client class runs (using the token to authenticate) it sends events back to the bot like on_ready and on_message
#@client.event signifies the following function as based on the results of a client event

# Actions to take after the client successfully authenticates and reports the ready status
@client.event
async def on_ready():
  main_logger.info('Logged on as: {0.user}'.format(client))
  main_logger.info('Connected to ' + str(len(client.guilds)) + " servers")
  main_logger.debug("Processing connected servers...")
  for guild in client.guilds:
    if guild.id not in client.server_ids:
      main_logger.info("NEW SERVER Name: {0};ID: {1};Owner: {2}".format(guild.name,guild.id,guild.owner))
      server = client.addServer(guild.id,guild.name,guild.owner)
      # Identify Role objects for schedulizer-based roles
      main_logger.info("Processing roles for server {0}...".format(server.name))
      server.mapRole(discord.utils.find(lambda r: r.name == "Raider",guild.roles),"Raider")
      main_logger.debug("Mapped RAIDER schedule to Role {0}".format(server.Raider))
      server.mapRole(discord.utils.find(lambda r: r.name == "Social",guild.roles),"Social")
      main_logger.debug("Mapped SOCIAL schedule to role {0}".format(server.Social))
      server.mapRole(discord.utils.find(lambda r: r.name == "Member",guild.roles),"Member")
      main_logger.debug("Mapped MEMBER schedule to role {0}".format(server.Member))
      server.mapRole(discord.utils.find(lambda r: r.name == "Pug",guild.roles),"PUG")
      main_logger.debug("Mapped PUG schedule to role {0}".format(server.PUG))
      main_logger.info("Completed processing roles for server {0}".format(server.name))
      # Create user objects for each player with a valid schedule role
      main_logger.info("Processing members for {0}...".format(server.name))
      for member in guild.members:
        try:
          p = Player(member.name,sched=discord.utils.find(lambda r: r == server.Raider or r == server.Social or r == server.Member or r == server.PUG,member.roles).name)
          server.updateRoster(p)
          main_logger.debug("Created Player Object: Name:{0};Schedule:{1};Roles:{2}".format(p.name,p.sched,p.roles))
        except AttributeError:
          continue
      main_logger.info("Completed processing members for {0}".format(server.name))
      main_logger.info("New server setup complete for {0}".format(server.name))
    else:
      main_logger.info("KNOWN SERVER Name: {0};ID: {1};Owner: {2}".format(guild.name,guild.id,guild.owner))
      server = client.servers[client.server_ids.index(guild.id)]
      main_logger.info("Getting roles from database for {0}...".format(server.name))
      server.getRoles(guild.roles)
      main_logger.info("Getting roster from database for {0}...".format(server.name))
      server.getRoster()
      main_logger.info("Getting events from database for {0}...".format(server.name))
      server.getEvents()
      main_logger.info("Known server setup complete for {0}".format(server.name))
    try:
      main_logger.info("Roles for {0}: RAIDER/{1},SOCIAL/{2},MEMBER/{3},PUG/{4}".format(server.name,server.Raider.name,server.Social.name,server.Member.name,server.PUG.name))
    except AttributeError:
      main_logger.info("No mapped roles for {0}".format(server.name))
    main_logger.info("Setting up timekeeper for {0}".format(server.name))
    server.timekeeper = timekeeper.TimeKeeper(server.id,server.name,server.db_path,server.exitFlag,server.event_lock)
    server.timekeeper.start()
    main_logger.info("Timekeeper for {0} started".format(server.name))
    main_logger.info("Initialization for {0} complete".format(server.name))
  main_logger.info("Schedulizer initialization complete")

@client.event
async def on_command(context):
  # run this parent function whenever a command is received
  main_logger.info("Received command; Server: {0}; Channel: {1}; Message: {2}; User: {3}".format(context.guild.name,context.channel,context.message.content,context.author))

@client.event
async def on_command_completion(context):
  # run this parent function whenever a command completes
  status = "ERROR"
  if context.command_failed:
    status = "FAIL"
  else:
    status = "SUCCESS"
  main_logger.info("Command complete, status {0}; Server: {1}; Channel: {2}; Message: {3}; User: {4}".format(status,context.guild.name,context.channel,context.message.content,context.author))
  
@client.command(name="hello",help="Prints 'Hello World!'")
async def helloWorld(context):
  await context.send("Hello World!")

@client.command(name="show",help="Displays different information.\nUsage: !show [roster|events]\nNote: !show roster only shows players on the Raider or Social schedule. To see other players use !player show <name>")
async def show(context,opt: str):
  server = client.servers[client.server_ids.index(context.guild.id)]
  if opt == "roster":
    ## TODO - this displays really weird, find a better way to show the roster as a command
    ### have to send each line individually, roster gets too big for a single message
    ### maybe write it to a file, upload the file, then delete the file?
    roster = map(lambda x: str(x),list(filter(lambda x: x.sched == "Raider" or x.sched == "Social",server.roster)))
    await context.trigger_typing()
    await context.send("\n".join(roster))
  elif opt == "events":
    server.event_lock.acquire()
    server.events_db._loaddb()
    events = []
    for key in server.events_db.getall():
      e = server.events_db.get(key)
      events.append("Type: "+e[0]+"\tName: "+e[2]+"\tDate: "+e[1])
    if len(events) > 0:
      await context.send("\n".join(events))
    else:
      await context.send("No events currently scheduled for this server")
    server.event_lock.release()
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
          ## TODO - log this error
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
        e = Event(d,name,rec)
      else:
        e = Event(d,name,rec,frequency)
    elif type == 'raid':
      e = Raid(d,name,rec,frequency)
    result = server.addEvent(e)
    message = ""
    if result:
      message = "Successfully added event {0}".format(e.name)
      ## TODO - log successful event creation
    else:
      message = "WARNING: Unable to add event"
      ## TODO - log this error
  elif operation == "delete":
    server.deleteEvent(name,type,date,time)
    message = "Successfully deleted {0} instance(s) of event {1}".format(type,name)
    # TODO - log event deletion
  elif operation == "set":
    if property == "date":
      value = datetime.datetime.strptime(value,"%d%b%Y")
    elif property == "time":
      value = datetime.datetime.strptime(value,"%H:%M")
    if d:
      server.setEvent(type,name,property,value,d)
    else:
      server.setEvent(type,name,property,value)
    message = "Successfully changed property {0} of event {1} to {2}".format(property,name,value)
    # TODO - log event change
  await context.send(message)

@client.command(name="player",help="Manipulate Player objects.\nUsage:\n!player set <name> <property> <val>\n!player show <name>\nNote: To set multiple roles for a player, use the following syntax: !player set <name> roles <first Role>,<second Role>")
async def player(context, *args):
  operation, name, property, value = [None]*4
  try:
    operation = args[0]
    name = args[1]
    property = args[2]
    value = args[3]
  except IndexError:
    None
  # Check the operation is approved
  if operation == "set":
    if property == None:
      raise ValueError("Operation \'set\' requires input \'property\'")
    elif value == None:
      raise ValueError("Operation \'set\' requires input \'value\'")
  elif operation == "show":
    ## Pass, show just needs a name
    None
  else:
    raise ValueError("Unknown operation")
  # check we got a name
  if name == None:
    raise ValueError("Input \'name\' required")
  # locate the player object
  server = client.servers[client.server_ids.index(context.guild.id)]
  player = next(filter(lambda p: p.name == name,server.roster))
  if player == None:
    raise ValueError("Unknown Player")
  # make sure the player object has a property associated with the input
  if property != None and not hasattr(player,property):
    raise ValueError("Unknown property")
  ## SHOW
  if operation == "show":
    await context.send(str(player))
  elif operation == "set":
    if property == "roles":
      value = value.split(",")
      ## check that the user input valid roles
      for r in value:
        if r not in ["Tank","Healer","DPS"]:
          raise ValueError("Unknown role")
    server.changePlayer(player,property,value)
    #await context.send("STUB SET\tname: {1};property: {2};value: {3}".format(operation,name,property,value))
    await context.send("Changed property {0} of player {1} to {2}".format(property,name,str(value)))
  else:
    # TODO - log internal error
    raise RuntimeError("Unknown operation")

@client.command(name="update",help="Force the server to rebuild certain components\nUsage:\t!update <component>\nAvailable Components: roster")
async def update(context,component):
  if component == "roster":
    server = client.servers[client.server_ids.index(context.guild.id)]
    for member in context.guild.members:
      try:
        p = Player(member.name,sched=discord.utils.find(lambda r: r == server.Raider or r == server.Social or r == server.Member or r == server.PUG,member.roles).name)
        server.updateRoster(p)
      except AttributeError:
        continue
  else:
    raise ValueError("Unknown component")
  # TODO - log the request to update the roster
  await context.send("Update complete, issue \'!show roster\' to check")

@client.event
async def on_command_error(context,error):
  if isinstance(error,discord.ext.commands.errors.CheckFailure):
    main_logger.warning("User {0}/{1} attempted to issue command {2}".format(context.user,context.guild.name,context.message))
    await context.send('You do not have the correct role for this command.')
  elif isinstance(error,discord.ext.commands.errors.MissingRequiredArgument):
    await context.send_help(context.command)
  elif isinstance(error,discord.ext.commands.errors.CommandNotFound):
    await context.send("Unrecognized command")
    await context.send_help()
  else:
    await context.send(":".join(str(error).split(":")[1:]))
    await context.send_help(context.command)

# Call the client run method of the previously created discord client, using the value of the TOKEN key in the current directory's environment file, .env
load_dotenv()
TOKEN = os.getenv('TOKEN')
client.run("ODAzNjc0MTI2NjkwMTU2NTU1.YBBN2w.KhfB1kwGoiXG5mz6TcFQ5Ufe0mc")

# another wrapper so that my logs will be pretty
def shutdown(client):
  main_logger.info("Commencing shutdown...")
  for server in client.servers:
    main_logger.info("Shutting down {0}".format(server.name))
    server.exitFlag.set()
    main_logger.debug("Waiting for timekeeper to close on server {0}...".format(server.name))
    server.timekeeper.join()
    main_logger.debug("TimeKeeper closed for server {0}".format(server.name))
    main_logger.info("Server {0} shutdown complete".format(server.name))
  main_logger.info("Shutdown complete")

shutdown(client)