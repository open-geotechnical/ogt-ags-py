# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

from Qt import QtGui, QtCore, Qt, pyqtSignal

from ogt import ags4

import app_globals as G

#from ogt import utils
from img import Ico
import xwidgets
from ags4_models import CG, CH,CA, SHOW_NONE, AGS4_COLORS


class AGS4DataDictBrowser( QtGui.QWidget ):

    def __init__( self, parent=None, mode=None ):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        ##=============================================================
        self.tabWidget = QtGui.QTabWidget()
        self.mainLayout.addWidget(self.tabWidget)


        ##=============================================================
        self.agsGroupsWidget = AGS4GroupsBrowser(self)
        self.tabWidget.addTab(self.agsGroupsWidget, Ico.icon(Ico.AgsGroups), "Groups")

        self.unitsTypesWidget = AGS4UnitsTypesWidget(self)
        self.tabWidget.addTab(self.unitsTypesWidget, Ico.icon(Ico.AgsGroups), "Units && Types")

        ##=============================================================
        #self.agsAbbrevsWidget = AgsAbbrevsWidget.AgsAbbrevsWidget(self)
        #self.tabWidget.addTab(self.agsAbbrevsWidget,dIco.icon(dIco.AgsAbbrevs),  "Abbreviations / Pick lists")

        ##=============================================================
        #self.agsUnitsWidget = AgsUnitsWidget.AgsUnitsWidget(self)
        #self.tabWidget.addTab(self.agsUnitsWidget, dIco.icon(dIco.AgsUnits), "Units")


    def init_load(self):

        # load data dict
        G.ags.init_load()
        #self.tabWidget.setCurrentIndex(1)

        self.agsGroupsWidget.set_focus()


