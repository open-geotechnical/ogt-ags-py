# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>

"""
# Icons http://www.visual-case.it/cgi-bin/vc/GMapsIcons.pl
import os

from Qt import QtCore, QtGui, QtWebKit
from img import Ico
import app_globals as G
from . import PROJECT_ROOT_PATH

MAP_PATH = os.path.join(PROJECT_ROOT_PATH, "static", "map")


##=================================================================================
## WebKit Sub Class
##=================================================================================

class WebViewX(QtWebKit.QWebView):
    """Subclassed QWebView for mouse events"""

    def __init__(self, parent=None):
        QtWebKit.QWebView.__init__(self, parent)

        self.x_mouse_point = None

    def mouseMoveEvent(self, ev):
        """Custom mouse moved
           @note: emits a "mouse_moved" event with position
        """
        # print "mouseMoveEvent", ev.globalPos()
        QtWebKit.QWebView.mouseMoveEvent(self, ev)
        self.emit(QtCore.SIGNAL("mouse_moved"), ev.globalPos())
        self.x_mouse_point = ev.globalPos()

    def mouse_point(self):
        return self.x_mouse_point



class MapViewWidget(QtGui.QWidget):
    debug = True

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.ogtDoc = None
        self.Zoom = MapZoomWidget()
        # self.gSpot = gLocation()

        self.map_initialized = False
        self.pending_markers = []
        self.locations = {}

        self.widget = None
        self.edit_mode = False
        self.dirty = None
        self.geo = None
        self.result_count = 0
        self.results = None

        ## The map local html url
        local_html_file_path = os.path.join(MAP_PATH, "map.html")
        self.map_url = QtCore.QUrl(local_html_file_path)

        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.on_timer)

        #####################################################
        ## Popup Menu's
        #####################################################
        self.popMarker = QtGui.QMenu("pop")
        self.actionMoveMarker = self.popMarker.addAction('Move Marker', self.on_action_move_marker)

        self.popMap = QtGui.QMenu("pop")
        self.actionAddMarker = self.popMap.addAction(Ico.icon(Ico.Add), 'Save this view', self.on_action_save_view)
        self.actionAddMarker = self.popMap.addAction(Ico.icon(Ico.Add), 'Add test point', self.on_action_test_point)
        # self.actionBranch = self.popMarker.addAction(dIco.icon(dIco.Branch), 'Branch', self.on_action_branch)


        ###############
        ##  Layout
        mapLayout = QtGui.QVBoxLayout()
        mapLayout.setContentsMargins(0, 0, 0, 0)
        mapLayout.setSpacing(0)
        self.setLayout(mapLayout)
        mapLayout.setSpacing(0)

        ##======================================================
        toolbar = QtGui.QToolBar()
        mapLayout.addWidget(toolbar, 0)
        m = 4
        style = "border-bottom: 0px; border-left: 0px;"

        ## Map Type Box
        groupBoxMapType = QtGui.QGroupBox("Map Type")
        groupBoxMapType.setStyleSheet(style)
        toolbar.addWidget(groupBoxMapType)
        layoutMapTypeBox = QtGui.QHBoxLayout()
        layoutMapTypeBox.setContentsMargins(m, m, m, m)
        groupBoxMapType.setLayout(layoutMapTypeBox)

        ## Zoom Level
        groupBoxZoom = QtGui.QGroupBox("Zoom View")
        groupBoxZoom.setStyleSheet(style)
        toolbar.addWidget(groupBoxZoom)
        layoutZoomBox = QtGui.QHBoxLayout()
        layoutZoomBox.setContentsMargins(m, m, m, m)
        groupBoxZoom.setLayout(layoutZoomBox)

        #####################################################
        #### Map Type Dropdown
        #####################################################
        self.groupMapType = QtGui.QButtonGroup(self)
        self.groupMapType.setExclusive(True)
        self.connect(self.groupMapType, QtCore.SIGNAL("buttonClicked(QAbstractButton *)"), self.on_map_type)

        for b in ['RoadMap', 'Satellite', 'Hybrid', 'Terrain']:
            butt = QtGui.QToolButton()
            butt.setText(b)
            butt.setCheckable(True)
            butt.setChecked(b == "Hybrid")
            layoutMapTypeBox.addWidget(butt)
            self.groupMapType.addButton(butt)

        #########################
        ## Zoom Views
        #########################
        self.groupZoom = QtGui.QButtonGroup(self)
        self.groupZoom.setExclusive(True)
        self.connect(self.groupZoom, QtCore.SIGNAL("buttonClicked(QAbstractButton *)"), self.on_zoom_action)
        for b in self.Zoom.levels():
            """act = QtGui.QAction(tolbar3)
            act.setText(b[0])
            act.setProperty("zoom", QtCore.QVariant(b[1]))
            act.setCheckable(True)

            tolbar3.addAction(act)
            self.groupZoom.addAction(act)
            """
            butt = QtGui.QToolButton()
            butt.setText(b[0])
            butt.setProperty("zoom", QtCore.QVariant(b[1]))
            butt.setCheckable(True)
            butt.setChecked(b[0] == 'Uk')
            layoutZoomBox.addWidget(butt)
            self.groupZoom.addButton(butt)

        # tolbar3.addWidget(widgets.Widgets.ToolBarSpacer())



        ##############################
        ## Map Mode - View or Edit
        ##############################
        """
        self.groupEditMode = QtGui.QButtonGroup(self)
        self.groupEditMode.setExclusive(True)
        self.connect(self.groupEditMode, QtCore.SIGNAL("buttonClicked(QAbstractButton *)"), self.on_edit_mode)
        for b in ['View Mode', 'Edit Mode']:
            butt = QtGui.QPushButton()
            butt.setText(b)
            butt.setCheckable(True)
            butt.setHidden(True)
            if b == "View Mode": #G.settings.value("map_mode", "Hybrid"):
                butt.setChecked(True)
                butt.setIcon(dIco.icon(dIco.Yellow))
            else:
                butt.setIcon(dIco.icon(dIco.Black))
            tolbar3.addWidget(butt)
            self.groupEditMode.addButton(butt)
        self.buttonSave = QtGui.QPushButton()
        self.buttonSave.setIcon(dIco.icon(dIco.Save))
        #.buttSave.setText("Save")
        self.buttonSave.setDisabled(True)
        self.buttonSave.setHidden(True)
        tolbar3.addWidget(self.buttonSave)
        self.connect(self.buttonSave, QtCore.SIGNAL("clicked()"), self.on_save_button)
        """

        ###########################################
        ## Web Browser view
        ###########################################
        self.webView = WebViewX()
        mapLayout.addWidget(self.webView, 20)
        self.webView.page().mainFrame().addToJavaScriptWindowObject("QtWidget", self)
        self.connect(self.webView, QtCore.SIGNAL("loadProgress(int)"), self.on_initialize_progress)
        self.connect(self.webView, QtCore.SIGNAL("loadFinished(bool)"), self.on_initialize_finished)

        ###########################################
        ## Status Bar
        ###########################################
        self.statusBar = QtGui.QStatusBar()
        mapLayout.addWidget(self.statusBar)

        ## Progress
        self.progress = QtGui.QProgressBar()
        self.statusBar.addPermanentWidget(self.progress)

        ## Lat
        style = ""  # background-color: #efefef;"
        self.statusBar.addPermanentWidget(QtGui.QLabel("Lat:"))
        self.lat = QtGui.QLabel()
        self.lat.setStyleSheet(style)
        self.lat.setFixedWidth(140)
        self.lat.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.statusBar.addPermanentWidget(self.lat)

        ## Lng
        self.statusBar.addPermanentWidget(QtGui.QLabel("Lng:"))
        self.lng = QtGui.QLabel()
        self.lng.setStyleSheet(style)
        self.lng.setFixedWidth(140)
        self.lng.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.statusBar.addPermanentWidget(self.lng)

        ## Zoom
        self.statusBar.addPermanentWidget(QtGui.QLabel("Zoom:"))
        self.zoomLabel = QtGui.QLabel("")
        self.zoomLabel.setFixedWidth(20)
        self.statusBar.addPermanentWidget(self.zoomLabel)

        ###########################################
        ## Setup
        self.connect(self, QtCore.SIGNAL("zoom_changed"), self.on_zoom_changed)
        # self.connect(self, QtCore.SIGNAL("marker_right_clicked"), self.on_zoom_changed)
        self.initialize()

    ###########################################
    ## Zoom Related
    ###########################################
    def on_zoom_action(self, butt):
        zoom = butt.property("zoom").toString()
        self.set_zoom(zoom)

    def set_zoom(self, zoom):
        js_str = "set_zoom(%s)" % zoom
        self.execute_js(js_str)

    def zoom_to(self, lat, lng, zoom=None):
        if zoom == None:
            zoom = self.zoomLabel.text()
        js_str = "zoom_to(%s, %s, %s)" % (lat, lng, zoom)
        print js_str
        self.execute_js(js_str)

    def zoom_to_marker(self, widget, mId, zoom=None):
        if zoom == None:
            zoom = self.zoomLabel.text()
        js_str = "zoom_to_marker('%s', '%s', %s)" % (self.widget_name(widget), str(mId), str(zoom))
        self.execute_js(js_str)

    @QtCore.pyqtSignature("map_zoom_changed(QString)")
    def map_zoom_changed(self, zoom):
        self.emit(QtCore.SIGNAL("zoom_changed"), zoom)

    def on_zoom_changed(self, new_zoom_level):
        self.zoomLabel.setText(new_zoom_level)
        for a in self.groupZoom.buttons():
            checked = a.property("zoom").toString() == new_zoom_level
            a.setChecked(checked)

    ###########################################
    ## Marker Events
    ###########################################

    ## Added
    @QtCore.pyqtSignature("marker_added(QString, QString, QString)")
    def marker_added(self, widget_name, mId, idx):
        self.emit(QtCore.SIGNAL("marker_added"), str(widget_name), str(mId), str(idx))

    ## Clicked
    @QtCore.pyqtSignature("marker_clicked(QString, QString)")
    def marker_clicked(self, widget_name, myId):
        if self.debug:
            print "MV>> marker_clicked", widget_name, myId
        self.emit(QtCore.SIGNAL("marker_clicked"), str(widget_name), str(myId))

    ## Right Clicked
    @QtCore.pyqtSignature("marker_right_clicked(QString, QString)")
    def marker_right_clicked(self, widget_name, mId):
        print " >> marker_right_clicked", widget_name, mId
        # self.curr_location_id = str(location_id)
        self.emit(QtCore.SIGNAL("marker_right_clicked"), str(widget_name), str(mId))

    # return
    # dic = self.locations[self.curr_location_id]
    # self.actionAccount.setText(dic['company'])
    # self.actionBranch.setText(dic['address'])
    # self.popMarker.exec_( self.webView.mouse_point() )

    ## Double Clicked
    @QtCore.pyqtSignature("marker_double_clicked(QString, QString)")
    def marker_double_clicked(self, idx, location_id):
        print "== marker_double_clicked", idx, location_id
        self.emit(QtCore.SIGNAL("marker_double_clicked"), idx, location_id)

    ## Un-Selected
    @QtCore.pyqtSignature("marker_unselected(QString, QString)")
    def marker_unselected(self, idx, location_id):
        print "== marker_unselected", idx, location_id
        self.emit(QtCore.SIGNAL("marker_unselected"), idx, location_id)

    ## Marker Save
    """
    @QtCore.pyqtSignature("marker_save(QString, QString, QString, QString)")
    def marker_save(self, idx, location_id, lat, lng):
        print "== marker_save", idx, location_id, lat, lng
        self.emit(QtCore.SIGNAL("marker_save"), str(idx), str(location_id), str(lat), str(lng))
        res = QtGui.QMessageBox.question(self, "Save", "Save change of position ?",  "No", "Yes")
        #print "q", res
        if res == 1:
            geo = {'lat': str(lat), 'lng': str(lng), 'method': 'manual'}
            server_vars = {'location_id': location_id, 'geo': json.dumps(geo)}
            server = dServerCall(self)
            self.connect(server, QtCore.SIGNAL('dataReady'), self.on_save_location_geo_callback)
            server.action(dAction.location_geo, server_vars, None, True)
            self.statusBar.showMessage("Saving....")	
    """

    def on_save_location_geo_callback(self, jsonData):
        print "back", jsonData
        self.statusBar.showMessage("Postion Saved", 5000)

    @QtCore.pyqtSignature("marker_edit(QString)")
    def marker_edit(self, idx):
        print "== marker_edit", idx
        ##item = self.tree.findItems(idx, QtCore.Qt.MatchExactly, self.COLS.idx)[0]
        ##item.setText(self.COLS.address, "FFFF")
        ##self.tree.setCurrentItem(item)
        QtGui.QMessageBox.information(self, "ff")

    ###########################################
    ## Map Events
    ###########################################

    ## Added
    @QtCore.pyqtSignature("map_error(QString)")
    def map_error(self, error_str):
        print "map_error", error_str
        self.emit(QtCore.SIGNAL("map_error"), error_str)

    ## Map Initialiszed callback
    @QtCore.pyqtSignature("set_map_init()")
    def set_map_init(self):
        self.map_initialized = True
        self.emit(QtCore.SIGNAL("map_initialized"), True)
        self.statusBar.showMessage("Map Initialised", 4000)

    @QtCore.pyqtSignature("map_mouse_move(QString, QString)")
    def map_mouse_move(self, lat, lng):
        # print "ll", lat, lng
        self.lat.setText(lat)
        self.lng.setText(lng)

    @QtCore.pyqtSignature("map_right_click(QString, QString)")
    def map_right_click(self, lat, lng):
        print "RIGHT", lat, lng, self.webView.mouse_point()
        # self.emit(
        # self.map_ri
        self.geo = {'lat': lat, 'lng': lng}
        # self.lat.setText(lat)
        # self.lng.setText(lng)
        self.popMap.exec_(self.webView.mouse_point())

    # self.popMarker.exec_( self.mapFrom(self, self.pos()) )

    ###########################################
    ## Do Lookup
    ###########################################
    def do_lookup(self, widget, location_id, search):
        self.result_count = None
        self.results = []
        widget_name = widget.property("widget_name").toString()
        search = str(search)
        print "-----------------------------------", widget
        # print ">> do_lookup >>", widget_name
        loc_id = str(location_id) if location_id else "0"
        js_str = "do_lookup('%s', '%s', '%s')" % (widget_name, loc_id, search)
        print "javascript:", js_str
        self.execute_js(js_str)
        self.statusBar.showMessage("Looking up...")
        self.progress.setRange(0, 0)
        self.progress.show()

    ## js >> Results Count
    @QtCore.pyqtSignature("lookup_result_count(QString, QString, QString)")
    def lookup_result_count(self, widget_name, location_id, count):
        # print "result count >>>", widget_name, location_id, count
        self.result_count = int(count)
        if self.result_count == 0:
            self.emit(QtCore.SIGNAL("lookup_results"), widget_name, None)
            self.progress.hide()
            self.statusBar.showMessage("No results found", 3000)

    ## js >> Result Item
    @QtCore.pyqtSignature("lookup_result_item(QString, QString, QString, QString, QString)")
    def lookup_result_item(self, widget_name, location_id, address_unicode, lat, lng):
        ## Clean up unicode
        address = ""
        for l in range(0, len(address_unicode)):
            try:
                character = str(address_unicode[l])
                address = address + character
            except:
                pass
        print ">>", address
        widget_name = str(widget_name)
        location_id = str(location_id)
        lat = str(lat)
        lng = str(lng)
        self.results.append({'location_id': location_id, 'address': address, 'lat': lat, 'lng': lng})

        ## This event fires after we got all the results from javascript - cant return dic yet
        if len(self.results) == self.result_count:
            self.emit(QtCore.SIGNAL("lookup_results"), widget_name, self.results)
            self.statusBar.showMessage("%s results found" % self.result_count, 3000)
            self.progress.hide()

    def add_address(self, dic, zoom_to=False):
        return
        if not dic['geo']:
            print "no geo"
            return

        if self.map_initialized:
            self.add_address_marker(dic, zoom_to)
            return

        self.pending_markers.append([dic, zoom_to])
        self.timer.start(3000)

    ####################################################
    ## Add Marker
    ####################################################
    def add_address_marker(self, dic, zoom_to=False):
        self.locations[dic['location_id']] = dic
        geo = dic['geo']  # json.loads( dic['geo'] )
        js_str = "add_address_marker(%s, '%s', %s, %s, '%s')" % (
        dic['location_id'], dic['company'], geo['lat'], geo['lng'], geo['method'])
        self.execute_js(js_str)
        if zoom_to:
            self.pan_to(geo['lat'], geo['lng'])
            self.set_zoom(self.Zoom.level('Local'))

    #def add_marker(self, widget, mId, lat, lng, icon_color=None, label=None):
    def add_marker(self, widget, id=None, lat=None, lon=None, icon_color=None, label=None):
        if icon_color == None:
            icon_color = "blue"
        if label == None:
            label = ""
        # print "add_marker", lat, lng, self.widget_name(widget)
        js_str = "add_marker('%s', '%s', %s, %s, '%s', '%s')" % (
            widget, id, lat, lon, icon_color, label)
        # print "js=", js_str
        self.execute_js(js_str)

    def select_marker_by_mid(self, widget, myId, emode=False):
        js_str = "select_marker_by_mid('%s', '%s', %s)" % (self.widget_name(widget), str(myId), 1 if emode else 0)
        self.execute_js(js_str)

    def set_marker_icon(self, widget, myId, icon_color):
        js_str = "set_marker_icon('%s', '%s', '%s')" % (self.widget_name(widget), str(myId), str(icon_color))
        self.execute_js(js_str)

    def clear_markers(self, widget):
        js_str = "clear_markers('%s')" % self.widget_name(widget)
        # print js_str
        self.execute_js(js_str)

    def hide_markers(self, widget, hidden):
        js_str = "hide_markers('%s', %s)" % (self.widget_name(widget), "1" if hidden else "0")
        # print js_str
        ret = self.execute_js(js_str)

    # print "ret< " , ret

    def widget_name(self, widget):
        return str(widget.property("widget_name").toString())

    ####################################################
    ## Map Control
    ####################################################
    def on_map_type(self, butt):
        js_str = "set_map_type('%s')" % str(butt.text().toLower())
        self.execute_js(js_str)

    def pan_to(self, lat, lng):
        js_str = "pan_to(%s, %s)" % (lat, lng)
        self.execute_js(js_str)

    def execute_js(self, js_str):
        print "EXEC >", js_str
        self.webView.page().mainFrame().evaluateJavaScript(js_str)

    ###########################################
    ## Map Initialise
    ###########################################
    def initialize(self, geo=None):
        self.map_initialized = False
        self.webView.load(self.map_url)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.show()

    def on_initialize_progress(self, x):
        self.progress.setValue(x)

    def on_initialize_finished(self):
        self.progress.hide()

    def on_timer(self):
        if self.map_initialized:
            self.timer.stop()
            for m in self.pending_markers:
                self.add_address_marker(m[0], m[1])

    ####################################################
    ## Actions
    ####################################################
    def on_action_test_point(self):
        # print "on_action_test_point"
        self.add_marker(self.geo['lat'], self.geo['lng'])

    def on_action_move_marker(self):
        # js_str = "set_edit_mode(1)"
        self.select_marker_by_idx(self.curr_idx, True)


    def on_action_save_view(self):
        print "on_action_save_view"
        view = self.webView.get_view();
        res = QtGui.QMessageBox.question(self, "Save", "Save Current View", "no", "Yes")
        if res == 1:
            view = self.webView.get_view();

    def get_map_view(self):
        js_str = "current_view()"
        return self.execute_js()

    ####################################################
    ## Edit Mode
    ####################################################
    def on_edit_mode(self, butt):
        print "butt=", butt.text()
        self.edit_mode = True if butt.text() == "Edit Mode" else False
        js_str = "set_edit_mode(%s)" % ("1" if self.edit_mode else "0")
        self.execute_js(js_str)
        print js_str
        self.buttonSave.setEnabled(self.edit_mode)
        for b in self.groupEditMode.buttons():
            if b.text() == butt.text():
                ico = dIco.Yellow
            else:
                ico = dIco.Black
            b.setIcon(dIco.icon(ico))
        print "--- <<<"

    def on_save_button(self):
        print "save"

    def on_map_view(self):
        print "on_map_view"


    def load_document(self, ogtDoc):

        self.ogtDoc = ogtDoc

        points =  self.ogtDoc.get_points()
        print points
        for idx, p in enumerate(points):
            self.add_marker("xmap", id="ID_%s" % idx, lat=p['lat'], lon=p['lon'])


class MapZoomWidget:
    """Zoom Helper Class.
      - Helps with map level zoom handling
      - Iniial zoom levels are Roof, street, Local, Area, Uk

    @todo: make zoom levels constants
    """

    def __init__(self):

        self.i_levels = {}
        self.labels = {}
        for level in [[19, 'Roof'], [17, 'Street'], [14, 'Local'], [8, 'Area'], [6, 'Uk']]:
            self.add_level(level[0], level[1])

    def add_level(self, level, label):
        self.i_levels[label] = level
        self.labels[level] = label

    def level(self, label=None):
        if label == None:
            label = 'Local'
        return self.i_levels[label]

    def levels(self):
        levels = self.labels.keys()
        levels.sort(reverse=True)
        ret_list = []
        for level in levels:
            ret_list.append([self.labels[level], level])
        return ret_list

    def make_menu(self, parent, menu, callback):
        zoomMenu = menu.addMenu("Zoom to")
        groupZoomLevels = QtGui.QActionGroup(parent)
        parent.connect(groupZoomLevels, QtCore.SIGNAL("selected(QAction *)"), callback)  # self.on_zoom_action)
        for z in self.levels():
            act = zoomMenu.addAction(z[0])
            act.setProperty("zoom", QtCore.QVariant(z[1]))
            groupZoomLevels.addAction(act)



