# -----------------------------------------------------------------------------
# Transferation of Assignments to spectrum (RNA version)
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee & Yanjiao Wang
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: October 17, 2019
# 
# Install (later):
#   Add the following line in the assignment_menu part of sparky_site.py
#       ('TA', 'Transfer assignments to spectrum', ('na_tan','NA_TAN')),
#
# Usage:
#   type "TA" command or select from extension menu
# 
#
# This module is the key of "predict-and-confirm" method.
#
#
# -----------------------------------------------------------------------------
import Tkinter
import atomnames
import na_shiftstats
import sparky
import sputil
import tkutil
import pinegraph
import tkMessageBox
import tkFileDialog
import os.path
from sys import stdout
import na_cstable
import pyutil
import sys
import nmrfam


# ----------------------------------------------------------------------------
# currently just provide prediction of RNA imino groups
imino_groups = {'G':['N1', 'H1'], 
                'U':['N3', 'H3'] }
# currently just provide prediction of canonical base pairs and GU wobble
canonical_BP = ['GC', 'CG', 'UA', 'AU' , 'GU', 'UG']


# ----------------------------------------------------------------------------
# peaks2ucsf input
class UcsfInput():
  
  def __init__(self, spec=None):
    self.peaks = []
    
    if spec: # following the parameters of current spectrum
      self.dimension = spec.dimension
      self.msize = spec.data_size
      self.origin = spec.region[1]
      self.nuclei = spec.nuclei
      self.specfreq = spec.hz_per_ppm
      self.specwidth = pyutil.seq_product(spec.spectrum_width, spec.hz_per_ppm)    
    else: #N-HSQC
     self.dimension = 2
     self.msize = (128, 256)
     self.origin = (165., 15.)
     self.nuclei = ('N', 'H')
     self.specfreq = (81.010, 800.244)
     self.specwidth = (24.*self.specfreq[0],6.*self.specfreq[1] )
 # ----------------------------------------------------------------------------
# add peak to peak list
  def AddPeak(self, freq):
    ppm_center = freq
    height = 1.e2
    linewidth = (0.19*self.specfreq[0], 0.07*self.specfreq[1])# based on prediction uncertainty
    self.peaks.append([ppm_center, height, linewidth])
# ----------------------------------------------------------------------------
# write to a file
  def Write(self, inputfile):
    
    f = open(inputfile, 'wt')
    f.write('%d' % self.dimension + ' # dimension\n')
    f.write(pyutil.sequence_string(self.msize, '%d ') + '# matrix size\n')
    f.write(pyutil.sequence_string(self.origin, '%.6f ') + '# ppm origin\n')
    f.write(pyutil.sequence_string(self.nuclei, '%s ') + '# nuclei\n')
    f.write(pyutil.sequence_string(self.specfreq, '%.9f ') + \
                                   '# spectometer freq\n')
    f.write(pyutil.sequence_string(self.specwidth, '%.3f ') + '# spectrum width\n')
    
    for ppm_center, height, linewidth in self.peaks:
      f.write(pyutil.sequence_string(ppm_center, '%8.5f ') +
                '%10.4g' % height +
                pyutil.sequence_string(linewidth, '%8.2f ') +
                '\n')
    f.close()
# ----------------------------------------------------------------------------
# should be implemented.....
# Yanjiao will implement secondary structure included version
# Currently considered to return:
#   [[1, 'A'], [2,'U'], [3, 'G'], [4, 'C'], .... ]
# What about using small and large characters to show paired and unpaired?
#   [[1, 'A'], [2, 'u']....] # e.g. A: paired, u: unpaired... 

def ReadNASequence(seq_file):
  if not seq_file:
    tkMessageBox.showerror('Sequence file Error',
       'Please choose a sequence file!')
    return
 
  lines = map(str.strip,open(seq_file).readlines())
  if len(lines)!=2:
    tkMessageBox.showerror('Sequence file Error',
       'Please give the sequence and secondary structure (in bracket-dot line),\n'\
       'e.g. GGACUUCGGUCC\n       ((((....))))')
    return
  
  seq = lines[0]
  bdstr = lines[1]
  if not all(map(lambda x:x in atomnames.dna_rna_attached_heavy_atoms,seq)):
    tkMessageBox.showerror('Sequence type Error',
       'Sequence contains atoms other than [AGCU].')
    return
  
  if not all(map(lambda x:x in ('(',')','.'),bdstr)):
    tkMessageBox.showerror('Secondary structure type Error',
       'Secondary structure contains character other than [().].')
    return
  
  seq_list = [[i+1,at] for i,at in enumerate(seq)]

  return seq_list,bdstr

