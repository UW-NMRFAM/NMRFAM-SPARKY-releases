# -----------------------------------------------------------------------------
# PINE dialog
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: July 30, 2019
# 
# I-PINE user group: http://i-pine.nmrfam.wisc.edu/usergroup.html
#
# -----------------------------------------------------------------------------
# CITATION:
#    Lee W, Markley JL. Bioinformatics 2018 May 1; 34(9): 1586-1588
#    "PINE-SPARKY. 2 for automated NMR-based protein structure research"
#    doi: 10.1093/bioinformatics/btx785
# -----------------------------------------------------------------------------
#
# WHAT TO ADD? check if resonances without peaks and ask.
#

import os
import Tkinter

import sparky
import sputil
import tkutil
import myseq
import tkMessageBox
import nmrfam        

# for token
import time
import random
#import sparkytimer

pine_types = ('HSQC (N15)','C13-HSQC','HN(CA)CO','HNCO','CBCA(CO)NH', 
              'HN(CO)CACB','HNCACB','HN(CO)CA','HNCA','CB(CA)(CO)NH',
              'HN(CA)CB','C(CO)NH','H(CCO)NH','HBHA(CO)NH','HA(CO)NH',
              'HCCH-TOCSY','CCH-TOCSY','HCCH-COSY','CCH-COSY','TOCSY-HSQC', 
              'HNHA', 'HBHANH','HN(CA)NNH','N15-NOESY', 'C13-NOESY', 
              'HNCOCA-4D', 'HNCACO-4D', 'HNCO(-1)CA-4D', 'simHNCOCA-4D') 
              # AFTER TOCSY-HSQC are for all only I-PINE
expected_counts = (1,2,2,1,2,2,4,1,2,1,2,2,3,2,1,3,3,2,2,3,1,2,2,4,10,1,2,1,2)
pine_field = ('file01','file15', 'file08', 'file02', 'file03', 'file05', 
            'file04', 'file07', 'file06', 'file09', 'file10', 'file11', 
            'file12', 'file13', 'file14', 'file16', 'file17', 'file18', 
            'file19', 'file20', 'file25', 'file21', 'file22', 'file23', 
            'file24', 'file26', 'file27', 'file28', 'file29')
pine_field2 = ('exp1','exp15', 'exp8', 'exp2', 'exp3', 'exp5', 'exp4', 'exp7', 
            'exp6', 'exp9', 'exp10', 'exp11', 'exp12', 'exp13', 'exp14', 
            'exp16', 'exp17', 'exp18', 'exp19', 'exp20', 'exp25', 'exp21', 
            'exp22', 'exp23', 'exp24', 'exp26', 'exp27', 'exp28', 'exp29')
aaa_types = ('CYS', 'ASP', 'SER', 'GLN', 'LYS', 'ILE', 'PRO', 'THR', 'PHE', 
  'ASN', 'GLY', 'HIS', 'LEU', 'ARG', 'TRP', 'ALA', 'VAL', 'GLU', 'TYR', 'MET')
pine3_exp_types = ['TOCSY-HSQC','HNHA', 'HBHANH','HN(CA)NNH','N15-NOESY',
  'C13-NOESY', 'HNCOCA-4D', 'HNCACO-4D', 'HNCO(-1)CA-4D', 'simHNCOCA-4D']

# preassign- pre_assign
# CS-Rosetta- bmrb_rosetta
# PDB: pdb_file
# -----------------------------------------------------------------------------
#
def getFirstKey(item):
  return item[0]

class pine_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    self.session = session
    self.verbose = 1
    self.msg = ''
    
    tkutil.Dialog.__init__(self, session.tk, 'PINE-SPARKY.2 automation')
    
    # User name
    user_name_ef = tkutil.entry_field(self.top, 'Your name: ', initial = '', 
                                    width = 30)
    user_name_ef.frame.pack(side = 'top', anchor = 'w', expand = 0)
    self.user_name = user_name_ef.variable
    
    # User email
    user_email_ef = tkutil.entry_field(self.top, 'Your email: ', initial = '', 
                                      width = 30)
    user_email_ef.frame.pack(side = 'top', anchor = 'w')
    self.user_email = user_email_ef.variable    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    # Sequence file    
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
    if session.project != None:
      if session.project.sparky_directory != '' and \
          os.path.exists(session.project.save_path):
        seq_path = session.project.save_path + '.seq'
        if os.path.exists(seq_path):
          user_seq_ff.variable.set(seq_path)
    
    # Use pre-assignment
    self.preassign = Tkinter.IntVar()
    self.preassign.set(1)
    self.use_preassign_cb = Tkinter.Checkbutton(self.top, 
          text = 'Use pre-assignment', variable = self.preassign, 
          onvalue=1, offvalue = 0)
    self.use_preassign_cb.pack(side = 'top', anchor = 'w', expand = 0)
    
    # Use selective labeling
    self.labeling = Tkinter.IntVar()
    self.labeling.set(0)
    self.use_labeling_cb = Tkinter.Checkbutton(self.top, 
          text = 'Use selective labeling', variable = self.labeling, 
          onvalue=1, offvalue = 0)
    self.use_labeling_cb.pack(side = 'top', anchor = 'w', expand = 0)

    # Use CS-Rosetta
    self.csrosetta = Tkinter.IntVar()
    self.csrosetta.set(0)
    self.use_csrosetta_cb = Tkinter.Checkbutton(self.top, 
          text = 'Run CS-Rosetta with I-PINE outputs (only for academic use)', 
          variable = self.csrosetta, onvalue=1, offvalue = 0)
    self.use_csrosetta_cb.pack(side = 'top', anchor = 'w', expand = 0)
        
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)            
    # Scrolling List
    self.listbox = tkutil.scrolling_list(self.top, 
                    'Spectra to run I-PINE / PINE-SPARKY 2', 5)
    self.listbox.frame.pack(side='top', fill = 'both', expand = 1)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    # spectrum and type
    spec_frame = Tkinter.Frame(self.top, width = 600, height = 25)
    spec_frame.pack(side='top', anchor='w')

    self.sp = sputil.spectrum_menu(session, spec_frame, 'Select spectrum: ')
    self.sp.frame.pack(side = 'top', anchor = 'nw', expand = 0)
    self.selected_type = tkutil.option_menu(spec_frame, "Experiment type", 
                                            pine_types, 'HSQC (N15)')
    self.selected_type.frame.pack(side = 'top', anchor = 'nw')    
        
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    
    
    # buttons
    self.br = tkutil.button_row(self.top,
			   ('Add', self.add_cb),
			   ('Delete', self.delete_cb),
			   ('Clear', self.clear_cb),
			   ('Submit', self.submit_cb),
			   ('I-PINE Web', self.web_cb),
         ('User group', self.user_group_cb),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 0)     
    tkutil.create_hint(self.br.buttons[0], \
            'Add a spectrum to run I-PINE or I-PINE-SPARKY importer. ' + \
            'Experiment type should match with your spectrum. N-HSQC ' + \
            'or HNCO as root experiment and at least one CA or CB ' + \
            'experiment are required.')
    tkutil.create_hint(self.br.buttons[1], \
            'Delete selected spectrum in the list.')
    tkutil.create_hint(self.br.buttons[2], \
            'Clear all spectra in the list.')
    tkutil.create_hint(self.br.buttons[3], \
            'Run an I-PINE automated assignment without visiting the ' + \
            'I-PINE web page.')
    tkutil.create_hint(self.br.buttons[4], \
            'Export peak lists and open I-PINE web page for manual submission.')
    tkutil.create_hint(self.br.buttons[5], \
            'Visit I-PINE user group to resolve issues.')
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0) 
    
    # PDB
    pdb_text = Tkinter.StringVar()
    pdb_text.set("3D coordinate file can enhance the results (optional).\n" + \
                  "N15-NOESY should exist to use this feature.")
    pdb_note = Tkinter.Label(self.top, textvariable = pdb_text, anchor = 'w', \
                              justify = 'left')		
    pdb_note.pack(side = 'top', anchor = 'w')
    
    user_pdb_ff = tkutil.file_field2(self.top, 'PDB file: ', '', 
              file_type=[('PDB file', '.pdb')], default_ext='.pdb', width = 25)
    user_pdb_ff.frame.pack(side = 'top', anchor = 'w')
    self.user_pdb = user_pdb_ff.variable
        
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0) 

    # selective labeling?
    #sel_label_frame = Tkinter.Frame(self.top, width = 600, height = 100)
    #sel_label_frame.pack(side='top', anchor='w')

    #
    self.ps_label_text = Tkinter.StringVar()    
    self.ps_label_text.set("- PINE-SPARKY.2: I-PINE-SPARKY importer -")    
    self.ps_label = Tkinter.Label(self.top, textvariable = self.ps_label_text, 
                                  anchor = 'w', justify = 'left')		
    self.ps_label.pack(side = 'top', anchor = 'w')
        
    # token
    # User name
    token_frame = Tkinter.Frame(self.top, width = 600, height = 25)
    token_frame.pack(side='top', anchor='w')
    token_ef = tkutil.entry_field(token_frame, 'Key: ', initial = '', width = 20)
    token_ef.frame.pack(side = 'left', anchor = 'w', expand = 0)
    self.token = token_ef.variable        
    self.br2 = tkutil.button_row(token_frame,
        ('Check', self.check_wrap_cb),
        ('Browse...', self.pine_browse_cb),
        ('Web...', self.web_report_cb),
        )      
    self.br2.frame.pack(side = 'top', anchor = 'e', expand = 0)             
    tkutil.create_hint(self.br2.buttons[0], 
                      'Check I-PINE job status and import the results.')
    tkutil.create_hint(self.br2.buttons[1], 
                      'Import the results in the local machine.')
    tkutil.create_hint(self.br2.buttons[2], 
                      'Open I-PINE web report page.')
    # tolerances
    tol_frame = Tkinter.Frame(self.top)
    tol_frame.pack(side = 'top', fill='both')
       
    self.ntol = tkutil.entry_field(tol_frame, 'N tol.:', 
                                  initial = 0.200, width = 5)
    self.ntol.frame.grid(row = 0, column=0)     
    self.ntol_ppm = self.ntol.variable
          
    self.ctol = tkutil.entry_field(tol_frame, ', C tol.:', 
                                  initial = 0.200, width = 5)
    self.ctol.frame.grid(row = 0, column=2)
    self.ctol_ppm = self.ctol.variable     
         
    self.htol = tkutil.entry_field(tol_frame, ', H tol.:', 
                                  initial = 0.020, width = 5)
    self.htol.frame.grid(row=0, column=4)    
    self.htol_ppm = self.htol.variable
        
    #
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)     
    self.notice_text = Tkinter.StringVar()    
    self.notice_text.set("* Check peak counts if I-PINE " + \
                          "keeps failing (Use 'pv' tool).")    
    self.notice = Tkinter.Label(self.top, textvariable = self.notice_text, \
                                anchor = 'w', justify = 'left')		
    self.notice.pack(side = 'top', anchor = 'w')
    
