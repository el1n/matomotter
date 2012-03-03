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


def get_userlist(access_key=None,access_secret=None,uid=None,num=5):

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
	while 100 > len(users) < num and len(id_list) > 0: # IDリストが空になるか、num個 or 100個貯まるまでルーーープ
		users.append(id_list.pop(random.randint(0,len(id_list)-1)))
	while 100 > len(users) < num and len(default_users) > 0: # num個に足りていなかったらデフォルトIDを設定
		users.append(default_users.pop())
	for i in api.lookup_users(users): # TweepyさんにID渡して戻ってきた情報をリストに入れる
		return_users[i.id] = i
	return return_users
	# おわり

def main():

	# 定数定義
	HOME_URI = "http://"+os.environ['HTTP_HOST']

	# ライブラリ略称定義
	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE","")) # クッキーおいしいです
	session = libGAEsession.session_memcache() # セッションDB
	dbq = libmatomotter.q() # 質問用DB
	dba = libmatomotter.a() # 回答用DB
	param = cgi.FieldStorage()

	# 変数定義
	http_loc = None # httpヘッダのLocation
        bitten_cookie = False # クッキー食べた？
	
	# クッキー処理
	if cookie.has_key("sessionid"):
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()
		else:
                        bitten_cookie = True # クッキー食べてた

	# HTTPヘッダ部
	print u"Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print u"Content-Type: text/html; charset=UTF-8"
	
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
		"param_theme":"",
		"param_option0":"",
		"param_option1":"",
		"param_option2":"",
		"param_option3":"",
		"error_theme":"",
		"error_option0":"",
		"error_option1":"",
		"param_q_id":"",
		"param_q_uid":"",
		"param_q_options":[],
		"param_q_tgt":[],
		"param_post_to":"",
		"login_toggle":"",
		"param_target_url_1":"",
		"param_target_url_2":"",
                "Results_id":[],
                "Results_value":{},
		}


	# 外部モード取得
	try: 
		m = param.getvalue("m","").decode("utf-8")
	except:
		m = None # こけたらクリアする


	# メイン処理部
	if m == "login": # ログイン前処理
		auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'], HOME_URI+u"/?m=callback", True)
		http_loc = auth.get_authorization_url()
		session.set("token_secret", auth.request_token.secret)

	elif m == "callback": # ログイン後処理(need cookie)
		if session.get("token_secret", None):
			auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'], HOME_URI+u"/?m=callback", True)
			api = tweepy.API(auth)
			try:
				auth.set_request_token(param.getvalue("oauth_token").decode("utf-8"),session.pop("token_secret"))
				auth.get_access_token(param.getvalue("oauth_verifier").decode("utf-8"))
				session.set("access_key",auth.access_token.key)
				session.set("access_secret",auth.access_token.secret)
				auth.set_access_token(session.get("access_key"),session.get("access_secret"))
				session.set("id",api.me().id)
				session.set("screen_name",api.me().screen_name)
				http_loc = HOME_URI+session.pop("return_to","")
			except:
				http_loc = auth.get_authorization_url()
				session.set("token_secret", auth.request_token.secret)
		else:
			http_loc = HOME_URI if bitten_cookie else HOME_URI+u"/?m=cookie_error"
				
	elif m == "logout":
		session.clear()
		http_loc = HOME_URI

	elif m == "make": # 質問作成ページ
		tmpl_file = "create.tmpl"
		post_flg = param.getvalue("post_flg","").decode("utf-8")
		q = {"theme":param.getvalue("theme","").decode("utf-8"),
		     "option0":param.getvalue("option0","").decode("utf-8"),
		     "option1":param.getvalue("option1","").decode("utf-8"),
		     "option2":param.getvalue("option2","").decode("utf-8"),
		     "option3":param.getvalue("option3","").decode("utf-8")
		     }
		if post_flg and q["theme"] and q["option0"] and q["option1"]:
			session.set("q",q)
			http_loc = HOME_URI+u"/?m=make_confirm"
		elif post_flg or session.get("q",None):
			if not post_flg:
				q = session.pop("q")
			if not q["theme"]:
				tmpl_args["error_theme"] = u"<br><b>タイトルを入力して下さい。</b>"
			if not q["option0"]:
				tmpl_args["error_option0"] = u"<br><b>選択肢1を入力して下さい。</b>"
			if not q["option1"]:
				tmpl_args["error_option1"] = u"<br><b>選択肢2を入力して下さい。</b>"
			tmpl_args["param_theme"] = q["theme"]
			tmpl_args["param_option0"] = q["option0"]
			tmpl_args["param_option1"] = q["option1"]
			tmpl_args["param_option2"] = q["option2"]
			tmpl_args["param_option3"] = q["option3"]
		else:
			pass

	elif m == "make_confirm": # 質問投稿確認ページ
		tmpl_file = "answer.tmpl"
		tmpl_args["param_post_to"] = u"?m=make_post"
		if session.get("q",None):
			q = session.get("q")
			tmpl_args["text"] = q["theme"]
			tmpl_args["param_q_uid"] = session.get("id","")
			for i in (q["option0"],q["option1"],q["option2"],q["option3"]):
				if i == "":
					break
				tmpl_args["param_q_options"].append(i)
			tmpl_args["param_q_tgt"] = get_userlist(session.get("access_key",None),session.get("access_secret",None),tmpl_args["param_q_uid"])
		else:
			http_loc = HOME_URI+u"/?m=make" if bitten_cookie else HOME_URI+u"/?m=cookie_error"

	elif m == "make_post": # 質問投稿処理
		if session.get("q",None):
			if session.get("id",None):
				q = session.pop("q")
				q["id"] = session.get("id")
				q["screen_name"] = session.get("screen_name")
				http_loc = HOME_URI + u"/?m=q&id=" + str(dbq.set(q))
			else:
				session.set("return_to",u"/?m=make_post")
				http_loc = HOME_URI + u"/?m=login"
		else:
			http_loc = HOME_URI

	elif m == "q": # 質問表示ページ
		tmpl_file = "answer.tmpl"
		qid = param.getvalue("id","").decode("utf-8")
		uid = param.getvalue("uid","").decode("utf-8")
		if qid:
			tmpl_args["param_post_to"] = u"?m=a&id="+qid
			r = dbq.get(int(qid))
			tmpl_args["text"] = r.get("theme",None)
			tmpl_args["param_q_uid"] = session.get("id","")
			for i in (r.get("option0",""),r.get("option1",""),r.get("option2",""),r.get("option3","")):
				if i == "":
					break
				tmpl_args["param_q_options"].append(i)
			q_tgt = get_userlist(session.get("access_key",None),session.get("access_secret",None),tmpl_args["param_q_uid"])
			tmpl_args["param_q_tgt"] = q_tgt
                        session.set("q_tgt",q_tgt)
                        

		else: # いやqidないっておかしいから帰れ
			http_loc = HOME_URI

	elif m == "a": # 回答処理＆結果確認ページ(need cookie)
                q_tgt = session.pop("q_tgt",None)
                a = {"qid":param.getvalue("id",None),
                     "referring_id":session.get("id",None),
                     "referring_screen_name":session.get("screen_name",None),
                     }
                if a["qid"] and q_tgt:
                        for i in q_tgt.keys():
                                a_list = []
                                if param.getvalue(str(i),None):
                                        a["referred_id"] = i
                                        a["referred_screen_name"] = q_tgt.get(i)
                                        a["choice"] = int(param.getvalue(str(i)))
                                        a_list.append(a)
                        if a["referring_id"]:
                                for i in a_list:
                                        dba.set(i)
                        else:
                                session.set("a",a_list)
                                session.set("return_to","/?m=a")
                                http_loc = HOME_URI+u"/?m=login"
                                        
		elif session.get("a",None):
                        a_list = session.pop("a")
                        for i in a_list:
                                dba.set(i)

                else:
			http_loc = HOME_URI if bitten_cookie else HOME_URI+u"/?m=cookie_error"

        elif m == "my": # 結果表示ページ
                tmpl_file = "result.tmpl"
                #仮データ
                tmpl_args["Results_id"] = [100,200]
                tmpl_args["Results_value"] = {100:{"Question":"質問1",
                                                   "Answer_num":3,
                                                   "Answer_text":["回答1","回答2","回答3"],
                                                   "Answer_Per":[10.00,20.00,70.00],
                                                   "Answered_User":[[],[],get_userlist().values()]
                                                   },
                                              200:{"Question":"質問2",
                                                   "Answer_num":4,
                                                   "Answer_text":["回答1","回答2","回答3","回答4"],
                                                   "Answer_Per":[10.00,20.00,30.00,40.00],
                                                   "Answered_User":[[],[],get_userlist().values(),[]]
                                                   }
                                              }
                
	elif m == "cookie_error": # クッキーないよページ
		tmpl_args["text"] = u"クッキー食べてください"

	else: # トップページ(無指定 or 無効なパラメータ)
		pass

	
	# makoちゃん設定部
	tmpl = mako.template.Template(
		filename="./"+tmpl_file,
		input_encoding="utf-8",
		output_encoding="utf-8",
		encoding_errors="replace",
		lookup = mako.lookup.TemplateLookup(directories=['./'])
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

        # デバッグモーーードトグル
        if param.getvalue("debug",None):
                session.set("debug",True)
        elif param.getvalue("debug",None) == 0:
                session.set("debug",None)

	# makoさんおねがいします!(*Location指定があればそっちに飛ばす)
	if http_loc:
                if session.get("debug",None):
                        print u""
                        print u'<a href="'+http_loc+u'">'+http_loc+u'</a>'
                else:
        		print u"Location:" + http_loc
	else:
		print u""
		print tmpl.render(**tmpl_args)


	if session.get("debug",None):
                print u"<BR>"
                for i in locals().keys():
                        print i
                        print u" = "
                        print locals().get(i)
                        print u"<BR>"

	# セッション保存
	session.save()

if __name__ == '__main__':
	sys.exit(main())
