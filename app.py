import os
import time
import random
import redis
from flask import Flask, redirect, url_for, request, render_template

from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient(
        "db", 
        27017)

db = client.taskdb



@app.route('/')
def index():
    for i in range (15):
        db.taskdb.insert([{"taskname":"task" + str(int(random.random() * 6200000)), "sleeptime": random.random() * 20, "state": "created"}])
    _items = db.taskdb.find()
    items = [item for item in _items]

    return render_template('database.html', items=items)



@app.route('/show_db')
def showDB():
    _items = db.taskdb.find()
    items = [item for item in _items]

    return render_template('database.html', items=items)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port= 8000)

