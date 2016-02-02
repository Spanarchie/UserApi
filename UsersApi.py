#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from py2neo import Graph

app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()
gbd = Graph("http://CivicBase:NhrBKsP5ULtZopafC7a9@civicbase.sb04.stations.graphenedb.com:24789/db/data/")

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

users = [
     {
            'id': 0,
            'name': 'User Ben Sparrow',
            'lastText': 'You on your way?',
            'face': 'img/ben.png'
          }, {
            'id': 1,
            'name': 'User Max Lynx',
            'lastText': 'Hey, it\'s me',
            'face': 'img/max.png'
          }, {
            'id': 2,
            'name': 'User Adam Bradleyson',
            'lastText': 'I should buy a boat',
            'face': 'img/adam.jpg'
          }, {
            'id': 3,
            'name': 'User Perry Governor',
            'lastText': 'Look at my mukluks!',
            'face': 'img/perry.png'
          }, {
            'id': 4,
            'name': 'User Mike Harrington',
            'lastText': 'This is wicked good ice cream.',
            'face': 'img/mike.png'
          }
]

task_fields = {
    'id': fields.String,
    'name': fields.String,
    'lastText': fields.String,
    'face': fields.String
}


class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True,
                                   help='No USER name provided',
                                   location='json')
        self.reqparse.add_argument('desc', type=str, default="",
                                   location='json')
        self.reqparse.add_argument('img', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        qry = "Match (u:SKILL) return u.name AS name"
        for record in gbd.cypher.execute(qry):
            print(record.name)
        return {'users': [marshal(task, task_fields) for task in users]}

    def post(self):
        args = self.reqparse.parse_args()
        qry = "MERGE (u:USERXXX {"
        for x in args:
            qry = qry+x+" : "
            qry = qry+" '"+args[x]+"',"
            print (qry)
        task = {
            'id': users[-1]['id'] + 1,
            'name': args['name'],
            'lastText': args['desc'],
            'face': args['img']
        }
        print(qry[:-1]+"})")
        qry=qry[:-1]+"})"
        gbd.cypher.execute(qry)
        qry = "Match (u:SKILL) return u.name AS name"
        for record in gbd.cypher.execute(qry):
            print(record.name)
        users.append(task)
        return {'task': marshal(task, task_fields)}, 201


class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('desc', type=str, location='json')
        self.reqparse.add_argument('img', type=str, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = [task for task in users if task['id'] == id]
        if len(task) == 0:
            abort(404)
        qry = "Match (u:USER) return u.name AS name"
        for record in gbd.cypher.execute(qry):
            print(record)
        return {'task': marshal(task[0], task_fields)}

    def put(self, id):
        task = [task for task in users if task['id'] == id]
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                task[k] = v
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task = [task for task in users if task['id'] == id]
        if len(task) == 0:
            abort(404)
        users.remove(task[0])
        return {'result': True}


api.add_resource(TaskListAPI, '/todo/api/v1.0/users', endpoint='users')
api.add_resource(TaskAPI, '/todo/api/v1.0/users/<int:id>', endpoint='task')


if __name__ == '__main__':
    app.run(port=5001, debug = True)