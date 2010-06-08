#!/usr/bin/env python
# Copyright (c) 2010, Westly Ward
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the wwBB Team nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY Westly Ward ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Westly Ward BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#import cgitb
#cgitb.enable()
import cgi, time, shelve, Cookie, hashlib, htmlhelper, os, cgitb, bbcode, urllib
cgitb.enable()
helper = htmlhelper.htmlhelper()
helper.setFooter('<div class="footer"><a href="http://validator.w3.org/check?%s">Valid XHTML 1.0</a> | <a href="http://github.com/sonicrules1234/wwBB/">Available</a> under the BSD license.</div>' % (helper.html_escape(urllib.urlencode({"uri":"http://"+os.environ["HTTP_HOST"]+os.environ["REQUEST_URI"]}))))

dbpath = ""
form = cgi.FieldStorage()
forumname = ""
logourl = "img/logo.png"
def cookiecheck() :
    if 'HTTP_COOKIE' in os.environ :
        c = os.environ['HTTP_COOKIE']
        c = c.split('; ')
        handler = {}
        for cookie in c :
            cookie = cookie.split("=")
            handler[cookie[0]] = cookie[1]
        return handler
    else : return {}
handler = cookiecheck()
db = shelve.open(dbpath, writeback=True)
if not db.has_key("categories") :
    db["categories"] = {"Main":{"Last Post":0, "Threads":[0]}}
    db.sync()
if not db.has_key("threads") :
    db["threads"] = [{"title":"Welcome to wwBB!", "starter":0, "time":time.time(), "posts":[{"poster":0, "body":"Welcome to wwBB!", "time":time.time()}]}]
    db.sync()
if not db.has_key("users") :
    db["users"] = [{"name":"wwBB", "website":"", "IRC":"", "IM":"", "pid":0, "registered":time.time()}]
    db.sync()
if not db.has_key("user2pid") :
    db["user2pid"] = {"wwBB":0}
    db.sync()
def listthreads(category) :
    print "Content-Type: text/html\n"
    times = []
    htmldata = "<table><tr><td>Thread</td><td>Poster</td><td>Time</td></tr>\n"
    for thread in db["categories"][category]["Threads"] :
        htmldata += '<tr><td>%(link)s</td><td>%(poster)s</td><td><span id="a%(time)s"></span></td></tr>\n' % {"link":helper.a("index.py?action=read&amp;tid="+str(thread), db["threads"][thread]["title"]), "poster":db["users"][db["threads"][thread]["posts"][-1]["poster"]]["name"], "time":str(int(db["threads"][thread]["posts"][-1]["time"]))}
        times.append(int(db["threads"][thread]["posts"][-1]["time"]))
    htmldata += "</table>"
    htmldata += generateJS(times)
    if auth() : htmldata += helper.a("index.py?action=newthreadform", "Create a new thread")
    print helper.html(helper.head('<link href="style.css" rel="stylesheet" type="text/css" />'+helper.title(bbcode.render_bbcode(category)))+helper.body(header()+htmldata))
def auth() :
    if handler["wwBBv2-status"] == "in" :
        username = db["users"][int(handler["pid"])]["name"]
        cookiepassword = handler["password"]
        password = db["users"][int(handler["pid"])]["password"]
        if hashlib.sha512(cookiepassword).hexdigest() == password :
            inornot = True
        else : inornot = False
    else : inornot = False
    return inornot
def header() :
    if handler["wwBBv2-status"] == "in" :
        username = db["users"][int(handler["pid"])]["name"]
        cookiepassword = handler["password"]
        password = db["users"][int(handler["pid"])]["password"]
        if hashlib.sha512(cookiepassword).hexdigest() == password :
            inornot = True
        else : inornot = False
    else : inornot = False
    if inornot :
        return '<div class="header"><img src="%(logo)s" alt="Logo"/><br /><p>Welcome to %(name)s, %(user)s | <a href="index.py?action=logout">Logout</a></p></div>' % dict(logo=logourl, user=username, name=forumname)
    else : return '<div class="header"><img src="%(logo)s" alt="Logo" /><br /><form action="index.py" method="post">Username: <input type="text" name="username" /> Password: <input type="password" name="password" /> <input type="hidden" name="action" value="login" />\n<input type="submit" value="Login" /> | <a href="index.py?action=registerform">Register</a></form></div>' % dict(logo=logourl, name=forumname)
