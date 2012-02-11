#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding: UTF-8

import os
import cgi
import time
import Cookie
import libGAEsession
import sys
import codecs

#sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

CALLBACK_URI = "http://localhost:8080/sample8.py"

def main():

	print u"Content-Type: text/html; charset=UTF-8"
	print u""
	print u"にほんご"

if __name__ == "__main__":
	main()
