# -----------------------------------------------------------------------------
# Read peak list dialog
# -----------------------------------------------------------------------------
#
# improved by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Nov 2, 2018
# 
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Read a peak list and create peaks in a spectrum.
# Auto dimension detection

import string
import Tkinter

import pyutil
import sparky
import sputil
import tkutil

# -----------------------------------------------------------------------------
#
class read_peaks_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    tkutil.Dialog.__init__(self, session.tk, 'Read Peak List')

    plp = tkutil.file_field(self.top, 'Peak file: ', 'peaklist')
    plp.frame.pack(side = 'top', anchor = 'w')
    self.peak_list_path = plp
    
    sc = sputil.spectrum_menu(session, self.top, 'Spectrum: ')
    sc.frame.pack(side = 'top', anchor = 'w')
    self.spectrum_choice = sc

    sl = tkutil.scrolling_list(self.top, 'Unreadable lines', 5)
    sl.frame.pack(side = 'top', anchor = 'w', fill = 'both', expand = 1)
    self.unreadable = sl
    
    progress_label = Tkinter.Label(self.top, anchor = 'nw')
    progress_label.pack(side = 'top', anchor = 'w')

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
 
    # Use auto dimension detection
    self.autodim = Tkinter.IntVar()
    self.autodim.set(0)
    self.autodim_cb = Tkinter.Checkbutton(self.top, text = 'Auto detect dimensions', variable = self.autodim, onvalue=1, offvalue = 0)
    self.autodim_cb.pack(side = 'top', anchor = 'w', expand = 0)
    
    br = tkutil.button_row(self.top,
         ('Create peaks', self.read_cb),
         ('Label peaks', self.label_cb),			   
         ('Stop', self.stop_cb),
         ('Close', self.close_cb),
         ('Help', sputil.help_cb(session, 'ReadPeaks')),
         )
    br.frame.pack(side = 'top', anchor = 'w')
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
            
    tol_frame = Tkinter.Frame(self.top)
    tol_frame.pack(side = 'top', fill='both')
       
    self.ntol = tkutil.entry_field(tol_frame, 'N tol.:', initial = 0.350, width = 5)
    self.ntol.frame.grid(row = 0, column=0)     
    self.ntol_ppm = self.ntol.variable
    self.dNtol = 0.35
          
    self.ctol = tkutil.entry_field(tol_frame, ', C tol.:', initial = 0.350, width = 5)
    self.ctol.frame.grid(row = 0, column=2)
    self.ctol_ppm = self.ctol.variable     
    self.dCtol = 0.35
         
    self.htol = tkutil.entry_field(tol_frame, ', H tol.:', initial = 0.025, width = 5)
    self.htol.frame.grid(row=0, column=4)    
    self.htol_ppm = self.htol.variable
    self.dHtol = 0.025

    tkutil.Stoppable.__init__(self, progress_label, br.buttons[2])

  # ---------------------------------------------------------------------------
  #
  def read_cb(self):

    self.unreadable.listbox.delete('0' ,'end')
    spectrum = self.spectrum_choice.spectrum()
    path = self.peak_list_path.get()
    if spectrum and path:
      self.stoppable_call(self.read_peaks, path, spectrum)

  # ---------------------------------------------------------------------------
  #
  def label_cb(self):

    self.unreadable.listbox.delete('0' ,'end')
    spectrum = self.spectrum_choice.spectrum()
    path = self.peak_list_path.get()
    if spectrum and path:
      self.stoppable_call(self.label_peaks, path, spectrum)
  # ---------------------------------------------------------------------------
  #
  def detect_dimensions(self, lines, spectrum):
    dim_list = []
    avg_list = []
    dif_list = []
    sorted_list = []
    idx_list = []
    rmin = spectrum.region[0]
    rmax = spectrum.region[1]
    ravg = []
    rwid = []
    for i in range(spectrum.dimension):
      dim_list.append([i, i]) # default: 0->0, 1->1, 2->2
      avg_list.append(0)
      dif_list.append([])
      sorted_list.append([])
      ravg.append( (rmin[i]+rmax[i])/2.0 )
      rwid.append( rmax[i] - rmin[i] )

    # if check button is not set, just go
    if self.autodim.get() == 0:
      return dict(dim_list)
    
    # the way it detects dimensions
    # 1. Use nuclei specific frequency
    # 2. Intensity at peak position
    
    # nuclei check
    #	  region = ((.4, -.5), (11.6, 10.7))	# (min-ppm, max-ppm)
    iLineCount = 0
    for line in lines:
      pinfo = self.parse_peak_line(line, spectrum.dimension)
      if pinfo == None: continue
      assignment, lbl, frequency, note = pinfo
      for j in range(len(frequency)):
        avg_list[j] = avg_list[j] + frequency[j]
      iLineCount = iLineCount+1
    if iLineCount == 0:
      return dict(dim_list) # not a good file
      
    for i in range(spectrum.dimension):
      avg_list[i] = avg_list[i] / float(iLineCount)
      
    # just find the best.
    # digits
    for i in range(spectrum.dimension):
      # dimensions
      for j in range(spectrum.dimension):
        dif_list[i].append(abs(avg_list[i]-ravg[j])/rwid[j])
      sorted_list[i] = sorted_list[i] + sorted(dif_list[i])
      idx_list.append(dif_list[i].index(sorted_list[i][0]))
    if len(list(set(idx_list))) != len(idx_list): 
      return dict(dim_list)    # not distinguishable
    
    for i in range(spectrum.dimension):
      dim_list[i][1] = idx_list[i] # distinguishable
    return dict(dim_list)
  # ---------------------------------------------------------------------------
  #
  def read_peaks(self, path, spectrum):

    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    
    self.dim_dict = self.detect_dimensions(lines, spectrum)

    count = 0
    self.stoppable_loop('peaks', 100)
    for line in lines:
      self.check_for_stop()
      count = count + self.create_peak(line, spectrum)

    msg = ('%d peaks created\n' % count +
     '%d unreadable lines shown below' % (len(lines) - count))
    self.unreadable.heading['text'] = msg

  # ---------------------------------------------------------------------------
  #
  def label_peaks(self, path, spectrum):

    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    
    self.dim_dict = self.detect_dimensions(lines, spectrum)
    
    try:
      self.dNtol = float(self.ntol_ppm.get())
      self.dCtol = float(self.ctol_ppm.get())
      self.dHtol = float(self.htol_ppm.get())            
    except:
      import tkMessageBox
      tkMessageBox.showerror('Warning', 'Tolerances are not set correctly. Default will be used.')
      self.dNtol = 0.35
      self.dCtol = 0.35
      self.dHtol = 0.025
      self.ntol_ppm.set(0.35)
      self.ctol_ppm.set(0.35)
      self.htol_ppm.set(0.025)
      
    count = 0
    self.stoppable_loop('peaks', 100)
    for line in lines:
      self.check_for_stop()
      
      ires = self.label_peak(line, spectrum)
      if ires == 1:
        count = count + 1
      elif ires == 0:  
        self.unreadable.listbox.insert('end', line)
      else: pass

    msg = ('%d peaks labeled\n' % count +
     '%d unlabelable lines shown below' % (len(lines) - count))
    self.unreadable.heading['text'] = msg
    
  # ---------------------------------------------------------------------------
  #
  def create_peak(self, line, spectrum):

    pinfo = self.parse_peak_line(line, spectrum.dimension)
    if pinfo:
      assignment, lbl, frequency, note = pinfo
      frequency2 = [0.,0.,0.,0.]
      for a in range(spectrum.dimension):
        b = self.dim_dict[a]
        frequency2[b] = frequency[a]
      frequency2 = frequency2[0:spectrum.dimension]
      peak = spectrum.place_peak(frequency2)
      self.move_peak_onto_spectrum(peak)

      assigned = 0
      if assignment != None:
        for a in range(spectrum.dimension):
          b = self.dim_dict[a]
          group_name, atom_name = assignment[a]
          if group_name or atom_name:
            peak.assign(b, group_name, atom_name)
            assigned = 1
      elif lbl != None:
        peak.show_label(lbl)
        
      if assigned:
        peak.show_assignment_label()
        
      if note:
        peak.note = note
        
      peak.selected = 1
      return 1
    
    return 0
    