def printThread(tid, form, handler) :
    print "Content-type: text/html\n"
    postdata = createPostData(tid)
    print helper.html(helper.head('<link href="style.css" rel="stylesheet" type="text/css" />'+helper.title(bbcode.render_bbcode(db["threads"][tid]["title"])))+helper.body(header()+postdata+'<br /><a href="index.py">Back</a>'))
def generateJS(times) :
    output = """<script type="text/javascript">
<!--//
/* <![CDATA[*/
var mmToMonth = new Array("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec");
function pad2(number) {
   
     return (number < 10 ? '0' : '') + number
   
}
function showLocalDate(timestamp){
var dt = new Date(timestamp * 1000);
var mm = mmToMonth[dt.getMonth()];
return dt.getDate() + "-" + mm + "-"+dt.getFullYear()+" "+dt.getHours()+":" +pad2(dt.getMinutes());
}
//-->
"""
    for x in times :
        output += 'document.getElementById("a%(time)d").innerHTML = showLocalDate(%(time)d);\n' % {"time":int(x)}
    output += "</script>"
    return output
def createPostData(tid) :
    postdata = ""
    times = []
    for post in db["threads"][tid]["posts"] :
        postdata += helper.p("""<div class="box">
<div class="infobox">
<span class="insideinfoboxleft">
<span class="innerleftinfo">%(username)s</span>
</span>
<span class="insideinfoboxright">
<span class="innerrightinfo"><span id="a%(time)s"></span></span>
</span>
</div>
<div class="postbox">
%(body)s
</div>
</div>
""" % {"time":str(int(post["time"])), "body":bbcode.render_bbcode(post["body"]), "username":db["users"][post["poster"]]["name"]}) + "\n"
        times.append(post["time"])
    postdata += generateJS(times)
    if auth() : postdata += '<form action="index.py" method="post">\n<textarea rows="10" cols="60" name="postdata"></textarea>\n<br />\n<input type="hidden" name="postid" value="%(postid)d" />\n\n<input type="hidden" name="action" value="reply" />\n<input type="submit" value="Post Reply" /></form>' % {"postid":tid}
    return postdata
def trytoregister(username, password) :
    valid = True
    for user in db["users"] :
        if username.lower() == user["name"] :
            valid = False
            break
    if valid :
        register(username, password)
    else :
        invalidregister()
def invalidregister() :
    print "Content-type: text/html\n"
    print helper.html(helper.head(helper.title("Username Taken"))+helper.body(helper.p("Sorry, that username is already taken.  Please try "+helper.a("index.py?action=registerform", "again"))))
def register(username, password) :
    uid = len(db["user2pid"].keys())
    db["user2pid"][username] = uid
    db.sync()
    db["users"].append({"registered":time.time(), "name":username, "website":"", "IRC":"", "IM":"", "pid":uid, "password":hashlib.sha512(hashlib.sha512(password).hexdigest()).hexdigest(), "userlevel":1})
    db.sync()
    a = Cookie.SimpleCookie()
    a['wwBBv2-status'] = "in"
    a["pid"] = uid
    a["password"] = hashlib.sha512(password).hexdigest()
    print a
    print "Location: index.py\n"
