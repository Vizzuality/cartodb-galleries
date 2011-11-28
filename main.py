from __future__ import with_statement
import os
import logging
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
from cartodb import cartodb
from config.credentials import CONSUMER_KEY, CONSUMER_SECRET, USER, PASSWORD, DOMAIN

CARTODB = cartodb.CartoDB(CONSUMER_KEY, CONSUMER_SECRET, USER, PASSWORD, DOMAIN)
   
class BaseHandler(webapp.RequestHandler):  
  
  def xhr_response(self):
    self.response.headers.add_header("Access-Control-Allow-Origin", "*")

  def xhr_content(self, content, content_type):
    self.response.headers["Access-Control-Allow-Origin"] = "*"
    self.xhr_response()
    self.response.out.write(content)
    self.response.headers.add_header("Cache-Control", "no-cache")
    self.response.headers.add_header("Content-Type", content_type)
    self.response.headers.add_header("Expires", "Fri, 01 Jan 1990 00:00:00 GMT")

  def bcapRequest(self):
    return dataPostProcess(self.request.body)
      
  def bcapResponse(self, jsonResp):
    resp = dataPreProcess(jsonResp)
    self.xhr_content(resp, "text/plain;charset=UTF-8")

  def bcapNullResponse(self):
    self.xhr_response()
    
  # allows cross-domain requests  
  def options(self):
    m = self.request.headers["Access-Control-Request-Method"]
    h = self.request.headers["Access-Control-Request-Headers"]

    self.response.headers["Access-Control-Allow-Origin"] = "*"
    self.response.headers["Access-Control-Max-Age"] = "2592000"
    self.response.headers["Access-Control-Allow-Methods"] = m      
    if h:
      self.response.headers["Access-Control-Allow-Headers"] = h
    else:
      pass

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
        
class WritePolygon(BaseHandler):
    def get(self):
        self.post()
    def post(self):
        poly = self.request.get('polygon').split(',')
        geojson = json.loads(self.request.get('geojson'))
        cartodb_id = self.request.get('cartodb_id',False)
        poly = geojson['coordinates'][0][0]
        try:
            #close the loop
            poly.append(poly[0])
            #check to enforce that all numeric values were supplied
            poly = ["%f %f" % (float(i[0]), float(i[1])) for i in poly]
            if cartodb_id is False:
                sql = "INSERT INTO write_polygons (the_geom) VALUES (GEOMETRYFROMTEXT('MULTIPOLYGON(((%s)))',4326))" % ','.join(poly)
            else:
                sql = "UPDATE write_polygons SET the_geom = GEOMETRYFROMTEXT('MULTIPOLYGON(((%s)))',4326) WHERE cartodb_id = %s" % (','.join(poly),cartodb_id)
            
            CARTODB.sql(sql)
            self.response.http_status_message(200)
        except:
            self.error(500)
        
application = webapp.WSGIApplication(
                                     [('/cartodb/write/point', WritePoint),
                                      ('/cartodb/write/polygon', WritePolygon)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
