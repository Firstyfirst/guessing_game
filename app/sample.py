from flask import Flask, request, jsonify
from pymongo import MongoClient
import os, json, redis

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

@application.route('/')
def start():
    body = '<div style="text-align:center;">'
    db.game.insert_one({'id' : 1,
                            'question' : ["_","_","_","_"],
                            'guessing' : ["*","*","*","*"],
                            'answer' : [],
                            'score' : [],
                            'fail' : 0,
                            'step' : 0,
                            })
    body += '<h1>Guessing Game</h1>'
    body += '<a href="/index" class = "btn btn-primary" type = "button"> Start </a>'
    body += '</div>'
    return body

@application.route('/index', methods=['GET', 'POST'])
def index():
    
    games = db.game.find_one({"id":1})
    body = '<div style="text-align:center;">'
    
    body += '<h1>Game not ready</h1>'
    # Initialize the document in database
    step = games['step']
    questions = games['question']
    question = ",".join(questions)
    guessing = ",".join(games['guessing'])
    answer = ",".join(games['answer'])
    fail = games['fail']
    ans_index = len(games['answer'])
    game_step = ['First', 'Second', 'Thrid', 'Fourth']

    # Question Phase (step 0 --> 3)
    if step < 4:
        body += f"<h1>Choose A, B, C or D to add the {game_step[step]} character to the question</h1>"
        body += f"<h2>{question}</h2><br></br>"
        body += '<form action = "/q/" method = "post"> '
        body += '<input type="submit" name="questioning" value="A" />'
        body += '<input type="submit" name="questioning" value="B" /> '
        body += '<input type="submit" name="questioning" value="C" /> '
        body += '<input type="submit" name="questioning" value="D" /> '
        body += '</form>'

    # Answer Phase (step 4 --> 7)
    elif step >= 4 and step < 8:
        body += f"<h1>Choose A, B, C or D to guess the {game_step[step-4]} character</h1>"
        body += f"<h2>{answer}</h2><br></br>"
        body += f"<h2>Character(s) remaining: {guessing}</h2><br></br>"
        body += '<form action = "/a/" method = "post">'
        body += '<input type="submit" name="answering" value="A" />'
        body += '<input type="submit" name="answering" value="B" /> '
        body += '<input type="submit" name="answering" value="C" /> '
        body += '<input type="submit" name="answering" value="D" /> '
        body += '</form>'
        body += f"<h2>Fail: {fail} <h2>"

    # Game Over
    elif step >= 8:
        body += f"<h1> Game Over: You Wins!!</h1>"
        body += f"<h2>The answer is {answer}</h2>"
        body += '<a href ="/f/" class = "btn btn-primary" type = "button"> Retry </a>'
    body += '</div>'
    return body

@application.route('/q/', methods=['POST'])
def questioning():
    ques = request.form.get('questioning')
    db.game.update_one({'id' : 1}, {"$inc" : {"step" : 1}})
    db.game.update_one({'question': '_'}, {'$set': {'question.$': ques}})
    return index()

@application.route('/a/', methods=['POST'])
def answering():
    ans = request.form.get('answering')
    games = db.game.find_one({"id":1})
    questions = games['question']
    ans_index = len(games['answer'])
    if questions[ans_index] == ans:
        db.game.update_one({'id': 1}, {"$push": {"answer": ans}})
        db.game.update_one({'id': 1}, {"$inc": {"step": 1}})
        db.game.update_one({'id': 1}, {"$pop": {"guessing": 1}})
    else:
        db.game.update_one({'id': 1}, {"$inc": {"fail": 1}})
    return index()

@application.route('/f/')
def finish():
    db.game.remove({})
    return start()

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)