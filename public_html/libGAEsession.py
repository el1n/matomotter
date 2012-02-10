import uuid
import cPickle
import google.appengine.ext.db
import google.appengine.api.memcache

class _:
	def __init__(s,namespace = u"libGAEsession",expire = 604800):
		s.dbh = s.dbi()
		s.namespace = namespace
		s.expire = expire
		s.id = None
		s.d = {}

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

class session(_):
	class db(google.appengine.ext.db.Model):
		namespace = google.appengine.ext.db.StringProperty()
		id = google.appengine.ext.db.StringProperty()
		d = google.appengine.ext.db.BlobProperty()

	def load(s,id):
		r = s.dbi.gql("WHERE namespace = :1 AND id = :2 LIMIT 0,1",s.namespace,id).get()
		if r != None:
			s.id = r.id
			s.d = cPickle.loads(r.d)

			return(s.id)
		else:
			return(None)

	def save(s):
		s.dbi.namespace = s.namespace
		s.dbi.id = s.id
		s.dbi.d = cPickle.dumps(s.d)
		s.dbi.put()

		return(1)

class session_memcache(_):
	class dbi():
		1

	def load(s,id):
		r = google.appengine.api.memcache.get(s.namespace + u"." + id)
		if r != None:
			s.id = id
			s.d = cPickle.loads(r)

			return(s.id)
		else:
			return(None)

	def save(s):
		google.appengine.api.memcache.set(s.namespace + u"." + s.id,cPickle.dumps(s.d),s.expire)

		return(1)
