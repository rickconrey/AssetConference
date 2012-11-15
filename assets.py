import webapp2
import jinja2
import os
import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                        autoescape = True)

# Constants for nomType
ADULT = 0
BUSINESS = 1
SCHOOL = 2
YOUTH = 3

#def render_str(template, **params):
#    t = jinja_environment.get_template(template)
#    return t.render(params)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Nomination(db.Model):
    """Models a nomination for Adult, Business, School, and Youth nominations"""
    nomType = db.IntegerProperty()
    nominee = db.StringProperty()
    q1 = db.StringProperty(multiline=True)
    q2 = db.StringProperty(multiline=True)
    subFirst = db.StringProperty()
    subLast = db.StringProperty()
    subEmail = db.EmailProperty()
    subAddress = db.PostalAddressProperty()
    subPhone = db.PhoneNumberProperty()

class NominationHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def checkError(self, req):
        have_error = False

        params = {}
        params['nominee'] = req.get('nominee')
        params['q1'] = req.get('q1')
        params['q2'] = req.get('q2')
        params['subFirst'] = req.get('first')
        params['subLast'] = req.get('last')
        params['subEmail'] = req.get('email')
        params['subPhone'] = req.get('phone')
        params['subAddress'] = req.get('address')

        return params
    
    def nomAdd(self, req, nType):
        nom = Nomination()

        nom.nomType = nType
        nom.nominee = req.get('nominee')
        nom.q1 = req.get('q1')
        nom.q2 = req.get('q2')
        nom.subFirst = req.get('first')
        nom.subLast = req.get('last')
        nom.subEmail = req.get('email')
        nom.subPhone = req.get('phone')
        nom.subAddress = req.get('address')

        nom.put()
        
        
class MainPage(NominationHandler):
    def get(self):
        self.render('index.html')

class AdultPage(NominationHandler):
    def get(self):
        self.render('adult.html')

    def post(self):
        self.nomAdd(self.request, ADULT)
        self.render("index.html", msg="Thank you for your nomination!")
        #self.redirect('/')
        

class BusinessPage(NominationHandler):
    def get(self):
        self.render("business.html")

    def post(self):
        self.nomAdd(self.request, BUSINESS)
        self.render("index.html", msg="Thank you for your nomination!")
        #self.redirect('/')



class SchoolPage(NominationHandler):
    def get(self):
        self.render("school.html")

    def post(self):
        self.nomAdd(self.request, SCHOOL)
        self.render("index.html", msg="Thank you for your nomination!")
        #self.redirect('/')


class YouthPage(NominationHandler):
    def get(self):
        self.render("youth.html")

    def post(self):
        self.nomAdd(self.request, YOUTH)
        self.render("index.html", msg="Thank you for your nomination!")
        #self.redirect('/')



class ResultsPage(NominationHandler):
    def get(self):
        adults = db.GqlQuery("SELECT * "
                            "FROM Nomination "
                            "WHERE nomType = " + str(ADULT))

        business = db.GqlQuery("SELECT * "
                               "FROM Nomination "
                               "WHERE nomType = " + str(BUSINESS))

        schools = db.GqlQuery("SELECT * "
                              "FROM Nomination "
                              "WHERE nomType = " + str(SCHOOL))

        youth = db.GqlQuery("SELECT * "
                            "FROM Nomination "
                            "WHERE nomType = " + str(YOUTH))


        self.render("results.html", adults=adults, 
                    business=business, schools=schools,
                    youth=youth)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/adult', AdultPage),
                               ('/business', BusinessPage),
                               ('/school', SchoolPage),
                               ('/youth', YouthPage),
                               ('/results',ResultsPage),],
                              debug=True)

