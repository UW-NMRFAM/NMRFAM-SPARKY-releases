# -----------------------------------------------------------------------------
# ssAPES peak picking
# 
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: November 24, 2019
# 
# APES algorithm regarding the following paper:
#   Structural proteomics by NMR spectroscopy
#     J Shin, W Lee, W Lee - 2008, Expert Review of Proteomics
#
#
# -----------------------------------------------------------------------------

import string
import Tkinter

import os
import axes
import myseq
import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox
import tkSimpleDialog
import atomnames

dMultDev = 3.0

# seq_id, # of expected peaks compared to sequence
ssapes_2D_specs = {'NCA':     {'N': ( 0, 1), 'CA':  ( 0, 1)},
                   'NCACB':   {'N': ( 0, 1), 'CACB':( 0, 2)}, 
                   'N(CA)CX': {'N': ( 0, 1), 'CX':  ( 0, 6)},
                   'NCO':     {'N': ( 0, 1), 'C':   (-1,1)},
                   'N(CO)CX': {'N': ( 0, 1), 'CX':  (-1,6)},
                   'CC':      {'CX':( 0, 1), 'CX':  ( 0, 1)}}
ssapes_3D_spec_names = {'NCACB': ('N', 'CA', 'CACB'), 
                  'NCACX': ('N', 'CA', 'CX'), 
                  'NCACO': ('N', 'CA', 'C'), 
                  'NCOCA': ('N', 'C', 'CA'), 
                  'NCOCACB': ('N', 'C', 'CACB'), 
                  'NCOCX': ('N', 'C', 'CX'),
                  'CONCA': ('C', 'N', 'CA'), 
                  'CON(CA)CX': ('C', 'N', 'CX'), 
                  'CANCO': ('CA', 'N', 'C'), 
                  'CAN(CO)CA': ('CA', 'N', 'CA'), 
                  'CAN(CO)CACB': ('CA', 'N', 'CACB'), 
                  'CAN(CO)CX': ('CA', 'N', 'CX'), }

