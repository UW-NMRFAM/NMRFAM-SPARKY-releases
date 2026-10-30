# -----------------------------------------------------------------------------
# Dialog for assignment of PINE outputs.
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Jan 28, 2018
# 
# Usage:
#
# I recommend to use this dialog with peak list(lt) dialog.
# First, select spectrum to assign by clicking the spectrum window.
# Second, press "lt" to show up peak list dialog.
# Third, select wanted peak which you want to assign from the dialog.
# Fourth, press "pr" to show up this dialog.
# Fifth, select possible assignment and press "Assign" button or just click 
#     "Best Prop." button if you want to choose an assignment which is the 
#     best probability.
# Sixth, press "Floating Labels" to select floating labels, select the spectrum
#     window, and press delete key to remove them. 
# Seventh, do third step to sixth step repeatedly. Substitute fourth step with 
#     pressing "Update" button of this dialog.
# 
# -----------------------------------------------------------------------------
import math
import string
import types
import Tkinter
import atoms
import pyutil
import sparky
import sputil
import tkutil
import tkFileDialog
import tkMessageBox
import pinegraph
import pinelayout
import os
import os.path
import myseq

# -----------------------------------------------------------------------------
#
class pine_dialog(tkutil.Dialog, tkutil.Stoppable):
  # ---------------------------------------------------------------------------
  #
  def __init__(self, session):
    # Initialize variables
    self.peak = None
    self.graph_dialog = None      
    self.spectrum_text = None
    self.peak_text = None
    self.label_box = None
    self.label_list = None
    self.br = None
    self.br2 = None
    self.progress_label = None
    
    tkutil.Dialog.__init__(self, session.tk, 'Pine Assigner')
    #self.top.grab_set()
    #self.top.focus_set()
    keypress_cb = pyutil.precompose(sputil.command_keypress_cb, session)
    self.top.bind('<KeyPress>', keypress_cb)
    
    self.session = session
    self.UpdateDialog()
  # ---------------------------------------------------------------------------
  #
  def keypress_cb(self, event):
      self.session.command_characters(event.char)
  # ---------------------------------------------------------------------------
  # Generate objects inside this dialog.
  # 
  def UpdateDialog(self):
    # Clear objects
    if self.spectrum_text <> None:
        self.spectrum_text.frame.destroy()
    if self.peak_text <> None:
        self.peak_text.frame.destroy()
    if self.label_box <> None:
        self.label_box.destroy()
    if self.br <> None:
        self.br.frame.destroy()
    if self.br2 <> None:
        self.br2.frame.destroy()        
    if self.progress_label <> None:
        self.progress_label.destroy()    
    
    # Set up selected spectrum
    self.spectrum = self.session.selected_spectrum()

    # There should be selected spectrum
    if self.spectrum == None:
        self.close_cb()
        
    # There should be one selected peak    
    peaks = self.spectrum.selected_peaks()
    
    if len(peaks) > 0:
        self.peak = peaks[0]
    else:
        self.close_cb()

    # Create label object for showing spectrum name
    t = tkutil.entry_row(self.top, 'Selected Spectrum: ' + self.spectrum.name)
    t.frame.pack(side = 'top', anchor = 'w')
    self.spectrum_text = t

    # Dunno why 'len(peaks) > 0' is not working 
    if self.peak <> None:
        if self.spectrum.dimension == 2:
            u = tkutil.entry_row(self.top, 'Selected Peak: %7.3f,%7.3f' % (self.peak.frequency[0],self.peak.frequency[1]) )
        elif self.spectrum.dimension == 3:
            u = tkutil.entry_row(self.top, 'Selected Peak: %7.3f,%7.3f,%7.3f' % (self.peak.frequency[0],self.peak.frequency[1],self.peak.frequency[2]) )
        else:
            u = tkutil.entry_row(self.top, 'Selected Peak: %7.3f,%7.3f,%7.3f,%7.3f' % (self.peak.frequency[0],self.peak.frequency[1],self.peak.frequency[2],self.peak.frequency[3]) )
        u.frame.pack(side = 'top', anchor = 'w')
        self.peak_text = u
        
        # Create listbox object for showing labels
        lbLabel = self.label_list_box(self.top)                         # List box
        lbLabel.pack(side = 'top', fill = 'both', expand = 1)
        self.label_box = lbLabel
        self.LabelBox()                           # Set up label list box


    # Create Buttons
    progress_label = Tkinter.Label(self.top, anchor = 'nw')
    progress_label.pack(side = 'top', anchor = 'w')   
    self.progress_label = progress_label
   
    self.br = tkutil.button_row(self.top,
                           ('Update', self.UpdateDialog),         # Func
                           ('Assign', self.Assign),         # Func
                           ('Best Prob.', self.AssignTheBest),
                           ('UnAssign', self.UnAssign),     # Func
                          )
    self.br2 = tkutil.button_row(self.top,
                           ('Floating Labels', self.FloatingLabel),
                           ('Graph...', self.Graph),        # Func
                           ('Stop', self.stop_cb),
                           ('Close', self.close_cb),
                           #('Help', sputil.Help(session, 'PineAssign')),
                          )
    self.br.frame.pack(side = 'top', anchor = 'w')
    self.br2.frame.pack(side = 'top', anchor = 'w')
     
    tkutil.Stoppable.__init__(self, progress_label, self.br2.buttons[2])
    #self.top.grab_set()
    #self.top.focus_set() 
  # ---------------------------------------------------------------------------
  #
  def Close(self):        # M1N-M1CB-M1H[1.0]
      #self.close_sb
      self.close_cb()

  # ---------------------------------------------------------------------------
  #
  def label_list_box(self, parent):

    pl = tkutil.scrolling_list(parent, 'Choose possible resonance assignments by PINE', 8)
    pl.listbox.bind('<Double-ButtonRelease-1>', self.Assign_cb)          # Func
    pl.listbox.bind('<ButtonRelease-3>', self.Assign_cb)          # Func
    self.label_list = pl
    
    return pl.frame
 
  # ---------------------------------------------------------------------------
  # Fill label box
  def LabelBox(self):
    
    self.label_list.clear()

    # append labels which are located on the selected peak
    iIndex = -1
    if self.spectrum == None:                   # if there is no selected spectrum, exit this function.
        return
    if self.peak == None:
        return
    szPos = '('
    for pos in self.peak.frequency:
        szPos = szPos + ('%7.3f,' % pos).strip() 
    szPos = szPos.rstrip(',')
    szPos = szPos + ')'
    #----------------------------------------------------------------------------------------------
    f = open(self.spectrum.save_path + '_pl', 'r')
    try:
        for label in f.readlines():
            label = label.strip()
            if label.find(szPos) <> -1:
                #tkMessageBox.showinfo('szPos',szPos)
                # find label object
                iFound = 0
                for pLabel in self.spectrum.label_list():
                    if pLabel.text == label:
                        iFound = 1
                        break
                if iFound == 1:
                    self.label_list.append(label, pLabel)
                else:
                    self.label_list.append(label, None) 
                if self.peak.is_assigned == 1:
                    asns = sputil.parse_assignment(self.peak.assignment)
                    filled_assignment = ''
                    for asn in asns:
                        filled_assignment = filled_assignment + asn[0] + asn[1] + '-'
                    filled_assignment = filled_assignment.rstrip('-')
