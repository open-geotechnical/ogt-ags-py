# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""
import json
from Qt import QtNetwork, QtCore, Qt, pyqtSignal

import app_globals as G

ATTR_ID = QtNetwork.QNetworkRequest.User


class XReply:
	"""This is the data that is emitted request finished et all"""
	def __init__(self, qreply, tid=None, origin=None, status=None, flag=None, error=None, data=None):

		self.origin = qreply.request().originatingObject()
		self.http_code = qreply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
		self.tid = str(qreply.request().attribute(ATTR_ID))

		self.url = qreply.request().url().toString(QtCore.QUrl.RemoveScheme|QtCore.QUrl.RemovePort)


		self.error = error

		self.data = None



	def __repr__(self):
		d = "-"
		if self.data:
			if isinstance(self.data, dict):
				d = sorted(self.data.keys())
			else:
				d = self.data
		return "<XReply ori=%s, err=%s data=%s>" % (self.origin.__class__.__name__,  self.error, d)

	def debug(self):
		if self.data:
			print(self.data.keys())


class ServerConnection( QtCore.QObject ):
	"""
	HTTP Client
	"""
	TIMEOUT = 3000 #30000

	response = pyqtSignal(object) # XReply

	def __init__( self, parent=None, server=None ):
		QtCore.QObject.__init__( self, parent )

		self.debug = False

		self.callbacks = {}

		self.netManager = QtNetwork.QNetworkAccessManager( self )

		## Initialise cookies
		self.cookieJar = QtNetwork.QNetworkCookieJar()
		self.netManager.setCookieJar( self.cookieJar )


		self.netManager.finished.connect(self.on_request_finished)
		#self.netMan.error.connect(self._on_server_read_error)



	def get( self, origin=None, url=None, params=None, tag=None,
	         cb=None, widget=None,  debug=False, spinner=True):


		self.debug = False


		srv = G.settings.current_server()
		if srv == None:
			print("NO Server in dServer.fetch()")
			return

		url = QtCore.QUrl( "%s/ajax%s" % ( srv.url, url ) )

		#q = QtCore.QUrlQuery()


		if params:
			for k, v in params.items():
				url.addQueryItem( str( k ), str( v ) )

		request = QtNetwork.QNetworkRequest()
		request.setUrl( url )
		request.setOriginatingObject(origin)
		request.setPriority(QtNetwork.QNetworkRequest.HighPriority)
		if tag:
			request.setAttribute(ATTR_ID, tag)

		#self.load_cookies() TODO

		if spinner:
			pass #self.spin(True)


		if G.args.dev:
			print("# --- GET: tag=%s, %s" % (tag, url.toString()))
		#self.trigger_reply( request, SERVER_STATUS.REQUESTING, SERVER_FLAG.WAIT )
		## creat own accoutn bundle and senf

		#req = Request(url)
		##req.timeout.connect(self.on_timeout)
		##self.requests.append(req)
		#req.reply = self.netManager.get( request )
		reply = self.netManager.get( request )



	def on_request_finished( self, qreply ):

		"""Server Request has finished, so parse and check for errors"""
		#self.spin(False)

		reply = XReply(qreply=qreply)
		reply.tag = qreply.request().attribute(ATTR_ID)

		reply.origin = qreply.request().originatingObject()

		## Things not OK
		if reply.http_code != 200:
			reply.error = "HTTP Error: %s" % reply.http_code
			qreply.deleteLater()
			self.response.emit(reply)
			return

		if qreply.error():
			print("ERROR", qreply.error(), qreply.attribute(QtNetwork.QNetworkReply.HttpStatusCodeAttribute))
			catchme_todo
			qreply.deleteLater()
			return

		## Save Cookies - TODO
		"""
		cookies = self.netManager.cookieJar().allCookies()
		#print "-------- REC COOKIES----------------_"
		G.settings.beginGroup( "cookies" )
		for cookie in cookies:
			G.settings.setValue( "%s" % str( cookie.name() ), str( cookie.value() ) )
			#print "SAVE", cookie.name(), cookie.value()
		G.settings.endGroup()
		"""


		## Decode json
		# make it py/str/ascii for now (need to catch non ascii soon and utf-8 everywhere)
		# TODO catch non unicode
		contents = str(qreply.readAll().data())
		#print("contents=", contents)

		try:
			reply.data = json.loads(contents)

			# Always expect a dict or list so add error
			if isinstance(reply.data, dict) or isinstance(reply.data, list):
				pass # ok
			else:
				reply.error = "Does nto seem to be json"

			qreply.deleteLater()
			self.response.emit(reply)
			return

		except ValueError as e:
			reply.error = "Not Valid json %s" % str(e)
			qreply.deleteLater()
			self.response.emit(reply)
			return

		except TypeError as e:
			reply.error = "Not Valid json %s" % str(e)
			qreply.deleteLater()
			self.response.emit(reply)
			return

		## json is decoded and works
		print "should now get here"
		if self.debug:
			print("       data keys: %s" % " ".join( sorted( resp.data.keys() ) ))
		qreply.deleteLater()
