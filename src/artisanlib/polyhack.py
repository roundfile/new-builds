#!/usr/bin/env python3

# ABOUT
# Artisan Curves Dialog

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
# Marko Luther, 2020

##########################################################################
#####################     EXTRAS/HUD  EDIT DLG     #######################
##########################################################################

import sys
import platform
import numpy
import prettytable

from artisanlib.util import (deltaLabelBigPrefix, deltaLabelPrefix, deltaLabelUTF8, 
                             stringtoseconds, stringfromseconds, toFloat)
from artisanlib.dialogs import ArtisanDialog
from artisanlib.widgets import MyQDoubleSpinBox
from help import symbolic_help

from PyQt5.QtCore import (Qt, pyqtSlot, QSettings, QCoreApplication, QRegularExpression)
from PyQt5.QtGui import (QColor, QIntValidator, QRegularExpressionValidator, QPixmap)
from PyQt5.QtWidgets import (QApplication, QWidget, QCheckBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QSpinBox, QTabWidget, QComboBox, QDialogButtonBox, QGridLayout,
                             QGroupBox, QLayout, QMessageBox, QRadioButton, QStyleFactory, QHeaderView,
                             QTableWidget, QTableWidgetItem,QMessageBox)



class polyhackDlg(ArtisanDialog):
    def __init__(self, parent = None, aw = None, activeTab = 0):
        super(polyhackDlg,self).__init__(parent, aw)
        
#        self.app = QCoreApplication.instance()
        
#        self.setWindowTitle(QApplication.translate("Form Caption","Curves", None))
#        self.setModal(True)

