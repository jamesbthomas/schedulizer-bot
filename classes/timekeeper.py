# Defines the TimeKeeper class as an extension of the Thread class for time-based actions

import threading, pickledb, os, datetime, hashlib
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
    try:
      # get the current list of events from the DB
      db = pickledb.load(os.path.join(db_path,"events.db"),False,sig=False)
      # check all events
      now = datetime.datetime.now()
      for key in list(db.getall()):
        e = db.get(key)
        eDate = datetime.datetime.fromisoformat(e[1])
        # if this event occurs in the future, pass
        if eDate > now:
          continue
        # this event has already occured
        elif eDate < now:
          # remove this event from the database
          db.rem(key)
          # if this event is recurring
          d = eDate
          if e[3]:
            # if it occurs every week
            if e[4] == "weekly":
              d = d + datetime.timedelta(7)
            elif e[4] == "monthly":
              d = d + datetime.timedelta(28)
            else:
              raise RuntimeError("Unknown frequency")

            if e[0] == "event":
              newEvent = event.Event(d,e[2],e[3],e[4])
              eList = ["event",str(newEvent.date),newEvent.name,newEvent.recurring,newEvent.frequency]
            elif e[0] == "raid":
              newEvent = event.Raid(d,e[2],e[3],e[4])
              eList = ["raid",str(newEvent.date),newEvent.name,newEvent.recurring,newEvent.frequency]
            else:
              raise RuntimeError("Unknown Event type")
            db.set(newEvent.name,eList)
        # run time error
        else:
          raise RuntimeError("Date comparison failed")
      # dump the database
      db.dump()
    finally:
      # release the lock
      db_lock.release()
  return