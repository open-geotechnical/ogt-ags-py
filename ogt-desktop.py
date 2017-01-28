#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import argparse
from PyQt4 import QtGui


import ogtgui.main_window


parser = argparse.ArgumentParser(description="Launch desktop application")
parser.add_argument("--dev", help="Developer mode", action="store_true")

parser.add_argument("ags_file", nargs='?', type=str, help="AGS formatted file to load at startup")

if __name__ == '__main__':


    args = parser.parse_args()

    app = QtGui.QApplication( sys.argv )

    if args.dev == False:
        splashScreen = ogtgui.main_window.MainWindow.show_splash()
    app.processEvents()

    ## Main Window
    window = ogtgui.main_window.MainWindow(args)

    if args.dev == False:
        splashScreen.finish( window )
    window.show()

    sys.exit( app.exec_() )

