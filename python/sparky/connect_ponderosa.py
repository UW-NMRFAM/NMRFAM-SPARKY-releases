
# -----------------------------------------------------------------------------
# Dialog for Ponderosa Analyzer connect.
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Jan 7, 2020
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
# 2D-NOESY and ssNMR spectra are being added in 2020
#
# 0-5   : 3D N-NOESY
# 6-11  : 3D C-NOESY (ali+aro)
# 12-15 : 2D NOESY
# 16-19 : 2D CC
# 20-25 : 3D NCACX
# 26-31 : 3D NCOCX

import string
import re
import Tkinter

import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox
import os
import pinegraph

# -----------------------------------------------------------------------------
#
class connect_ponderosa_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Ponderosa Analyzer Connector')

    cnt = tkutil.file_field(self.top, 'Connection file (sparky.cnt): ', 
                                      'Connection file')
    cnt.frame.pack(side = 'top', anchor = 'w')
    self.cnt_path = cnt
    szCnt = os.getcwd() +  os.sep + "sparky.cnt"
    if os.path.isfile(szCnt):
      self.cnt_path.set(szCnt)
    
    spec_labels = ['15N-NOESY: ', '13C-NOESY(ali-): ', '13C-NOESY(aro-): ',
          '2D NOESY: ', '2D CC: ', '3D NCACX: ', '3D NCOCX: ']
    sm_list = []
    specfrm = Tkinter.Frame(self.top)
    specfrm.pack(side='top', fill = 'both', expand = 0)
    self.specfrm = specfrm

    for lbl in spec_labels:
      spec = sputil.spectrum_menu(session, specfrm, lbl, 
                                allow_no_choice = 1)
      spec.frame.pack(side = 'top', anchor = 'w')
      sm_list.append(spec)
    self.sm_list = sm_list      
    self.nnoe, self.cnoe, self.aronoe, self.hhnoe, self.cc, self.ncacx, \
      self.ncocx = sm_list
    self.showhide = True
    self.n15_ppms = []        # w1, w2, w3 chemical shifts
    self.c13_ppms = []        # w1, w2, w3 chemical shifts
    self.hh_ppms = []         # w1, w2 chemical shifts
    self.ncacx_ppms = []      # w1, w2, w3 chemical shifts
    self.ncocx_ppms = []      # w1, w2, w3 chemical shifts

    btmfrm = Tkinter.Frame(self.top)
    btmfrm.pack(side='bottom', fill = 'both', expand = 1)

    self.br = tkutil.button_row(btmfrm,
			   ('Update', self.update_cb),
			   ('Update (j-i)', self.update_rev_cb),
			   ('Move(NNOE)', self.move_nnoe_cb),
			   ('Move(CNOE)', self.move_cnoe_cb),
			   ('Move(HH)', self.move_hh_cb),
      )
    self.br2 = tkutil.button_row(btmfrm,
         ('Move(CC)', self.move_cc_cb),
			   ('Move(NCACX)', self.move_ncacx_cb),
			   ('Move(NCOCX)', self.move_ncacx_cb),
         ('Show/Hide', self.show_hide_cb),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')
    self.br2.frame.pack(side = 'top', anchor = 'w')
    
    tkutil.create_hint(self.br.buttons[0], 'List correlated NMR peak (i-j) ' +
        'from external program. You do not have to relaunch NMRFAM-Sparky ' +
        'but to click this button.')
    tkutil.create_hint(self.br.buttons[1], 'List correlated NMR peak (j-i) ' + 
        'from external program. You do not have to relaunch NMRFAM-Sparky ' + 
        'but to click this button.')
    tkutil.create_hint(self.br2.buttons[3], 'Show/hide spectrum setting panel.')
    self.label_frame = Tkinter.Frame(btmfrm, width = 500, height = 100)
    self.label_frame.pack(side='top', anchor = 'nw')

    ll = pinegraph.modified_listbox(self.label_frame, 'Label List', 49, 6, 
                                    "single")
    ll.listbox.bind('<Double-ButtonRelease-1>', self.move_to_selected_cb)
    ll.listbox.bind('<ButtonRelease-3>', self.move_to_selected_cb)
    self.label_list = ll
    self.label_list.frame.grid(sticky='news')
 
# ----------------------------------------------------------------------------
  def show_hide_cb(self):
    self.showhide = not self.showhide
    if not self.showhide:
      self.specfrm.forget()
    else:
      self.specfrm.pack(side='top', fill = 'both', expand = 0)
    #for sm in self.sm_list:
    #    sm.frame.forget()
    #  else:
    #    sm.frame.pack(side = 'top', anchor = 'w')

# ----------------------------------------------------------------------------
  def update_sparky_cnt(self, mode):
    # check if user set sparky.cnt file
    # if not, show message
    if self.cnt_path.get() == '' or os.path.isfile(self.cnt_path.get()) == False:
      tkMessageBox.showerror("Connection Error", "Please set valid sparky.cnt.")
      return

    # read sparky.cnt and validate the format
    self.label_list.clear()
    cnt_file = self.cnt_path.get()
    if mode == 1:
      cnt_file = cnt_file + '.rev' # reversed
      
    f = open(cnt_file, 'r')

    self.n15_ppms = []        # w1, w2, w3 chemical shifts
    self.c13_ppms = []        # w1, w2, w3 chemical shifts    
    self.hh_ppms = []         # w1, w2 chemical shifts
    self.ncacx_ppms = []      # w1, w2, w3 chemical shifts
    self.ncocx_ppms = []      # w1, w2, w3 chemical shifts

    cnt_read = f.readlines()
    f.close()
    # if not, show message
    if len(cnt_read) < 12: # we now accept over 12 because 2D HH and SSNMR
      tkMessageBox.showerror("Connection Error", "Please set valid sparky.cnt.")
      return

    for i in range(len(cnt_read)):
      if cnt_read[i] == '\n':
        cnt_read[i] = 'None'
    for i in range(len(cnt_read), 32):
      cnt_read.append('None')

    # N-NOE
    w1 = [cnt_read[0].rstrip(), cnt_read[3].rstrip()]
    w2 = [cnt_read[1].rstrip(), cnt_read[4].rstrip()]
    w3 = [cnt_read[2].rstrip(), cnt_read[5].rstrip()]
    self.n15_ppms = [w1, w2, w3]

    # C-NOE
    w1 = [cnt_read[6].rstrip(), cnt_read[9].rstrip()]
    w2 = [cnt_read[7].rstrip(), cnt_read[10].rstrip()]
    w3 = [cnt_read[8].rstrip(), cnt_read[11].rstrip()]
    self.c13_ppms = [w1, w2, w3]

    # 2D HH
    w1 = [cnt_read[12].rstrip(), cnt_read[14].rstrip()]
    w2 = [cnt_read[13].rstrip(), cnt_read[15].rstrip()]
    self.hh_ppms = [w1, w2]

    # 2D CC
    w1 = [cnt_read[16].rstrip(), cnt_read[18].rstrip()]
    w2 = [cnt_read[17].rstrip(), cnt_read[19].rstrip()]
    self.cc_ppms = [w1, w2]

    # 3D NCACX
    w1 = [cnt_read[20].rstrip(), cnt_read[23].rstrip()]
    w2 = [cnt_read[21].rstrip(), cnt_read[24].rstrip()]
    w3 = [cnt_read[22].rstrip(), cnt_read[25].rstrip()]
    self.ncacx_ppms = [w1, w2, w3]

    # 3D NCOCX
    w1 = [cnt_read[26].rstrip(), cnt_read[29].rstrip()]
    w2 = [cnt_read[27].rstrip(), cnt_read[30].rstrip()]
    w3 = [cnt_read[28].rstrip(), cnt_read[31].rstrip()]
    self.ncocx_ppms = [w1, w2, w3]

    # update labels in the box
    spec_labels = ['15N-NOE: ', '13C-NOE: ', '2D-HH: ',
          '2D-CC: ', 'NCACX: ', 'NCOCX: ']
    ppms = [self.n15_ppms, self.c13_ppms, self.hh_ppms,
            self.cc_ppms, self.ncacx_ppms, self.ncocx_ppms]
    for i in range(len(spec_labels)):
      lbl = spec_labels[i]
      if i in [2, 3]: # 2D
        szLabel = '%s %s[%s]-%s[%s]' % (lbl, ppms[i][0][1], ppms[i][0][0],
                                            ppms[i][1][1], ppms[i][1][0], )
      else:
        szLabel = '%s %s[%s]-%s[%s]-%s[%s]' % (lbl, ppms[i][0][1], ppms[i][0][0],
          ppms[i][1][1], ppms[i][1][0], ppms[i][2][1], ppms[i][2][0])
      self.label_list.append(szLabel, ppms[i])
  
# ----------------------------------------------------------------------------
  def update_cb(self):
    self.update_sparky_cnt(0)
# ----------------------------------------------------------------------------
  def update_rev_cb(self):
    self.update_sparky_cnt(1)
# ----------------------------------------------------------------------------
  def move_nnoe_cb(self):
    # validate 15N label
    if len(self.n15_ppms) != 3:
      tkMessageBox.showerror("Connection Error", "No valid 15N position set.")
      return    
      
    # check if user set spectrum
    if self.nnoe.spectrum() == None: 
      tkMessageBox.showerror("Connection Error", "Please set 15N NOESY.")
      return

    spec = self.nnoe.spectrum()
    specwidth = spec.spectrum_width
    # change order
    # find highest average -> N/C
    # find bigger spectra width and less than 16ppm -> H
    s1, s2, s3 = 'None', 'None', 'None'
    w1, w2, w3 = 'None', 'None', 'None'
    ppms = self.n15_ppms
    if (specwidth[0] > specwidth[1]) and (specwidth[0] > specwidth[2]):
      s1, w1 = ppms[0][0], ppms[0][1]
      if (specwidth[1] < specwidth[2]):
        s2, w2 = ppms[1][0], ppms[1][1]
        s3, w3 = ppms[2][0], ppms[2][1]
      else:
        s3, w3 = ppms[1][0], ppms[1][1]
        s2, w2 = ppms[2][0], ppms[2][1]
    elif (specwidth[1] > specwidth[0]) and (specwidth[0] > specwidth[2]):       
      s2, w2 = ppms[0][0], ppms[0][1]
      if (specwidth[0] < specwidth[2]):
        s1, w1 = ppms[1][0], ppms[1][1]
        s3, w3 = ppms[2][0], ppms[2][1]
      else:
        s3, w3 = ppms[1][0], ppms[1][1]
        s1, w1 = ppms[2][0], ppms[2][1]
    elif (specwidth[2] > specwidth[0]) and (specwidth[2] > specwidth[1]):             
      s3, w3 = ppms[0][0], ppms[0][1]
      if (specwidth[0] < specwidth[1]):
        s1, w1 = ppms[1][0], ppms[1][1]
        s2, w2 = ppms[2][0], ppms[2][1]
      else:
        s2, w2 = ppms[1][0], ppms[1][1]
        s1, w1 = ppms[2][0], ppms[2][1]      
    if 'None' in [s1, s2, s3, w1, w2, w3]:
      tkMessageBox.showerror('Connection Error', 'No valid 15N position set.')
      return      
    
    try:  
      v1, v2, v3 = eval(w1), eval(w2), eval(w3)
    except:
      tkMessageBox.showerror('Connection Error', \
                            'No exact chemical shift match found.')
      return
          

    # move to the 15N, place a peak
    peak = sputil.place_peak_in_spectral_region(spec, (v1, v2, v3))
    if peak == None:
      tkMessageBox.showerror('Connection Error', 'No valid 15N position set.')
      return
    peak.selected = 1
    peak.center()

    # compare two peaks.
    diff = [abs(peak.frequency[0] - v1), abs(peak.frequency[1] - v2),
            abs(peak.frequency[2] - v3)]

    bFine = 1
    for i in range(3):
      if (peak.frequency[i] < 15.0 and diff[i] > 0.05) or \
          (peak.frequency[i] >= 15.0 and diff[i] > 0.5):
        bFine = 0
        break
    if bFine == 0: # original place
      peak.selected = 0
      peak = spec.place_peak((v1, v2, v3))
      tkMessageBox.showerror("Peak center error", 
                "Centered position is a little off from the original" + \
                " position. You will see two peaks.")
    peak.selected = 1

    # append to sparky.out
    szSparkyCnt = self.cnt_path.get()
    szSparkyOut = os.path.splitext(szSparkyCnt)[0] + ".out"
    f = open(szSparkyOut, 'a')
    szLine = '%s-%s-%s-%f-%d\n' % (s1, s2, s3, peak.data_height, 0) # nnoe
    f.write(szLine)
    f.close()

    if peak:
      sputil.show_peak(peak)

# ----------------------------------------------------------------------------
  def move_cnoe_cb(self):
    # validate 13C label
    if len(self.c13_ppms) != 3:
      tkMessageBox.showerror("Connection Error", "No valid 13C position set.")
      return      
    
    # check if user set spectrum
    ppms = self.c13_ppms
    try:
      if float(ppms[0][1]) > 100 or float(ppms[1][1]) > 100 or \
          float(ppms[2][1]) > 100:
        spec = self.aronoe.spectrum()
      else:
        spec = self.cnoe.spectrum()
    except:
      tkMessageBox.showerror("Connection Error", "No valid 13C position.")
      return
              
    if spec == None: 
      tkMessageBox.showerror("Connection Error", "Please set 13C NOESY.")
      return


    # change order
    # find highest average -> N/C
    # find bigger spectra width and less than 16ppm -> H
    specwidth = spec.spectrum_width

    # change order
    # find highest average -> N/C
    # find bigger spectra width and less than 16ppm -> H
    s1, s2, s3 = 'None', 'None', 'None'
    w1, w2, w3 = 'None', 'None', 'None'

    if (specwidth[0] > specwidth[1]) and (specwidth[0] > specwidth[2]):
      s1, w1 = ppms[0][0], ppms[0][1]    
      if (specwidth[1] < specwidth[2]):
        s2, w2 = ppms[1][0], ppms[1][1]
        s3, w3 = ppms[2][0], ppms[2][1]
      else:
        s3, w3 = ppms[1][0], ppms[1][1]
        s2, w2 = ppms[2][0], ppms[2][1]
    elif (specwidth[1] > specwidth[0]) and (specwidth[1] > specwidth[2]):       
      s2, w2 = ppms[0][0], ppms[0][1]
      if (specwidth[0] < specwidth[2]):
        s1, w1 = ppms[1][0], ppms[1][1]
        s3, w3 = ppms[2][0], ppms[2][1]
      else:
        s3, w3 = ppms[1][0], ppms[1][1]
        s1, w1 = ppms[2][0], ppms[2][1]
    elif (specwidth[2] > specwidth[0]) and (specwidth[2] > specwidth[1]):             
      s3, w3 = ppms[0][0], ppms[0][1]
      if (specwidth[0] < specwidth[1]):
        s1, w1 = ppms[1][0], ppms[1][1]
        s2, w2 = ppms[2][0], ppms[2][1]
      else:
        s2, w2 = ppms[1][0], ppms[1][1]
        s1, w1 = ppms[2][0], ppms[2][1]
        
    if 'None' in [s1, s2, s3, w1, w2, w3]:
      tkMessageBox.showerror("Connection Error", "No valid 13C position set.")
      return 
           
    try:  
      v1, v2, v3 = eval(w1), eval(w2), eval(w3)
    except:
      tkMessageBox.showerror("Connection Error", \
                            "No exact chemical shift match found.")
      return
      
    # move to the 13C, place a peak
    peak = sputil.place_peak_in_spectral_region(spec, (v1, v2, v3))
    if peak == None:
      tkMessageBox.showerror('Connection Error', 'No valid 13C position set.')
      return
    peak.selected = 1
    peak.center()

    # compare two peaks.
    diff = [abs(peak.frequency[0] - v1), abs(peak.frequency[1] - v2),
            abs(peak.frequency[2] - v3)]
    
    bFine = 1
    for i in range(3):
      if (peak.frequency[i] < 15.0 and diff[i] > 0.05) or \
        (peak.frequency[i] >= 15.0 and diff[i] > 0.5):
        bFine = 0
        break
    if bFine == 0: # original place
      peak.selected = 0
      peak = spec.place_peak((v1, v2, v3))
      tkMessageBox.showerror("Peak center error", 
                "Centered position is a little off from the original" + \
                " position. You will see two peaks.")
    peak.selected = 1
      
    # append to sparky.out
    szSparkyCnt = self.cnt_path.get()
    szSparkyOut = os.path.splitext(szSparkyCnt)[0] + ".out"
    f = open(szSparkyOut, 'a')
    if v1 > 100 or v2 > 100 or v3 > 100: #aro
      szLine = '%s-%s-%s-%f-%d\n' % (s1, s2, s3, peak.data_height, 2) # aro
    else:
      szLine = '%s-%s-%s-%f-%d\n' % (s1, s2, s3, peak.data_height, 1) # ali
    f.write(szLine)
    f.close()

    if peak:
      sputil.show_peak(peak)
# ----------------------------------------------------------------------------
  def move_hh_cb(self):
    self.move_hh_cc(0)
# ----------------------------------------------------------------------------
  def move_cc_cb(self):
    self.move_hh_cc(1)
# ----------------------------------------------------------------------------
  def move_hh_cc(self, mode):    
    if mode == 0:
      ppms = self.hh_ppms
      spec = self.hh.spectrum()
      exp = 'H-H NOESY'
      tol = 0.05
    elif mode == 1:
      ppms = self.cc_ppms
      spec = self.cc.spectrum()
      exp = 'C-C'
      tol = 1.0

    if len(ppms) != 2:
      tkMessageBox.showerror("Connection Error", 
        "No valid %s position set." % (exp))
      return
    
    if spec == None: 
      tkMessageBox.showerror("Connection Error", 
        "Please set %s." % (exp))
      return
    specwidth = spec.spectrum_width # we do not change order
    s1, w1 = ppms[0][0], ppms[0][1]
    s2, w2 = ppms[1][0], ppms[1][1]
    if 'None' in [s1, s2, w1, w2]:
      tkMessageBox.showerror("Connection Error", 
        "No valid %s position set." % (exp))
      return
    
    try:
      v1, v2 = eval(w1), eval(w2)
    except:
      tkMessageBox.showerror("Connection Error", \
                            "No exact chemical shift match found.")
      return
    
    try:
      dh = abs(spec.data_height((v1, v2)))
    except:
      dh = -10**10
    try:
      dh2 = abs(spec.data_height((v2, v1)))
    except:
      dh2 = -10**10
    
    if dh < 0 and dh2 < 0:
      tkMessageBox.showerror('Connection Error', 
        'No valid %s position set.' % (exp))
      return

    bSwap = False
    if dh > dh2:
      peak = sputil.place_peak_in_spectral_region(spec, (v1, v2))
    else:
      peak = sputil.place_peak_in_spectral_region(spec, (v2, v1))
      bSwap = True

    if peak == None:
      tkMessageBox.showerror('Connection Error', 
        'No valid %s position set.' % (exp))
      return
      
    peak.selected = 1
    peak.center()

    if not bSwap:
      diff = [abs(peak.frequency[0] - v1), abs(peak.frequency[1] - v2)]
    else:
      diff = [abs(peak.frequency[1] - v2), abs(peak.frequency[0] - v1)]
    if diff[0] > tol and diff[1] > tol:
      peak.selected = 0
      if not bSwap: peak = spec.place_peak((v1, v2))
      else: peak = spec.place_peak((v2, v1))
      tkMessageBox.showerror("Peak center error", 
                "Centered position is a little off from the original" + \
                " position. You will see two peaks.")
    peak.selected = 1      

    # append to sparky.out
    szSparkyCnt = self.cnt_path.get()
    szSparkyOut = os.path.splitext(szSparkyCnt)[0] + ".out"
    f = open(szSparkyOut, 'a')
    szLine = '%s-%s-%f-%d\n' % (s1, s2, peak.data_height, 3+mode)
    f.write(szLine)
    f.close()

    if peak:
      sputil.show_peak(peak)
# ----------------------------------------------------------------------------
  def move_ncacx_cb(self):
    self.move_ncacx_ncocx(0)
# ----------------------------------------------------------------------------
  def move_ncocx_cb(self):
    self.move_ncacx_ncocx(1)
# ----------------------------------------------------------------------------
  def move_ncacx_ncocx(self, mode):
    if mode == 0:
      exp = 'NCACX'
      ppms = self.ncacx_ppms
      spec = self.ncacx.spectrum()
    elif mode == 1:
      exp = 'NCOCX'
      ppms = self.ncocx_ppms
      spec = self.ncocx.spectrum()
    if len(ppms) != 3:
      tkMessageBox.showerror("Connection Error", 
                            "No valid %s position set." % (exp))
      return
    
    if spec == None: 
      tkMessageBox.showerror("Connection Error", "Please set %s." % (exp))
      return
    specwidth = spec.spectrum_width
    s1, s2, s3 = 'None', 'None', 'None'
    w1, w2, w3 = 'None', 'None', 'None'
    if spec.nuclei[0] == '15N': # N
      s1, w1 = ppms[0][0], ppms[0][1]
      if specwidth[1] < specwidth[2]: # CA/O-CX
        s2, w2 = ppms[1][0], ppms[1][1]
        s3, w3 = ppms[2][0], ppms[2][1]
      else: # CX-CA/O
        s2, w2 = ppms[2][0], ppms[2][1]
        s3, w3 = ppms[1][0], ppms[1][1]        
    elif spec.nuclei[1] == '15N': # N
      s2, w2 = ppms[0][0], ppms[0][1]
      if specwidth[0] < specwidth[2]: # CA/O-CX
        s1, w1 = ppms[1][0], ppms[1][1]
        s3, w3 = ppms[2][0], ppms[2][1]
      else: # CX-CA/O
        s1, w1 = ppms[2][0], ppms[2][1]
        s3, w3 = ppms[1][0], ppms[1][1]
    elif spec.nuclei[2] == '15N':
      s3, w3 = ppms[0][0], ppms[0][1]
      if specwidth[0] < specwidth[1]: # CA/O-CX
        s1, w1 = ppms[1][0], ppms[1][1]
        s2, w2 = ppms[2][0], ppms[2][1]
      else: # CX-CA
        s1, w1 = ppms[2][0], ppms[2][1]
        s2, w2 = ppms[1][0], ppms[1][1]
    else: # error
      tkMessageBox.showerror("Connection Error", 
                  "Please set correct %s." % (exp))
      return
    try:  
      v1, v2, v3 = eval(w1), eval(w2), eval(w3)
    except:
      tkMessageBox.showerror("Connection Error", \
                            "No exact chemical shift match found.")
      return
    peak = sputil.place_peak_in_spectral_region(spec, (v1, v2, v3))
    if peak == None:
      tkMessageBox.showerror('Connection Error', 
                  'No valid %s position set.' % (exp))
      return
    peak.selected = 1
    peak.center()

    # compare two peaks
    diff = [abs(peak.frequency[0] - v1), abs(peak.frequency[1] - v2),
            abs(peak.frequency[2] - v3)]
    
    bFine = 1
    for i in range(3):
      if diff[i] > 1.0: 
        bFine = False
        break
    if bFine == 0: # original
      peak.selected = 0
      peak = spec.place_peak((v1, v2, v3))
      tkMessageBox.showerror("Peak center error", 
                "Centered position is a little off from the original" + \
                " position. You will see two peaks.")
    peak.selected = 1

    # append to sparky.out
    szSparkyCnt = self.cnt_path.get()
    szSparkyOut = os.path.splitext(szSparkyCnt)[0] + ".out"
    f = open(szSparkyOut, 'a')
    szLine = '%s-%s-%s-%f-%d\n' % (s1, s2, s3, peak.data_height, 5+mode)
    f.write(szLine)
    f.close()

    if peak:
      sputil.show_peak(peak)
# ----------------------------------------------------------------------------
  def move_to_selected_cb(self, event):
    # Get currently double clicked item
    ilines = self.label_list.selected_line_numbers()
    if len(ilines) == 0: 
      tkMessageBox.showerror("Connection Error", "Please select a label.")
      return    

    # Parsing d-clicked item
    if ilines[0] == 0:
      self.move_nnoe_cb()
    elif ilines[0] == 1:
      self.move_cnoe_cb()
    elif ilines[0] == 2:
      self.move_hh_cb()
    elif ilines[0] == 3:
      self.move_cc_cb()
    elif ilines[0] == 4:
      self.move_ncacx_cb()
    elif ilines[0] == 5:
      self.move_ncocx_cb()
# -----------------------------------------------------------------------------
#
def connect_ponderosa_analyzer(session):
  sputil.the_dialog(connect_ponderosa_dialog,session).show_window(1)
  