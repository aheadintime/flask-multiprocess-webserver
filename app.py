from flask import Flask

from multiprocessing import Process, Queue

import subprocess

import re 
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import base64
import os

plt.style.use('_mpl-gallery')
matplotlib.use('agg')

ms_lists = []


def standard_handler(i, q):
    return "<p/>".join(dump_queue(q))

def regex_handler(i, q):
    items = dump_queue(q)

    for item in items:
        x = re.search("(.*?) (.*?): (.*?)=(.*?) (.*?)=(.*?)ms (.*?)=(.*?)\n", item + "\n")
        if(x == None):
            continue
        
        ms = int(x.group(6))

        while len(ms_lists) < i + 1:
            ms_lists.append([])

        ms_lists[i].append(ms)

    return plot_to_image_base64(ms_lists[i]) + "<p>" + "<p/>".join(items)



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
     ['ping','-t', '8.8.8.8'], #COMMAND
     regex_handler #HANDLE DATA TO SHOW IN HTML
     ], 

    ["ping 8.8.4.4", 
     ['ping','-t', '8.8.4.4'],
     regex_handler
     ],
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
    
    
    return "<p>" + commands[i][2](i, q) + "</p>"


def with_title(title, body):
    return "<h2>" + title + "</h2>" + body

def dump_queue(q):
    items = []
    while(not q.empty()):
        items.append(q.get(block=False))
    return items

def plot_to_image_base64(data):
    fig, ax = plt.subplots()

    ax.stairs(data, linewidth=2.5)

    ax.set(xlim=(0, len(data)), xticks=[],
       ylim=(0, max(data) * 2), yticks=[])

    plt.savefig('temp.png')

    plt.close()

    graph_png = ""

    with open("temp.png", "rb") as image_file:
        graph_png = base64.b64encode(image_file.read()).decode('utf-8')

    os.remove("temp.png") 

    return "<img src=\"data:image/png;base64," + graph_png + "\"/>"