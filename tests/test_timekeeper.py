# Test-Driven Development for the TimeKeeper class
import pytest, sys, os, re, datetime, time, threading, hashlib, pickledb
project_root = os.path.split(os.path.dirname(__file__))[0]
sys.path.append(os.path.join(project_root,"classes"))

# Import module for testing
import event, server, timekeeper

def test_TimeKeeper():
  """
  GIVEN TimeKeeper constructor and appropriate inputs
  WHEN the method is called
  THEN create and return a correctly structured TimeKeeper for the given server
  """

  # Create the client
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  s1 = client.addServer(
    id = "firstServer",
    name = "Server for TimeKeeper",
    owner = "TestOwner"
  )
  s2 = client.addServer(
    id = "secondServer",
    name = "Second Server for TimeKeeper",
    owner = "TestOwner"
  )

  try:
    e = threading.Event()
    l = threading.Lock()
    t1 = timekeeper.TimeKeeper(s1.id,s1.name,s1.db_path,e,l)
    assert isinstance(t1,timekeeper.TimeKeeper)
    assert isinstance(t1,threading.Thread)
    assert t1.serverID == s1.id
    assert t1.name == s1.name
    assert t1.db_path == s1.db_path
    assert t1.exitFlag == e
    assert t1.db_lock == l
    e2 = threading.Event()
    l2 = threading.Lock()
    t2 = timekeeper.TimeKeeper(s2.id,s2.name,s2.db_path,e2,l2)
    assert isinstance(t2,timekeeper.TimeKeeper)
    assert isinstance(t2,threading.Thread)
    assert t2.serverID == s2.id
    assert t2.name == s2.name
    assert t2.db_path == s2.db_path
    assert t2.exitFlag == e2
    assert t2.db_lock == l2

  finally:
    os.remove(os.path.join(project_root,"databases","firstServer.db","server.db"))
    os.remove(os.path.join(project_root,"databases","firstServer.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","firstServer.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","firstServer.db"))
    client.servers.pop(client.server_ids.index("firstServer"))
    client.server_ids.pop(client.server_ids.index("firstServer"))
    os.remove(os.path.join(project_root,"databases","secondServer.db","server.db"))
    os.remove(os.path.join(project_root,"databases","secondServer.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","secondServer.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","secondServer.db"))
    client.servers.pop(client.server_ids.index("secondServer"))
    client.server_ids.pop(client.server_ids.index("secondServer"))

def test_keepTime():
  """
  GIVEN TimeKeeper object and list of events
  WHEN the method is called
  THEN remove old events and create new instances of repeating events
  """

  # Create the client
  client = None
  client = server.SchedClient(command_prefix='!')
  client.setup()
  s = client.addServer(
    id = "keepTime",
    name = "Server for keepTime tests",
    owner = "TestOwner"
  )
  d = datetime.datetime.now()
  ## create a recurring event that has already happened
  ### 2 days before now, weekly recurrence
  recHappenedW = event.Event(d-datetime.timedelta(2),"recurring event weekly",True,"weekly")
  ### 2 days before now, monthly recurrence
  recHappenedM = event.Event(d-datetime.timedelta(2),"recurring event monthly",True,"monthly")
  ## create a one-time event that has already happened
  onceHappened = event.Event(d-datetime.timedelta(2),"occurs once",False)
  onceH_str = "{0}{1}".format(onceHappened.name,str(onceHappened.date))
  onceH_id = hashlib.md5(onceH_str.encode("utf-8")).hexdigest()
  ## create a recurring event that has not happened
  recFuture = event.Event(d+datetime.timedelta(2),"future recurring event",True,"monthly")
  ## create a one-time event that has not happened
  onceFuture = event.Event(d+datetime.timedelta(2),"future one-time event",False)
  onceF_str = "{0}{1}".format(onceFuture.name,str(onceFuture.date))
  onceF_id = hashlib.md5(onceF_str.encode("utf-8")).hexdigest()
  ## add events to the server
  s.addEvent(recHappenedW)
  s.addEvent(recHappenedM)
  s.addEvent(onceHappened)
  s.addEvent(recFuture)
  s.addEvent(onceFuture)
  ## Make timekeeper
  ### use the threading module to track the exit flag and lock for the db, defaults to UNSET/FALSE
  exitFlag = threading.Event()
  db_lock = threading.Lock()
  t = timekeeper.TimeKeeper(s.id,s.name,s.db_path,exitFlag,db_lock)

  try:
    # run the thread
    t.start()
    # guarantee it will run for 5 seconds
    time.sleep(5)
    # signal the thread to stop
    exitFlag.set()
    # wait for thread to stop
    t.join()
    ## grab the db_lock as a second check to make sure everything is closed
    db_lock.acquire()
    s.events_db = pickledb.load(os.path.join(s.db_path,"events.db"),False)

    # run tests
    ## non-recurring previous event should be gone
    assert onceH_id not in s.events_db.getall()
    ## non-recurring future event should still be there
    assert onceF_id in s.events_db.getall()
    ## recurring previous event should have new instance
    ### weekly
    newHappenedW = event.Event(d-datetime.timedelta(2)+datetime.timedelta(7),"recurring event weekly",True,"weekly")
    assert newHappenedW.name in s.events_db.getall()
    e_db = s.events_db.get(newHappenedW.name)
    assert e_db
    print(e_db)
    assert newHappenedW.date == datetime.datetime.fromisoformat(e_db[1])
    assert newHappenedW.name == e_db[2]
    assert newHappenedW.recurring == e_db[3]
    assert newHappenedW.frequency == e_db[4]
    ### monthly
    newHappenedM = event.Event(d-datetime.timedelta(2)+datetime.timedelta(28),"recurring event monthly",True,"monthly")
    assert newHappenedM.name in s.events_db.getall()
    e_db = s.events_db.get(newHappenedM.name)
    assert e_db
    assert newHappenedM.date == datetime.datetime.fromisoformat(e_db[1])
    assert newHappenedM.name == e_db[2]
    assert newHappenedM.recurring == e_db[3]
    assert newHappenedM.frequency == e_db[4]

  finally:
    os.remove(os.path.join(project_root,"databases","keepTime.db","server.db"))
    os.remove(os.path.join(project_root,"databases","keepTime.db","roster.db"))
    os.remove(os.path.join(project_root,"databases","keepTime.db","events.db"))
    os.rmdir(os.path.join(project_root,"databases","keepTime.db"))
    client.servers.pop(client.server_ids.index("keepTime"))
    client.server_ids.pop(client.server_ids.index("keepTime"))