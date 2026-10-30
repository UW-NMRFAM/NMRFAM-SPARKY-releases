# -----------------------------------------------------------------------------
# Transferation of Assignments to spectrum
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: December 4, 2019
# 
# Install:
#   Add the following line in the assignment_menu part of sparky_site.py
#       ('ta', 'Transfer assignments to spectrum', ('tan','TAN')),
#
# Usage:
#   type "ta" command or select from extension menu
# 
#
#
#
# This module is the key of "predict-and-confirm" method.
#
#
# Oct 11, 2017: Added sidechain peak supports in N-HSQC and N-NOESY
# Sep 12, 2018: Added aromatic sidechains
# Nov 19, 2018: Added 2D-CBHE
#
# -----------------------------------------------------------------------------
import math
import string
import types
import Tkinter

import atoms
import atomnames
import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox
import pinelayout
import pacsylayout
import talos
import pecan
import pacsysimulate
import pinegraph
import tkFileDialog
import shiftx2
import myseq

arom_singlea = "HFWY"
arom_dict = {
  "H":(["CD2", "HD2"], ["CE1", "HE1"]),
  "F":(["CD1", "HD1"], ["CD2", "HD2"], ["CE1", "HE1"], ["CE2", "HE2"], 
       ["CZ", "HZ"]),
  "W":(["CD1", "HD1"], ["CE3", "HE3"], ["CH2", "HH2"], 
       ["CZ2", "HZ2"], ["CZ3", "HZ3"]),
  "Y":(["CD1", "HD1"], ["CD2", "HD2"], ["CE1", "HE1"], ["CE2", "HE2"])}

# -----------------------------------------------------------------------------    
# group class
class WGroup:
  name = '0'    # T12
  symbol = ''   # T
  number = 0    # 12
  def __init__(self, szSymbol, iNumber):
    self.name = '%s%d' % (szSymbol, iNumber)
    self.symbol = szSymbol
    self.number = iNumber
# -----------------------------------------------------------------------------    
# from assignment. including pseudoatoms.
def GetFreq2(session, szGroup, szAtom):
  for condition in session.project.condition_list():
    resonance = condition.find_resonance(szGroup, szAtom)
    if resonance <> None:
      if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
        return 9999, 9999
      return resonance.frequency, resonance.deviation
    else:
      # HN
      if szAtom == 'H':
        resonance = condition.find_resonance(szGroup, 'HN')
        if resonance <> None:
          if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
            return 9999, 9999
          return resonance.frequency, resonance.deviation
  return 9999, 9999        
# -----------------------------------------------------------------------------    
# from assignment. including pseudoatoms.
def GetFreq(session, group, szAtom):
    if group == None:
      return 9999, 9999
    selected_group = []
    selected_group.append(group.symbol)
    selected_group.append(group.number)
    for condition in session.project.condition_list():
        group_name = '%s%d' % (selected_group[0], selected_group[1])
        resonance = condition.find_resonance(group_name, szAtom)
        if resonance <> None:
            if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                return 9999, 9999
            return resonance.frequency, resonance.deviation
        else:
            # HN
            if szAtom == 'H':
                resonance = condition.find_resonance(group_name, 'HN')
                if resonance <> None:
                    if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                        return 9999, 9999
                    return resonance.frequency, resonance.deviation
            # processing pseudo atoms
            if pinelayout.pseudo_layout.has_key(selected_group[0]) and \
                  szAtom[:1] == 'H' and len(szAtom) > 1 and szAtom != 'HN':
                layout = pinelayout.pseudo_layout[selected_group[0]]
                szAtom2 = ('Q%s' % szAtom[1:len(szAtom)])
                resonance = condition.find_resonance(group_name, szAtom2)                
                if resonance <> None:
                    if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                        return 9999, 9999  
                    return resonance.frequency, resonance.deviation
            # processing meta atoms
            if szAtom[:1] == 'H' and len(szAtom) > 1 and szAtom != 'HN':
                szAtom2 = ('M%s' % szAtom[1:len(szAtom)])
                resonance = condition.find_resonance(group_name, szAtom2)                
                if resonance <> None:
                    if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                        return 9999, 9999
                    return resonance.frequency, resonance.deviation
            # processing sub-level methyl atoms
            if szAtom[:1] == 'H'and len(szAtom) > 1 and szAtom != 'HN':
              # try to add numbers.        
              for i in range(3):
                szAtom2 = '%s%d' % (szAtom, i+1)
                resonance = condition.find_resonance(group_name, szAtom2)
                if resonance <> None:
                    if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                        return 9999, 9999
                    return resonance.frequency, resonance.deviation
    return 9999, 9999
# -----------------------------------------------------------------------------    
# from assignment. including pseudoatoms and giving atom
def GetFreq3(session, group, szAtom):
  if group == None:
    return 9999, 9999, ''
  selected_group = []
  selected_group.append(group.symbol)
  selected_group.append(group.number)
  for condition in session.project.condition_list():
    group_name = '%s%d' % (selected_group[0], selected_group[1])
    resonance = condition.find_resonance(group_name, szAtom)
    if resonance <> None:
      if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
        return 9999, 9999, ''
      return resonance.frequency, resonance.deviation, szAtom
    else:
      # HN
      if szAtom == 'H':
        resonance = condition.find_resonance(group_name, 'HN')
        if resonance <> None:
          if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
            return 9999, 9999, ''
          return resonance.frequency, resonance.deviation, 'HN'
              
      # processing pseudo atoms
      if szAtom[:1] == 'C':
        for tr in [0, 1]:
          if  len(szAtom) > 1+tr:
            for prefix in ['C','CQ']:
              szAtom2 = prefix + szAtom[1:len(szAtom)-tr]
              resonance = condition.find_resonance(group_name, szAtom2)
              if resonance <> None:
                if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                  return 9999, 9999, ''
                return resonance.frequency, resonance.deviation, szAtom2
            
      if szAtom[:1] == 'H' and szAtom != 'HN':
        for tr in [0, 1]:
          if len(szAtom) > 1+tr:
            for prefix in ['H','Q','M']:
              szAtom2 = prefix + szAtom[1:len(szAtom)-tr]
              resonance = condition.find_resonance(group_name, szAtom2)
              if resonance <> None:
                if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                  return 9999, 9999, ''
                return resonance.frequency, resonance.deviation, szAtom2
    
      # processing sub-level methyl atoms
      if szAtom[:1] == 'H'and len(szAtom) > 1 and szAtom != 'HN':
        # try to add numbers.        
        for i in range(3):
          szAtom2 = '%s%d' % (szAtom, i+1)
          resonance = condition.find_resonance(group_name, szAtom2)
          if resonance <> None:
            if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
              return 9999, 9999, ''
            return resonance.frequency, resonance.deviation, szAtom2
    return 9999, 9999, ''
# -----------------------------------------------------------------------------    
# from assignment. exact same nomenclature required.
def GetExactFreq(session, group, szAtom):
    if group == None:
      return 9999, 9999
    selected_group = []
    selected_group.append(group.symbol)
    selected_group.append(group.number)
    for condition in session.project.condition_list():
        group_name = '%s%d' % (selected_group[0], selected_group[1])
        resonance = condition.find_resonance(group_name, szAtom)
        if resonance <> None:
            if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                return 9999, 9999
            return resonance.frequency, resonance.deviation
    return 9999, 9999    
# -----------------------------------------------------------------------------
# Check whether assignment for correlated pseudoatom is already assigned.
def GetPseudoPass(session, group, szAtom):
    if group == None:
      return 0

    if (szAtom[:1] != 'Q') and (szAtom[:1] != 'H') and (szAtom[:1] != 'M'):
      return 0
    if (len(szAtom) == 1) or (szAtom == 'HN'):
      return 0
    pszTag = ('Q','H','M')
    for szTag in pszTag:
      #if szTag == szAtom[:1]: continue
      szAtom2 = szTag + szAtom[1:len(szAtom)]
      [fFreq, fDev] = GetExactFreq(session, group, szAtom2)
     
      if (fFreq < 1000) and (szAtom != szAtom2):
        return 1
        
      if len(szAtom) > 2:  
        szAtom2 = szTag + szAtom[1:len(szAtom)-1]      
        [fFreq, fDev] = GetExactFreq(session, group, szAtom2)
        if fFreq < 1000:
          return 1  # pass!       
    return 0  # no pass!

