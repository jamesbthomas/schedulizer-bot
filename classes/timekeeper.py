# Defines the TimeKeeper class as an extension of the Thread class for time-based actions

import threading, pickledb, os
import event

class TimeKeeper (threading.Thread):

  def __init__(self,serverID,name,db_path,exitFlag,db_lock):
    threading.Thread.__init__(self)
    self.serverID = serverID
    self.db_path = db_path
    self.name = name
    self.exitFlag = exitFlag
    self.db_lock = db_lock

  def run(self):
    ## what to do while the thread is running
    print("Starting thread for ",self.name)
    keepTime(self.exitFlag,self.db_path,self.db_lock)
    print("Exiting thread for ",self.name)

def keepTime(exitFlag,db_path,db_lock):
  ## Function to keep track of events as time passes
  while not exitFlag.isSet():
    # get the lock
    db_lock.acquire()
    # get the current list of events from the DB
    db = pickledb.load(os.path.join(db_path,"events.db"),False)
    events = db.getall()
    # check all events
    now = datetime.datetime.now()
    for event in events:
      e = db.get(event)
      # if this event occurs in the future, pass
      if e[1] > now:
        continue
      # this event has already occured
      elif e[1] < now:
        # remove this event from the database
        e_id = hashlib.md5("{0}{1}".format(e[2],e[1]).encode("utf-8")).hexdigest()
        db.rem(e_id)
        # if this event is recurring
        d = e[1]
        if e.recurring:
          db.rem(e)
          # if it occurs every week
          if e[4] == "weekly":
            d = d + datetime.timedelta(7)
          elif e[4] == "monthly":
            d = d + datetime.timedelta(28)
          else:
            raise RuntimeError("Unknown frequency")
        if e[0] == "event":
          newEvent = event.Event(d,e.name,e.recurring,e.frequency)
          eList = ["event",e[1],e[2],e[3],e[4]]
          db.set(newEvent.name,eList)
        elif e[0] == "raid":
          newEvent = event.Raid(d,e.name,e.recurring,e.frequency)
          eList = ["raid",e[1],e[2],e[3],e[4]]
          db.set(newEvent.name,eList)
        else:
          db_lock.release()
          raise RuntimeError("Unknown Event type")
      # run time error
      else:
        db_lock.release()
        raise RuntimeError("Date comparison failed")
    # dump the database
    db.dump()
    # release the lock
    db_lock.release()
  return