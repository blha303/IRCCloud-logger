IRCCloud-logger
==========

Project discussion: irc://irc.irccloud.com/#logger <sup>([webirc](https://kiwiirc.com/client/irc.irccloud.com/?nick=logger|?#logger))</sup>

This project uses [websocket-client](https://github.com/liris/websocket-client). Use `pip install https://github.com/liris/websocket-client/archive/master.zip` to install it.

Python program for producing text logs from IRCCloud's stream and backlog.

Currently saves log names as base64, because, come on, if you need the filenames, you can parse the name. Nicknames can contain characters that don't work in filenames, and converting the filename to base64 removes that problem.

Authentication and backlog-loading issues solved by moving to websocket instead of https. Many thanks to @l1am9111 for doing this.

Contributing
------------

* Please make all code conform to PEP8, including the 80 character limit per line. Use the tool `pep8` available from pip if needed.

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/blha303/irccloud-logger/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

