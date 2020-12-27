#!/usr/bin/env python3

# ABOUT
# Artisan Sustainability Dialog

# LICENSE
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later versison. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

# AUTHOR
# Dave Baxter & Marko Luther, 2020

import sys
import math
import platform
import prettytable

# import artisan.plus module
import plus.config  # @UnusedImport
import plus.util

from artisanlib.suppress_errors import suppress_stdout_stderr
from artisanlib.util import stringfromseconds,stringtoseconds, toInt
from artisanlib.dialogs import ArtisanResizeablDialog
from artisanlib.widgets import MyQComboBox
from help import sustainability_help

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRegularExpression, QSettings, QTimer, QEvent
from PyQt5.QtGui import QColor, QIntValidator, QRegularExpressionValidator, QKeySequence, QPalette
from PyQt5.QtWidgets import (QApplication, QWidget, QCheckBox, QComboBox, QDialogButtonBox, QGridLayout,
                             QHBoxLayout, QVBoxLayout, QHeaderView, QLabel, QLineEdit, QTextEdit, QListView, 
                             QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QTabWidget, QSizePolicy,
                             QGroupBox)
                             
if sys.platform.startswith("darwin"):
    import darkdetect # @UnresolvedImport


########################################################################################
#####################  Sustainability Dialog  ##########################################