class AGS4GroupsBrowser( QtGui.QWidget ):
    """The left panel with the classes, search and groups view"""

    sigGroupSelected = pyqtSignal(object)

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.setObjectName("AGS4GroupsBrowser")

        self.proxy = QtGui.QSortFilterProxyModel()
        self.proxy.setSourceModel(G.ags.modelGroups)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)


        ##===============================================
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.splitter = QtGui.QSplitter(self)
        self.splitter.setObjectName(self.objectName() + "groups_splitter")
        self.mainLayout.addWidget(self.splitter)

        ##############################################################################
        leftWidget = QtGui.QWidget()
        leftLayout = xwidgets.vlayout()
        leftWidget.setLayout(leftLayout)
        self.splitter.addWidget(leftWidget)

        ##================================
        ## Filter
        grpFilter = xwidgets.GroupHBox("Filter by")
        mmm = 5
        grpFilter.setContentsMargins(mmm, mmm, mmm, mmm)
        # grpFilter.grid.setSpacing(5)
        # grpFilter.setFixedWidth(150)
        leftLayout.addWidget(grpFilter)

        # filter combo
        self.comboSearchFor = QtGui.QComboBox()
        grpFilter.addWidget(self.comboSearchFor)

        self.comboSearchFor.addItem("Code", CG.code)
        self.comboSearchFor.addItem("Description", CG.description)
        self.comboSearchFor.addItem("Code + Description", CG.search)
        self.comboSearchFor.setMaximumWidth(150)
        # clear button
        self.buttClear = xwidgets.ClearButton(self, callback=self.on_clear_filter)
        grpFilter.addWidget(self.buttClear)

        ## filter text
        self.txtFilter = QtGui.QLineEdit()
        self.txtFilter.setMaximumWidth(100)
        grpFilter.addWidget(self.txtFilter, )
        self.txtFilter.textChanged.connect(self.on_txt_changed)

        grpFilter.layout.addStretch(3)

        ##================================
        ## Classification Tree
        topLayout = QtGui.QVBoxLayout()
        leftLayout.addLayout(topLayout, 0)
        self.treeClass = QtGui.QTreeView()
        topLayout.addWidget(self.treeClass, 3)
        self.treeClass.setModel(G.ags.modelClasses)
        self.treeClass.setRootIsDecorated(False)

        self.treeClass.setExpandsOnDoubleClick(False)

        self.treeClass.setFixedHeight(250)

        self.treeClass.selectionModel().selectionChanged.connect(self.on_class_tree_selected)




        ##===============================================
        self.tree = QtGui.QTreeView()
        leftLayout.addWidget(self.tree, 10)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.setModel(self.proxy)
        self.tree.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.tree.header().setStretchLastSection(True)
        for c in [CG.search, CG.x_id]:
            self.tree.setColumnHidden(c, True)

        self.tree.setColumnWidth(CG.code, 120)
        self.tree.setColumnWidth(CG.description, 250)

        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.selectionModel().selectionChanged.connect(self.on_groups_tree_selected)

        self.tree.sortByColumn(CG.code)


        self.agsGroupViewWidget = AGS4GroupViewWidget(self)
        self.splitter.addWidget(self.agsGroupViewWidget)

        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 5)
        G.settings.restore_splitter(self.splitter)
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

        #self.statusBar = QtGui.QStatusBar()
        #self.mainLayout.addWidget(self.statusBar, 0)


        ##############################################################################
        rightWidget = QtGui.QWidget()
        rightLayout = xwidgets.vlayout()
        rightWidget.setLayout(rightLayout)
        self.splitter.addWidget(rightWidget)


        self.agsHeadingDetailWidget = AGS4HeadingDetailWidget()
        rightLayout.addWidget(self.agsHeadingDetailWidget)

        #self.init_setup()
        G.ags.sigLoaded.connect(self.on_loaded)
        self.agsGroupViewWidget.sigHeadCodeSelected.connect(self.agsHeadingDetailWidget.load_heading)

    def on_splitter_moved(self, i, pos):
        G.settings.save_splitter(self.splitter)

    def set_focus(self):
        self.txtFilter.setFocus()


    def init(self):
        print "init", self

    def on_proxy_changed(self, tl, br):
        print "changes", tl, br

    #=========================================
    def on_groups_tree_selected(self, sel=None, desel=None):

        if not self.tree.selectionModel().hasSelection():
             self.agsGroupViewWidget.load_group( None )
             self.sigGroupSelected.emit( None )
             return

        selidx = sel.indexes()[0]
        srcidx = self.proxy.mapToSource(selidx)

        model = self.proxy.sourceModel()
        tIdx = model.index(srcidx.row(), CG.code, srcidx.parent())
        item = model.itemFromIndex( tIdx )

        group_code = str(item.text())
        self.agsGroupViewWidget.load_group(group_code)
        self.sigGroupSelected.emit( group_code )


    def on_filter_col(self, idx):
        self.update_filter()
        self.txtCode.setFocus()

    def on_txt_changed(self, x):
        self.update_filter()

    def update_filter(self):
        self.treeClass.blockSignals(True)
        self.treeClass.clearSelection()
        self.treeClass.blockSignals(False)

        cidx = self.comboSearchFor.itemData(self.comboSearchFor.currentIndex()).toInt()[0]
        self.proxy.setFilterKeyColumn(cidx)

        txt = str(self.txtFilter.text()).strip()
        if "_" in txt:
            grp_code, _ = txt.split("_")
        else:
            grp_code = txt
        self.proxy.setFilterFixedString(grp_code)

        if self.proxy.rowCount() == 1:

            # TODO
            # #self.tree.selectionModel().select(self.proxy.index(0,0))
            pass


    def on_clear_filter(self):
        self.txtCode.setText("")
        self.txtCode.setFocus()



    def on_class_tree_selected(self, selected, deselected):
        if not self.treeClass.selectionModel().hasSelection():
            self.txtFilter.setFocus()
            #self.on_group_tree_selected()
            return

        self.proxy.setFilterKeyColumn(CG.cls)

        item = self.treeClass.model().itemFromIndex(selected.indexes()[0])
        if item.text() == "All":
            self.proxy.setFilterFixedString("")
        else:
            self.proxy.setFilterFixedString(item.text())
        self.txtFilter.setFocus()


    def init_load(self):
        pass

    def on_loaded(self):
        # expand first row, set sort orders
        self.treeClass.setExpanded( self.treeClass.model().item(0,0).index(), True)
        self.treeClass.sortByColumn(0, Qt.AscendingOrder)
        self.tree.sortByColumn(CG.code, Qt.AscendingOrder)

        self.tree.resizeColumnToContents(CG.code)



