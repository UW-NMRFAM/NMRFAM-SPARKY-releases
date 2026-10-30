# -----------------------------------------------------------------------------
# Dialog for NPD Plot (Local)
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: April 25, 2015
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import string
import re
import Tkinter

import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox
import math
#import colormap
import os
import os.path
# -----------------------------------------------------------------------------
#def f7(seq):
#    seen = set()
#    seen_add = seen.add
#    return [x for x in seq if not (x in seen or seen_add(x))]
# -----------------------------------------------------------------------------
#
class show_ntdplot_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Titration Plot')
    self.session = session
    
    self.data_list = []
        
    # title
    self.title = tkutil.entry_field(self.top, 'Title: ', 'Titration Plot', 34)
    self.title.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # axis
    self.xlabel = tkutil.entry_field(self.top, 'X Label: ', 'Molar Ratio', 32)
    self.xlabel.frame.pack(side = 'top', fill = 'both', expand = 1)
    self.ylabel = tkutil.entry_field(self.top, 'Y Label: ', 'H (ppm)', 32)
    self.ylabel.frame.pack(side = 'top', fill = 'both', expand = 1)    
    
    # seperator 
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
    inputlabel = tkutil.entry_row(self.top, 'Add Titration Data (X POS can be simple formula)')
    inputlabel.frame.pack(side = 'top', fill = 'both', expand = 1)            
    
    # spectrum
    self.sp = sputil.spectrum_menu(session, self.top, 'Spectrum: ')
    self.sp.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # assignment
    self.asn = tkutil.entry_field(self.top, 'Resonance: ', 'T12H', 32)
    self.asn.frame.pack(side = 'top', fill = 'both', expand = 1)
   
    # X position
    self.xpos = tkutil.entry_field(self.top, 'X POSITION: ', '0', 32)
    self.xpos.frame.pack(side = 'top', fill = 'both', expand = 1)

    # color map
    #initcolors = list(colormap.supported_colors)
    #colors = []
    #for clr in initcolors:
    #  if ' ' not in clr:
    #    colors.append(clr)
    #colors = f7(colors)
    #self.cl1 = tkutil.option_menu(self.top, "", colors, 'blue', 
    #                                alphabet = True)
    #self.cl1.add_entry('Custom', forceroot=True)
    #self.cl1.frame.pack(side = 'top', anchor = 'nw')

    # buttons
    self.br = tkutil.button_row(self.top,
			   ('Update', self.update_cb),			   			   
			   ('Append', self.append_cb),
			   ('Clear', self.clear_cb),
			   ('Plot', self.curve_cb),
#			   ('Shape', self.shape_cb),
			   ('Export to CSV', self.export_cb),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 1)        
        
    # seperator 
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')    
    
    # scrolling_list
    self.listbox = tkutil.scrolling_list(self.top, 'Titration Data', 10)
    self.listbox.frame.pack(side = 'top', fill = 'both', expand = 1)
    self.listbox.listbox.bind('<ButtonRelease-1>', self.move_cb)
    
    # file names
    self.ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    self.ini2_path = os.path.join(os.path.expanduser("~"), 'ndpplot2.ini')
    self.csv_path = os.path.join(os.path.expanduser("~"), 'ntdplot.csv')
    
  # -----------------------------------------------------------------------------
  #
  def append_cb(self):
    import tkMessageBox
    # get selected spectrum
    spec = self.sp.spectrum()
    
    # check x position
    try:
      import __future__
      szXpos = self.xpos.variable.get()
      dXpos = eval(compile(szXpos, '<string>', 'eval', __future__.division.compiler_flag))
    except:
      tkMessageBox.showerror('Error', 'Please set X position.')
      return
      
    # check assignment
    asn = self.asn.variable.get()
    if asn == '':
      tkMessageBox.showerror('Error', 'Please set resonance to trace.')
      return    
      
    # find assignment & c.s.
    iFound = 0
    dCS = 9999
    for peak in spec.peak_list():
      for i in range(len(peak.resonances())):
        resn = peak.resonances()[i]
        if resn == None: continue
        if resn.name == asn:
          dCS = peak.frequency[i]
          iFound = 1
          iDim = i
          break
      if iFound == 1:
        break
    if iFound == 0:        
      tkMessageBox.showerror('Error', 'The assigned resonance could not be found in the peaks.')
      return        
      
    # add to data_list
    iFound = 0
    for data in self.data_list:
      if (data[0] == spec) and (data[1] == asn):
        iFound = 1
        break
    if iFound == 0:    
      self.data_list.append( [spec, asn, dXpos, dCS, szXpos, peak, iDim] )
    
    # update
    self.update_cb()

  # -----------------------------------------------------------------------------
  #
  def update_cb(self):
    # update CS
    for i in range(len(self.data_list)):
      data = self.data_list[i]
      iFound = 0
      dCS = 9999
      for peak in data[0].peak_list():
        for i in range(len(peak.resonances())):
          resn = peak.resonances()[i]
          if resn == None: continue
          if resn.name == data[1]:
            dCS = peak.frequency[i]
            iFound = 1
            break
        if iFound == 1:
          break
      if iFound == 1:
        #self.data_list[i][3] = dCS
        data[3] = dCS
  
    # sort by x_pos
    self.data_list = sorted(self.data_list, key=lambda data: data[2])
        
    # generate ntdplot.csv
    # format is...
    # GROUP XLABEL YLABEL
    # M1     1     VALUE
    f = open(self.csv_path, 'w')
    szHeader = 'spectrum,%s,%s,%s\n' % (self.xlabel.variable.get(), 'xpos', self.ylabel.variable.get())
    f.write(szHeader)
    xmin = 999999999
    xmax = -999999999    
    ymin = 999999999
    ymax = -999999999  
    hmin = 999999999
    hmax = -999999999      
    for data in self.data_list:
      szLine = '%s,%s,%f,%f\n' % (data[0].name, data[4], data[2], data[3])
      if xmin > data[2]: xmin = data[2]
      if xmax < data[2]: xmax = data[2]
      if ymin > data[3]: ymin = data[3]
      if ymax < data[3]: ymax = data[3]            
      if hmin > data[5].data_height: hmin = data[5].data_height
      if hmax < data[5].data_height: hmax = data[5].data_height      
      f.write(szLine)
    f.close()
    rangex = xmax-xmin
    rangey = ymax-ymin
    xmin=xmin-rangex/10.0
    xmax=xmax+rangex/10.0    
    ymin=ymin-rangey/10.0    
    ymax=ymax+rangey/10.0        
    self.listbox.clear()
    f = open(self.ini_path, 'w')
    f.write('[GENERAL_START]\n')
    f.write('TITLE=%s\n' % self.title.variable.get())
    f.write('XLABEL=%s\n' % self.xlabel.variable.get())    
    f.write('YLABEL=%s\n' % self.ylabel.variable.get())        
    f.write('XMIN=%f\n' % xmin)
    f.write('XMAX=%f\n' % xmax)
    f.write('YMIN=%f\n' % ymin)
    f.write('YMAX=%f\n' % ymax)
    f.write('XSCALE=FLOAT\n')    
    f.write('[GENERAL_END]\n')
    f.write('[SERIES1_START]\n')
    f.write('NAME=NMR Titration Data Plot\n')
    f.write('PLOTTYPE=LINE\n')
    f.write('COLORCOUNT=1\n')
    f.write('DATACOUNT=%d\n' % len(self.data_list))
    f.write('COLOR_1=%d,%d,%f,%f,SILVER\n' % (xmin, xmax, ymin, ymax))
    for i in range(1, len(self.data_list)+1):
      data = self.data_list[i-1]
      f.write('DATA_%d=%f,%f,0,%s\n' % (i, data[2], data[3],data[4]))
      # update scroll_list
      self.listbox.append( '%s-%s(%s): %.4f ppm' % (data[4], data[0].name, data[1], data[3]),  {'spec': data[0], 'asn': data[1], 'xpos': data[2], 'ypos': data[3], 'xpos_txt': data[4]})
    f.write('[SERIES1_END]\n')
    f.write('[SERIES2_START]\n')
    f.write('NAME=NMR Titration Data Plot\n')
    f.write('PLOTTYPE=DOT\n')
    f.write('COLORCOUNT=1\n')
    f.write('DATACOUNT=%d\n' % len(self.data_list))
    f.write('COLOR_1=%d,%d,%f,%f,NAVY\n' % (xmin, xmax, ymin, ymax))
    for i in range(1, len(self.data_list)+1):
      data = self.data_list[i-1]
      f.write('DATA_%d=%f,%f,0,%s\n' % (i, data[2], data[3],data[4]))
      # update scroll_list
    f.write('[SERIES2_END]\n')
    f.close()
    if len(self.data_list) < 3:
      return 0
    
    # let's do line shape...
    # it depends what nuclei type we are looking
    # this works only for 2D
    for data in self.data_list:
      if data[0].dimension != 2:
        return 2  # this means non-2D is in the list
        
    rangex = ymax-ymin    # chemical shifts
    elev_step = (hmax-hmin) / 20.0
    elev = 0    
    shift_step = rangex / 99.0  # ymin to ymax
        
    f = open(self.ini2_path, 'w')
    f.write('[GENERAL_START]\n')
    f.write('TITLE=%s\n' % self.title.variable.get())
    f.write('XLABEL=%s\n' % self.ylabel.variable.get())    
    f.write('YLABEL=Data Height\n')
    f.write('XMIN=%f\n' % ymin)
    f.write('XMAX=%f\n' % ymax)
    f.write('YMIN=%f\n' % hmin)
    f.write('YMAX=%f\n' % hmax)
    f.write('XSCALE=FLOAT\n')    
    f.write('[GENERAL_END]\n')
    
    for i in range(len(self.data_list)):
      data = self.data_list[i]      
      f.write('[SERIES%d_START]\n' % (i+1))
      f.write('NAME=%s\n' % data[0].name)
      f.write('PLOTTYPE=LINE\n')
      f.write('COLORCOUNT=1\n')
      f.write('DATACOUNT=100\n')
      f.write('COLOR_1=%d,%d,%f,%f,DEFAULT\n' % (ymin, ymax, hmin, hmax))
      elev = elev_step * float(i)
      iDim = data[6]      
      if iDim == 0:          dStaticShift = peak.frequency[1]
      else:                  dStaticShift = peak.frequency[0]      
      
      for j in range(100):
        # what dimension?- start from 0 <- data[6]
        
        # loop
        # ymin to ymax by step
        dShift = ymin + shift_step * float(j)
          
        # make tuple
        if iDim == 0:
          dTuple = (dShift, dStaticShift)
        else:
          dTuple = (dStaticShift, dShift)
        dHeight = data[0].data_height(dTuple)
        f.write('DATA_%d=%f,%f,%f,%s:%f\n' % (j+1, dShift, dHeight, elev, data[4], dHeight))
             

        
      f.write('[SERIES%d_END]\n' % (i+1))
    f.close()
      
    return 1
  # -----------------------------------------------------------------------------
  #
  def clear_cb(self):
    self.data_list = []
    self.listbox.clear()
    pass  
  # -----------------------------------------------------------------------------
  #
  def curve_cb(self):
    if self.update_cb() == 0: 
      tkMessageBox.showerror("Error", "Data analysis failed.")
      return
    import nmrfam
    nmrfam.run_npdplot(self.session)
  # -----------------------------------------------------------------------------
  #
  def shape_cb(self):
    if self.update_cb() == 0: 
      tkMessageBox.showerror("Error", "Data analysis failed.")
      return
    import nmrfam
    import shutil
    shutil.copyfile(self.ini2_path, self.ini_path)
    nmrfam.run_npdplot(self.session)    
  # -----------------------------------------------------------------------------
  #    
  def move_cb(self, *args):  
    # get assignment from spec
    # center it.
    ds = self.listbox.selected_line_data()
    if len(ds) != 1:
      return
    if ds[0]['spec'] == None:
      return
    spec = ds[0]['spec']  
    asn = ds[0]['asn']

    for peak in spec.peak_list():
      if peak.is_assigned == 0: continue
      for resn in peak.resonances():
        if resn.name == asn:
          sputil.show_peak(peak)       
          return 
          
  # -----------------------------------------------------------------------------
  #
  def export_cb(self):
    if self.update_cb() == 0: 
      tkMessageBox.showerror("Error", "Data analysis failed.")
      return
    # copy 
    path = tkutil.save_file(self.session.tk, "Save file", "Save .csv file")
    if not path: return
    import shutil
    shutil.copyfile(self.csv_path, path)
    tkMessageBox.showinfo("Export", "Saved.") 
                     
def show_ntd_dialog(session):
  sputil.the_dialog(show_ntdplot_dialog,session).show_window(1)
