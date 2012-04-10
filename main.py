#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# HDBench - Benchmarking for hard disks
# Copyright (c) 2012 - Manuel Joaquin Díaz Pol
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#==============================================================================
#

import commands
import re
from gi.repository import Gtk

class main:
    def __init__(self):
        #Crea la ventana de trabajo principal y obtiene los objetos en Glade
        builder = Gtk.Builder();
        builder.add_from_file("main.glade")
        
        links = {"on_butPlay_clicked" : self.playBench,
                 "on_butRefresh_clicked" : self.initComboHD,
                 "on_comboHD_changed" : self.comboHDChanged,
                 "on_window_destroy" : self.quitAll,
                 "on_errorWindow_response" : self.closeErrorWindow,
                 "on_errorWindow_close" : self.closeErrorWindow,
                 "on_PartitionCancel_clicked" : self.messagePartCancel,
                 "on_PartitionWindow_close" : self.messagePartCancel,
                 "on_comboPartition_changed" : self.comboPartChanged}
        
        builder.connect_signals(links)
        
        self.textHDInfo = builder.get_object("textbufferHDinfo")
        self.labelPart = builder.get_object("labelPartition")
        self.lcomboHd = builder.get_object("lComboHD")
        self.lcomboInc = builder.get_object("lComboInc")
        self.lcomboPart = builder.get_object("lComboPartition")
        self.comboHD = builder.get_object("comboHD")
        self.comboInc = builder.get_object("comboIncr")
        self.comboPart = builder.get_object("comboPartition")
        self.spinInitial = builder.get_object("spinInitial")
        self.spinInc = builder.get_object("spinInc")
        self.spinMax = builder.get_object("spinMax")
        self.errorWindow = builder.get_object("messageWindow")
        self.partWindow = builder.get_object("messagePartition")
        self.buttonOkPart = builder.get_object("buttonOkPart")
        
        self.initComboHD()
    
    def closeErrorWindow(self,widget,x):
        self.errorWindow.hide()
    
    def messagePartCancel(self,widget):
        self.partWindow.hide()
        
    def readFile(self,nameFile):
        try:
            fPart = open(nameFile,"r")
        except:
            self.throwError("File " + nameFile + " not found")
        
        return fPart
        
    def initComboHD(self,*widget):
        self.lcomboHd.clear()
        self.textHDInfo.set_text("")
        
        fPart = self.readFile("/proc/partitions")
        for line in fPart:
            if re.findall("sd[a-z]\s",line):
                self.lcomboHd.append(re.findall("sd[a-z]",line)) 
                
        self.comboHD.set_active(0)
        
    def comboHDChanged(self,widget):
        tree_iter = self.comboHD.get_active_iter()  
        if tree_iter != None:
            model = self.comboHD.get_model()
            name = model[tree_iter][0]        
            self.textHDInfo.set_text(self.getHDInfo(name))
        
    def getHDInfo(self,hd):        
        textCommand = "udisks --show-info /dev/" + hd
        commandOut = commands.getoutput(textCommand)
        if(commandOut!="sh: udisks: not found"):
            modelHD = commandOut.split("model:")[1].split("revision:")[0].strip()
            sizeHD = commandOut.split("size:")[1].split("block")[0].strip()
        else:
            self.throwError("Command udisks not found.\nInstall: apt-get install udisks")
        
        return modelHD + "\n" + str(int(sizeHD)/10**9) + "GB"
    
    def playBench(self,widget):
        #Collect data from spins
        spinIni = int(self.spinInitial.get_value())
        spinInc = int(self.spinInc.get_value())
        spinMax = int(self.spinMax.get_value())
        
        #Collect from comboHD
        tree_iter = self.comboHD.get_active_iter()  
        if tree_iter != None:      
            model = self.comboHD.get_model()
            selHD = model[tree_iter][0]
        else:
            self.throwError("Select a Hard Disk")
            
        #Collect from comboInc    
        tree_iter1 = self.comboInc.get_active_iter()  
        if tree_iter1 != None:      
            model1 = self.comboInc.get_model()
            selInc = model1[tree_iter1][0]
        else:
            self.throwError("Select Increase")
        
        self.tLaunch = self.calcLaunch(spinIni,spinInc,spinMax,selInc)
        
        self.readPartition(selHD)
        self.comboPart.set_active(0)
        self.partWindow.run()
        
    def comboPartChanged(self,widget):
        try:
            textCommand = "df " + self.lcomboPart[self.comboPart.get_active()][0]
        except:
            return
        commandOut = commands.getoutput(textCommand)
        if(commandOut!="sh: df: not found"):
            freeHD = int(commandOut.splitlines()[1].split()[3])/1024**2
            totReq = self.tLaunch.__len__() * int(self.spinMax.get_value()) / 1024
            if(totReq<freeHD):
                self.buttonOkPart.set_sensitive(True)
                self.labelPart.set_text("")
            else:
                self.buttonOkPart.set_sensitive(False)
                labelText = "Not enough free space. " + str(totReq) +"GB required"               
                self.labelPart.set_markup("<span foreground='red'>" + labelText + "</span>")
        else:
            self.throwError("Command df not found")
      
    def readPartition(self,hd):
        self.lcomboPart.clear()
        fPart = self.readFile("/proc/mounts")
        for line in fPart:
            line = line.split()
            if re.match("/dev/" + hd + "\d",line[0]):
                self.lcomboPart.append([line[0],line[1],line[2]])
            
    def calcLaunch(self,Ini,Inc,Max,sInc):
        tLaunch = []
        Max = Max*1024
        while(Max>Ini):
            tLaunch.append([Ini, Max/Ini, Max%Ini])
            if(sInc=="Linear"):
                Ini = Ini*Inc
            else:
                if(Ini==1):
                    Ini=2
                else:
                    Ini = Ini**Inc
        
        return tLaunch
        
    def throwError(self,textError):
        self.errorWindow.format_secondary_text(textError)
        self.errorWindow.run()
        
    def quitAll(self,widget):
        Gtk.main_quit()
        
if __name__ == '__main__':
    main()
    Gtk.main()
    