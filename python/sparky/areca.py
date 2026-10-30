# -----------------------------------------------------------------------------
# Dialog for ARECA.
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: May 24, 2017
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import string
import re
import Tkinter

import sparky
import sputil
import tkutil
import tkMessageBox
import os
import os.path
import pinegraph


# -----------------------------------------------------------------------------
#
class show_areca_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Show ARECA lists')
    
    self.session = session
    
    areca = tkutil.file_field(self.top, 'ARECA file: ', 'Browse...', width = 30)
    areca.frame.pack(side = 'top', anchor = 'w')
    self.areca_path = areca
    
    spec = sputil.spectrum_menu(session, self.top, 'NOESY Spectrum: ')
    spec.frame.pack(side = 'top', anchor = 'w')    
    self.spec = spec
    
    self.cutoff_list=('0.05','0.10','0.15','0.20','0.25','0.30','0.35','0.40','0.45','0.50','0.55','0.60','0.65',
                  '0.70','0.75','0.80','0.85','0.90','0.95')    
    self.cutoff1_om = tkutil.option_menu(self.top, "Good ARECA cutoff", self.cutoff_list, '0.70')
    self.cutoff1_om.frame.pack(side = 'top', anchor = 'nw')    
    self.cutoff2_om = tkutil.option_menu(self.top, "Intermediate ARECA cutoff", self.cutoff_list, '0.40')
    self.cutoff2_om.frame.pack(side = 'top', anchor = 'nw')                          
    
    self.br = tkutil.button_row(self.top,
			   ('Read', self.read_cb),
			   ('Deploy peaks', self.deploy_cb),
			   ('Close', self.close_cb),			   
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')
    self.sort_label = Tkinter.Label(self.top, text = 'Sort by...')
    self.sort_label.pack(side = 'top', anchor = 'w')
    self.br2 = tkutil.button_row(self.top,
			   ('Label', self.sort_label_cb),
			   ('prob.', self.sort_prob_cb),
			   ('w1', self.sort_w1_cb),
			   ('w2', self.sort_w2_cb),
			   ('w3', self.sort_w3_cb),			   			   
			   )
    self.br2.frame.pack(side = 'top', anchor = 'w')    
  	    
    
#    self.label_frame = Tkinter.Frame(self.top, width = 500, height = 100)
#    self.label_frame.pack(side='top', anchor = 'nw')    
    
    ll = pinegraph.modified_listbox(self.top, 'ARECA labels', 52, 8, "multiple")
    ll.listbox.bind('<ButtonRelease-1>', self.select_peak_cb)
    ll.listbox.bind('<ButtonRelease-2>', self.move_to_selected_cb)    
    ll.listbox.bind('<Double-ButtonRelease-1>', self.move_to_selected_cb)        
    ll.listbox.bind('<ButtonRelease-3>', self.move_to_selected_cb)
    self.label_list = ll
    self.label_list.frame.pack(side = 'top', fill = 'both', expand = 1)
#    self.label_list.frame.grid(sticky='news')
    
  # -----------------------------------------------------------------------------
  #
  def read_cb(self):
    if self.areca_path.get() == '' or os.path.isfile(self.areca_path.get()) == False:
      tkMessageBox.showerror("ARECA Error", "Please set valid ARECA file.")
      return
    f = open(self.areca_path.get(), 'r')
    areca_read = f.readlines()
    f.close()
    
    if len(areca_read) < 2:
      tkMessageBox.showerror("ARECA Error", "Please set valid ARECA file.")
      return

    # clear label_list first
    self.label_list.clear()
    for i in range(len(areca_read)):
      if i < 2: continue  # head and blank
      szLine = areca_read[i]
      splited = szLine.split()
      if len(splited) != 5: continue # assignment  w1   w2   w3   prob
      pdNumbers = [eval(splited[1]), eval(splited[2]), eval(splited[3]), eval(splited[4])]
      szLabel = '%-22s %7.3f %7.3f %7.3f %5.3f' % (splited[0], pdNumbers[0], pdNumbers[1], pdNumbers[2], pdNumbers[3])
      self.label_list.append(szLabel, [splited[0], pdNumbers[0], pdNumbers[1], pdNumbers[2], pdNumbers[3]])
      
  def deploy_cb(self):
    if len(self.label_list.line_data) == 0:
      return
    if self.spec == None:
      return
      
    loop_list = self.label_list.selected_line_data()
    if len(loop_list) == 0: loop_list = self.label_list.line_data
    
    
    for label in loop_list:
      szLabel = label[0]
      w1 = label[1]
      w2 = label[2]
      w3 = label[3]            
      prob = label[4]
      peak = self.spec.spectrum().place_peak( (w1, w2, w3) )
      asns = sputil.parse_assignment(szLabel)
      for i in range(len(asns)):
        asn = asns[i]
        peak.assign(i, asn[0], asn[1])
      if prob >= eval(self.cutoff1_om.get()):
        peak.color = 'green'
      elif prob >= eval(self.cutoff2_om.get()):
        peak.color = 'yellow'
      else:
        peak.color = 'red'
      try:  
        peak.note = '%5.3f' % prob  
      except:
        pass
      cur_label = peak.show_assignment_label()
      cur_label.color = peak.color
      
    tkMessageBox.showinfo("ARECA deploy", "ARECA deployment finished.")
  # ---------------------------------------------------------------------------
  # Sorting
  #!    
  def sort_label_cb(self):
    temp_list = self.label_list.line_data
    
    temp_list.sort()
    self.label_list.clear()
    
    for label in temp_list:
      szLabel = '%-22s %7.3f %7.3f %7.3f %5.3f' % (label[0], label[1], label[2], label[3], label[4])    
      self.label_list.append(szLabel, label)
    
  def sort_by_type(self, iType):
    temp_list = self.label_list.line_data
    
    for label in temp_list:
      #tkMessageBox.showinfo('before', '%d' % (len(label)) )
      label.insert(0, label[iType+1])
      #tkMessageBox.showinfo('after', '%d' % (len(label)) )      
    if iType == 3:
      temp_list.sort()
    else:    
      temp_list.sort()
    self.label_list.clear()
    
    for label in temp_list:
      szLabel = '%-22s %7.3f %7.3f %7.3f %5.3f' % (label[1], label[2], label[3], label[4], label[5])    
      self.label_list.append(szLabel, label[1:6])
      
  def sort_w1_cb(self):
    self.sort_by_type(0)
    
  def sort_w2_cb(self):
    self.sort_by_type(1)  
    
  def sort_w3_cb(self):
    self.sort_by_type(2)
    
  def sort_prob_cb(self):
    self.sort_by_type(3)  
  # ---------------------------------------------------------------------------
  # select peak
  #!    
  def select_peak_cb(self, event):
    freq = []
    ranges = []    

    # set ranges depending on atom types
    for atom_type in self.spec.spectrum().nuclei:
      if atom_type == '1H':
        ranges.append(0.04)
      elif atom_type == '13C':
        ranges.append(0.6)
      elif atom_type == '15N':
        ranges.append(0.6)    

    self.session.unselect_all_ornaments()
    
    for label in self.label_list.selected_line_data():
      freq = label[1:3]      
      peak = sputil.closest_peak(freq, self.spec.spectrum().peak_list(), ranges)
      peak.selected = 1     
         
  # ---------------------------------------------------------------------------
  # Move to current selected
  #!
  def move_to_selected_cb(self, event): 
    if self.spec == None:
      return 
    ilines = self.label_list.event_line_data(event)
    if ilines == None or len(ilines) == 0:
      tkMessageBox.showinfo("ARECA error", "Please select a label.")    
      return
  
    freq = ilines[1:3]
    ranges = []    

    # set ranges depending on atom types
    for atom_type in self.spec.spectrum().nuclei:
      if atom_type == '1H':
        ranges.append(0.04)
      elif atom_type == '13C':
        ranges.append(0.6)
      elif atom_type == '15N':
        ranges.append(0.6)
                     
    peak = sputil.closest_peak(freq, self.spec.spectrum().peak_list(), ranges)
    if peak:
      sputil.show_peak(peak)    
# -----------------------------------------------------------------------------
#
def show_areca(session):
  sputil.the_dialog(show_areca_dialog,session).show_window(1)
  
# -----------------------------------------------------------------------------
#
class show_areca_export_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Generate ARECA inut files')

    self.spec_list = []
    self.session = session
    for i in range(0,5):
      spec_frame = Tkinter.Frame(self.top, width = 500, height = 25)
      spec_frame.pack(side = 'top', anchor = 'nw')
      
      spec = sputil.spectrum_menu(session, spec_frame, 'Spectrum: ')
      spec.frame.pack(side = 'top', anchor = 'w')
      
      type_list = ('DO NOT APPLY', '15N-NOESY', '13C-NOESY (ali)', '13C-NOESY (aro)')
      type_om = tkutil.option_menu(spec_frame, "type: ", type_list, 'DO NOT APPLY')
      type_om.frame.pack(side = 'top', anchor = 'nw')

      self.spec_list.append( (spec, type_om) )
      
      sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
      sep.pack(fill="both", padx=5,pady=5, side = 'top')      

    self.br = tkutil.button_row(self.top,
			   ('Export and Open ARECA', self.export_cb),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')  
# -----------------------------------------------------------------------------
#
  def export_cb(self):
    iBMRB = 1
    #if tkMessageBox.askyesno('Export','Do you want to add BMRB headers and footers in .str file?'):
    #  iBMRB = 1  
    options = {}
    options['title'] = 'Select a directory to save input files.'
    path = tkFileDialog.askdirectory(**options)
    session = self.session
    if path:
      # Peak list files
      for (spec,type_om) in self.spec_list:
        if type_om.get() == 'DO NOT APPLY':        continue
        if spec == None: continue  
        spectrum = spec.spectrum()
        
        f = open(path + os.sep + spectrum.name + '.list', 'w')      
        szHeader = '      Assignment    '
        szHead = '?'
        for i in range(spectrum.dimension-1):
            szHeader = szHeader + '   w%d   ' % (i+1)
            szHead = szHead + '-?'
        szHeader = szHeader + '   w%d   ' % (spectrum.dimension)              
        szHeader = szHeader + 'Data Height\n\n'
        f.write(szHeader)            
  
        peaks = spec.spectrum().peak_list()
        for peak in peaks:      
            if peak.data_height == None: continue     
            szWrite = '%10s' % szHead
            for i in range(spectrum.dimension):
                szWrite = szWrite + '%9.3f' % (peak.frequency[i])
            szWrite = szWrite + '%16.3f' % (peak.data_height)                  
            szWrite = szWrite + '\n'
            f.write(szWrite)
        f.close()
      
      # Assignment file
      f = open(path + os.sep + 'assignment_bmrb21.str', 'w')  
      if iBMRB == 1:
        # add header
        szWrite = 'loop_\n'
        f.write(szWrite)
        szWrite = '    _Atom_shift_assign_ID\n'
        f.write(szWrite)          
        szWrite = '    _Residue_seq_code\n'
        f.write(szWrite)          
        szWrite = '    _Residue_label\n'
        f.write(szWrite)          
        szWrite = '    _Atom_name\n'
        f.write(szWrite)          
        szWrite = '    _Atom_type\n'
        f.write(szWrite)          
        szWrite = '    _Chem_shift_value\n'
        f.write(szWrite)          
        szWrite = '    _Chem_shift_value_error\n'
        f.write(szWrite)          
        szWrite = '    _Chem_shift_ambiguity_code\n\n'
        f.write(szWrite)          
      iLine = 1                  
      for condition in session.project.condition_list():
        for resonance in condition.resonance_list():
          if resonance.deviation > 1:
            continue
          iAmb = 0    
          if pinelayout.pseudo_layout.has_key(resonance.group.symbol):
            if pinelayout.pseudo_layout[resonance.group.symbol].has_key(resonance.atom.name):
              iAmb = 1
          if pinelayout.meta_layout.has_key(resonance.group.symbol):
            if pinelayout.meta_layout[resonance.group.symbol].has_key(resonance.atom.name):
              iAmb = 1                  
          aaa = myseq.a2aaa(resonance.group.symbol)
          if aaa == '': continue
          szWrite = '%5d %5d %5s %5s %6s %9.3f %7.3f %3d\n' % (iLine, resonance.group.number, aaa, resonance.atom.name, resonance.atom.name[0:1], resonance.frequency,1.000, iAmb)
          iLine = iLine+1
          f.write(szWrite)
      if iBMRB == 1:
        # add footer    
        szWrite = '\nstop_\nsave_\n'
        f.write(szWrite)
      f.close()

      import webbrowser
      webbrowser.open('http://areca.nmrfam.wisc.edu')
# -----------------------------------------------------------------------------
#
def show_areca_export(session):
  sputil.the_dialog(show_areca_export_dialog,session).show_window(1)    