class sustainabilityDlg(ArtisanResizeablDialog):

    def __init__(self, parent = None, aw = None, activeTab = 0):
        super(sustainabilityDlg,self).__init__(parent, aw)
        self.setModal(True)
        self.setWindowTitle(QApplication.translate("Form Caption","Sustainability",None))
        
        self.helpdialog = None
        self.wasDirty = self.aw.qmc.safesaveflag
        
        # remember parameters to enable a Cancel action
        self.org_roaster = self.aw.qmc.roastertype  #dave likely to become read-only and can be removed

        self.org_burnerrating = self.aw.qmc.burnerrating       
        self.org_burner_etype = self.aw.qmc.burner_etype       
        self.org_btu_betweenbatch = self.aw.qmc.btu_betweenbatch   
        self.org_btu_warmup = self.aw.qmc.btu_warmup
        self.org_ratingunit = self.aw.qmc.ratingunit
        self.org_fueltype = self.aw.qmc.fueltype
        self.org_burnerevent_zeropct= self.aw.qmc.burnerevent_zeropct
        self.org_burnerevent_hundpct = self.aw.qmc.burnerevent_hundpct
        self.org_roasts_per_session = self.aw.qmc.roasts_per_session
        self.loadsustainabilityfromprofile = self.aw.qmc.loadsustainabilityfromprofile
        
        # connect the ArtisanDialog standard OK/Cancel buttons
        self.dialogbuttons.accepted.connect(self.accept)
        self.dialogbuttons.rejected.connect(self.cancel_dialog)
        self.helpButton = self.dialogbuttons.addButton(QDialogButtonBox.Help)
        self.dialogbuttons.button(QDialogButtonBox.Help).clicked.connect(self.showsustainabilityhelp)

        okLayout = QHBoxLayout()
        okLayout.addStretch()
        okLayout.addWidget(self.dialogbuttons)
        okLayout.setSpacing(10)
        okLayout.setContentsMargins(5, 15, 5, 15) # left, top, right, bottom
        
        #DATA Table
        self.datatable = QTableWidget()
        self.datatable.setTabKeyNavigation(True)
        self.copydataTableButton = QPushButton(QApplication.translate("Button", "Copy Table",None))
        self.copydataTableButton.setToolTip(QApplication.translate("Tooltip","Copy table to clipboard, OPTION or ALT click for tabular text",None))
        self.copydataTableButton.setFocusPolicy(Qt.NoFocus)
        self.copydataTableButton.setMaximumSize(self.copydataTableButton.sizeHint())
        self.copydataTableButton.setMinimumSize(self.copydataTableButton.minimumSizeHint())
        self.copydataTableButton.clicked.connect(self.copyDataTabletoClipboard)

        databuttonLayout = QHBoxLayout()
        databuttonLayout.addWidget(self.copydataTableButton)
        databuttonLayout.addStretch()


        self.loadSustainabilityFromProfile = QCheckBox(QApplication.translate("CheckBox", "Load from profile",None))
        self.loadSustainabilityFromProfile.setChecked(self.aw.qmc.loadsustainabilityfromprofile)

        
        #metrics
        self.metricsLabel = QLabel()
        self.updateMetricsLabel()


        g0Layout = QVBoxLayout()
        g0Layout.addWidget(self.metricsLabel)
        g0GroupBox = QGroupBox(QApplication.translate("GroupBox","Sustainability metrics",None))
        g0GroupBox.setLayout(g0Layout)


        #roaster
        roasterLabel = QLabel(QApplication.translate("Label","Roaster",None))
        self.roaster = QLineEdit(self.aw.qmc.roastertype)
        self.roaster.editingFinished.connect(self.roaster_editingfinished)  #dave likely to become read-only

        roasterLayout = QHBoxLayout()
        roasterLayout.addWidget(roasterLabel)
        roasterLayout.addWidget(self.roaster)
        roasterLayout.addStretch()
                
        #burner rating
        burnerratingLabel = QLabel(QApplication.translate("Label","Burner Rating",None))
        self.burnerrating = QLineEdit(str(self.aw.qmc.burnerrating))
        self.burnerrating.setAlignment(Qt.AlignRight)
        self.burnerrating.editingFinished.connect(self.burnerrating_editingfinished)
  
        #unit
        #ratingunitLabel = QLabel(QApplication.translate("Label","Unit",None))
        self.ratingunitComboBox = QComboBox()
        self.ratingunitComboBox.addItems(self.aw.qmc.heatunits)
        self.ratingunitComboBox.setCurrentIndex(self.aw.qmc.heatunits.index(self.aw.qmc.ratingunit))
        self.ratingunitComboBox.currentIndexChanged.connect(self.combobox_currentindexchanged)
        
        burnerratingLayout = QHBoxLayout()
        burnerratingLayout.addWidget(burnerratingLabel)
        burnerratingLayout.addWidget(self.burnerrating)
        burnerratingLayout.addWidget(self.ratingunitComboBox)
        burnerratingLayout.addStretch()

        #fuel type        
        fueltypeLabel = QLabel(QApplication.translate("Label","Fuel Type",None))
        self.fueltypeComboBox = QComboBox()
        self.fueltypeComboBox.addItems(self.aw.qmc.fueltypes)
        self.fueltypeComboBox.setCurrentIndex(self.aw.qmc.fueltypes.index(self.aw.qmc.fueltype))
        self.fueltypeComboBox.currentIndexChanged.connect(self.combobox_currentindexchanged)
        
        fueltypeLayout = QHBoxLayout()
        fueltypeLayout.addWidget(fueltypeLabel)
        fueltypeLayout.addWidget(self.fueltypeComboBox)
        fueltypeLayout.addStretch()

        #burner event
        burnereventLabel = QLabel(QApplication.translate("Label","Burner Event",None))
        self.burnereventComboBox = QComboBox()
        self.burnereventComboBox.addItems(self.aw.qmc.etypes[0:4])
        self.burnereventComboBox.setCurrentIndex(self.aw.qmc.burner_etype)
        self.burnereventComboBox.currentIndexChanged.connect(self.combobox_currentindexchanged)
        
        burnerevent_zeropctLabel = QLabel(QApplication.translate("Label","0% Value",None))
        self.burnerevent_zeropctEdit = QLineEdit(str(self.aw.qmc.burnerevent_zeropct))
        self.burnerevent_zeropctEdit.setAlignment(Qt.AlignRight)
        self.burnerevent_zeropctEdit.editingFinished.connect(self.burnereventzeropct_editingfinished)        
        
        burnerevent_hundpctLabel = QLabel(QApplication.translate("Label","100% Value",None))
        self.burnerevent_hundpctEdit = QLineEdit(str(self.aw.qmc.burnerevent_hundpct))
        self.burnerevent_hundpctEdit.setAlignment(Qt.AlignRight)
        self.burnerevent_hundpctEdit.editingFinished.connect(self.burnereventhundpct_editingfinished)        
        
        burnereventLayout = QHBoxLayout()
        burnereventLayout.addWidget(burnereventLabel)
        burnereventLayout.addWidget(self.burnereventComboBox)
        burnereventLayout.addWidget(burnerevent_zeropctLabel)
        burnereventLayout.addWidget(self.burnerevent_zeropctEdit)
        burnereventLayout.addWidget(burnerevent_hundpctLabel)
        burnereventLayout.addWidget(self.burnerevent_hundpctEdit)
        burnereventLayout.addStretch()
        
        btu_betweenbatchLabel = QLabel(QApplication.translate("Label","BTUs used for\nbetween batch protocol",None))
        self.btu_betweenbatchEdit = QLineEdit(str(self.aw.qmc.btu_betweenbatch))
        self.btu_betweenbatchEdit.setAlignment(Qt.AlignRight)
        self.btu_betweenbatchEdit.editingFinished.connect(self.btu_betweenbatchEdit_editingfinished)
        
        btu_betweenbatchLayout = QHBoxLayout()
        btu_betweenbatchLayout.addWidget(btu_betweenbatchLabel)
        btu_betweenbatchLayout.addWidget(self.btu_betweenbatchEdit)
        btu_betweenbatchLayout.addStretch()

        btu_warmupLabel = QLabel(QApplication.translate("Label","BTUs used for\nroaster warm up",None))
        self.btu_warmupEdit = QLineEdit(str(self.aw.qmc.btu_warmup))
        self.btu_warmupEdit.setAlignment(Qt.AlignRight)
        self.btu_warmupEdit.editingFinished.connect(self.btu_warmupEdit_editingfinished)
        
        roastpersessionLabel = QLabel(QApplication.translate("Label","Typical number of\nroasts per session",None))
        self.roastpersessionSpin = QSpinBox()
        self.roastpersessionSpin.setSingleStep(1)
        self.roastpersessionSpin.setRange(1,999)
        self.roastpersessionSpin.setAlignment(Qt.AlignRight)
        self.roastpersessionSpin.setValue(self.aw.qmc.roasts_per_session)
        self.roastpersessionSpin.editingFinished.connect(self.roastpersessionSpin_editingfinished)
        
        btu_warmupLayout = QHBoxLayout()
        btu_warmupLayout.addWidget(btu_warmupLabel)
        btu_warmupLayout.addWidget(self.btu_warmupEdit)
        btu_warmupLayout.addStretch()
        
        roastpersessionLayout = QHBoxLayout()
        roastpersessionLayout.addWidget(roastpersessionLabel)
        roastpersessionLayout.addWidget(self.roastpersessionSpin)
        roastpersessionLayout.addStretch()


        g1Layout = QVBoxLayout()
        g1Layout.addLayout(roasterLayout)
        g1Layout.addLayout(burnerratingLayout)
        g1Layout.addLayout(fueltypeLayout)
        g1Layout.addLayout(burnereventLayout)
        self.roasterspecs = QGroupBox(QApplication.translate("GroupBox","Roaster Information",None))
        self.roasterspecs.setLayout(g1Layout)
        
        g2Layout = QVBoxLayout()
        g2Layout.addLayout(btu_betweenbatchLayout)
        g2Layout.addLayout(btu_warmupLayout)
        g2Layout.addLayout(roastpersessionLayout)
        self.typicaluse = QGroupBox(QApplication.translate("GroupBox","Typical Usage",None))
        self.typicaluse.setLayout(g2Layout)



        #tab 1
        tab1Layout = QVBoxLayout()
        tab1Layout.setContentsMargins(5, 5, 5, 5) # left, top, right, bottom
        tab1Layout.addWidget(self.roasterspecs)
        tab1Layout.addWidget(self.typicaluse)
        tab1Layout.addStretch()
        tab1Layout.setSpacing(0)