#                        tkMessageBox.showinfo('filled',filled_assignment)
                    if label.find(filled_assignment) <> -1:
                        iIndex = self.label_list.listbox.size()-1
#                    if self.peak.is_assigned == 1 and label.find(self.peak.assignment) <> -1: 
#                        iIndex = self.label_list.listbox.size()-1
                
    finally:
        f.close()
        
    if iIndex <> -1:
        self.label_list.listbox.selection_set(iIndex, )
        self.label_list.listbox.see(iIndex)
       
  def FloatingLabel(self):
    # if already assigned, clear labels
    self.peak.selected = 0
    
    for pLabel in self.spectrum.label_list():
        pLabel.selected = 0
        for idx in range(self.label_list.listbox.size()):
            label = self.label_list.listbox.get(idx)
            if pLabel.text == label:
                pLabel.selected = 1
                break

  # ---------------------------------------------------------------------------
  # "Best Prob."
  def AssignTheBest(self):
    if len(self.label_list.line_data) == 0:
        return
    self.spectrum = self.session.selected_spectrum()
    if self.spectrum == None: 
        return
    peaks = self.spectrum.selected_peaks()
    if len(peaks) > 0:
        if self.peak <> peaks[0]:
            self.UpdateDialog()
    else:
        return
        
    # find best line data
    dTemp = 0.0
    dMax = 0.0
    max_Label = None
    for pLabel in self.label_list.line_data:
        line_data = pLabel.text
        szSplited = line_data.split('[')
        szSplited2 = szSplited[1].split(']')
        dTemp = eval(szSplited2[0])
        if dTemp > dMax:
            dMax = dTemp
            max_Label = pLabel
    if max_Label <> None:
        if self.peak.is_assigned:
            self.UnAssign()
        pLabel2 = max_Label.text.split('[')
        pList = pLabel2[0].split('-')
        
        for i in range(len(pList)):
            tAssign = sputil.split_group_atom(pList[i])
            self.peak.assign(i, tAssign[0], tAssign[1])
        self.peak.show_assignment_label()    
    # select !!
    self.LabelBox()
    # select floating labels
    self.FloatingLabel()
    self.session.command_characters("")    

  def Assign_cb(self, event):
      self.Assign()
                  
  def Assign(self):
    # First, check selected peak and label
    # Second, assign selected peak by selected label
    # Selected peak and label should be one
    if self.label_list == None:
        return
    
    if len(self.label_list.selected_line_numbers()) == 0:
        return
    
    label = self.label_list.listbox.get(self.label_list.selected_line_numbers()[0])   

    # UnAssign
    if self.peak.is_assigned:
        self.UnAssign()
    
    # Assign - # M1CA-M1N-M1H[1.0]:(xxx.xxx,x.xxx,x.xxx)
    pLabel = label.split('[')   # M1CA-M1N-M1H   
    pList = pLabel[0].split('-')   # (M1CA, M1N, M1H)
   
    for i in range(len(pList)):
        tAssign = sputil.split_group_atom(pList[i])        # (M1, CA)
        self.peak.assign(i, tAssign[0], tAssign[1])
    self.peak.show_assignment_label()
            
    #self.peak.selected = 1
    #self.Update()
    # select floating labels
    self.FloatingLabel()
    self.LabelBox()
    self.session.command_characters("")    
    
  def UnAssign(self):
    for i in range(self.spectrum.dimension):
        self.peak.assign(i, '', '')
    self.label_list.listbox.selection_clear(0, 'end')
    self.FloatingLabel()
 
  # -----------------------------------------------------------------------------
  # Shows visualized diagram of assignments
  def Graph(self): 
      self.peak.selected = 1
      sputil.the_dialog(pinegraph.pine_graph, self.session).show_window(1)
      return    
