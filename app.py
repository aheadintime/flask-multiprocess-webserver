from flask import Flask

from multiprocessing import Process, Queue

import subprocess

def run_process_with_queue(q, a):
    proc = subprocess.Popen(a,stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if(line):
            q.put(line.decode("utf-8"))


app = Flask(__name__)

refresh_time = 5 #HTML PAGE REFRESH TIME (in seconds)

commands = [
    ["ping 8.8.8.8", #COMMAND TITLE
     ['ping','-t', '8.8.8.8']], #COMMAND

    ["ping 8.8.4.4", 
     ['ping','-t', '8.8.4.4']],

    ["ping 208.67.222.222", 
     ['ping', '-t', '208.67.222.222']]
]

helpers = [] #USED TO STORE PROCESS AND QUEUE


@app.route("/")
def hello_world():

    initialize()

    return "<html><head><meta http-equiv=\"refresh\" content=\"" + str(refresh_time) + "\" /></head><body><h1>MULTIPROCESS-WEBSERVER</h1>" + html_commands_output() + "</body></html>"

 
def initialize():
    if len(helpers) > 0:
        return
    
    for i in range(0, len(commands)):
        q = Queue()
        helpers.append([q, Process(target=run_process_with_queue, args=(q, commands[i][1]))])

def html_commands_output():
    output = ""
    for i in range(0, len(helpers)):
        output += html_item(i)
    return output
    
def html_item(i):
    return with_title(commands[i][0], html_body(i) )


def html_body(i):
    p = helpers[i][1]
    q = helpers[i][0]

    if (p.pid == None):
        p.start()
        return "<p>Starting...</p>"

    if q.empty():
        return "<p>Waiting...</p>"
    
    
    return "<p>" + "<p/>".join(dump_queue(q)) + "</p>"


def with_title(title, body):
    return "<h2>" + title + "</h2>" + body

def dump_queue(q):
    items = []
    while(not q.empty()):
        items.append(q.get(block=False))
    return items
    