#        tab1Layout.addStretch()

#        #tab 2
        tab2Layout = QVBoxLayout()
        tab2Layout.addWidget(self.datatable) 
        tab2Layout.addLayout(databuttonLayout)
        tab2Layout.setContentsMargins(5, 5, 5, 5) # left, top, right, bottom 

        #tabwidget
        self.TabWidget = QTabWidget()
        self.TabWidget.setContentsMargins(0,0,0,0)
        Tab1Widget = QWidget()
        Tab1Widget.setLayout(tab1Layout)
        self.TabWidget.addTab(Tab1Widget,QApplication.translate("Tab", "Settings",None))
 
        Tab2Widget = QWidget()
        Tab2Widget.setLayout(tab2Layout)
        self.TabWidget.addTab(Tab2Widget,QApplication.translate("Tab", "Detail",None)) 
        self.TabWidget.currentChanged.connect(self.tabSwitched)

        #full dialog layout
        layout = QVBoxLayout()
        layout.addWidget(g0GroupBox)
        layout.addStretch()
        layout.addWidget(self.TabWidget)
        layout.addWidget(self.loadSustainabilityFromProfile)
        layout.addLayout(okLayout)
        layout.setContentsMargins(10,10,10,0)
        layout.setSpacing(5)
        self.setLayout(layout)
        
        self.TabWidget.setCurrentIndex(activeTab)

        settings = QSettings()
        if settings.contains("SustainabiltyGeometry"):
            self.restoreGeometry(settings.value("SustainabiltyGeometry"))
        else:
            self.resize(self.minimumSizeHint())
   
    
    @pyqtSlot()
    def roaster_editingfinished(self):
        self.aw.qmc.fileDirty()

    @pyqtSlot()
    def burnerrating_editingfinished(self):
        self.burnerrating.setText(str(abs(toInt(self.aw.comma2dot(str(self.burnerrating.text()))))))
        self.updateAll()
        self.aw.qmc.fileDirty()

    @pyqtSlot()
    def btu_betweenbatchEdit_editingfinished(self):
        self.btu_betweenbatchEdit.setText(str(abs(toInt(self.aw.comma2dot(str(self.btu_betweenbatchEdit.text()))))))
        self.updateAll()
        self.aw.qmc.fileDirty()

    @pyqtSlot()
    def btu_warmupEdit_editingfinished(self):
        self.btu_warmupEdit.setText(str(abs(toInt(self.aw.comma2dot(str(self.btu_warmupEdit.text()))))))
        self.updateAll()
        self.aw.qmc.fileDirty()

    @pyqtSlot()
    def roastpersessionSpin_editingfinished(self):
        self.updateAll()
        self.aw.qmc.fileDirty()

    @pyqtSlot()
    def combobox_currentindexchanged(self):
        self.updateAll()
        self.aw.qmc.fileDirty()

    @pyqtSlot()
    def burnereventzeropct_editingfinished(self):
        self.burnerevent_zeropctEdit.setText(str(abs(toInt(self.aw.comma2dot(str(self.burnerevent_zeropctEdit.text()))))))
        self.burnereventpct_editingfinished("zero")

    @pyqtSlot()
    def burnereventhundpct_editingfinished(self):
        self.burnerevent_hundpctEdit.setText(str(abs(toInt(self.aw.comma2dot(str(self.burnerevent_hundpctEdit.text()))))))
        self.burnereventpct_editingfinished("hund")
        
    def burnereventpct_editingfinished(self,field):
        print("Edit finished")  #dave
        if int(self.burnerevent_zeropctEdit.text()) >= int(self.burnerevent_hundpctEdit.text()):
            self.aw.sendmessage(QApplication.translate("DAVE","The 0% value must be less than the 100% value.",None))
            QApplication.beep()
            if field == "zero":
                self.burnerevent_zeropctEdit.setText(str(int(self.burnerevent_hundpctEdit.text())-1))
            else:
                self.burnerevent_hundpctEdit.setText(str(int(self.burnerevent_zeropctEdit.text())+1))
        self.updateAll()
        self.aw.qmc.fileDirty()
        
    def updateAll(self):
        self.aw.qmc.roastertype = self.roaster.text()
        self.aw.qmc.burner_etype = self.burnereventComboBox.currentIndex()
        self.aw.qmc.burnerrating = int(self.burnerrating.text())
        self.aw.qmc.btu_betweenbatch = int(self.btu_betweenbatchEdit.text())
        self.aw.qmc.btu_warmup = int(self.btu_warmupEdit.text())
        self.aw.qmc.ratingunit = self.ratingunitComboBox.currentText()
        self.aw.qmc.fueltype = self.fueltypeComboBox.currentText()
        self.aw.qmc.burnerevent_zeropct = self.burnerevent_zeropctEdit.text()
        self.aw.qmc.burnerevent_hundpct = self.burnerevent_hundpctEdit.text()
        self.aw.qmc.roasts_per_session = int(self.roastpersessionSpin.text())
        self.aw.qmc.loadsustainabilityfromprofile = self.loadSustainabilityFromProfile.isChecked()
        self.updateMetricsLabel()

    def updateMetricsLabel(self):
        try:
            self.metrics,self.btu_list = self.aw.qmc.calcsustainability()
            metricsstr = '<font style = "color: blue; font-weight: bold;">'
            if self.metrics["BTU"] > 0:
                metricsstr += QApplication.translate("Label","Estimated heat energy used by this profile",None) + " {:.1f} BTU ".format(self.metrics["BTU"])
                if self.metrics["CO2g"] > 0:
                      metricsstr += "<br/><b>" + QApplication.translate("Label","Estimated CO2 emitted by this profile",None) + " {:.1f}g </b>".format(self.metrics["CO2g"])
                      if self.metrics["CO2g_perRoastedkg"] > 0:
                          metricsstr += "<b> {} {}g {} kG </b>".format(QApplication.translate("Label","or",None),self.metrics['CO2g_perRoastedkg'],QApplication.translate("Label","per roasted",None))
            else:
                metricsstr = "NOTHING HERE dave"
            metricsstr += "</font>"
            self.metricsLabel.setText(metricsstr)
        except:
            pass
        return metricsstr

        
    # triggered if dialog is closed via its windows close box
    # and called from accept if dialog is closed via OK
    def closeEvent(self, _):
        settings = QSettings()
        #save window geometry
        settings.setValue("SustainabiltyGeometry",self.saveGeometry())
        self.aw.sustainabilityDlg_activeTab = self.TabWidget.currentIndex()


    @pyqtSlot(int)
    def tabSwitched(self,i):
        if i == 0:
            pass
        elif i == 1:
            self.createDataTable()
            pass

    def createDataTable(self):
