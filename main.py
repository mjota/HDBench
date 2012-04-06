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
                 "on_comboHD_changed" : self.comboHDChanged}
        
        builder.connect_signals(links)
        
        self.textHDInfo = builder.get_object("textbufferHDinfo")
        self.lcomboHd = builder.get_object("lComboHD")
        self.comboHD = builder.get_object("comboHD")
        
        self.initComboHD()
        
    def readFile(self):
        try:
            fPart = open("/proc/partitions","r")
        except (NameError, ValueError):
            print "No existe y es uno de estos"
        except IOError:
            print "Error de archivo no encontrado"
        except:
            print "No existe y el error es otro"
        
        return fPart
        
    def initComboHD(self,*widget):
        self.lcomboHd.clear()
        self.textHDInfo.set_text("")
        
        fPart = self.readFile()
        for line in fPart:
            if re.findall("sd[a-z]\s",line):
                self.lcomboHd.append(re.findall("sd[a-z]",line))  
        
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
        
        return modelHD + "\n" + str(int(sizeHD)/1000000000) + "GB"
    
    def playBench(self,widget):
        print "PlayBench"
        
if __name__ == '__main__':
    main()
    Gtk.main()
    