class AGS4GroupViewWidget( QtGui.QWidget ):
    """The GroupView contains the vertically the Group Label at top, headings and notes"""

    sigHeadCodeSelected = pyqtSignal(object)

    def __init__( self, parent=None, mode=None ):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True

        self.cache = None

        self.group_by = "none"

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.toolbar = xwidgets.hlayout()
        self.mainLayout.addLayout(self.toolbar, 0)

        self.icoLabel = xwidgets.IconLabel(self, ico=Ico.AgsGroup)
        self.icoLabel.setStyleSheet("background-color: white; color: #444444;")
        self.toolbar.addWidget(self.icoLabel)

        self.lblGroupCode = QtGui.QLabel(" ")
        self.lblGroupCode.setStyleSheet("background-color: white; color: %s; font-weight: bold; font-family: monospace; padding: 3px;" % AGS4_COLORS.group)
        self.toolbar.addWidget(self.lblGroupCode, 1)
        self.lblGroupCode.setFixedWidth(50)

        self.lblDescription = QtGui.QLabel(" ")
        self.lblDescription.setStyleSheet("background-color: white; color: #444444;")
        self.toolbar.addWidget(self.lblDescription, 3)

        self.mainLayout.addSpacing(10)

        #self.tabWidget = QtGui.QTabWidget()
        #self.mainLayout.addWidget(self.tabWidget)

        #self.lblHeadings = Widgets.Label(text="Headings")
        #self.mainLayout.addWidget(self.lblHeadings, 0)



        self.agsHeadingsTable = AGS4HeadingsTable(self)
        self.mainLayout.addWidget(self.agsHeadingsTable, 10)

        #self.tabWidget.addTab(self.agsHeadingsTable, dIco.icon(dIco.AgsField), "Headings")
        #self.lblNotes = Widgets.Label(text="Notes")
        #self.mainLayout.addWidget(self.lblNotes, 0)


        self.agsGroupNotesTable = AGS4GroupNotesTable(self)
        self.agsGroupNotesTable.setFixedHeight(200)
        self.mainLayout.addWidget(self.agsGroupNotesTable)
        #self.tabWidget.addTab(self.agsGroupNotesTable, dIco.icon(dIco.AgsNotes), "Notes")
        #self.connect(self.agsGroupNotesTable, QtCore.SIGNAL("loaded"), self.on_notes_loaded)

        self.agsHeadingsTable.sigHeadCodeSelected.connect(self.on_head_code)

    def on_head_code(self, head_code):
        self.sigHeadCodeSelected.emit(head_code)

    def on_notes_loaded(self, c):
        self.tabWidget.setTabText(1, "Notes - %s" % (c if c > 0 else "None") )

    def clear(self):
        self.lblGroupCode.setText("")
        self.lblDescription.setText("")
        self.agsGroupNotesTable.clear()

    def load_group(self, group_code):

        if group_code == None:
            self.agsHeadingsTable.filter_by_group(None)
            self.lblGroupCode.setText("")
            self.lblDescription.setText("")
            return


        g = G.ags.get_group(group_code)
        if g == None:
            # not found..
            g = dict(group_code=group_code, group_description="`%s` group not found" % group_code)

        self.lblGroupCode.setText(g['group_code'])
        self.lblDescription.setText(g['group_description'])

        if False:
            self.tabWidget.setTabText(0, "Headings - %s" % len(g['headings']))
            if len(g['notes']) == 0:
                s = "None"
            else:
                s = len(g['notes'])
            self.tabWidget.setTabText(1, "Notes - %s" % s)

        self.agsHeadingsTable.filter_by_group(g['group_code'])
        self.agsGroupNotesTable.load_notes(g['group_code'])



