# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

import os
import sys

from Qt import Qt, QtCore


import app_globals as G

class Srv(object):

    def __init__(self, name=None, ki=None, url=None):
        self.name = name
        self.ki = ki
        self.url = url


    def __repr__(self):
        return "<Src url=%s>"

class XSettings( QtCore.QObject ):

    CURR_SERVER_KI = "current/server_ki"

    def __init__( self, parent=None ):
        QtCore.QObject.__init__( self, parent )

        self.settings = QtCore.QSettings("AGS", "ags-desktop-pyqt")

        self.servers = {}

        self.servers['online'] = Srv(**{'name': 'Online', "ki": "live",
                                    'url': 'http://ags.daffodil.uk.com'})

        self.servers['dev'] = Srv(**{'name': 'Developer', "ki": "dev",
                                    'url': 'http://localhost:13777'})

    def set_current_server( self, ki ):
        self.settings.setValue( self.CURR_SERVER_KI, ki )
        self.settings.sync()
        if ki in self.servers:
            self._current_server = self.servers[ki]
        return self._current_server

    def current_server( self ):
        ki = str( self.settings.value( self.CURR_SERVER_KI ) )
        if ki in self.servers:
            return self.server[ki]
        return self.servers["dev"]

    ##==============================
    ## Window Save/Restore
    def save_window( self, window ):
        name = window.objectName()
        if len(name) == 0:
            return
        self.settings.setValue( "window/%s/geometry" % name, QtCore.QVariant( window.saveGeometry() ) )

    def restore_window( self, window ):
        name = str(window.objectName())
        if len(name) == 0:
            return
        window.restoreGeometry( self.settings.value( "window/%s/geometry" % name ).toByteArray() )