# -----------------------------------------------------------------------------
#
def show_pine_assigner(session):
  sputil.the_dialog(pine_dialog,session).show_window(1)
  
# -----------------------------------------------------------------------------
# Choose the best probability calculated by PINE for all peaks. 
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: July 9, 2008
# 
#
# Usage:
# 
# First, select spectrum which you want to assign all by best probabilities.
# Second, press "ab", then it will take some time to assign all.
# Third, after processing is done, all floating labels are selected. Press delete key to remove them.
# Finally you can see all assigned peaks by the best results of PINE.
#
# -----------------------------------------------------------------------------
def best_assign(session):
    
    setup_dialog = sputil.the_dialog(base_prob, session)
    setup_dialog.show_window(1)

        
# -----------------------------------------------------------------------------
# Select spectra, expected peaks, and tolerances for assigner_dialog.
#
class base_prob(tkutil.Dialog, tkutil.Not_Stoppable):

  def __init__(self, session):

    self.session = session

    tkutil.Dialog.__init__(self, session.tk, 'Assign the best by PINE')
    
    label = Tkinter.Label(self.top, text = 'Base Probability(0.0~1.0):')
    label.pack(side = 'left')
    v = Tkinter.StringVar(self.top)
    v.set('0.9')
    self.variable = v
    entry = Tkinter.Entry(self.top, textvariable = v, width = 5)
    entry.pack(side = 'left')
        
    br = tkutil.button_row(self.top,
                           ('Assign', self.assign_wrap_cb),
                           ('Cancel', self.close_cb),
               )
    br.frame.pack(side = 'top', anchor = 'w')
  def assign_wrap_cb(self):
    self.assign_cb(self.session.selected_spectrum())
  # ---------------------------------------------------------------------------
  #
  def assign_cb(self, spectrum):
   
    if spectrum == None:
        return
    
    szPrb = self.variable.get()
    dPrb = eval(szPrb)
    
    if len(spectrum.selected_peaks()) == 0:
        peaks = spectrum.peak_list()
    else:
        peaks = spectrum.selected_peaks()
    
    for pLabel in spectrum.label_list():
        pLabel.selected = 0
    
    pParsedLabelList = []
    pLabelList = []
    pSameList = []
    pFloatList = []
    pProbList = []  
     
    iTotal = len(peaks)
    iAssigned = 0

    # generate empty list
    for i in range(2100):
        pParsedLabelList.append([])

    # parse labels
    for pLabel in spectrum.label_list():
        splited = pLabel.text.split(':')
        if len(splited) == 1: continue

        szLabel = (splited[0].split('['))[0]
        szProb = (((splited[0].split('['))[1]).split(']'))[0]
        try:
            fProb = float(szProb)
            if fProb < dPrb: continue        # probability higher than dPrb will not be used
        except:
            continue
        splited2 = splited[1].split('(')        # (53.2120,124.321,8.23400)
        splitedsplited = splited2[1].split(')')
        pos = splitedsplited[0].split(',')      # 53.2120,124.321,8.23400

        if len(pos) == 0: continue
        if pos[0] == '?': continue
        try:
            idx = int(eval(pos[0]) * 10.0 + 100.0)
            if idx < 0 or idx > 2099: continue
            fPos = []
            for p in pos:
                 fPos.append(eval(p))
        except:
            continue
        pParsedLabelList[idx].append( [fPos, fProb, szLabel, pLabel]  )
            
    for pPeak in peaks:
        if pPeak.is_assigned == 1:
            continue;
        pPeak.selected = 0
        del pLabelList[:]
        del pFloatList[:]
        del pProbList[:]

        idx = int(pPeak.position[0]*10.0 + 100.0)
        if idx < 1 or idx > 2098: continue

        pTempLabelList = pParsedLabelList[idx-1]+pParsedLabelList[idx]+pParsedLabelList[idx+1] 

        for (fPos, fProb, szLabel, pLabel) in pTempLabelList:
            bSame = 1
            for i in range(len(fPos)):
                if abs(pPeak.frequency[i]*1000.0 - fPos[i]*1000.0) > 1:
                    bSame = 0
                    break
                    
            if bSame == 0: continue
            pFloatList.append(pLabel)
            pLabelList.append(szLabel)
            pProbList.append(fProb)

        # The best is the first
        if len(pProbList) == 0:          continue

        # Get maximum probability
        pmax = 0.0
        idx = -1
        for i in range(len(pProbList)):
            if pmax < pProbList[i]:
                pmax = pProbList[i]
                idx = i
        line_data = pLabelList[idx]
        pList = line_data.split('-')   # (M1CA, M1N, M1H)
        for i in range(len(pList)):
            tAssign = sputil.split_group_atom(pList[i])        # (M1, CA)
            pPeak.assign(i, tAssign[0], tAssign[1])
        pPeak.show_assignment_label()

        for pLabel in pFloatList:
            pLabel.selected = 1
        iAssigned = iAssigned + 1

    self.session.command_characters("")

    szAssigned = '%d of %d peaks assigned.' % (iAssigned, iTotal)
    tkMessageBox.showinfo('Assign the Best by Pine', szAssigned)
    self.close_cb()