#    self.sparkytimer = sparkytimer.SparkyTimer(30, self.check_token, [])    
  # -----------------------------------------------------------------------------
  #    
#  def check_token(self):
#    if self.token.get() == '': return
#    if self.sparkytimer.is_running == False: return
#    self.sparkytimer.stop()
#    self.check_cb(0)
#    time.sleep(30)
#    self.sparkytimer.start()
  # -----------------------------------------------------------------------------
  #    
  # ipine_params = [['',''],['',''],['',''],['',?],]
  def auto_setup(self, ipine_params):
    # 'user_name', 'user_email'
    # 'pre_assign', 'selective_label', 'cs_rosetta', 'seq_file', 
    # 'HSQC (N15)', ....
    self.verbose = 0
    self.msg = ''
    self.listbox.clear()
    for key, value in ipine_params:
      if key == 'user_name':          self.user_name.set(value)
      elif key == 'user_email':       self.user_email.set(value)
      elif key == 'pre_assign':       self.preassign.set(value)
      elif key == 'selective_label':  self.labeling.set(value)
      elif key == 'cs_rosetta':       self.csrosetta.set(value)
      elif key == 'seq_file':         self.user_seq.set(value)
      else: # experiments
        try:
          exp_no = pine_types.index(key)
          self.listbox.append('[%s]:%s' % (key, value.name), (key, value) )
        except:
          self.msg = 'Unknown experiment: ' + key
          return
    self.submit_cb()
    if self.msg == '':
      self.msg = 'Submission succeeded.'
    self.verbose = 1
  # -----------------------------------------------------------------------------
  #    
  def add_cb(self):
    spec = self.sp.spectrum()
    spec_type = self.selected_type.get()
    # already in the list?
    iFound = 0
    
    for data in self.listbox.line_data:
      if data[0] == spec_type and data[1] == spec:
        iFound = 3
        break
      if data[0] == spec_type:
        iFound = 1
        break
      if data[1] == spec:  
        iFound = 2
        break      
    if iFound == 3 and spec_type == 'Selective_labeling':
      self.msg = '[%s]:%s already added.' % (spec_type, spec.name)
      if self.verbose == 1:
        tkMessageBox.showerror('Already added', self.msg )
    if iFound == 1 and spec_type != 'Selective_labeling':
      self.msg = '%s already added.' % (spec_type)
      if self.verbose == 1:
        tkMessageBox.showerror('Already added', self.msg )
      return
    if iFound == 2 and spec_type != 'Selective_labeling':
      self.msg = '%s already added.' % (spec.name)
      if self.verbose == 1:
        tkMessageBox.showerror('Already added', self.msg )
      return      
    self.listbox.append( '[%s]:%s' % (spec_type, spec.name), (spec_type, spec) )  
    
  # -----------------------------------------------------------------------------
  #    
  def delete_cb(self):  
    selects = self.listbox.delete_selected()
  # -----------------------------------------------------------------------------
  #    
  def clear_cb(self):  
    self.listbox.clear()  
  # -----------------------------------------------------------------------------
  #    
  def submit_cb(self):  
    # sequence
    if not os.path.exists(self.user_seq.get()):
      self.msg = 'Please set your sequence file.'
      if self.verbose == 1:
        tkMessageBox.showerror('Sequence', self.msg)
      return

#    self.sparkytimer.stop()
    readSeq = myseq.ReadSequenceFromFile(self.user_seq.get())
    oneline = ''
    pine_seq = ''
    
    # default is pine 2 and check if pine 3 exp exists. 
    pine_ver = 2
    
    iSeqCount = len(readSeq)
    
    for seq in readSeq:
      if seq[1] == 'X':
        self.msg = 'Wrong sequence format.'
        if self.verbose == 1:
          tkMessageBox.showerror('Sequence', self.msg)
          tkMessageBox.showerror('Sequence', oneline)        
        return      
      oneline = oneline+seq[1]
      pine_seq = pine_seq + seq[1] + '\n' 
      
    if iSeqCount < 5:
      self.msg = 'Your sequence length is only %d. ' + \
        'Please use different sequence file if it is incorrect.' + str(iSeqCount)
      if self.verbose == 1:
        tkMessageBox.showerror('Sequence', self.msg )  
      
    # check if available name and email exist
    szUserName = self.user_name.get()
    szUserEmail = self.user_email.get()
    
    if szUserName == '':
      szUserName = 'anonymous'
      
    if szUserName == '':    
      self.msg = 'Your name is required to track the I-PINE run.'
      if self.verbose == 1:
        tkMessageBox.showerror('Name', self.msg)
      return
      
    if (szUserEmail == '') or (szUserEmail.find('@') == -1):
      szUserEmail = 'nobody@nobody.com'      

    if (szUserEmail == '') or (szUserEmail.find('@') == -1):
      self.msg = 'Your email is required to receive the I-PINE results.'
      if self.verbose == 1:
        tkMessageBox.showerror('Email', self.msg)
      return    
      
    # check first if N-HSQC or C-HSQC exist
    iFound = 0
    for (spec_type, spec) in self.listbox.line_data:
      if spec_type in ['HSQC (N15)', 'HNCO', 'HN(CO)CA', 'HNCOCA-4D']:
        iFound = 1
        break     
    iSimulate = 0    
    if iFound == 0 and self.preassign.get() == 0:
      if self.verbose == 1:
        if not tkMessageBox.askokcancel('No root experiment', 'N-HSQC, HNCO, HN(CA)CO, HNCOCA-4D must exist. Do you want to used simulated N-HSQC?'):
          return
        iSimulate = 1
      else:
        iSimulate = 1
      
    fields = [['name', szUserName],
              ['email', szUserEmail]]
              
    # make up spectra
    contents = [ ['seqfile', 'nmrfamsparky_seqfile.txt', pine_seq] ]
    fields.append (['seq', 'sequence'])                  
                    
    # selective labeling should have selective labeling data
    iFound = 0
    szWrite = ''
    if self.labeling.get() == 1:
      # check if really a selective label exists  
      iFound = 0
      for (spec_type, spec) in self.listbox.line_data:
        if spec_type == 'HSQC (N15)':
          if spec.nuclei[0] == '1H': 
            iH = 0
            iN = 1
          else:
            iH = 1
            iN = 0
          for peak in spec.peak_list():
            if peak == None: continue
            if peak.label == None: 
