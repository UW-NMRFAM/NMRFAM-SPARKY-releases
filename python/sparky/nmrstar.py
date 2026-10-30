# -----------------------------------------------------------------------------
# BMRB file support
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Oct 7, 2019
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import myseq
import tkMessageBox
import tkFileDialog
import tkutil

# -----------------------------------------------------------------------------
#
class generate_nmrstar_peak_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = sesion
    
    # Chemical shift check box
    self.m_csoption = Tkinter.IntVar()
    cstype_cb = Tkinter.Checkbutton(self.top, text = 'Include chemical shifts', variable = self.m_csoption, onvalue=1, offvalue = 0)
    cstype_cb.pack(side = 'top', anchor = 'w')
    
    # spectrum list box
    # Spectrum list
    spec = sputil.spectrum_menu(session, self.top, 'Spectrum: ')
    spec.frame.pack(side = 'top', anchor = 'w')
    self.spec = spec
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
        
    # Peak List ID
    pl_ID = tkutil.entry_field(self.top, 'Peak List ID: ', initial = 1, width = 5)
    pl_ID.frame.pack(side = 'top')
    self.pl_id = pl_ID.variable
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
            
    # Generate button
    br = tkutil.button_row(self.top,
         ('Add', self.add_cb),
         ('Delete', self.del_cb),
         ('Clear', self.clear_cb),         
			   ('Generate', self.generate_cb),
			   ('Stop', self.stop_cb),
			   ('Close', self.close_cb),
			   )
      
# -----------------------------------------------------------------------------
#
def GenerateNmrStarPeak(session):
  sputil.the_dialog(generate_nmrstar_peak_dialog,session).show_window(1)  
# -----------------------------------------------------------------------------
#
class convert_nmrstar_peak_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = sesion
    
    # STAR FILE - Load
    # Spectral Peak List
    # Output 
    # Convert button  
# -----------------------------------------------------------------------------
#
def ConvertNmrStarPeak(session):
  sputil.the_dialog(convert_nmrstar_peak_dialog,session).show_window(1)    
# -----------------------------------------------------------------------------
#
def GetBiomoleculeType(session):
  atgcu = 0
  no_atgcu = 0
  for condition in session.project.condition_list():
    for resn in condition.resonance_list():
      aaa = myseq.a2aaa(resn.group.symbol)
      if aaa == 'XXX': continue
      if aaa in ['ADE', 'GUA', 'CYT', 'URA', 'THY']: atgcu = atgcu + 1
      else: no_atgcu = no_atgcu + 1
  if no_atgcu == 0 and atgcu > 0: return 'n'    
  return 'p'
