# -----------------------------------------------------------------------------
# NMR Exchange Format file support
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: March 24, 2020
#               Slight changes in the format
# Usage:
#
# 
# -----------------------------------------------------------------------------
#

import myseq
import tkMessageBox
import tkFileDialog
import tkutil
import time

current_time = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime())
szHeader = """#==========================================================================
#  Nmr Exchange Format Exported from NMRFAM-Sparky
#
#  Version: March 24, 2020
#
#

data_nef_my_nmr_meta_data

#
#===========================================================================
# Section 1
#
# Mandatory: nmr meta data
#
# Singleton (only one per project)
#
#========================================================================

save_nef_nmr_meta_data

# Mandatory:
  _nef_nmr_meta_data.sf_category                  nef_nmr_meta_data
  _nef_nmr_meta_data.sf_framecode                 nef_nmr_meta_data
  _nef_nmr_meta_data.format_name                  nmr_exchange_format
  _nef_nmr_meta_data.format_version               1.1
  _nef_nmr_meta_data.program_name                 NMRFAM-SPARKY
  _nef_nmr_meta_data.program_version              1.470
"""
szHeader = szHeader + "  _nef_nmr_meta_data.creation_date                " + current_time + "\n"
szHeader = szHeader + "  _nef_nmr_meta_data.uuid                         NMRFAM-SPARKY-" + current_time + "\n"
szHeader = szHeader + "save_" + "\n"
# requires stop and save
szSeqHeader = """
#=========================================================================
#
# Section 3
#
# Mandatory: Molecular system
#
# Singleton (only one per data block)
#
#=======================================================================


save_nef_molecular_system
  _nef_molecular_system.sf_category           	nef_molecular_system
  _nef_molecular_system.sf_framecode          	nef_molecular_system

  loop_
    _nef_sequence.index
    _nef_sequence.chain_code
    _nef_sequence.sequence_code
    _nef_sequence.residue_name
    _nef_sequence.linking
    _nef_sequence.residue_variant
    _nef_sequence.cis_peptide

"""

def BuildSeqNEF(session):
  # Get sequence index
  # Sorting is included
  group_list = []    
  sequence_from_session = []
  for molecule in session.project.molecule_list():
    for group in molecule.group_list():
      sequence_from_session.append( (group.number, group.name[0:1]) )

  sequence = myseq.CheckSequence(sequence_from_session)
  
  if myseq.GapInSequence(sequence) == 1: # there is a gap
    tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
    sequence = myseq.LoadSeq(session, sequence) # this fills a gap
    if sequence == None:
      tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
      return ""

  content = ""
  iCur = 1
  for i in range(len(sequence)):
    seq = sequence[i]
    if i == 0: postfix = 'start'
    elif i == len(sequence)-1: postfix = 'end'
    else: postfix = 'middle'
    seqidx = seq[0]
    aaa = myseq.a2aaa(seq[1])
    
    line = '      %-4d  A %4d %3s %8s   .\n' % (iCur, seqidx, aaa, postfix)
    iCur += 1
    content = content + line
    
  content = content + '  stop_\nsave_\n'
  return (szSeqHeader + content)
  
def ExtractSeqNEF(session, read_in, chainID='A'):
  f = open(read_in, 'r')
  lines = f.readlines()
  f.close()
  
  iStart = 999999  
  iStart2 = 999999
  iEnd = -999999
  
  for i in range(len(lines)):
    line = lines[i]
    if line.strip() == 'save_nef_molecular_system':
      iStart = i
    elif (iStart < 999990) and (line.strip() == 'loop_'):
      iStart2 = i      
    elif (iStart < 999990) and (line.strip() == 'stop_'):
      iEnd = i
    if (iStart < 999990) and (iStart2 < 999990) and (iEnd > -999990):
      break 
  if (iStart2 > 999990) or (iEnd < -999990):
    tkMessageBox.showerror('Error', 'File is corrupted.')
    return ""
      
  newlines = lines[iStart2:iEnd]

  seqlines = ""
  for line in newlines:
    if line.strip() == '': continue
    try:
      if line.strip().split()[1] != chainID: continue
    except:
      continue
    if len(line.strip().split()) < 5: continue
    if line.strip().split()[4] not in ['start', 'middle', 'end']:
      continue
      
    seqlines = seqlines + '%s %s\n' % (line.strip().split()[3], line.strip().split()[2])
  
  return seqlines
  
  
