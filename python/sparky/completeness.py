# -----------------------------------------------------------------------------
# Completeness counter
# 
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Nov 8, 2019
#
#                     Ryan Russell added non-hydrogen conditions for ssNMR
# 
# -----------------------------------------------------------------------------

import tkutil
import sputil
import sparky
import Tkinter
import os
import myseq
import atomnames
import tkMessageBox
import pinelayout

atom_option_list = ['All atoms', 'All atoms except C', 
                    'All atoms except aromatic atoms', 
                    'All atoms except C and aromatic atoms', 
                    'N, H, C, CA, CB', 
                    'N, H, CA, CB', 
                    'N, H, C, CA', 
                    'N, H, CA', 
                    'N, H', 'N', 'CA', 'CB', 'C', 
                    'N, C, CA, CB', 'N, C, CA' ] 
                        
disabled_layout = {
    'S':('OG', 'HG'),
    'T':('HX','HG1'),
    'C':('SG', 'HG'),
    'M':('CE', 'HE', 'HE1', 'HE2', 'HE3'),
    'F':('CG', 'CD1', 'CE1', 'CZ', 'HZ', 'CD2', 'CE2', 'HD1', 
          'HE1', 'HD2', 'HE2', 'HD11', 'HD12', 'HE11', 'HE12', 
          'HD21', 'HD22', 'HE21', 'HE22'),
    'Y':('CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'HD1', 'HD11', 'HD12', 
          'HD2', 'HD21', 'HD22', 'HE1', 'HE11', 'HE12', 'HE2', 'HE21', 
          'HE22', 'HH', 'OH'),
    'W':('CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 
          'CH2', 'HD1', 'HD2', 'HE1', 'HE3', 'HZ2', 'HZ3', 'HH2'),
    'H':('CG', 'ND1', 'CD2', 'NE1', 'NE2', 'CE1', 'CE2', 'HD1',
          'HD2', 'HE1', 'HE2'),
    'D':('CG','CG2', 'OD1', 'OD2', 'HD2'),
    'E':('CD', 'OD1', 'OD2', 'HD2', 'HE2'),
    'N':('CG', 'OD1', 'ND2', 'HD21', 'HD22'),
    'Q':('CD', 'OE1', 'NE2', 'HE21', 'HE22'),
    'K':('NZ', 'HZ', 'HZ1', 'HZ2', 'HZ3'),
    'R':('NE', 'CZ', 'NH1', 'NH2', 'HE', 'HH11', 'HH12', 'HH21', 'HH22'),                        
    }
    