# -----------------------------------------------------------------------------
#
def GenerateNmrStar(session):
  path = tkutil.save_file(session.tk, "Save to NMRSTAR 3.1 file", "nmrstar.str")
  if path:
    iFirst = 99999
    lines = []
    groups = []

  szSeqHeader = """save_protein
   _Entity.Sf_category                       entity
   _Entity.Sf_framecode                      protein
   _Entity.Entry_ID                          .
   _Entity.ID                                1
   _Entity.BMRB_code                         .
   _Entity.Name                              protein
   _Entity.Type                              polymer
   _Entity.Polymer_common_type               .
   _Entity.Polymer_type                      .
   _Entity.Polymer_type_details              .
   _Entity.Polymer_strand_ID                 .

   loop_
      _Entity_comp_index.ID
      _Entity_comp_index.Comp_ID

"""    
  szHeader = """save_chem_shift_list_1
   _Assigned_chem_shift_list.Sf_category                   assigned_chemical_shifts
   _Assigned_chem_shift_list.Sf_framecode                  chem_shift_list_1
   _Assigned_chem_shift_list.Entry_ID                      .
   _Assigned_chem_shift_list.ID                            1
   _Assigned_chem_shift_list.Chem_shift_1H_err             .
   _Assigned_chem_shift_list.Chem_shift_13C_err            .
   _Assigned_chem_shift_list.Chem_shift_15N_err            .
   _Assigned_chem_shift_list.Chem_shift_31P_err            .
   _Assigned_chem_shift_list.Chem_shift_2H_err             .
   _Assigned_chem_shift_list.Chem_shift_19F_err            .
   _Assigned_chem_shift_list.Error_derivation_method       .
   _Assigned_chem_shift_list.Details                       .
   _Assigned_chem_shift_list.Text_data_format              .
   _Assigned_chem_shift_list.Text_data                     .

   loop_  
      _Atom_chem_shift.ID
      _Atom_chem_shift.Comp_index_ID
      _Atom_chem_shift.Seq_ID
      _Atom_chem_shift.Comp_ID
      _Atom_chem_shift.Atom_ID
      _Atom_chem_shift.Atom_type
      _Atom_chem_shift.Atom_isotope_number
      _Atom_chem_shift.Val
      _Atom_chem_shift.Val_err
      _Atom_chem_shift.Ambiguity_code
      _Atom_chem_shift.Assigned_chem_shift_list_ID
      
"""
  szFooter = "\n   stop_\nsave_\n"
  import pinelayout

  
  # we don't know this is protein or nucleic acids.
  # we will determine using resonances.
  bt = GetBiomoleculeType(session)

  # Seq ID, Seq ID, Seq, Atom, Atom type, Isotop, CS, CS_Dev, 2
  for condition in session.project.condition_list():
    for resonance in condition.resonance_list():
      if bt == 'p':
        aaa = myseq.a2aaa(resonance.group.symbol)
      else:
        aaa = myseq.na_a2aaa(resonance.group.symbol)
      if aaa == 'XXX': continue
      
      atom_type = resonance.atom.name[0]
      if (atom_type == 'Q') or (atom_type == 'M'): atom_type = 'H'
      isotope = 1
      if atom_type == 'C': isotope = 13
      elif atom_type == 'N': isotope = 15
      elif atom_type == 'P': isotope = 31
            
      group = [resonance.group.number, aaa, resonance.atom.name, atom_type, 
                isotope, resonance.frequency, resonance.deviation]
      groups.append(group)
  groups.sort()
  
  group_list2 = myseq.BuildSequence(session, 3)
  group_list2 = myseq.CheckSequence(group_list2) # sort and fill the gap
  
  if myseq.GapInSequence(group_list2) == 1: # there is a gap
    tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
    group_list2 = myseq.LoadSeq(session, group_list2) # this fills a gap
    if group_list2 == None:
      tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
      return 0
     
  f = open(path, 'w')
  # add header
  f.write(szSeqHeader)
  for group2 in group_list2:
    szAAA = myseq.a2aaa(group2[1])
    if bt == 'n': szAAA = myseq.aaa2na_aaa(szAAA)
    szWrite = '%9d %s\n' % (group2[0], szAAA)
    f.write(szWrite)
  f.write('%s\n' % (szFooter))
    
  f.write(szHeader)
  iLine = 1                  
  for group in groups:

    iAmb = 0    
    if group[0] == None:
      continue
    if pinelayout.pseudo_layout.has_key(group[1]):
      if pinelayout.pseudo_layout[group[1]].has_key(group[2]):
        iAmb = 1
    if pinelayout.meta_layout.has_key(group[1]):
      if pinelayout.meta_layout[group[1]].has_key(group[2]):
        iAmb = 1                  
                  
    try:
      szWrite = "%6d %4d %4d %5s %5s %2s %2d %8.3f %6.2f %d  1\n" % \
                (iLine, group[0], group[0], group[1], 
                  group[2], group[3], group[4], group[5], 
                  group[6], iAmb)
  
      iLine = iLine+1
      f.write(szWrite)
    except:
      tkMessageBox.showerror('error', group)
      pass      

  f.write(szFooter)
  f.close()
  tkMessageBox.showinfo('Export to NMRSTAR 3.1', 'Saved.')      
  return 1

def ConvertBmrbToSparky(session):
  file_opt = options = {}  
  options['defaultextension'] = '.str'
  options['filetypes'] = [('NMR-STAR 3.1', '.str')]
  options['title'] = 'Select NMR-STAR 3.1 file to convert'  
  szFileName = tkFileDialog.askopenfilename(**file_opt)
  
  if szFileName == '':
    return
    
  external_cs_list = FetchBMRB(szFileName)
  myseq.SaveSparkyResonance(session, external_cs_list)
  
  tkMessageBox.showinfo('Resonance List', 'Finished. Use two-letter-code rl to read-in')  


def FetchBMRB(szURL):
  # if szURL starts with 'www', put 'http://'
  # else if 'http:', none
  # else, put 'file://'
  iType = 0   # 0: http, 1: local
  if szURL.strip() == '': return []
  if len(szURL) < 6 and szURL.find('.') == -1: 
    iType = 0
    szURL = 'http://rest.bmrb.wisc.edu/bmrb/' + szURL + '/nmr-star3'
  elif szURL[0:3] == 'www': 
    iType = 0
    szURL = 'http://' + szURL
  elif szURL[0:4] != 'http': iType = 1
  
  if iType == 0:  # url
    try: 
      import urllib2
    except:
      tkMessageBox.showerror('urllib2', 'You do not have openssl installed or set properly.\nPlease download .str (NMR-STAR V3) file to your local machine.');
      return []
    try:  
      response = urllib2.urlopen(szURL)
    except:
      tkMessageBox.showerror('URL','URL for your shift file is not correct.');
      return []
    csv_lines = response.readlines()
  else:   # file type
    try:
      f = open(szURL, 'r')
    except:  
      tkMessageBox.showerror('PATH','File path for your shift csv is not correct.');
      return []
    csv_lines = f.readlines()
    f.close()
    

  # now start parsing!!!  
  iRecordStart = 0
  iSeqID = iCompID = iAtomID = iVal = -1
  
  nmrstar_list = []
  for i in range(len(csv_lines)):
    line = csv_lines[i]
    # try to find field structure first
    splitted = line.strip().split('.')
    if len(splitted) < 2: continue
    if splitted[0] == '_Atom_chem_shift': # here comes!
      for j in range(i,len(csv_lines)):
        line2 = csv_lines[j]
        if iRecordStart == 0:
          splitted = line2.strip().split('.')
          if len(splitted) < 2: 
           # done reading fields.
            iRecordStart = iRecordStart + 1
            continue 
          if splitted[1] == 'Seq_ID':
            iSeqID = j-i    # SeqIdx
          elif splitted[1] == 'Comp_ID':
            iCompID = j-i   # Amino Acid
          elif splitted[1] == 'Atom_ID':
            iAtomID = j-i   # Amino Acid
          elif splitted[1] == 'Val':
            iVal = j-i   # Chemical Shift
        elif iRecordStart == 1: 
          splitted = line2.strip().split()        
          if len(splitted) < 2: 
           # done reading chemical shifts.
            iRecordStart = iRecordStart + 1
            continue           
          if iSeqID == -1 or iCompID == -1 or iAtomID == -1 or iVal == -1:
            iRecordStart = iRecordStart + 1
            continue  # wrong format
          try:  
            iSeqIdx = int(splitted[iSeqID])
          except:
            continue
          szA = myseq.aaa2a(splitted[iCompID])
          if szA != 'X':
            szAtom = splitted[iAtomID]
          elif myseq.na_aaa2a(splitted[iCompID]):
            szAtom = splitted[iAtomID]
          else: continue

          try:
            dCS = float(splitted[iVal])
          except:
            continue
          nmrstar_list.append( (iSeqIdx,  szA, szAtom, dCS) )  
        else:
          continue    
  # done reading
  
  return nmrstar_list