szCSHeader = """
#===========================================================================
# Section 4
#
# Mandatory: Chemical shift table(s)
#===========================================================================

save_nef_chemical_shift_list_1

# All tags in this saveframe are mandatory, except for value_uncertainty.

  _nef_chemical_shift_list.sf_category            nef_chemical_shift_list
  _nef_chemical_shift_list.sf_framecode           nef_chemical_shift_list_1

  _nef_chemical_shift_list.atom_chem_shift_units  ppm

  loop_
      _nef_chemical_shift.chain_code
      _nef_chemical_shift.sequence_code
      _nef_chemical_shift.residue_name
      _nef_chemical_shift.atom_name
      _nef_chemical_shift.value
      _nef_chemical_shift.value_uncertainty
      _nef_chemical_shift.element
      _nef_chemical_shift.isotope_number

"""
def BuildShiftNEF(session):
  import pinelayout
  groups = []
  for condition in session.project.condition_list():
    for resonance in condition.resonance_list():
      aaa = myseq.a2aaa(resonance.group.symbol)
      if aaa == '': continue
      
      group = [resonance.group.number, aaa, resonance.atom.name, \
                resonance.frequency, resonance.deviation]
      groups.append(group)
  groups.sort()
     
  content = ""   
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
                  
    szAtom = group[2]
    if iAmb == 1: szAtom = szAtom + '%'
    if szAtom[0] == 'H': isot = 1
    elif szAtom[0] == 'C': isot = 13
    elif szAtom[0] == 'N': isot = 15
    elif szAtom[0] == 'P': isot = 31
    else: isot = 1
    line = "      A %4d %5s %5s %7.3f %6.3f %2s %2d\n" % \
            (group[0], group[1], szAtom, group[3], group[4],
              szAtom[0], isot)
    content = content + line
  content = content + '  stop_\nsave_\n'
  return (szCSHeader + content)

def ExtractShiftNEF(session, read_in, chainID = 'A'):  
  f = open(read_in, 'r')
  lines = f.readlines()
  f.close()
  
  iStart = 999999  
  iStart2 = 999999
  iEnd = -999999
  
  for i in range(len(lines)):
    line = lines[i]
    if line.strip().find('save_nef_chemical_shift_list_') != -1:
      iStart = i
    elif (iStart < 999990) and (line.strip() == 'loop_'):
      iStart2 = i      
    elif (iStart < 999990) and (line.strip() == 'stop_'):
      iEnd = i
    if (iStart < 999990) and (iStart2 < 999990) and (iEnd > -999990):
      break 
  if (iStart2 > 999990) or (iEnd < -999990):
    tkMessageBox.showerror('Error', 'File is corrupted.')
    return []
      
  newlines = lines[iStart2:iEnd]
  cslist = []
  for line in newlines:
    if line.strip() == '': continue
    splited = line.strip().split()
    try:
      if splited[0] != chainID: continue
    except:
      continue
    if len(splited) < 6: continue
    
    try:
      iSeqIdx = int(splited[1])
      szA = myseq.aaa2a(splited[2])
      if szA == 'X': continue
      
      szAtom = splited[3]
      szAtom = szAtom.replace("%", "")
      szAtom = szAtom.replace("X", "2")    
      szAtom = szAtom.replace("Y", "3")
      szAtom = szAtom.replace("CQ", "C")    
      szAtom = szAtom.replace("HN", "H")
      szAtom = szAtom.replace("HT1", "H")
      szAtom = szAtom.replace("HT2", "H")
      szAtom = szAtom.replace("HT3", "H")
      szAtom = szAtom.replace("Q", "H")    
      dCS = float(splited[4])
      
      cslist.append((iSeqIdx, szA, szAtom, dCS))
    except:
      continue  
  return cslist
  

szPLHeader = """
#=======================================================================
# Section 8
#
# Optional: Peak list(s)
#=======================================================================

save_nef_nmr_spectrum_$SPECNAME
  _nef_nmr_spectrum.sf_category           		nef_nmr_spectrum
  _nef_nmr_spectrum.sf_framecode              nef_nmr_spectrum_$SPECNAME
  _nef_nmr_spectrum.num_dimensions        		$DIMCOUNT
  _nef_nmr_spectrum.chemical_shift_list       nef_chemical_shift_list_1
  
  loop_
      _nef_spectrum_dimension.dimension_id
      _nef_spectrum_dimension.axis_unit
      _nef_spectrum_dimension.axis_code
      _nef_spectrum_dimension.spectrometer_frequency
      _nef_spectrum_dimension.spectral_width
      _nef_spectrum_dimension.value_first_point

      1  ppm  1H   500.139  10.4    9.9
      2  ppm 15N    98.37   30.7  127.0
      3  ppm  1H   500.139  14.2   11.8
  stop_  
"""

szPLHeader2 = """  
  loop_
      _nef_spectrum_dimension_transfer.dimension_1
      _nef_spectrum_dimension_transfer.dimension_2
      _nef_spectrum_dimension_transfer.transfer_type

      1 3 through-space
      2 3 onebond       
  stop_  
"""  

