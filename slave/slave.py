import os
import time
import random
import json
from flask import Flask, redirect, url_for, request, render_template,  jsonify
import requests
from bson.json_util import dumps
from pymongo import MongoClient
import threading


def test():
    return
task_name = ""
task_status = ""
slavename = "worker" + str(random.randint(0, 100000))
timer = threading.Timer(0, test)
app = Flask(__name__)


@app.route('/')
def home():
    return slavename


@app.route('/status')
def stat():
    global task_name
    global task_status
    returnJson = json.dumps({"taskname":task_name,"status":task_status,"host":slavename})
    return returnJson

#called by master to start task
@app.route('/start_task')
def start_task():
    global task_status 
    global task_name
    global timer
    #if worker busy tell master
    if task_status == "running" and timer.is_alive():
        ret = status(task_name, task_status)
        print("Worker running")
        return ret

    #if finished or free accept work
    json_string = request.data.decode("utf-8")
    json_dict = json.loads(json_string)
    taskname = json_dict['taskname']
    sleeptime = json_dict['sleeptime']
    print("Worker started")
    work(sleeptime,taskname)
    
    prevTask = task_name
    prevStatus = task_status
    task_name = taskname
    task_status = "running"

    ret = status(prevTask, prevStatus)
    print(ret)
    return ret


def work(worktime, taskname):
    global timer
    timer = threading.Timer(float(worktime), finish_task)
    timer.setName(taskname)
    timer.start();

#called when timer ends
@app.route('/finish')
def finish_task():
    global task_status 
    task_status = "finished"
    ret = stat()
    try:
        res = requests.get('http://master:8001/finish_task', data= ret)
    except:
        print("master unreached")
        count = 2
        while count > 0:
            time.sleep(1)
            count -= 1
        finish_task()
        return
    if(res.text) == "task_complete":
        return '0'
    else:
        print("master failed to update")
        count = 2
        while count > 0:
            time.sleep(1)
            count -= 1
        finish_task()
        return


def status(task_name,task_stat):
    returnJson = json.dumps({ "taskname":task_name,"status":task_stat,"host":slavename})
    return returnJson
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8002)