# -----------------------------------------------------------------------------
#
class tan_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    self.sequences = []
    self.groups = []
    self.session = session
    self.selected_spec_type = None
    
    tkutil.Dialog.__init__(self, session.tk, 'Transfer and simulate assignments- PACSY')

    spec = sputil.spectrum_menu(session, self.top, 'Spectrum: ')
    spec.frame.pack(side = 'top', anchor = 'w')
    self.spec = spec

    # checkbutton- apply to only selected N-HSQC peaks
    self.m_applyoption = Tkinter.IntVar()
    applytype_cb = Tkinter.Checkbutton(self.top, \
                        text = 'Apply to only selected (N,C)-HSQC peaks', \
                        variable = self.m_applyoption, onvalue=1, offvalue = 0)
    applytype_cb.pack(side = 'top', anchor = 'w')
    
    self.middle_frame = Tkinter.Frame(self.top, width = 600, height = 400)
    self.middle_frame.pack(side='top', anchor='w')
    
    spec_type = pinegraph.modified_listbox(self.middle_frame, 'Type: ', 13, 20, "single")
    self.spec_type = spec_type    
    spec_type.frame.pack(side = 'left', anchor = 'w')
    spec_type.listbox.bind('<ButtonRelease-1>', self.select_spectype)    
    #spec_type = tkutil.scrolling_list(self.middle_frame, 'Type: ', 20)
    #spec_type.listbox.config(width = 13)
    #spec_type.frame.pack(side = 'left', anchor = 'w')
    #spec_type.clearself.groups

    supported_spectra = 'N-HSQC C-HSQC HNCO HN(CA)CO CBCA(CO)NH HNCACB HN(CO)CA '\
          'HNCA CB(CA)(CO)NH HN(CA)CB C(CO)NH H(CCO)NH HBHA(CO)NH '\
          'HA(CO)NH HNHA HCCH-TOCSY CCH-TOCSY TOCSY-HSQC 13C-NOESY '\
          '15N-NOESY C-HSQC(aro) CBHD(aro) CBHE(aro) CBHDHE(aro) '\
          'CBCDHD(aro) CBCEHE(aro) HCCH-TOCSY(aro) CCH-TOCSY(aro) 13C-NOESY(aro)'
    
    self.supported_spectra = supported_spectra
    supported_spectrum_list = supported_spectra.split()
    self.supported_spectrum_list = supported_spectrum_list

     # 0: i-1, 1: i-1, i, 2: 2D, 3: TOCSY type, 4: NOESY type, 5: aromatics
    spectrum_types = '2 2 0 1 0 1 0 1 0 1 0 0 0 0 1 3 3 3 4 4 5 5 5 5 5 5 5 5 5'
    self.spectrum_types = spectrum_types
    spectrum_type_list = spectrum_types.split()
    self.spectrum_type_list = spectrum_type_list 

    last_atom_types = 'HHX HX C C CACB CACB CA CA CB CB CX HX HAHB HA HA HX CX '\
                      'HHX HHX HHX HX HD HDHE HE HD HDHE HX CX HX'
    self.last_atom_types = last_atom_types
    last_atom_type_list = last_atom_types.split()
    self.last_atom_type_list = last_atom_type_list

    corr_atom_types = '0 1 0 0 0 0 0 0 0 0 '\
                      '0 0 0 0 0 1 1 0 1 0 1 1 1 1 1 1 1 1 1' # 0: N-H, 1: CX-HX
    self.corr_atom_types = corr_atom_types
    corr_atom_type_list = corr_atom_types.split()
    self.corr_atom_type_list = corr_atom_type_list

    reversed_cn_dim_types = '0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 '\
            '2 0 0 0 2 2 2 2 2 2 2 2 2' # 0: N, C > 2nd Ind, 1: N, C > 2nd. 2: x
    self.reversed_cn_dim_types = reversed_cn_dim_types
    reversed_cn_dim_type_list = reversed_cn_dim_types.split()
    self.reversed_cn_dim_type_list = reversed_cn_dim_type_list

    reversed_h_dim_types = '0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 2 '\
            '0 1 0 1 2 2 2 2 2 2 2 2 2' # 0: H < 2nd Ind, 1: H > 2nd Ind. 2: x
    self.reversed_h_dim_types = reversed_h_dim_types
    
    
    reversed_h_dim_type_list = reversed_h_dim_types.split()
    self.reversed_h_dim_type_list = reversed_h_dim_type_list


    for szSpectrum in self.supported_spectrum_list:
      self.spec_type.append(szSpectrum, szSpectrum)
    
    
    # conditions
    self.ph_list=('DO NOT APPLY','2.5','3.0','3.5','4.0','4.5',
                  '5.0','5.5','6.0','6.5','7.0','7.5','8.0','8.5',
                  '9.0','9.5','10.0','10.5','11.0','11.5','12.0')
    self.ph_list2=('DO NOT APPLY','PH_2.0_3.0','PH_2.5_3.5',
      'PH_3.0_4.0','PH_3.5_4.5','PH_4.0_5.0','PH_4.5_5.5','PH_5.0_6.0',
      'PH_5.5_6.5','PH_6.0_7.0','PH_6.5_7.5','PH_7.0_8.0','PH_7.5_8.5',
      'PH_8.0_9.0','PH_8.5_9.5','PH_9.0_10.0','PH_9.5_10.5','PH_10.0_11.0',
      'PH_10.5_11.5','PH_11.0_12.0','PH_11.5_12.0')        
    
    self.PH_om = tkutil.option_menu(self.middle_frame, "Sample pH", 
                                    self.ph_list, 'DO NOT APPLY')
    self.PH_om.frame.pack(side = 'top', anchor = 'nw')    

    self.temp_list=('DO NOT APPLY','258','263','268','273','278','283',
      '288','293','298','303','308','313','318','323','328','333',
      '338','343','348')
    self.temp_list2=('DO NOT APPLY', 'TEMP_253_263', 'TEMP_258_268',
      'TEMP_263_273', 'TEMP_268_278', 'TEMP_273_283','TEMP_278_288', 
      'TEMP_283_293', 'TEMP_288_298', 'TEMP_293_303', 'TEMP_298_308', 
      'TEMP_303_313','TEMP_308_318', 'TEMP_313_323', 'TEMP_318_328', 
      'TEMP_323_333', 'TEMP_328_338', 'TEMP_333_343','TEMP_338_348','TEMP_343_353')
    self.TEMP_om = tkutil.option_menu(self.middle_frame, "Exp. temp.", 
                                      self.temp_list, 'DO NOT APPLY')
    self.TEMP_om.frame.pack(side = 'top', anchor = 'nw')   

    self.PECAN_cb = tkutil.checkbutton(self.middle_frame, 
                                      "Use PECAN data for reference:", 0) 
    self.PECAN_cb.button.pack(side = 'top', anchor = 'w') #, anchor = 'nw')    
    self.PECAN_cb.button.bind('<ButtonRelease>', self.ApplyButtonReleaseCB)

    self.pecan_file = tkutil.file_field(self.middle_frame, '', 'Browse...')
    self.pecan_file.frame.pack(side = 'top', anchor = 'w')
            
    self.TALOS_cb = tkutil.checkbutton(self.middle_frame, 
                                      "Use TALOS data for reference:", 0) 
    self.TALOS_cb.button.pack(side = 'top', anchor = 'w') #, anchor = 'nw')    
    self.TALOS_cb.button.bind('<ButtonRelease>', self.ApplyButtonReleaseCB2)
        
    self.talos_file = tkutil.file_field(self.middle_frame, '', 'Browse...')
    self.talos_file.frame.pack(side = 'top', anchor = 'w')

    self.COND_cb = tkutil.checkbutton(self.middle_frame, 
                                      "Apply below conditions", 0)
    self.COND_cb.button.pack(side = 'top', anchor = 'w') #, anchor = 'nw')
    self.COND_cb.button.bind('<ButtonRelease>', self.ApplyButtonReleaseCB3)    
        
    self.SS_list=('DO NOT APPLY','Alpha helix','Beta strand','Turn',
                  '310 helix','Random coil','-S-S-')
    self.SS_list2=('DO NOT APPLY','SS_H','SS_E','SS_T','SS_G','SS_C','SS_B')    
    self.SS_om = tkutil.option_menu(self.middle_frame, "Sec. Struct.", 
                    self.SS_list, 'DO NOT APPLY')
    self.SS_om.frame.pack(side = 'top', anchor = 'nw')        
    
    self.TA_list = ('DO NOT APPLY','-165','-150','-135','-120','-105',
                    '-90','-75','-60','-45','-30','-15','0','15','30',
                    '45','60','75','90','105','120','135','150','165')
    self.TA_list2 = ('DO NOT APPLY', 'PHI_-180_-150', 'PHI_-165_-135', 
                    'PHI_-150_-120', 'PHI_-135_-105', 'PHI_-120_-90', 
                    'PHI_-105_-75', 'PHI_-90_-60', 'PHI_-75_-45', 
                    'PHI_-60_-30', 'PHI_-45_-15', 'PHI_-30_0', 
                    'PHI_-15_15', 'PHI_0_30', 'PHI_15_45', 'PHI_30_60', 
                    'PHI_45_75', 'PHI_60_90', 'PHI_75_105', 'PHI_90_120', 
                    'PHI_105_135', 'PHI_120_150', 'PHI_135_165', 'PHI_150_180')    
    self.TA_list3 = ('DO NOT APPLY', 'PSI_-180_-150', 'PSI_-165_-135', 
                    'PSI_-150_-120', 'PSI_-135_-105', 'PSI_-120_-90', 
                    'PSI_-105_-75', 'PSI_-90_-60', 'PSI_-75_-45', 
                    'PSI_-60_-30', 'PSI_-45_-15', 'PSI_-30_0', 'PSI_-15_15', 
                    'PSI_0_30', 'PSI_15_45', 'PSI_30_60', 'PSI_45_75', 
                    'PSI_60_90', 'PSI_75_105', 'PSI_90_120', 'PSI_105_135', 
                    'PSI_120_150', 'PSI_135_165', 'PSI_150_180')            
    
    self.PHI_om = tkutil.option_menu(self.middle_frame, "PHI degree", 
                                      self.TA_list, 'DO NOT APPLY')    
    self.PHI_om.frame.pack(side = 'top', anchor = 'nw')                
        
    self.PSI_om = tkutil.option_menu(self.middle_frame, "PSI degree", 
                                      self.TA_list, 'DO NOT APPLY')        
    self.PSI_om.frame.pack(side = 'top', anchor = 'nw')                
                
    self.core_list = ('DO NOT APPLY','Buried', 'Medium', 'Exposed')
    self.core_list2 = ('DO NOT APPLY','CORE_B', 'CORE_M', 'CORE_E')    
    self.CORE_om = tkutil.option_menu(self.middle_frame, "Buriedness", 
                                      self.core_list, 'DO NOT APPLY')        
    self.CORE_om.frame.pack(side = 'top', anchor = 'nw')                
                
    self.AA_list = ('DO NOT APPLY','A','R','N','D','C','Q','E','G','H',
                    'I','L','K','M','F','P','S','T','W','Y','V','X')               
    self.AA_list2 = ('DO NOT APPLY','PREV_A','PREV_R','PREV_N','PREV_D',
                      'PREV_C','PREV_Q','PREV_E','PREV_G','PREV_H',
                      'PREV_I','PREV_L','PREV_K','PREV_M','PREV_F',
                      'PREV_P','PREV_S','PREV_T','PREV_W','PREV_Y',
                      'PREV_V','PREV_X')                   
    self.AA_list3 = ('DO NOT APPLY','NEXT_A','NEXT_R','NEXT_N',
                    'NEXT_D','NEXT_C','NEXT_Q','NEXT_E','NEXT_G','NEXT_H',
                    'NEXT_I','NEXT_L','NEXT_K','NEXT_M','NEXT_F','NEXT_P',
                    'NEXT_S','NEXT_T','NEXT_W','NEXT_Y','NEXT_V','PREV_X')                       
             
    self.PREV_om = tkutil.option_menu(self.middle_frame, "Previous residue", 
                                      self.AA_list, 'DO NOT APPLY')        
    self.PREV_om.frame.pack(side = 'top', anchor = 'nw')                    
               
    self.NEXT_om = tkutil.option_menu(self.middle_frame, "Next residue", 
                                      self.AA_list, 'DO NOT APPLY')        
    self.NEXT_om.frame.pack(side = 'top', anchor = 'nw')                    
            
    self.br = tkutil.button_row(self.top,
          # transfer assignments onto spectra
			   ('Transfer', self.transfer_cb),  
         # simulate possible assignments with a little _s
			   ('Simulate', self.simulate_cb),  
			   ('Untag', self.untag_cb),  # untag "_s"
			   ('Use .seq', self.seq_cb),  # use seq
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')
    
    tkutil.create_hint(self.br.buttons[0], 'Generate formated peak and '
                          'assignment onto selected experiment based on '
                          'existing assignment.')
    tkutil.create_hint(self.br.buttons[1], 'Generate formated peak and '
                          'assignment onto selected experiment based on '
                          'existing assignment and predicted chemical shifts')
    tkutil.create_hint(self.br.buttons[2], 'Untag "_s". "_s" indicates the '
                          'label is from non-existing assignment.')
    tkutil.create_hint(self.br.buttons[3], 'Use sequence file. Using "sq" '
            'to import sequence information into the project is recommended.')
        
    # shiftx2 set up
    self.bottom_frame = Tkinter.Frame(self.top, width = 600, height = 25)
    self.bottom_frame.pack(side='top', anchor='w')
    self.shiftx = tkutil.file_field(self.bottom_frame, 'ShiftX2', 
                                    'Select template .csv file.') 
    self.shiftx.frame.pack(side = 'left')
    self.shiftx_button = Tkinter.Button(self.bottom_frame, text = "?", 
                                  command = self.about_using_shiftx2)
    self.shiftx_button.pack(side = 'left')  
    self.shiftx_list = []
    
    # bmrb set up  
    self.bottom_frame2 = Tkinter.Frame(self.top, width = 600, height = 25)
    self.bottom_frame2.pack(side='top', anchor='w')
    self.bmrb = tkutil.file_field(self.bottom_frame2, 'BMRB', 
                                  'Select template .str file.')
    self.bmrb.frame.pack(side = 'left')
    self.bmrb_button = Tkinter.Button(self.bottom_frame2, text = "?", 
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
    self.status2_text.set("!Multiple runs on the spectrum may "
                          "generate duplicate peaks!")

        
    self.Carbons = 'C CA CB CD CD1 CD2 CE CE1 CE2 CE3 CG CG1 CG2 CH2 CZ '\
                    'CZ2 CZ3'
    self.Protons = 'H HA HA2 HA3 HB HB2 HB3 HD1 HD2 HD21 HD22 HD3 HE HE1 '\
                  'HE2 HE21 HE22 HE3 HG HG1 HG12 HG13 HG2 HG3 HH11 HH12 '\
                  'HH2 HH21 HH22 HZ HZ2 HZ3 QA QB QG QG1 QG2 QD QD1 QD2 '\
                  'QE QE1 QE2 QH QH1 QH2 QZ MA MB MG MG1 MG2 MD MD1 MD2 '\
                  'ME ME1 ME2 MH MH1 MH2 MZ'
    self.Nitrogen = 'N ND1 ND2 NE NE1 NE2 NH NH1 NH2 NZ'
    self.C_list = self.Carbons.split()
    self.H_list = self.Protons.split()
    self.N_list = self.Nitrogen.split()
# -----------------------------------------------------------------------------
#
  def about_using_shiftx2(self):
    tkMessageBox.showinfo('SHIFTX2', 'This is model-based prediction.\n'
              'You will be directed to SHIFTX2 webserver.\n'
              'Set to CSV output format.\nDownload .csv file and set it here.')
    import nmrfam
    nmrfam.about_shiftx2(self.session) 
# -----------------------------------------------------------------------------
# BMRB has higher priority
  def about_using_bmrb(self):
    tkMessageBox.showinfo('NMR-STAR', 'Select a NMR-STAR(BMRB V3.1) file to '
                          'use as chemical shift template.\n')

    import nmrfam
    nmrfam.about_bmrb(self.session)
# ----------------------------------------------------------------------------
# if PECAN apply button clicked
  def ApplyButtonReleaseCB(self, event):
    if self.PECAN_cb.state() == 1:
      self.TALOS_cb.set_state(0)      
      self.COND_cb.set_state(0)            
# ----------------------------------------------------------------------------
# if TALOS apply button clicked
  def ApplyButtonReleaseCB2(self, event):
    if self.TALOS_cb.state() == 1:
      self.PECAN_cb.set_state(0)    
      self.COND_cb.set_state(0)
# ----------------------------------------------------------------------------
# if COND apply button clicked
  def ApplyButtonReleaseCB3(self, event):
    if self.COND_cb.state() == 1:
      self.PECAN_cb.set_state(0)        
      self.TALOS_cb.set_state(0)      
# ----------------------------------------------------------------------------
  def simulate_cb(self):
    # check if spec and spec_type selected
    self.TransferAndSimulatePeaks(1)     # with simulation     
# ----------------------------------------------------------------------------
  def get_group(self, iSeqIdx):
    for group in self.group_list:
      if group.number == iSeqIdx:
        return group
    return None
# ----------------------------------------------------------------------------
  def seq_cb(self):
    seq_list = myseq.ReadSequence(self.session)
      
    # set sequences
    self.sequences = []
    self.groups = []
    ga = []
    
    for seq in seq_list:    
        self.sequences.append( (seq[1], seq[0]) )
        self.groups.append(WGroup(seq[1], seq[0]) )
        
    tkMessageBox.showinfo('Use sequence', '%d residues loaded.' % \
                          (len(self.sequences)) )
# ----------------------------------------------------------------------------
  def untag_cb(self):
    UNTAG_S(self.session)

# ----------------------------------------------------------------------------
  def transfer_cb(self):
    self.TransferAndSimulatePeaks(0)    # no simulaation
  # ---------------------------------------------------------------------------
  # Update peak lists when spectra selection is changed
  #!
  def select_spectype(self, event):
    # add selected spectra to selected spectra list
    ed = self.spec_type.event_line_data(event)
    self.selected_spec_type = ed    
# ----------------------------------------------------------------------------
  def TransferAndSimulatePeaks(self, iSimMode):
    # check if sp=ec and spec_type selected
    bSwap = False
    if self.spec.spectrum() == None:
      tkMessageBox.showerror("Spectrum Error", 
                          "Please select a spectrum to populate assignments.")
      return

    # fetch bmrb if there are
    import nmrstar
    self.bmrb_list = []
    if self.bmrb.variable.get() != '':    
      self.bmrb_list = nmrstar.FetchBMRB(self.bmrb.variable.get())
    
    # fetch shiftx2 if there are
    import shiftx2
    self.shiftx_list = []
    if self.shiftx.variable.get() != '':
      self.shiftx_list = shiftx2.FetchShiftX2(self.shiftx.variable.get())
             
    session = self.session
    current_spectrum = self.spec.spectrum()
    try:  
      if self.spec_type == None or self.selected_spec_type == None:
        tkMessageBox.showerror("Spectrum Type Error", 
                            "Please select a type to populate assignments.")      
        return
      spec_name = self.selected_spec_type
      spectrum_index = self.supported_spectrum_list.index(spec_name)
    except TypeError:      
      tkMessageBox.showerror("Spectrum Type Error", 
                            "Please select a type to populate assignments.")
      return          
    
    current_spectrum_type_name = self.supported_spectrum_list[spectrum_index]
    current_spectrum_type = self.spectrum_type_list[spectrum_index]
 
    current_last_atom_type = self.last_atom_type_list[spectrum_index]
    current_corr_atom_type = self.corr_atom_type_list[spectrum_index]
    current_reversed_h_dim_type = self.reversed_h_dim_type_list[spectrum_index]
    current_reversed_cn_dim_type = self.reversed_cn_dim_type_list[spectrum_index]    
    
    
    # Get sequence index
    # Sorting is included
    group_list2 = myseq.BuildSequence(self.session, 3)
    group_list2 = myseq.CheckSequence(group_list2) # sort and fill the gap
    if len(self.bmrb_list) > 20:
      group_list2 = myseq.ReadSequence2(self.bmrb_list)
    elif len(self.shiftx_list) > 20:
      group_list2 = myseq.ReadSequence2(self.shiftx_list)
      

    # fill WGroup      
    group_list = []
    for i in range(len(group_list2)):
        group2 = group_list2[i]
        try:
          x = group2[0]+1
        except TypeError:
          print group2[0]
          continue
        group = WGroup(group2[1], group2[0])
        group_list.append(group)
    # filling a gap
    if (self.PECAN_cb.state() == 1):
      pecan_dict = pecan.ReadPecan(self.pecan_file.get())
      if len(pecan_dict) == 0:
        tkMessageBox.showerror("Format error", "PECAN output is not correct.");
        return
      for pecan_group in pecan_dict:
        new_group = WGroup(pecan_dict[pecan_group][1], pecan_group)
        bFound = 0
        for i in range(len(group_list)):
          curr_group = group_list[i]          
          if curr_group.number > new_group.number:
            group_list.insert(i, new_group)
            bFound = 1
            break
          elif curr_group.number == new_group.number:
            bFound = 1
            break
        if bFound == 0:
          group_list.append(new_group)
    
    elif (self.TALOS_cb.state() == 1):
      talos_dict = talos.ReadTalos(self.talos_file.get())
      if len(talos_dict) == 0:
        tkMessageBox.showerror("Format error", "TALOS output is not correct.");
        return
      for talos_group in talos_dict:
        new_group = WGroup(talos_dict[talos_group][1], talos_group)
        bFound = 0
        for i in range(len(group_list)):
          curr_group = group_list[i]          
          if curr_group.number > new_group.number:
            group_list.insert(i, new_group)
            bFound = 1
            break
          elif curr_group.number == new_group.number:
            bFound = 1
            break
        if bFound == 0:
          group_list.append(new_group) 

    else:       # if sequence is loaded by user
      for i in range(len(self.groups)):
        user_group = self.groups[i]
        (seqA, seqIndex) = sputil.parse_group_name(user_group.name)
        user_residue = self.sequences[i]
        new_group = WGroup(seqA, seqIndex)
        bFound = 0
        for j in range(len(group_list)):
          curr_group = group_list[j]          
          if curr_group.number > new_group.number:
            group_list.insert(j, new_group)
            bFound = 1
            break
          elif curr_group.number == new_group.number:
            bFound = 1
            break
        if bFound == 0:
          group_list.append(new_group)   
    self.group_list = group_list
    
    # check whether they are selected
    group_selection = []
    for i in range(len(group_list)):
        group = group_list[i]
        if self.m_applyoption.get() == 0:
          group_selection.append(1)        
          continue
        else:
          bSelected = 0
        for peak in self.session.selected_peaks():
            if peak.selected <> 1:
                continue
            if peak.is_assigned <> 1:
                continue      
            asns = sputil.parse_assignment(peak.assignment)
            if len(asns) <> 2:
                continue
            #group_atom1 = sputil.split_group_atom(asns[0])    
            #group_atom2 = sputil.split_group_atom(asns[1])
            group_atom1 = asns[0]
            group_atom2 = asns[1]
#            if ( ((group_atom1[1] == 'N') and (group_atom2[1] == 'H')) or \
# ((group_atom2[1] == 'N') and (group_atom1[1] == 'H')) ) and \
# (group.name == group_atom1[0]):
            if ( ((group_atom1[1][0:1] == 'N') and \
                  (group_atom2[1][0:1] == 'H')) or \
                  ((group_atom2[1][0:1] == 'N') and \
                  (group_atom1[1][0:1] == 'H')) ) and \
                  (group.name == group_atom1[0]):
                bSelected = 1
                break
            elif ( ((group_atom1[1][0:1] == 'C') and \
                  (group_atom2[1][0:1] == 'H')) or \
                  ((group_atom2[1][0:1] == 'C') and \
                  (group_atom1[1][0:1] == 'H')) ) and \
                  (group.name == group_atom1[0]):
                bSelected = 1
                break   
        if bSelected == 1:
            group_selection.append(1)
        else: 
            group_selection.append(0)
        
        
    if len(group_selection) == 0:
      tkMessageBox.showerror('No targets', 'Nothing to transfer.')
      return
    
    # data_size
    # types
    # 2D
    #   0: Small-Big, 1: Big-Small
    # 3D
    #   0: Small-Medium-Big, 1: Small-Big-Medium
    #   2: Medium-Small-Big, 3: Medium-Big-Small
    #   4: Big-Small-Medium, 5: Big-Medium-Small
    iPtType = -1
    if len(current_spectrum.data_size) == 3:  # not 2D
      [pt1, pt2, pt3] = current_spectrum.data_size
      if (pt1 < pt2) and (pt2 < pt3):        iPtType = 0
      elif (pt1 < pt3) and (pt3 < pt2):      iPtType = 1
      elif (pt2 < pt1) and (pt1 < pt3):      iPtType = 2
      elif (pt2 < pt3) and (pt3 < pt1):      iPtType = 3
      elif (pt3 < pt1) and (pt1 < pt2):      iPtType = 4
      elif (pt3 < pt2) and (pt2 < pt1):      iPtType = 5
    else: # 2D
      [pt1, pt2] = current_spectrum.data_size
      if pt1 < pt2: iPtType = 0
      else: iPtType = 1
    # Dimension typing, 0: H, 1: C,N, 2: h, co, cx
    # types
    # 2D
    #   0: Small-Big, 1: Big-Small
    # 3D
    #   0: Small-Medium-Big, 1: Small-Big-Medium
    #   2: Medium-Small-Big, 3: Medium-Big-Small
    #   4: Big-Small-Medium, 5: Big-Medium-Small

    res1 = float(current_spectrum.data_size[0]) / \
                current_spectrum.spectrum_width[0]
    res2 = float(current_spectrum.data_size[1]) / \
                current_spectrum.spectrum_width[1]
    if len(current_spectrum.data_size) == 3:  # not 2D
      [[min1, min2, min3], [max1, max2, max3]] = current_spectrum.region
      mean1 = (min1 + max1) / 2.0
      mean2 = (min2 + max2) / 2.0
      mean3 = (min3 + max3) / 2.0
      res3 = float(current_spectrum.data_size[2]) / \
                current_spectrum.spectrum_width[2]
      if (mean1 < mean2) and (mean2 < mean3):        iDimType = 0
      elif (mean1 < mean3) and (mean3 < mean2):      iDimType = 1
      elif (mean2 < mean1) and (mean1 < mean3):      iDimType = 2
      elif (mean3 < mean1) and (mean1 < mean2):      iDimType = 3
      elif (mean2 < mean3) and (mean3 < mean1):      iDimType = 4
      elif (mean3 < mean2) and (mean2 < mean1):      iDimType = 5
    else:     # 2D
      [[min1, min2], [max1, max2]] = current_spectrum.region
      mean1 = (min1 + max1) / 2.0
      mean2 = (min2 + max2) / 2.0
      if (mean1 < mean2):
        iDimType = 0
      else:
        iDimType = 1
   
    # Direct, Indirect typing
    # types
    # 2D
    #   0: H-N (HX-CX), 1: N-H (CX-HX)
    # 3D
    #   0: H-CN-ch, 1: H-ch-CN
    #   2: CN-H-ch, 3: CN-ch-H
    #   4: ch-H-CN, 5: ch-CN-H
    # use information: iDimType and current_reversed_dim_type
    iAxisType = 0
    iAddedCount = 0
    # aromatic experiments
    if current_spectrum_type_name.find('aro') != -1:
      # make all CX-HX-CB combinations first
      """
      arom_dict = {
        "H":(["CD2", "HD2"], ["CE1", "HE1"]),
        "F":(["CD1", "HD1"], ["CD2", "HD2"], ["CE1", "HE1"], ["CE2", "HE2"], 
             ["CZ", "HZ"]),
        "W":(["CD1", "HD1"], ["CE3", "HE3"], ["CH2", "HH2"], 
             ["CZ2", "HZ2"], ["CZ3", "HZ3"]),
        "Y":(["CD1", "HD1"], ["CD2", "HD2"], ["CE1", "HE1"], ["CE2", "HE2"])}
      """
      for i in range(len(group_list)):
        self.status_text.set("Current: %d / %d" % (i+1, len(group_list)))
        self.status.update_idletasks()
        if i == 0:    grp = None
        else:         grp = group_list[i-1]
        grp2 = group_list[i]
        if i == len(group_list)-1:    grp3 = None
        else:                         grp3 = group_list[i+1]
        
        if not grp2.symbol in arom_singlea:
          continue
        arom_set = arom_dict[grp2.symbol]
        
        label_list = []
        # C-HSQC, CBHD, CBHDHE
        if current_spectrum_type_name == 'C-HSQC(aro)' or \
            current_spectrum_type_name == 'CBHD(aro)' or \
            current_spectrum_type_name == 'CBHE(aro)' or \
            current_spectrum_type_name == 'CBHDHE(aro)':
          
          fCshift, fCdev, fCatm = GetFreq3(session, grp2, 'CB')
          fCshift_s, fCdev_s, iCount = \
                    pacsysimulate.GetSimFreq(session, self, grp2, 'CB')
          for catm, hatm in arom_set:
            if current_spectrum_type_name == 'C-HSQC(aro)':
              fCshift, fCdev, fCatm = GetFreq3(session, grp2, catm)
              fCshift_s, fCdev_s, iCount = \
                    pacsysimulate.GetSimFreq(session, self, grp2, catm)
            elif current_spectrum_type_name == 'CBHD(aro)' and catm[1] != 'D':
              continue
            elif current_spectrum_type_name == 'CBHE(aro)' and catm[1] != 'E':
              continue
            elif current_spectrum_type_name == 'CBHDHE(aro)' and \
                catm[1] != 'D' and catm[1] != 'E':
              continue
            fHshift, fHdev, fHatm = GetFreq3(session, grp2, hatm)
            fHshift_s, fHdev_s, iCount = pacsysimulate.GetSimFreq(session, \
                                                    self, grp2, hatm)
            
            if fCshift < 500:
              szCatom = fCatm
              fCcs = fCshift
            else:
              if current_spectrum_type_name == 'C-HSQC(aro)':
                szCatom = catm + '_s'
              else:
                szCatom = 'CB_s'
              fCcs = fCshift_s
            if fHshift < 500:
              szHatom = fHatm
              fHcs = fHshift
            else:
              szHatom = hatm + '_s'
              fHcs = fHshift_s
            lbl = szCatom + '-' + szHatom
            if lbl in label_list: continue
            if fCcs > 500 or fHcs > 500: continue
            label_list.append(lbl)
            if mean1 > mean2:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, \
                                                          [fCcs, fHcs])
              if pPeak != None:
                pPeak.assign(0, grp2.name, szCatom)
                pPeak.assign(1, grp2.name, szHatom)
            else:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, \
                                                            [fHcs, fCcs])
              if pPeak != None:
                pPeak.assign(0, grp2.name, szHatom)
                pPeak.assign(1, grp2.name, szCatom)
            if pPeak != None:
              pPeak.show_assignment_label()
              iAddedCount = iAddedCount+1
        # 3D    
        elif current_spectrum_type_name == 'CBCDHD(aro)' or \
              current_spectrum_type_name == 'CBCEHE(aro)':
          fCshift, fCdev, fCatm = GetFreq3(session, grp2, 'CB')
          fCshift_s, fCdev_s, iCount = pacsysimulate.GetSimFreq(session, \
                                                          self, grp2, 'CB')
          for catm, hatm in arom_set:
            if current_spectrum_type_name == 'CBCDHD(aro)' and catm[1] != 'D': 
              continue
            elif current_spectrum_type_name == 'CBCEHE(aro)' and catm[1] != 'E': 
              continue
            fCXshift, fCXdev, fCXatm = GetFreq3(session, grp2, catm)
            fCXshift_s, fCXdev_s, iCount = pacsysimulate.GetSimFreq(session, \
                                                            self, grp2, catm)
            fHshift, fHdev, fHatm = GetFreq3(session, grp2, hatm)
            fHshift_s, fHdev_s, iCount = pacsysimulate.GetSimFreq(session, \
                                                            self, grp2, hatm)
            
            if fCshift < 500:
              szCatom, fCcs = fCatm, fCshift
            else:
              szCatom, fCcs = 'CB_s', fCshift_s
            if fCXshift < 500:
              szCXatom, fCXcs = fCXatm, fCXshift
            else:
              szCXatom = catm + '_s'
              fCXcs = fCXshift_s
            if fHshift < 500:
              szHatom, fHcs = fHatm, fHshift
            else:
              szHatom, fHcs = hatm + '_s', fHshift_s
              
            lbl = szCatom + '-' + szCXatom + '-' + szHatom
            if lbl in label_list: continue
            if fCcs > 500 or fHcs > 500: continue
            
            if mean1 > mean2 and mean2 > mean3:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, 
                                                        [fCXcs, fCcs, fHcs])
              if pPeak != None:
                pPeak.assign(0, grp2.name, szCXatom)
                pPeak.assign(1, grp2.name, szCatom)
                pPeak.assign(2, grp2.name, szHatom)
            elif mean1 > mean3 and mean3 > mean2:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, 
                                                        [fCXcs, fHcs, fCcs])
              if pPeak != None:
                pPeak.assign(0, grp2.name, szCXatom)
                pPeak.assign(1, grp2.name, szHatom)
                pPeak.assign(2, grp2.name, szCatom)
            elif mean2 > mean1 and mean1 > mean3:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, 
                                                        [fCcs, fCXcs, fHcs])
              if pPeak != None:
                pPeak.assign(0, grp2.name, szCatom)
                pPeak.assign(1, grp2.name, szCXatom)
                pPeak.assign(2, grp2.name, szHatom)
            elif mean2 > mean3 and mean3 > mean1:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, 
                                                        [fHcs, fCXcs, fCcs])
              if pPeak != None:
                pPeak.assign(0, grp2.name, szHatom)
                pPeak.assign(1, grp2.name, szCXatom)
                pPeak.assign(2, grp2.name, szCatom)
            elif mean3 > mean1 and mean1 > mean2:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, 
                                                        [fCcs, fHcs, fCXcs])
              if pPeak != None:
                pPeak.assign(0, grp2.name, szCatom)
                pPeak.assign(1, grp2.name, szHatom)
                pPeak.assign(2, grp2.name, szCXatom)
            elif mean3 > mean2 and mean2 > mean1:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, 
                                                        [fCcs, fCXcs, fHcs])
              if pPeak != None:
                pPeak.assign(0, grp2.name, szCatom)
                pPeak.assign(1, grp2.name, szCXatom)
                pPeak.assign(2, grp2.name, szHatom)
            if pPeak != None:
              label_list.append(lbl)
              iAddedCount = iAddedCount+1
              pPeak.show_assignment_label()
        elif current_spectrum_type_name.find('TOCSY') != -1 or \
              current_spectrum_type_name.find('NOESY') != -1:
          for catm, hatm in arom_set:
            fCshift, fCdev, fCatm = GetFreq3(session, grp2, catm)
            fCshift_s, fCdev_s, iCount = pacsysimulate.GetSimFreq(session, 
                                                        self, grp2, catm)
            fHshift, fHdev, fHatm = GetFreq3(session, grp2, hatm)
            fHshift_s, fHdev_s, iCount = pacsysimulate.GetSimFreq(session, 
                                                        self, grp2, hatm)
                
            if fCshift < 500:
              szCatom, fCcs = fCatm, fCshift
            else:
              szCatom = catm + '_s'
              fCcs = fCshift_s
              
            if fHshift < 500:
              szHatom, fHcs = fHatm, fHshift
            else:
              szHatom = hatm + '_s'
              fHcs = fHshift_s
              
            if fCcs > 500 or fHcs > 500: continue
            
            ind_set = arom_set
            if current_spectrum_type_name.find('NOESY') != -1:
              x_list = atomnames.protein_atoms_by_group_no_pseudo[grp2.symbol]
              ind_set = []
              for xatm in x_list:
                if xatm[0] == 'H':
                  ind_set.append(['XX', xatm])

            for cxatm, hxatm in ind_set:
              if current_spectrum_type_name == 'HCCH-TOCSY(aro)' or \
                  current_spectrum_type_name == '13C-NOESY(aro)':
                fXshift, fXdev, fXatm = GetFreq3(session, grp2, hxatm)
                fXshift_s, fXdev_s, iCount = pacsysimulate.GetSimFreq(session, 
                                                            self, grp2, hxatm)
              elif current_spectrum_type_name == 'CCH-TOCSY(aro)':
                fXshift, fXdev, fXatm = GetFreq3(session, grp2, cxatm)
                fXshift_s, fXdev_s, iCount = pacsysimulate.GetSimFreq(session, 
                                                            self, grp2, cxatm)

              if fXshift < 500:
                szXatom = fXatm
                fXcs = fXshift
              else:
                if current_spectrum_type_name == 'HCCH-TOCSY(aro)' or \
                    current_spectrum_type_name == '13C-NOESY(aro)':
                  szXatom = hxatm + '_s'
                elif current_spectrum_type_name == 'CCH-TOCSY(aro)': 
                  szXatom = cxatm + '_s'
                fXcs = fXshift_s
              
              lbl = szCatom + '-' + szHatom + '-' + szXatom
              if lbl in label_list: continue
              if fXcs > 500: continue
              
              if current_spectrum_type_name == 'HCCH-TOCSY(aro)' or \
                  current_spectrum_type_name == '13C-NOESY(aro)':
                if mean1 > mean2 and mean1 > mean3 :     # C - 1
                  if (bSwap != (res2 < res3)) == \
                      current_spectrum_type_name == 'HCCH-TOCSY(aro)':   # H - 2, X - 3
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fCcs, fHcs, fXcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szCatom)
                      pPeak.assign(1, grp2.name, szHatom)
                      pPeak.assign(2, grp2.name, szXatom)
                  else: # H - 3, X - 2
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fCcs, fXcs, fHcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szCatom)
                      pPeak.assign(1, grp2.name, szXatom)
                      pPeak.assign(2, grp2.name, szHatom)
                elif mean2 > mean1 and mean2 > mean3:   # C - 2
                  if (bSwap != (res1 < res3)) == \
                      current_spectrum_type_name == 'HCCH-TOCSY(aro)':   # H - 1, X - 3
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fHcs, fCcs, fXcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szHatom)
                      pPeak.assign(1, grp2.name, szCatom)
                      pPeak.assign(2, grp2.name, szXatom)
                  else: # X - 1, H - 3
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fXcs, fCcs, fHcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szXatom)
                      pPeak.assign(1, grp2.name, szCatom)
                      pPeak.assign(2, grp2.name, szHatom)
                elif mean3 > mean1 and mean3 > mean2:   # C - 3
                  if (bSwap != (res1 < res2)) == \
                      current_spectrum_type_name == 'HCCH-TOCSY(aro)':   # H - 1, X - 2
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fHcs, fXcs, fCcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szHatom)
                      pPeak.assign(1, grp2.name, szXatom)
                      pPeak.assign(2, grp2.name, szCatom)
                  else: # X - 1, H - 2
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fXcs, fHcs, fCcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szXatom)
                      pPeak.assign(1, grp2.name, szHatom)
                      pPeak.assign(2, grp2.name, szCatom)
              elif current_spectrum_type_name == 'CCH-TOCSY(aro)':
                if mean1 < mean2 and mean1 < mean3:   # H - 1
                  if not bSwap:
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fHcs, fCcs, fXcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szHatom)
                      pPeak.assign(1, grp2.name, szCatom)
                      pPeak.assign(2, grp2.name, szXatom)
                  else:
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fHcs, fXcs, fCcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szHatom)
                      pPeak.assign(1, grp2.name, szCatom)
                      pPeak.assign(2, grp2.name, szXatom)
                elif mean2 < mean1 and mean2 < mean3: # H - 2
                  if not bSwap:
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fCcs, fHcs, fXcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szCatom)
                      pPeak.assign(1, grp2.name, szHatom)
                      pPeak.assign(2, grp2.name, szXatom)
                  else:
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fXcs, fHcs, fCcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szXatom)
                      pPeak.assign(1, grp2.name, szHatom)
                      pPeak.assign(2, grp2.name, szCatom)
                elif mean3 < mean1 and mean3 < mean2: # H - 3
                  if not bSwap:
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fCcs, fXcs, fHcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szCatom)
                      pPeak.assign(1, grp2.name, szXatom)
                      pPeak.assign(2, grp2.name, szHatom)
                  else:
                    pPeak = sputil.place_peak_in_spectral_region(
                                current_spectrum, [fXcs, fCcs, fHcs])
                    if pPeak != None:
                      pPeak.assign(0, grp2.name, szXatom)
                      pPeak.assign(1, grp2.name, szCatom)
                      pPeak.assign(2, grp2.name, szHatom)
              if pPeak != None:
                label_list.append(lbl)
                iAddedCount = iAddedCount+1
    # aliphatic experiments
    elif spectrum_index < 2: # 2D
      iAxisType = iDimType
    else:
      if (current_reversed_cn_dim_type == '0') and \
          (current_reversed_h_dim_type == '0'):  # CN > ch > H
        if iDimType == 0:  iAxisType = 1
        elif iDimType == 1: iAxisType = 0
        elif iDimType == 2: iAxisType = 4
        elif iDimType == 3: iAxisType = 5
        elif iDimType == 4: iAxisType = 2
        elif iDimType == 5: iAxisType = 3
      elif (current_reversed_cn_dim_type == '0') and \
          (current_reversed_h_dim_type == '1'):  # CN > H > ch
        if iDimType == 0:   iAxisType = 4
        elif iDimType == 1: iAxisType = 5
        elif iDimType == 2: iAxisType = 1
        elif iDimType == 3: iAxisType = 0
        elif iDimType == 4: iAxisType = 3
        elif iDimType == 5: iAxisType = 2
      elif (current_reversed_cn_dim_type == '1') and \
          (current_reversed_h_dim_type == '0'):  # ch > CN > H 
        if iDimType == 0:  iAxisType = 0
        elif iDimType == 1: iAxisType = 1
        elif iDimType == 2: iAxisType = 2
        elif iDimType == 3: iAxisType = 3
        elif iDimType == 4: iAxisType = 4
        elif iDimType == 5: iAxisType = 5       
      elif (current_reversed_cn_dim_type == '1') and \
          (current_reversed_h_dim_type == '1'):  # H > ch > CN
        if iDimType == 0:  iAxisType = 3
        elif iDimType == 1: iAxisType = 2
        elif iDimType == 2: iAxisType = 5
        elif iDimType == 3: iAxisType = 4
        elif iDimType == 4: iAxisType = 0
        elif iDimType == 5: iAxisType = 1         
      elif (current_reversed_cn_dim_type == '2') and \
          (current_reversed_h_dim_type == '0'):  # ch > H, CN ? ch
        if (iDimType == 0) or (iDimType == 1):  # small-X-X
          if pt2 > pt3: iAxisType = 1      # H-ch-CN
          else:         iAxisType = 0      # H-CN-ch
        elif (iDimType == 2) or (iDimType == 4): # X-small-X
          if pt1 > pt3: iAxisType = 4      # ch-H-CN 
          else:         iAxisType = 2      # CN-H-ch
        elif (iDimType == 3) or (iDimType == 5): # X-X-small
          if pt1 > pt2: iAxisType = 5      # ch-CN-H
          else:         iAxisType = 3      # CN-ch-H
      elif (current_reversed_cn_dim_type == '0') and \
          (current_reversed_h_dim_type == '2'):  # CN > ch, H ? ch H            layout3    
        if (iDimType == 0) or (iDimType == 2):
          if pt1 > pt2: iAxisType = 4      # ch-H-CN
          else:         iAxisType = 1      # H-ch-CN
        elif (iDimType == 1) or (iDimType == 3):
          if pt1 > pt3: iAxisType = 5      # ch-CN-H
          else:         iAxisType = 0      # H-CN-ch
        elif (iDimType == 4) or (iDimType == 5):
          if pt2 > pt3: iAxisType = 3      # CN-ch-H
          else:         iAxisType = 2      # CN-H-ch
    

    heavyatoms = []                
    # N, CX loop
    if current_corr_atom_type == '0': # H-N
      if current_spectrum_type_name == 'N-HSQC' or \
          current_spectrum_type_name == '15N-NOESY':
        heavyatoms.extend(self.N_list)      
      else:
        heavyatoms.append('N')
    else: #CX-HX    
      heavyatoms.extend(self.C_list)
      heavyatoms.remove('C')
    
  
    # what's the last atom type?
    ind_list = []
    if current_last_atom_type == 'C':    ind_list.append('C')  # carbonyl carbon
    elif current_last_atom_type == 'CA': ind_list.append('CA')
    elif current_last_atom_type == 'CB': ind_list.append('CB')
    elif current_last_atom_type == 'CACB':
      ind_list.append('CA')
      ind_list.append('CB')
    elif current_last_atom_type == 'HA': 
      ind_list.append('HA')
      ind_list.append('HA2')
      ind_list.append('HA3')
    elif current_last_atom_type == 'HB': 
      ind_list.append('HB')
      ind_list.append('HB2')
      ind_list.append('HB3')
    elif current_last_atom_type == 'HAHB':
      ind_list.append('HA')
      ind_list.append('HA2')
      ind_list.append('HA3')
      ind_list.append('HB')
      ind_list.append('HB2')
      ind_list.append('HB3')
    elif current_last_atom_type == 'CX':
      ind_list.extend(self.C_list)
      ind_list.remove('C')
    elif current_last_atom_type == 'HX':
      ind_list.extend(self.H_list)
      ind_list.remove('H')
    elif current_last_atom_type == 'HHX': # H+HX         
      ind_list.extend(self.H_list)
  
      
    # Loop sequence
    # GROUP: M1     #ATOMNAME:CA #RESONANCE.name : M1CA      
    for i in range(len(group_list)):
      self.status_text.set("Current: %d / %d" % (i+1, len(group_list)))    
      self.status.update_idletasks()
      if i == 0:
        group = None
      else:
        group = group_list[i-1]
      group2 = group_list[i]
      if i == len(group_list)-1:
        group3 = None
      else:
        group3 = group_list[i+1]  
      # see prior and next group sequence index	
      if (group != None) and (group.number != group2.number-1):
        group = None
      if (group3 != None) and (group3.number != group2.number+1):
        group3 = None        
      # set list for group, group2, group3
      grouplt = []
      if group != None:
        grouplt.append(group)
      if group2 != None:
        grouplt.append(group2)
      if group3 != None:	
        grouplt.append(group3)      
        
      if group_selection[i] == 0:
        continue  
          
      if (group2.symbol == 'P') and (current_corr_atom_type == '0'):   # proline with N-H types
        continue
                        
      for szHeavyAtom in heavyatoms:
        # N, CX frequency
        [fHeavyFreq, fHeavyDevi, szHeavyAtm] = \
                GetFreq3(session, group2, szHeavyAtom)
        [fSHeavyFreq, fSHeavyDevi, iSCount] = \
                pacsysimulate.GetSimFreq(session, self, group2, szHeavyAtom)

        if (fHeavyFreq > 1000) and (fSHeavyFreq > 1000):
          continue
        if (spectrum_index < 2) and (fHeavyFreq > 1000) and (iSimMode == 0): # 2D
          continue
          
        # H, HX frequency
        H_atom_list = []
        szTempH = 'H' + szHeavyAtom[1:]
        szTempQ = 'Q' + szHeavyAtom[1:]
        
        if (fHeavyFreq > 1000): 
          fHeavyFreq = fSHeavyFreq
          szHeavyAtom = szHeavyAtom + "_s"
        
        for szHAtom in self.H_list: 
          if (szHAtom == szTempH) or ( (szHAtom[:-1] == szTempH) \
              and (szHAtom[:-1] != 'H') ) or (szHAtom == szTempQ) \
              or ( (szHAtom[:-1] == szTempQ) and (szHAtom[:-1] != 'Q')):
            H_atom_list.append(szHAtom)
                      
        H_freq_list = []
        for szHAtom in H_atom_list:
          [fHFreq, fHDevi, szHAtm] = GetFreq3(session, group2, szHAtom)
          [fHSFreq, fHSDevi, iSCount] = pacsysimulate.GetSimFreq(session, \
                                                  self, group2, szHAtom)
          if (fHFreq > 1000) and (fHSFreq > 1000):
            continue
            
          if fHFreq < 500 and szHAtm != szHAtom and szHAtom != 'H':
            continue  # assigned to other nomenclature
          
          szHAtom_o = szHAtom
          if fHFreq > 1000:
            fHFreq = fHSFreq
            szHAtom = szHAtom + "_s"
          H_freq_list.append([szHAtom, fHFreq, szHAtom_o])
        
        # loop for CX-HX or NX-HX
        for [szHAtom, fHFreq, szHAtom_o] in H_freq_list:
          bPseudo = 0
          if pinelayout.pseudo_layout.has_key(group2.symbol):
            for szPseudo in pinelayout.pseudo_layout[group2.symbol]:
              if szHAtom_o in pinelayout.pseudo_layout[group2.symbol][szPseudo]:
                bPseudo = 1
                break
          if bPseudo == 1:
            [fRet1, fRet2, szHAtm] = GetFreq3(session, group2, szPseudo)
            if fRet1 < 9000:
              continue
            
          if GetPseudoPass(session, group2, szHAtom_o) == 1:
            continue
            
          # 2D
          if spectrum_index < 2:
            if ('_s' in szHAtom) and (iSimMode == 0): # 2D transfer
              continue          
            if iAxisType == 0:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, 
                                                        [fHFreq,fHeavyFreq])
            else:
              pPeak = sputil.place_peak_in_spectral_region(current_spectrum, 
                                                        [fHeavyFreq,fHFreq])
            if pPeak != None:
              pPeak.assign(iAxisType, group2.name, szHAtom)
              pPeak.assign(1-iAxisType, group2.name, szHeavyAtom)            
              pPeak.show_assignment_label() 
              iAddedCount = iAddedCount+1
            continue
          # 3D 
          for szIndirectAtom in ind_list:
            [fIndFreq, fIndDevi, szIndAtm] = \
                GetFreq3(session, group, szIndirectAtom)
            [fIndFreq2, fIndDevi2, szIndAtm2] = \
                GetFreq3(session, group2, szIndirectAtom)
            
            [fIndSFreq, fIndSDevi, iSCount] = pacsysimulate.GetSimFreq(
                                  session, self, group, szIndirectAtom)
            [fIndSFreq2, fIndSDevi2, iSCount2] = pacsysimulate.GetSimFreq(
                                  session, self, group2, szIndirectAtom)

            if (fIndFreq > 1000) and (fIndSFreq < 1000) and (iSimMode == 1):
              fIndFinalFreq = fIndSFreq
              szIndAtom = szIndirectAtom + '_s'
            else:
              fIndFinalFreq = fIndFreq
              szIndAtom = szIndirectAtom
              
            if (fIndFreq2 > 1000) and (fIndSFreq2 < 1000) and (iSimMode == 1):
              fIndFinalFreq2 = fIndSFreq2
              szIndAtom2 = szIndirectAtom + '_s'                       
            else:
              fIndFinalFreq2 = fIndFreq2
              szIndAtom2 = szIndirectAtom

            pPeak = None
            pPeak2 = None
            pPeak3 = None

            szHAtom_n = szHAtom.replace("_s", "")
            szIndAtom_n = szIndAtom.replace("_s", "")
            szIndAtom2_n = szIndAtom2.replace("_s", "")
            szHeavyAtom_n = szHeavyAtom.replace("_s", "")
                                              
            # i-1
            if ((current_spectrum_type == '0') or \
                (current_spectrum_type == '1') or \
                (current_spectrum_type == '4') and 1) and \
                (fIndFinalFreq < 1000):
              # check whether the atom is available or not
              bDraw = 1
              disabled_layout = []
              disabled_layout2 = []
              if pinelayout.pine_disabled_layout.has_key(group2.symbol):
                disabled_layout2 = pinelayout.pine_disabled_layout[group2.symbol]
              if pinelayout.pine_disabled_layout.has_key(group.symbol):
                disabled_layout = pinelayout.pine_disabled_layout[group.symbol]
                
              if (szHeavyAtom_n in disabled_layout2) or \
                  (szHAtom_n in disabled_layout2) or \
                  (szIndAtom_n in disabled_layout):
                bDraw = 0

              if ('_s' in szHAtom or '_s' in szHeavyAtom or '_s' in szIndAtom) \
                  and (iSimMode == 0):
                bDraw = 0

              if szIndAtm[1:] != szIndAtom_n[1:] and not '_s' in szIndAtom:
                bDraw = 0

              if bDraw == 1:
                # fHeavyFreq, fHFreq, fIndFreq - szHeavyAtom, szHAtom, szIndirectAtom
                if iAxisType == 0:          #   0: H-CN-ch
                  pPeak = sputil.place_peak_in_spectral_region(
                        current_spectrum, [fHFreq, fHeavyFreq, fIndFinalFreq])
                  if pPeak != None:
                    pPeak.assign(0, group2.name, szHAtom)
                    pPeak.assign(1, group2.name, szHeavyAtom)
                    pPeak.assign(2, group.name, szIndAtom)                
                elif iAxisType == 1:        #   1: H-ch-CN
                  pPeak = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fHFreq, fIndFinalFreq, fHeavyFreq])
                  if pPeak != None:
                    pPeak.assign(0, group2.name, szHAtom)
                    pPeak.assign(1, group.name, szIndAtom)                 
                    pPeak.assign(2, group2.name, szHeavyAtom)                
                elif iAxisType == 2:        #   2: CN-H-ch
                  pPeak = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fHeavyFreq, fHFreq, fIndFinalFreq])
                  if pPeak != None:
                    pPeak.assign(0, group2.name, szHeavyAtom)
                    pPeak.assign(1, group2.name, szHAtom)                
                    pPeak.assign(2, group.name, szIndAtom)                
                elif iAxisType == 3:        #   3: CN-ch-H
                  pPeak = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fHeavyFreq, fIndFinalFreq, fHFreq])
                  if pPeak != None:
                    pPeak.assign(0, group2.name, szHeavyAtom)
                    pPeak.assign(1, group.name, szIndAtom)                
                    pPeak.assign(2, group2.name, szHAtom)
                elif iAxisType == 4:        #   4: ch-H-CN
                  pPeak = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fIndFinalFreq, fHFreq, fHeavyFreq])
                  if pPeak != None:
                    pPeak.assign(0, group.name, szIndAtom)                
                    pPeak.assign(1, group2.name, szHAtom)              
                    pPeak.assign(2, group2.name, szHeavyAtom)                              
                elif iAxisType == 5:        #   5: ch-CN-H        
                  pPeak = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fIndFinalFreq, fHeavyFreq, fHFreq])
                  if pPeak != None:
                    pPeak.assign(0, group.name, szIndAtom)                
                    pPeak.assign(1, group2.name, szHeavyAtom)              
                    pPeak.assign(2, group2.name, szHAtom)
                if pPeak != None:
                  iAddedCount = iAddedCount + 1
            # i
            if ((current_spectrum_type == '1') or \
                (current_spectrum_type == '3') or \
                (current_spectrum_type == '4') and 1) and \
                (fIndFinalFreq2 < 1000):
                
              # check whether the atom is available or not
              bDraw = 1
              disabled_layout = []                
            
              if pinelayout.pine_disabled_layout.has_key(group2.symbol):
                disabled_layout = pinelayout.pine_disabled_layout[group2.symbol]
                if (szHeavyAtom_n in disabled_layout) or \
                    (szHAtom_n in disabled_layout) or \
                    (szIndAtom2_n in disabled_layout):
                  bDraw = 0
                  
              if ('_s' in szHAtom or '_s' in szHeavyAtom or '_s' in szIndAtom2) \
                  and (iSimMode == 0):
                bDraw = 0
          
              if szIndAtm2[1:] != szIndAtom_n[1:] and not '_s' in szIndAtom2:
                bDraw = 0

              if bDraw == 1:
                # fHeavyFreq, fHFreq, fIndFreq - szHeavyAtom, szHAtom, szIndirectAtom
                if iAxisType == 0:          #   0: H-CN-ch
                  pPeak2 = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fHFreq, fHeavyFreq, fIndFinalFreq2])
                  if pPeak2 != None:
                    pPeak2.assign(0, group2.name, szHAtom)
                    pPeak2.assign(1, group2.name, szHeavyAtom)
                    pPeak2.assign(2, group2.name, szIndAtom2)                
                elif iAxisType == 1:        #   1: H-ch-CN
                  pPeak2 = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fHFreq, fIndFinalFreq2, fHeavyFreq])
                  if pPeak2 != None:
                    pPeak2.assign(0, group2.name, szHAtom)
                    pPeak2.assign(1, group2.name, szIndAtom2)                 
                    pPeak2.assign(2, group2.name, szHeavyAtom)                
                elif iAxisType == 2:        #   2: CN-H-ch
                  pPeak2 = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fHeavyFreq, fHFreq, fIndFinalFreq2])
                  if pPeak2 != None:
                    pPeak2.assign(0, group2.name, szHeavyAtom)
                    pPeak2.assign(1, group2.name, szHAtom)                
                    pPeak2.assign(2, group2.name, szIndAtom2)                
                elif iAxisType == 3:        #   3: CN-ch-H
                  pPeak2 = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fHeavyFreq, fIndFinalFreq2, fHFreq])
                  if pPeak2 != None:
                    pPeak2.assign(0, group2.name, szHeavyAtom)
                    pPeak2.assign(1, group2.name, szIndAtom2)                
                    pPeak2.assign(2, group2.name, szHAtom)
                elif iAxisType == 4:        #   4: ch-H-CN
                  pPeak2 = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fIndFinalFreq2, fHFreq, fHeavyFreq])
                  if pPeak2 != None:
                    pPeak2.assign(0, group2.name, szIndAtom2)                
                    pPeak2.assign(1, group2.name, szHAtom)              
                    pPeak2.assign(2, group2.name, szHeavyAtom)                              
                elif iAxisType == 5:        #   5: ch-CN-H      
                  pPeak2 = sputil.place_peak_in_spectral_region(
                      current_spectrum, [fIndFinalFreq2, fHeavyFreq, fHFreq])
                  if pPeak2 != None:                                          
                    pPeak2.assign(0, group2.name, szIndAtom2)                
                    pPeak2.assign(1, group2.name, szHeavyAtom)              
                    pPeak2.assign(2, group2.name, szHAtom)    
                if pPeak2 != None:
                  iAddedCount = iAddedCount + 1        
            # i+1    : NOESY
            #if ((current_spectrum_type == '4') and 1):
                    
            if pPeak != None:    
              pPeak.show_assignment_label()   
            if pPeak2 != None:                  
              pPeak2.show_assignment_label()  
            if pPeak3 != None:                  
              pPeak3.show_assignment_label()                          
    # Direct, Indirect typing
    # types
    # 2D
    #   0: H-N (HX-CX), 1: N-H (CX-HX)
    # 3D
    #   0: H-CN-ch, 1: H-ch-CN
    #   2: CN-H-ch, 3: CN-ch-H
    #   4: ch-H-CN, 5: ch-CN-H
    # use information: iDimType and current_reversed_dim_type
    szPrint = '%d peaks were populated.' % (iAddedCount)
    tkMessageBox.showinfo('Transfer assignments onto spectrum', szPrint)