# ---------------------------------------------------------------------------
  #
  def label_peak(self, line, spectrum):

    pinfo = self.parse_peak_line(line, spectrum.dimension)

    tol_list = []
    for nuclei in spectrum.nuclei:
      if nuclei == '1H': tol_list.append(self.dHtol)
      elif nuclei == '13C': tol_list.append(self.dCtol)
      elif nuclei == '15N': tol_list.append(self.dNtol)      
      else: tol_list.append(0.1) # arbitrary

    closest_peak = None    
    
    if pinfo:
      assignment, lbl, frequency, note = pinfo
      frequency2 = [0.,0.,0.,0.]
      for a in range(spectrum.dimension):
        b = self.dim_dict[a]
        frequency2[b] = frequency[a]
      frequency2 = frequency2[0:spectrum.dimension]
      
      pool_list = []
      for peak in spectrum.peak_list():
        # is this a peak in the tolerance ?
        isInTol = 1
        for i in range(len(peak.frequency)):
          if abs(peak.frequency[i]-frequency2[i]) > tol_list[i]:
            isInTol = 0
            break
        if isInTol == 1:
          pool_list.append(peak)
        
      for peak in pool_list:
        dist = 0
        for i in range(len(peak.frequency)):
          dist = dist + pow(abs(peak.frequency[i]-frequency2[i]) / tol_list[i], 2)
          
        if closest_peak == None:
          closest_peak = peak
          nearest_dist = dist
          continue
          
        if nearest_dist > dist:
          closest_peak = peak
          nearest_dist = dist
    else:
      return -1
      
    if closest_peak == None:
      return 0
      
    if closest_peak.is_assigned == 0:
      for i in range(spectrum.dimension):
        b = self.dim_dict[i]
        group_name, atom_name = assignment[b]
     
        assigned = 0
        if group_name or atom_name:
          closest_peak.assign(b, group_name, atom_name)
          assigned = 1
          
      if assigned and note:          
        closest_peak.note = note
          
      if assigned:
        closest_peak.show_assignment_label()
        closest_peak.selected = 1           
        return 1     
      
      return 0
    
    # create same peak
    assigned = 0
    for i in range(spectrum.dimension):
      b = self.dim_dict[i]
      group_name, atom_name = assignment[b]
      if group_name or atom_name:
        assigned = 1
    if assigned == 0:
      return 0
      
    new_peak = spectrum.place_peak(closest_peak.frequency)
    self.move_peak_onto_spectrum(new_peak)
                 
    for i in range(spectrum.dimension):
      b = self.dim_dict[i]
      group_name, atom_name = assignment[b]
      if group_name or atom_name:
        new_peak.assign(b, group_name, atom_name)

    if note:
      new_peak.note = note
      new_peak.selected = 1
        
    new_peak.show_assignment_label()        
    return 1

  # ---------------------------------------------------------------------------
  # If the peak is off the edge of the spectrum, fold it onto the spectrum
  # and set the alias to keep its frequency the same.
  #
  def move_peak_onto_spectrum(self, peak):

    freq = peak.frequency
    pos = sputil.alias_onto_spectrum(freq, peak.spectrum)
    if pos != freq:
      peak.position = pos
      peak.alias = pyutil.subtract_tuples(freq, pos)

  # ---------------------------------------------------------------------------
  #
  def parse_peak_line(self, line, dim):

    fields = string.split(line, None, dim + 1)
    if len(fields) < dim + 1:
      return None

    assignment = sputil.parse_assignment(fields[0])
    lbl = None
    if assignment == None or len(assignment) != dim:
      lbl = fields[0]
      assignment = None
      #self.unreadable.listbox.insert('end', line)
      #return None

    frequency = []
    try:
      for a in range(dim):
        f = pyutil.string_to_float(fields[a+1])
        if f == None:
          self.unreadable.listbox.insert('end', line)
          return None
        frequency.append(f)
    except:
      return None

    if len(fields) > dim + 1:
      note = fields[dim + 1]
    else:
      note = ''

    return (assignment, lbl, frequency, note)

# -----------------------------------------------------------------------------
#
def read_peak_list(session):
  sputil.the_dialog(read_peaks_dialog,session).show_window(1)
