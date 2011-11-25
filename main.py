from __future__ import with_statement
import os
import logging
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from cartodb import cartodb
from config.credentials import CONSUMER_KEY, CONSUMER_SECRET, USER, PASSWORD, DOMAIN

CARTODB = cartodb.CartoDB(CONSUMER_KEY, CONSUMER_SECRET, USER, PASSWORD, DOMAIN)

class WritePoint(webapp.RequestHandler):
    def get(self):
        latitude = float(self.request.get('latitude'))
        longitude = float(self.request.get('longitude'))
        if abs(latitude) < 90 and abs(longitude) < 180: 
            sql = "INSERT INTO write_points (latitude, longitude, the_geom) VALUES (%s, %s, GEOMETRYFROMTEXT('POINT(%s %s)',4326));" % (latitude, longitude, longitude, latitude)
            res = CARTODB.sql(sql)
            #self.response.out.write( 'success' )
            self.response.http_status_message(200)
        else:
            self.error(500)
        
application = webapp.WSGIApplication(
                                     [('/cartodb/write/point', WritePoint)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
