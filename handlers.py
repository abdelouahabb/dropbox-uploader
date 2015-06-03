#coding: utf-8
import tornado.web, tornado.gen
from tornado.httputil import HTTPHeaders
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import datetime
import pytz
import motor
import os
from pymongo.errors import DuplicateKeyError
from hashlib import md5


db = motor.MotorClient(os.environ["URI"]).exam #replace this with motor.MotorClient().exam if you want to use it in local
http_client = AsyncHTTPClient()


class RootHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        nbr = yield db.etudiant.find().count()
        self.render("index.html", nbr=nbr)


class Upload(RootHandler):
    @tornado.gen.coroutine
    def post(self):
        nom = self.get_arguments("nom")
        prenom = self.get_arguments("prenom")
        size = self.get_argument("size")
        if int(size) <= 10485760:
            if ( False in [len(i)>2 for i in nom] ) or ( False in [len(i)>2 for i in prenom] ) :
                self.write("Za3ma tu essaies de passer le controle? ")
            else:
                etudiants = []
                for i in xrange(len(nom)):
                    etudiants.append((nom[i], prenom[i]))
                etudiants = [' '.join(w) for w in etudiants]
                nom = md5(reduce(lambda x, y: x + y, etudiants, "")).hexdigest()
                proj = self.request.files['proj'][0]
                content = proj["body"]
                ctype = proj["content_type"]
                if (ctype == "application/octet-stream"):
                    try:
                        url = "https://api-content.dropbox.com/1/files_put/sandbox/{0}.zip".format(nom)
                        headers = HTTPHeaders({'Authorization': 'Bearer {0}'.format(os.environ["TOKEN"]), 'Content-Type':ctype}) # get your token from dropbox console
                        yield http_client.fetch(HTTPRequest(url, 'PUT', body=content, headers=headers))
                        yield db.etudiant.insert({"_id":nom,
                                            "time":datetime.datetime.now(pytz.timezone("Africa/Algiers")),
                                            "stu": etudiants})
                        self.redirect('/thanks')
                    except DuplicateKeyError:
                        self.write("<h1>Vous avez deja uploade votre projet!</h1>")    
                        self.finish()
                else:
                    self.write("<h1>UNIQUEMENT LES FICHIERS COMPRESSES!</h1>")
                    self.finish()
        else:
            self.write("<h1>10 Mega max!</h1>")
            
class Thanks(RootHandler):
    @tornado.gen.coroutine
    def get(self):
        self.write("<h1>Merci ^_^</h1>")