# -----------------------------------------------------------------------------
#
class ssapes_pick_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    self.session = session
    self.grid_widgets = []
    self.verbose = 1
    self.ipine_run = 0
    self.msg = ''
    self.user_email = ''
    
    tkutil.Dialog.__init__(self, session.tk, 'APES peak picking')

    # Num of residues
    res = tkutil.entry_field(self.top, 'Number of residues: ', initial = 100, width = 5)    
    res.frame.pack(side = 'top')
    self.res_count = res.variable
    
    # separator
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    # GUI
    self.spec_menu = []
    self.spec_pl = []
    for spec_name in apes_spec_names:
      m = apes_menu(session, self.top, spec_name + ': ', allow_no_choice = 1)
      m.frame.pack(side = 'top', anchor = 'nw')
      self.spec_menu.append(m)
      self.spec_pl.append([])

      # separator            
      if (spec_name == 'HN(CA)CB') or (spec_name == 'H(CCO)NH'):
        sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
        sep.pack(fill="both", padx=5,pady=5, side = 'top')

    # TOCSY COSY
    self.spec_menu2 = []
    self.spec_pl2 = []
    for i in range(3):
      m = apes_menu(session, self.top, 'TOCSY or COSY: ', allow_no_choice = 1)
      m.frame.pack(side = 'top', anchor = 'nw')
      self.spec_menu2.append(m)
      self.spec_pl2.append([])

    # separator
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
        
    # NOESY
    self.spec_menu3 = []
    self.spec_pl3 = []
    for i in range(2):
      m = apes_menu(session, self.top, '3D-NOESY: ', allow_no_choice = 1)
      m.frame.pack(side = 'top', anchor = 'nw')
      self.spec_menu3.append(m)
      self.spec_pl3.append([])

    # separator
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    br = tkutil.button_row(self.top,
         ('Run APES', self.pick_cb),
         ('Filter', self.filter_cb),         
         ('Stop', self.stop_cb),       
         ('Close', self.close_cb),
         )
    br.frame.pack(side = 'top', anchor = 'w')

    # separator    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
        
    tol_frame = Tkinter.Frame(self.top)
    tol_frame.pack(side = 'top', fill='both')
       
    self.ntol = tkutil.entry_field(tol_frame, 'N tol.:', initial = 0.200, width = 5)
    self.ntol.frame.grid(row = 0, column=0)     
    self.ntol_ppm = self.ntol.variable
          
    self.ctol = tkutil.entry_field(tol_frame, ', C tol.:', initial = 0.200, width = 5)
    self.ctol.frame.grid(row = 0, column=2)
    self.ctol_ppm = self.ctol.variable     
         
    self.htol = tkutil.entry_field(tol_frame, ', H tol.:', initial = 0.020, width = 5)
    self.htol.frame.grid(row=0, column=4)    
    self.htol_ppm = self.htol.variable

    progress_label = Tkinter.Label(self.top, anchor = 'nw')
    progress_label.pack(side = 'top', anchor = 'w')

    tkutil.Stoppable.__init__(self, progress_label, br.buttons[2])
    
    self.seq_list = myseq.ReadSequence(session)    
    if len(self.seq_list) != 0:
      res.variable.set(len(self.seq_list))
        
  # ---------------------------------------------------------------------------
  # Make sequence filter
  #
  def make_sequence_filter(self):
    self.seq_filter = []
    self.seq_Nfilter = []
    self.seq_Hfilter = []   
    self.seq_Cfilter = []    
    self.seq_CAfilter = []    
    self.seq_CBfilter = []
    self.seq_HAfilter = []    
    self.seq_HBfilter = []
    
    from tan import GetFreq2
    
    for i in range(3000): # -100.0 - +200.0
      self.seq_filter.append(0)
      self.seq_Nfilter.append(0)
      self.seq_Hfilter.append(0)
      self.seq_Cfilter.append(0)
      self.seq_CAfilter.append(0)
      self.seq_CBfilter.append(0)
      self.seq_HAfilter.append(0)
      self.seq_HBfilter.append(0)
      
    # no sequence  
    if len(self.seq_list) == 0: 
      import shiftstats    
      for a in atomnames.online_a:
        atms = atomnames.protein_atoms_by_group_2[a]
        for atm in atms:
          ast = shiftstats.atom_statistics(a, atm)
          if ast == None: continue
          m = ast.average_shift
          d = ast.shift_deviation
          dmin = m - dMultDev * d
          dmax = m + dMultDev * d
          
            
          imin = int( (dmin+100.0) * 10.0 )
          imax = int( (dmax+100.0) * 10.0 )
          imin = max(0, imin)
          imax = min(2999, imax)

          for i in range(imin, imax+1):
            self.seq_filter[i] = self.seq_filter[i] + 1
            try:
              if atm == 'N':  self.seq_Nfilter[i] = self.seq_Nfilter[i] + 1
            except:
              pass            
            try:
              if atm == 'H':  self.seq_Hfilter[i] = self.seq_Hfilter[i] + 1
            except:
              pass            
            try:
              if atm == 'C':  self.seq_Cfilter[i] = self.seq_Cfilter[i] + 1
            except:
              pass            
            try:
              if atm[0:2] == 'CA':  self.seq_CAfilter[i] = self.seq_CAfilter[i] + 1
            except:
              pass
            try:    
              if atm[0:2] == 'CB':  self.seq_CBfilter[i] = self.seq_CBfilter[i] + 1
            except:
              pass   
            try:
              if atm[0:2] == 'HA':  self.seq_HAfilter[i] = self.seq_HAfilter[i] + 1
            except:
              pass
            try:    
              if atm[0:2] == 'HB':  self.seq_HBfilter[i] = self.seq_HBfilter[i] + 1
            except:
              pass
              
      return
      
    from pacsylayout import pacsy_prev_layout
    from pacsylayout import pacsy_next_layout
    
    for i in range(len(self.seq_list)):
      (seqidx, seq) = self.seq_list[i]
      seq_prev = ''
      seq_next = ''
      prev_key = ''
      next_key = ''
      
      if i != 0:
        seq_prev = self.seq_list[i-1]
        prev_key = 'PREV_' + seq_prev[1]
        
      if i != len(self.seq_list)-1:
        seq_next = self.seq_list[i+1]
        next_key = 'NEXT_' + seq_next[1]
                        
      atms = atomnames.protein_atoms_by_group_2[seq]
      
      for atm in atms:
        pacsykey = '%s_%s' % (seq, atm)
        n1 = 0
        n2 = 0
        m1 = 0
        m2 = 0
        d1 = 0
        d2 = 0
        
        try:
          prev = pacsy_prev_layout[pacsykey]
          (m1, d1, n1, sk1, ku1) = prev[prev_key]
        except:
          pass
          
        try:
          next = pacsy_next_layout[pacsykey]
          (m2, d2, n2, sk2, ku2) = next[next_key]
        except:
          pass
        
        try:
          m = (m1 * n1 + m2 * n2) / (n1 + n2)
          d = (d1 * n1 + d2 * n2) / (n1 + n2)
        except:      
          continue
          
        dmin = m - dMultDev * d
        dmax = m + dMultDev * d
        
        
        # check if this is already assigned...
        f, d = GetFreq2(self.session, '%s%d' % (seq, seqidx), atm)
        if f < 200:
          if atm[0] == 'C':         tol = self.cppm
          elif atm[0] == 'N':       tol = self.nppm
          else: self.hppm
          dmin = f - dMultDev * self.hppm
          dmax = f + dMultDev * self.hppm
          
        imin = int( (dmin+100.0) * 10.0 )
        imax = int( (dmax+100.0) * 10.0 )
        imin = max(0, imin)
        imax = min(2999, imax)
        
        for j in range(imin, imax+1):
          self.seq_filter[j] = self.seq_filter[j] + 1
          try:
            if atm == 'N':  self.seq_Nfilter[j] = self.seq_Nfilter[j] + 1
          except:
            pass            
          try:
            if atm == 'H':  self.seq_Hfilter[j] = self.seq_Hfilter[j] + 1
          except:
            pass            
          try:
            if atm == 'C':  self.seq_Cfilter[j] = self.seq_Cfilter[j] + 1
          except:
            pass            
          try:
            if atm[0:2] == 'CA':  self.seq_CAfilter[j] = self.seq_CAfilter[j] + 1
          except:
            pass
          try:    
            if atm[0:2] == 'CB':  self.seq_CBfilter[j] = self.seq_CBfilter[j] + 1
          except:
            pass   
          try:
            if atm[0:2] == 'HA':  self.seq_HAfilter[j] = self.seq_HAfilter[j] + 1
          except:
            pass
          try:    
            if atm[0:2] == 'HB':  self.seq_HBfilter[j] = self.seq_HBfilter[j] + 1
          except:
            pass        
  # ---------------------------------------------------------------------------
  def filter_shift(self, seq_filter, shift):
    idx = int( (shift + 100.0) * 10.0 )
    if idx < 0 or idx > 2999: return 0
    return seq_filter[idx]
  #--
  def shift_to_index(self, shift):
    return int( (shift + 100.0) * 10.0 )
  def index_to_shift(self, idx):
    return float(idx) / 10.0 - 100.0     
  # ---------------------------------------------------------------------------
  def filter_shifts(self, peak, spec_pkg):      
    iSum = 0
    iValue = 0
    
    spec = spec_pkg[0]
    aspec = spec_pkg[1]
    layo_neg = spec_pkg[3]
    layo_pos = spec_pkg[4]
    
    #apes_specs = ('nhsqc', 'hnco', 'hn_ca_co', 'hn_co_ca', 'hnca', 'cbca_co_nh', 'hncacb', 'cb_ca_co_nh', 'hn_ca_cb', 'chsqc', 'cconh', 'hbhaconh', 'hcconh')
    
    shifts = peak.frequency

    for i in range(len(spec.nuclei)):
      if spec.nuclei[i] == '15N':
        iValue = self.filter_shift(self.seq_filter, shifts[i])
      elif spec.nuclei[i] == '1H':
        if apes_specs.index(aspec) < 9 or aspec == 'cconh':
          iValue = self.filter_shift(self.seq_Hfilter, shifts[i])
        elif aspec == 'hbhaconh':
          iValue = self.filter_shift(self.seq_Hfilter, shifts[i])
          iValue = iValue + self.filter_shift(self.seq_HAfilter, shifts[i])
          iValue = iValue + self.filter_shift(self.seq_HBfilter, shifts[i])
        else:
          iValue = self.filter_shift(self.seq_filter, shifts[i])        
      elif spec.nuclei[i] == '13C':
        if aspec == 'hnco' or aspec == 'hn_ca_co':
          iValue = self.filter_shift(self.seq_Cfilter, shifts[i])
        elif aspec == 'hnca' or aspec == 'hn_co_ca':      
          iValue = self.filter_shift(self.seq_CAfilter, shifts[i])
        elif aspec == 'cbca_co_nh' or aspec == 'hn_co_cacb' or aspec == 'hncacb' or aspec == 'cb_ca_co_nh' or aspec == 'hn_ca_cb':
          iValue = self.filter_shift(self.seq_CAfilter, shifts[i])
          iValue = iValue + self.filter_shift(self.seq_CAfilter, shifts[i])                    
        else:
          iValue = self.filter_shift(self.seq_filter, shifts[i])
      #if iValue == 0:
      #  return 0
      iSum = iSum + iValue
    if len(spec.nuclei) > iSum: return 0
    return iSum
  
  # ---------------------------------------------------------------------------
  # Take the higher of the spectrum peak picking threshold and the lowest
  # displayed contour level.
  #
  def picking_thresholds(self, pick_view):
    return (pick_view.negative_levels.lowest, pick_view.positive_levels.lowest) 
  # ---------------------------------------------------------------------------
  #
  def pick_cb(self):
    self.pick_core_cb(0)
  # ---------------------------------------------------------------------------
  #
  def filter_cb(self):
    self.pick_core_cb(1)
  # ---------------------------------------------------------------------------
  #
  def pick_core_cb(self, pick_mode):
  
    # N-HSQC cannot be empty.
    if self.spec_menu[0].spectrum() == None:
      if self.verbose == 1:   tkMessageBox.showerror('Error', 'N-HSQC cannot be none.');
      else:                   self.msg = 'N-HSQC cannot be none.'
      return
    # If side chain is there
    if (self.spec_menu[11].spectrum() != None) or (self.spec_menu[12].spectrum() != None) or (self.spec_menu[13].spectrum() != None):
      if self.spec_menu[10].spectrum() == None:
        if self.verbose == 1: tkMessageBox.showerror('Error', 'C-HSQC cannot be none for side chain peak picking.');
        else:                 self.msg = 'C-HSQC cannot be none for side chain peak picking.'
        return    
        
    
    try:
      htol = float(self.htol_ppm.get())
      ctol = float(self.ctol_ppm.get())
      ntol = float(self.ntol_ppm.get())
      self.hppm = htol
      self.cppm = ctol
      self.nppm = ntol
    except:  
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Tolerance value is set improperly.')
      else:                 self.msg = 'Tolerance value is set improperly.'
      return
      
    self.make_sequence_filter()

    # check if user wants to run I-PINE after APES
    # fill self.user_email in that case
    # this will be asked only when sequence exists
    if len(self.seq_list) != 0 and self.verbose == 1:
      # do we have enough information?
      if not tkMessageBox.askokcancel('APES', 'Do you want to launch APES followed by I-PINE automated assignment?'):
        self.ipine_run = 0
      else:
        # what is the user email ?
        for i in range(3):
          user_email = tkSimpleDialog.askstring('APES to I-PINE', 'Please type your email to receive the results back.', initialvalue = 'your_email@address.net')
          if user_email != 'your_email@address.net' and user_email != '' and user_email.find('@') != -1:
            self.user_email = user_email
            self.ipine_run = 1
            break
        if self.ipine_run == 0:
          tkMessageBox.showinfo('Error', "The email address could not be recognized. The I-PINE won't run after the APES.")

    self.pick_mode = pick_mode
    self.stoppable_call(self.pick_peaks)
    
    if self.msg.find('Succeeded') == -1:
      return 
    
    # TOCSY
    for sm in self.spec_menu2:
      if sm.spectrum() != None:
        hsqc_spec = None
        try:
          idx = list(sm.spectrum().nuclei).index('13C')
          hsqc_spec = self.spec_menu[10].spectrum()
        except:  
          hsqc_spec = self.spec_menu[0].spectrum()
        if hsqc_spec == None:  
          if self.verbose == 1: tkMessageBox.showerror('Error', 'Reference HSQC is not set.')
          else:                 self.msg = 'Reference HSQC is not set.'
        else:
          if pick_mode == 0:
            self.stoppable_call(self.auto_restrict_picking, sm.spectrum(), hsqc_spec, 'tocsy_cosy')

    # NOESY
    for sm in self.spec_menu3:
      if sm.spectrum() != None:
        hsqc_spec = None
        # N-NOESY or C-NOESY
        try:
          idx = list(sm.spectrum().nuclei).index('13C')
          hsqc_spec = self.spec_menu[10].spectrum() # C-HSQC for C-NOESY
        except:
          hsqc_spec = self.spec_menu[0].spectrum() # N-HSQC for N-NOESY

        if hsqc_spec == None:
          if self.verbose == 1: tkMessageBox.showerror('Error', 'Reference HSQC is not set.')
          else:                 self.msg = 'Reference HSQC is not set.'
        else:
          if pick_mode == 0:        
            self.stoppable_call(self.auto_restrict_picking, sm.spectrum(), hsqc_spec, 'noesy')


    if self.msg.find('Succeeded') == -1:
      if self.verbose == 1:    tkMessageBox.showerror('APES', self.msg);    
      return

    self.msg = 'Succeeded.'
    if self.ipine_run == 1 and os.path.exists(self.session.project.save_path + '.seq'):
      self.transfer_to_ipine(user_email)

    if self.verbose == 1:    
      tkMessageBox.showinfo('APES', 'APES peak picking finished. Please validate the results.');

  def transfer_to_ipine(self, user_email):
    persist_seq_path = self.session.project.save_path + '.seq'
    user_name = user_email.split('@')[0]
    ipine_params = [['user_name', user_name],['user_email',user_email],['pre_assign',0],['selective_label',0],['cs_rosetta',0],['seq_file',persist_seq_path],]

    # 
    apes2pine = { 'N-HSQC':'HSQC (N15)', 'HNCO':'HNCO', 'HN(CA)CO':'HN(CA)CO', 'HN(CO)CA':'HN(CO)CA', 'HNCA':'HNCA', 'CBCA(CO)NH':'CBCA(CO)NH', 'HN(CO)CACB':'HN(CO)CACB', 'HNCACB':'HNCACB', 'CB(CA)(CO)NH':'CB(CA)(CO)NH', 'HN(CA)CB':'HN(CA)CB',  'C-HSQC':'C13-HSQC', 'C(CO)NH':'C(CO)NH', 'HBHA(CO)NH':'HBHA(CO)NH', 'H(CCO)NH':'H(CCO)NH' }
    for i in range(len(self.spec_menu)):
      spec = self.spec_menu[i].spectrum()
      if spec == None: continue
      pine_name = apes2pine[apes_spec_names[i]]
      ipine_params.append([pine_name, spec])

    # TOCSY??
    for i in range(len(self.spec_menu2)):
      spec = self.spec_menu2[i].spectrum()
      if spec == None: continue
      nuc_list = sorted([spec.nuclei[0][-1], spec.nuclei[1][-1], spec.nuclei[2][-1]])
      nucs = nuc_list[0]+nuc_list[1]+nuc_list[2]
      if nucs == 'CHH':     ipine_params.append(['HCCH-TOCSY', spec])
      elif nucs == 'CCH':   ipine_params.append(['CCH-TOCSY', spec])
      elif nucs == 'HHN':   ipine_params.append(['TOCSY-HSQC', spec])
      elif nucs == 'HNN':   ipine_params.append(['HN(CA)NNH', spec])
    
    # NOESY?? 
    for i in range(len(self.spec_menu3)):
      spec = self.spec_menu3[i].spectrum()
      if spec == None: continue
      nuc_list = sorted([spec.nuclei[0][-1], spec.nuclei[1][-1], spec.nuclei[2][-1]])
      nucs = nuc_list[0]+nuc_list[1]+nuc_list[2]
      if nucs == 'CHH':     ipine_params.append(['C13-NOESY', spec])
      elif nucs == 'HHN':   ipine_params.append(['N15-NOESY', spec])

    # LAUNCH PINE-SPARKY.2 window
    # AUTO-SETUP and RUN
    import pinenmr
    pine_diag = sputil.the_dialog(pinenmr.pine_dialog, self.session)
    pine_diag.show_window(1)
    pine_diag.auto_setup(ipine_params)


  # ---------------------------------------------------------------------------
  #
  def pick_peaks(self):
    self.seq_count = int(self.res_count.get())    
          
    spec_list = []  
    
    iNHmin = 0
    iCmin = 0
    iCAmin = 0
    iCBmin = 0
    iCXmin = 0
    iHAmin = 0
    iHBmin = 0
    iHXmin = 0
                    
    for i in range(len(apes_spec_names)):
      spec = self.spec_menu[i].spectrum()
      spec_pkg = (spec, apes_specs[i], apes_peak_count[i], apes_layout[i], apes_layout[i], [], [])
      spec_list.append( spec_pkg )  # 5, 6 peak list
      if spec != None: 
        if i != 10:  iNHmin = iNHmin + 1
        if (i == 1) or (i == 2): iCmin = iCmin + 1
        if (i == 3) or (i == 5): iCAmin = iCAmin + 1
        if (i == 4) or (i == 6): iCAmin = iCAmin + 2        
        if (i == 5) or (i == 7): iCBmin = iCBmin + 1
        if (i == 6) or (i == 8) or (i == 9): iCBmin = iCBmin + 2        
        if (i == 11): iCXmin = iCXmin + 1
        if (i == 12): iHAmin = iHAmin + 1
        if (i == 13): iHXmin = iHXmin + 1
        
        iNHmin = min(3, iNHmin)
        iCmin = min(1, iCmin)
        iCAmin = min(3, iCAmin)
        iCBmin = min(2, iCBmin)
        iCXmin = min(2, iCXmin)
        iHAmin = min(2, iHAmin)
        iHXmin = min(2, iHXmin)
                                  
        self.progress_report(spec.name)
        for peak in spec.peak_list():
          peak.selected = 0
        ######################################################    
        # initial peak picking module for spectra
        if self.pick_mode == 0:    
          (neg_pc, pos_pc) = self.find_local_maxima(spec_pkg)
          
          if self.check_contour(spec_pkg, neg_pc, pos_pc) == 0:
            if self.verbose == 1: tkMessageBox.showerror('Error', 'Please adjust contour level of %s.' % (spec.name));
            self.msg = 'Please adjust contour level of %s.' % (spec.name)
            return 0       
      self.session.command_characters("")          
    
    # return  
    # initial filter
    # shift filter first!

    for i in range(len(spec_list)):    
      spec_pkg = spec_list[i]
      if spec_pkg[0] == None: continue       
      self.progress_report(spec_pkg[0].name + ': filtering by statistics ')
      for peak in spec_pkg[0].peak_list():      
        if self.filter_shifts(peak, spec_pkg) == 0 and peak.is_assigned == 0: 
          peak.selected = 1
        else:
          peak.selected = 0
      self.session.command_characters("")
              
    # two cycle
    for i in range(0, 2):  
      # N-H validation  
      cycle = 'Cycle%d:' % (i)
      for i in range(len(spec_list)):    
        spec_pkg = spec_list[i]
        
        if spec_pkg[0] == None: continue 
        
        # No C-HSQC     
        if i == 10: continue
          
        self.progress_report(cycle+spec_pkg[0].name + ': N-H validation process ')
        
        for peak in spec_pkg[0].peak_list():
          if peak.selected == 1: continue
          iFound = 0
          
          for j in range(len(spec_list)):    
            spec_pkg2 = spec_list[j]          
            if spec_pkg2[0] == None: continue  
            
            # No C-HSQC     
            if j == 10: continue
                    
            if spec_pkg[0].name == spec_pkg2[0].name: continue  # skip same spectrum
            for peak2 in spec_pkg2[0].peak_list():   
              iSame = self.check_nh(peak, peak2)
              iFound = iFound + iSame
              
          if iFound < iNHmin-1 and peak.is_assigned == 0:
            peak.selected = 1
            peak.color = 'yellow'
          else:
            peak.selected = 0
        self.session.command_characters("")
      # CA, CB validation
      for i in range(len(spec_list)):
        spec_pkg = spec_list[i]
        if spec_pkg[0] == None: continue
        if spec_pkg[0].dimension == 2: continue
        #if (spec_pkg[3] < 3) and (spec_pkg[3] > 8): continue
        if (i < 3) or (i > 9): continue
        self.progress_report(cycle+spec_pkg[0].name + ': CACB validation process ')
        for peak in spec_pkg[0].peak_list():
          if peak.selected == 1: continue
          iFound = 0
          #for spec_pkg2 in spec_list:
          for j in range(len(spec_list)):
            spec_pkg2 = spec_list[j]
            if spec_pkg2[0] == None: continue
            if spec_pkg2[0].dimension == 2: continue
            #if spec_pkg2[3] < 3: continue                    
            if (j < 3) or (j > 9): continue                    
            for peak2 in spec_pkg2[0].peak_list():   
              if peak == peak2: continue
              (iSame, freq) = self.check_cacb(peak, peak2)
              iFound = iFound + iSame
          
          if freq > 48 and freq < 67:
            iMin = iCAmin
          elif freq > 43:
            iMin = iCAmin-1 # GLY  
          else:
            iMin = iCBmin    
          if iFound < iMin-1 and peak.is_assigned == 0:
            peak.selected = 1
            peak.color = 'yellow'            
          else:
            peak.selected = 0    
        self.session.command_characters("")                
      # CO validation
      for i in range(len(spec_list)):    
        spec_pkg = spec_list[i]
        if spec_pkg[0] == None: continue      
        if spec_pkg[0].dimension == 2: continue
        if i > 2: continue        
        self.progress_report(cycle+spec_pkg[0].name + ': CO validation process ')
        for peak in spec_pkg[0].peak_list():
          if peak.selected == 1: continue
          iFound = 0
          for j in range(len(spec_list)):  
            spec_pkg2 = spec_list[j]          
            if spec_pkg2[0] == None: continue        
            if spec_pkg2[0].dimension == 2: continue         
            if j > 2: continue            
            for peak2 in spec_pkg2[0].peak_list():   
              if peak == peak2: continue
              (iSame, freq) = self.check_co(peak, peak2)
              iFound = iFound + iSame
          
          if freq > 145:
            iMin = iCmin
          if iFound < iMin and peak.is_assigned == 0:
            peak.selected = 1
            peak.color = 'yellow'            
          else:
            peak.selected = 0  
        self.session.command_characters("")                    
      # Sidechain validation
      chsqc_spec = None
      cconh_spec = None
      hbhaconh_spec = None
      hcconh_spec = None
      for i in range(len(spec_list)):    
        spec_pkg = spec_list[i]
        if spec_pkg[0] == None: continue      
        if i == 10: chsqc_spec = spec_pkg[0]
        elif i == 11: cconh_spec = spec_pkg[0]
        elif i == 12: hbhaconh_spec = spec_pkg[0]
        elif i == 13: hcconh_spec = spec_pkg[0]                        
              
      if chsqc_spec != None:
        if (cconh_spec != None) and (hcconh_spec != None):
          # check cconh
          self.progress_report(cycle+': CX validation process ')                  
          for peak in cconh_spec.peak_list():
            if peak.selected == 1: continue
            iFound = 0
            for peak2 in hcconh_spec.peak_list():
              if peak2.selected == 1: continue
              iFound = self.check_ch(peak, peak2, chsqc_spec)
              if iFound != 0: break
            if iFound == 0: 
              peak.is_selected = 1 
              peak.color = 'yellow'                
          self.session.command_characters("")                              
          # check hcconh
          self.progress_report(cycle+': HX validation process ')                  
          for peak in hcconh_spec.peak_list():
            if peak.selected == 1: continue
            iFound = 0
            for peak2 in cconh_spec.peak_list():
              if peak2.selected == 1: continue
              iFound = self.check_ch(peak2, peak, chsqc_spec)
              if iFound != 0: break
            if iFound == 0: 
              peak.is_selected = 1
        self.session.command_characters("")                      
        # check hbhaconh              
        self.progress_report(cycle+': HAHB validation process ')                          
        if (hbhaconh_spec != None) and (hcconh_spec != None):
          for peak in hbhaconh_spec.peak_list():
            if peak.selected == 1: continue
            iFound = 0                
            for peak2 in hcconh_spec.peak_list():
              if peak2.selected == 1: continue
              iFound = self.check_hbhaconh(peak, peak2)
              if iFound != 0: break
            if iFound == 0: 
              peak.is_selected = 1
              peak.color = 'yellow'
        self.session.command_characters("")                                    
        # c-hsqc
        self.progress_report(cycle+': C-HSQC validation process ')
        cconh_peaks = []
        hcconh_peaks = []
        for j in range(13):
          cconh_peaks.append([])
          hcconh_peaks.append([])
        if (cconh_spec != None) and (hcconh_spec != None):
          # cconh
          for peak in cconh_spec.peak_list():
            if (peak.frequency[0] > 10) and (peak.frequency[0] < 80):
              iIdx = int(peak.frequency[0] / 10.0)
              cconh_peaks[iIdx].append(peak)
            elif (peak.frequency[1] > 10) and (peak.frequency[1] < 80):
              iIdx = int(peak.frequency[1] / 10.0)
              cconh_peaks[iIdx].append(peak)
            elif (peak.frequency[2] > 10) and (peak.frequency[2] < 80):
              iIdx = int(peak.frequency[2] / 10.0)
              cconh_peaks[iIdx].append(peak)                        
          # hcconh    
          for peak in hcconh_spec.peak_list():
            if (peak.frequency[0] > -2) and (peak.frequency[0] < 8):
              iIdx = int((peak.frequency[0]+2.0))
              hcconh_peaks[iIdx].append(peak)
            elif (peak.frequency[1] > -2) and (peak.frequency[1] < 8):
              iIdx = int((peak.frequency[1]+2.0))
              hcconh_peaks[iIdx].append(peak)
            elif (peak.frequency[2] > -2) and (peak.frequency[2] < 8):
              iIdx = int((peak.frequency[2]+2.0))
              hcconh_peaks[iIdx].append(peak)
                            
        for peak in chsqc_spec.peak_list():
          iFound = 0
          if (cconh_spec != None) and (hcconh_spec != None):
            if peak.frequency[0] > 10:
              iIdx = int(peak.frequency[0] / 10.0)
              iIdx2 = int((peak.frequency[1]+2.0))              
              cconh_peaklist = cconh_peaks[iIdx]
              hcconh_peaklist = hcconh_peaks[iIdx2]
            elif peak.frequency[1] > 10:
              iIdx = int(peak.frequency[1] / 10.0)
              iIdx2 = int((peak.frequency[0]+2.0))                            
              cconh_peaklist = cconh_peaks[iIdx]
              hcconh_peaklist = hcconh_peaks[iIdx2]
                            
            for peak2 in cconh_peaklist:              
              if peak2.selected == 1: continue          
              for peak3 in hcconh_peaklist:
                if peak3.selected == 1: continue          
                iFound = self.check_ch2(peak2, peak3, peak)
                if iFound != 0: break
              if iFound != 0: break
            if iFound == 0 and peak.is_assigned == 0:
              peak.is_selected = 1
              peak.color = 'yellow'              
        self.session.command_characters("")                                                        
    # cut by minimum numbers
    for spec_pkg in spec_list:
      if spec_pkg[0] == None: continue        
      
      expected_neg_count = int(spec_pkg[2][0] * self.seq_count)
      expected_pos_count = int(spec_pkg[2][1] * self.seq_count)
      
      iMaxPosPeakCount = expected_pos_count + int(0.2 * expected_pos_count)
      iMaxNegPeakCount = expected_neg_count + int(0.2 * expected_neg_count)
      
      # negative peaks
      peaklist = sort_peaks_by_height(spec_pkg[0].peak_list(), self)      
      if expected_neg_count != 0:
        neg_peaklist = 0
        for peak in spec_pkg[0].peak_list():
          if peak.data_height == None: continue
          if peak.selected == 1: continue
          if (neg_peaklist > iMaxNegPeakCount) and (peak.data_height < 0) and peak.is_assigned == 0:
            peak.selected = 1
          elif peak.data_height < 0:
            neg_peaklist = neg_peaklist + 1
      if expected_pos_count != 0:
        pos_peaklist = 0
        rev_peaklist = reversed(peaklist)
        for peak in rev_peaklist:
          if peak.selected == 1: continue
          if (peak.data_height > 0) and (pos_peaklist > iMaxPosPeakCount) and peak.is_assigned == 0:
            peak.selected = 1
            peak.color = 'yellow'            
          elif peak.data_height > 0:
            pos_peaklist = pos_peaklist + 1
      self.session.command_characters("")
    self.progress_report('APES finished. Please validate the results.')      
    self.msg = 'Succeeded: APES peak picking finished. Please validate the results.'
    return 1
  # ---------------------------------------------------------------------------
  #      
  def check_nh(self, peak, peak2):
    n_cs = n2_cs = 9999 
    h_cs = h2_cs = 9999
    for freq in peak.frequency:
      if freq > 95 and freq < 140:
        n_cs = freq
      elif freq > 6 and freq < 15:
        h_cs = freq
    if (n_cs > 1000) or (h_cs > 1000):
      return 0
    for freq in peak2.frequency:
      if freq > 95 and freq < 140:
        n2_cs = freq
      elif freq > 6 and freq < 15:
        h2_cs = freq        
    if (n2_cs > 1000) or (h2_cs > 1000):
      return 0
    if abs(n_cs - n2_cs) < self.nppm and abs(h_cs - h2_cs) < self.hppm:
      return 1
    return 0    
  # ---------------------------------------------------------------------------
  #      
  def check_ch(self, peak, peak2, spec):
    cx_cs = n_cs = h_cs = 9999 
    hx_cs = n2_cs = h2_cs = 9999 
    
    for freq in peak.frequency:
      if freq > 15 and freq < 80:
        cx_cs = freq
      elif freq > 90:  
        n_cs = freq      
      elif freq > 7:
        h_cs = freq
                    
    if (cx_cs > 1000) or (n_cs > 1000) or (h_cs > 1000):      return 0
    
    for freq in peak2.frequency:
      if freq < 7:
        hx_cs = freq
      elif freq > 90:  
        n2_cs = freq      
      elif freq > 7:
        h2_cs = freq    
        
        
    if (hx_cs > 1000) or (n2_cs > 1000) or (h2_cs > 1000):      return 0    
    
    if abs(n_cs - n2_cs) > self.nppm or abs(h_cs - h2_cs) > self.hppm:
      return 0

    for peak3 in spec.peak_list():
      if (abs(peak3.frequency[0] - cx_cs) < self.cppm and abs(peak3.frequency[1] - hx_cs) < self.hppm) or (abs(peak3.frequency[1] - cx_cs) < self.cppm and abs(peak3.frequency[0] - hx_cs) < self.hppm):
        return 1
      
    return 0    
  # ---------------------------------------------------------------------------
  #      
  def check_ch2(self, peak, peak2, peak3):
    cx_cs = n_cs = h_cs = 9999 
    hx_cs = n2_cs = h2_cs = 9999 
    
    for freq in peak.frequency:
      if freq > 15 and freq < 80:
        cx_cs = freq
      elif freq > 90:  
        n_cs = freq      
      elif freq > 7:
        h_cs = freq
    if (cx_cs > 1000) or (n_cs > 1000) or (h_cs > 1000):      return 0
    
    for freq in peak2.frequency:
      if freq < 7:
        hx_cs = freq
      elif freq > 90:  
        n2_cs = freq      
      elif freq > 7:
        h2_cs = freq    
        
    if (hx_cs > 1000) or (n2_cs > 1000) or (h2_cs > 1000):      return 0    
    
    # from same n-h
    if abs(n_cs - n2_cs) > self.nppm or abs(h_cs - h2_cs) > self.hppm:
      return 0

    # 
    if (abs(peak3.frequency[0] - cx_cs) < self.cppm and abs(peak3.frequency[1] - hx_cs) < self.hppm) or (abs(peak3.frequency[1] - cx_cs) < self.cppm and abs(peak3.frequency[0] - hx_cs) < self.hppm):
      return 1
      
    return 0            
  # ---------------------------------------------------------------------------
  #      
  def check_hbhaconh(self, peak, peak2):
    hx_cs = n_cs = h_cs = 9999 
    hx2_cs = n2_cs = h2_cs = 9999 

    for freq in peak.frequency:
      if freq < 7:
        hx_cs = freq
      elif freq > 90:  
        n_cs = freq      
      elif freq > 7:
        h_cs = freq    
        
    if (hx_cs > 1000) or (n_cs > 1000) or (h_cs > 1000):      return 0    
    
    for freq in peak2.frequency:
      if freq < 7:
        hx2_cs = freq
      elif freq > 90:  
        n2_cs = freq      
      elif freq > 7:
        h2_cs = freq    
        
    if (hx2_cs > 1000) or (n2_cs > 1000) or (h2_cs > 1000):      return 0    
    
    if abs(n_cs - n2_cs) > self.nppm or abs(h_cs - h2_cs) > self.hppm:
      return 0

    if abs(hx_cs - hx2_cs) < self.hppm:
      return 1
     
    return 0            
    
  # ---------------------------------------------------------------------------
  #      
  def check_cacb(self, peak, peak2):
    cacb_cs = cacb2_cs = 9999 
    for freq in peak.frequency:
      if freq > 15 and freq < 85:
        cacb_cs = freq
    for freq in peak2.frequency:
      if freq > 15 and freq < 85:
        cacb2_cs = freq      
        
    if (cacb_cs > 1000) or (cacb2_cs > 1000):
      return (0, cacb_cs)
    
    if abs(cacb_cs - cacb2_cs) < self.cppm:
      return (1, cacb_cs)
    return (0, cacb_cs)
  # ---------------------------------------------------------------------------
  #      
  def check_co(self, peak, peak2):
    co_cs = co2_cs = 9999 
    for freq in peak.frequency:
      if freq > 163 and freq < 190:
        co_cs = freq
    for freq in peak2.frequency:
      if freq > 163 and freq < 190:
        co2_cs = freq
        
    if (co_cs > 1000) or (co2_cs > 1000):
      return (0, co_cs)          
    
    if abs(co_cs - co2_cs) < self.cppm:
      return (1, co_cs)
    return (0, co_cs)    
  # ---------------------------------------------------------------------------
  #      
  def find_freq(self, peak, c_shift):
    if c_shift > 15: tol = self.cppm
    else: tol = self.hppm
    for freq in peak.frequency:
      if abs(freq - c_shift) < tol:
        return 1
    return 0
   
  # ---------------------------------------------------------------------------
  #  
  def check_contour(self, spec_instance, neg_pc, pos_pc):
    expected_neg_count = spec_instance[2][0] * self.seq_count
    expected_pos_count = spec_instance[2][1] * self.seq_count
    iMinPosPeakCount = expected_pos_count + int(0.2 * expected_pos_count)
    iMaxPosPeakCount = expected_pos_count + int(0.5 * expected_pos_count)
    iMinNegPeakCount = expected_neg_count + int(0.2 * expected_neg_count)
    iMaxNegPeakCount = expected_neg_count + int(0.5 * expected_pos_count)
    if iMinPosPeakCount != 0: 
      if pos_pc < iMinPosPeakCount:
        if self.verbose == 1: tkMessageBox.showinfo('error','p min %d,%d' % (pos_pc, iMinPosPeakCount))
        return 0
    
    if iMinNegPeakCount != 0: 
      if neg_pc < iMinNegPeakCount:
        if self.verbose == 1: tkMessageBox.showinfo('error','n min %d,%d: Please lower negative contour threshold.' % (neg_pc, iMinNegPeakCount))      
        else:                 self.msg = 'n min %d,%d: Please lower negative contour threshold.' % (neg_pc, iMinNegPeakCount)
        return 0
    
    peaklist = sort_peaks_by_height(spec_instance[0].peak_list(), self)    

    for i in range(int(iMaxNegPeakCount), len(peaklist)):
      peak = peaklist[i]    
      if peak.data_height > 0: continue
      if peak.is_assigned == 0:
        peak.selected = 1
      peak.color = 'yellow'      
      
    peaklist.reverse()
    
    for i in range(int(iMaxPosPeakCount),  len(peaklist)):
      peak = peaklist[i]
      if peak.data_height < 0: continue
      if peak.is_assigned == 0:
        peak.selected = 1
      peak.color = 'yellow'      

        
    return 1
  # ---------------------------------------------------------------------------
  #    
  def find_local_maxima(self, spec_instance):
    spec = spec_instance[0]
    if spec == None:      return (0,0)
    view = self.get_view(spec)
    if view == None:      return (0,0)
    expected_neg_count = int(spec_instance[2][0] * self.seq_count)
    expected_pos_count = int(spec_instance[2][1] * self.seq_count)
    iMinPosPeakCount = expected_pos_count + int(0.20 * expected_pos_count)
    iMinNegPeakCount = expected_neg_count + int(0.20 * expected_neg_count)
    
    min_lw = spec.pick_minimum_linewidth
    min_dr = spec.pick_minimum_drop_factor
            
    neg_lowest = view.negative_levels.lowest
    pos_lowest = view.positive_levels.lowest
    
    if expected_neg_count == 0:   neg_lowest = -9999999999
    if expected_pos_count == 0:   pos_lowest = 9999999999
    
    # negative peaks
    self.progress_report(spec.name + ' local maxima' ) 
    neg_pc = 0
    pos_pc = 0

    for i in range(5):
      height_thresholds = (neg_lowest, pos_lowest)
      self.progress_report(spec.name + (' local maxima: %d / %d trial' % (i+1, 5))  )
      spec.pick_peaks(spec.region, height_thresholds, min_lw, min_dr)   
      neg_pc = 0
      pos_pc = 0
      for peak in spec.peak_list():
        if peak.data_height > 0: pos_pc = pos_pc + 1
        else: neg_pc = neg_pc + 1
      if neg_pc < iMinNegPeakCount:
        neg_lowest = neg_lowest * 0.8
      if pos_pc < iMinPosPeakCount:
        pos_lowest = pos_lowest * 0.8
      if pos_pc >= iMinPosPeakCount and neg_pc >= iMinNegPeakCount:
        break

    return (neg_pc, pos_pc)
  # -----------------------------------------------------------------------------
  # This is for TOCSY, COSY, NOESY
  def auto_restrict_picking(self, tc_spec, hs_spec, exp_type):
    if tc_spec == None: 
      self.msg = 'no tocsy, cosy or noesy spectrum'
      return self.msg
    if hs_spec == None: 
      self.msg = 'no hsqc spectrum'
      return self.msg
    if tc_spec.dimension != 3:
      self.msg = '%s is not 3D spectrum' % (tc_spec.name)
      return self.msg
    if hs_spec.dimension != 2:
      self.msg = '%s is not 2D spectrum' % (hs_spec.name)
      return self.msg
    
    
    session = self.session
    #  tol_list:  H N C
    tols = [0, 0, 0]
    for i in range(len(tc_spec.nuclei)):
      if    tc_spec.nuclei[i][-1] == 'H': tols[i] = self.hppm
      elif  tc_spec.nuclei[i][-1] == 'N': tols[i] = self.nppm
      elif  tc_spec.nuclei[i][-1] == 'C': tols[i] = self.cppm
    
    # CCH or CHH, HNN or HHN
    temp_list = []
    tc_spec_type = ''
    hs_spec_type = ''
    
    for i in range(len(tc_spec.nuclei)):
      temp_list.append(tc_spec.nuclei[i][-1])
    sort_list = sorted(temp_list) # HCH(?) -> CHH or HNH(?) -> HHN
    tc_spec_type = temp_list[0]+temp_list[1]+temp_list[2]  
    tc_spec_type2 = sort_list[0]+sort_list[1]+sort_list[2]
    
    
    temp_list = []
    for i in range(len(hs_spec.nuclei)):
      temp_list.append(hs_spec.nuclei[i][-1])
    sort_list = sorted(temp_list) # HC(?) -> CH or NH(?) -> HN
    hs_spec_type = temp_list[0]+temp_list[1]  
    hs_spec_type2 = sort_list[0]+sort_list[1]
    
    
    try:
      idx = ['CCH','CHH','HNN','HHN'].index(tc_spec_type2)
    except:
      self.msg = 'no tocsy, cosy or noesy spectrum'
      return self.msg

    try:
      idx = ['CH','HN'].index(hs_spec_type2)
    except:
      self.msg = 'no hsqc spectrum'  
      return self.msg
    
    if tc_spec_type2.find(hs_spec_type2) == -1:
      self.msg = 'given two spectra are not comparable.'
      return self.msg

    tc_view = self.get_view(tc_spec)
    neg_lowest = tc_view.negative_levels.lowest
    pos_lowest = tc_view.positive_levels.lowest
    height_thresholds = (neg_lowest, pos_lowest)
    min_lw = tc_spec.pick_minimum_linewidth
    min_dr = tc_spec.pick_minimum_drop_factor
    region = tc_spec.region

    # match axis- what is the free dimension?
    # this will be smaller point H for NOESY and larger for TOCSY & COSY
    iFreeDim = -1
    if exp_type == 'noesy':     iFreeSize = 100000000
    else:                       iFreeSize = -100000000


    for i in range(len(tc_spec.data_size)):
      if tc_spec.nuclei[i][-1] != 'H': continue
      if (tc_spec.data_size[i] < iFreeSize and exp_type == 'noesy') or \
          (tc_spec.data_size[i] > iFreeSize and exp_type != 'noesy' and \
          (tc_spec_type2 == 'CHH' or tc_spec_type2 == 'HHN')):
        iFreeDim = i
        iFreeSize = tc_spec.data_size[i]

    # CCH ?????
    
    region_list = []
    dim_match = [-1, -1, -1]
    for i in range(len(tc_spec.nuclei)):
      dim_match[i] = list(hs_spec.nuclei).index(tc_spec.nuclei[i])
    
    # make region list  
    for peak in hs_spec.peak_list():
      rmin = list(region[0]) # rmin and rmax are from root peak
      rmax = list(region[1])
      if (tc_spec_type2 == 'CHH' or tc_spec_type2 == 'HHN'):
        for i in range(len(tc_spec.nuclei)):
          if i == iFreeDim: continue
          rmin[i] = peak.frequency[dim_match[i]] - tols[i]
          rmax[i] = peak.frequency[dim_match[i]] + tols[i]
        region_list.append((tuple(rmin), tuple(rmax))) # tolerance added from
      else: # CCH or NNH- we make two kinds.
        rmin2 = list(rmin) # copy of root peaks (rmin, rmax)
        rmax2 = list(rmax)
        iFirst = 1
        for i in range(len(tc_spec.nuclei)):
          if tc_spec.nuclei[i] == '13C' or tc_spec.nuclei[i] == '15N': # heavy atom
            if iFirst == 1: # 1
              rmin[i] = peak.frequency[dim_match[i]] - tols[i]
              rmax[i] = peak.frequency[dim_match[i]] + tols[i]
              iFirst = 0
            else:   # 2
              rmin2[i] = peak.frequency[dim_match[i]] - tols[i]
              rmax2[i] = peak.frequency[dim_match[i]] + tols[i]
          else: # proton
            rmin[i] = peak.frequency[dim_match[i]] - tols[i]
            rmax[i] = peak.frequency[dim_match[i]] + tols[i]
            rmin2[i] = peak.frequency[dim_match[i]] - tols[i]
            rmax2[i] = peak.frequency[dim_match[i]] + tols[i]
        region_list.append((tuple(rmin), tuple(rmax)))
        region_list.append((tuple(rmin2), tuple(rmax2)))

    # picking
    for i in range(len(region_list)):
      reg = region_list[i]
      self.progress_report(tc_spec.name + (' local maxima: %d / %d' % (i+1, len(region_list)))  )
      tc_spec.pick_peaks(reg, height_thresholds, min_lw, min_dr)

    # filter
    pos_num = 0
    neg_num = 0
    for peak in tc_spec.peak_list():
      if self.filter_shift(self.seq_filter, peak.frequency[iFreeDim]) == 0 and peak.is_assigned == 0:
        peak.selected = 1
      else:
        peak.selected = 0
      if peak.data_height > 0: pos_num = pos_num + 1  
      else: neg_num = neg_num + 1
    for peak in tc_spec.peak_list():  
      if    pos_num > neg_num and peak.data_height < 0 and peak.is_assigned == 0: peak.selected = 1
      elif  pos_num < neg_num and peak.data_height > 0 and peak.is_assigned == 0: peak.selected = 1

    # select to delete if not assigned
    min_num = len(hs_spec.peak_list())*2.5
    if exp_type == 'noesy':
        min_num = len(hs_spec.peak_list()) * 18
    else:
        min_num = len(hs_spec.peak_list()) * 5
    peaklist = sort_peaks_by_height(tc_spec.peak_list(), self)
    for i in range(min_num, len(peaklist)):
      peak = peaklist[i]
      if peak.is_assigned == 0:
        peak.selected = 1
      peak.color = 'yellow'
      
    session.command_characters("")
    return 'Succeeded.'
  # ---------------------------------------------------------------------------
  #
  def get_view(self, spectrum):
    for view in self.session.project.view_list():
      if view.spectrum == spectrum:
        return view
    return None

