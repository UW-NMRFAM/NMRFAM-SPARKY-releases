# -----------------------------------------------------------------------------
# Generate UPL, LOL files from NOESY spectra
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: March 3, 2018
# 
# -----------------------------------------------------------------------------

import os
import tkutil
import sputil
import Tkinter
import tkMessageBox
import myseq

# upl_lol.generate_upl_lol_wlt( [(spec1,type2),(spec2,type2)], 'noe.upl', 0.33333 ) 
# type_list = ('DO NOT APPLY', '15N-NOESY', '13C-NOESY (ali)', '13C-NOESY (aro)', '2D-NOESY')
# -----------------------------------------------------------------------------
#
def generate_upl_wlt(spec_list, path, dApprox, dRef):
  (root, ext) = os.path.splitext(path) 
  path2 = root + '.wlt'       
  
  numpy_exist = 0
  try:  
    import numpy
    wlt_array = numpy.zeros((1000, 1000))
    numpy_exist = 1    
  except:
    pass

  cutoff = 5.5
  vdw = 2.4
  tol = 1.4    # 40% tolerance
  
  total_peak_list = []
  for (spec,type_om) in spec_list:
    if type_om.get() == 'DO NOT APPLY':        continue
    if spec == None: continue

    dMax = -9999999999
    dMin = 9999999999
    #peaks = sputil.sort_peaks_by_assignment(spec.spectrum().peak_list(), self)      
    peaks = spec.spectrum().peak_list()
    if len(peaks) == 0: continue
    
    frequency_list = []
    
    # 2D 
    for peak in peaks:
      if peak.is_assigned == 0: continue
      if peak.data_height == None: continue
      #if peak.data_height < 0: continue      
      
      if (abs(peak.frequency[0] - peak.frequency[1]) < 0.03): continue 
        
      if spec.spectrum().dimension == 2:
        if abs(peak.data_height) > dMax: dMax = abs(peak.data_height)        
        if abs(peak.data_height) < dMin: dMin = abs(peak.data_height)
              
      # 3D  
      elif spec.spectrum().dimension == 3:
      # if this peak is diagonal, continue
        if (abs(peak.frequency[0] - peak.frequency[2]) < 0.03): continue
        if (abs(peak.frequency[1] - peak.frequency[2]) < 0.03): continue
        
        if abs(peak.data_height) > dMax: dMax = abs(peak.data_height)        
        if abs(peak.data_height) < dMin: dMin = abs(peak.data_height)
        
      frequency_list.append( peak.frequency )
        
    if (dMax < -999999998) or (dMin > 999999998): continue

    # start calculating calibration constant
    
    if (dMin == 0.0) or (abs(-1.0+(dMax / dMin)**dApprox) < 0.0001):
      constant = 1
    else:   
      constant = (cutoff - vdw) / (-1.0 + (dMax / dMin)**dApprox)
    
    # calculate upper limits!
    for peak in spec.spectrum().peak_list():
      if peak.data_height == None: continue
      if peak.is_assigned == 0: continue
      height = abs(peak.data_height)
      if height == 0: height = 1 # to avoid floating point error
      #if peak.data_height <= 0: continue
      
      # find peak at the same position
      
      # count and divide the amplitude
      # iCount = 1
      iCount = 0
      for freq in frequency_list:
        if freq == peak.frequency:
          iCount = iCount+1
      
      if iCount == 0: continue    
      #for peak2 in spec.spectrum().peak_list():
      #  if peak2.is_assigned == 0: continue        
      #  iSame = 1
      #  for iDim in range(spec.spectrum().dimension):
      #  
      #    if spec.spectrum().nuclei[iDim] != '1H': dTol = 0.4
      #    else: dTol = 0.03
      #    
      #    if abs(peak.frequency[iDim] - peak2.frequency[iDim]) > dTol: 
      #      iSame = 0
      #      break
      #  if iSame == 1: iCount = iCount + 1  
        
      upl_limit = vdw + (-1.0 + (dMax / ( abs(height) / float(iCount)) )**dApprox) * constant
      #upl_limit = upl_limit * tol        
      total_peak_list.append( (peak, upl_limit) )
      
  # delete same constraints    
  total_upl_list = []        
  for (peak, upl_limit) in total_peak_list:
    groupatoms = sputil.parse_assignment(peak.assignment) # (('M3','CA'), ('M3','N'), ('M3','H'))
    if len(groupatoms) < 2: continue
    
    protons = []
    
    for groupatom in groupatoms:
      if groupatom[0] == '' or groupatom[1] == '':        continue
      if groupatom[1][0] != 'Q' and groupatom[1][0] != 'H' and groupatom[1][0] != 'M': continue
      atom = 'H' + groupatom[1][1:]
      #atom[0] = 'H' # change to H anyway
      ga = sputil.parse_group_name(groupatom[0])             # ('M', 3)
      if ga[0] == '' or ga[1] == '': continue
      szAAA = myseq.a2aaa(ga[0])
      if szAAA == 'XXX': continue                
      protons.append((szAAA, ga[1], atom))
    if len(protons) != 2: 
      continue
    proton1 = protons[0]
    proton2 = protons[1]
    
    if proton1[0] == proton2[0] and proton1[1] == proton2[1]: 
      continue # diagonal doesn't need to be here
    
    if numpy_exist == 1:
      wlt_array[proton1[1],proton2[1]] = 1
      wlt_array[proton2[1],proton1[1]] = 1
          
    iFound = 0  # this is for removing duplications
    for i in range(len(total_upl_list)):
      upl = total_upl_list[i]
      proton3 = upl[0]
      proton4 = upl[1]
      upl_limit2 = upl[2]
      if (proton1==proton3 and proton2==proton4) or (proton1==proton4 and proton2==proton3):
        # use small limit
        if upl_limit < upl_limit2:
          total_upl_list[i][2] = upl_limit
        iFound = 1
        break
    if iFound == 0:
      # this is new upl
      total_upl_list.append( [proton1, proton2, upl_limit] )
  
  dRatio = 1.0
  dDiff = 0.0
  
  if len(total_upl_list) != 0 and dRef != 0.0:
    dSum = 0
    for (proton1, proton2, upl_limit) in total_upl_list:
      dSum += (upl_limit-dRef)
    dAvg = dRef + dSum / float(len(total_upl_list))
    dRatio = dRef / dAvg       
    dDiff = dRef-dAvg
    
    
  # done here. let's save it as a file
  f = open(path, 'w')
  for (proton1, proton2, upl_limit) in total_upl_list:
    #szLine = '%3d %3s %4s %5d %3s %4s %8.2f\n' % (proton1[1], proton1[0], proton1[2], proton2[1], proton2[0], proton2[2], upl_limit * dRatio)
    szLine = '%3d %3s %4s %5d %3s %4s %8.2f\n' % (proton1[1], proton1[0], proton1[2], proton2[1], proton2[0], proton2[2], upl_limit + dDiff)  
    f.write(szLine)
    if abs(proton1[1] - proton2[1]) < 2: continue
    if numpy_exist == 1:
      wlt_array[proton1[1],proton2[1]] = 1
      wlt_array[proton2[1],proton1[1]] = 1      
  f.close()  
  if numpy_exist == 1:  
    f = open(path2, 'w')
    iCount = 0
    for i in range(len(wlt_array)):
      for j in range(len(wlt_array[i])):
        if wlt_array[i][j] < 0.5: continue
        if abs(i-j) < 3: continue
        szLine = '%3d XXX %3d XXX\n' % (i, j)
        f.write(szLine)
        iCount = iCount+1
    f.close()  
  return total_upl_list, iCount
    
