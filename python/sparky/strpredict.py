
# -----------------------------------------------------------------------------
# Dialog for PECAN
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Oct 1, 2015
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import Tkinter
import myseq
import sparky
import tkutil
import sputil
import tkMessageBox
import os


def sort_resonances(session):
  iMin = 999999999
  iMax = -999999999
  
  resonances = []
  sorted_resonances = []
  
  # collect assigned resonances and get sequence index range
  for condition in session.project.condition_list():
    for resonance in condition.resonance_list():
      if resonance.group.number == None: continue
      if iMin < resonance.group.number: iMin = resonance.group.number
      elif iMin > resonance.group.number: iMin = resonance.group.number
      if iMax > resonance.group.number: iMax = resonance.group.number
      elif iMax < resonance.group.number: iMax = resonance.group.number
      resonances.append(resonance)
              
  # binning sort              
  for iSeq in range(iMin, iMax+1):
    for resonance in resonances:
      if resonance.group.number == iSeq:
        sorted_resonances.append(resonance)
        
  return sorted_resonances      

def export_pacsyalign(session):
  import nmrstar
  iRet = nmrstar.GenerateNmrStar(session)
  if iRet == 1:
    import webbrowser
    webbrowser.open('http://pine.nmrfam.wisc.edu/PACSYALIGN')  
    
