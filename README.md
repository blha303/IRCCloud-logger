IRCCloud-logger
---------

Python program for producing text logs from IRCCloud's stream and backlog.

Currently saves log names as base64, because, come on, if you need the filenames, you can parse the name. Nicknames can contain characters that don't work in filenames, and converting the filename to base64 removes that problem.

Currently auth doesn't work. Please pull-request a fix if you find one. Until then, use `curl -d email=email -d password=password https://www.irccloud.com/chat/login` to get your session ID, then edit logger.py and put the session ID in tmpcookie at the top. TODO: fix this, it's awful.

Currently loads backlog from a text file in the same folder. To get this file (`backlogdemooutput.txt`), log in at https://www.irccloud.com, go to https://www.irccloud.com/chat/stream, look for the line starting with `{"bid":-1,"eid":-1,"type":"oob_include"` (it's directly after a blank line), copy the URL from `/chat/oob-loader` to just before the quote mark to the address bar replacing `/chat/stream`. You have to do this within two seconds of seeing the page. I'm thinking of putting together a tool to do this, if I can't get backlog automatically. (At the moment, the program is too slow to get the backlog. Please fix if you can.)