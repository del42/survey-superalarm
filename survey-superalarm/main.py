#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
from gaesessions import get_current_session
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import re
import csv
import cgi
import logging
import random
from random import sample
from google.appengine.ext import db



#create empty containers 
superAlarmPatterns = []
controlPatterns = []
trigger = []
surveyAnswers = [1000, 100, 10, 1]
surveyTotal = 50

#copy superAlarmPatterns.txt into array
with open('superAlarmPatterns.txt', 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        superAlarmPatterns.append(row)

#copy controlPatterns.txt into array
with open('controlPatterns.txt', 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        controlPatterns.append(row)

#copy trigger.txt into array
with open('trigger.csv', 'rU') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        trigger.append(row)

class surveyTaker(db.Model):
    email = db.StringProperty(required=True)
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    specialty = db.StringProperty()
    expeirence = db.StringProperty()

class survey(db.Model):
    email = db.IntegerProperty(required=True)
    answer = db.IntegerProperty()
    choiceForA = db.ListProperty(long)
    choiceForB = db.ListProperty(long)
    completed = db.BooleanProperty()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        #check wether session is new
        if len(session['userEmail'])>0:
            self.redirect('/survey')
        else:
            email = self.request.get("user")
            session['userEmail'] = email
        logging.info("email  = "+ str(session['userEmail']))
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, session))




class sendSurveyHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {
                'name': self.request.get('user'),
                'specialty': self.request.get('user'),
                }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        #self.redirect('/')



class surveyHandler(webapp2.RequestHandler):
    def post(self):
        name = self.request.get("specialty")
        specialty = self.request.get("experience")
     
        #email = self.request.get("user")
     
        choiceA=forChoiceA()
        choiceB=forChoiceB(len(choiceA))
        session = get_current_session()
        email = cgi.escape(session.get('userEmail', ''), quote = "true")
        logging.info("email is " + email)
        session['userEmail'] = email
        session['name'] = email
        session['specialty'] = specialty
        session['sap'] = choiceA[1:]
        session['cp'] = choiceB[1:]
        session['result'] = "(The highlighted pattern/Both highlighted patterns/Neither patterns) is the/are SuperAlarm pattern(s). The pattern was used on a sample of retrospective ICU patient data to predict cardiorespiratory arrest. The SuperAlarm pattern had a xx% true positive rate and a xx% false positive rate. The other pattern had a 0% true positive rate and a 0% false positive rate. "

        if name == "Select specialty...":
            self.redirect('/')
        path = os.path.join(os.path.dirname(__file__), 'survey.html')
        self.response.out.write(template.render(path, session))



def surveyMixer():
    surveyForUser = []
    while len(surveyForUser)<50:
        surveyForUser.append(sample(surveyAnswers, 1))
    return surveyForUser

logging.info(surveyMixer())
logging.info(len(surveyMixer()))

def forChoiceA():
    randomSAP = random.choice(superAlarmPatterns)
    logging.info("ramdomSAP = "+str(randomSAP))
    return randomSAP


def forChoiceB(lenOfChoiceA):
    logging.info("superAlarm len="+str(lenOfChoiceA))
    r = int(random.randint(0,9))
    logging.info("ramdom r="+str(r))
    r = r+(lenOfChoiceA-3)*10
    logging.info("ramdom after r="+str(r))
    logging.info("control len="+str(len(controlPatterns[r])))
    return controlPatterns[r]

app = webapp2.WSGIApplication([('/', MainHandler),('/survey', surveyHandler),('/admin', sendSurveyHandler)], debug=True)

def main():
  run_wsgi_app(app)

if __name__ == "__main__":
  main()