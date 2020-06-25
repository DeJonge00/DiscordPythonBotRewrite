# Discord Python Bot "Biribiri"
#### Notes
The default prefix for Biribiri is the character `>`, this can be changed with the `prefix` command.\
If you forgot the prefix you set, you can mention Biribiri with the word `prefix`.\
\
`words`: literally the word(s) in the brackets (choices separated by a `,`)\
_`words`_: variable string, describing any word(s) you need\
___`user`___: Mentioning the user, or giving a name in text (using only characters in a-z, A-Z or 0-9)
this second will prompt you to choose an option if multiple are found.\
_Do note that the text does not need to be italic or bold, this is simply a way to clarify the type of argument in the help text_\
\
The response message `Hahaha, no.` indicates that you lack the permissions to use the command.\
\
Biribiri is still in development, comments and improvements are welcome by messaging `Nya#2698` to contact me\
There are also commands for complaints, suggestions and bugreports, or an invitelink to a helpserver, which can be found below.

The commands marked with the __WIP__ tag have not been added to the rewritten version yet

### Reactions to messages

|Message                                |Reaction                           |Reaction disable command
|---                                    |---                                |---
|`\o/`                                  |Praise the sun!                    |`togglecommand server \\o/` or `togglecommand channel \\o/`
|`ded` (After a period of no messages)  |Cry about a ded chat               |`togglecommand server response_ded` or `togglecommand channel response_ded`
|`(╯°□°）╯︵ ┻━┻`                        | `┬─┬ ノ( ゜-゜ノ)`                 |`togglecommand server tableflip` or `togglecommand channel tableflip`
|`ayy`                                  |`lmao`                             |`togglecommand server ayy` or `togglecommand channel ayy`
|`lenny`                                |`( ͡° ͜ʖ ͡°)`                      |`togglecommand server response_lenny` or `togglecommand channel response_lenny`
|Mentions, `biri` or `biribiri`         |I will talk to your lonely self    |`togglecommand server talk` or `togglecommand channel talk`

### Basic commands

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|botstats       |`botstats,botinfo`                                     |Show stats of the bot in an embed
|cast        	|`cast` ___`user`___                                    |Cast a spell targeted at ___`user`___
|compliment  	|`compliment` ___`user`___                              |Give ___`user`___ a compliment
|cookie         |`cookie`                                               |Click the cookie, let's see how far we come. For teh greater good!
|countdown      |`countdown` _`seconds`_                                |Ping on times until the seconds run out (dms only for spam reasons)
|delete      	|`del,delete,d` _`seconds`_ _`normal message`_          |Make biri delete your message after _`seconds`_ seconds
|dice           |`dice,roll` _`number`_ `d` _`number`_ `k` _`number`_   |Roll some dice. State the amount of dice (optional), the type of dice, and how many you keep (optional, for example `4d6k3` means roll a d6 4 times and keep the highest 3) Examples: `d6`, `2d4`, `4d6k3`, `1d4+2d6`.
|               |`dice,roll` `stats`                                    |Rolls `4d6k3` 6 times, the default rolling for stats in Dnd 5E.
|echo        	|`echo` _`text`_                                        |Biri repeats _`text`_ (Images can only be echoed if toggledeletecommands is set to false)
|embed          |`embed` _`text or single attachment`_                  |Send an embed of _`text`_ or an _`attachment`_
|emoji       	|`emoji` _`emoji`_                                      |Send a big version of _`emoji`_
|emojify     	|`emojify` _`text`_                                     |Transform _`text`_ to regional indicators
|face        	|`face`                                                 |Send a random ascii face
|hug         	|`hug` ___`user`___                                     |Give ___`user`___ a hug
|hype           |`hype`                                                 |Make hype by sending 10 random emoji from the current server
|kick        	|`kick` ___`user`___                                    |Fake kick ___`user`___
|kill        	|`kill` ___`user`___                                    |Wish ___`user`___ a happy death (is a bit explicit)
|kiss        	|`kiss` ___`user`___                                    |Give ___`user`___ a little kiss
|lenny       	|`lenny` _`message`_                                    |Send _`message`_ `( ͡° ͜ʖ ͡°)`
|lottery __WIP__    	|`lottery` _`description`_                          |Set up a lottery, ends when creator adds the correct reaction
|nice           |`nice`                                                 |Figure out how nice you are
|               |`nice` ___`user`___                                    |Figure out how nice ___`user`___ is
|pat         	|`pat` ___`user`___                                     |Pat ___`user`___, keeps track of pats
|quote          |`quote`                                                |Fetch a random quote from the internet
|role           |`role` _`rolename`_                                    |Add or remove the role _`rolename`_ from yourself, if it is in the self-assignable roles list. Give to rolename argument to see a list of roles
|serverinfo  	|`serverinfo,serverstats`                               |Get the server's information
|userinfo    	|`userinfo,user,info` ___`user`___                      |Get ___`user`___'s information

