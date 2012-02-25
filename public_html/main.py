#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import random
import cgi
import time
import Cookie
import tweepy
import mako.template
import mako.lookup
import libmatomotter
import libGAEsession
import conf


def get_userlist(access_key=None,access_secret=None,uid=None):

	# Tweepyに認証情報渡す
	auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'])
	api = tweepy.API(auth)

	# 初期化
	users = []
	id_list = {}
	return_users = {}
	default_users = [152965674,132426553,78364364,12939012,36803580]
	
	if access_key and access_secret: # アクセスキーがある時はフォロー中を取りに行く
		auth.set_access_token(access_key,access_secret)
		id_list = api.friends_ids()
	if uid: # IDの指定がある時は優先してリストに入れる
		users.append(uid)
		try:
			id_list.remove(uid)
		except:
			pass
	while len(users) < 5 and len(id_list) > 0: # IDリストが空になるか、5個貯まるまでルーーープ
		users.append(id_list.pop(random.randint(0,len(id_list)-1)))
	while len(users) < 5: # 5個に足りていなかったらデフォルトIDを設定
		users.append(default_users.pop())
	for i in api.lookup_users(users): # TweepyさんにID渡して戻ってきた情報をリストに入れる
		return_users[i.id] = i
	return return_users
	# おわり

