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
import os
import re
from gi.repository import Gtk

class messagePartition():

    def __init__(self,tLaunch,spinMax):
        #Crea la ventana de trabajo principal y obtiene los objetos en Glade
        builder = Gtk.Builder();
        builder.add_from_file("messagePartition.glade")
        
        self.Window = builder.get_object("messagePartition")
        self.lcomboPart = builder.get_object("lComboPartition")
        self.comboPart = builder.get_object("comboPartition")
        self.labelPart = builder.get_object("labelPartition")
        
        links = {"on_comboPartition_changed" : self.comboPartChanged}
        
        builder.connect_signals(links)
        
        self.totReq = tLaunch.__len__() * int(spinMax.get_value()) / 1024
        
    def comboPartChanged(self,widget):
        try:
            textCommand = "df " + self.lcomboPart[self.comboPart.get_active()][0]
        except:
            return
        commandOut = commands.getoutput(textCommand)
        if(commandOut!="sh: df: not found"):
            freeHD = int(commandOut.splitlines()[1].split()[3])/1024**2
            if(self.totReq<freeHD):
                if os.access(self.lcomboPart[self.comboPart.get_active()][1], os.W_OK):
                    self.Window.set_response_sensitive(Gtk.ResponseType.OK,True)
                    self.labelPart.set_text("")
                else:
                    self.Window.set_response_sensitive(Gtk.ResponseType.OK,False)              
                    self.labelPart.set_markup("<span foreground='red'>No writable partition</span>")
            else:
                self.Window.set_response_sensitive(Gtk.ResponseType.OK,False)
                labelText = "Not enough free space. " + str(self.totReq) +"GB required"               
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
                
    def throwError(self,textError):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.CLOSE, "Error")
        dialog.format_secondary_text(textError)
        dialog.run()

        dialog.destroy() 
        
    def readFile(self,nameFile):
        try:
            fPart = open(nameFile,"r")
        except:
            self.throwError("File " + nameFile + " not found")
        
        return fPart
            
        
    
        
        