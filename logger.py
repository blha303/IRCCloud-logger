import requests
import time
import json
import os
import errno
import sys
import unicodedata
import base64

tmpcookie = "PUT COOKIE HERE"
s = requests.Session()
delay = 0.0
idleinterval = 0
user = {}
servers = {}
buffers = {}
whois = {}


def uni2str(inp):
    if isinstance(inp, unicode):
        return unicodedata.normalize('NFKD', inp).encode('ascii', 'ignore')
    elif isinstance(inp, str):
        return inp
    else:
        print inp


def auth(email, password):
    req = requests.post("https://www.irccloud.com/chat/login",
                        params={"email": email, "password": password})
    d = req.json()
    if d["success"]:
        return d["session"]
    else:
        return False


def streamiter(cookie):
    cookies = dict(session=cookie)
    req = requests.Request("GET",'https://www.irccloud.com/chat/stream',
                           cookies=cookies).prepare()
    resp = s.send(req, stream=True)
    for line in resp.iter_lines():
        if line:
            yield json.loads(line)


def parseline(line):
    msgfmt = "{time} <{nick}> {msg}"
    mefmt = "{time} * {nick} {msg}"
    noticefmt = "{time} -{nick}- {msg}"
    topicfmt = "{time} -!- {nick} changed the topic of {chan} to: {msg}"
    chjoinfmt = "{time} -!- {nick} [{usermask}] has joined {chan}"
    chpartfmt = "{time} -!- {nick} [{usermask}] has left {chan} [{msg}]"
    chkickfmt = "{time} -!- {nick} was kicked from {chan} by {kicker} [{msg}]"
    chquitfmt = "{time} -!- {nick} [{usermask}] has quit [{msg}]"
    chnickfmt = "{time} {old_nick} is now known as {new_nick}"
    with open("rawlog.json", "a") as f:
        f.write(json.dumps(line) + "\n")
    def getts(l):
        return time.gmtime(float(str(l["eid"])[:-6] + "." + str(l["eid"])[-6:]))
    def p_header(l):
        delay = int(time.time()) - l["time"]
    def p_idle(l):
        """ Do nothing """
    def p_stat_user(l):
        user.update(l)
    def p_num_invites(l):
        user["num_invites"] = l["num_invites"]
    def p_oob_include(l):