def login(handler, form) :
    username = form["username"].value
    pid = int(db["user2pid"][username])
    password = db["users"][pid]["password"]
    if hashlib.sha512(hashlib.sha512(form["password"].value).hexdigest()).hexdigest() == password :
        g = Cookie.SimpleCookie()
        g["wwBBv2-status"] = "in"
        g["password"] = hashlib.sha512(form["password"].value).hexdigest()
        g["pid"] = str(pid)
        print g
        print "Location: index.py\n"
    else :
        print "Content-type: text/html\n"
        print loginfailed()
def loginfailed() :
    return helper.html(helper.head(helper.title("Login Failed"))+helper.body(helper.p('Login failed.  This could be do to an invald username and/or password.  Please <a href="index.py">Try again</a>')))
def printRegisterForm() :
    print "Content-type: text/html\n"
    print helper.html(helper.head('<link href="style.css" rel="stylesheet" type="text/css" />'+helper.title("Registration Form"))+helper.body('<div class="header"><img src="%(logo)s" /><br /></div><form action="index.py" method="post">\nUsername: <input type="text" name="username" />\n<br />\nPassword: <input type="password" name="password" /><br />\n<input type="hidden" name="action" value="register" />\n<input type="submit" value="Submit" /></form>' % dict(logo=logourl)))
def postreply(postid, postdata) :
    if auth() :
        db["threads"][postid]["posts"].append({"poster":int(handler["pid"]), "body":postdata, "time":time.time()})
        db.sync()
        print "Location: index.py?action=read&tid=%d\n" % (postid)
def printThreadForm() :
    print "Content-type: text/html\n"
    print helper.html(helper.head('<link href="style.css" rel="stylesheet" type="text/css" />'+helper.title("Create a Thread"))+helper.body(header()+helper.p('<form action="index.py" method="post">\nThread Title: <input type="text" name="title" /><br /><textarea rows="10" cols="60" name="firstpost"></textarea>\n<br />\n<input type="hidden" name="action" value="newthread" />\n<input type="submit" value="Create Thread" /></form>')))
def newthread(title, firstpost, category="Main") :
    if auth() :
        tid = len(db["threads"])
        db["categories"][category]["Threads"].append(tid)
        db.sync()
        db["threads"].append({"starter":int(handler["pid"]), "time":time.time(), "title":title, "posts":[{"poster":int(handler["pid"]), "body":firstpost, "time":time.time()}]})
        db.sync()
        print "Location: index.py?action=read&tid=%d\n" % (tid)
if handler == None or handler == {} :
    c = Cookie.SimpleCookie()
    c['wwBBv2-status'] = "out"
    print c
    handler["wwBBv2-status"] = "out"
    listthreads("Main")
elif "wwBBv2-status" in handler :
    if form.has_key("action") :
        if form["action"].value == "postform":
                printpostform(form)
        elif form["action"].value == "userlist" :
            printuserlist()
        elif form["action"].value == "login" :
            if form.has_key("username") and form.has_key("password") :
                login(handler, form)
        elif form["action"].value == "read" :
            if form.has_key("tid") :
                thid = form["tid"].value
                if int(thid) < len(db["threads"]) :
                    printThread(int(thid), form, handler)
        elif form["action"].value == "registerform" :
            printRegisterForm()
        elif form["action"].value == "register" :
            if form.has_key("username") and form.has_key("password") :
                trytoregister(form["username"].value, form["password"].value)
        elif form["action"].value == "logout" :
            c = Cookie.SimpleCookie()
            c["wwBBv2-status"] = "out"
            print c
            print "Location: index.py\n"
        elif form["action"].value == "reply" :
            if form.has_key("postid") and form.has_key("postdata") :
                postreply(int(form["postid"].value), form["postdata"].value)
        elif form["action"].value == "newthread" :
            if form.has_key("title") and form.has_key("firstpost") :
                newthread(form["title"].value, form["firstpost"].value)
        elif form["action"].value == "newthreadform" :
            printThreadForm()
    elif handler["wwBBv2-status"] == "out" : listthreads("Main")
    elif handler["wwBBv2-status"] == "in" :
        listthreads("Main")