#        buttonsLayout = QHBoxLayout()
#        buttonsLayout.addStretch()
#        buttonsLayout.addWidget(self.dialogbuttons)
#        #incorporate layouts
#        Slayout = QVBoxLayout()
#        Slayout.addLayout(buttonsLayout)
#        Slayout.setContentsMargins(5,15,5,5)
#        Slayout.setSpacing(5)
#        self.setLayout(Slayout)
#
#        # connect the ArtisanDialog standard OK/Cancel buttons
#        self.dialogbuttons.accepted.connect(self.updatetargets)
#        self.dialogbuttons.rejected.connect(self.close)


        self.showSegmentCurve = False

        if self.aw.qmc.extradevices[0] != 25:
            string = "Upps, gotta have a virtual device in the first position!"
            QMessageBox.information(self.aw,QApplication.translate("Message","Profile information",None),string)
            self.close()
        elif self.aw.qmc.timeindex[0] == -1:
            string = "There is no profile loaded"
            QMessageBox.information(self.aw,QApplication.translate("Message","Profile information",None),string)
            self.close()
        elif self.aw.qmc.timeindex[1] == 0:
            string = "There is no Dry End event"
            QMessageBox.information(self.aw,QApplication.translate("Message","Profile information",None),string)
            self.close()
        elif self.aw.qmc.timeindex[6] == 0:
            string = "There is no DROP event"
            QMessageBox.information(self.aw,QApplication.translate("Message","Profile information",None),string)
            self.close()
        elif not self.aw.qmc.DeltaBTflag:
            string = "Delta BT must be displayed"
            QMessageBox.information(self.aw,QApplication.translate("Message","Profile information",None),string)
            self.close()
        elif self.showSegmentCurve and (len(self.aw.qmc.extradevices) < 2 or self.aw.qmc.extradevices[1] != 25):
            string = "Upps, gotta have a virtual device in the first position!"
            QMessageBox.information(self.aw,QApplication.translate("Message","Profile information",None),string)
            self.close()

        self.equstr = {}
        
        self.aw.qmc.extraname1[0] = "ET-BT"
        self.aw.qmc.extraname2[0] = "mapping"
        self.aw.extraDelta1[0] = False
        self.aw.extraDelta2[0] = True
        aw.qmc.extradevicecolor1[0] = "#000000"
        aw.qmc.extradevicecolor2[0] = "#ff00ff"
        aw.extraCurveVisibility1[0] = False
        aw.extraCurveVisibility2[0] = True
        aw.extraFill1[0] = 0
        aw.extraFill2[0] = 0

        if self.showSegmentCurve:
            self.aw.qmc.extraname1[1] = "segment"
            self.aw.qmc.extraname2[1] = ""
            self.aw.extraDelta1[1] = True
            self.aw.extraDelta2[1] = False
            aw.qmc.extradevicecolor1[1] = "#00ff00"
            aw.qmc.extradevicecolor2[1] = "#000000"
            aw.extraCurveVisibility1[1] = True
            aw.extraCurveVisibility2[1] = False
            aw.extraFill1[1] = 0
            aw.extraFill2[1] = 0

        self.aw.qmc.extramathexpression1[0] = "Y1-Y2"
        self.aw.calcVirtualdevices(update=True)

        self.collectCurves()
        if not self.doPolyfit() :
            string = "Polyfit failed"
            QMessageBox.information(self.aw,QApplication.translate("Message","Profile information",None),string)
            self.close()
        
        self.aw.qmc.extramathexpression2[0] = self.equstr["de2drop"].replace('x','Y3')
        if self.showSegmentCurve:
            self.aw.qmc.extramathexpression1[1] = self.equstr["segment"].replace('x','Y3')
        self.aw.calcVirtualdevices(update=True)
        self.aw.qmc.redraw(recomputeAllDeltas=False)
        self.close()
           

    def doPolyfit(self):
        try:
            # Assumes picking the 4th item in the left dropdown and the 1st item in the right dropdown.
            polyfit_degree = 1
            if self.aw.qmc.DeltaETflag:
                c1_index = 4  # Y5 (0xT1: ET-BT)
                c2_index = 1  # DeltaBT
            else:
                c1_index = 3  # Y5 (0xT1: ET-BT)
                c2_index = 0  # DeltaBT
            startindex = self.aw.qmc.timeindex[1]
            endindex = self.aw.qmc.timeindex[6]
            c1 = self.curves[c1_index]
            c2 = self.curves[c2_index]
            # print the equation for each sample from DE to DROP
            if False:
                for j in range(startindex, endindex):
                    z = self.aw.qmc.polyfit(c1,c2,
                           polyfit_degree,startindex,j,self.deltacurves[0])
                    res = True
                    if z is not None:
                        for e in z:
                            if numpy.isnan(e):
                                res = False
                                print(j, "BROKEN")
                    if res and z is not None:
                        s = self.aw.fit2str(z)
                        self.equstr = s
                        print("{} {}".format(j, s))

            # find the slope and intercept over a defined segment
            if self.showSegmentCurve:
                samples_after_DE = 30
                samples_before_FCs = 60
                start_ = self.aw.qmc.timeindex[1] + samples_after_DE
                end_ = self.aw.qmc.timeindex[2] - samples_before_FCs
                z = self.aw.qmc.polyfit(c1,c2,
                       polyfit_degree,start_,end_,self.deltacurves[0])
                res = True
                if z is not None:
                    for e in z:
                        if numpy.isnan(e):
                            res = False
                            print(j, "BROKEN")
                            return False
                if res and z is not None:
                    s_seg = self.aw.fit2str(z)
                    self.equstr["segment"] = s_seg

            # this is the polyfit equation that will be passed to the extra device
            z = self.aw.qmc.polyfit(c1,c2,
                   polyfit_degree,startindex,endindex,self.deltacurves[0])
            res = True
            if z is not None:
                for e in z:
                    if numpy.isnan(e):
                        res = False
                        return False
            if res and z is not None:
                s = self.aw.fit2str(z)
                self.equstr["de2drop"] = s
                print("\n{}{} {} \nDryEnd to Drop : {}".format(self.aw.qmc.batchprefix, self.aw.qmc.roastbatchnr, self.aw.qmc.title,s))  #dave
                if self.showSegmentCurve:
                    print("Defined segment: {}".format(s_seg))  #dave
                return True
            else:
                return False
        except Exception as ex:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + "doPolyfit(): {0}").format(str(ex)),exc_tb.tb_lineno)


    # TODO: add background curves temp1B, temp2B, timeB, delta1B, delta2B (could be of different size!)
    def collectCurves(self):
        try:
            idx = 0
            self.curves = []
            self.curvenames = []
            self.deltacurves = [] # list of flags. True if delta curve, False otherwise
            if self.aw.qmc.DeltaETflag:
                self.curvenames.append(deltaLabelUTF8 + QApplication.translate("Label","ET",None))
                self.curves.append(self.aw.qmc.delta1)
                self.deltacurves.append(True)
                idx = idx + 1
            if self.aw.qmc.DeltaBTflag:
                self.curvenames.append(deltaLabelUTF8 + QApplication.translate("Label","BT",None))
                self.curves.append(self.aw.qmc.delta2)
                self.deltacurves.append(True)
                idx = idx + 1
            self.curvenames.append(QApplication.translate("ComboBox","ET",None))
            self.curvenames.append(QApplication.translate("ComboBox","BT",None))
            self.curves.append(self.aw.qmc.temp1)
            self.curves.append(self.aw.qmc.temp2)
            self.deltacurves.append(False)
            self.deltacurves.append(False)
            for i in range(len(self.aw.qmc.extradevices)):
                self.curvenames.append(str(i) + "xT1: " + self.aw.qmc.extraname1[i])
                self.curvenames.append(str(i) + "xT2: " + self.aw.qmc.extraname2[i])
                self.curves.append(self.aw.qmc.extratemp1[i])
                self.curves.append(self.aw.qmc.extratemp2[i])
                self.deltacurves.append(False)
                self.deltacurves.append(False)
        except Exception as ex:
            _, _, exc_tb = sys.exc_info()
            self.aw.qmc.adderror((QApplication.translate("Error Message", "Exception:",None) + "collectCurves(): {0}").format(str(ex)),exc_tb.tb_lineno)


    def closeEvent(self,_):
        self.close()
        
    #cancel button
    @pyqtSlot()
    def close(self):
        self.accept()

    #button OK
    @pyqtSlot()
    def updatetargets(self):
        self.accept()