# -----------------------------------------------------------------------------
# Export to PINE for better accuracy. 
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facility at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Oct 10, 2008
# 
#
# Usage:
# 
#    1) Type "eb" and type file name to save.
#    2) Open PINE web page with your web browser and select the file by pressing "Browse" button of "Pre-assignment".
#    3) Fill other blanks.
#    4) Press "Submit" button.
# -----------------------------------------------------------------------------
def a2aaa(a):
    lAAA = ["ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL"]
    lA = ["A", "R", "N", "D", "C", "Q", "E", "G", "H", "I", "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"]
    if not a in lA:
      return ''    
    index = lA.index(a)
    return lAAA[index]

def select_all_float_labels(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pLabel in spectrum.label_list():
    if pLabel.peak <> None or pLabel.text == '?-?' or pLabel.text == '?-?-?' or pLabel.text == '?-?-?-?':
      pLabel.selected = 0
    else:
      if pLabel.text.find(']:(') <> -1:
        pLabel.selected = 1
      else:
        pLabel.selected = 0


def export_pine(session):
    options = {}
    options['title'] = 'Select a directory to save input files.'
    path = tkFileDialog.askdirectory(**options)
#    path = tkutil.save_file(session.tk, "Save to PINE input file", "save to pine input")
    if path:
      # Peak list files
      for spectrum in session.project.spectrum_list():
          f = open(path + os.sep + spectrum.name + '.list', 'w')      
          szHeader = '      Assignment    '
          szHead = '?'
          for i in range(spectrum.dimension-1):
              szHeader = szHeader + '   w%d   ' % (i+1)
              szHead = szHead + '-?'
          szHeader = szHeader + '   w%d   ' % (spectrum.dimension)              
          szHeader = szHeader + 'Data Height\n\n'
          f.write(szHeader)    
            
          for peak in spectrum.peak_list():
              if peak.data_height == None: continue
              szWrite = '%10s' % szHead
              for i in range(spectrum.dimension):
                  szWrite = szWrite + ' %8.3f' % (peak.frequency[i])
              szWrite = szWrite + ' %16.3f' % (peak.data_height)                  
              szWrite = szWrite + '\n'
              f.write(szWrite)
          f.close()
      
      # Pre-assignment file
      

      #iBMRB = 0
      
      #if tkMessageBox.askyesno(title='Export',message='Do you want to add BMRB headers and footers in .str file?', default="yes"):
      #    iBMRB = 1
          # add header

      groups = []
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
              aaa = a2aaa(resonance.group.symbol)
              if aaa == '': continue
              atom_type = resonance.atom.name[0:1]
              if (atom_type == 'Q') or (atom_type == 'M'): atom_type = 'H' 
              group = [resonance.group.number, aaa, resonance.atom.name, atom_type, resonance.frequency,1.000, iAmb]
              groups.append(group)
      groups.sort()

      if len(groups) > 0:      

        f = open(path + os.sep + 'preassignment.str', 'w')            
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
        for group in groups:
            szWrite = '%5d %5d %5s %5s %6s %9.3f %7.3f %3d\n' % (iLine, group[0], group[1], group[2], group[3], group[4], group[5], group[6])
            iLine = iLine+1
            f.write(szWrite)
        #if iBMRB == 1:
        # add footer    
        szWrite = '\nstop_\nsave_\n'
        f.write(szWrite)
        f.close()
      
      #if tkMessageBox.askyesno('Export','Finished. Do you want to open PINE web page?'):
      import webbrowser
      webbrowser.open('http://pine3.nmrfam.wisc.edu')
      
      
      
      
# -----------------------------------------------------------------------------
# Convert PINE to Sparky resonance list. 
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facility at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Aug 10, 2015
# #
# Usage:
# 
#    1) Type "ip" and select PINE output files.
#    2) Set file to save.
#    3) Select base threshold to convert.
#    4) Press "Convert" button.
# -----------------------------------------------------------------------------      


def convert_pine_to_sparky(session):
    convert_dialog = sputil.the_dialog(convert_pine_prob, session)
    convert_dialog.show_window(1)

        
# -----------------------------------------------------------------------------
# Select spectra, expected peaks, and tolerances for assigner_dialog.
#
class convert_pine_prob(tkutil.Dialog, tkutil.Not_Stoppable):

  def __init__(self, session):

    self.session = session

    tkutil.Dialog.__init__(self, session.tk, 'Convert I-PINE outputs to Sparky')
    
    desc_label = Tkinter.Label(self.top, text = 'Convert I-PINE outputs to Sparky resonance list.')    
    desc_label.pack(side='top', anchor='w')    
    
    sep5 = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep5.pack(fill="both", padx=5,pady=5, side = 'top')
    
    input_label = Tkinter.Label(self.top, text = 'INPUT:')    
    input_label.pack(side='top', anchor='w')
        
    bb_label = Tkinter.Label(self.top, text = '   protein_backbone_assignment.txt (Required)')
    bb_label.pack(side='top', anchor='w')
    self.pine_bb = tkutil.file_field(self.top, 'Backbone:', 'Select I-PINE bacbone probabilistic output file.', width = 40)
    self.pine_bb.frame.pack(side = 'top')
            
    sc_label = Tkinter.Label(self.top, text = '   sidechain_table.txt (Optional)')
    sc_label.pack(side='top', anchor='w')
    self.pine_sc = tkutil.file_field(self.top, 'Sidechain:', 'Select I-PINE sidechain probabilistic output file.', width = 40)
    self.pine_sc.frame.pack(side = 'top')    
            
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
            
    input_label = Tkinter.Label(self.top, text = 'OUTPUT:')        
    input_label.pack(side='top', anchor='w')
        
    list_label = Tkinter.Label(self.top, text = '   Sparky resonance list file (Required)')
    list_label.pack(side='top', anchor='w')
    self.sparky_lt = tkutil.file_field(self.top, 'Sparky:', 'Assign sparky resonance list file name.', save=1, width = 40)
    self.sparky_lt.frame.pack(side = 'top')

    sep2 = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep2.pack(fill="both", padx=5,pady=5, side = 'top')        

    base_label = tkutil.entry_field(self.top, 'Base Probability(0.0~1.0):', initial = '0.9', width = 7)
    base_label.frame.pack(side = 'top', anchor = 'w')
    self.base_label = base_label
    
    sep3 = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep3.pack(fill="both", padx=5,pady=5, side = 'top')            
    
    br = tkutil.button_row(self.top,
                           ('Convert', self.convert_cb),
                           ('Cancel', self.close_cb),
               )
    br.frame.pack(side = 'top')
    
    sep4 = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep4.pack(fill="both", padx=5,pady=5, side = 'top')    
    bottom_label = Tkinter.Label(self.top, text = 'Use two-letter "rl" to read in after conversion.')
    bottom_label.pack(side = 'top')    
    
  # ---------------------------------------------------------------------------
  #    
  def convert_cb(self):    
    pine_bb_file = self.pine_bb.variable.get()
    pine_sc_file = self.pine_sc.variable.get()    
    sparky_lt_file = self.sparky_lt.variable.get()
    
    # check threshold    
    try:
      szPrb = self.base_label.variable.get()
      dPrb = eval(szPrb)
    except:
      tkMessageBox.showerror('Error', 'Please set number between 0.0 to 1.0.')
      return
    if dPrb < 0.0 or dPrb > 1.0:
      tkMessageBox.showerror('Error', 'Please set number between 0.0 to 1.0.')
              
    # check backbone
    if pine_bb_file == '':
      tkMessageBox.showerror('Error', 'Please set pine_backbone_assignment.txt path.')    
      return
          
    if not os.path.exists(pine_bb_file):
      tkMessageBox.showerror('Error', '%s not found.' % (pine_bb_file))    
      return
    
    # check sidechain
    if pine_sc_file != '':
      if not os.path.exists(pine_sc_file):
        tkMessageBox.showerror('Error', '%s not found.' % (pine_sc_file))    
        return
          
    # check output
    if sparky_lt_file == '':
      tkMessageBox.showerror('Error', 'Please set sparky resonance list path.')    
      return
          
    # read in
    
    # BB
    f = open(pine_bb_file, 'r')
    bb_lines = f.readlines()
    f.close()
    try:
      if bb_lines[0].strip().split()[0] != 'Residue_Name':
        tkMessageBox.showerror('Error', 'Incorrect pine_backbone_assignment.txt file.')
        return
    except:
      tkMessageBox.showerror('Error', 'Incorrect pine_backbone_assignment.txt file.')
      return    
              
    pine_bb_read = []
    
    iSeqMin = 9999
    iSeqMax = -9999
    
    for bb_line in bb_lines:
      splited_line = bb_line.strip().split()
      try:
        # HN
        bb_segment = [int(splited_line[0]), myseq.aaa2a(splited_line[1]), 'H', float(splited_line[3]), float(splited_line[2])]
        if bb_segment[1] != 'X' and bb_segment[3] < 500.0 and bb_segment[4] >= dPrb and bb_segment[3] != 0.0:
          pine_bb_read.append(bb_segment)
        # N
        bb_segment = [int(splited_line[0]), myseq.aaa2a(splited_line[1]), 'N', float(splited_line[4]), float(splited_line[2])]
        if bb_segment[1] != 'X' and bb_segment[3] < 500.0 and bb_segment[4] >= dPrb and bb_segment[3] != 0.0:
          pine_bb_read.append(bb_segment)
        # CO
        bb_segment = [int(splited_line[0]), myseq.aaa2a(splited_line[1]), 'C', float(splited_line[5]), float(splited_line[2])]
        if bb_segment[1] != 'X' and bb_segment[3] < 500.0 and bb_segment[4] >= dPrb and bb_segment[3] != 0.0:
          pine_bb_read.append(bb_segment)          
        # CA
        bb_segment = [int(splited_line[0]), myseq.aaa2a(splited_line[1]), 'CA', float(splited_line[6]), float(splited_line[2])]
        if bb_segment[1] != 'X' and bb_segment[3] < 500.0 and bb_segment[4] >= dPrb and bb_segment[3] != 0.0:
          pine_bb_read.append(bb_segment)                 
        # CB
        bb_segment = [int(splited_line[0]), myseq.aaa2a(splited_line[1]), 'CB', float(splited_line[7]), float(splited_line[2])]
        if bb_segment[1] != 'X' and bb_segment[3] < 500.0 and bb_segment[4] >= dPrb and bb_segment[3] != 0.0:
          pine_bb_read.append(bb_segment)     
          if iSeqMin > bb_segment[0]:   iSeqMin = bb_segment[0]
          if iSeqMax < bb_segment[0]:   iSeqMax = bb_segment[0]                        
      except:
        pass
    
    # SC
    pine_sc_read = []
    if os.path.exists(pine_sc_file):
      f = open(pine_sc_file, 'r')
      sc_lines = f.readlines()
      f.close()
      for sc_line in sc_lines:
        splited_line = sc_line.strip().split()      
        try:
          sc_segment = [int(splited_line[1]), myseq.aaa2a(splited_line[2]), splited_line[3], float(splited_line[5]), float(splited_line[4])]
          if sc_segment[1] != 'X' and sc_segment[3] < 500.0 and sc_segment[4] >= dPrb:
            pine_sc_read.append(sc_segment)                           
          if iSeqMin > sc_segment[0]:   iSeqMin = sc_segment[0]
          if iSeqMax < sc_segment[0]:   iSeqMax = sc_segment[0]                                    
        except:
          pass
        
    # combine
    pine_combined_read = []
    for iSeq in range(iSeqMin, iSeqMax+1):
      for segment in pine_bb_read:
        if segment[0] != iSeq: continue
        # check in sc
        for segment2 in pine_sc_read:
          if segment[0] != segment2[0] or segment[2] != segment2[2]: continue
          if segment[4] < segment2[4]: 
            segment[3] = segment2[3]
            segment[4] = segment2[4]
            break
        pine_combined_read.append(segment)
      # read in sidechain specific
      for segment in pine_sc_read:      
        if segment[0] != iSeq: continue
        # check in bb
        iFound = 0
        for segment2 in pine_combined_read:
          if segment[0] == segment2[0] and segment[2] == segment2[2]: 
            iFound = 1
            break
        if iFound == 0:
          pine_combined_read.append(segment)    
        
    # write out
    f = open(sparky_lt_file, 'w')
    for segment in pine_combined_read:
      if segment[2][0] == 'C': szNuc = '13C'
      elif segment[2][0] == 'N': szNuc = '15N'
      elif segment[2][0] == 'H': szNuc = '1H'
      else: continue
      
      ga = '%s%d' % (segment[1], segment[0])
      szLine = '%7s  %6s  %5s  %7.3f   0.0     0\n' % (ga, segment[2], szNuc, segment[3])  
      f.write(szLine)
    f.close()
    tkMessageBox.showinfo('Converted', 'Successfully saved.')
      