def main():

	HOME_URI = conf.dict['HOME_URI']

	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE","")) # クッキーおいしいです
	session = libGAEsession.session_memcache() # セッションDB
	dbq = libmatomotter.q() # 質問用DB
	dba = libmatomotter.a() # 回答用DB
	param = cgi.FieldStorage()
	auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'], HOME_URI, True) # tweepy(TwitterAPI)にConsumer keyくわせる
	api = tweepy.API(auth)

	# クッキー埋め込み
	if cookie.has_key("sessionid"):
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()

	# makoちゃんに渡すパラメータ初期化
	tmpl_file = "main.tmpl" # 無指定の場合はmain.tmplを読みにいこう
	tmpl_args = {
		"title":"",
		"text":u"誰かに質問する→誰かについて答える→競え!!",
		"screen_name":session.get("screen_name",""),
		"profile_image":"",
		"user_list":"",
		"question":"",
		"answer":"",
		"param_make_theme":"",
		"param_make_option0":"",
		"param_make_option1":"",
		"param_make_option2":"",
		"param_make_option3":"",
		"error_make_theme":"",
		"error_make_desc":"",
		"error_make_option0":"",
		"error_make_option1":"",
		"param_q_id":"",
		"param_q_uid":"",
		"param_q_options":[],
		"param_q_tgt":[],
		"login_toggle":"",
		"param_target_url_1":"",
		"param_target_url_2":"",
		}


	# HTTP共通ヘッダ部
	print u"Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print u"Content-Type: text/html; charset=UTF-8"

	try: # 外部モード取得
		m = param.getvalue("m","").decode("utf-8")
	except: # こけたらクリアする
		m = None
	in_mode = session.get("in_mode",()) # 内部モード取得


	# 内部モード処理開始
	if len(in_mode):
		if in_mode[0] == "callback": # ログイン後処理
			try:
				auth.set_request_token(param.getvalue("oauth_token","").decode("utf-8"),session.get("token_secret"))
				auth.get_access_token(param.getvalue("oauth_verifier","").decode("utf-8"))
				session.set("access_key",auth.access_token.key)
				session.set("access_secret",auth.access_token.secret)
				auth.set_access_token(session.get("access_key"),session.get("access_secret"))
				session.set("id",api.me().id)
				session.set("screen_name",api.me().screen_name)
				url = HOME_URI
				session.set("in_mode",in_mode[1:])
			except:
				url = auth.get_authorization_url()
				session.set("token_secret", auth.request_token.secret)
			finally:
				m = "blank"
				print u"Location:"+url
			session.save()

		elif in_mode[0] == "post_q": # 質問投稿
			if session.get("id",None):
				q = session.get("temp_q")
				q["id"] = session.get("id")
				q["screen_name"] = session.get("screen_name")
				url = HOME_URI+u"?m=q&id="+str(dbq.set(q))
				session.set("in_mode",in_mode[1:])
				print u"Location:"+url
				m = "blank"
				session.save()

		elif in_mode[0] == "post_a": # 回答投稿
			if session.get("id",None):
				a_list = session.get("a_list")
				for i in a_list:
					i["referring_id"] = session.get("id")
					i["referring_screen_name"] = session.get("screen_name")
					dba.set(i)
				m = "blank"
				session.set("in_mode",in_mode[1:])
				print u"Location:"+HOME_URI
				session.save()

		elif in_mode[0] == "return_page": # もどれ
			if session.get("id",None):
				session.set("in_mode",in_mode[1:])
				print u"Location:"+HOME_URI+u"?"+session.get("return_to")
				m = "blank"
				session.set("return_to",None)
				session.save()

	# 外部モード処理開始
	if m == "blank": # 空白
		sys.exit()

	elif m == "login": # ログイン処理
		url = auth.get_authorization_url()
		session.set("token_secret", auth.request_token.secret)
		session.set("in_mode",("callback",)+session.get("in_mode",()))
		session.save()
		print(u"Location:"+url)
		sys.exit()

	elif m == "logout": # ログアウト処理
		session.clear()
		session.save()
		print u"Location:"+HOME_URI
		sys.exit()

	elif m == "make": # 質問作成ペーーーージ
		tmpl_file = "create.tmpl"
		if (param.getvalue("post_flg","").decode("utf-8")
		    and param.getvalue("theme","").decode("utf-8")
		    and param.getvalue("option0","").decode("utf-8")
		    and param.getvalue("option1","").decode("utf-8")
		    ):
			if session.get("id",None):
				q = {
					"theme":param.getvalue("theme","").decode("utf-8"),
					"option0":param.getvalue("option0","").decode("utf-8"),
					"option1":param.getvalue("option1","").decode("utf-8"),
					"option2":param.getvalue("option2","").decode("utf-8"),
					"option3":param.getvalue("option3","").decode("utf-8"),
					"id":session.get("id"),
					"screen_name":session.get("screen_name")
				}
			else:
				q = {
					"theme":param.getvalue("theme","").decode("utf-8"),
					"option0":param.getvalue("option0","").decode("utf-8"),
					"option1":param.getvalue("option1","").decode("utf-8"),
					"option2":param.getvalue("option2","").decode("utf-8"),
					"option3":param.getvalue("option3","").decode("utf-8")
				}
			session.set("temp_q",q)
			session.save()
			print u"Location:"+HOME_URI+u"?m=make_confirm"
			sys.exit()

		elif param.getvalue("post_flg","").decode("utf-8") or session.get("temp_q",None):

			q = {
				"theme":param.getvalue("theme","").decode("utf-8"),
				"option0":param.getvalue("option0","").decode("utf-8"),
				"option1":param.getvalue("option1","").decode("utf-8"),
				"option2":param.getvalue("option2","").decode("utf-8"),
				"option3":param.getvalue("option3","").decode("utf-8"),
				}
			
			if session.get("temp_q",None):
				q = session.pop("temp_q")
				session.save()
			
			if not q["theme"]:
				tmpl_args["error_make_theme"] = u"<br><b>タイトルを入力して下さい。</b>"
			if not q["option0"]:
				tmpl_args["error_make_option0"] = u"<br><b>選択肢1を入力して下さい。</b>"
			if not q["option1"]:
				tmpl_args["error_make_option1"] = u"<br><b>選択肢2を入力して下さい。</b>"
			tmpl_args["param_make_theme"] = q["theme"]
			tmpl_args["param_make_option0"] = q["option0"]
			tmpl_args["param_make_option1"] = q["option1"]
			tmpl_args["param_make_option2"] = q["option2"]
			tmpl_args["param_make_option3"] = q["option3"]
			
		else:
			pass

	elif m == "make_confirm": # 質問投稿確認
		tmpl_file = "answer.tmpl"
		if session.get("temp_q",None):
			q = session.get("temp_q")
			tmpl_args["text"] = q["theme"]
			tmpl_args["param_q_uid"] = session.get("id","")
			for i in (q["option0"],q["option1"],q["option2"],q["option3"]):
				if i == "":
					break
				tmpl_args["param_q_options"].append(i)
