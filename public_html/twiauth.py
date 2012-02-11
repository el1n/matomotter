#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, random, urllib, urllib2, cgi, hmac, hashlib

CONSUMER_KEY = 'WsgAzyPtjNmiRd3F9cVW9w'
CONSUMER_SECRET = 'G7HH3NYFfWMggzpM1cH0eJtBtI0U4G0QpgWvwvrLpcY'
request_token_url = 'http://twitter.com/oauth/request_token'
access_token_url = 'http://twitter.com/oauth/access_token'

def geturl(callback):

        # Request Token は GET で取得
        method = 'GET'
        
        # 必須パラメータを準備
        params = {
                "oauth_consumer_key": CONSUMER_KEY, # WEB で登録した oauth consumer key
                "oauth_signature_method": "HMAC-SHA1", # 暗号のアルゴリズム
                "oauth_timestamp": str(int(time.time())), # unixtime 
                "oauth_nonce": str(random.getrandbits(64)), # ランダム文字列
                "oauth_version": "1.0", # バージョン番号
                "oauth_callback": callback
                }
        # パラメータをソートし，URIエンコードした key=value の形にして & で繋げます
        params_str = '&'.join(['%s=%s' % (urllib.quote(key, ''),urllib.quote(params[key], ''))
                                   for key in sorted(params)])

        # メソッド，URIエンコードした URL,上で作ったパラメータ文字列を & で繋げます 
        message = '%s&%s&%s' % (method,urllib.quote(request_token_url,''), urllib.quote(params_str,''))

        # consumer_secret を元にキーを作成します 
        key = "%s&%s" % (CONSUMER_SECRET, '')

        # キーを元に message で hmac を作成します
        signature = hmac.new(key, message, hashlib.sha1)

        # そのダイジェストを base64 でエンコードし，余計な空白を取り除きます
        digest_base64 = signature.digest().encode("base64").strip()

        # 作成したダイジェストをパラメータに追加します
        params['oauth_signature'] = digest_base64

        # 作成したパラメータを GET のパラメータとして追加します
        _url = request_token_url+ '?' + urllib.urlencode(params)
        # その URL にアクセスし, ResponseBody を読み込みます
        data = cgi.parse_qs(urllib.urlopen(_url).read())


        
        return data.get("oauth_callback_confirmed")[0], u'http://twitter.com/oauth/authorize?oauth_token='+data['oauth_token'][0], data.get("oauth_token_secret")[0]

def getatoken(oauth_token, oauth_verifier, oauth_token_secret):

        # Access Token は GET で取得
        method = 'GET'

        # 必須パラメータを準備
        params = {
                "oauth_consumer_key": CONSUMER_KEY, # WEB で登録した oauth consumer key
                "oauth_signature_method": "HMAC-SHA1", # 暗号のアルゴリズム
                "oauth_timestamp": str(int(time.time())), # unixtime 
                "oauth_nonce": str(random.getrandbits(64)), # ランダム文字列
                "oauth_version": "1.0" # バージョン番号
                }
        # パラメータに先程取得した値を追加
        params['oauth_token'] = oauth_token
        params['oauth_verifier'] = oauth_verifier

        # パラメータをソートし，URIエンコードした key=value の形にして & で繋げます
        params_str = '&'.join(['%s=%s' % (urllib.quote(key, ''),urllib.quote(params[key], ''))
                                   for key in sorted(params)])

        # メソッド，URIエンコードした URL,上で作ったパラメータ文字列を & で繋げます 
        message = '%s&%s&%s' % (method,urllib.quote(access_token_url,''), urllib.quote(params_str,''))

        # consumer_secret と oauth_token_secret を元にキーを作成します 
        key = "%s&%s" % (CONSUMER_SECRET, oauth_token_secret)

        # キーを元に message で hmac を作成します
        signature = hmac.new(key, message, hashlib.sha1)

        # そのダイジェストを base64 でエンコードし，余計な空白を取り除きます
        digest_base64 = signature.digest().encode("base64").strip()

        # 作成したダイジェストをパラメータに追加します
        params['oauth_signature'] = digest_base64

        # ヘッダに Authorization:OAuth を追加します
        opener = urllib2.build_opener()
        opener.addheaders = [('Authorization','OAuth')]

        # 作成したパラメータを GET のパラメータとして追加します
        _url = access_token_url + '?' + urllib.urlencode(params)

        # その URL にアクセスし, ResponseBody を読み込みます
        data = cgi.parse_qs(opener.open(_url).read())
        
        return data.get("screen_name")[0], data.get("oauth_token")[0]
