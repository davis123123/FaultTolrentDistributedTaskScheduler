import os
import time
import random
import json
from flask import Flask, redirect, url_for, request, render_template, jsonify
from bson.json_util import dumps
from pymongo import MongoClient
import requests
import threading 

app = Flask(__name__)

client = MongoClient(
        "db", 
        27017)

db = client.taskdb

slaveList = []

@app.route('/')
def home():
    return "Hello"


#test 
@app.route('/test')
def test():
	res = requests.get('http://slave:8002/test')
	return res.text

#start master routine
@app.route('/init')
def init():
	#check for all running tasks
	get_running_task()
	monitor()
	return 'All tasks Completed'

#monitor workers until all tasks complete
@app.route('/monitor')
def monitor():
	tasks_compeleted = False
	while(not tasks_compeleted):
		tasks_compeleted = start_task()
		count = 2
		while count > 0:
			time.sleep(1)
			count -= 1
	return

#start send out tasks to workers
@app.route('/start_task')
def start_task():
	#fetch task
	try:
		task = db.taskdb.find_one({"state":{"$in":["created","killed"]}})
		if not task:
			running_task = db.taskdb.find_one({"state":{"$in":["running"]}})
			if not running_task:
				print("No more tasks")
				return True
			else:
				return False
		list_db = list(task)
		json_string = dumps(task)
		json_dict = json.loads(json_string)
		
		taskname = json_dict["taskname"]
		if not list_db or not json_string:
			return "None"
	except(e):
		print(e)

	print(json_string + " Master Task " + taskname)
	taskAccepted = False
	#keep sending same task until a worker accepts
	while not taskAccepted:
		try:
			#keep send task until master can find a worker that is free	
			res = requests.get('http://slave:8002/start_task', data= json_string)
			print("Distributing task: " + res.text)
			res_string = json.loads(res.text)

			task_name = res_string['taskname']
			task_status = res_string['status']
			host = res_string['host']
			#if worker busy try different worker
			if task_status == "running":
				print(host + " already running task: "+task_name)
				count = 1
				while count > 0:
					time.sleep(1)
					count -= 1
				continue

			#worker has accepted task
			taskAccepted = True
			print("updating db to running")
			x = db.taskdb.update_one({"taskname":taskname},{"$set":{"state":"running","host":host}});
			print("task successfully started")
			startTimer(taskname)
		except:
			print("worker down")
		
		count = 2
		while count > 0:
			time.sleep(1)
			count -= 1
		
	return False

#get all running task in db
@app.route('/get_running_task')
def get_running_task():
	#get all running task
	for task in db.taskdb.find({"state":{"$in":["running"]}}):
		list_db = list(task)
		json_string = dumps(task)
		json_dict = json.loads(json_string)
		
		if not list_db or not json_string:
			return "None"
		print( " running task found: " + json_string)

		taskname = json_dict['taskname']
		sleeptime = json_dict['sleeptime']
		state = json_dict['state']
		#restart timer for running tasks
		startTimer(taskname)
	return '0'
	
#start timer
def startTimer(taskname):
	#add heartbeat timer
	timer = threading.Timer(30.0, kill_task, [taskname])
	timer.setName(taskname) 
	slaveList.append(timer.native_id)
	timer.start()
	return

#end timer
def endTimer(taskname):
	for thread in threading.enumerate():
			#print(taskname + "  " + thread.getName())
			if thread.name == taskname:
				print(taskname + "  task completed and timer ended")
				thread.cancel()
	return

#update db of completed task, called by worker
@app.route('/finish_task')
def finish_task():
	#end timer
	print("master finishing task")
	json_string = request.data.decode("utf-8")
	json_dict = json.loads(json_string)
	taskname = json_dict['taskname']
	host = json_dict['host']
	endTimer(taskname)
	
	#update db
	s = db.taskdb.update_one({"taskname":taskname},{"$set":{"state":"success","host":host}});
	print(s)
	print("completed task updated: " + taskname)

	return "task_complete"

#timer ran out and no signel from worker
def kill_task(taskname):
	state = ""
	try:
		task = db.taskdb.find_one(taskname)
		json_string = dumps(task)
		json_dict = json.loads(json_string)
		state = json_dict['state']
	except:
		print("task not found")
	#if not completed task
	if state != "success":
		x = db.taskdb.update_one({"taskname":taskname},{"$set":{"state":"killed"}});
		print(taskname + "  Task killed")
	return

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 8001)

