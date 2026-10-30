# -----------------------------------------------------------------------------
# 1D slice inspecter
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: January 15, 2017
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import string
import Tkinter

import os
import sparky
import sputil
import tkutil
import nmrfam
import pinegraph
import tkMessageBox

# -----------------------------------------------------------------------------
#
class show_1D_inspect_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, '1D inspecter')
    
    self.session = session

    ll = pinegraph.modified_listbox(self.top, 'Select peaks and update:', 52, 8, "single")
    ll.listbox.bind('<ButtonRelease-2>', self.move_to_selected_cb)
    ll.listbox.bind('<Double-ButtonRelease-1>', self.move_to_selected_cb)
    ll.listbox.bind('<ButtonRelease-3>', self.move_to_selected_cb)
    self.label_list = ll
    self.label_list.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
    axis_om = tkutil.option_menu(self.top, "Axis: ", ['w1','w2','w3'], 'w1')
    axis_om.frame.pack(side = 'top', anchor = 'nw')
    self.axis_om = axis_om
    
    sep2 = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep2.pack(fill="both", padx=5,pady=5, side = 'top')
    
    self.br = tkutil.button_row(self.top,
			   ('Update', self.update_cb),
			   ('Fit Selected', self.fit_cb),			   
			   ('Fit All', self.fit_all_cb),			   			   
			   ('Plot', self.plot_cb),
			   ('Close', self.close_cb),			   
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')

  # -----------------------------------------------------------------------------
  #
  def move_to_selected_cb(self):  
    pitem = self.label_list.event_line_data(event)
    if pitem == None:
        return
        
    sputil.show_peak(pitem[1])
  # -----------------------------------------------------------------------------
  #
  def update_cb(self):  
    self.label_list.clear()
    if self.session.project == None: return
    
    peak_list = []
    for spec in self.session.project.spectrum_list():
      for peak in spec.selected_peaks():
        peak_list.append(peak)
    
    # check if they are from all same type spectrum
    if len(peak_list) == 0:
      tkMessageBox.showerror('Error', 'No selected peaks.')
      return
      
    peak_0 = peak_list[0]
    for peak in peak_list:
      if peak_0.spectrum.dimension != peak.spectrum.dimension:
        tkMessageBox.showerror('Error', 'Inconsistent peak properties.')
        return      

      if peak_0.spectrum.nuclei != peak.spectrum.nuclei:
        tkMessageBox.showerror('Error', 'Inconsistent peak properties.')
        return      
              
      if peak_0.volume_method != peak.volume_method:
        tkMessageBox.showerror('Error', 'Inconsistent fitting methods.')
        return      
              
    for peak in peak_list:
        # assign, freq
        szFrequency = ''
        for iDim in range(peak.spectrum.dimension):
          szFrequency = szFrequency + '%.3f' % (peak.frequency[iDim])
          if iDim != peak.spectrum.dimension - 1:
            szFrequency = szFrequency + ','
        szLabel = peak.spectrum.name+':[' + peak.assignment + ']:(' + szFrequency + ')' + '-'
        if peak.fit_height != None:
          szLabel = szLabel + peak.volume_method
        else:
          szLabel = szLabel + 'no fit'
        
        self.label_list.append(szLabel, [peak, szLabel])
  # -----------------------------------------------------------------------------
  #
  def get_view_from_spectrum(self, spec):
    for view in self.session.project.view_list():
      if view.spectrum == spec:
        return view
    return None    

  # -----------------------------------------------------------------------------
  #
  def fit_peak(self, peak):
    view = self.get_view_from_spectrum(peak.spectrum)
    if view == None: return
    peak.fit(view)              
      
  # -----------------------------------------------------------------------------
  #
  def fit_cb(self):  
    for pitem in self.label_list.selected_line_data():
      peak = pitem[0]
      self.fit_peak(peak)
    self.update_cb()          
    return      
  # -----------------------------------------------------------------------------
  #
  def fit_all_cb(self):    
    for pitem in self.label_list.line_data:
      peak = pitem[0]
      self.fit_peak(peak)
    self.update_cb()          
    return        
  # -----------------------------------------------------------------------------
  #
  def plot_cb(self):
    if len(self.label_list.line_data) == 0:
      tkMessageBox.showerror('No data', 'Please select peaks and click update button before plotting.')
      return
      
    if len(self.label_list.line_data) > 10:
      tkMessageBox.showerror('Too many data', 'If you select more than 10 peaks, you will only see summed fit peaks.')
      
      
    
    szW = self.axis_om.get()
    if szW == '':
      tkMessageBox.showerror('Axis error', 'Please select axis to investigate.')
      return    

    peak_0 = self.label_list.line_data[0][0]
    if (peak_0.spectrum.dimension == 2) and szW == 'w3':
      tkMessageBox.showerror('Axis error', 'Please select available axis.')
      return  
    
    iDim = ['w1','w2','w3'].index(szW)
    szNuclei = peak_0.spectrum.nuclei[iDim]
    spec = peak_0.spectrum
      
    xmin = 9999999999
    xmax = -9999999999
    ymin = 9999999999
    ymax = -9999999999
        
    # sort by chemical shift
    itemlist = []
    iFitCount = 0
    for pitem in self.label_list.line_data:
      peak = pitem[0]
      dCS = peak.frequency[iDim]
      if xmin > dCS: xmin = dCS
      if xmax < dCS: xmax = dCS
      if ymin > peak.data_height: ymin = peak.data_height
      if ymax < peak.data_height: ymax = peak.data_height      
      if peak.fit_height != None:
        iFitCount = iFitCount + 1
        if ymin > peak.fit_height: ymin = peak.fit_height
        if ymax < peak.fit_height: ymax = peak.fit_height                    
        
      itemlist.append([dCS, peak])
    itemlist.sort()  
    
    xmargin = (xmax-xmin) * 0.1
    
    if xmargin == 0.0:
      if szNuclei != '1H': xmargin = 2.0
      else: xmargin = 0.2
    xmin = xmin - xmargin
    xmax = xmax + xmargin
    
    if xmin < spec.region[0][iDim]: xmin = spec.region[0][iDim]  
    if xmax > spec.region[1][iDim]: xmax = spec.region[1][iDim]      
    
    ymargin = (ymax - ymin) * 0.1
    ymin = ymin - ymargin
    ymax = ymax + ymargin
    
    # Header
    szHeader = "[GENERAL_START]\n"
    szHeader = szHeader + "TITLE=1D inspection\n"
    szHeader = szHeader + "XLABEL=%s Chemical Shift (ppm)\n" % (szNuclei)
    szHeader = szHeader + "YLABEL=Data Height\n"
    szHeader = szHeader + "XMIN=%f\n" % (xmin)
    szHeader = szHeader + "XMAX=%f\n" % (xmax)
    szHeader = szHeader + "YMIN=%f\n" % (ymin)
    szHeader = szHeader + "YMAX=%f\n" % (ymax)
    szHeader = szHeader + "XSCALE=FLOAT\n"
    szHeader = szHeader + "XINVERT=TRUE\n"    
    szHeader = szHeader + "[GENERAL_END]\n"

    # NOISE     
    szNoise = "[SERIES1_START]\n"
    szNoise = szNoise + "NAME=NOISE LINE\n"
    szNoise = szNoise + "PLOTTYPE=LINE\n"
    szNoise = szNoise + "COLORCOUNT=1\n"
    szNoise = szNoise + "DATACOUNT=2\n"
    szNoise = szNoise + "COLOR_1=%d,%d,%f,%f,BLACK\n" % (-9999999999, 9999999999, -9999999999, 9999999999)
    szNoise = szNoise + "DATA_1=%f,%f,0,middle\n" % (xmin, spec.noise)
    szNoise = szNoise + "DATA_2=%f,%f,0,middle\n" % (xmax, spec.noise)    
    szNoise = szNoise + "[SERIES1_END]\n"

    # DOT
    szDot = "[SERIES2_START]\n"
    szDot = szDot + "NAME=DOT\n"
    szDot = szDot + "PLOTTYPE=DOT\n"
    szDot = szDot + "COLORCOUNT=1\n"
    szDot = szDot + "DATACOUNT=%d\n" % (iFitCount)
    szDot = szDot + "COLOR_1=%d,%d,%f,%f,RED\n" % (-9999999999, 9999999999, -9999999999, 9999999999)
    
    iCurIdx = 1
    for dCS, peak in itemlist:
      if peak.fit_height == None: continue
      szDot = szDot + "DATA_%d=%f,%f,%f,%s\n" % (iCurIdx, dCS, peak.data_height, 0, peak.assignment)
      iCurIdx = iCurIdx + 1
    szDot = szDot + "[SERIES2_END]\n"
    iPeakCount = iCurIdx - 1


    # FIT GRAPH (blue)
    szFit = ""
    iCurIdx = 1
    if len(self.label_list.line_data) <= 10:
      for dCS, peak in itemlist:
        if peak.fit_height == None: continue
        
        szFit = szFit + "[SERIES%d_START]\n" % (iCurIdx+2)
        szFit = szFit + "NAME=FITTED LINE\n"
        if peak_0.volume_method == 'gaussian': 
          szFit = szFit + "PLOTTYPE=GPEAK\n"
        elif peak_0.volume_method == 'lorentzian': 
          szFit = szFit + "PLOTTYPE=LPEAK\n"    
        else:
          szFit = szFit + "PLOTTYPE=DOT\n"        
        szFit = szFit + "COLORCOUNT=1\n"
        szFit = szFit + "COLOR_1=%d,%d,%f,%f,BLUE\n" % (-9999999999, 9999999999, -9999999999, 9999999999)
        szFit = szFit + "DATACOUNT=1\n"      
        szFit = szFit + "DATA_1=%f,%f,%f,%s\n" % (dCS, peak.fit_height, peak.line_width[iDim], peak.assignment)
        szFit = szFit + "[SERIES%d_END]\n" % (iCurIdx+2)     
        iCurIdx = iCurIdx + 1
      
    # SUM OF FIT GRAPH
    szFit = szFit + "[SERIES%d_START]\n" % (iCurIdx+2)
    szFit = szFit + "NAME=SUM FIT\n"
    if peak_0.volume_method == 'gaussian': 
      szFit = szFit + "PLOTTYPE=GPEAK\n"
    elif peak_0.volume_method == 'lorentzian': 
      szFit = szFit + "PLOTTYPE=LPEAK\n"    
    else:
      szFit = szFit + "PLOTTYPE=DOT\n"        
    szFit = szFit + "COLORCOUNT=1\n"
    szFit = szFit + "COLOR_1=%d,%d,%f,%f,GREEN\n" % (-9999999999, 9999999999, -9999999999, 9999999999)
    szFit = szFit + "DATACOUNT=%d\n" % (iPeakCount)
    iCurIdx2 = 1
    for dCS, peak in itemlist:
      if peak.fit_height == None: continue    
      szFit = szFit + "DATA_%d=%f,%f,%f,%s\n" % (iCurIdx2, dCS, peak.fit_height, peak.line_width[iDim], peak.assignment)
      iCurIdx2 = iCurIdx2 + 1                
    szFit = szFit + "[SERIES%d_END]\n" % (iCurIdx+2)
    
    self.ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')    
    
    f = open(self.ini_path, 'w')
    f.write(szHeader+szNoise+szDot+szFit)
    f.close()
    nmrfam.run_npdplot(self.session)               
        
def show_1D_inspect(session):
  sputil.the_dialog(show_1D_inspect_dialog, session).show_window(1)

