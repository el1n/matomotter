#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding: UTF-8

import os
import sys
import codecs
import random
import cgi
import time
import Cookie
import tweepy
import libmatomotter
import libGAEsession
import conf

def main():

	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE","")) # クッキーおいしいです
	session = libGAEsession.session_memcache() # セッションDB
	dbq = libmatomotter.q() # 質問用DB
	dba = libmatomotter.a() # 回答用DB


	param = cgi.FieldStorage()

	HOME_URI = conf.dict['HOME_URI']
	auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'], HOME_URI+"?m=callback", True) # tweepy(TwitterAPI)にConsumer keyくわせる
	api = tweepy.API(auth)

	if cookie.has_key("sessionid"): # クッキー埋め込み
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()

	try: # モード取得
		m = param.getvalue("m","").decode("utf-8")
	except: # こけたらクリアする
		m = None

	# HTTP共通ヘッダ部
	print u"Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print u"Content-Type: text/html; charset=UTF-8"


	if m == "login": # 認証前処理

		if session.get("access_key",None) == None:
			url = auth.get_authorization_url()
			session.set("token_secret", auth.request_token.secret)
			session.save()
			print u"Location:"+url
		else:
			auth.set_access_token(session.get("access_key"),session.get("access_secret"))

			try:
				url = HOME_URI
				auth.get_username()
				session.set("id",api.me().id)
				session.set("screen_name",api.me().screen_name)
			except:
				url = auth.get_authorization_url()
				session.set("token_secret", auth.request_token.secret)
			finally:
				print u"Location:"+url

			session.save()


	elif m == "callback": # 認証後処理

		oauth_token = param.getvalue("oauth_token","").decode("utf-8")
		oauth_verifier = param.getvalue("oauth_verifier","").decode("utf-8")

		try:
			auth.set_request_token(oauth_token,session.get("token_secret"))
			auth.get_access_token(oauth_verifier)
			session.set("access_key",auth.access_token.key)
			session.set("access_secret",auth.access_token.secret)
			auth.set_access_token(session.get("access_key"),session.get("access_secret"))
			session.set("id",api.me().id)
			session.set("screen_name",api.me().screen_name)
			url = HOME_URI+session.pop("int_cb","")
		except:
			url = HOME_URI+"?m=login"
		finally:
			print u"Location:"+url

		session.save()


	elif m == "logout": # ログアウト処理

		session.clear()
		session.save()
		print u"Location:"+HOME_URI


	elif m == "make": #質問作成ペーーーーージ
		if param.getvalue("post_flg","False").decode("utf-8") == "True":
			try: # access_keyとaccess_secretが使えるかどうか確認
				auth.set_access_token(session.get("access_key"),session.get("access_secret"))
				username = auth.get_username()
				if not session.get("q_temp",None) == None:
					q = session.get("q_temp")
					session.set("q_temp",None)
					q["id"] = session.get("id")
					q["screen_name"] = session.get("screen_name")
				else:
					q = {
						"theme":param.getvalue("theme","").decode("utf-8"),
						"option0":param.getvalue("option0","").decode("utf-8"),
						"option1":param.getvalue("option1","").decode("utf-8"),
						"option2":param.getvalue("option2","").decode("utf-8"),
						"option3":param.getvalue("option3","").decode("utf-8"),
						"id":session.get("id"),
						"screen_name":session.get("screen_name")
					}
				url = HOME_URI+u"?m=q&id="+str(dbq.set(q))
			except: # 使えなかった場合
				q = {
					"theme":param.getvalue("theme","").decode("utf-8"),
					"option0":param.getvalue("option0","").decode("utf-8"),
					"option1":param.getvalue("option1","").decode("utf-8"),
					"option2":param.getvalue("option2","").decode("utf-8"),
					"option3":param.getvalue("option3","").decode("utf-8")
				}
				session.set("q_temp",q)
				session.set("int_cb","?m=make&post_flg=True")
				url = HOME_URI+u"?m=login"
			finally:
				print u"Location:"+url

			print u""
			session.save()

		else:

			print u""
			try: # access_keyとaccess_secretが使えるかどうか確認
				auth.set_access_token(session.get("access_key"),session.get("access_secret"))
				username = auth.get_username()
				user_status = u'Logged in as @' + username + "(" + str(session.get("id")).encode("utf-8") + ") "
				login = True # 使えたらログインフラグ立つ
			except: # 使えなかった場合
				user_status = u'<a href="?m=login">Login</a>'
				login = False # ログインフラグへし折る
			finally:
				print user_status
				print u'<a href="?m=logout">Logout</a><br>'

			print u'<form method="POST" action="'+HOME_URI+u'?m=make">'
			print u'<input type="hidden" name="post_flg" value="True">'
			print u'<input type="text" name="theme" value=""><br>'
			print u'<input type="text" name="option0" value="">'
			print u'<input type="text" name="option1" value="">'
			print u'<input type="text" name="option2" value="">'
			print u'<input type="text" name="option3" value=""><br>'
			print u'<input type="submit" value="Post">'
			print u'</form>'

	elif m == "q": # 回答ペーーーーーージ
		print u""
		try: # access_keyとaccess_secretが使えるかどうか確認
			auth.set_access_token(session.get("access_key"),session.get("access_secret"))
			username = auth.get_username()
			user_status = u'Logged in as @' + username + "(" + str(session.get("id")).encode("utf-8") + ") "
			login = True # 使えたらログインフラグ立つ
		except: # 使えなかった場合
			user_status = u'<a href="?m=login">Login</a>'
			login = False # ログインフラグへし折る
		finally:
			print user_status
			print u'<a href="?m=logout">Logout</a><br>'

		print u'質問に答えるのれす^q^<br>'
		r = dbq.get(int(param.getvalue("id")))
		print u"しつもん: "+r.get("theme",None)+u"<br>"
		print u'こたえ１: <a href="?m=a&id='+param.getvalue("id")+u'&o=0">'+r.get("option0",None)+u'</a>'
		print u'こたえ２: <a href="?m=a&id='+param.getvalue("id")+u'&o=1">'+r.get("option1",None)+u'</a>'
		print u'こたえ３: <a href="?m=a&id='+param.getvalue("id")+u'&o=2">'+r.get("option2",None)+u'</a>'
		print u'こたえ４: <a href="?m=a&id='+param.getvalue("id")+u'&o=3">'+r.get("option3",None)+u'</a>'

	elif m == "a": # 答えた時の処理^p^

		if param.getvalue("id","").decode("utf-8") == "" or  param.getvalue("o","").decode("utf-8") == "" or param.getvalue("uid","").decode("utf-8") == "":
			print u"Location:"+HOME_URI

		else:
			try: # access_keyとaccess_secretが使えるかどうか確認
				auth.set_access_token(session.get("access_key"),session.get("access_secret"))
				username = auth.get_username()
				if not session.get("a_temp",None) == None:
					a = session.get("a_temp")
					session.set("a_temp",None)
					a["referring_id"] = session.get("id")
					a["referring_screen_name"] = session.get("screen_name")
				else:
					a = {
						"qid":param.getvalue("id").decode("utf-8"),
						"referred_id":param.getvalue("uid").decode("utf-8"),
						"referred_screen_name":(api.get_user(param.getvalue("uid").decode("utf-8"))).screen_name,
						"choice":param.getvalue("o").decode("utf-8"),
						"referring_id":session.get("id"),
						"referring_screen_name":session.get("screen_name")
					}
				url = HOME_URI+u"?m=q&id="+str(dba.set(a))
			except: # 使えなかった場合
				a = {
					"qid":param.getvalue("id").decode("utf-8"),
					"referred_id":param.getvalue("uid").decode("utf-8"),
					"referred_screen_name":(api.get_user(param.getvalue("uid").decode("utf-8"))).screen_name,
					"choice":param.getvalue("o").decode("utf-8"),
				}
				session.set("a_temp",a)
				session.set("int_cb","?m=a&post_flg=True")
				url = HOME_URI+u"?m=login"
			finally:
				print u"Location:"+url

			print u""
			session.save()

	else: # トップペーーーージ

		print u""

		try: # access_keyとaccess_secretが使えるかどうか確認
			auth.set_access_token(session.get("access_key"),session.get("access_secret"))
			username = auth.get_username()
			user_status = u'Logged in as @' + username + "(" + str(session.get("id")).encode("utf-8") + ") "
			login = True # 使えたらログインフラグ立つ
		except: # 使えなかった場合
			user_status = u'<a href="?m=login">Login</a>'
			login = False # ログインフラグへし折る
		finally:
			print user_status
			print u'<a href="?m=logout">Logout</a><br>'
			print u'<a href="?m=make">Make Question</a><br>'

		print (api.get_user(param.getvalue("uid","purin_fps").decode("utf-8"))).screen_name
#		if login == True: # ログイン状態の時
#			id_list = api.friends_ids() # フォロー中idを5000件上限で持ってくる
#			users = [] # 格納用のリスト作成

#			while len(users) < 10 and len(id_list) > 0: # 10件格納 or idのストックがなくなるまでルーーーープ
#				users.append(id_list.pop(random.randint(0,len(id_list)-1))) # どんどん格納する

#			for i in api._lookup_users(users):
#				print i.screen_name+u"<br>"


if __name__ == "__main__":
	main()