# -----------------------------------------------------------------------------
# LACS
#
# -----------------------------------------------------------------------------
#    
def export_lacs(session):
  path = tkutil.save_file(session.tk, "Save to LACS input file", "lacs.str")
  if path:
    iFirst = 99999
    groups = []
    
    seqgroup_list = myseq.BuildSequence(session, 3)
    seqgroup_list = myseq.CheckSequence(seqgroup_list) # sort and fill the gap
    if myseq.GapInSequence(seqgroup_list) == 1: # there is a gap
      tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
      seqgroup_list = myseq.LoadSeq(session, seqgroup_list)
      if seqgroup_list == None:
        tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
        return
        
    userseq = ''    
    for seqgroup in seqgroup_list:
      userseq = userseq + seqgroup[1]  
      
    # find selected groups?
    selected_group_list = []
    if self.m_applyoption.get() == 1:
      for spec in session.project.spectrum_list():
        for peak in spec.selected_peaks():
          for resn in peak.resonances():
            if resn == None: continue          
            gn = resn.group.name
            if gn == '?': continue
            selected_group_list.append(gn)
    selected_group_list = list(set(selected_group_list))      
    
    f = open(path, 'w')  
    # add header
    f.write('_Mol_residue_sequence\n;\n')
    f.write('%s\n' % (userseq))
    f.write(';\n\n')
    
    f.write('loop_\n')
    f.write('_Atom_shift_assign_ID\n')
    f.write('_Residue_seq_code\n')
    f.write('_Ressidue_label\n')
    f.write('_Atom_name\n')
    f.write('_Atom_type\n')
    f.write('_Chem_shift_value\n')
    f.write('_Chem_shift_ambiguity_code\n')       
   
    iLine = 1       
    resonances = []   
    iMin = 9999999
    iMax = -9999999   
                   
    for condition in session.project.condition_list():
      for resonance in condition.resonance_list():
        #if resonance.deviation > 1:
        #    continue
        if self.m_applyoption.get() == 1:
          try:
            idx = selected_group_list.index(resonance.group.name)
          except:
            continue  
        resonances.append(resonance)    
        if resonance.group.number < iMin: iMin = resonance.group.number
        if resonance.group.number > iMax: iMax = resonance.group.number                        
          
    # sort resonances
    sorted_resonances = []
    for iSeq in range(iMin, iMax+1):
      for resonance in resonances:
        if resonance.group.number == iSeq:
          sorted_resonances.append(resonance)            
          
    if len(sorted_resonances) == 0:
      tkMessageBox.showerror('Error', 'No available resonances.')          
      return          
              
    for resonance in sorted_resonances:              
      aaa = myseq.a2aaa(resonance.group.symbol)
      if aaa == '': continue
      if resonance.atom.name.find('_s') != -1: continue # this is simulated assignment
      
      atom_type = resonance.atom.name[0:1]
      if (atom_type == 'Q') or (atom_type == 'M'): atom_type = 'H'
      szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, resonance.group.number, aaa, resonance.atom.name, atom_type, resonance.frequency)
      if iFirst > resonance.group.number: iFirst = resonance.group.number
      iLine = iLine+1
      f.write(szWrite)
      if not (resonance.group.number, resonance.group.symbol) in groups:
          groups.append( (resonance.group.number, resonance.group.symbol) )
                
    # fill gap
    for group in seqgroup_list:
      if not group in groups:
        aaa = myseq.a2aaa(group[1])
        if aaa == '': continue
        szWrite = szWrite + ('%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, group[0], aaa, 'N', 'N', 9999.99))
        iLine = iLine+1                

    # add footer    
    szWrite = '\nstop_\n'
    f.write(szWrite)
    f.close()
    
    ##if tkMessageBox.askyesno('Export','Finished. Do you want to open PECAN web page?'):
    import webbrowser
    webbrowser.open('http://pine.nmrfam.wisc.edu/LACS')
  pass      

class lacs_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    self.session = session
    
    tkutil.Dialog.__init__(self, session.tk, 'LACS chemical shift validation')
    
    # User name
    user_name_ef = tkutil.entry_field(self.top, 'Your name: ', initial = '', width = 30)
    user_name_ef.frame.pack(side = 'top', anchor = 'w')
    self.user_name = user_name_ef.variable
    
    # User email
    user_email_ef = tkutil.entry_field(self.top, 'Your email: ', initial = '', width = 30)
    user_email_ef.frame.pack(side = 'top', anchor = 'w')
    self.user_email = user_email_ef.variable    
    
    # checkbutton- apply to only selected groups
    self.m_applyoption = Tkinter.IntVar()
    applytype_cb = Tkinter.Checkbutton(self.top, text = 'Apply to only selected groups', variable = self.m_applyoption, onvalue=1, offvalue = 0)
    applytype_cb.pack(side = 'top', anchor = 'w')
        
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
    # buttons
    self.br = tkutil.button_row(self.top,
			   ('Submit', self.submit_cb),
			   ('LACS Web', self.lacs_web),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 1)            
    tkutil.create_hint(self.br.buttons[0], 'Run LACS chemical shift validation. Plese check if your sequence number starts from 1. You can easily change by using two-letter-code "rn"')
    tkutil.create_hint(self.br.buttons[1], 'Generate LACS input and open LACS web page.')    
  def lacs_web(self):
    export_lacs(self.session)
    
  def submit_cb(self):
    iFirst = 99999
    groups = []
    session = self.session
    
    szUserName = self.user_name.get()
    szUserEmail = self.user_email.get()
    
    if szUserName == '':
      tkMessageBox.showerror('Name', 'Your name is required to follow the LACS run.')
      return
    if (szUserEmail == '') or (szUserEmail.find('@') == -1):
      tkMessageBox.showerror('Email', 'Your email is required to receive the LACS results.')
      return    

    seqgroup_list = myseq.BuildSequence(self.session, 3)
    seqgroup_list = myseq.CheckSequence(seqgroup_list) # sort and fill the gap
    if myseq.GapInSequence(seqgroup_list) == 1: # there is a gap
      tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
      seqgroup_list = myseq.LoadSeq(self.session, seqgroup_list)
      if seqgroup_list == None:
        tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
        return
        
    userseq = ''    
    for seqgroup in seqgroup_list:
      userseq = userseq + seqgroup[1]  
    
    szWrite = ''
    # add header
    szWrite = szWrite + '_Mol_residue_sequence\n;\n'
    szWrite = szWrite + ('%s\n' % (userseq))
    szWrite = szWrite + ';\n\n'
    
    szWrite = szWrite + 'loop_\n'
    szWrite = szWrite + '_Atom_shift_assign_ID\n'
    szWrite = szWrite + '_Residue_seq_code\n'
    szWrite = szWrite + '_Ressidue_label\n'
    szWrite = szWrite + '_Atom_name\n'
    szWrite = szWrite + '_Atom_type\n'
    szWrite = szWrite + '_Chem_shift_value\n'
    szWrite = szWrite + '_Chem_shift_ambiguity_code\n\n'

    # find selected groups?
    selected_group_list = []
    if self.m_applyoption.get() == 1:
      for spec in session.project.spectrum_list():
        for peak in spec.selected_peaks():
          for resn in peak.resonances():
            if resn == None: continue
            gn = resn.group.name
            if gn == '?': continue
            selected_group_list.append(gn)
    selected_group_list = list(set(selected_group_list))
    
    # add header
    iLine = 1           
    resonances = []   
    iMin = 9999999
    iMax = -9999999    
    for condition in session.project.condition_list():
      for resonance in condition.resonance_list():
        #if resonance.deviation > 1:
        #    continue
        if self.m_applyoption.get() == 1:
          try:
            idx = selected_group_list.index(resonance.group.name)
          except:
            continue  
        resonances.append(resonance)    
        if resonance.group.number < iMin: iMin = resonance.group.number
        if resonance.group.number > iMax: iMax = resonance.group.number            

    if len(resonances) == 0:
      tkMessageBox.showerror('Error', 'No available resonances.')          
      return          
                    
    # sort resonances
    sorted_resonances = []
    for iSeq in range(iMin, iMax+1):
      for resonance in resonances:
        if resonance.group.number == iSeq:
          sorted_resonances.append(resonance)
          
    if len(sorted_resonances) == 0:
      tkMessageBox.showerror('Error', 'No available resonances.')          
      return          
          
    for resonance in sorted_resonances:          
      aaa = myseq.a2aaa(resonance.group.symbol)
      if aaa == '': continue
      
      if resonance.atom.name.find('_s') != -1: continue # this is simulated assignment
      
      atom_type = resonance.atom.name[0:1]
      if (atom_type == 'Q') or (atom_type == 'M'): atom_type = 'H'
      szTemp = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, resonance.group.number, aaa, resonance.atom.name, atom_type, resonance.frequency)
      if iFirst > resonance.group.number: iFirst = resonance.group.number
      iLine = iLine+1
      szWrite = szWrite + szTemp
      if not (resonance.group.number, resonance.group.symbol) in groups:
          groups.append( (resonance.group.number, resonance.group.symbol) )
                
    # fill gap
    for group in seqgroup_list:
      if not group in groups:
        aaa = myseq.a2aaa(group[1])
        if aaa == '': continue
        szWrite = szWrite + ('%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, group[0], aaa, 'N', 'N', 9999.99))
        iLine = iLine+1

    # add footer    
    szWrite = szWrite + '\nstop_\n'

    import posthtml
    import httplib    
    
    fields = [['name', szUserName],
              ['email', szUserEmail]]

    contents = [ ['assignment_file', 'lacs.str', szWrite] ]
    fields.append (['assignment_file', 'lacs.str'])                
    fields.append (['Assign', 'Assignment'])       
    
    lacs_url = 'pine.nmrfam.wisc.edu'
    lacs_selector = '/cgi-bin/lacsuploader.cgi'
       
    text=posthtml.post_multipart(lacs_url, lacs_selector, fields, contents)
    tkMessageBox.showinfo('LACS job sumitted.', 'LACS job submitted. Check your email periodically.') 
    
  
def run_lacs(session):
  sputil.the_dialog(lacs_dialog,session).show_window(1)   
  
# -----------------------------------------------------------------------------
#
def export_pecan(session):
  path = tkutil.save_file(session.tk, "Save to PECAN input file", "pecan.str")
  if path:
    iFirst = 99999
    groups = []
    f = open(path, 'w')  
    # add header
    szWrite = '_Chem_shift_ambiguity_code\n'
    f.write(szWrite)
    iLine = 1                  
    resonances = []   
    iMin = 9999999
    iMax = -9999999    
    
    seqgroup_list = myseq.BuildSequence(self.session, 3)
    seqgroup_list = myseq.CheckSequence(seqgroup_list) # sort and fill the gap
    if myseq.GapInSequence(seqgroup_list) == 1: # there is a gap
      tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
      seqgroup_list = myseq.LoadSeq(session, seqgroup_list)
      if seqgroup_list == None:
        tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
        return    
    
    # find selected groups?
    selected_group_list = []
    if self.m_applyoption.get() == 1:
      for spec in session.project.spectrum_list():
        for peak in spec.selected_peaks():
          for resn in peak.resonances():
            if resn == None: continue          
            gn = resn.group.name
            if gn == '?': continue
            selected_group_list.append(gn)
    selected_group_list = list(set(selected_group_list))    
        
    for condition in session.project.condition_list():
      for resonance in condition.resonance_list():
        #if resonance.deviation > 1:
        #    continue
        if self.m_applyoption.get() == 1:
          try:
            idx = selected_group_list.index(resonance.group.name)
          except:
            continue  
        resonances.append(resonance)    
        if resonance.group.number < iMin: iMin = resonance.group.number
        if resonance.group.number > iMax: iMax = resonance.group.number            
              
    # sort resonances
    sorted_resonances = []
    for iSeq in range(iMin, iMax+1):
      for resonance in resonances:
        if resonance.group.number == iSeq:
          sorted_resonances.append(resonance)
          
    if len(sorted_resonances) == 0:
      tkMessageBox.showerror('Error', 'No available resonances.')          
      return          
    
    for resonance in sorted_resonances:                                  
      aaa = myseq.a2aaa(resonance.group.symbol)
      if aaa == '': continue
      
      if resonance.atom.name.find('_s') != -1: continue # this is simulated assignment
      
      atom_type = resonance.atom.name[0:1]
      if (atom_type == 'Q') or (atom_type == 'M'): atom_type = 'H'
      szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, resonance.group.number, aaa, resonance.atom.name, atom_type, resonance.frequency)
      if iFirst > resonance.group.number: iFirst = resonance.group.number
      iLine = iLine+1
      f.write(szWrite)
      if not (resonance.group.number, resonance.group.symbol) in groups:
        groups.append( (resonance.group.number, resonance.group.symbol) )
              
    #groups.sort()
    # find gap
    #sequence = myseq.CheckSequence(groups)
  
    #if myseq.GapInSequence(sequence) == 1: # there is a gap
    #  tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
    #  sequence = myseq.LoadSeq(sequence)
    #  if sequence == None:
    #    tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
    #    szWrite = '\nstop_\n'
    #    f.write(szWrite)
    #    f.close()            
    #    return
            
    # fill gap
    #for group in sequence:
    #  if not group in groups:
    #    aaa = myseq.a2aaa(group[1])
    #    if aaa == '': continue
    #    szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, group[0], aaa, 'N', 'N', 9999.99)
    #    iLine = iLine+1
    #    f.write(szWrite)
    
    # fill gap
    for group in seqgroup_list:
      if not group in groups:
        aaa = myseq.a2aaa(group[1])
        if aaa == '': continue
        szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, group[0], aaa, 'N', 'N', 9999.99)
        iLine = iLine+1    
        lines = lines + szWrite    
            
    # fill until first sequence with arbitrary HIS
    if iFirst > 1:
      for i in range(iFirst):
        if i == 0: continue
        szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, i, 'HIS', 'N', 'N', 9999.99)
        iLine = iLine+1
        f.write(szWrite)                  

    # add footer    
    szWrite = '\nstop_\n'
    f.write(szWrite)
    f.close()
    ##if tkMessageBox.askyesno('Export','Finished. Do you want to open PECAN web page?'):
    import webbrowser
    webbrowser.open('http://pine.nmrfam.wisc.edu/PECAN')
    
    