# Maybe should check for roast in process and show a message if that is true.
        self.datatable.clear()
        self.updateAll()
        self.metics,self.btu_list = self.aw.qmc.calcsustainability()
        ndata = len(self.btu_list)
        self.datatable.setRowCount(ndata)
        columns = [QApplication.translate("Table", "Burner",None),
                   QApplication.translate("Table", "Duration",None),
                   QApplication.translate("Table", "BTU",None),
                   QApplication.translate("Table", "CO2 (g)",None)]
        self.datatable.setColumnCount(len(columns))
        self.datatable.setHorizontalHeaderLabels(columns)
        self.datatable.setAlternatingRowColors(True)
        self.datatable.setShowGrid(True)
        self.datatable.verticalHeader().setSectionResizeMode(2)
        for i in range(ndata):
            duration_mmss = QLabel(stringfromseconds(self.btu_list[i]["duration"]))
            duration_mmss.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            burner = QLabel("{:.1f}%".format(self.btu_list[i]["burner_pct"]))
            BTUs = QLabel("{:.1f}".format(self.btu_list[i]["BTUs"]))
            CO2g = QLabel("{:.1f}".format(self.btu_list[i]["CO2g"]))
            burner.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
            BTUs.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)            
            CO2g.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)            

            self.datatable.setCellWidget(i,0,burner)
            self.datatable.setCellWidget(i,1,duration_mmss)
            self.datatable.setCellWidget(i,2,BTUs)
            self.datatable.setCellWidget(i,3,CO2g)

    @pyqtSlot(bool)
    def copyDataTabletoClipboard(self,_=False):
        nrows = self.datatable.rowCount() 
        ncols = self.datatable.columnCount()
        clipboard = ""
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:  #alt click
            tbl = prettytable.PrettyTable()
            fields = []
            for c in range(ncols):
                fields.append(self.datatable.horizontalHeaderItem(c).text())
            tbl.field_names = fields
            for i in range(nrows):
                print(self.datatable.cellWidget(i,0).text())  #dave
                rows = []
                rows.append(self.datatable.cellWidget(i,0).text())
                rows.append(self.datatable.cellWidget(i,1).text())
                rows.append(self.datatable.cellWidget(i,2).text())
                rows.append(self.datatable.cellWidget(i,3).text())
                tbl.add_row(rows)
            clipboard = tbl.get_string()
        else:
            for c in range(ncols):
                clipboard += self.datatable.horizontalHeaderItem(c).text()
                if c != (ncols-1):
                    clipboard += '\t'
            clipboard += '\n'
            for r in range(nrows):
                clipboard += self.datatable.cellWidget(r,0).text() + "\t"
                clipboard += self.datatable.cellWidget(r,1).text() + "\t"
                clipboard += self.datatable.cellWidget(r,2).text() + "\t"
                clipboard += self.datatable.cellWidget(r,3).text() + "\n"
        # copy to the system clipboard
        sys_clip = QApplication.clipboard()
        sys_clip.setText(clipboard)
        self.aw.sendmessage(QApplication.translate("Message","Data table copied to clipboard",None))

    @pyqtSlot(bool)
    def showsustainabilityhelp(self,_=False):
        self.helpdialog = self.aw.showHelpDialog(
                self,            # this dialog as parent
                self.helpdialog, # the existing help dialog
                QApplication.translate("Form Caption","Sustainability Help",None),
                sustainability_help.content())

    def closeHelp(self):
        self.aw.closeHelpDialog(self.helpdialog)

    
    # triggered via the cancel button
    @pyqtSlot()
    def cancel_dialog(self):
        print("cancel")  #dave
        settings = QSettings()
        #save window geometry
        settings.setValue("SustainabiltyGeometry",self.saveGeometry())
        self.aw.sustainabilityDlg_activeTab = self.TabWidget.currentIndex()
        
        #restore all the variables here
        self.aw.qmc.roastertype = self.org_roaster
        self.aw.qmc.burner_etype = self.org_burner_etype
        self.aw.qmc.burnerrating = self.org_burnerrating
        self.aw.qmc.btu_betweenbatch = self.org_btu_betweenbatch
        self.aw.qmc.btu_warmup = self.org_btu_warmup
        self.aw.qmc.ratingunit = self.org_ratingunit
        self.aw.qmc.fueltype = self.org_fueltype
        self.aw.qmc.burnerevent_zeropct = self.org_burnerevent_zeropct
        self.aw.qmc.burnerevent_hundpct = self.org_burnerevent_hundpct
        self.aw.qmc.roasts_per_session = self.org_roasts_per_session
        self.aw.qmc.loadsustainabilityfromprofile = self.loadsustainabilityfromprofile
        if self.wasDirty:
            self.aw.qmc.fileDirty()
        else:
            self.aw.qmc.fileClean()
        self.reject()

    @pyqtSlot()
    def accept(self):
        pass
        print("accept")  #dave
        self.updateAll()
       
        if not self.aw.qmc.flagon:
            self.aw.sendmessage(QApplication.translate("Message","Sustainability values changed but profile not saved to disk", None))
        self.close()

