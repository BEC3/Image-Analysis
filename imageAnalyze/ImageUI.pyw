#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, glob
import wx, numpy
import matplotlib

import time

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.cm as cm


from imagePlot import *
from imgFunc import *
from watchforchange import *
from localPath import *
from fitTool import *


class ImageUI(wx.Frame):
  
    def __init__(self, parent, title):
        super(ImageUI, self).__init__(parent, title=title, 
            size=(1300, 600))
            
        self.InitUI()
        self.Centre()
        self.Show()
        # self.AOI = [(None,None),(None,None)]
        self.gVals = None
        self.pVals = None
        self.fVals = None
        self.AOIImage = None
        self.AOI = None
        self.xLeft = None
        self.xRight = None
        self.yBottom = None
        self.yTop = None
        # self.Bind(wx.EVT_PAINT, self.OnPaint)

        #benchmarking variables
        self.benchmark_startTime=0
        self.benchmark_endTime=0

        self.q = None
        self.gaussionParams = None
        self.fermionParams = None
        self.bosonParams = None

        self.filename = None
        self.Tmp = None
        self.data = None
        self.observer = None
        self.observer = Observer()
        self.observer.schedule(MyHandler(self.autoRun, self), path = self.imageFolderPath.GetValue())

        self.fitMethodGaussian.SetValue(True)
        self.autoRunning = False
        # self.FermionFitChosen(e)

    def InitUI(self):

    	panel = wx.Panel(self)
        font1 = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
    	# font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
    	# font.SetPointSize(9)
######### file ############
        # set data path

        
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        

        settingBox = wx.StaticBox(panel, label = 'Setting')
        settingBoxSizer = wx.StaticBoxSizer(settingBox, wx.VERTICAL)

        fileBox = wx.StaticBox(panel, label = 'File')
        fileBoxSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)
        pathText = wx.StaticText(panel,label='Image Folder Path')
        fileBoxSizer.Add(pathText, flag=wx.ALL, border=5)
        self.imageFolderPath = wx.TextCtrl(panel, value=LOCAL_PATH)
        fileBoxSizer.Add(self.imageFolderPath, flag=wx.ALL|wx.EXPAND, border=5)
        nameText = wx.StaticText(panel, label='Image File Name')
        fileBoxSizer.Add(nameText, flag=wx.ALL, border=5)
        hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        self.filenameText = wx.TextCtrl(panel)
        hbox12.Add(self.filenameText, 1, flag=wx.ALL| wx.EXPAND , border=5)
        chooseFileButton = wx.Button(panel, label = 'Choose File')
        chooseFileButton.Bind(wx.EVT_BUTTON, self.chooseFile)
        hbox12.Add(chooseFileButton, flag=wx.ALL, border=5)
        fileBoxSizer.Add(hbox12, flag=wx.ALL| wx.EXPAND, border=0)

        settingBoxSizer.Add(fileBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)



        fermionOrBosonBox = wx.StaticBox(panel, label = 'Fermion/Boson/Gaussian')
        fermionOrBosonBoxSizer = wx.StaticBoxSizer(fermionOrBosonBox, wx.HORIZONTAL)
        self.fitMethodFermion = wx.RadioButton(panel, label="Fermion")
        self.fitMethodBoson = wx.RadioButton(panel, label="Boson")
        self.fitMethodGaussian = wx.RadioButton(panel, label="Gaussian")
        self.Bind(wx.EVT_RADIOBUTTON, self.FermionFitChosen, id=self.fitMethodFermion.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.BosonFitChosen, id=self.fitMethodBoson.GetId())
        self.Bind(wx.EVT_RADIOBUTTON, self.GaussianFitChosen, id=self.fitMethodGaussian.GetId())
        
        fermionOrBosonBoxSizer.Add(self.fitMethodFermion, flag=wx.ALL, border=5)
        fermionOrBosonBoxSizer.Add(self.fitMethodBoson, flag=wx.ALL, border=5)
        fermionOrBosonBoxSizer.Add(self.fitMethodGaussian, flag=wx.ALL, border=5)

        settingBoxSizer.Add(fermionOrBosonBoxSizer, flag=wx.ALL| wx.EXPAND, border = 5)

        aoiBox = wx.StaticBox(panel, label='AOI')
        aoiBoxSizer = wx.StaticBoxSizer(aoiBox, wx.VERTICAL)
        aoiText = wx.StaticText(panel, label = 'AOI: (x,y)->(x,y)')
        aoiBoxSizer.Add(aoiText, flag=wx.ALL, border=5)

        hbox11 = wx.BoxSizer(wx.HORIZONTAL)
        self.AOI1 = wx.TextCtrl(panel, value='10', size=(40,22))
        self.AOI2 = wx.TextCtrl(panel, value='10', size=(40,22))
        self.AOI3 = wx.TextCtrl(panel, value='900', size=(40,22))
        self.AOI4 = wx.TextCtrl(panel, value='900', size=(40,22))
        hbox11.Add(self.AOI1, flag=wx.ALL, border=2)
        hbox11.Add(self.AOI2, flag=wx.ALL, border=2)
        hbox11.Add(self.AOI3, flag=wx.ALL, border=2)
        hbox11.Add(self.AOI4, flag=wx.ALL, border=2)
        aoiBoxSizer.Add(hbox11, flag=wx.EXPAND|wx.ALL, border=5)
        
        settingBoxSizer.Add(aoiBoxSizer, flag=wx.ALL| wx.EXPAND, border=5)

        paramBox = wx.StaticBox(panel, label='Parameters')
        paramBoxSizer = wx.StaticBoxSizer(paramBox, wx.VERTICAL)

        hbox21 = wx.BoxSizer(wx.HORIZONTAL)
        st8 = wx.StaticText(panel, label = 'Time of Flight(ms)')
        self.tof = wx.TextCtrl(panel, value='5', size=(50,22))
        hbox21.Add(st8, flag=wx.ALL, border=5)
        hbox21.Add(self.tof, flag=wx.ALL, border=5)
        paramBoxSizer.Add(hbox21, flag=wx.ALL, border=0)


        st9 = wx.StaticText(panel, label = 'Trapping Frequency(Hz)')
        paramBoxSizer.Add(st9, flag=wx.ALL, border=5)
        
        hbox22 = wx.BoxSizer(wx.HORIZONTAL)
        st10 = wx.StaticText(panel, label = 'Axial  ')
        self.omegaAxial = wx.TextCtrl(panel, value='20')
        hbox23 = wx.BoxSizer(wx.HORIZONTAL)
        st11 = wx.StaticText(panel,label = 'Radial')
        self.omegaRadial = wx.TextCtrl(panel, value='250')
        
        
        hbox22.Add(st10, flag=wx.ALL, border=5)
        hbox22.Add(self.omegaAxial, flag=wx.ALL, border=5)
        hbox23.Add(st11, flag=wx.ALL, border=5)
        hbox23.Add(self.omegaRadial, flag=wx.ALL, border=5)

        paramBoxSizer.Add(hbox22, flag=wx.ALL|wx.EXPAND, border=0)
        paramBoxSizer.Add(hbox23, flag=wx.ALL|wx.EXPAND, border=0)

        settingBoxSizer.Add(paramBoxSizer, flag=wx.ALL| wx.EXPAND, border=5)
        hbox.Add(settingBoxSizer, 1, wx.ALL ,  10)


        ###############################
        fittingBox = wx.StaticBox(panel, label = 'Fitting')
        fittingBoxSizer = wx.StaticBoxSizer(fittingBox, wx.VERTICAL)

        showImgButton = wx.Button(panel,  label = 'Fit Image')
        showImgButton.Bind(wx.EVT_BUTTON, self.fitImage)
        fittingBoxSizer.Add(showImgButton, flag=wx.ALL|wx.EXPAND, border=5)

        
        self.autoButton = wx.Button(panel, label = 'Auto Fit')
        self.autoButton.Bind(wx.EVT_BUTTON, self.startAutoRun)
        fittingBoxSizer.Add(self.autoButton, flag=wx.ALL|wx.EXPAND, border=5)