szPLHeader3 = """
  loop_
      _nef_peak.ordinal
      _nef_peak.peak_id
      _nef_peak.volume
      _nef_peak.volume_uncertainty
      _nef_peak.height
      _nef_peak.height_uncertainty
      _nef_peak.position_1
      _nef_peak.position_uncertainty_1
      _nef_peak.position_2
      _nef_peak.position_uncertainty_2
      _nef_peak.position_3
      _nef_peak.position_uncertainty_3
      _nef_peak.chain_code_1
      _nef_peak.sequence_code_1
      _nef_peak.residue_type_1
      _nef_peak.atom_name_1
      _nef_peak.chain_code_2
      _nef_peak.sequence_code_2
      _nef_peak.residue_type_2
      _nef_peak.atom_name_2
      _nef_peak.chain_code_3
      _nef_peak.sequence_code_3
      _nef_peak.residue_type_3
      _nef_peak.atom_name_3

 1  1 7.3E7 5.1E6 3.3E7 1.1E6  3.2 0.05 119.5 0.5 8.3 0.03 A 19 LEU HBY A 17 GLN N   A 17 GLN H
 2  1 7.3E7 5.1E6 3.3E7 1.1E6  3.2 0.05 119.5 0.5 8.3 0.03 A 20 CYS HBX A 17 GLN N   A 17 GLN H
 3  1 7.3E7 5.1E6 3.3E7 1.1E6  3.2 0.05 119.5 0.5 8.3 0.03 A 19 LEU HBY A 19 TYR N   A 19 TYR H
 4  1 7.3E7 5.1E6 3.3E7 1.1E6  3.2 0.05 119.5 0.5 8.3 0.03 A 20 CYS HBX A 19 TYR N   A 19 TYR H
 5  1 7.3E7 5.1E6 3.3E7 1.1E6  3.2 0.05 119.5 0.5 8.3 0.03 A 14 TRP HB3 A 18 PHE N   A 18 PHE H
 6  3 5.4E7 7.3E6 3.4E7 5.3E6  4.4 0.05 106.5 0.5 7.8 0.03 .  .   .   . A 15 GLY N   A 15 GLY H
 7  4 8.8E7 1.3E7 4.8E7 3.3E6  3.2 0.05 135.6 0.5 9.9 0.03 A 14 TRP HB3 A 14 TRP NE1 A 14 TRP HE1
 8  5 8.8E7 1.3E7 5.8E7 2.3E7  3.4 0.05 135.6 0.5 9.9 0.03 A 14 TRP HB2 A 14 TRP NE1 A 14 TRP HE1
 9  5 8.8E7 1.3E7 5.8E7 2.3E7  3.4 0.05 135.6 0.5 9.9 0.03 A 24 ASP HBY A 14 TRP NE1 A 14 TRP HE1
  stop_  
  
"""

def export_nef_seq(session):
  path = tkutil.save_file(session.tk, \
          "Save sequence to NMR Exchange File", \
          "nef_sparky_seq.nef")
  if path:
    content =  BuildSeqNEF(session)
    if content != '':
      f = open(path, 'w')
      f.write(szHeader)
      f.write(content)
      f.close()
      tkMessageBox.showinfo('Export to NEF', 'Saved.')
      return
    tkMessageBox.showerror('Export to NEF', 'Failed to build nef file.')      

def export_nef_seq_cs(session):
  path = tkutil.save_file(session.tk, \
          "Save sequence and shifts to NMR Exchange File", \
          "nef_sparky_seq_cs.nef")
  if path:
    content =  BuildSeqNEF(session)  
    content2 =  BuildShiftNEF(session)
    if content != '':
      f = open(path, 'w')
      f.write(szHeader)      
      f.write(content)
      f.write(content2)      
      f.close()
      tkMessageBox.showinfo('Export to NEF', 'Saved.')
      return
    tkMessageBox.showerror('Export to NEF', 'Failed to build nef file.')      
    
def export_nef_to_seq(session):
  file_opt = options = {}  
  options['defaultextension'] = '.nef'
  options['filetypes'] = [('NMR Exchange Format', '.nef')]
  options['title'] = 'Select NEF file to convert'  
  szFileName = tkFileDialog.askopenfilename(**file_opt)
  
  if szFileName == '':
    return
    
  content =  ExtractSeqNEF(session, szFileName)
  if content != '':
    path = tkutil.save_file(session.tk, \
      "Extract sequence from NMR Exchange File", \
      "extracted.seq")
    if path:
      f = open(path, 'w')
      f.write(content)
      f.close()
      tkMessageBox.showinfo('Exract .seq file', 'Saved.')
      return
    return  
  tkMessageBox.showerror('Export .seq file', 'Failed to read nef file.')      
  
def export_nef_to_rlist(session):    
  file_opt = options = {}  
  options['defaultextension'] = '.nef'
  options['filetypes'] = [('NMR Exchange Format', '.nef')]
  options['title'] = 'Select NEF file to convert'  
  szFileName = tkFileDialog.askopenfilename(**file_opt)
  
  if szFileName == '':
    return
    
  contentlist =  ExtractShiftNEF(session, szFileName)
  
  if len(contentlist) != 0:
    myseq.SaveSparkyResonance(session, contentlist)
    return
  tkMessageBox.showerror('Export .list file', 'Failed to read nef file.')      
    
  # peak list should be implemented
  #def build_nef_peak_list(session):
  #def export_nef_peak_list(session):
  #def read_nef_peak_list(session):
  #def write_sparky_peak_list(session):