# -----------------------------------------------------------------------------
#
class completeness_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
  
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'Completeness counter')
        
    # sequence file
    user_seq_ff = tkutil.file_field2(self.top, 'Sequence file: ', '', 
          file_type=[('3-letter-code sequence file with indices', '.seq'), 
                  ('1-letter-code sequence file', '.fasta'), 
                  ('3-letter-code sequence file without indices', '.txt')], 
                  default_ext='.seq', width = 25)
    user_seq_ff.frame.pack(side = 'top', anchor = 'w')
    self.user_seq = user_seq_ff.variable
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    
    # check if file exists
    szInitRange = '1-100'
    if session.project != None:
      if session.project.sparky_directory != '' and \
          os.path.exists(session.project.save_path):
        seq_path = session.project.save_path + '.seq'
        if os.path.exists(seq_path):
          user_seq_ff.variable.set(seq_path)
          try:
            readSeq = myseq.ReadSequenceFromFile(self.user_seq.get())          
            szInitRange = '%d-%d' % (readSeq[0][0], readSeq[-1][0])
          except:
            pass  
          
    # condition
    self.get_conditions()
    self.cond_om = tkutil.option_menu(self.top, "Condition: ", \
                                      self.condition_list, 'Any*')
    self.cond_om.frame.pack(side = 'top', anchor = 'nw')
    self.cond_om.menu.bind("<<MenuSelect>>", self.update_callback)
        
    # sequence range
    self.seq_range_ef = tkutil.entry_field(self.top, 'Ranges:', \
                                      initial = szInitRange, width = 40)
    self.seq_range_ef.frame.pack(side = 'top', anchor = 'nw', expand = 0)
        
    # atoms
    self.atom_om = tkutil.option_menu(self.top, "Atoms: ", \
                                    atom_option_list, 'N, H, C, CA, CB')
    self.atom_om.frame.pack(side = 'top', anchor = 'nw')
    self.atom_om.menu.bind("<<MenuSelect>>", self.update_callback)
        
    # Use Proline N
    self.use_PN = Tkinter.IntVar()
    self.use_PN.set(0)
    self.use_PN_cb = Tkinter.Checkbutton(self.top, 
        text = 'Consider amide nitrogens of prolines', 
        variable = self.use_PN, onvalue=1, offvalue = 0)
    self.use_PN_cb.pack(side = 'top', anchor = 'w', expand = 0)

    self.notice_text = Tkinter.StringVar()    
    self.notice_text.set("* Completeness: not yet calculated.")
    self.notice = Tkinter.Label(self.top, textvariable = self.notice_text, \
                                anchor = 'w', justify = 'left')		
    self.notice.pack(side = 'top', anchor = 'w')    
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    
        
    # buttons
    self.br = tkutil.button_row(self.top,
			   ('Calculate', self.update_cb),			   			   
			   ('Write', self.write_cb),			   
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 0)     
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    
    # missing resonances
    # Scrolling List
    self.listbox = tkutil.scrolling_list(self.top, 'Missing resonances', 5)
    self.listbox.frame.pack(side='top', fill = 'both', expand = 1)    
    
    self.update_cb()
        
  # ---------------------------------------------------------------------------
  #
  def get_condition_list(self):
    cond_list = []
    if self.cond_om.get() == 'Any*':
      for condition in self.session.project.condition_list():
        cond_list.append(condition)
      return cond_list

    for condition in self.session.project.condition_list():
      if self.cond_om.get() == condition.name:
        cond_list.append(condition)
        return cond_list
        
    return []    
  # ---------------------------------------------------------------------------
  #    
  def get_conditions(self):
    self.condition_list = ['Any*']
    for condition in self.session.project.condition_list():
      self.condition_list.append(condition.name)    
  # ---------------------------------------------------------------------------
  #
  def update_callback(self, event):
    self.update_cb()            
  # ---------------------------------------------------------------------------
  #
  def write_cb(self):    
    path = tkutil.save_file(self.session.tk, "Save missing resonances", \
                                              "missing_resonances.txt")
    if path: 
      f = open(path, 'w')
      for data in self.listbox.line_data:
        f.write('%s\n' % data)
      f.close()  
  # ---------------------------------------------------------------------------
  #
  def update_cb(self):
    # depending on what is being selected
    # what condition?
    self.cond_list = self.get_condition_list()
    
    # sequence file
    readSeq = myseq.ReadSequenceFromFile(self.user_seq.get())
    oneline = ''
    iSeqCount = len(readSeq)
    if iSeqCount == 0:
      tkMessageBox.showerror('Error', 'Sequence file is incorrect.')
      return
      
    dictSeq = dict(readSeq)
    rangeList = []
    
    # parse sequence range
    szRange = self.seq_range_ef.variable.get()
    if szRange.find(',') != -1:     szRangeList = szRange.split(',')
    else:                           szRangeList = szRange.split('+') 
    for szSplitRange in szRangeList:
      if szSplitRange.find('-') != -1:  szSplitList = szSplitRange.split('-')
      else:                             szSplitList = szSplitRange.split('..')
      if szSplitList == 0:
        tkMessageBox.showinfo('Warning', \
            'Sequence ranges are set incorrect. All sequences will be used.')
        rangeList = [[readSeq[0][0],readSeq[-1][0]]]        
        break
      try:  
        rangeList.append([int(szSplitList[0]),int(szSplitList[1])])  
      except:        
        tkMessageBox.showinfo('Warning', \
          'Sequence ranges are set incorrect. All sequences will be used.')
        rangeList = [[readSeq[0][0],readSeq[-1][0]]]                
        break
      
    
    szOption = self.atom_om.variable.get()
    iOption = atom_option_list.index(szOption)
    
    # make sequence list
    count_list = []
    for [startidx, endidx] in rangeList:
      for idx in range(startidx, endidx+1):
        a = dictSeq[idx]
        atom_list = self.make_atoms_for_sequence(a)
        # disabled list    
        try:
          arom_list = list(disabled_layout[a])
        except:
          arom_list = []
        filtered_atom_list = \
          self.make_filtered_atom_list(atom_list, iOption, arom_list)
        shift_list = []
        for i in range(len(filtered_atom_list)): shift_list.append(9999)
        
        count_list.append([idx, a, filtered_atom_list, shift_list])
      
    # let's count
    (iAssignedCount, iTotalCount) = self.count_assigned_resonances(count_list)
    if iTotalCount != 0:
      self.notice_text.set("* Completeness (%.2f%%): %d / %d" % \
              (float(iAssignedCount) / float(iTotalCount) * 100.0, \
              iAssignedCount, iTotalCount))
    else:
      self.notice_text.set("* Completeness (%.2f%%): %d / %d" % \
              (0, iAssignedCount, iTotalCount))
    #tkMessageBox.showinfo('Completeness', self.notice_text.get())

  # ---------------------------------------------------------------------------
  #
  def count_assigned_resonances(self, count_list):
    self.listbox.clear()  
    iAssignedCount = 0
    iTotalCount = 0
    self.listbox.clear()
    for [idx, a, filtered_atom_list, shift_list] in count_list:
      iTotalCount = iTotalCount + len(filtered_atom_list)
      for atom in filtered_atom_list:
        cshift, shiftdev = self.GetFrequency(a, idx, atom, \
                            self.cond_om.variable.get())
        if cshift < 0 and shiftdev < 0: 
          szLine = '%5d %5s %5s' % (idx, a, atom)
          self.listbox.append(szLine, szLine)
          continue
        iAssignedCount = iAssignedCount + 1
    return (iAssignedCount, iTotalCount)        
  # ---------------------------------------------------------------------------
  #
  def check_assigned(self, a, idx, atom, cond):
    pass  
  # ---------------------------------------------------------------------------
  #
  def make_filtered_atom_list(self, atom_list, iOption, arom_list):
    filtered_atom_list = atom_list
    if iOption < 4:
      if    iOption == 0:   filtered_atom_list = atom_list
      elif  iOption == 1:   filtered_atom_list = self.filter_by_options(atom_list, [], ['C'])
      elif  iOption == 2:   filtered_atom_list = self.filter_by_options(atom_list, [], arom_list)
      elif  iOption == 3:   filtered_atom_list = self.filter_by_options(atom_list, [], arom_list+['C'])
    elif iOption == 4:      filtered_atom_list = self.filter_by_options(atom_list, ['N', 'H', 'C', 'CA', 'CB'], [])
    elif iOption == 5:      filtered_atom_list = self.filter_by_options(atom_list, ['N', 'H', 'CA', 'CB'], [])
    elif iOption == 6:      filtered_atom_list = self.filter_by_options(atom_list, ['N', 'H', 'C', 'CA'], [])
    elif iOption == 7:      filtered_atom_list = self.filter_by_options(atom_list, ['N', 'H', 'CA'], [])
    elif iOption == 8:      filtered_atom_list = self.filter_by_options(atom_list, ['N', 'H'], [])        
    elif iOption == 9:      filtered_atom_list = self.filter_by_options(atom_list, ['N'], [])        
    elif iOption == 10:      filtered_atom_list = self.filter_by_options(atom_list, ['CA'], [])        
    elif iOption == 11:      filtered_atom_list = self.filter_by_options(atom_list, ['CB'], [])        
    elif iOption == 12:      filtered_atom_list = self.filter_by_options(atom_list, ['C'], [])        
    elif iOption == 13:      filtered_atom_list = self.filter_by_options(atom_list, ['N', 'C', 'CA', 'CB'], [])
    elif iOption == 14:      filtered_atom_list = self.filter_by_options(atom_list, ['N', 'C', 'CA'], [])

    return filtered_atom_list
  # ---------------------------------------------------------------------------
  #
  def make_atoms_for_sequence(self, a):
    all_atom_list = list(atomnames.protein_atoms_by_group_no_pseudo[a])
    atom_list = []
    for atom in all_atom_list:
      if atom[0] != 'C' and atom[0] != 'N' and atom[0] != 'H': continue
      if a == 'P' and atom == 'N' and self.use_PN.get() == 0: continue
      if len(atom) > 1:
        if atom[1] == '1' or atom[1] == '2' or atom[1] == '3': continue
      atom_list.append(atom)
    return atom_list      
    
  # ---------------------------------------------------------------------------
  #
  def filter_by_options(self, atom_list, allow_list, disallow_list):
    temp_list = []
    if len(allow_list) != 0:
      for atom in atom_list:
        try:
          idx = allow_list.index(atom)
          temp_list.append(atom)
        except:
          pass
    else:
      for atom in atom_list:
        try:
          idx = disallow_list.index(atom)
          continue
        except:
          temp_list.append(atom)
    return temp_list
  # ---------------------------------------------------------------------------
  #
  def GetFrequency(self, szSeq, iSeqIdx, szAtom, szCondition):
    group_name = '%s%d' % (szSeq, iSeqIdx)
    for condition in self.cond_list:
      resonance = condition.find_resonance(group_name, szAtom)
      if resonance != None:
        if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
          return -1, -1
        return resonance.frequency, resonance.deviation
      else:
        # processing pseudo atoms
        if pinelayout.pseudo_layout.has_key(szSeq):
          layout = pinelayout.pseudo_layout[szSeq];
          if (szAtom[:1] == 'H') or (szAtom[:1] == 'Q') or (szAtom[:1] == 'M'):   
            szAtom2 = ('H%s' % szAtom[1:-1])
          else:
            szAtom2 = szAtom[0:-1]      
          if (len(szAtom2) == 1) and (szAtom != 'HN'):
            return -1, -1                                  
          resonance = condition.find_resonance(group_name, szAtom2)
          if resonance <> None:
            if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
              return -1, -1                  
            return resonance.frequency, resonance.deviation
        # processing meta atoms
        if not pinelayout.meta_layout.has_key(szSeq):
          continue
        layout = pinelayout.meta_layout[szSeq];
        szAtom2 = szAtom  #HB3
        while len(szAtom2) > 2:
          szAtom_1 = szAtom2[:-1] # HB
          if layout.has_key(szAtom_1):
            atom_list = layout[szAtom_1]
            if szAtom in atom_list:
              resonance = condition.find_resonance(group_name, szAtom_1)
              if resonance <> None:
                if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                  return -1, -1                                            
                return resonance.frequency, resonance.deviation
              else:
                for szPseudoAtom in atom_list:
                  resonance = condition.find_resonance(group_name, szPseudoAtom)
                  if resonance <> None:
                    if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                        return -1, -1                                                    
                    return resonance.frequency, resonance.deviation
          szAtom2 = szAtom_1
          if len(szAtom2) < 2:
            break
    return -1, -1  
    
def show_assignment_completeness(session):
  sputil.the_dialog(completeness_dialog, session).show_window(1)    