# -----------------------------------------------------------------------------    
# custom group class
class WGroup:
  name = '0'    # A12
  symbol = ''   # A
  number = 0    # 12
  def __init__(self, symb, resnum):
    self.name = '%s%d' % (symb, resnum)
    self.symbol = symb
    self.number = resnum
    
# -----------------------------------------------------------------------------    
# from existing assignment.
def GetFreq(session, group, atm):
    if group == None:
      return 9999, 9999
    
    for condition in session.project.condition_list():
        resn = condition.find_resonance(group.name, atm)
        if resn != None:
            if (resn.frequency == 0.0) and (resn.deviation == 0.0):
                return 9999, 9999
            return resn.frequency, resn.deviation
    
    return 9999, 9999
# ----------------------------------------------------------------------------- 
# find base pairs for each secondary structure
def Pairing(bdstr):
  stack = []
  pairs = {}
  
  for i,nt in enumerate(bdstr):
    if nt == '(':
      stack.append(i)
    elif nt ==')':
      pairs[stack[-1]] = i
      pairs[i] = stack[-1]
      stack[-1:] = []
  
  return pairs
# ----------------------------------------------------------------------------- 
# find BP-triplet motif for each residue
def GetTriplet(seq, bdstr, group):
  idx = group.number - 1
  pairs = Pairing(bdstr)
  
  try:
    bp_cur = (idx,  pairs[idx]  ) # current base pair
    bp_pre = (idx-1,pairs[idx-1]) # 5' base pair
    bp_nxt = (idx+1,pairs[idx+1]) # 3' base pair
  except KeyError:
    return
 
  if bp_cur[1]==bp_pre[1] - 1 and \
    bp_cur[1]==bp_nxt[1] + 1:
    bps = [seq[idx-1] + seq[pairs[idx-1]],
           seq[idx]   + seq[pairs[idx]],
           seq[idx+1] + seq[pairs[idx+1]] ] #[GU,UA,AU]
  else:
      return
  
  if not all(map(lambda x:x in canonical_BP, bps)):
    tkMessageBox.showerror('Secondary structure Error',
      'Secondary structure contains non-canonical base pairs'\
      ' other than W-C base pairs and GU wobble.')
    return

  return '-'.join(bps) #GU-UA-AU
      
# -----------------------------------------------------------------------------
# Frequency prediction
# currently just provide BMRB statistics
# Yanjiao will implement advanced version
#def PredictFreq(session, group, atm):
#  ast = na_shiftstats.na_atom_statistics(group.symbol, atm)
#  if ast == None: return 9999, 9999
#  #return ast.average_shift, ast.shift_deviation
#  return ast.average_shift

# Frequency prediction based on BP-triplet motif
# curretly just provide prediction of canonical motif for RNA imino groups
def PredictFreq(session, sequence, bdstr, group, atm):
  if group.symbol not in imino_groups:
    return 9999, 9999
  
  if atm not in imino_groups[group.symbol]:
    return 9999, 9999
  triplet = GetTriplet(sequence, bdstr, group)
  
  if not triplet:
    return 9999, 9999
  cs = na_cstable.PredictImino(triplet, atm)
  
  return cs