# ----------------------------------------------------------------------------
def TAN(session):
  sputil.the_dialog(tan_dialog,session).show_window(1)
  
def UNTAG_S(session):
  # check if spec and spec_type selected
  if session.selected_spectrum() == None:
    tkMessageBox.showerror("Spectrum Error", "Please select a spectrum to untag.")
    return

  for peak in session.selected_spectrum().peak_list():
    if not peak.is_assigned:
      continue
      
    if peak.selected <> 1:
      continue

    asns = sputil.parse_assignment(peak.assignment)

    for i in range(len(asns)):
      asn = asns[i]
      new_asn = asn[1].replace("_s", "")
      peak.assign(i, asn[0], new_asn)

def CENTER_AND_UNTAG_S(session):
  if session.selected_spectrum() == None:
    tkMessageBox.showerror("Spectrum Error", "Please select a spectrum to untag.")
    return
    
  for peak in session.selected_spectrum().peak_list():
    if peak.is_assigned != 1:
      continue
      
    if peak.selected != 1:
      continue
    
    peak.center()
          
  UNTAG_S(session)

def MERGE_TWO_H(session):
  if session.selected_spectrum() == None:
    tkMessageBox.showerror("Spectrum Error", "Please select a spectrum to untag.")
    return

  if len(session.selected_spectrum().selected_peaks()) != 2:
    tkMessageBox.showerror("Peak Error", "Please select two peaks to merge.")
    return

  peak1 = session.selected_spectrum().selected_peaks()[0]
  peak2 = session.selected_spectrum().selected_peaks()[1]
  
  if (peak1.is_assigned != 1) or (peak2.is_assigned != 1):
    tkMessageBox.showerror("Peak Error", "Select two peaks must be assigned.")
    return

  pdTol = []
  for i in range(len(peak1.frequency)):
    if peak1.resonances()[i].atom.nucleus == '1H':
      dTol = 0.01
    else:
      dTol = 0.1
    pdTol.append(dTol)
    
    if abs(peak1.frequency[i]-peak2.frequency[i]) > dTol:
      tkMessageBox.showerror("Peak Error", "Select two peaks at the same position.")
      return
   
    if peak1.resonances()[i].group.name != peak2.resonances()[i].group.name: 
      tkMessageBox.showerror("Assignment Error", "Select two peaks with the similar assignments.")
      return
      
  peak1.selected = 0
  if peak1.label != None:
    peak1.label.selected = 0
    
  peak2.selected = 0    
  if peak2.label != None:
    peak2.label.selected = 0
    
  for i in range(len(peak1.frequency)):
    resonance1 = peak1.resonances()[i]
    resonance2 = peak2.resonances()[i]

    if abs(peak1.frequency[i]-peak2.frequency[i]) > pdTol[i]: continue
    if len(resonance1.atom.name) < 2: continue
    if len(resonance2.atom.name) < 2: continue
    if resonance1.atom.name[0:2] != resonance2.atom.name[0:2]: continue

    #if resonance1.atom.nucleus != '1H': 
    #  continue

    new_nomenclature = resonance1.atom.name[0:2]
    for j in range(2, len(resonance1.atom.name)):
      if resonance1.atom.name[j] == resonance2.atom.name[j]:
        new_nomenclature = new_nomenclature + resonance1.atom.name[j]

    peak1.assign(i, resonance1.group.name, new_nomenclature)
    
    peak1.selected = 0
    peak2.selected = 1

  for label in session.selected_spectrum().label_list():
    label.selected = 0
  
  if peak2.label != None:
    peak2.label.selected = 1
    
  session.command_characters("")            
