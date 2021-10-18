# schedulizer-bot
A Discord Bot to help World of Warcraft Raid Leaders create and manage guild events through Discord.

# Key Features
* Tracks players based on their role preference (Tank, Healer, and DPS) and one of four available schedules:
  * Raider: These players are members of the core group and are expected to be at every Raid event.
  * Social: These players are members of the core group, but are not expected to be at every Raid event due to other circumstances. (This schedule is great for people with overlapping commitments that can only make one Raid per week or every other week)
  * Member: These players are regular members of the guild/server that can sign up for Raid whenever they feel like it. They are not members of the core group, and they may not be able to play their most preferred role.
  * PUG: These players are random people that the group has played with before that might be interested in playing with the group again. These players receive the lowest prioritization when it comes to high-value roles.
* Create events and allow people to sign up. Event creators can also select from one of multiple event types with different behavior.
* Automatically selects the most optimal composition for supported event types based on a combination of player preference for high-value roles (like Tank and Healer) and schedule. (Currently only supported by the Raid event type)
  * For example, a player on Raider schedule that prefers to play DPS more than Tank will be selected to Tank over a player on the Member schedule that prefers to Tank over DPS. However, if the Member **only** wants to play Tank, they will be selected first in order to ensure everyone gets to play (and enjoy what they're playing).
* Maintains a depth chart to avoid conflicts when selecting roles and break ties when all else is equal.
  * For example, three players only want to play Tank - without the depth chart, the two selected Tank players would depend on whomever signed up first. Event creators and Raid Leaders maintain the depth chart to promote the overall efficiency of the Raid, ensuring the two most effective Tanks are selected first.

## Event Types
* Event - Generic event type that allows sign ups, but does not track roles or schedules. Useful when another event type does not meet your criteria. 
* Raid - Specific to Flex Raiding, this event type will automatically sign up all players on the Raider schedule, and allow all other schedules to sign up on their own. As players accept or decline the event, the Schedulizer will automatically recalculate the most effective setup, including the overall composition (Number of Tanks, Healers, and DPS) and the role assignments for signed up players.

## Selection Algorithm
The Schedulizer selects players for specific roles based on  a specific algorithm. This algorithm takes into account player schedules, player preferences, and the leader-maintained depth chart, in that order.
* 1) Determine the total number of players attending this event
  * This number (and the type of event) will determine the composition used. For example, if 25 people sign up for a raid, the Schedulizer to select the a 2 Tank, 5 Healer, 18 DPS composition.
  * If there are more people than feasible compositions, i.e. 31 or more people sign up for the raid, the Schedulizer will eliminate players by schedule, first PUGs, then Members.
  * If more than 30 players remain, the depth chart will break the tie based on a 2 Tank, 6 Healer, 22 DPS composition.
* 2) Select players for each role. The Schedulizer repeats the following steps three times: first for Tanks, then for Healers, and finally for DPS. If, after each substep, enough players have been selected to Tank, continue to the next step. If any substep results in a tie where more players are selected than there are available spots for that role, the depth chart breaks the tie.
  * a) Players who only want to perform the current role (excluding PUGs)
  * b) Raiders who have the current role as their first preference
  * c) Socials who have the current role as their first preference
  * d) Members who have the current role as their first preference
  * e) Raiders or Socials who have the current role as their second preference
  * f) Members who have the current role as their second preference
  * g) Raiders or Socials who have the current role as their third preference
  * h) Members who have the current role as their third preference
  * i) PUGs who have the current role as a preference

# Installing
Use the included makefile to install this on your system. The makefile supports the following targets:
* install: installs dependencies
* test: installs dependencies and runs all pytest batteries
* run: installs dependencies and runs the Schedulizer
* debug: installs dependencies and runes the Schedulizer in debug mode
* clean: removes dependencies
* all (Default): installs dependencies and runs all pytest batteries

**NOTE**: If you would like to run the Schedulizer on your own, be sure to setup an application and a bot through the Discord website. You can check the documentation for the official Discord python module for instructions on creating a bot account (https://discordpy.readthedocs.io/en/latest/discord.html).

If you would like to install the Schedulizer on your server without maintaining your own version, paste the following link into your browser and follow the prompts: https://discord.com/api/oauth2/authorize?client_id=803674126690156555&permissions=2147486784&scope=bot
**NOTE**: While the Bot remains in early development (prior to the release of v1.0), it will not be available publicly. Contact the maintainer at james.b.thomas@mac.com if you would like an exception.
Ensure you have the "Manage Server" permission on any server you want the bot to join.
## Dependencies
Python 3.8+, dotenv, pytest, pickledb, and discord python libraries.

# Development Milestones
## v0.1 - Initial release - No release date
* Basic system functionality, including logging, start-up and shutdown
* Commands to create, modify, and delete Events and Raids
* Automatic role assignments for Raids
* By-user sign ups for Events, and for Raids based on schedule
* Pre-Staged development environment leveraging Python3.8 virtual environments (Issue #16)
## v1.0 - Vanilla - No release date
* Privacy-oriented services that allow administrators and users to control the information the Schedulizer maintains
* Ad-Hoc and On-Demand configuration options, allowing server owners and administrators to configure/reconfigure key aspects of the app at will
* Depth Chart tracking to prevent non-deterministic role assignments and enable greater control of Raid compositions
