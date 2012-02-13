import google.appengine.ext.db

class q:
	class dbi_q(google.appengine.ext.db.Model):
		id = google.appengine.ext.db.IntegerProperty()
		screen_name = google.appengine.ext.db.StringProperty()
		theme = google.appengine.ext.db.StringProperty()
		option0 = google.appengine.ext.db.StringProperty()
		option1 = google.appengine.ext.db.StringProperty()
		option2 = google.appengine.ext.db.StringProperty()
		option3 = google.appengine.ext.db.StringProperty()
		mtime = google.appengine.ext.db.DateTimeProperty(auto_now = True)
		ctime = google.appengine.ext.db.DateTimeProperty(auto_now = True,auto_now_add = True)

	def getid(s):
		return(s.id)

	def get(s,id):
		cur = s.dbi_q.get_by_id(id)
		if cur != None:
			r = {
				u"id":cur.id,
				u"screen_name":cur.screen_name,
				u"theme":cur.theme,
				u"option0":cur.option0,
				u"option1":cur.option1,
				u"option2":cur.option2,
				u"option3":cur.option3,
				u"mtime":cur.mtime,
				u"ctime":cur.ctime
			}
			return(r)
		else:
			return(None)

	def set(s,g,id = None):
		if g.get("id",None) == None:
			return(0)
		if g.get("screen_name",None) == None:
			return(0)
		if g.get("theme",None) == None:
			return(0)
		if g.get("option0",None) == None:
			return(0)

		cur = None
		if id != None:
			cur = s.dbi_q.get_by_id(id)
		if cur == None:
			cur = s.dbi_q()
		cur.id = g.get("id",None)
		cur.screen_name = g.get("screen_name",None)
		cur.theme = g.get("theme",None)
		cur.option0 = g.get("option0",None)
		cur.option1 = g.get("option1",None)
		cur.option2 = g.get("option2",None)
		cur.option3 = g.get("option3",None)
		cur.put()

		return(cur.key().id())

class a:
	class dbi_a(google.appengine.ext.db.Model):
		referring_id = google.appengine.ext.db.IntegerProperty()
		referring_screen_name = google.appengine.ext.db.StringProperty()
		referred_id = google.appengine.ext.db.IntegerProperty()
		referred_screen_name = google.appengine.ext.db.StringProperty()
		choice = google.appengine.ext.db.IntegerProperty()
		mtime = google.appengine.ext.db.DateTimeProperty(auto_now = True)
		ctime = google.appengine.ext.db.DateTimeProperty(auto_now = True,auto_now_add = True)

	def getid(s):
		return(s.id)

	def get(s,id):
		cur = s.dbi_a.get_by_id(id)
		if cur != None:
			r = {
				u"referring_id":cur.referring_id,
				u"referring_screen_name":cur.referring_screen_name,
				u"referred_id":cur.referred_id,
				u"referred_screen_name":cur.referred_screen_name,
				u"choice":cur.choice,
				u"mtime":cur.mtime,
				u"ctime":cur.ctime
			}
			return(r)
		else:
			return(None)

	def set(s,g,id = None):
		if g.get("referring_id",None) == None:
			return(0)
		if g.get("referring_screen_name",None) == None:
			return(0)
		if g.get("referring_id",None) == None:
			return(0)
		if g.get("referring_screen_name",None) == None:
			return(0)
		if g.get("choice",None) == None:
			return(0)

		cur = None
		if id != None:
			cur = s.dbi_a.get_by_id(id)
		if cur == None:
			cur = s.dbi_a()
		cur.referring_id = g.get("referring_id",None)
		cur.referring_screen_name = g.get("referring_screen_name",None)
		cur.referring_id = g.get("referring_id",None)
		cur.referring_screen_name = g.get("referring_screen_name",None)
		cur.choice = g.get("choice",None)
		cur.put()

		return(cur.key().id())