#              for aaa in aaa_types:   szWrite = szWrite + '%s %7.3f %7.3f\n' % (aaa, peak.frequency[iH], peak.frequency[iN])
              continue
            if peak.label.text == '': 
#              for aaa in aaa_types:   szWrite = szWrite + '%s %7.3f %7.3f\n' % (aaa, peak.frequency[iH], peak.frequency[iN])            
              continue
            selective_label_list = peak.label.text.split(',')
            iSuccess = 0
            for slbl in selective_label_list:
              aaa = myseq.a2aaa(slbl)
              if aaa != 'XXX':
                iFound = iFound+1
                szWrite = szWrite + '%s %7.3f %7.3f\n' % (aaa, peak.frequency[iH], peak.frequency[iN])
                iSuccess = 1
                break
#            if iSuccess == 0: 
#              for aaa in aaa_types:   szWrite = szWrite + '%s %7.3f %7.3f\n' % (aaa, peak.frequency[iH], peak.frequency[iN])
      if iFound == 0:
        self.msg = 'No selective labeling data found. Please add user labels by using two-letter-code "pl". E.g. Select a peak, type "pl" and type "I" or "I,L,V"'
        if self.verbose == 1:
          tkMessageBox.showerror('No selective labeling', self.msg)
        return
      contents.append( ['labeling', 'selectivelabel.list', szWrite] )
      fields.append (['label_file', 'Selective_Labeling'])         
                  
    if self.csrosetta.get() == 1:
      fields.append (['bmrb_rosetta', 'bmrb_rosetta'])      

    import posthtml
    import httplib    
    
    # simulate nhsqc
    if iSimulate == 1:
      
      NH_list = []
      filter_NH_list = []
      
      htolppm = float(self.htol_ppm.get())
      ntolppm = float(self.ntol_ppm.get())
      
      for (spec_type, spec) in self.listbox.line_data:
        if spec.dimension != 3: continue
        nuclei_order = spec.nuclei[0]+spec.nuclei[1]+spec.nuclei[2] 
        if nuclei_order.find('C') == -1 or nuclei_order.find('N') == -1 or nuclei_order.find('H') == -1: continue
        for peak in spec.peak_list():
          for i in range(len(peak.frequency)):
            if spec.nuclei[i] == '15N':
              dN = peak.frequency[i]
            elif spec.nuclei[i] == '1H':  
              dH = peak.frequency[i]
          NH_list.append([dN, dH]) 
          
      # header
      peaklist = '      Assignment    '
      szHead = '?-?'
      peaklist = peaklist + '   w1      w2     \n\n'
                
      # filter
      for (dN, dH) in NH_list:
        iFound = 0
        for (dN2, dH2) in filter_NH_list:
          if abs(dH-dH2) < htolppm and abs(dN-dN2) < ntolppm:
            iFound = 1
            break
        if iFound != 1:
          szWrite = '%10s' % szHead
          szWrite = szWrite + ' %8.3f %8.3f\n' % (dN, dH)
          peaklist = peaklist + szWrite
          filter_NH_list.append([dN, dH])
      contents.append( [pine_field[0], 'simulated_NHSQC.list', peaklist] )
      fields.append ([pine_field2[0], pine_types[0]])
            
    for (spec_type, spec) in self.listbox.line_data:
      try:
        iIdx = pine_types.index(spec_type)
      except:
        self.msg = 'What is this experiment??? - ' + spec_type
        if self.verbose == 1:
          tkMessageBox.showerror('Wrong experiment', self.msg  )
        return            
      if iIdx > 18 or spec_type in pine3_exp_types:
        pine_ver = 3  
      else:
        pine_ver = 2
      # build file
      
      peaklist = '      Assignment    '
      szHead = '?'
      for i in range(spec.dimension-1):
        peaklist = peaklist + '   w%d   ' % (i+1)
        szHead = szHead + '-?'
      peaklist = peaklist + '   w%d   ' % (spec.dimension)              
      peaklist = peaklist + 'Data Height\n\n'
        
      if len(spec.peak_list()) == 0:
        self.msg = '%s does not have any peak.' % spec.name
        if self.verbose == 1:
          tkMessageBox.showerror('No peaks', self.msg  )
        return                    
        
      iCurrentCount = len(spec.peak_list())
      iExpectCount = expected_counts[iIdx]
      if iCurrentCount < int(float(iExpectCount) * 0.75):
        self.msg = '%s may need more peaks. Keep going anyway.' % spec.name
        if self.verbose == 1:
          tkMessageBox.showerror('Warning', self.msg )
        
      peaklist2 = []
      for peak in spec.peak_list():
        if peak.data_height == None: continue
        szWrite = '%10s' % szHead
        for i in range(spec.dimension):
          szWrite = szWrite + ' %8.3f' % (peak.frequency[i])
        szWrite = szWrite + ' %16.3f' % (peak.data_height)                  
        szWrite = szWrite + '\n'
        peaklist2.append(szWrite)
      filtered_list = list(set(peaklist2))
      for peakitem in filtered_list:
        peaklist = peaklist + peakitem
      
      contents.append( [pine_field[iIdx], spec.name + '.list', peaklist] )
      fields.append ([pine_field2[iIdx], pine_types[iIdx]])

    ##
                
    if self.preassign.get() == 1:
      import pinelayout
      groups = []
      for condition in self.session.project.condition_list():
        for resonance in condition.resonance_list():
          if resonance.deviation > 1:  continue
          iAmb = 0
          if pinelayout.pseudo_layout.has_key(resonance.group.symbol):
            if pinelayout.pseudo_layout[resonance.group.symbol].has_key(resonance.atom.name): iAmb = 1
            if pinelayout.meta_layout.has_key(resonance.group.symbol):
              if pinelayout.meta_layout[resonance.group.symbol].has_key(resonance.atom.name): iAmb = 1
          if pinelayout.pine_layout.has_key(resonance.group.symbol):
            aaa = myseq.a2aaa(resonance.group.symbol)
            if aaa == '': continue
            atom_type = resonance.atom.name[0:1]
            tolppm = 1.000              
            try:
              if (atom_type == 'Q') or (atom_type == 'M') or (atom_type == 'H'): 
                atom_type = 'H' 
                tolppm = float(self.htol_ppm.get())
              elif atom_type == 'N':
                tolppm = float(self.ntol_ppm.get())            
              elif atom_type == 'C':
                tolppm = float(self.ctol_ppm.get())                          
            except:
              tolppm = 1.000  
              
            group = [resonance.group.number, aaa, resonance.atom.name, atom_type, resonance.frequency,tolppm, iAmb]
            groups.append(group)
            if resonance.group.number > iSeqCount:
              self.msg = 'Check your current assignments by "rl". Make sure you removed unused resonances by "dr".'
              if self.verbose == 1:
                tkMessageBox.showerror('Assignment error', self.msg)
              return
            if oneline[resonance.group.number-1] != resonance.group.symbol:
              self.msg = 'You have %s in your assignments which cannot be found in your sequence file. You have %s%d.' % (resonance.group.name, oneline[resonance.group.number-1], resonance.group.number)
              if self.verbose == 1:
                tkMessageBox.showerror('Assignment error', self.msg)
              return            
      groups.sort()

      if len(groups) > 0:      
        szWrite = """loop_
    _Atom_shift_assign_ID
    _Residue_seq_code
    _Residue_label
    _Atom_name
    _Atom_type
    _Chem_shift_value
    _Chem_shift_value_error
    _Chem_shift_ambiguity_code\n\n"""
        iLine = 1                      
        for group in groups:
            szWrite = szWrite+'%5d%5d%5s%5s%6s%9.3f%7.3f%3d\n' % \
                    (iLine, group[0], group[1], group[2], group[3], \
                    group[4], group[5], group[6])
            iLine = iLine+1
        szWrite = szWrite+'\nstop_\nsave_\n'
        contents.append( ['pre_assign', 'preassignment.str', szWrite] )
        fields.append (['assign_file', 'Pre_assignment'])
    
    # check if PDB exists
    if os.path.exists(self.user_pdb.get()):
      f_pdb = open(self.user_pdb.get(), 'r')
      szPdbContent = f_pdb.read()
      f_pdb.close()
      contents.append( ['pdb', 'coordinate.pdb', szPdbContent] )
      fields.append (['pdb_file', 'PDB coordinate'])
      pine_ver = 3
      
    # preassign only mode
    if len(self.listbox.line_data) == 0:
      pine_ver = 3

    random.seed()
    token = time.strftime("%y%m%d_%H%M%S_") + \
                "%06d" % random.randrange(0, 1000000)
    fields.append (['nmrfamsparky_token', token])
    self.token.set(token)
    
    pine_url = 'pine.nmrfam.wisc.edu'
    pine_selector = '/cgi-bin/pineuploader.cgi'
    
    if pine_ver == 3:
      pine_url = 'pine3.nmrfam.wisc.edu'
      pine_selector = '/cgi-bin/pine3uploader.cgi'

    text=posthtml.post_multipart(pine_url, pine_selector, fields, contents)
    if self.verbose == 1:
      tkMessageBox.showinfo('I-PINE job sumitted.', 
        'I-PINE job submitted. Check your result in this window ' + \
        'or in your email inbox after a few minutes. Please cite ' + \
        'our PINE-SPARKY.2 and I-PINE web server papers to support ' + \
        'the maintenance (check with "n0").')