#        req = requests.get("https://www.irccloud.com" + l["url"], headers={"Accept-Encoding": "gzip"}).json()
#        if type(req) == dict:
#            return
        with open("backlogdemooutput.txt") as f:
            req = json.loads(f.read())
        for oobline in req:
            try:
                parseline(oobline)
            except:
                print json.dumps(oobline)
                raise
    def p_backlog_complete(l):
        """ Do nothing """
    def p_makeserver(l):
        if not l["cid"] in servers:
            servers[l["cid"]] = l
        else:
            servers[l["cid"]].update(l)
    def p_end_of_backlog(l):
        """ Do nothing """
    def p_makebuffer(l):
        ts = float(str(l["min_eid"])[:-6] + "." + str(l["min_eid"])[-6:])
        if l["name"] == "*":
            l["name"] = servers[l["cid"]]["name"]
        log("*** Buffer opened at " + time.ctime(ts),
            server=servers[l["cid"]]["name"],
            channel=l["name"],
            date=time.strftime("%Y-%m-%d", time.gmtime(ts)) )
    def p_channel_init(l):
        if not l["bid"] in buffers:
            buffers[l["bid"]] = l
        else:
            buffers[l["bid"]].update(l)
    def p_status_changed(l):
        print json.dumps(l)
    def p_connection_lag(l):
        servers[l["cid"]]["lag"] = l["lag"]
    def p_heartbeat_echo(l):
        """ Do nothing """
    def p_buffer_msg(l):
        ts = getts(l)
        log(msgfmt.format(time=time.strftime("%H:%M:%S", ts),
                          nick=l["from"],
                          msg=uni2str(l["msg"])),
            server=servers[l["cid"]]["name"],
            channel=l["chan"],
            date=time.strftime("%Y-%m-%d", ts) )
    def p_buffer_me_msg(l):
        ts = getts(l)
        log(mefmt.format(time=time.strftime("%H:%M:%S", ts),
                          nick=l["from"],
                          msg=l["msg"]),
            server=servers[l["cid"]]["name"],
            channel=l["chan"],
            date=time.strftime("%Y-%m-%d", ts) )
    def p_notice(l):
        ts = getts(l)
        if l["target"] == servers[l["cid"]]["nick"]:
            fromusr = l["from"]
        else:
            fromusr = l["target"]
        log(noticefmt.format(time=time.strftime("%H:%M:%S", ts),
                          nick=l["from"],
                          msg=l["msg"]),
            server=servers[l["cid"]]["name"],
            channel=fromusr,
            date=time.strftime("%Y-%m-%d", ts) )
    def p_channel_timestamp(l):
        buffers[l["bid"]]["timestamp"] = l["timestamp"]
    def p_channel_url(l):
        """ Do nothing """
    def p_channel_topic(l):
        ts = getts(l)
        topicdata = {'text': l["topic"],
                     'time': l["topic_time"],
                     'nick': l["author"],
                     'ident_prefix': l["ident_prefix"],
                     'user': l["from_name"],
                     'userhost': l["from_host"],
                     'usermask': l["hostmask"]}
        buffers[l["bid"]]["topic"].update(topicdata)
        log(topicfmt.format(time=time.strftime("%H:%M:%S", ts),
                            nick=l["author"],
                            chan=l["chan"],
                            topic=l["topic"]),
             server=servers[l["cid"]]["name"],
             channel=l["chan"],
             date=time.strftime("%Y-%m-%d", ts) )
    def p_channel_topic_is(l):
        """ Do nothing """
    def p_channel_mode(l):
        ts = getts(l)
        """ TODO """
    def p_channel_mode_is(l):
        p_channel_mode(l)
    def p_user_channel_mode(l):
        ts = getts(l)
        """ TODO """
    def p_member_updates(l):
        """ Do nothing """
    def p_who_response(l):
        """ Do nothing """
    def p_self_details(l):
        data = {'server': l["server"],
                'ircserver': l["ircserver"],
                'away': l["away"],
                'ident_prefix': l["ident_prefix"]}
        servers[l["cid"]].update(data)
    def p_user_away(l):
        """ TODO """
    def p_away(l):
        """ TODO """
    def p_self_away(l):
        servers[l["cid"]]["away"] = l["away_msg"]
    def p_self_back(l):
        servers[l["cid"]]["away"] = False
    def p_joined_channel(l):
        ts = getts(l)
        log(chjoinfmt.format(time=time.strftime("%H:%M:%S", ts),
                          nick=l["nick"],
                          usermask=l["from_mask"],
                          chan=l["chan"]),
            server=servers[l["cid"]]["name"],
            channel=l["chan"],
            date=time.strftime("%Y-%m-%d", ts) )
    def p_you_joined_channel(l):
        p_joined_channel(l)
    def p_parted_channel(l):
        ts = getts(l)
        log(chpartfmt.format(time=time.strftime("%H:%M:%S", ts),
                          nick=l["nick"],
                          usermask=l["from_mask"],
                          chan=l["chan"],
                          msg=l["msg"]),
            server=servers[l["cid"]]["name"],
            channel=l["chan"],
            date=time.strftime("%Y-%m-%d", ts) )
    def p_you_parted_channel(l):
        p_parted_channel(l)
    def p_kicked_channel(l):
        ts = getts(l)
        log(chkickfmt.format(time=time.strftime("%H:%M:%S", ts),
                          nick=l["nick"],
                          chan=l["chan"],
                          kicker=l["kicker"],
                          msg=l["msg"]),
            server=servers[l["cid"]]["name"],
            channel=l["chan"],
            date=time.strftime("%Y-%m-%d", ts) )
    def p_you_kicked_channel(l):
        p_kicked_channel(l)
    def p_quit(l):
        ts = getts(l)
        log(chkickfmt.format(time=time.strftime("%H:%M:%S", ts),
                          nick=l["nick"],
                          usermask=l["from_mask"],
                          msg=l["msg"]),
            server=servers[l["cid"]]["name"],
            channel=buffers[l["bid"]]["name"],
            date=time.strftime("%Y-%m-%d", ts) )
    def p_quit_server(l):
        """ TODO """
    def p_nickchange(l):
        ts = getts(l)
        log(chnickfmt.format(time=time.strftime("%H:%M:%S", ts),
                          old_nick=l["old_nick"],
                          new_nick=l["new_nick"]),
            server=servers[l["cid"]]["name"],
            channel=buffers[l["bid"]]["name"],
            date=time.strftime("%Y-%m-%d", ts) )
    def p_you_nickchange(l):
        p_nickchange(l)
    def p_rename_conversation(l):
        buffers[l["bid"]]["name"] = l["new_name"]
    def p_delete_buffer(l):
        ts = float(str(l["min_eid"])[:-6] + "." + str(l["min_eid"])[-6:])
        log("*** Buffer closed at " + time.ctime(ts),
            server=servers[l["cid"]]["name"],
            channel=l["name"],
            date=time.strftime("%Y-%m-%d", time.gmtime(ts)) )
    def p_buffer_archived(l):
        ts = float(str(l["min_eid"])[:-6] + "." + str(l["min_eid"])[-6:])
        log("*** Buffer archived at " + time.ctime(ts),
            server=servers[l["cid"]]["name"],
            channel=l["name"],
            date=time.strftime("%Y-%m-%d", time.gmtime(ts)) )
    def p_buffer_unarchived(l):
        ts = float(str(l["min_eid"])[:-6] + "." + str(l["min_eid"])[-6:])
        log("*** Buffer unarchived at " + time.ctime(ts),
            server=servers[l["cid"]]["name"],
            channel=l["name"],
            date=time.strftime("%Y-%m-%d", time.gmtime(ts)) )
    def p_server_details_changed(l):
        p_makeserver(l)
    def p_whois_response(l):
        """ TODO """
    def p_set_ignores(l):
        servers[l["cid"]]["ignores"].extend(l["masks"])
    def p_link_channel(l):
        """ TODO """
    def p_isupport_params(l):
        """ TODO """
    def p_myinfo(l):
        """ TODO """
    try:
        locals()["p_"+line["type"]](line)
    except KeyError:
        """ """


