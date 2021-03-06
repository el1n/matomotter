import uuid
import cPickle
import google.appengine.ext.db
import google.appengine.api.memcache

class _:
	def __init__(s,namespace = u"libGAEsession",expire = 604800):
		s.namespace = namespace
		s.expire = expire

		s.clear()
		s.new()

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

	def pop(s,k,v = None):
		r = s.get(k,v)
		s.set(k,None)
		return(r)

	def clear(s):
		s.d = {}
		return()

class session(_):
	class dbi(google.appengine.ext.db.Model):
		d = google.appengine.ext.db.BlobProperty()

	def load(s,id):
		cur = s.dbi.get_by_key_name(s.namespace + u"." + id)
		if cur != None:
			s.id = id
			s.d = cPickle.loads(cur.d)

			return(s.id)
		else:
			return(None)

	def save(s):
		cur = s.dbi.get_by_key_name(s.namespace + u"." + s.id)
		if cur == None:
			cur = s.dbi(key_name = s.namespace + u"." + s.id)
		cur.d = cPickle.dumps(s.d)
		cur.put()

		return(1)

class session_memcache(_):
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