### Image commands

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|fps __WIP__        	|`fps,60`                                               |Send a high-fps gif
|biribiri __WIP__   	|`biribiri,biri`                                        |Send pics of the only best girl
|cat        	|`cat`                                                  |Pictures of my cats
|cuddle      	|`cuddle`                                               |Send a cuddly gif
|cute           |`cute`                                                 |For when you need a cute anime girl gif
|ded __WIP__        	|`ded`                                                  |Ded chat reminder (image)
|heresy     	|`heresy`                                               |Send images worthy of the emperor (warhammer 40k)
|happy          |`happy`                                                |Send a happy gif
|lewd           |`lewd`                                                 |Send anti-lewd gif
|love           |`love`                                                 |Send a confession of love through a gif
|nonazi __WIP__     	|`nonazi`                                               |Try to persuade Lizzy with anti-nazi-propaganda!
|nyan           |`nyan`                                                 |Send an anime happy catgirl gif
|otter          |`otter`                                                |Send a cute otter picture
|plsno          |`plsno`                                                |Send a gif that expresses 'pls no'
|pp          	|`pp,avatar,picture` ___`user`___                           |Show ___`user`___'s profile pic, a bit larger
|sadness        |`sadness`                                              |Send a sad gif

### Lookup commands

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|anime          |`anime,mal,myanimelist` _`title`_                      |Search for the MAL entry of the anime _`title`_
|game           |`game` _`title`_                                       |Search for a description of the video game named _`title`_ 
|manga          |`manga` _`title`_                                      |Search for the MAL entry of manga _`title`_
|movie          |`movie,imdb` _`title`_                                 |Search for the IMDb entry of movie _`title`_
|osu            |`osu` _`playername`_                                   |Search profile data for a popular rhythm game
|urban       	|`urban,us,urbandictionary` _`query`_                   |Search urbandictionary for _`query`_
|wikipedia   	|`wikipedia,wiki` _`query`_                             |Search wikipedia for _`query`_


### Hangman

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|hangman     	|`hm, hangman` `create,new` `custom,c,random,r` _`sentence`_         |Create a new hangman game
|               |`hm, hangman` _`guess`_                                |Guess a letter or sentence in the current hangman game

### Minesweeper

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|minesweeper  	|`minesweeper,ms`                                       |Minesweeper game
|               |`minesweeper,ms` `create,new` _`height`_ _`width`_ _`mines`_  |Create a new minesweeper board
|               |`minesweeper,ms` _`x`_ _`y`_                           |Guess a non-mine at coordinates (x,y)
|               |`minesweeper,ms` `quit`                                |Forfeit the current game

### Trivia

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|trivia       	|`trivia,tr` `new`                                      |Create a new trivia game
|               |`trivia,tr` `categories,cat`                           |Display question categories for Trivia
|               |`trivia,tr` `join`                                     |Join an upcoming turn by turn Trivia game on the channel
|               |`trivia,tr` `quit`                                     |Quit the game you're currently playing                                           

### Other games

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|blackjack      |`blackjack` `d,draw`                                   |Draw another card
|               |`blackjack` `s,stop,f,fold`                            |Stop drawing and resolve the game
|connectfour    |`connectfour,c4`                                       |Play a game of connect four with another user, use the reactions to play the game
|               |`connectfour,c4` `reset,stop,quit`                     |Quit the current game

### Misc

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|inviteme    	|`inviteme`                                             |Invite me to your own server
|helpserver  	|`helpserver`                                           |Join my masters discord server if questions need answering
|suggestion     |`suggestion,suggest`                                   |Give the bot-owners a suggestion to improve the bot
|complaint      |`complain,complaint`                                   |Complaint about bad practices, or just about whatever irritates you to the bot-owners
|bugreport      |`bug,bugreport`                                        |Notify the bot-owners of a bug in the commands, or an error in the help or readme
|vote           |`vote`                                                 |Vote for me! This makes me more popular, which results in more attention from my master...

### Mod

|Name			|Command, aliases and usage					            |Description                                                                                |Permissions needed
|---			|---										            |---                                                                                        |---
|autovc         |`autovc` _`channel-name`_                                | Create a voice-channel that multiplies when users join. These extra voice channels will be removed when there is nobody in them. | manage_channels
|banish      	|`banish` ___`user`___                                      |Ban ___`user`___                                                                               |kick_members
|invite         |`invite` _`max members`_                               |Create an invite. Maximum _`max-members`_ members, unlimited if not given, will be active for 24 hours   |create_instant_invite
|               |`invite`                                               |Find an active invite in the server and show it, no mod-powers needed                      |manage_guild
|membercount    |`membercount,membercounter`                            |Create a locked channel in the channel list, which will be updated with the amount of members currently in the server | manage_channels
|nickname __WIP__   	|`nickname,nn` ___`user`___ _`new_name`_                    |Nickname a person                                                                          |change_nickname, manage_nicknames
|purge       	|`purge` _`amount`_ ___`user`___                        |Remove ___`user`___'s messages (all if user is not given) from the past _`amount`_ messages    |manage_messages
|setwelcome  	|`setwelome` _`message`_                                |Sets a welcome message                                                                     |manage_server
|setgoodbye  	|`setgoodbye` _`message`_                               |Sets a goodbye message                                                                     |manage_server
|togglerole     |`togglerole,sarole,toggleassignable` _`rolename`_      |Add or remove a role to the list of self-assignable roles                                  |manage_roles


