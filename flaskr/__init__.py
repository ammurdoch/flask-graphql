import os
import json

from flask import Flask, g, request, Response
from . import db
from .ql import schema

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
  )

  if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
  else:
    # load the test config if passed in
    app.config.from_mapping(test_config)

  # ensure the instance folder exists
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  @app.route('/query', methods=['POST', 'GET'])
  def query():
    # return json.dumps(g.db.execute('SELECT * FROM user').fetchall())
    if request.method == 'POST':
      request_json = request.get_json()
      if (request_json):
        result = schema.execute(request.get_json()['query'])
        return json.dumps(result.data)
      return Response(json.dumps({
        "message": "Bad Request",
      }), status=400, mimetype='application/json')
    
    query = '''
        query SayHello {
          hello
        }
    '''
    result = schema.execute(query)
    return json.dumps(result.data)

  # a simple page that says hello
  @app.route('/hello')
  def hello():
    return 'Hello, World!'
  
  @app.before_request
  def before_get_db():
    db.get_db()
  
  @app.after_request
  def after_close_db(r):
    db.close_db()
    return r

  db.init_app(app)

  return app
