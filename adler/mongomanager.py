import ast
import urllib

import tornado.web
import tornado.ioloop
import motor

import simplejson as json


PORT = 13000

class GlmHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        """Handle post method and insert data to MongoDB."""
        # convert 'pseudo' dict in str format to real dict
        document = ast.literal_eval(json.loads(self.request.body))

        # write to 'glm' collection
        self.settings['db'].glm.insert(document, callback=self.on_response)

    # TODO this response may be just for mongo
    def on_response(self, result, error):
        """A callback called by post method above."""
        # TODO error message is still wrong. it may be not 500
        # mongoDB may be down
        if error:
            raise tornado.web.HTTPError(500, error)
        else:
            self.write({'success': 0})
            self.finish()


db = motor.motor_tornado.MotorClient().inetscada

application = tornado.web.Application([(r'/glm/create', GlmHandler)],
                                      db=db)

print "MongoManager on port " + str(PORT)

application.listen(PORT)
tornado.ioloop.IOLoop.instance().start()
