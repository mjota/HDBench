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
                 "on_window_destroy" : self.quitAll}
        
        builder.connect_signals(links)
        
        self.textHDInfo = builder.get_object("textbufferHDinfo")
        self.lcomboHd = builder.get_object("lComboHD")
        self.lcomboInc = builder.get_object("lComboInc")
        self.comboHD = builder.get_object("comboHD")
        self.comboInc = builder.get_object("comboIncr")
        self.spinInitial = builder.get_object("spinInitial")
        self.spinInc = builder.get_object("spinInc")
        self.spinMax = builder.get_object("spinMax")
        
        self.initComboHD()
        
    def readFile(self):
        try:
            fPart = open("/proc/partitions","r")
        except:
            print "Error"
        
        return fPart
        
    def initComboHD(self,*widget):
        self.lcomboHd.clear()
        self.textHDInfo.set_text("")
        
        fPart = self.readFile()
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
        modelHD = commandOut.split("model:")[1].split("revision:")[0].strip()
        sizeHD = commandOut.split("size:")[1].split("block")[0].strip()
        
        return modelHD + "\n" + str(int(sizeHD)/10**9) + "GB"
    
    def playBench(self,widget):
        
        spinIni = self.spinInitial.get_value()
        spinInc = self.spinInc.get_value()
        spinMax = self.spinMax.get_value()
        
        tree_iter = self.comboHD.get_active_iter()  
        if tree_iter != None:      
            model = self.comboHD.get_model()
            selHD = model[tree_iter][0]
        else:
            self.throwError()
            
        print selHD
            
        tree_iter1 = self.comboInc.get_active_iter()  
        if tree_iter1 != None:      
            model1 = self.comboInc.get_model()
            selInc = model1[tree_iter1][0]
        else:
            self.throwError()
 
        print selInc
        
        
    def throwError(self):
        print "Error"
        
    def quitAll(self,widget):
        print "cerrado"
        Gtk.main_quit()
        
if __name__ == '__main__':
    main()
    Gtk.main()
    