class AGS4GroupViewDialog(QtGui.QDialog):


    def __init__(self, parent=None, group_code=None):
        QtGui.QDialog.__init__(self, parent)


        self.setWindowTitle(group_code)
        self.setWindowIcon(Ico.icon(Ico.Ags4))


        self.setMinimumWidth(1100)



        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.setSpacing(0)
        margarine = 0
        self.mainLayout.setContentsMargins(margarine, margarine, margarine, margarine)
        self.setLayout(self.mainLayout)

        self.groupViewWidget = AGS4GroupViewWidget(self)
        self.mainLayout.addWidget(self.groupViewWidget)
        self.groupViewWidget.load_group(group_code)



class AGS4HeadingsTable( QtGui.QWidget ):

    sigHeadCodeSelected = pyqtSignal(object)
    """A row has been selected or delelected

    :return: HeadCode or `None`
    """



    def __init__( self, parent ):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True
        self.group_code = None
        self.cache = None

        self.proxy = QtGui.QSortFilterProxyModel()
        self.proxy.setSourceModel(G.ags.modelHeadings)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(CH.group_code)
        self.proxy.setFilterFixedString(SHOW_NONE)


        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        ##===============================================================
        self.tree = QtGui.QTreeView()
        self.mainLayout.addWidget(self.tree)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)

        self.tree.setModel(self.proxy)


        for c in [CH.class_, CH.group_code, CH.group_descr]:
           self.tree.setColumnHidden(c, True)
        self.tree.setColumnWidth(CH.sort, 20)
        self.tree.setColumnWidth(CH.head_code, 100)
        self.tree.setColumnWidth(CH.unit, 50)
        self.tree.setColumnWidth(CH.status, 40)
        self.tree.setColumnWidth(CH.data_type, 50)

        self.tree.header().setStretchLastSection(True)

        self.tree.setSortingEnabled(True)

        self.tree.selectionModel().selectionChanged.connect(self.on_tree_selected)

        #self.statusBar = StatusBar(self, True)
        #self.mainLayout.addWidget(self.statusBar, 0)
        #self.statusBar.hide()




    def filter_by_group(self, gc=None):

        self.group_code = SHOW_NONE if gc == None else gc
        self.proxy.setFilterFixedString(self.group_code)

    #=========================================
    def on_tree_selected(self, sel, desel):

        if not self.tree.selectionModel().hasSelection():
             self.sigHeadCodeSelected.emit( None )
             return

        selidx = sel.indexes()[0]
        srcidx = self.proxy.mapToSource(selidx)

        model = self.proxy.sourceModel()
        tIdx = model.index(srcidx.row(), CH.head_code, srcidx.parent())
        item = model.itemFromIndex( tIdx )

        head_code = str(item.text())
        self.sigHeadCodeSelected.emit(head_code)



    def on_tree_context_menu(self, point):

        if not self.tree.selectionModel().hasSelection():
            return

    def deadon_butt_pop(self, butt):
        code =  str(butt.property("code").toString())

        p = self.mapFromGlobal(QtGui.QCursor.pos())
        #print p
        p = QtGui.QCursor.pos()
        d = ags.AgsAbbrevPopDialog.AgsAbbrevPopDialog(self, abrev_code=code)

        d.move(p.x() - 50, 100)
        d.exec_()


class CN:
    node = 0
    note_id = 1
    so = 2