BMRB_sample="""

save_spectral_peak_list_1
   _Spectral_peak_list.Sf_category                     spectral_peak_list
   _Spectral_peak_list.Sf_framecode                    spectral_peak_list_1
   _Spectral_peak_list.Entry_ID                        15063
   _Spectral_peak_list.ID                              1
   _Spectral_peak_list.Sample_ID                       1
   _Spectral_peak_list.Sample_label                   $sample
   _Spectral_peak_list.Sample_condition_list_ID        1
   _Spectral_peak_list.Sample_condition_list_label    $sample_conditions_1
   _Spectral_peak_list.Experiment_ID                   9
   _Spectral_peak_list.Experiment_name                '13C-EDITED 1H,1H-NOESY'
   _Spectral_peak_list.Number_of_spectral_dimensions   3
   _Spectral_peak_list.Details                         .
   _Spectral_peak_list.Text_data_format                .
   _Spectral_peak_list.Text_data 
   

   loop_
      _Spectral_dim.ID
      _Spectral_dim.Atom_type
      _Spectral_dim.Atom_isotope_number
      _Spectral_dim.Spectral_region
      _Spectral_dim.Magnetization_linkage_ID
      _Spectral_dim.Under_sampling_type
      _Spectral_dim.Sweep_width
      _Spectral_dim.Sweep_width_units
      _Spectral_dim.Encoding_code
      _Spectral_dim.Encoded_source_dimension_ID
      _Spectral_dim.Entry_ID
      _Spectral_dim.Spectral_peak_list_ID

      1 H  1 H . . 14513.788 . . . 15063 1 
      2 H  1 H . . 11001.1   . . . 15063 1 
      3 C 13 C . . 13797.661 . . . 15063 1 

   stop_
   
   loop_
      _Peak_general_char.Peak_ID
      _Peak_general_char.Intensity_val
      _Peak_general_char.Intensity_val_err
      _Peak_general_char.Measurement_method
      _Peak_general_char.Entry_ID
      _Peak_general_char.Spectral_peak_list_ID

         1       486568.0 . height 15063 1 
         2      3092896.0 . height 15063 1 
         3      1107406.0 . height 15063 1 
   loop_
      _Peak_char.Peak_ID
      _Peak_char.Spectral_dim_ID
      _Peak_char.Chem_shift_val
      _Peak_char.Chem_shift_val_err
      _Peak_char.Line_width_val
      _Peak_char.Line_width_val_err
      _Peak_char.Phase_val
      _Peak_char.Phase_val_err
      _Peak_char.Decay_rate_val
      _Peak_char.Decay_rate_val_err
      _Peak_char.Coupling_pattern
      _Peak_char.Bounding_box_upper_val
      _Peak_char.Bounding_box_lower_val
      _Peak_char.Bounding_box_range_val
      _Peak_char.Details
      _Peak_char.Derivation_method_ID
      _Peak_char.Entry_ID
      _Peak_char.Spectral_peak_list_ID

         1 1  0.487 . . . . . . . . . . . . . 15063 1 
         1 2  2.822 . . . . . . . . . . . . . 15063 1 
         1 3 26.293 . . . . . . . . . . . . . 15063 1 
         2 1  0.873 . . . . . . . . . . . . . 15063 1 
         2 2  3.188 . . . . . . . . . . . . . 15063 1 
         2 3 23.566 . . . . . . . . . . . . . 15063 1 
         3 1  1.543 . . . . . . . . . . . . . 15063 1 
         3 2  3.994 . . . . . . . . . . . . . 15063 1 
         3 3 41.339 . . . . . . . . . . . . . 15063 1 
"""