# -----------------------------------------------------------------------------
#
class generate_upl_lol_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Generate distance constraints')

    self.spec_list = []
    self.session = session
    for i in range(0,5):
      spec_frame = Tkinter.Frame(self.top, width = 500, height = 25)
      spec_frame.pack(side = 'top', anchor = 'nw')
      
      spec = sputil.spectrum_menu(session, spec_frame, 'Spectrum: ')
      spec.frame.pack(side = 'top', anchor = 'w')
      
      type_list = ('DO NOT APPLY', '15N-NOESY', '13C-NOESY (ali)', '13C-NOESY (aro)', '2D-NOESY')
      type_om = tkutil.option_menu(spec_frame, "type: ", type_list, 'DO NOT APPLY')
      type_om.frame.pack(side = 'top', anchor = 'nw')

      self.spec_list.append( (spec, type_om) )
      sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
      sep.pack(fill="both", padx=5,pady=5, side = 'top')          

    # 
    dref = tkutil.entry_field(self.top, 'Auto calibration (empty to pass): ', initial = 4.5, width = 5)
    dref.frame.pack(side = 'top')
    self.dref = dref.variable     
    
    approx_type_list = ('r^-3 approximation','r^-4 approximation','r^-5 approximation','r^-6 approximation')
    self.approx_type = tkutil.option_menu(self.top, "Approx. :", approx_type_list, 'r^-3 approximation')
    self.approx_type.frame.pack(side = 'top', anchor = 'nw')
    
    #      
    self.spec_list.append( (spec, type_om) )
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')          
      
    self.br = tkutil.button_row(self.top,
			   ('Generate', self.generate_cb),
			   ('Run Ponderosa Client', self.run_pc_cb),
	   	   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')

  def generate_cb(self):  
    path = tkutil.save_file(self.session.tk, "Save file", "Save .upl and .wlt file")
    if not path: return
    
    filepath = os.path.splitext(path)
    if filepath[1] != '.upl':
      tkMessageBox.showinfo('Warning', 'File extension will be forced to be .upl.')
      path = filepath[0] + '.upl'
      
    # approx
    szApprox = self.approx_type.get()
    dApprox = 0.3333
    if szApprox == 'r^-3 approximation':      dApprox = 1.0 / 3.0
    elif szApprox == 'r^-4 approximation':    dApprox = 1.0 / 4.0
    elif szApprox == 'r^-5 approximation':    dApprox = 1.0 / 5.0
    elif szApprox == 'r^-6 approximation':    dApprox = 1.0 / 6.0 

    # okay. let's use averaged calibration- 4.5A
    try:
      dRef = float(self.dref.get())
    except:
      dRef = 0.0
            
    total_upl_list, iCount = generate_upl_wlt(self.spec_list, path, dApprox, dRef)
    
    tkMessageBox.showinfo('Finished', '%d constraints in .upl and %d constraints in .wlt finished.' % (len(total_upl_list), iCount) )
            
  def run_pc_cb(self):
    import nmrfam
    nmrfam.run_ponderosa_client(self.session)  

# -----------------------------------------------------------------------------
#
def generate_upl_lol(session):
  sputil.the_dialog(generate_upl_lol_dialog,session).show_window(1)
