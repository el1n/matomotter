import uuid
import cPickle
import google.appengine.ext.db

class sei:
	class gae_session(google.appengine.ext.db.Model):
		id = google.appengine.ext.db.StringProperty()
		d = google.appengine.ext.db.BlobProperty()

	ses = gae_session()
	id = None
	d = {}

	def new(s):
		s.id = str(uuid.uuid4())
		return(s.id)

	def id_(s):
		return(s.id)

	def has_key(s,k):
		if s.d.has_key(k):
			return(1)
		else:
			return(0)

	def get(s,k,v = None):
		if s.has_key(k):
			return(s.d[k])
		else:
			return(v)

	def set(s,k,v = None):
		if v != None:
			s.d[k] = v
		else:
			if s.has_key(k):
				return(s.d.pop(k))
			else:
				return(None)

	def load(s,id):
		cur = google.appengine.ext.db.GqlQuery("SELECT * FROM gae_session WHERE id = :1 LIMIT 0,1",id)
		r = cur.get()
		if(r != None):
			s.id = r.id
			s.d = cPickle.loads(r.d)

			return(s.id)
		else:
			return(None)

	def save(s):
		s.ses.id = s.id
		s.ses.d = cPickle.dumps(s.d)
		s.ses.put()

		return(1)
