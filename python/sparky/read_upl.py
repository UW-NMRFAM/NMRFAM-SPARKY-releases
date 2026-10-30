# -----------------------------------------------------------------------------
# Read UPL files to generate NOE peaks on NOESY spectra
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: November 23, 2014
# 
# -----------------------------------------------------------------------------

import os
import tkutil
import sputil
import Tkinter
import tkMessageBox
import myseq
import pinelayout
# -----------------------------------------------------------------------------
#
class read_upl_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Read distance constraints')

    self.spec_list = []
    self.session = session
    
    # upl
    upl_frame = Tkinter.Frame(self.top, width = 500, height = 25)
    upl_frame.pack(side = 'top', anchor = 'nw')
    
    upl = tkutil.file_field(upl_frame.top, 'UPL file (*.upl): ', 'Browse')
    upl.frame.pack(side = 'top', anchor = 'w')
    self.upl = upl
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')   
    
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
			   ('Generate NOEs', self.generate_cb),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')

  def generate_cb(self):
    # check if user set upl file
    # if not, show message
    if self.upl.get() == '' or os.path.isfile(self.upl.get()) == False:
      tkMessageBox.showerror("UPL error", "Please set valid .upl file.")
      return
    # read upl and validate the format
    f = open(self.upl.get(), 'r')
    upl_read = f.readlines()
    f.close()
    
    iPassed = 0
    
    # loop
    for (spec,type_om) in self.spec_list:
      if type_om.get() == 'DO NOT APPLY':        continue
      if spec == None: continue
      if type_om.get() == '15N-NOESY': spec_type = '15N'
      elif type_om.get() == '13C-NOESY (ali)': spec_type = '13C1'
      elif type_om.get() == '13C-NOESY (aro)': spec_type = '13C2'
      else: continue
      
      for restraint_line in upl_read:
        if restraint_line.strip() == '': 
          iPassed = iPassed + 1;
          continue
        if restraint_line.strip()[0] == '#': 
          iPassed = iPassed + 1;
          continue
        splited = restraint_line.strip().split()
        if len(splited) < 7: 
          iPassed = iPassed + 1;
          continue
        
        try:
          iSeqIdx = int(splited[0])
          iSeqIdx2 = int(splited[3])
        except:
          iPassed = iPassed + 1;
          continue
          
        szAAA = splited[1]
        szAAA2 = splited[4]
        szA = myseq.aaa2a(szAAA)
        szA2 = myseq.aaa2a(szAAA2)
        szAtom = splited[2]
        szAtom2 = splited[4]
        
        szGroup = '%s%d' % (szA, iSeqIdx)         # M1
        szGroup2 = '%s%d' % (szA2, iSeqIdx2)      
        
        if (len(szAtom) < 1) or (len(szAtom2) < 1): 
          iPassed = iPassed + 1;
          continue
          
        # only hydrogens?  
        if szAtom[0] <> 'H' and szAtom[0] <> 'Q' and szAtom[0] <> 'M':
          iPassed = iPassed + 1;
          continue
        if szAtom2[0] <> 'H' and szAtom2[0] <> 'Q' and szAtom2[0] <> 'M':
          iPassed = iPassed + 1;
          continue
        # reset nomenclature: QX, QQX, MX ->  HX. HN -> H
        # DON'T COMPLAIN! WHAT ELSE I CAN DO???
        szAtom = szAtom.replace("QQ", "H")
        szAtom = szAtom.replace("Q", "H")
        szAtom = szAtom.replace("M", "H")
        szAtom = szAtom.replace("HN", "H")
        szAtom2 = szAtom2.replace("QQ", "H")
        szAtom2 = szAtom2.replace("Q", "H")
        szAtom2 = szAtom2.replace("M", "H")
        szAtom2 = szAtom2.replace("HN", "H")
        
        szCNAtom = myseq.GetAttachedHeavyAtom(szA, szAtom)
        szCNAtom2 = myseq.GetAttachedHeavyAtom(szA2, szAtom2)
        
        # get chemical shift
        dAtom = 9999
        dAtom2 = 9999
        dCNAtom = 9999
        dCNAtom2 = 9999
        dDevTemp = 0
        
        # chemical shift?
        (dCNAtom, dDevTemp) = GetFrequency(szGroup, szCNAtom)
        (dCNAtom2, dDevTemp) = GetFrequency(szGroup2, szCNAtom2)
        (dAtom, dDevTemp) = GetFrequency(szGroup, szAtom)
        (dAtom2, dDevTemp) = GetFrequency(szGroup2, szAtom2)
        
        # simulate NOE
        # N-H-h
        
        # CX-HX-h

        
        spec.spectrum().place_peak((v1, v2, v3))
        
  # ---------------------------------------------------------------------------
  # This function is from PINE-SPARKY code
  # usage: (cs_avg, cs_dev) = self.GetFrequency("M1", "CA")
  #
  def GetFrequency(self, selected_group, szAtom):
      for condition in self.session.project.condition_list():
          group_name = '%s%d' % (selected_group[0], selected_group[1])
          resonance = condition.find_resonance(group_name, szAtom)
          if resonance <> None:
              if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                  return 9999, 9999
              return resonance.frequency, resonance.deviation
          else:
              # processing pseudo atoms
              if pinelayout.pseudo_layout.has_key(selected_group[0]) and szAtom[:1] == 'H':
                  layout = pinelayout.pseudo_layout[selected_group[0]];   
                  szAtom2 = ('Q%s' % szAtom[1:-1])
                  resonance = condition.find_resonance(group_name, szAtom2)
                  if resonance <> None:
                      if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                          return 9999, 9999
                      return resonance.frequency, resonance.deviation
              # processing meta atoms
              if not pinelayout.meta_layout.has_key(selected_group[0]):
                  continue
              layout = pinelayout.meta_layout[selected_group[0]];
              szAtom2 = szAtom  #HB3
              while len(szAtom2) > 2:
                  szAtom_1 = szAtom2[:-1] # HB
                  if layout.has_key(szAtom_1):
                      atom_list = layout[szAtom_1]
                      if szAtom in atom_list:
                          resonance = condition.find_resonance(group_name, szAtom_1)  
                          if resonance <> None:
                              if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                                  return 9999, 9999
                              return resonance.frequency, resonance.deviation
                          else:
                              for szPseudoAtom in atom_list:
                                  resonance = condition.find_resonance(group_name, szPseudoAtom)
                                  if resonance <> None:
                                      if (resonance.frequency == 0.0) and (resonance.deviation == 0.0):
                                          return 9999, 9999
                                      return resonance.frequency, resonance.deviation
                  szAtom2 = szAtom_1
                  if len(szAtom2) < 2:
                      break
      return 9999, 9999
# -----------------------------------------------------------------------------
#
def read_upl(session):
  sputil.the_dialog(read_upl_dialog,session).show_window(1)
