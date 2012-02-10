import uuid
import cPickle
import google.appengine.ext.db

class session:
	class db(google.appengine.ext.db.Model):
		id = google.appengine.ext.db.StringProperty()
		d = google.appengine.ext.db.BlobProperty()

	dbi = db()
	id = None
	d = {}

	def new(s):
		s.id = unicode(uuid.uuid4())
		return(s.id)

	def getid(s):
		return(s.id)

	def get(s,k,v = None):
		if s.d.has_key(k):
			return(s.d[k])
		else:
			return(v)

	def set(s,k,v = None):
		if v != None:
			s.d[k] = v
		else:
			if s.d.has_key(k):
				return(s.d.pop(k))
			else:
				return(None)

	def load(s,id):
		r = s.dbi.gql("WHERE id = :1 LIMIT 0,1",id).get()
		if r != None:
			s.id = r.id
			s.d = cPickle.loads(r.d)

			return(s.id)
		else:
			return(None)

	def save(s):
		s.dbi.id = s.id
		s.dbi.d = cPickle.dumps(s.d)
		s.dbi.put()

		return(1)
