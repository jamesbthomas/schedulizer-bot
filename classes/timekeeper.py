# Defines the TimeKeeper class as an extension of the Thread class for time-based actions

import threading, pickledb, os, datetime, hashlib, logging, time
import event

class TimeKeeper (threading.Thread):

  def __init__(self,serverID,name,db_path,exitFlag,db_lock,test_mode = False):
    # Generate a child logger of the root for this server
    self.logger = logging.getLogger("schedulizer.{0}.TimeKeeper".format(name))
    self.logger.info("Creating new TimeKeeper for {0}".format(name))

    threading.Thread.__init__(self)
    self.serverID = serverID
    self.db_path = db_path
    self.name = name
    self.exitFlag = exitFlag
    self.db_lock = db_lock
    self.test_mode = test_mode

  def run(self):
    ## what to do while the thread is running
    self.logger.info("Starting TimeKeeper")
    keepTime(self.exitFlag,self.db_path,self.db_lock,self.logger,self.name,self.test_mode)
    self.logger.info("Stopping TimeKeeper...")

def keepTime(exitFlag,db_path,db_lock,logger,name, test_mode = False):
  ## Function to keep track of events as time passes
  logger.info("Thread started")
  while not exitFlag.isSet():
    logger.debug("Starting to process events for {0}".format(name))
    # get the lock
    db_lock.acquire()
    try:
      # get the current list of events from the DB
      db = pickledb.load(os.path.join(db_path,"events.db"),False,sig=False)
      # check all events
      now = datetime.datetime.now()
      for key in list(db.getall()):
        e = db.get(key)
        eDate = datetime.datetime.fromisoformat(e[2])
        # if this event occurs in the future, pass
        if eDate > now:
          logger.debug("Event {0} on server {1} is in the future".format(key,name))
          continue
        # this event has already occured
        elif eDate < now:
          logger.debug("Event {0} is expired".format(key))
          # remove this event from the database
          db.rem(key)
          logger.debug("Expired Event {0} removed from DB".format(key))
          # if this event is recurring
          d = eDate
          if e[4]:
            logger.debug("Expired Event {0} is recurring".format(key))
            # if it occurs every week
            if e[5] == "weekly":
              d = d + datetime.timedelta(7)
            elif e[5] == "monthly":
              d = d + datetime.timedelta(28)
            else:
              logger.critical("Unknown Frequency; server:{0};event:{1}".format(name,e))
              raise RuntimeError("Unknown frequency")

            if e[0] == "event":
              newEvent = event.Event(e[1],d,e[3],e[4],e[5])
              eList = ["event",e[1],str(newEvent.date),newEvent.name,newEvent.recurring,newEvent.frequency]
            elif e[0] == "raid":
              newEvent = event.Raid(e[1],d,e[3],e[4],e[5])
              eList = ["raid",e[1],str(newEvent.date),newEvent.name,newEvent.recurring,newEvent.frequency]
            else:
              logger.critical("Unknown Event type; server:{0};event: {1}".format(name,e))
              raise RuntimeError("Unknown Event type")
            logger.debug("Future Event {0} added to DB".format(key))
            db.set(newEvent.name,eList)
        # run time error
        else:
          logger.critical("Date comparison failed; server:{0};event:{2}".format(name,e))
          raise RuntimeError("Date comparison failed")
      # dump the database
      db.dump()
    finally:
      # release the lock
      db_lock.release()
    # sleep so that this thing doesnt just spin endlessly forever
    if not test_mode and not exitFlag.isSet():
      logger.debug("Sleeping...")
      time.sleep(30)
  logger.info("Stopping...")
  return