#-----------------------------------------------------------------------------
#
class na_tan_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    #self.sequences = []
    #self.groups = []
    self.session = session
    self.selected_spec_type = None
    
    tkutil.Dialog.__init__(self, session.tk, \
      'Transfer and simulate assignments for nucleic acids')

    self.top_frame = Tkinter.Frame(self.top, width=300, height=25,)
    self.top_frame.pack(side='top', anchor='w')  
    # Sequence file    
    user_seq_ff = tkutil.file_field2(self.top_frame, 'Sequence file: ', '', 
          file_type=[('3-letter-code sequence file with indices', '.seq'), 
          ('1-letter-code sequence file', '.fasta'), 
          ('3-letter-code sequence file without indices', '.txt')], 
          default_ext='.seq', width = 25)
    user_seq_ff.frame.pack(side = 'left')
    self.user_seq = user_seq_ff.variable # user sequence file
    self.seq_button = Tkinter.Button(self.top_frame, text = "?", 
                        command = self.about_seq_format)
    self.seq_button.pack(side = 'left')      
   # just a separater
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    
    # check if file exists
    if session.project != None:
      if session.project.sparky_directory != '' and \
          os.path.exists(session.project.save_path):
        seq_path = session.project.save_path + '.seq'
        if os.path.exists(seq_path):
          self.user_seq.set(seq_path)

    spec = sputil.spectrum_menu(session, self.top, 'Spectrum: ')
    spec.frame.pack(side = 'top', anchor = 'w')
    self.spec = spec

    # checkbutton- apply to only selected N-HSQC peaks
    # this is for future implementation of new experiments
    self.m_applyoption = Tkinter.IntVar()
    applytype_cb = Tkinter.Checkbutton(self.top, 
                text = 'Apply to only selected (N,C)-HSQC peaks', 
                variable = self.m_applyoption, onvalue=1, offvalue = 0)
    applytype_cb.pack(side = 'top', anchor = 'w')
    
    self.middle_frame = Tkinter.Frame(self.top, height = 200)
    self.middle_frame.pack(side='top', anchor='w', fill='both',expand=1)
    
    spec_type = pinegraph.modified_listbox(self.middle_frame,
                      'Type: ', 20, 5, "single")
    self.spec_type = spec_type    
    spec_type.frame.pack(side = 'left', anchor = 'w', fill='both', expand=1)
    spec_type.listbox.bind('<ButtonRelease-1>', self.select_spectype)    

    self.supported_spectra = 'N-HSQC C-HSQC ' # can be extended later
    self.supported_spectrum_list = self.supported_spectra.split()
    for sp in self.supported_spectrum_list:
      self.spec_type.append(sp,sp)
    
    self.br = tkutil.button_row(self.top,
			   ('Transfer', self.transfer_cb),  # transfer assignments onto spectra
			   ('Simulate Assignments', self.simulateAssign_cb),  # simulate possible assignments
			   ('Simulate Spectrum', self.simulateSpec_cb),  # simulate spectrum
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')
    
#    tkutil.create_hint(self.br.buttons[0], 'Generate formatted peak and assignment onto selected experiment based on existing assignment.')
#    tkutil.create_hint(self.br.buttons[1], 'Generate formatted peak and assignment onto selected experiment based on existing assignment and predicted chemical shifts')
#    
    # For existing BMRB entry set up  
    self.bottom_frame = Tkinter.Frame(self.top, width = 300, height = 25)
    self.bottom_frame.pack(side='top', anchor='w')
    self.bmrb = tkutil.file_field(self.bottom_frame, 'BMRB', 
                                  'Select template .str file.')
    self.bmrb.frame.pack(side = 'left')
    self.bmrb_button = Tkinter.Button(self.bottom_frame, text = "?", 
                        command = self.about_using_bmrb)
    self.bmrb_button.pack(side = 'left')      
    self.bmrb_list = []    
    
    self.status_text = Tkinter.StringVar()
    self.status = Tkinter.Label(self.top, textvariable = self.status_text, 
                                anchor = 'w', justify = 'left')		
    self.status.pack(side = 'top', anchor = 'w')
    self.status_text.set("Current: 0 / 0")
    
    self.status2_text = Tkinter.StringVar()    
    self.status2 = Tkinter.Label(self.top, textvariable = self.status2_text, 
                                anchor = 'w', justify = 'left')		
    self.status2.pack(side = 'top', anchor = 'w')
    self.status2_text.set("!Multiple runs on the spectrum may generate duplicate peaks!")

# -----------------------------------------------------------------------------
# BMRB has higher priority
  def about_using_bmrb(session):
    tkMessageBox.showinfo('NMR-STAR', 'Select a NMR-STAR(BMRB V3.1) file to use as chemical shift template.\n')

    import nmrfam
    nmrfam.about_bmrb(session)
# -----------------------------------------------------------------------------
# user sequence format
  def about_seq_format(session):
    tkMessageBox.showinfo('Sequence format', 'GGACUUCGGUCC\n((((....))))\n')

# ----------------------------------------------------------------------------
  def transfer_cb(self):
    self.TransferAndSimulatePeaks(0)    # no simulaation
# ----------------------------------------------------------------------------
  def simulateAssign_cb(self):
    # check if spec and spec_type selected
    self.TransferAndSimulatePeaks(1)     # with simulation of assignments  
# ----------------------------------------------------------------------------
  def simulateSpec_cb(self):
    # check if spec and spec_type selected
    self.TransferAndSimulatePeaks(2)     # with simulation of spectrum  

# ----------------------------------------------------------------------------
  def get_group(self, iSeqIdx):
    for group in self.group_list:
      if group.number == iSeqIdx:
        return group
    return None
# ----------------------------------------------------------------------------
  def get_seq(self, verbose=False):
    seq_file = self.user_seq.get()
    if not os.path.exists(seq_file) and verbose:
      tkMessageBox.showerror('Use sequence', '%s not found.' % (seq_file))
    seq_list,bdstr = ReadNASequence(seq_file) # we should implement
      
    # set sequences
    self.sequences = []
    self.groups = []
    self.bdstr = bdstr
    ga = []
    
    for seq in seq_list:    
      self.sequences.append( (seq[1], seq[0]) )
      self.groups.append(WGroup(seq[1], seq[0]) )
    if verbose:        
      tkMessageBox.showinfo('Use sequence', '%d residues loaded.' % \
                          (len(self.sequences)) )
    return self.groups
  # ---------------------------------------------------------------------------
  # Update peak lists when spectra selection is changed
  #!
  def select_spectype(self, event):
    # add selected spectra to selected spectra list
    ed = self.spec_type.event_line_data(event)
    self.selected_spec_type = ed
# ----------------------------------------------------------------------------
  def TransferAndSimulatePeaks(self, sim_mode):
    # check if sp=ec and spec_type selected
    bSwap = False
    if self.spec.spectrum() == None:
      tkMessageBox.showerror('Spectrum Error', 
        'Please select a spectrum to populate assignments.')
      return

    # fetch bmrb if user sets a BMRB code or an actual file
    import nmrstar
    self.bmrb_list = []
    if self.bmrb.variable.get() != '':
      self.bmrb_list = nmrstar.FetchBMRB(self.bmrb.variable.get())
    
    session = self.session
    curr_spec = self.spec.spectrum()

    try:  
      if self.spec_type == None or self.selected_spec_type == None:
        tkMessageBox.showerror('Spectrum Type Error', 
                              'Please select a type to populate assignments.')     
        return
      spec_name = self.selected_spec_type
      spectrum_index = self.supported_spectrum_list.index(spec_name)
    except TypeError:      
      tkMessageBox.showerror('Spectrum Type Error', 
                          'Please select a type to populate assignments.')
      return          
    
    curr_spec_type = self.supported_spectrum_list[spectrum_index]
    
    # Get sequence index
    # fill WGroup      
    group_list = self.get_seq()
    
    # check whether they are selected
    # this is for future experiments anchoring HSQC peaks
    sgroup_list = [] # selected group list
    for i in range(len(group_list)):
      group = group_list[i]
      if self.m_applyoption.get() == 0: # all groups if not specified
        sgroup_list.append(1)
        continue
      else:
        bSelected = 0
      for peak in self.session.selected_peaks():
        if peak.selected * peak.is_assigned == 0: continue
        asns = sputil.parse_assignment(peak.assignment)
        if len(asns) != 2:              continue # parse failed
        ga1, ga2 = asns[0], asns[1]
        if ( ((ga1[1][0] == 'N') and (ga2[1][0] == 'H')) or \
            ((ga2[1][0] == 'N') and (ga1[1][0] == 'H')) ) and \
            (group.name == ga[0]):
          bSelected = 1 # selected N-HSQC peak
        elif ( ((ga1[1][0] == 'C') and (ga2[1][0] == 'H')) or \
            ((ga2[1][0] == 'C') and (ga1[1][0] == 'H')) ) and \
            (group.name == group_atom1[0]):
          bSelected = 1 # selected C-HSQC peak
        else: continue # not N/C-HSQC  
        sgroup_list.append(bSelected)
        
    if len(sgroup_list) == 0:
      tkMessageBox.showerror('No targets', 'Nothing to transfer.')
      return
          
    # Loop sequence
    iAddedCount = 0
    if sim_mode==1:# simulation assignments
      for i in range(len(group_list)):
        self.status_text.set("Current: %d / %d" % (i+1, len(group_list)))    
        self.status.update_idletasks()
        if sgroup_list[i] == 0:  continue   # not a selected group
        group = group_list[i]
        
        try:
          group_dict = atomnames.dna_rna_attached_heavy_atoms[group.symbol]
        except: # not supported na
          continue  
        
        Hlist = group_dict.keys()
        if curr_spec_type.find('-HSQC') != -1: # N/C-HSQC support
          for hatm in Hlist:
            heavyatm = group_dict[hatm]
            if curr_spec_type == 'N-HSQC': # N-HSQC
              if heavyatm[0] != 'N': continue
            elif curr_spec_type == 'C-HSQC': #C-HSQC
              if heavyatm[0] != 'C': continue
  
            Hfreq, Hdevi = GetFreq(session, group, hatm)
            NCfreq, NCdevi = GetFreq(session, group, heavyatm)
           
            if (Hfreq < 500 or NCfreq < 500): continue# has assigned
            sequence = ''.join([s[0] for s in self.sequences])
            bdstr = self.bdstr
            if Hfreq > 500:
              Hfreq = PredictFreq(session, sequence, bdstr, group, hatm)
              hatm = hatm + '_s' # this means this is simulated
            if NCfreq > 500:
              NCfreq = PredictFreq(session,sequence, bdstr, group, heavyatm)
              heavyatm = heavyatm + '_s' # this means this is simulated  
           
            if Hfreq > 500 or NCfreq > 500:
              continue
            if curr_spec.nuclei[0] == '1H':
              pk = curr_spec.place_peak([Hfreq, NCfreq])
              pk.assign(0, group.name, hatm)
              pk.assign(1, group.name, heavyatm)
            elif curr_spec.nuclei[1] == '1H':
              pk = curr_spec.place_peak([NCfreq, Hfreq])
              pk.assign(0, group.name, heavyatm)
              pk.assign(1, group.name, hatm)
            else: continue # not N/C-HSQC
            
            pk.show_assignment_label() 
            iAddedCount = iAddedCount+1
      msg = '%d peaks were populated.' % (iAddedCount)
      tkMessageBox.showinfo('Simulate assignments onto spectrum', msg)
    
    
    elif sim_mode==2: # simulation spectrum
      if curr_spec_type != 'N-HSQC':
        tkMessageBox.showerror('Spectrum type Error', 'Currently just provide'\
          ' prediction of N-HSQC spectrum')
        return
      
      #p2uInput = UcsfInput(curr_spec)
      p2uInput = UcsfInput()
      peaks = []
      
      for i in range(len(group_list)):
        self.status_text.set("Current: %d / %d" % (i+1, len(group_list)))    
        self.status.update_idletasks()
        if sgroup_list[i] == 0:  continue   # not a selected group
        group = group_list[i]
        try:
          group_dict = atomnames.dna_rna_attached_heavy_atoms[group.symbol]
        except: # not supported na
          continue  
        
        Hlist = group_dict.keys()
        if curr_spec_type.find('-HSQC') != -1: # N/C-HSQC support
          for hatm in Hlist:
            heavyatm = group_dict[hatm]
            if curr_spec_type == 'N-HSQC': # N-HSQC
              if heavyatm[0] != 'N': continue
            elif curr_spec_type == 'C-HSQC': #C-HSQC
              if heavyatm[0] != 'C': continue
            sequence = ''.join([s[0] for s in self.sequences])
            bdstr = self.bdstr
            Hfreq = PredictFreq(session, sequence, bdstr, group, hatm)
              #hatm = hatm + '_s' # this means this is simulated
            NCfreq = PredictFreq(session,sequence, bdstr, group, heavyatm)
              #heavyatm = heavyatm + '_s' # this means this is simulated  
            
            if Hfreq > 500 or NCfreq > 500:
              continue
            #if curr_spec.nuclei[0] == '1H':
            p2uInput.AddPeak([NCfreq, Hfreq])
            peaks.append([[NCfreq, Hfreq], group.name, hatm, heavyatm])
            #elif curr_spec.nuclei[1] == '1H':
              #p2uInput.AddPeak([NCfreq, Hfreq])
              #peaks.append([[NCfreq, Hfreq], group.name, heavyatm, hatm])
            #else: continue # not N/C-HSQC
      
      p2uInput.Write('p2u.input')
      peaks2ucsf = 'peaks2ucsf'
      rm_command = '\rm -f'
      if sys.platform == 'Windows':
        peaks2ucsf = peaks2ucsf + '.exe'
        rm_command = 'del'
      paths = nmrfam.get_nmrfam_sparky_lookup_path(self.session)
      for p in paths:
        peaks2ucsf_path = os.path.join(p, 'peaks2ucsf')
        if os.path.exists(peaks2ucsf_path):
          break  
      os.system('%s sim.ucsf < p2u.input'%peaks2ucsf_path) # generate a simulated ucsf
      os.system('%s p2u.input'%rm_command)
      session.open_file('sim.ucsf')
      sim_spec = sputil.name_to_spectrum('sim', session)
      
      for peak in peaks:
        pk = sim_spec.place_peak(peak[0])
        pk.assign(0, peak[1], peak[2])
        pk.assign(1, peak[1], peak[3])
        pk.show_assignment_label()
        iAddedCount = iAddedCount+1
     
      msg = '%d peaks were populated.' % (iAddedCount)
      tkMessageBox.showinfo('Simulate spectrum', msg)

# ----------------------------------------------------------------------------
def NA_TAN(session):
  sputil.the_dialog(na_tan_dialog,session).show_window(1)
  