class AGS4GroupNotesTable( QtGui.QWidget ):

    sigLoaded = pyqtSignal(int, object)

    def __init__( self, parent, mode=None ):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True

        self.cache = None

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        ##==============================
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidgetResizable(True)
        self.mainLayout.addWidget(scrollArea, 100)

        self.scrollWidget = QtGui.QWidget()
        #self.mainLayout.addWidget(self.noticesListWidget, 100)
        scrollArea.setWidget(self.scrollWidget)

        self.scrollLayout = QtGui.QVBoxLayout()
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)
        self.scrollWidget.setLayout(self.scrollLayout)



    def clear(self):
        """Removes all QLabel entries"""
        ## pain.. all this shite just to nuke a list
        self.setUpdatesEnabled(False)
        while self.scrollLayout.count() > 0:
            vari = self.scrollLayout.itemAt(0)
            w = vari.widget()
            if w:
                self.scrollLayout.removeWidget( w )
                w.setParent(None)
                w = None
            else:
                self.scrollLayout.removeItem( vari )

        self.setUpdatesEnabled(True)
        self.update()



    def load_notes(self, group_code):
        """Loads group notes

        :param group_code: The four character group code

        """
        lookup = G.ags.get_words()


        self.clear()
        notes = G.ags.get_notes(group_code)
        #print notes

        if notes == None:
            return

        self.setUpdatesEnabled(False)
        for note in notes:

            w = widget = QtGui.QLabel()

            words = note.split(" ")
            res = []
            for word in words:
                #print word
                if word in lookup:
                    res.append("<a href='#%s-%s'>%s</a>" % (lookup[word]['type'], word, word))
                else:
                    res.append(word)

            widget.setText(" ".join(res))
            widget.setTextFormat(QtCore.Qt.RichText)
            widget.setWordWrap(True)
            widget.setMargin(0)
            widget.setStyleSheet("background-color: #C3F6A9; padding: 2px; margin: 0; border-bottom:1px solid #dddddd;")
            widget.setAlignment(QtCore.Qt.AlignTop)

            self.scrollLayout.addWidget(w, 0)
            self.connect(widget, QtCore.SIGNAL("linkHovered(const QString)"), self.on_link_hover)

        #if len(notes) < 4:
        self.scrollLayout.addStretch(10)
        self.setUpdatesEnabled(True)

        self.sigLoaded.emit(len(notes), self)
        #self.emit(QtCore.SIGNAL("loaded"), len(notes), self)

    def on_link_hover(self, lnk):
        #print "link=", lnk
        #self.statusBar.showMessage(lnk)
        print "TODO"

    def on_tree_context_menu(self, point):

        if not self.tree.selectionModel().hasSelection():
            return




class AGS4HeadingDetailWidget( QtGui.QWidget ):
    """Shows details about a heading, including example, etc"""

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = True

        self.proxy = QtGui.QSortFilterProxyModel()
        self.proxy.setSourceModel(G.ags.modelAbbrItems)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(CA.head_code)
        self.proxy.setFilterFixedString(SHOW_NONE)

        ##===============================================
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        self.toolbar = xwidgets.hlayout()
        self.mainLayout.addLayout(self.toolbar, 0)

        self.icoLabel = xwidgets.IconLabel(self, ico=Ico.AgsGroup)
        self.icoLabel.setStyleSheet("background-color: white; color: #444444;")
        self.toolbar.addWidget(self.icoLabel, 0)

        self.lblAbbrCode = QtGui.QLabel(" ")
        self.lblAbbrCode.setStyleSheet("background-color: white; color: %s; font-weight: bold; font-family: monospace; padding: 3px;" % AGS4_COLORS.group)
        self.toolbar.addWidget(self.lblAbbrCode, 20)
        #self.lblAbbrCode.setFixedWidth(50)


        self.splitter = QtGui.QSplitter()
        self.mainLayout.addWidget(self.splitter)

        ##===============================================================
        self.tree = QtGui.QTreeView()
        self.mainLayout.addWidget(self.tree)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)

        self.tree.setModel(self.proxy)


        for c in [CA.head_code]:
            self.tree.setColumnHidden(c, True)
        self.tree.setColumnWidth(CA.code, 100)
        self.tree.setColumnWidth(CA.description, 50)
        self.tree.setColumnWidth(CA.head_code, 40)


        self.tree.header().setStretchLastSection(True)

        # TODO fix sort to ags
        self.tree.setSortingEnabled(True)

        self.load_heading(None)


    def load_heading(self, head_code):

        self.proxy.setFilterFixedString(SHOW_NONE if head_code == None else head_code)

        # now check rowCount() to see if records
        # FIXME we need to check for PA, P? instead
        dis = self.proxy.rowCount() == 0
        self.lblAbbrCode.setText("" if dis else head_code)
        self.setDisabled(dis)