#         #Fitting result
        
        fittingResult = wx.StaticBox(panel, label='Fitting Result')
        fittingResultSizer = wx.StaticBoxSizer(fittingResult, wx.VERTICAL)

        gaussResult = wx.StaticBox(panel, label='Gaussian Fit')
        gaussResultBox = wx.StaticBoxSizer(gaussResult, wx.VERTICAL)

        hbox121 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(panel, label='Center at')
        self.gCenter = wx.TextCtrl(panel, value='', style=wx.TE_READONLY)
        hbox121.Add(st5, flag=wx.ALL, border=5)
        hbox121.Add(self.gCenter, flag=wx.ALL, border=0)

        hbox122 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(panel, label='Sigma')
        self.gSigma = wx.TextCtrl(panel, value='', style=wx.TE_READONLY)
        hbox122.Add(st6, flag=wx.ALL, border=5)
        hbox122.Add(self.gSigma, flag=wx.ALL, border=0)

        hbox126 = wx.BoxSizer(wx.HORIZONTAL)
        st7 = wx.StaticText(panel, label='Atom#')
        st8 = wx.StaticText(panel, label='Atom#from fit')
        self.atomNumberInt = wx.TextCtrl(panel, value='', style=wx.TE_READONLY)
        self.atomNumberIntFit = wx.TextCtrl(panel, value='', style=wx.TE_READONLY)
        hbox126.Add(st7, flag=wx.LEFT | wx.TOP, border=5)
        hbox126.Add(self.atomNumberInt, flag=wx.LEFT | wx.TOP, border=0)
        hbox126.Add(st8, flag=wx.LEFT | wx.TOP, border=5)
        hbox126.Add(self.atomNumberIntFit, flag=wx.LEFT | wx.TOP, border=0)

        hbox130 = wx.BoxSizer(wx.HORIZONTAL)
        st12 = wx.StaticText(panel, label='Temperature(nK)')
        self.gTemperature = wx.TextCtrl(panel, value='', style=wx.TE_READONLY)
        hbox130.Add(st12, flag=wx.ALL, border=5)
        hbox130.Add(self.gTemperature, flag=wx.ALL, border=0) 

        gaussResultBox.Add(hbox121, flag=wx.ALL, border=5)
        gaussResultBox.Add(hbox122, flag=wx.ALL, border=5)
        gaussResultBox.Add(hbox126, flag=wx.ALL, border=5)
        gaussResultBox.Add(hbox130, flag=wx.ALL, border=5)
        fittingResultSizer.Add(gaussResultBox, flag=wx.ALL|wx.EXPAND, border=5)

        self.fermionResult = wx.StaticBox(panel, label='Fermion Fit')
        fermionResultBox = wx.StaticBoxSizer(self.fermionResult, wx.VERTICAL)

        hbox127 = wx.BoxSizer(wx.HORIZONTAL)
        self.fText1 = wx.StaticText(panel, label='Size')
        self.fWidth = wx.TextCtrl(panel, value='', style=wx.TE_READONLY)
        hbox128 = wx.BoxSizer(wx.HORIZONTAL)
        self.fText2 = wx.StaticText(panel, label='Fugacity(=mu*beta)')
        self.fq = wx.TextCtrl(panel, value='', style=wx.TE_READONLY)
        hbox129 = wx.BoxSizer(wx.HORIZONTAL)
        self.tOverTFLabel = wx.StaticText(panel, label='T/T_F')
        self.tOverTF = wx.TextCtrl(panel, value='', style=wx.TE_READONLY)
        
        hbox127.Add(self.fText1, flag=wx.LEFT | wx.TOP, border=5)
        hbox127.Add(self.fWidth, flag=wx.LEFT | wx.TOP, border=5)
        hbox128.Add(self.fText2, flag=wx.LEFT | wx.TOP, border=5)
        hbox128.Add(self.fq, flag=wx.LEFT | wx.TOP, border=5)
        hbox129.Add(self.tOverTFLabel, flag=wx.LEFT | wx.TOP, border=5)
        hbox129.Add(self.tOverTF, flag=wx.LEFT | wx.TOP, border=5)

        fermionResultBox.Add(hbox127, flag=wx.LEFT | wx.TOP, border=5)
        fermionResultBox.Add(hbox128, flag=wx.LEFT | wx.TOP, border=5)
        fermionResultBox.Add(hbox129, flag=wx.LEFT | wx.TOP, border=5)
        fittingResultSizer.Add(fermionResultBox, flag=wx.ALL|wx.EXPAND, border=5)

        # bosonResult = wx.StaticBox(fittingBox, label='Boson Fit')
        # bosonResultBox = wx.StaticBoxSizer(bosonResult, wx.VERTICAL)

        # hbox123 = wx.BoxSizer(wx.HORIZONTAL)
        # self.pText1 = wx.StaticText(fittingBox, label='Thermal Size')
        # self.pWidth1 = wx.TextCtrl(fittingBox, value='', style=wx.TE_READONLY)
        # hbox124 = wx.BoxSizer(wx.HORIZONTAL)
        # self.pText2 = wx.StaticText(fittingBox, label='Condensate Size')
        # self.pWidth2 = wx.TextCtrl(fittingBox, value='', style=wx.TE_READONLY)
        # hbox125 = wx.BoxSizer(wx.HORIZONTAL)
        # self.becFractionLabel = wx.StaticText(fittingBox, label='BEC Fraction')
        # self.becFraction = wx.TextCtrl(fittingBox, value='', style=wx.TE_READONLY)

        # hbox123.Add(self.pText1, flag=wx.LEFT | wx.TOP, border=5)
        # hbox123.Add(self.pWidth1, flag=wx.LEFT | wx.TOP, border=5)
        # hbox124.Add(self.pText2, flag=wx.LEFT | wx.TOP, border=5)
        # hbox124.Add(self.pWidth2, flag=wx.LEFT | wx.TOP, border=5)
        # hbox125.Add(self.becFractionLabel, flag=wx.LEFT | wx.TOP, border=5)
        # hbox125.Add(self.becFraction, flag=wx.LEFT | wx.TOP, border=5)
        # bosonResultBox.Add(hbox123, flag=wx.LEFT | wx.TOP, border=5)
        # bosonResultBox.Add(hbox124, flag=wx.LEFT | wx.TOP, border=5)
        # bosonResultBox.Add(hbox125, flag=wx.LEFT | wx.TOP, border=5)

        # fittingResultSizer.Add(bosonResultBox, flag=wx.ALL|wx.EXPAND, border=5)



        fittingBoxSizer.Add(fittingResultSizer, flag=wx.ALL|wx.EXPAND, border=5)


        dataBox = wx.StaticBox(panel, label='Save Data')
        dataBoxSizer = wx.StaticBoxSizer(dataBox, wx.VERTICAL)


        self.saveFermionButton = wx.Button(panel,  label = 'Save Above Results')
        self.saveFermionButton.Bind(wx.EVT_BUTTON, self.saveResult)
        cleanButton = wx.Button(panel,  label = 'Remove all saved data')
        cleanButton.Bind(wx.EVT_BUTTON, self.cleanData)

        dataBoxSizer.Add(self.saveFermionButton, flag=wx.ALL|wx.EXPAND, border=5)
        dataBoxSizer.Add(cleanButton, flag=wx.ALL|wx.EXPAND, border=5)

        fittingBoxSizer.Add(dataBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
        
        hbox.Add(fittingBoxSizer, 2, wx.ALL|wx.EXPAND ,  10)
######### images ##################
        
        imagesBox = wx.StaticBox(panel, label='Images')
        imagesBoxSizer = wx.StaticBoxSizer(imagesBox, wx.VERTICAL)

        
        figure = Figure()
        self.axes1 = figure.add_subplot(221)
        self.axes1.set_title('Original', fontsize=10)
        for label in (self.axes1.get_xticklabels() + self.axes1.get_yticklabels()):
            label.set_fontsize(7)
        self.axes2 = figure.add_subplot(222)
        self.axes2.set_title('Gaussian', fontsize=10)
        for label in (self.axes2.get_xticklabels() + self.axes2.get_yticklabels()):
            label.set_fontsize(7)
        self.axes3 = figure.add_subplot(223)
        self.axes3.set_title('Fermion/Boson', fontsize=10)
        for label in (self.axes3.get_xticklabels() + self.axes3.get_yticklabels()):
            label.set_fontsize(7)
        self.axes4 = figure.add_subplot(224)
        self.axes4.set_title('OD Distribution', fontsize=10)
        for label in (self.axes4.get_xticklabels() + self.axes4.get_yticklabels()):
            label.set_fontsize(7)
        self.canvas =  FigureCanvas(panel, -1, figure)
        imagesBoxSizer.Add(self.canvas, flag=wx.ALL|wx.EXPAND, border=5)

       
        hbox.Add(imagesBoxSizer, 4, wx.ALL|wx.EXPAND, 10)

######## multiple shoots functions ############
        listFitBox = wx.StaticBox(panel, label='List Fit')
        listFitBoxSizer = wx.StaticBoxSizer(listFitBox, wx.VERTICAL)

        readDataBox = wx.StaticBox(panel, label='Read data')
        readDataBoxSizer = wx.StaticBoxSizer(readDataBox, wx.HORIZONTAL)
        readButton = wx.Button(panel, label = 'Read saved data')
        readButton.Bind(wx.EVT_BUTTON, self.readData)
        self.dataReadedText = wx.TextCtrl(panel,value='input: 0', style=wx.TE_READONLY)
        readDataBoxSizer.Add(readButton, flag=wx.LEFT | wx.TOP, border=5)
        readDataBoxSizer.Add(self.dataReadedText, 1, flag=wx.LEFT | wx.TOP | wx.EXPAND, border=5)
        listFitBoxSizer.Add(readDataBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)

        fitListButton = wx.Button(panel, label = 'List Data Fit')
        fitListButton.Bind(wx.EVT_BUTTON, self.fitListData)
        listFitBoxSizer.Add(fitListButton, flag=wx.ALL|wx.EXPAND, border=5)

        listFitResultBox = wx.StaticBox(panel, label='List Fit Result')
        listFitResultBoxSizer = wx.StaticBoxSizer(listFitResultBox, wx.VERTICAL)
        hbox33 = wx.BoxSizer(wx.HORIZONTAL)
        st13 = wx.StaticText(panel,label = 'Temperature(nK)')
        self.fitTempText = wx.TextCtrl(panel, style=wx.TE_READONLY)
        st14 = wx.StaticText(panel,label = 'Trapping Frequency(Hz)')
        hbox34 = wx.BoxSizer(wx.HORIZONTAL)
        st15 = wx.StaticText(panel, label = 'Axial  ')
        self.fitTrapAxialFreqText = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hbox35 = wx.BoxSizer(wx.HORIZONTAL)
        st16 = wx.StaticText(panel, label = 'Radial')
        self.fitTrapRadialFreqText = wx.TextCtrl(panel, style=wx.TE_READONLY)
        
        hbox33.Add(st13, flag=wx.ALL, border=5)
        hbox33.Add(self.fitTempText, flag=wx.ALL, border=5)
        listFitResultBoxSizer.Add(hbox33, flag=wx.ALL, border=0)
        listFitResultBoxSizer.Add(st14, flag=wx.ALL, border=5)
        hbox34.Add(st15, flag=wx.ALL, border=5)
        hbox34.Add(self.fitTrapAxialFreqText, flag=wx.ALL, border=0)
        listFitResultBoxSizer.Add(hbox34, flag=wx.ALL, border=5)
        hbox35.Add(st16, flag=wx.ALL, border=5)
        hbox35.Add(self.fitTrapRadialFreqText, flag=wx.ALL, border=5)
        listFitResultBoxSizer.Add(hbox35, flag=wx.ALL, border=0)

        listFitBoxSizer.Add(listFitResultBoxSizer, flag=wx.ALL|wx.EXPAND, border=5)
        
        hbox.Add(listFitBoxSizer, 1, wx.ALL|wx.EXPAND, 10)


# ######## show image on screen ############
        
        # vbox4 = wx.BoxSizer(wx.VERTICAL)
        # centerImage = wx.Image('../data/1.jpg', wx.BITMAP_TYPE_ANY)
        # self.imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(centerImage))
        # # vbox4.Add(centerImage, flag=wx.LEFT | wx.TOP, border=5)

        # hbox.Add(vbox4, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=20)


        panel.SetSizer(hbox)
 #####################################################    

    def chooseFile(self, e):
        
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(None, 'Open', '', style=style)
        if dialog.ShowModal() == wx.ID_OK:
            self.filename = dialog.GetFilename()
            self.filenameText.SetValue(self.filename)
        else:
            self.filename = None

        dialog.Destroy()


    def FermionFitChosen(self, e):
        print "Mode: Fermion Fit"
        self.cleanValue()
        self.fermionResult.SetLabel('Fermion Fit Result')
        self.fText1.SetLabel('Size')
        self.fText2.SetLabel('Fugacity(=mu*beta)')
        self.tOverTFLabel.SetLabel('T/T_F')

    def BosonFitChosen(self, e):

        print "Mode: Boson Fit"
        self.cleanValue()
        self.fermionResult.SetLabel('Boson Fit Result')
        self.fText1.SetLabel('Thermal Size')
        self.fText2.SetLabel('BEC Size')
        self.tOverTFLabel.SetLabel('BEC fraction')

    def GaussianFitChosen(self, e):
        print "Mode: Gaussian Fit"
        self.cleanValue()


    def cleanValue(self):
        self.fWidth.SetValue('')
        self.fq.SetValue('')
        self.tOverTF.SetValue('')
        self.gCenter.SetValue('')
        self.gSigma.SetValue('')
        self.atomNumberInt.SetValue('')
        self.gTemperature.SetValue('')
        self.atomNumberIntFit.SetValue('')


    def fitImage(self, e):
        
        
        self.benchmark_startTime=time.time()
        print "Begin to fit..."+str(self.benchmark_startTime)
        self.readImage()
        tmp = time.time()
        # print "Read Image totally took " + str(tmp - self.benchmark_startTime)
        self.showImg(e)

    def readImage(self):
        plotMin = 0.0
        plotMax = 0.3
        
        try:
            # Read Image
            path = self.imageFolderPath.GetValue()
            if not path:
                print "Wrong Folder!"
                return None
                # self.alert
            self.filename = self.filenameText.GetValue()

            
            if not self.filename:
                latest = max(glob.iglob(path + '*.aia'), key=os.path.getctime)
                s = latest
                s0 = s.split('/')
                self.filename = s0[-1]
            else:
                s = path + self.filename

            self.xLeft = int(self.AOI1.GetValue())
            # print xLeft
            self.xRight = int(self.AOI3.GetValue())
            # print xRight
            self.yTop = int(self.AOI2.GetValue())
            # print yTop
            self.yBottom = int(self.AOI4.GetValue())
            # print yBottom
            self.AOI = [[self.xLeft,self.yTop],[self.xRight,self.yBottom]]

            absorbImg = readData(s)

            self.atomImage = -np.log(absorbImg)
            ### Restrict to the are of interest
            self.AOIImage = self.atomImage[self.yTop:self.yBottom,self.xLeft:self.xRight]
            print "Successfully read Image"

        except Exception:
            print "Failed to read this image."
            

        ## view fit result
    def showImg(self, e): 
        if not self.autoRunning:
            mode = "Single"
        else:
            mode = "Auto"
        #self.gaussionParams = fitData(self.AOIImage, gaussionDistribution, mode)
        #print self.gaussionParams
        try:

            N_int = 0#atomNumber(self.AOIImage, self.offset)
            tempp = self.atomImage[self.yTop-3:self.yBottom+3,self.xLeft-3:self.xRight+3]
            self.offsetEdge = aoiEdge(tempp)
            N_intEdge = atomNumber(self.AOIImage, self.offsetEdge)
           
            print "Start Gaussian Fit..."

            tmp1 = time.time()
        
            self.gaussionParams = fitData(self.AOIImage, gaussionDistribution, mode)
            tmp2 = time.time()
            
            """x0, y0, a, b, amplitude, offset"""

            plotParam = [self.gaussionParams[0], self.gaussionParams[1], self.gaussionParams[2],self.gaussionParams[3]]
            self.gaussionParams[0] += self.xLeft
            self.gaussionParams[1] += self.yTop
            self.offset = self.gaussionParams[5]

            
            
           
            x = np.arange(self.xLeft, self.xRight, 1)
            
            y = np.arange(self.yTop, self.yBottom, 1)
            
            x0, y0, a, b, amplitude, offset = self.gaussionParams
            if x0 < self.xLeft or x0 > self.xRight or y0 < self.yTop or y0 > self.yBottom:
                print "Find the wrong center. Please change the AOI.."
                #raise Exception
            
            if a > self.xRight - self.xLeft or b > self.yBottom - self.yTop:
                print "Find the wront sigma. Please change the AOI.."
                #raise Exception
                
            print "Create Gaussian Fit Image..."
            
            # gaussianFitImage = self.gVals[2]*np.exp(-0.5*(((X-self.gVals[0][0])/self.gVals[1][0])**2+((Y-self.gVals[0][1])/self.gVals[1][1])**2))+self.gVals[3]
            size = np.shape(self.AOIImage)
            coordinates = np.meshgrid(x, y)
            tmp3 = time.time()

            gaussianFitImage = gaussionDistribution(coordinates, x0, y0, a, b, amplitude, offset).reshape(self.yBottom-self.yTop,self.xRight-self.xLeft)
            tmp4 = time.time()
           

            
            # atomImagePlot([atomImage, gaussianFitImage], ['original image', 'gaussianFitImage'] )
            self.gCenter.SetValue('( %.0f'%abs(x0) + ' , %.0f )'%abs(y0))
            self.gSigma.SetValue('( %.0f'%abs(a) + ' , %.0f )'%abs(b))
            
            

            N_gaussianFit = abs(atomNumberGaussianFit(self.gaussionParams[2],self.gaussionParams[3], self.gaussionParams[4]))
           
            self.atomNumberInt.SetValue(str("%.0f" % N_intEdge))
            self.atomNumberIntFit.SetValue(str("%.0f" % N_gaussianFit))
           
            self.axes1.imshow(self.AOIImage, cmap='gray_r', aspect=1, vmin=-1, vmax=1)
            self.axes2.imshow(gaussianFitImage, cmap='gray_r', aspect=1, vmin=-1, vmax=1)
           
           
            self.axes4.lines=[]
            # for i, line in enumerate(self.axes4.lines):
            #     print "2"
            #     self.axes4.lines.pop(i)
                # line.remove()

            if self.fitMethodGaussian.GetValue():
                
                data = [self.AOIImage, gaussianFitImage]
                
                center = plotParam[0:2]
                sigma = plotParam[2:4]
                
                yy=[]
                for k in range(2):
                   l = radioDistribution(data[k], center, sigma)
                   yy.append(l)
                xx= range(len(yy[0]))
                
                originalLine,  = self.axes4.plot(xx, yy[0], 'g:', label='origianl')
                gaussianLine,  = self.axes4.plot(xx, yy[1], 'r--', label='gaussian')
                # fitLine,  = self.axes4.plot(xx, yy[2], 'b-', label='fit')
                
                self.axes4.legend([originalLine, gaussianLine], ['original', 'gaussian'])
            


            # plotStr = [str("Atom#(offset from fit): %.3fm" % (N_int/1000000))]
            # plotStr.append(str("Atom#(offset from edge): %.3fm" % (N_intEdge/1000000)))
            # plotStr.append(str("Atom#(from gaussfit): %.3fm" % (N_gaussianFit/1000000)))
            elif self.fitMethodFermion.GetValue():
                print "Start Fermion Fit..."
                self.fermionParams = fitData(self.AOIImage, fermionDistribution, mode)
                """x0, y0, a, b, amplitude, offset, q"""
                
            
                self.fermionParams[0] += self.xLeft
                self.fermionParams[1] += self.yTop
            
                x0, y0, a, b, amplitude, offset, q = self.fermionParams
                self.foffset = self.fermionParams[5]
                self.fWidth.SetValue('( %.0f'%(self.fermionParams[2]) + ' , %.0f )'%(self.fermionParams[3]))
                self.fq.SetValue('%.2f'%(self.fermionParams[6]))
                tovertf = TOverTF(self.fermionParams[6])
                self.tOverTF.SetValue(str('%.3f' % tovertf ))
                # plotStr.append(str('T/T_F=%.3f' % tovertf ))

                print "Create Fermion Fit Image..."
                fermionFitImage = fermionDistribution(coordinates, x0, y0, a, b, amplitude, offset, q).reshape(self.xRight-self.xLeft,self.yBottom-self.yTop)
        
                #atomImagePlot([self.AOIImage, gaussianFitImage, fermionFitImage], ['original', 'gaussian', 'fermion'], plotParam, plotStr)
                self.axes3.imshow(fermionFitImage, cmap='gray_r', aspect=1, vmin=-1, vmax=1)
                #self.axes4.imshow(self.AOIImage, cmap='jet', aspect='auto', vmin=-1, vmax=5)
                ### od distribution
                
                data = [self.AOIImage, gaussianFitImage, fermionFitImage]
                
                center = plotParam[0:2]
                sigma = plotParam[2:4]
                
                yy=[]
                for k in range(3):
                   l = radioDistribution(data[k], center, sigma)
                   yy.append(l)
                xx= range(len(yy[0]))
                
                originalLine,  = self.axes4.plot(xx, yy[0], 'g:', label='origianl')
                gaussianLine,  = self.axes4.plot(xx, yy[1], 'r--', label='gaussian')
                fitLine,  = self.axes4.plot(xx, yy[2], 'b-', label='fit')
                

                self.axes4.legend([originalLine, gaussianLine, fitLine], ['original', 'gaussian', 'fermion'])
                
                #plt.title('Density Distribution')
                
            elif self.fitMethodBoson.GetValue():
                print "Start Boson Fit..."
                self.bosonParams = fitData(self.AOIImage, bosonDistribution, mode)
                print self.bosonParams
                self.bosonParams[0] += self.xLeft
                self.bosonParams[1] += self.yTop
                x0, y0, a, b, amplitudeC, offset, amplitudeT, Ca, Cb = self.bosonParams

                print "Create Boson Fit Image..."
                # plotStr.append(str('Condensate Fraction:%0.2f'%(amplitudeC/(amplitudeT+amplitudeC))) )
                bosonFitImage = bosonDistribution(coordinates, x0, y0, a, b, amplitudeC, offset, amplitudeT, Ca, Cb).reshape(self.xRight-self.xLeft,self.yBottom-self.yTop)
                #atomImagePlot([self.AOIImage, gaussianFitImage, bosonFitImage], ['original','gaussian','boson'],  plotParam, plotStr)
                self.axes3.imshow(bosonFitImage, cmap='gray_r', aspect=1, vmin=-1, vmax=1)

                data = [self.AOIImage, gaussianFitImage, bosonFitImage]
                
                center = plotParam[0:2]
                sigma = plotParam[2:4]
                
                yy=[]
                for k in range(3):
                   l = radioDistribution(data[k], center, sigma)
                   yy.append(l)
                xx= range(len(yy[0]))
                
                originalLine,  = self.axes4.plot(xx, yy[0], 'g:', label='origianl')
                gaussianLine,  = self.axes4.plot(xx, yy[1], 'r--', label='gaussian')
                fitLine,  = self.axes4.plot(xx, yy[2], 'b-', label='fit')
                

                self.axes4.legend([originalLine, gaussianLine, fitLine], ['original', 'gaussian', 'boson'])
                


                self.fWidth.SetValue('( %.0f'%self.bosonParams[2] + ' , %.0f )'%self.bosonParams[3])
                self.fq.SetValue('( %.0f'%(1/np.sqrt(self.bosonParams[7])) + ' , %.0f )'%(1/np.sqrt(self.bosonParams[8])))
                self.tOverTF.SetValue('%0.2f'%(amplitudeC/(amplitudeT+amplitudeC)))       

            

            ToF = float(self.tof.GetValue()) / 1000
            omegaAxial = float(self.omegaAxial.GetValue()) * np.pi * 2
            omegaRadial = float(self.omegaRadial.GetValue()) * np.pi * 2
            
            atom = "Li"
            if self.fitMethodBoson.GetValue():
                atom = "Na"
            elif self.fitMethodFermion.GetValue():
                atom = "Li"
            
            if self.fitMethodFermion.GetValue():
                Rx = self.fermionParams[2] * pixelToDistance
                Ry = self.fermionParams[3] * pixelToDistance
                self.q = self.fermionParams[6]

            
            gSigmaX = self.gaussionParams[2] * pixelToDistance
            gSigmaY = self.gaussionParams[3] * pixelToDistance
            
            self.gTmp = temperatureSingleGaussianFit(ToF, gSigmaX, gSigmaY, omegaAxial, omegaRadial, atom) 
            
            self.gTemperature.SetValue(str('( %.0f' % (self.gTmp[0]*1E9)) + ' , ' + '%.0f )' % (self.gTmp[1]*1E9))
            # wx.Yield()

            self.canvas.draw()
            self.Update()
            
            print "Finished Fitting."
        except Exception:

            print 'Sorry. Fitting Failed.'
            
        self.benchmark_endTime=time.time()
        print  "This shot took " + str(abs(self.benchmark_startTime-self.benchmark_endTime)) + " seconds"

        # atomImagePlot([atomImage, gaussianFitImage,parabolicFitImage], ['original image','gaussian fit','parabolic fit'] )
        
        

    def startAutoRun(self, e):
        try:
            if self.autoRunning == False:
                print "Start Auto Run.. Begin Watching File Changes in the Folder..."
                self.autoButton.SetLabel('Auto Fitting... Watching File Changes in the Folder...')
                 
                self.observer = Observer()
                self.observer.schedule(MyHandler(self.autoRun, self), path = self.imageFolderPath.GetValue())

                self.observer.start()
                #self.observer.join()
                self.autoRunning = True
            elif self.autoRunning == True:
                print "Stop Watching Folder."
                self.autoButton.SetLabel('Auto Fit')
                self.observer.stop()
                # self.observer.
                # self.observer.restart()
                self.observer.join()
                self.observer = None
                self.autoRunning = False
        except:
            print "Sorry. There is some problem about auto fit. Please just restart the program."




    def autoRun(self, e):
        self.fitImage(e)
        self.saveResult(e)



    def saveResult(self, e):
        if self.fitMethodFermion.GetValue():
            self.saveFermionResult(e)
        elif self.fitMethodBoson.GetValue():
            self.saveBosonResult(e)
        elif self.fitMethodGaussian.GetValue():
            self.saveGaussianResult(e)

    def saveBosonResult(self, e):
        f = open("C:\\ExperimentImages\\Image-Analysis\\boson_data.txt", "a")
        f.writelines(self.filename + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         # + str(self.gVals[0][0]) + ' , ' + str(self.gVals[0][1]) + ' , ' \
         + self.atomNumberInt.GetValue() + '\t' \
         + str(self.bosonParams[2]) + '\t' + str(self.bosonParams[3]) + '\t' \
         + str(1/np.sqrt(self.bosonParams[7])) + '\t' + str(1/np.sqrt(self.bosonParams[8]))  \
            + '\n') 
        
        f.close()

    def saveFermionResult(self, e):
        f = open("C:\\ExperimentImages\\Image-Analysis\\fermion_data.txt", "a")
        
        f.writelines(self.filename + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         + str(self.gaussionParams[0]) + '\t' + str(self.gaussionParams[1]) + '\t' \
         + self.atomNumberInt.GetValue() + '\t' \
         + str(self.fermionParams[2]) + '\t' + str(self.fermionParams[3]) + '\t' \
         + str(self.fermionParams[6]) + '\n') 
        
        f.close()

    def saveGaussianResult(self, e):
        f = open(LOCAL_PATH + "Image-Analysis\\gaussian_data.txt", "a")
        f.writelines(self.filename + '\t' + self.tof.GetValue() + '\t'\
         # + self.omegaAxial.GetValue() + ' , ' + self.omegaRadial.GetValue() + ' , '\
         + str(self.gaussionParams[0]) + '\t' + str(self.gaussionParams[1]) + '\t' \
         + str(self.atomNumberInt.GetValue()) + '\t' + str(self.atomNumberIntFit.GetValue()) + '\t'\
         + str(self.gaussionParams[2]) + '\t' + str(self.gaussionParams[3]) \
         + '\n') 
        
        f.close()

    def cleanData(self, e):
        if self.fitMethodFermion.GetValue():
            f = open(LOCAL_PATH + "Image-Analysis\\fermion_data.txt", "w")
        elif self.fitMethodBoson.GetValue():
            f = open(LOCAL_PATH + "Image-Analysis\\boson_data.txt", "w")
        f.close()

    def readData(self, e):
        if self.fitMethodFermion.GetValue():
            f = open(LOCAL_PATH + "Image-Analysis\\fermion_data.txt", "r")
            self.data = f.readlines()
        elif self.fitMethodBoson.GetValue():
            f = open(LOCAL_PATH + "Image-Analysis\\boson_data.txt", "r")
            self.data = f.readlines()
        elif self.fitMethodGaussian.GetValue():
            f = open(LOCAL_PATH + "Image-Analysis\\guassian_data.txt", "r")
            self.data = f.readlines()
        # f = open("../data.txt", "r")

        
        
        self.dataReadedText.SetValue("input: %i"%len(self.data))
        
        for i in range(len(self.data)):
            self.data[i] = self.data[i].split(' , ')
        
    
        f.close()

    def fitListData(self, e):
        tofList = []
        RXList = []
        RYList = []
       
        atom = ""

        n = len(self.data)
        for i in self.data:
            tofList.append(float(i[1])/1000.)
            RXList.append(float(i[3]) * pixelToDistance)
            RYList.append(float(i[4]) * pixelToDistance)
           
        if self.fitMethodBoson.GetValue():
            atom = "Na"
        elif self.fitMethodFermion.GetValue():
            atom = "Li"

        tx, ty, wx, wy = dataFit(atom, tofList, RXList, RYList)
        self.fitTempText.SetValue('(%.1f' %(tx*1E9) + ' , ' + '%.1f )' %(ty*1E9))

        self.fitTrapAxialFreqText.SetValue(str('%.1f' % (wy/(2*np.pi))))
        self.fitTrapRadialFreqText.SetValue(str('%.1f' % (wx/(2*np.pi))))
        # self.fitrho0Text.SetValue(str('%.1f' % (t[2]*1E6)))

    def drawAtomNumber(self, e):
        atomNumberI = []
        n = len(self.data)
        for i in self.data:
            atomNumberI.append(int(i[2]))
            # atomNumberC.append(int(i[11]))
        atomNumberPlot(n, atomNumberI)

            
	
class FigurePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,  size=(600, 600))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)

        # self.axes = self.figure.add_subplot(111)
        # self.canvas = FigureCanvas(self, -1, self.figure)
        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.sizer.Add(self.canvas, 1, wx.ALL)
        # print self.sizer
        # self.SetSizer(self.sizer)
        # self.Fit()
        self.canvas = FigureCanvas(self, -1, self.figure)

    def drawFigure(self, data, plotMin, plotMax):
        # t = arange(0.0, 3.0, 0.01)
        # s = sin(2*pi*t)
        # self.axes.plot(t, s)
        self.axes.imshow(data, vmin = plotMin, vmax = plotMax)



        # self.draw()

# plt.subplot(121)
# plt.imshow(AOIImage, vmin = plotMin, vmax = plotMax)
# plt.title("Li Original Img")





if __name__ == '__main__':
  
    app = wx.App()
    ui = ImageUI(None, title='Image Analysis v1.0')
    app.MainLoop()