# -----------------------------------------------------------------------------
#
def sort_peaks_by_height(peaks, stoppable):
  return tkutil.stoppable_sort_by_key(peaks, height_sort_key, stoppable)

# -----------------------------------------------------------------------------
# Return assignment as ((residue #, residue symbol, atom name), ...)
# for sorting.
#
def height_sort_key(peak):
  a = []
  a.append(peak.data_height)
      
  return tuple(a)    
    
# ----------------------------------------------------------------------------
# Create an option menu listing spectra in the current project.
#
class apes_menu(tkutil.option_menu):

  def __init__(self, session, parent, label, allow_no_choice = 1):

    self.session = session
    self.allow_no_choice = allow_no_choice
    self.names = self.spectrum_names()
    tkutil.option_menu.__init__(self, parent, label,
                                self.names, '')
    self.menu['postcommand'] = self.update_menu_cb

  # --------------------------------------------------------------------------
  #
  def spectrum_names(self):

    spectra = self.session.project.spectrum_list()
    names = pyutil.attribute_values(spectra, 'name')
    if self.allow_no_choice:
      names = ('',) + names
    return names

  # --------------------------------------------------------------------------
  #
  def default_spectrum_name(self):

    return pyutil.attribute(self.session.selected_spectrum(), 'name', '')

  # --------------------------------------------------------------------------
  #
  def update_menu_cb(self):

    current_names = self.spectrum_names()
    if current_names != self.names:
      self.names = current_names
      self.remove_all_entries()
      for name in self.names:
        self.add_entry(name)
      if not self.get() in self.names:
        self.set(self.default_spectrum_name())

  # --------------------------------------------------------------------------
  #
  def spectrum(self):
    return name_to_spectrum(self.get(), self.session)

# ----------------------------------------------------------------------------
#
def name_to_spectrum(name, session):

  slist = session.project.spectrum_list()
  for s in slist:
    if s.name == name:
      return s
  return None  

# -----------------------------------------------------------------------------
#
def show_ssapes(session):
  sputil.the_dialog(ssapes_pick_dialog,session).show_window(1)