class pecan_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    self.session = session
    
    tkutil.Dialog.__init__(self, session.tk, 'PECAN secondary structure prediction')
    
    # User name
    user_name_ef = tkutil.entry_field(self.top, 'Your name: ', initial = '', width = 30)
    user_name_ef.frame.pack(side = 'top', anchor = 'w')
    self.user_name = user_name_ef.variable
    
    # User email
    user_email_ef = tkutil.entry_field(self.top, 'Your email: ', initial = '', width = 30)
    user_email_ef.frame.pack(side = 'top', anchor = 'w')
    self.user_email = user_email_ef.variable    
    
    # checkbutton- apply to only selected groups
    self.m_applyoption = Tkinter.IntVar()
    applytype_cb = Tkinter.Checkbutton(self.top, text = 'Apply to only selected groups', variable = self.m_applyoption, onvalue=1, offvalue = 0)
    applytype_cb.pack(side = 'top', anchor = 'w')
    
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
   
    # buttons
    self.br = tkutil.button_row(self.top,
			   ('Submit', self.submit_cb),
			   ('PECAN Web', self.pecan_web),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 1)            
    tkutil.create_hint(self.br.buttons[0], 'Run PECAN secondary structure prediction. Plese check if your sequence number starts from 1. You can easily change by using two-letter-code "rn"')
    tkutil.create_hint(self.br.buttons[1], 'Generate PECAN input and open PECAN web page.')        
    
  def pecan_web(self):
    export_pecan(self.session)
    
  def submit_cb(self):
    iFirst = 99999
    lines = ''
    groups = []
    session = self.session
    
    szUserName = self.user_name.get()
    szUserEmail = self.user_email.get()
    
    if szUserName == '':
      tkMessageBox.showerror('Name', 'Your name is required to follow the PECAN run.')
      return
    if (szUserEmail == '') or (szUserEmail.find('@') == -1):
      tkMessageBox.showerror('Email', 'Your email is required to receive the PECAN results.')
      return    
      
    seqgroup_list = myseq.BuildSequence(self.session, 3)
    seqgroup_list = myseq.CheckSequence(seqgroup_list) # sort and fill the gap
    if myseq.GapInSequence(seqgroup_list) == 1: # there is a gap
      tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
      seqgroup_list = myseq.LoadSeq(self.session, seqgroup_list)
      if seqgroup_list == None:
        tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
        return      
      
    # find selected groups?
    selected_group_list = []
    if self.m_applyoption.get() == 1:
      for spec in session.project.spectrum_list():
        for peak in spec.selected_peaks():
          for resn in peak.resonances():
            if resn == None: continue          
            gn = resn.group.name
            if gn == '?': continue
            selected_group_list.append(gn)
    selected_group_list = list(set(selected_group_list))      


    # add header
    szWrite = '_Chem_shift_ambiguity_code\n\n'
    lines = lines + szWrite
    iLine = 1          
    resonances = []   
    iMin = 9999999
    iMax = -9999999    
        
    for condition in session.project.condition_list():
      for resonance in condition.resonance_list():
        #if resonance.deviation > 1:
        #    continue
        if self.m_applyoption.get() == 1:
          try:
            idx = selected_group_list.index(resonance.group.name)
          except:
            continue  
        resonances.append(resonance)    
        if resonance.group.number < iMin: iMin = resonance.group.number
        if resonance.group.number > iMax: iMax = resonance.group.number            

    # sort resonances
    sorted_resonances = []
    for iSeq in range(iMin, iMax+1):
      for resonance in resonances:
        if resonance.group.number == iSeq:
          sorted_resonances.append(resonance)
    
    if len(sorted_resonances) == 0:
      tkMessageBox.showerror('Error', 'No available resonances.')          
      return
          
    for resonance in sorted_resonances:                                  
      aaa = myseq.a2aaa(resonance.group.symbol)
      if aaa == '': continue
      
      if resonance.atom.name.find('_s') != -1: continue # this is simulated assignment
      
      atom_type = resonance.atom.name[0:1]
      if (atom_type == 'Q') or (atom_type == 'M'): atom_type = 'H'
      szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, resonance.group.number, aaa, resonance.atom.name, atom_type, resonance.frequency)
      if iFirst > resonance.group.number: iFirst = resonance.group.number
      iLine = iLine+1
      lines = lines + szWrite
      if not (resonance.group.number, resonance.group.symbol) in groups:
        groups.append( (resonance.group.number, resonance.group.symbol) )
    #groups.sort()
    
    # find gap
    #sequence = myseq.CheckSequence(groups)
  
    #if myseq.GapInSequence(sequence) == 1: # there is a gap
    #  tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
    #  sequence = myseq.LoadSeq(sequence)
    #  if sequence == None:
    #    tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
    #    return
            
    # fill gap
    #for group in sequence:
    #  if not group in groups:
    #    aaa = myseq.a2aaa(group[1])
    #    if aaa == '': continue
    #    szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, group[0], aaa, 'N', 'N', 9999.99)
    #    iLine = iLine+1
    #    lines = lines + szWrite        
    
    # fill gap
    for group in seqgroup_list:
      if not group in groups:
        aaa = myseq.a2aaa(group[1])
        if aaa == '': continue
        szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, group[0], aaa, 'N', 'N', 9999.99)
        iLine = iLine+1    
        lines = lines + szWrite
            
    # fill until first sequence with arbitrary HIS
    if iFirst > 1:
      for i in range(iFirst):
        if i == 0: continue
        szWrite = '%5d %5d %5s %5s %6s %9.3f  .  2\n' % (iLine, i, 'HIS', 'N', 'N', 9999.99)
        iLine = iLine+1
        lines = lines + szWrite

    # add footer    
    szWrite = '\nstop_\n'
    lines = lines + szWrite        

    import posthtml
    import httplib    
    
    fields = [['name', szUserName],
              ['email', szUserEmail]]

    contents = [ ['assignment_file', 'pecan.str', lines] ]
    fields.append (['assignment_file', 'pecan.str'])                
    fields.append (['Assign', 'Assignment'])       
    
    pecan_url = 'pine.nmrfam.wisc.edu'
    pecan_selector = '/cgi-bin/pecanuploader.cgi'
       
    text=posthtml.post_multipart(pecan_url, pecan_selector, fields, contents)
    tkMessageBox.showinfo('PECAN job sumitted.', 'PECAN job submitted. Check your email periodically.')                        
    
# -----------------------------------------------------------------------------
#
def run_pecan(session):
  sputil.the_dialog(pecan_dialog,session).show_window(1)       