class AlreadyLoggedError(Exception):
    pass


def log(msg, server="IRCCloud", channel="#feedback",
        date="2013-10-31", ts="00:00:00"):
    def make_sure_path_exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    try:
        make_sure_path_exists("logs" + os.sep + server)
        filename = base64.urlsafe_b64encode(channel + "_" + date)
        with open("logs" + os.sep + server + 
                  os.sep + filename + ".log", "a+") as f:
            f.write(uni2str(msg))
        print "(S)", date, server+":"+channel, msg
    except OSError as exception:
        print "--- ERROR ---"
        print "Unable to log %s %s:%s %s" % (date, server, channel, msg)
        print "because: " + os.strerror(exception.errno)


if __name__ == "__main__":
    with open("rawlog.json", "w") as f:
        print time.ctime() + " log started"
    if len(sys.argv) > 2 and "@" in sys.argv[1] and tmpcookie != "PUT COOKIE HERE":
        isauthed = auth(sys.argv[1], " ".join(sys.argv[2:]))
        if isauthed:
            tmpcookie = isauthed
        else:
            print "Unable to authenticate with email " + sys.argv[1]
            sys.exit(1)
    elif tmpcookie == "PUT COOKIE HERE" and len(sys.argv) == 2 and not "@" in sys.argv[1]:
        tmpcookie = sys.argv[1]
    elif tmpcookie == "PUT COOKIE HERE":
        print "Usage: logger.py <cookie> | logger.py <email> <password>"
        print "Or, edit logger.py and put the cookie " \
              "in 'tmpcookie' at the top of the file"
        sys.exit(1)
    for line in streamiter(tmpcookie):
        parseline(line)