class PickListComboDelegate(QtGui.QItemDelegate):
    """A combobox for a table that whos the abrreviations picklist"""
    def __init__(self, parent, heading):
        QtGui.QItemDelegate.__init__(self, parent)

        self.ogtHeading = heading

    def createEditor(self, parent, option, index):

        editor = QtGui.QComboBox(parent)
        editor.addItem("--unknown--", "")

        # populate combobox from abbreviations
        for typ in ags4.AGS4.picklist(self.ogtHeading.head_code):
            editor.addItem( "%s: %s " % (typ['code'], typ['description']), typ['code'])

        return editor

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        curr = index.model().data(index).toString()
        idx = editor.findData(curr)
        if idx != -1:
            editor.setCurrentIndex(idx)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        txt = editor.itemData(editor.currentIndex()).toString()
        model.setData(index, txt)

class NumberEditDelegate(QtGui.QItemDelegate):
    """Number editor to n decimal places"""
    def __init__(self, parent, heading):
        QtGui.QItemDelegate.__init__(self, parent)

        self.ogtHeading = heading

        ##self.data_type = heading['type']
        #self.data_type = heading['type']
        self.dp = None
        if self.ogtHeading.type.endswith("DP"):
            self.dp = int(self.ogtHeading.type[:-2])

    def createEditor(self, parent, option, index):

        editor = QtGui.QLineEdit(parent)
        if self.ogtHeading.type.endswith("DP"):
            validator = QtGui.QDoubleValidator()
            validator.setDecimals(self.dp)
            editor.setValidator(validator)

        return editor

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        curr = index.model().data(index) #.toString()
        editor.setText(curr)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        no = float(editor.text())
        f = "%01."
        f += "%sf" % self.dp
        #print f
        txt = f % (no,)
        model.setData(index, txt)

class IDComboDelegate(QtGui.QItemDelegate):
    """A combobox for the ID"""
    def __init__(self, parent, heading, options):
        QtGui.QItemDelegate.__init__(self, parent)

        self.ogtHeading = heading
        self.options = options

    def createEditor(self, parent, option, index):

        editor = QtGui.QComboBox(parent)
        editor.addItem("--unknown--", "")

        # populate combobox from abbreviations
        for v in self.options:
            editor.addItem( "%s" % v, "%s" % v)

        return editor

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        curr = index.model().data(index).toString()
        idx = editor.findData(curr)
        if idx != -1:
            editor.setCurrentIndex(idx)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        txt = editor.itemData(editor.currentIndex()).toString()
        model.setData(index, txt)

class AGS4UnitsTypesWidget( QtGui.QWidget ):
    """The Units and Types tab"""

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False
        self.setObjectName("AGS4UnitTypesWidget")


        self.proxyUnits = QtGui.QSortFilterProxyModel()
        self.proxyUnits.setSourceModel(G.ags.modelUnits)
        self.proxyUnits.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.proxyTypes = QtGui.QSortFilterProxyModel()
        self.proxyTypes.setSourceModel(G.ags.modelTypes)
        self.proxyTypes.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        ##===============================================
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.splitter = QtGui.QSplitter()
        self.mainLayout.addWidget(self.splitter)

        self.treeUnits = self.make_tree(self.proxyUnits, "Unit", "Description")
        self.splitter.addWidget(self.treeUnits)

        self.treeTypes = self.make_tree(self.proxyTypes, "Type", "Description")
        self.splitter.addWidget(self.treeTypes)


    def make_tree(self, model, tit1, tit2):
        tree = QtGui.QTreeView()
        tree.setRootIsDecorated(False)
        tree.setSortingEnabled(True)
        tree.setModel(model)
        return tree
        hi = tree.headerItem()
        hi.setText(0, tit1)
        hi.setText(1, tit2)
        return tree
