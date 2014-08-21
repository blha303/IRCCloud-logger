IRCCloud-logger
==========

Project discussion: irc://irc.irccloud.com/#logger <sup>([webirc](https://kiwiirc.com/client/irc.irccloud.com/?nick=logger|?#logger))</sup>

This project uses [websocket-client](https://github.com/liris/websocket-client). Use `pip install https://github.com/liris/websocket-client/archive/master.zip` to install it.

Python program for producing text logs from IRCCloud's stream and backlog.

Currently saves log names as base64, because, come on, if you need the filenames, you can parse the name. Nicknames can contain characters that don't work in filenames, and converting the filename to base64 removes that problem.

Authentication and backlog-loading issues solved by moving to websocket instead of https. Many thanks to @l1am9111 for doing this.

Configuration
-------------
Configuration goes in a file named ~/.irccloudrc, and should contain either "email" and "password" keys, or a "cookie" key.
Example:
{
 "email": "example@example.com",
 "password": "passwordgoeshere"
}

Contributing
------------

* Please make all code conform to PEP8, including the 80 character limit per line. Use the tool `pep8` available from pip if needed.
