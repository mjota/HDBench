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

import os
import shutil
import commands
import re
import time
from gi.repository import Gtk,GObject
import threading
import fileCSV,plot,messagePartition

class main(threading.Thread):
    def __init__(self):
        super(main,self).__init__()
        #Crea la ventana de trabajo principal y obtiene los objetos en Glade
        builder = Gtk.Builder();
        builder.add_from_file("main.glade")
        
        links = {"on_butPlay_clicked" : self.playBench,
                 "on_butRefresh_clicked" : self.initComboHD,
                 "on_butExport_clicked" : self.export,
                 "on_comboHD_changed" : self.comboHDChanged,
                 "on_window_destroy" : self.quitAll,
                 "on_errorWindow_response" : self.closeErrorWindow,
                 "on_errorWindow_close" : self.closeErrorWindow}
        
        builder.connect_signals(links)
        
        self.textHDInfo = builder.get_object("textbufferHDinfo")
        self.lcomboHd = builder.get_object("lComboHD")
        self.lcomboInc = builder.get_object("lComboInc")
        self.comboHD = builder.get_object("comboHD")
        self.comboInc = builder.get_object("comboIncr")
        self.spinInitial = builder.get_object("spinInitial")
        self.spinInc = builder.get_object("spinInc")
        self.spinMax = builder.get_object("spinMax")
        self.errorWindow = builder.get_object("messageWindow")
        self.lResultList = builder.get_object("lResultList")
        self.topBar = builder.get_object("supBar")
        self.butExport = builder.get_object("butExport")
        self.imagePlot = builder.get_object("imagePlot")
        
        context = self.topBar.get_style_context()
        context.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        
        self.initComboHD()
        
        shutil.rmtree("/run/shm/bench",ignore_errors=True)
        os.mkdir("/run/shm/bench")
            
    
    def closeErrorWindow(self,widget,x):
        self.errorWindow.hide()
        
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
        self.lResultList.clear()
        #self.imagePlot.set_from_file("blank.svg")
        self.plotCharge("Hard disk")
        
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
        self.lResultList.clear()
        
        self.mes = messagePartition.messagePartition(self.tLaunch,self.spinMax)
        self.mes.readPartition(selHD)
        self.mes.Window.set_response_sensitive(Gtk.ResponseType.OK,False)
        self.mes.comboPart.set_active(0)
        response = self.mes.Window.run()
        self.mes.Window.destroy()
        if (response == Gtk.ResponseType.OK):
            launchW = self.launchWrite()
            launchR = self.launchRead()
            self.nameHD = self.textHDInfo.get_text(self.textHDInfo.get_start_iter(),
                                           self.textHDInfo.get_iter_at_line(1),
                                           include_hidden_chars=True).rstrip()
            self.tablePrint(launchW,launchR)
            self.plotCharge(self.nameHD)
            self.butExport.set_sensitive(True)
        
    def launchWrite(self):
        mountP = self.mes.lcomboPart[self.mes.comboPart.get_active()][1]
        writeTimes = []
        for line in self.tLaunch:
            os.mkdir("/run/shm/bench/" + str(line[0]))
            for n in range(0,line[1]):
                textCommand = "dd bs=" + str(line[0]) + "kB if=/dev/urandom of=/run/shm/bench/" + str(line[0])+ "/" + str(n) + " count=1"
                commands.getoutput(textCommand)
            textCommand = "dd bs=" + str(line[2]) + "kB if=/dev/urandom of=/run/shm/bench/" + str(line[0])+ "/R count=1"
            commands.getoutput(textCommand)
            
            textCommand = "cp -R /run/shm/bench/" + str(line[0]) + " " + mountP
            iniTime = time.time()
            commands.getoutput(textCommand)            
            endTime = time.time()
            writeTimes.append(endTime-iniTime)
            
            shutil.rmtree("/run/shm/bench/" + str(line[0])) 
            #GObject.idle_add(self.update)
        return writeTimes
    
    def launchRead(self):
        mountP = self.mes.lcomboPart[self.mes.comboPart.get_active()][1]
        readTimes = []
        for line in self.tLaunch:
            textCommand = "cp -R " + mountP + "/" + str(line[0]) + " /run/shm/bench/"
            iniTime = time.time()
            commands.getoutput(textCommand)
            endTime = time.time()
            readTimes.append(endTime-iniTime)
            
            shutil.rmtree(mountP + "/" + str(line[0]))
            shutil.rmtree("/run/shm/bench/" + str(line[0]))
            #GObject.idle_add(self.update)
        return readTimes
    
    def tablePrint(self,launchW,launchR):
        for line in self.tLaunch:
            self.lResultList.append([str(line[0]),str(launchW.pop(0)),str(launchR.pop(0))])  
           
    def plotCharge(self,nameHD):
        plt = plot.plot(self.lResultList)
        plt.printPlot(nameHD)
        
        self.imagePlot.set_from_file(nameHD + ".png") 
        
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
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.CLOSE, "Error")
        dialog.format_secondary_text(textError)
        dialog.run()

        dialog.destroy()  
        
    def export(self,widget):
        fCSV = fileCSV.fileCSV(self.nameHD)
        outfCSV = fCSV.Window.run()
        if (outfCSV == Gtk.ResponseType.OK):
            fCSV.writeCSV(self.lResultList,self.nameHD)
            fCSV.Window.destroy()
        else:
            fCSV.Window.destroy()         
              
    def quitAll(self,widget):
        shutil.rmtree("/run/shm/bench",ignore_errors=True)
        Gtk.main_quit()
        
if __name__ == '__main__':
    GObject.threads_init()
    app = main()
    app.start()
    Gtk.main()
    