### Config
|Name			        |Command, aliases and usage					            |                                                                                   |Permissions needed
|---			        |---										            |---                                                                                |---
|toggledeletecommands   |`toggledeletecommands,tdc`                             |Toggles whether commands will be deleted. Commands are deleted by default          |manage_channels, manage_messages
|togglecommand          |`togglecommand,tc` `server,channel` _`command name`_   |Toggles whether the command _`command name`_ can be used in the current `server,channel`. Use command name `all` to disable all commands. All commands are enabled by default      |manage_channels, manage_messages
|prefix                 |`prefix` _`prefix text`_                               |Changes the prefix to _`prefix text`_, ignoring trailing spaces

### MusicPlayer

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|music          |`music,m`                                              |All music commands start with _`prefix`_ `music` or _`prefix`_ `m`
|reset          |`music,m` `reset`                                      |Reset the player for this server
|leave          |`music,m` `leave,l`                                    |Let Biribiri leave voice chat
|skip           |`music,m` `skip,s` _`number`_                          |Vote to skip a song, or just skip it if you are the requester
|               |                                                       |No number given means voting to skip the current song
|queue          |`music,m` `queue,q`                                    |Show the queue 
|               |`music,m` `queue,q` _`songname,url`_                   |Add a song to the queue
|repeat         |`music,m` `repeat,r`                                   |Repeat the current song
|volume         |`music,m` `volume,v`                                   |Change the volume of the songs
|current        |`music,m` `current,c`                                  |Show information about the song currently playing
|stop           |`music,m` `stop`                                       |Empty the queue and skip the current song, then leave the voice channel
|play           |`music,m` `play,p`                                     |Pause or resume singing 
|               |`music,m` `play,p` _`songname,url`_                    |Add a song to the queue
|join           |`music,m` `join,j`                                     |Let Biribiri join a voice channel

### RPGGame

|Name			|Command, aliases and usage					            |Description
|---			|---										            |---
|rpg            |`rpg,b&d,bnd` `help`                                   |Show the info for the RPG game
|role           |`rpg,b&d,bnd` `r,role` _`rolename`_                    |Assign yourself a role (required to start the game)
|setchannel     |`rpg,b&d,bnd` `setchannel`                             |The current channel will be where Biribiri sends bossbattle results
|adventure      |`rpg,b&d,bnd` `a,adventure` _`time`_                   |Go on an adventure to slay monsters
|wander         |`rpg,b&d,bnd` `w,wander` _`time`_                      |Go wandering, its a less costly adventuring
|battle         |`rpg,b&d,bnd` `b,battle` ___`user`___                  |Battle another player of the game
|info           |`rpg,b&d,bnd` `i,info` ___`user`___                    |View ___`user`___'s battlestats
|               |`rpg,b&d,bnd` `i,info` `weapon,w,armor,a` ___`user`___ |View ___`user`___'s weapon or armor stats
|party          |`rpg,b&d,bnd` `p,party`                                |Show the current party that will challenge the boss at the hour mark
|join           |`rpg,b&d,bnd` `j,join`                                 |Join the upcoming bossfight
|king           |`rpg,b&d,bnd` `k,king`                                 |Show who is the server's current king
|               |`rpg,b&d,bnd` `k,king` `c,b,challenge,battle`          |Challenge the king (level 10 required)
|levelup        |`rpg,b&d,bnd` `levelup,lvlup,lvl`                      |Claim your level-up rewards
|top            |`rpg,b&d,bnd` `top` `exp,money,bosstier`               |Show the top players of the game
|pet            |`rpg,b&d,bnd` `pet,pets`                               |Show the pets you own
|               |`rpg,b&d,bnd` `pet,pets` `r,release,remove` _`pet number`_ |Release a pet to make room for a different one
|train          |`t,train` `ws,weapon,weaponskill`                      |Train your weaponskill
|               |`t,train` `h,hp,health,maxhealth`                      |Train your maximum healthpool
|shop           |`s,shop` `armor`                                       |Show shop armor inventory
|               |`s,shop` `armor` _`itemnumber`_                        |Buy armor number _`itemnumber`_
|               |`s,shop` `item`                                        |Show shop item inventory
|               |`s,shop` `item` _`itemnumber`_                         |Buy item number _`itemnumber`_
|               |`s,shop` `weapon`                                      |Show shop weapon inventory
|               |`s,shop` `weapon` _`itemnumber`_                       |Buy weapon number _`itemnumber`_
|work           |`work`                                                 |Work for some money to spend in the shop

[![Discord Bots](https://discordbots.org/api/widget/244410964693221377.svg)](https://discordbots.org/bot/244410964693221377)