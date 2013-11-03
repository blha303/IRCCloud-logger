IRCCloud-logger
---------

Python program for producing text logs from IRCCloud's stream and backlog.

Currently saves log names as base64, because, come on, if you need the filenames, you can parse the name. Nicknames can contain characters that don't work in filenames, and converting the filename to base64 removes that problem.

Authentication and backlog-loading issues solved by moving to websocket instead of https. Many thanks to @l1am9111 for doing this.