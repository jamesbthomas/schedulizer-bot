# Logs
This folder contains log files pertaining to the Schedulizer-Bot.
## Structure
There will be one main log file with log messages in the following format: <timestamp>: <log_level> - <facility> - <server> - <message>
Where facility identifies the component of the Schedulizer sending the message, and the server identifies the server the message came from. For example, when the schedulizer starts it will log the following message: "<timestamp>: INFO - main - main - Schedulizer initiation complete". Additionally, servers will log players signing up/out for events in the following message: "<timestamp>: INFO - main - <server name> - Player '<player name>' signed <up/out> for event <event name>". Lastly, different server components will also log their actions, including the timekeeper thread which will log event changes in the following format: "<timestamp>: INFO - timekeeper - <server name> - Created/Removed event <event name> scheduled for <event date and time>"

NOTE: prior to the creation of the logger AND when the log level is set to DEBUG, messages will also be logged to the console without accompanying timestamps