#    self.sparkytimer.start()
  # -----------------------------------------------------------------------------
  #    
  def check_wrap_cb(self):  
    self.check_cb(1)
  # -----------------------------------------------------------------------------
  #    
  def pine_browse_cb(self):
    self.check_cb(2)
  # -----------------------------------------------------------------------------
  #    
  def web_report_cb(self):
    if self.token.get() == '':
      tkMessageBox.showerror('Error', 'I-PINE job ID not specified.')
      return
    url = 'http://pine.nmrfam.wisc.edu/upload/script/users/' + self.token.get() + '/web_results/'
    import webbrowser
    webbrowser.open(url)
    
  # -----------------------------------------------------------------------------
  #    
  def check_cb(self, clicked):
    if clicked == 2: # directory mode
      import tkFileDialog
      pine_dir = tkFileDialog.askdirectory(initialdir = self.session.project.sparky_directory,
                                title = 'Select a I-PINE output directory',
                                mustexist = 1)
      if pine_dir == '': return
      self.token.set(pine_dir)
      
    if self.token.get() == '':
      if clicked == 1:
        tkMessageBox.showinfo('I-PINE job sumitted.', \
                            'No submitted I-PINE job found.')        
      return
    pine_job_id = self.token.get()
      
    # retrieve PINE URL + token path.
    try:
      import urllib2
    except:
      tkMessageBox.showerror('urllib2', 
        'You do not have openssl installed or set properly.\n' + \
        'Please check your email instead.')
      return

    pine_root_url = 'http://pine.nmrfam.wisc.edu/upload/script/users/%s/' % (pine_job_id)
    pine_token_url = pine_root_url + 'token_status.txt' 
    pine_result_url = pine_root_url + 'results/'
    
    if clicked == 2:
      pine_root_url = 'file://%s/' % (self.token.get())
      pine_result_url = pine_root_url
      
    pine_package_url = pine_result_url + 'all_results.zip'    
        
    pine_status_lines = ['waiting',]
    if clicked == 1:
      try: 
        pine_status = urllib2.urlopen(pine_token_url, timeout=2)
        pine_status_lines = pine_status.readlines()
        if len(pine_status_lines) == 0:
          tkMessageBox.showerror('Retrieve error', \
              'Unknown error during retrieving data from NMRFAM. ' + \
              'Please check your email instead.')
        elif pine_status_lines[0].find('DOCTYPE') != -1:
          tkMessageBox.showerror('Retrieve error', \
              'It seems your job is not finished yet.')
          self.notice_text.set("* Check peak counts if I-PINE keeps failing (Use 'pv' tool).")      
          return      
      except:
        tkMessageBox.showerror('Retrieve error', \
            'It seems your job is not finished yet.')
        self.notice_text.set("* Check peak counts if I-PINE keeps failing (Use 'pv' tool).")      
        return      

    
    if clicked == 2 or pine_status_lines[0].strip() == 'finished':
      pine_ndpplot_url = pine_result_url + 'ndpplot_PINE.ini'      
      pecan_ndpplot_url = pine_result_url + 'ndpplot_PECAN.ini'
      lacs_co_ndpplot_url = pine_result_url + 'ndpplot_LACS_CACB_CO.ini'
      lacs_ca_ndpplot_url = pine_result_url + 'ndpplot_LACS_CACB_CA.ini'
      lacs_cb_ndpplot_url = pine_result_url + 'ndpplot_LACS_CACB_CB.ini'
      hdopbt_ndpplot_url = pine_result_url + 'ndpplot_CORE.ini'
      rci_s2_ndpplot_url = pine_result_url + 'talosn_results/ndpplot_talosn_s2.ini'
      ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')   
      
      
      if tkMessageBox.askokcancel('I-PINE finished','Do you want to download and unpack I-PINE package?'):
        pine_dir = os.path.join(self.session.project.sparky_directory, 'I-PINE')
        pine_job_dir = os.path.join(pine_dir, pine_job_id)
        pine_path = os.path.join(pine_job_dir, 'all_results.zip')
        try:
          if not os.path.exists(pine_dir):
            os.makedirs(pine_dir)
          if not os.path.exists(pine_job_dir):
            os.makedirs(pine_job_dir)

          pine_response = urllib2.urlopen(pine_package_url, timeout=45)
          pine_html = pine_response.read()
          f = open(pine_path, 'wb')
          f.write(pine_html)
          f.close()
          
          import zipfile
          zip_ref = zipfile.ZipFile(pine_path, 'r')
          zip_ref.extractall(pine_job_dir)
          zip_ref.close()
        except:
          tkMessageBox.showerror("Error", "I-PINE results could not be retrieved or could not be unpacked. Check I-PINE directory if you have all_results.zip file.")

      if tkMessageBox.askokcancel('I-PINE finished','Do you want to plot PECAN secondary structure prediction results?'):
        try:      
          pecan_ndpplot = urllib2.urlopen(pecan_ndpplot_url, timeout=10)
          lines = pecan_ndpplot.readlines()
          # write ndpplot.ini
          f = open(ini_path, 'w')
          for line in lines:
            f.write(line)
          f.close()  
          # open ndpplot
          nmrfam.run_npdplot(self.session)
        except:
          tkMessageBox.showerror('Retrieve error','PECAN NDPPLOT results could not be retrieved.')
          pass  

      if tkMessageBox.askokcancel('I-PINE finished','Do you want to plot I-PINE chemical shift assignment results?'):
        try:
          pine_ndpplot = urllib2.urlopen(pine_ndpplot_url, timeout=10)
          lines = pine_ndpplot.readlines()
          if len(lines) > 5:
            if lines[0].find('[GENERAL_START]') != -1:
              # write ndpplot.ini
              f = open(ini_path, 'w')
              for line in lines:
                f.write(line)
              f.close()  
              # open ndpplot
              nmrfam.run_npdplot(self.session)
        except:
          tkMessageBox.showerror('Retrieve error','I-PINE NDPPLOT results could not be retrieved.')
          pass

      if tkMessageBox.askokcancel('I-PINE finished','Do you want to plot LACS chemical shift validation results?'):
        try:
          lacs_co_ndpplot = urllib2.urlopen(lacs_co_ndpplot_url, timeout=10)
          lines = lacs_co_ndpplot.readlines()
          if len(lines) > 5:
            if lines[0].find('[GENERAL_START]') != -1:
              # write ndpplot.ini
              f = open(ini_path, 'w')
              for line in lines:
                f.write(line)
              f.close()
              # open ndpplot          
              nmrfam.run_npdplot(self.session)          
              time.sleep(3)
        except:
          pass
          
        try:
          lacs_cb_ndpplot = urllib2.urlopen(lacs_cb_ndpplot_url, timeout=10)
          lines = lacs_cb_ndpplot.readlines()
          if len(lines) > 5:
            if lines[0].find('[GENERAL_START]') != -1:
              # write ndpplot.ini
              f = open(ini_path, 'w')
              for line in lines:
                f.write(line)
              f.close()  
              # open ndpplot          
              nmrfam.run_npdplot(self.session)          
              time.sleep(3)          
        except:
          pass   
                         
        try:
          lacs_ca_ndpplot = urllib2.urlopen(lacs_ca_ndpplot_url, timeout=10)
          lines = lacs_ca_ndpplot.readlines()
          if len(lines) > 5:
            if lines[0].find('[GENERAL_START]') != -1:
              # write ndpplot.ini
              f = open(ini_path, 'w')
              for line in lines:
                f.write(line)
              f.close()  
              # open ndpplot          
              nmrfam.run_npdplot(self.session)          
        except:
          pass                    
               
      if tkMessageBox.askokcancel('I-PINE finished','Do you want to plot PACSY hydrophobic prediction results?'):
        try:
          hdopbt_ndpplot = urllib2.urlopen(hdopbt_ndpplot_url, timeout=10)
          lines = hdopbt_ndpplot.readlines()
          if len(lines) > 5:
            if lines[0].find('[GENERAL_START]') != -1:
              # write ndpplot.ini
              f = open(ini_path, 'w')
              for line in lines:
                f.write(line)
              f.close()  
              # open ndpplot          
              nmrfam.run_npdplot(self.session)          
              time.sleep(3)          
        except:
          pass

      if tkMessageBox.askokcancel('I-PINE finished','Do you want to visualize ordered regions (RCI-S2 prediction)?'):
        try:
          rci_s2_ndpplot = urllib2.urlopen(rci_s2_ndpplot_url, timeout=10)
          lines = rci_s2_ndpplot.readlines()
          if len(lines) > 5:
            if lines[0].find('[GENERAL_START]') == -1:
              tkMessageBox.showinfo('TALOS-N not finished', 'It seems TALOS-N job is not finished. Try again a few minutes later.')
            else:
              # write ndpplot.ini
              f = open(ini_path, 'w')
              for line in lines:
                f.write(line)
              f.close()  
              # open ndpplot          
              nmrfam.run_npdplot(self.session)          
              time.sleep(3)          
          else:  
            tkMessageBox.showinfo('TALOS-N not finished', 'It seems TALOS-N job is not finished. Try again a few minutes later.')
        except:
          tkMessageBox.showinfo('TALOS-N not finished', 'It seems TALOS-N job is not finished. Try again a few minutes later.')
          pass
                            
      if tkMessageBox.askokcancel('I-PINE finished','Do you want to create I-PINE labels by PINE-Sparky.2 ?'):
        # read - backbone, sidechain
        pine_bb_url = pine_result_url + 'protein_backbone_assignment.txt'
        pine_sc_url = pine_result_url + 'sidechain_table.txt'
        
        try:      
          pine_bb = urllib2.urlopen(pine_bb_url, timeout=10)        
          pine_bb_lines = pine_bb.readlines()
          pine_sc = urllib2.urlopen(pine_sc_url, timeout=10)          
          pine_sc_lines = pine_sc.readlines()
        except:
          tkMessageBox.showerror('Retrieve error','I-PINE results could not be retrieved.')
          pass           
          
        if self.create_pine_labels(pine_bb_lines, pine_sc_lines):
          tkMessageBox.showinfo('PINE-Sparky','I-PINE labels created.')
          
          if tkMessageBox.askokcancel('I-PINE finished', 'Do you want to assign peaks with I-PINE labels higher than 0.5 probability (A few seconds will be needed.) ?'):
            self.assign_the_best()
            
          tkMessageBox.showinfo('PINE-Sparky','Use PINE-Sparky extensions to use I-PINE labels. Start with two-letter-code "pp". Floating I-PINE labels can be selected with two-letter-code "se". ')            
        else:
          tkMessageBox.showerror('PINE label error','PINE labels could not be generated.')
          
    
      self.notice_text.set("* Check peak counts if I-PINE keeps failing (Use 'pv' tool).")                        
    else:
#      self.sparkytimer.stop()    
      pine_message = ''
      for line in pine_status_lines:
        pine_message = pine_message + line
      tkMessageBox.showerror('I-PINE error', pine_message)
      self.notice_text.set("* Check peak counts if I-PINE keeps failing (Use 'pv' tool).")    
      return
    
  # -----------------------------------------------------------------------------
  # 
  # PINE 3 specific exp: 'TOCSY-HSQC','HNHA', 'HBHANH','HN(CA)NNH','N15-NOESY','C13-NOESY'
  #                      'HNCOCA-4D', 'HNCACO-4D', 'HNCO(-1)CA-4D', 'simHNCOCA-4D'
  def check_pattern(self, spec_type, w1, w2, w3, w4):
    [shift, resonance, seq, seqidx, atom, prob] = w1
    [shift2, resonance2, seq2, seqidx2, atom2, prob2] = w2
    if w3 != None:
      [shift3, resonance3, seq3, seqidx3, atom3, prob3] = w3

    if (spec_type == 'HSQC (N15)' or spec_type == 'C13-HSQC') and (w3 != None):  return 0
    elif (spec_type != 'HSQC (N15)' and spec_type != 'C13-HSQC') and (w3 == None): return 0
    elif spec_type.find('4D') != -1 and w4 == None: return 0
    elif spec_type.find('4D') == -1 and w4 != None: return 0
    
    # 'HSQC (N15)','C13-HSQC'; same sequence index, same second alphabet for C-HSQC
    if (spec_type == 'HSQC (N15)'):
      if seqidx != seqidx2: return 0
      if (atom == 'N' and atom2 == 'H') or (atom == 'H' and atom2 == 'N'): return 1
      return 0
      
    if (spec_type == 'C13-HSQC'):
      if seqidx != seqidx2: return 0
      if (atom[0] != 'C' and atom2[0] == 'H') and (atom[0] != 'H' and atom2[0] == 'C'): return 0
      if (len(atom) == 1) or (len(atom2) == 1): return 0
      if (atom[1] == atom2[1]): return 1
      return 0
      
    # sort by shift!
    if spec_type.find('4D') != -1:
      sort_list = sorted([w1, w2, w3, w4], key=getFirstKey)
      [w1, w2, w3, w4] = sort_list
    else:
      sort_list = sorted([w1, w2, w3], key=getFirstKey)
      [w1, w2, w3] = sort_list
    [shift, resonance, seq, seqidx, atom, prob] = w1
    [shift2, resonance2, seq2, seqidx2, atom2, prob2] = w2
    [shift3, resonance3, seq3, seqidx3, atom3, prob3] = w3
    if spec_type.find('4D') != -1:
      [shift4, resonance4, seq4, seqidx4, atom4, prob4] = w1
      
    # H - N - C
    if (spec_type == 'HN(CA)CO'):  # H - N - C
      if seqidx != seqidx2 or abs(seqidx-seqidx3) > 1 or seqidx < seqidx3: return 0
      if atom != 'H' or atom2 != 'N' or atom3 != 'C': return 0
      return 1
    
    if (spec_type == 'HNCO'):
      if seqidx != seqidx2 or abs(seqidx-seqidx3) > 1 or seqidx <= seqidx3: return 0
      if atom != 'H' or atom2 != 'N' or atom3 != 'C': return 0        
      return 1
      
    # H - CX - N
    if spec_type == 'HN(CO)CA':
      if seqidx != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx <= seqidx2: return 0
      if atom != 'H' or atom2 != 'CA' or atom3 != 'N': return 0
      return 1
    
    if spec_type == 'HNCA':
      if seqidx != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx < seqidx2: return 0
      if atom != 'H' or atom2 != 'CA' or atom3 != 'N': return 0
      return 1
      
    if spec_type == 'CB(CA)(CO)NH':
      if seqidx != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx <= seqidx2: return 0
      if atom != 'H' or atom2 != 'CB' or atom3 != 'N': return 0
      return 1
    
    if spec_type == 'HN(CA)CB':
      if seqidx != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx < seqidx2: return 0
      if atom != 'H' or atom2 != 'CB' or atom3 != 'N': return 0
      return 1
          
    if spec_type == 'CBCA(CO)NH' or spec_type == 'HN(CO)CACB':
      if seqidx != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx <= seqidx2: return 0
      if atom != 'H' or (atom2 != 'CA' and atom2 != 'CB') or atom3 != 'N': return 0
      return 1
    
    if spec_type == 'HNCACB':
      if seqidx != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx < seqidx2: return 0
      if atom != 'H' or (atom2 != 'CA' and atom2 != 'CB') or atom3 != 'N': return 0
      return 1
              
    if spec_type == 'C(CO)NH':
      if seqidx != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx <= seqidx2: return 0
      if atom != 'H' or atom2[0] != 'C' or atom3 != 'N': return 0
      return 1
               
    # HX - H - N                    
    if spec_type == 'HA(CO)NH':
      if seqidx2 != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx >= seqidx2: return 0
      try:
        if (atom[0] != 'H' or atom[1] != 'A') or atom2[0] != 'H' or atom3 != 'N': return 0
      except:
        return 0  
      return 1
          
    if spec_type == 'HBHA(CO)NH':
      if seqidx2 != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx >= seqidx2: return 0
      try:
        if atom[0] != 'H' or (atom[1] != 'A' and atom[1] != 'B') or atom2 != 'H' or atom3 != 'N': return 0
      except:
        return 0  
      return 1
      
    if spec_type == 'H(CCO)NH':
      if seqidx2 != seqidx3 or abs(seqidx-seqidx2) > 1 or seqidx >= seqidx2: return 0
      try:
        if atom[0] != 'H' or atom2 != 'H' or atom3 != 'N': return 0
      except:
        return 0  
      return 1
      
    if spec_type == 'TOCSY-HSQC':
      if seqidx2 != seqidx3 or seqidx != seqidx2: return 0
      try:
        if atom[0] != 'H' or atom2[0] != 'H' or atom3 != 'N': return 0
        if atom != 'H' and atom2 != 'H': return 0
      except:
        return 0
      return 1
    
    if spec_type == 'HBHANH':
      if seqidx2 != seqidx3 or seqidx != seqidx2: return 0
      try:
        if atom[0] != 'H' or atom2 != 'H' or atom3 != 'N': return 0
        if atom[1] != 'A' and atom[1] != 'B': return 0
      except:
        return 0
      return 1
    
    if spec_type == 'HN(CA)NNH':    
      if abs(seqidx2-seqidx3) > 1 or abs(seqidx-seqidx3) > 1: return 0
      try:
        if atom != 'H' or atom2 != 'N' or atom3 != 'N': return 0
      except:
        return 0
      return 1
      
    if spec_type == 'HNCOCA-4D':
      if seqidx != seqidx3 or seqidx3-1 == seqidx2 or seqidx2 != seqidx4: return 0
      try:
        if atom != 'H' or atom2 != 'CA' or atom3 != 'N' or atom4 != 'C': return 0
      except:
        return 0
      return 1
      
    if spec_type == 'HNCACO-4D':
      if seqidx != seqidx3 or abs(seqidx3-seqidx2) > 1 or seqidx2 != seqidx4: return 0
      try:
        if atom != 'H' or atom2 != 'CA' or atom3 != 'N' or atom4 != 'C': return 0
      except:
        return 0
      return 1
      
    if spec_type == 'HNCO(-1)CA-4D':
      if seqidx != seqidx3 or seqidx2 != seqidx3 or seqidx != seqidx4: return 0
      try:
        if atom != 'H' or atom2 != 'CA' or atom3 != 'N' or atom4 != 'C': return 0
      except:
        return 0
      return 1

    if spec_type == 'simHNCOCA-4D':
      if seqidx != seqidx3 or abs(seqidx2 - seqidx1) > 1 or seqidx1-1 != seqidx4: return 0
      try:
        if atom != 'H' or atom2 != 'CA' or atom3 != 'N' or atom4 != 'C': return 0
      except:
        return 0
      return 1
      
    if spec_type == 'N15-NOESY' or spec_type == 'C13-NOESY':
      return 0

    hydrogen_order = 'ABGDE'
    
    # HX-CX-CX
    if spec_type == 'CCH-TOCSY' or spec_type == 'CCH-COSY':
      if seqidx != seqidx2 or seqidx != seqidx3: return 0
      if atom[0] != 'H' or atom2[0] != 'C' or atom3[0] != 'C': return 0
      try:
        if atom[1] != atom2[1] and atom[1] != atom3[1]: return 0
      except:
        return 0
      try:
        if atom[1:3] != atom2[1:3] and atom[1:3] != atom3[1:3]: return 0
      except:
        return 0  
      if spec_type.find('COSY') != -1:  
        try:
          idx1 = hydrogen_order.index(atom2[1])
          idx2 = hydrogen_order.index(atom3[1])
          if abs(idx1-idx2) > 1: return 0
        except:
          return 0          
      return 1
    
    # HX-HX-CX              
    if spec_type == 'HCCH-TOCSY' or spec_type == 'HCCH-COSY':
      if seqidx != seqidx2 or seqidx != seqidx3: return 0
      if atom[0] != 'H' or atom2[0] != 'H' or atom3[0] != 'C': return 0      
      try:
        if atom[1] != atom3[1] and atom2[1] != atom3[1]: return 0
      except:
        return 0
      try:
        if atom[1:3] != atom3[1:3] and atom2[1:3] != atom3[1:3]: return 0
      except:
        return 0  
      if spec_type.find('COSY') != -1:  
        try:
          idx1 = hydrogen_order.index(atom[1])
          idx2 = hydrogen_order.index(atom2[1])
          if abs(idx1-idx2) > 1: return 0
        except:
          return 0  
      return 1      
      
  # -----------------------------------------------------------------------------
  #
  def add_resonance_to_list(self, shift, resonance, seq, seqidx, atom, prob):
    if prob < 0.001: return
    if shift > 0.001 and shift < 200.0:
      if shift < 14.0:  iShiftIdx = int( (shift + 5.05) * 10.0 ) # proton rule
      else: iShiftIdx = int( shift + 200.5 )
      
      self.resonance_list[iShiftIdx-1].append([shift, resonance, seq, seqidx, atom, prob])      
      self.resonance_list[iShiftIdx].append([shift, resonance, seq, seqidx, atom, prob])
      self.resonance_list[iShiftIdx+1].append([shift, resonance, seq, seqidx, atom, prob])
  # -----------------------------------------------------------------------------
  #
  def sort_resonance_list(self):
    for i in range(len(self.resonance_list)):
      temp_list = self.resonance_list[i]
      if len(temp_list) != 0:
        self.resonance_ascend_list[i] = sorted(temp_list, key=getFirstKey)
        self.resonance_descend_list[i] = sorted(temp_list, key=getFirstKey, reverse = True)

  # -----------------------------------------------------------------------------
  #
  def find_probables(self, peak, spec_type):
    probable_list = []
    probable_sorted_list = []    
    
    res_list = [[], [], [], []]
    tol_list = []
    # fill res_list
    for dim in range(len(peak.frequency)):
      shift = peak.frequency[dim]
      
      if shift < 14.0:  iShiftIdx = int( (shift + 5.05) * 10.0 ) # proton rule
      else: iShiftIdx = int( shift + 200.5 )
      
      # get tolerances
      try:
        if shift < 14.0: tol = float(self.htol_ppm.get())
        elif shift < 80.0: tol = float(self.ctol_ppm.get())
        elif shift < 140.0: tol = float(self.ntol_ppm.get())
        else: tol = float(self.ctol_ppm.get())
      except:
        if shift < 14.0: tol = 0.02
        else: tol = 0.2     
               
      from_shift = shift-tol
      to_shift = shift+tol
      tol_list.append(tol)
      
      # iShiftIdx-1 -> go descending
      desc_list = self.resonance_descend_list[iShiftIdx-1]
      shift_list = self.resonance_ascend_list[iShiftIdx]
      asce_list = self.resonance_ascend_list[iShiftIdx+1]
      for [shift, resonance, seq, seqidx, atom, prob] in desc_list:
        if shift < from_shift: break
        if shift >= from_shift and shift <= to_shift:
          iExist = 0
          for (shift2, resonance2, seq2, seqidx2, atom2, prob2) in res_list[dim]:
            if shift == shift2 and resonance == resonance2 and seqidx == seqidx2 and atom == atom2:
              iExist = 1
              break
          if iExist == 0: res_list[dim].append([shift, resonance, seq, seqidx, atom, prob])
      # iShiftIdx -> go ascending         
      for [shift, resonance, seq, seqidx, atom, prob] in shift_list:
        if shift > to_shift: break
        if shift >= from_shift and shift <= to_shift:
          iExist = 0
          for (shift2, resonance2, seq2, seqidx2, atom2, prob2) in res_list[dim]:
            if shift == shift2 and resonance == resonance2 and seqidx == seqidx2 and atom == atom2:
              iExist = 1
              break
          if iExist == 0: res_list[dim].append([shift, resonance, seq, seqidx, atom, prob])
      # iShiftIdx -> go ascending         
      for [shift, resonance, seq, seqidx, atom, prob] in asce_list:
        if shift > to_shift: break
        if shift >= from_shift and shift <= to_shift:
          iExist = 0
          for (shift2, resonance2, seq2, seqidx2, atom2, prob2) in res_list[dim]:
            if shift == shift2 and resonance == resonance2 and seqidx == seqidx2 and atom == atom2:
              iExist = 1
              break
          if iExist == 0: res_list[dim].append([shift, resonance, seq, seqidx, atom, prob])
              
    # make probable_list, and check okay pattern
    for w1 in res_list[0]:
      for w2 in res_list[1]:
        pine_diff = abs(w1[0]-peak.frequency[0])/tol_list[0] + abs(w2[0]-peak.frequency[1])/tol_list[1]
        if len(peak.frequency) == 2:
          if self.check_pattern(spec_type, w1, w2, None, None) == 1:
            atm_list = [w1[4],w2[4]]
            seqidx_list = [w1[3],w2[3]]
            prob_list = [w1[5],w2[5]]
            try:
              idx1 = atm_list.index('N')
              idx2 = atm_list.index('H')
              if seqidx_list[idx1] == seqidx_list[idx2]:
                # in this case, they need to be the same probability
                if prob_list[idx1] != prob_list[idx2]: continue                
                combined_prob = w1[5]
              else: combined_prob = w1[5]*w2[5]
            except:
              combined_prob = w1[5]*w2[5]                          
            pinelabel = '%s-%s[%.3f]:(%.3f,%.3f)' % (w1[1], w2[1], combined_prob, peak.frequency[0], peak.frequency[1])
            asgnlabel = '%s-%s[' % (w1[1], w2[1])
            iFound = 0
            for (prob, plabel, pdiff) in probable_list:
              if plabel.find(asgnlabel) != -1:
                iFound = 1
                break
            if iFound == 0:
              probable_list.append([combined_prob, pinelabel, pine_diff])
            continue

        if len(peak.frequency) == 3:
          for w3 in res_list[2]:
            pine_diff = abs(w1[0]-peak.frequency[0])/tol_list[0] + abs(w2[0]-peak.frequency[1])/tol_list[1] + abs(w3[0]-peak.frequency[2])/tol_list[2]
            if self.check_pattern(spec_type, w1, w2, w3, None) == 1:
              atm_list = [w1[4],w2[4],w3[4]]
              seqidx_list = [w1[3],w2[3],w3[3]]
              prob_list = [w1[5],w2[5],w3[5]]
              try:
                idx1 = atm_list.index('N')
                idx2 = atm_list.index('H')
                if seqidx_list[idx1] == seqidx_list[idx2]:
                  # in this case, they need to be the same probability              
                  if prob_list[idx1] != prob_list[idx2]: continue
                  if prob_list[idx1] != 0:
                    combined_prob = w1[5]*w2[5]*w3[5] / prob_list[idx1]
                  else:
                    combined_prob = 0
                else:      
                  combined_prob = w1[5]*w2[5]*w3[5]  
              except:
                combined_prob = w1[5]*w2[5]*w3[5]  
                          
              pinelabel = '%s-%s-%s[%.3f]:(%.3f,%.3f,%.3f)' % (w1[1], w2[1], w3[1], combined_prob, peak.frequency[0], peak.frequency[1], peak.frequency[2])
              asgnlabel = '%s-%s-%s[' % (w1[1], w2[1], w3[1])
              iFound = 0
              for (prob, plabel, pdiff) in probable_list:
                if plabel.find(asgnlabel) != -1:
                  iFound = 1
                  break
              if iFound == 0:
                probable_list.append([combined_prob, pinelabel, pine_diff])
              continue

        if len(peak.frequency) == 4:
          for w3 in res_list[2]:
            for w4 in res_list[3]:
              pine_diff = abs(w1[0]-peak.frequency[0])/tol_list[0] + abs(w2[0]-peak.frequency[1])/tol_list[1] + abs(w3[0]-peak.frequency[2])/tol_list[2] + abs(w4[0]-peak.frequency[3])/tol_list[3]
            if self.check_pattern(spec_type, w1, w2, w3, w4) == 1:
              atm_list = [w1[4],w2[4],w3[4],w4[4]]
              seqidx_list = [w1[3],w2[3],w3[3],w4[3]]
              prob_list = [w1[5],w2[5],w3[5],w4[5]]
              try:
                idx1 = atm_list.index('N')
                idx2 = atm_list.index('H')
                if seqidx_list[idx1] == seqidx_list[idx2]:
                  # in this case, they need to be the same probability              
                  if prob_list[idx1] != prob_list[idx2]: continue
                  if prob_list[idx1] != 0:
                    combined_prob = w1[5]*w2[5]*w3[5]*w4[5] / prob_list[idx1]
                  else:
                    combined_prob = 0
                else:      
                  combined_prob = w1[5]*w2[5]*w3[5]*w4[5]
              except:
                combined_prob = w1[5]*w2[5]*w3[5]*w4[5]
                          
              pinelabel = '%s-%s-%s-%s[%.3f]:(%.3f,%.3f,%.3f,%.3f)' % (w1[1], w2[1], w3[1], w4[1], combined_prob, peak.frequency[0], peak.frequency[1], peak.frequency[2], peak.frequency[3])
              asgnlabel = '%s-%s-%s-%s[' % (w1[1], w2[1], w3[1], w4[1])
              iFound = 0
              for (prob, plabel, pdiff) in probable_list:
                if plabel.find(asgnlabel) != -1:
                  iFound = 1
                  break
              if iFound == 0:
                probable_list.append([combined_prob, pinelabel, pine_diff])
              continue

    # python sort is not working for unknown reason. so we do bubble sort
    temp_list = sorted(probable_list, key=lambda probable: (probable[0], probable[2]), reverse = True)  
    return temp_list
    #for item in temp_list:
    #  probable_sorted_list.append(item[1])
                
    #return probable_sorted_list    
  # -----------------------------------------------------------------------------
  #  

  # PINE SPARKY module   
  def create_pine_labels(self, pine_bb_lines, pine_sc_lines):                    
    #pine_types = ('HSQC (N15)','C13-HSQC','HN(CA)CO','HNCO','CBCA(CO)NH','HNCACB','HN(CO)CA','HNCA','CB(CA)(CO)NH','HN(CA)CB','C(CO)NH','H(CCO)NH','HBHA(CO)NH','HA(CO)NH','HCCH-TOCSY','CCH-TOCSY','HCCH-COSY','CCH-COSY')
    # generate ".save_pl"
    # # M1CA-M1N-M1H[1.0]:(53.2120,124.321,8.23400)
    # sparky.Label(spec, 'label', 'color', (position))
    # sparky.Label(spec, 'M1CA-M1N-M1H[1.0]:(53.2120,124.321,8.23400)', 'blue', (53.2120,124.321,8.23400))
    
    # remove all floating PINE labels first      
    for peak in self.session.selected_peaks():
      peak.selected = 0
      
    for (s_type, spec) in self.listbox.line_data:          
      for pLabel in spec.label_list():
        if pLabel.peak == None: 
          if pLabel.text.find(']:(') <> -1:
            pLabel.selected = 1
        else: pLabel.selected = 0
    self.session.command_characters("")        

    iSeqCount = len(pine_bb_lines)-1
    
    # parse chemical shifts
    szSeq = ' '
    self.resonance_list = []
    self.resonance_ascend_list = []    
    self.resonance_descend_list = []
    for i in range(400):    # -5 ~ 14 -> H, 14 ~ -> C, N
      self.resonance_list.append([])
      self.resonance_ascend_list.append([])      
      self.resonance_descend_list.append([])      
      
    for line in pine_bb_lines:
      try:
        splited = line.strip().split()
        iSeqIdx = int(splited[0])
        szA = myseq.aaa2a(splited[1])
        szSeq = szSeq + szA
        # read bb prob
        # Prob 1
        prob = float(splited[2])        
        # H
        resonance = '%s%dH' % (szA, iSeqIdx)
        shift = float(splited[3])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'H', prob)
        
        # N
        resonance = '%s%dN' % (szA, iSeqIdx)
        shift = float(splited[4])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'N', prob)
        
        # CO
        resonance = '%s%dC' % (szA, iSeqIdx)
        shift = float(splited[5])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'C', prob)
                
        # CA                
        resonance = '%s%dCA' % (szA, iSeqIdx)
        shift = float(splited[6])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'CA', prob)

        # CB                
        resonance = '%s%dCB' % (szA, iSeqIdx)
        shift = float(splited[7])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'CB', prob)
        
        # Prob 2
        prob = float(splited[8])
        # H
        resonance = '%s%dH' % (szA, iSeqIdx)
        shift = float(splited[9])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'H', prob)
        # N
        resonance = '%s%dN' % (szA, iSeqIdx)
        shift = float(splited[10])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'N', prob)
        
        # Prob 3
        prob = float(splited[11])
        # H
        resonance = '%s%dH' % (szA, iSeqIdx)
        shift = float(splited[12])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'H', prob)
        # N
        resonance = '%s%dN' % (szA, iSeqIdx)
        shift = float(splited[13])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'N', prob)
        
        # Prob 4
        prob = float(splited[14])
        # H
        resonance = '%s%dH' % (szA, iSeqIdx)
        shift = float(splited[15])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'H', prob)
        # N
        resonance = '%s%dN' % (szA, iSeqIdx)
        shift = float(splited[16])
        self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, 'N', prob)
      except:
        continue        
        
    # side chains        
    for line in pine_sc_lines:        
      try:  
        splited = line.strip().split()
        iSeqIdx = int(splited[1])
        szA = myseq.aaa2a(splited[2])
        szAtom = splited[3]
        resonance = '%s%d%s' % (szA, iSeqIdx, szAtom)
      except:
        tkMessageBox.showerror('PINE label error',splited)      ##
        continue
                
      try:
        for i in range(0, 4):
          prob = float(splited[4+2*i])
          shift = float(splited[5+2*i])
          self.add_resonance_to_list(shift, resonance, szA, iSeqIdx, szAtom, prob)
      except:
        tkMessageBox.showerror('PINE label error2',splited)      ##
        continue          
  
    try:
      self.sort_resonance_list()
    except:
      tkMessageBox.showerror('PINE label error', 'sort error')      ##
      return 0
      
    # loop spectrum
    # generate labels and .pl files
    pinelabel_color = ['turquoise', 'orange', 'magenta', 'tomato', 'gray']
    for (s_type, spec) in self.listbox.line_data:
      try:
        f = open(spec.save_path+'_pl', 'w')
      except:
        tkMessageBox.showerror('PINE label error', spec.save_path+'_pl is not writable.')      ##
        return 0
        
      spec_probable_list = []                
      for peak in spec.peak_list():
        probable_list = self.find_probables(peak, s_type)
        spec_probable_list.extend(probable_list)        
        for i in range(len(probable_list)):
          prob, pinelabel, pinediff = probable_list[i]
          # make labels- turquoise, orange, margenta, tomato, gray-  
          if i < len(pinelabel_color):          pinecolor = pinelabel_color[i]
          else:                                 pinecolor = 'gray'
          sparky.Label(spec, pinelabel, pinecolor, peak.frequency)
          # write to file
          #f.write(pinelabel+'\n')
      sorted_probable_list = sorted(spec_probable_list, key=lambda prob: (prob[0], prob[2]), reverse=True)    
      for prob, pinelabel, pinediff in sorted_probable_list:
        f.write(pinelabel+'\n')
      f.close()
    return 1      
  # -----------------------------------------------------------------------------
  def assign_the_best(self):
  
    iTotal = 0
    iAssigned = 0
    iDuplicate = 0
    session = self.session
    
    # we will deselect all peaks first because we will delete floating labels at the end
    selected_peaks = session.selected_peaks()
    for peak in selected_peaks:
      peak.selected = 0
    
    # self.notice_text.set("* Check peak counts if PINE keeps failing (Use 'pv' tool).")
    for (s_type, spec) in self.listbox.line_data:
      if spec == None: continue
      if len(spec.selected_peaks()) == 0:
        peaks = spec.peak_list()
      else:
        peaks = spec.selected_peaks()

      for pLabel in spec.label_list():
        pLabel.selected = 0

      pParsedLabelList = [] # parse first. -10.0 (0) to 200.0 (2100).   
      pLabelList = []
      pSameList = []
      pFloatList = []
      pProbList = []
      
      # generate empty list
      for i in range(2100):
        pParsedLabelList.append([])

      # parse labels
      for pLabel in spec.label_list():  
        splited = pLabel.text.split(':')        # M1CA-M1N-M1H[1.0]:(53.2120,124.321,8.23400)
        if len(splited) == 1: continue          # if it doesn't have position property, then continue.

        szLabel = (splited[0].split('['))[0]
        szProb = (((splited[0].split('['))[1]).split(']'))[0]
        try:
          fProb = float(szProb)
          if fProb < 0.5: continue        # probability lower than 0.5 will not be used
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

      iTotal = iTotal + len(peaks)

      for pPeak in peaks:
        if pPeak.is_assigned == 1:
            continue;
        pPeak.selected = 0
        del pLabelList[:]
        del pFloatList[:]
        del pProbList[:]

        idx = int(pPeak.frequency[0]*10.0 + 100.0)
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
        if len(pFloatList) == 0:          continue

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
    
      for i in range(len(peaks)):
        pks1 = peaks[i]
        if pks1.is_assigned != 1: continue
        for j in range(len(peaks)):
          if i == j: continue
          pks2 = peaks[j]
          if pks2.is_assigned != 1: continue          
          if pks1.assignment == pks2.assignment:
            iDuplicate = iDuplicate + 1  

    session.command_characters("")
    
    szAssigned = '%d of %d peaks assigned. %d peaks have duplicated assignments in the same spectrum.' % (iAssigned, iTotal, iDuplicate)
    tkMessageBox.showinfo('Assign the Best by I-PINE', szAssigned)

  # -----------------------------------------------------------------------------
  #    
  def web_cb(self):  
    import pineassign
    pineassign.export_pine(self.session)
  # -----------------------------------------------------------------------------
  #    
  def user_group_cb(self):  
    url = 'http://i-pine.nmrfam.wisc.edu/usergroup.html'
    import webbrowser
    webbrowser.open(url)
    
# -----------------------------------------------------------------------------
#
def run_pine(session):
  sputil.the_dialog(pine_dialog,session).show_window(1)    