##			for i in get_userlist(session.get("access_key",None),session.get("access_secret",None),tmpl_args["param_q_uid"]):
##				q_tgt[str(i.id)] = i.screen_name
			tmpl_args["param_q_tgt"] = get_userlist(session.get("access_key",None),session.get("access_secret",None),tmpl_args["param_q_uid"])
		else:
			sys.exit()
			

	elif m == "q": # 回答ペーーーーーージ
		tmpl_file = "answer.tmpl"
		if not session.get("id",None) and not param.getvalue("uid",None): # ログインしてないし対象者も無い
			session.set("return_to",os.environ['QUERY_STRING'])
			session.set("in_mode",("return_page",))
			print u"Location:"+HOME_URI+u"?m=login"
			sys.exit()
		else: # ログインしてる or 対象者(uid)いる
			r = dbq.get(int(param.getvalue("id").decode("utf-8")))
			tmpl_args["text"] = r.get("theme",None)
			tmpl_args["param_q_id"] = param.getvalue("id").decode("utf-8")
			tmpl_args["param_q_uid"] = param.getvalue("uid","").decode("utf-8")
			for i in (r.get("option0",""),r.get("option1",""),r.get("option2",""),r.get("option3","")):
				if i == "":
					break
				tmpl_args["param_q_options"].append(i)
			q_tgt = {}
			for i in get_userlist(session.get("access_key",None),session.get("access_secret",None),tmpl_args["param_q_uid"]):
				q_tgt[i.id] = i.screen_name
			tmpl_args["param_q_tgt"] = q_tgt
			session.set("q_tgt",q_tgt)
		session.save()

	elif m == "a": # 回答処理
		q_tgt = session.get("q_tgt",None)
		qid = param.getvalue("id",None)
		if q_tgt and qid:
			a_list = []
			for i in q_tgt.keys():
				if param.getvalue(str(i),None):
					a = {
						"qid":qid,
						"referred_id":i,
						"referred_screen_name":q_tgt.get(i),
						"choice":int(param.getvalue(str(i)))
					}
					a_list.append(a)

			if session.get("id",None):
				for i in a_list:
					i["referring_id"] = session.get("id")
					i["referring_screen_name"] = session.get("screen_name")
					dba.set(i)
				url = HOME_URI+u"?m=q&id="+str(qid).encode("utf-8")
			else:
				session.set("a_list",a_list)
				session.set("return_to","m=q&id="+str(qid))
				session.set("in_mode",("post_a","return_page"))
				url = HOME_URI+u"?m=login"
			session.save()
			print u"Location:"+url
			sys.exit()

		else:
			pass

	else: # デフォルト（トップページ）
		pass


	# makoちゃん設定部
	tmpl_lookup = mako.lookup.TemplateLookup(directories=['./'])
	tmpl_file = "./"+tmpl_file
	tmpl = mako.template.Template(
		filename=tmpl_file,
		input_encoding="utf-8",
		output_encoding="utf-8",
		encoding_errors="replace",
		lookup = tmpl_lookup
		)

	# makoちゃん後処理
	if tmpl_args["title"]:
		tmpl_args["title"] += u" - "
	if tmpl_args["screen_name"]:
		tmpl_args["screen_name"] = u"@"+tmpl_args["screen_name"]
	else:
		tmpl_args["screen_name"] = u"ゲストさん (未認証)"
	if session.get("id",None):
		tmpl_args["login_toggle"] = u'<a href="./?m=logout">ログアウト</a>'
	else:
		tmpl_args["login_toggle"] = u'<a href="./?m=login">ログイン</a>'

	# makoさんおねがいします！
	print tmpl.render(**tmpl_args)

if name == '__main__':
	sys.exit(main())
