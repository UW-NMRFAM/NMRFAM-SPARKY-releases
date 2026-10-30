# -----------------------------------------------------------------------------
# My sequence module
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

import os
import tkutil
import sputil
import tkFileDialog
import pinelayout

# -----------------------------------------------------------------------------
AAA_dict = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
     'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
     'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W',
     'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}
A_dict = {'C': 'CYS', 'D': 'ASP', 'S': 'SER', 'Q': 'GLN', 'K': 'LYS',
     'I': 'ILE', 'P': 'PRO', 'T': 'THR', 'F': 'PHE', 'N': 'ASN',
     'G': 'GLY', 'H': 'HIS', 'L': 'LEU', 'R': 'ARG', 'W': 'TRP',
     'A': 'ALA', 'V':'VAL', 'E': 'GLU', 'Y': 'TYR', 'M': 'MET'}

Aline = 'ARNDCQEGHILKMFPSTWYVX'
Ponly = 'RNDQEHILKMFPSWYV'

NA_AAA_dict = {'ADE': 'A', 'GUA': 'G', 'CYT': 'C', 'URA': 'U', 'THY': 'T'}
NA_A_dict = {'A': 'ADE', 'G': 'GUA', 'C': 'CYT', 'U': 'URA', 'T': 'THY'}

'''output is dict:
 {1: ("MET", "M", phi, psi, dphi, dpsi, "Strong")
  ...
 }
'''
# ----------------------------------------------------------------------------
def aaa2na_aaa(szAAA):
  # ATGCU
  if szAAA == 'ALA': return 'ADE'
  if szAAA == 'THR': return 'THY'
  if szAAA == 'GLY': return 'GUA'
  if szAAA == 'CYS': return 'CYT'
  return 'XXX'
# ----------------------------------------------------------------------------
def aaa2a(szAAA):
  if len(szAAA) == 1:
    if A_dict.has_key(szAAA.upper()):
      return szAAA.upper()
  if len(szAAA) != 3:
    return 'X'
  if not AAA_dict.has_key(szAAA.upper()):
    return na_aaa2a(X)
  return AAA_dict[szAAA.upper()]
# ----------------------------------------------------------------------------
def a2aaa(szA):
  if len(szA) == 3:
    if AAA_dict.has_key(szA.upper()):
      return szA.upper()
  if len(szA) != 1:
    return 'XXX'
  if not A_dict.has_key(szA.upper()):
    return na_a2aaa(szA.upper())
  return A_dict[szA.upper()]
# ----------------------------------------------------------------------------
def na_aaa2a(szAAA):
  if len(szAAA) != 3:
    return 'X'
  if not NA_AAA_dict.has_key(szAAA.upper()):
    return "X"
  return NA_AAA_dict[szAAA.upper()]
# ----------------------------------------------------------------------------
def na_a2aaa(szA):
  if len(szA) != 1:
    return 'XXX'
  if not NA_A_dict.has_key(szA.upper()):
    return "XXX"
  return NA_A_dict[szA.upper()]

# ----------------------------------------------------------------------------
# sequence format is list of ....
# (1, 'A')
# (2, 'R') ......
def CheckSequence(sequence):
  # sort sequence
  iMin = 9999
  iMax = -9999
  iFirstIndex = -9999
  result_sequence = []

  for seq in sequence:
    try:
      temp = int(seq[0])
    except:
      continue
    if iMin > seq[0]:
      iMin = seq[0]
    if iMax < seq[0]:
      iMax = seq[0]

  iFirstIndex = iMin
  if iMin == 9999:
    return []

  for i in range(iMin, iMax+1):
    result_sequence.append( [i, 'X'] )
      
  for seq in sequence:
    if seq[1] == 'X': continue
    result_sequence[seq[0] - iMin][1] = seq[1]
    
  return result_sequence

# ----------------------------------------------------------------------------
def GapInSequence(sequence):
  for seq in sequence:
    if seq[1] == 'X': return 1
  return 0

# ----------------------------------------------------------------------------
def LoadSeq(session, sequence):
  import myseq

  # set sequences
  readsequence = ReadSequence(session)

  # try to fill the gap
  retSeq = FillSequenceGap(readsequence, sequence)
  return retSeq

# -----------------------------------------------------------------------------
# iMode:
#    0: template: shiftx or bmrb
#    1: template: your assignment
def ReadSequence2(template_cs_list):
  iTemMin = 9999
  iTemMax = -9999
  for group in template_cs_list:
    if group[0] < iTemMin: iTemMin = group[0]
    if group[1] > iTemMax: iTemMax = group[0]
  szTemSeq = ''

  # make fasta of temp
  retSeq = []
  for i in range(iTemMin, iTemMax+1):
    iFound = 0
    for group in template_cs_list:
      if group[0] == i:
        retSeq.append( (i, group[1]) )
        iFound = 1
        break
    if iFound == 0:
        retSeq.append( (i, 'X') )

  return retSeq
  # renumber regarding current assignment.
  # if fails, do not change.
  # return value is another list

# -----------------------------------------------------------------------------
def SaveSparkyResonance(session, external_cs_list):
  import tkutil
  path = tkutil.save_file(session.tk, 
                          "Save to Sparky resonance format (.list)", 
                          "Save to Sparky resonance file format (.list)")
  if not path: return


  line_queue = []
  for rec in external_cs_list:
    (iSeqIdx,  szA, szAtom, dCS) = rec
    if (szAtom[0] == 'C'):
      szNuc = '13C'
    elif (szAtom[0] == 'N'):
      szNuc = '15N'
    elif (szAtom[0] == 'H') or (szAtom[0] == 'Q') or (szAtom[0] == 'M'):
      szNuc = '1H'
    else:
      continue
    szLine = '%s%d   %s   %s %7.3f   0.0     0\n' % (szA, iSeqIdx, 
                                                    szAtom, szNuc, dCS)
    line_queue.append(szLine)

  f = open(path, 'w')
  for line in line_queue:
    f.write(line)
  f.close()
# -----------------------------------------------------------------------------
def GetExternalFreq(session, iSeqID, szA, szAtom, external_cs_list):
  for rec in external_cs_list:
    if rec[0] == iSeqID and rec[1] == szA and rec[2] == szAtom:
      return rec[3]

  # we need to look at pseudo-atoms
  # this only works for protons
  if not szAtom[:1] in ['H', 'Q', 'M']:
    return 9999
  # HN
  if szAtom == 'H' or szAtom == 'HN':
    for rec in external_cs_list:
      if rec[0] == iSeqID and rec[1] == szA and \
          (rec[2] == 'HN' or rec[2] == 'H'):
        return rec[3]
    return 9999

  # processing pseudo atoms
  prefixes = ['H','Q','M']
  if pinelayout.pseudo_layout.has_key(szA) and len(szAtom) > 1:
    for prefix in prefixes:
      szPseudoAtom = prefix + szAtom[1:len(szAtom)]
      for rec in external_cs_list:
        if rec[0] == iSeqID and rec[1] == szA and rec[2] == szPseudoAtom:
          return rec[3]
  # processing sub-level
  postfixes = ['1','2','3']
  if pinelayout.pseudo_layout.has_key(szA) and len(szAtom) > 1:
    for postfix in postfixes:
      szPseudoAtom = szAtom + postfix
      for rec in external_cs_list:
        if rec[0] == iSeqID and rec[1] == szA and rec[2] == szPseudoAtom:
          return rec[3]
  return 9999
# -----------------------------------------------------------------------------
def RenumberSeqIndices(session):
  renumber_dialog = sputil.the_dialog(renum_seq, session)
  renumber_dialog.show_window(1)
  renumber_dialog.update()

class renum_seq(tkutil.Dialog, tkutil.Not_Stoppable):
  def __init__(self, session):
    self.session = session

    import Tkinter
    import tkMessageBox
    tkutil.Dialog.__init__(self, session.tk, 'Renumber sequence indices')
    label = Tkinter.Label(self.top, text = 'Set the first index of the sequence.')
    label.pack()
    v = Tkinter.StringVar(self.top)
    self.v = v
    self.ebIndex = Tkinter.Entry(self.top, bd = 1, textvariable=v)
    self.ebIndex.pack()

    br = tkutil.button_row(self.top,
                          ('Okay', self.okay_cb),
                          ('Cancel', self.close_cb),
               )
    br.frame.pack(side = 'top', anchor = 'w')

  def update(self):
    # first index
    iMin = 9999
    iMax = -9999
    session = self.session
    v = self.v

    for condition in session.project.condition_list():
      for resonance in condition.resonance_list():
        group = resonance.group
        if group.number < iMin:
          try:
            iMin = int(group.number)
          except:
            pass
        if group.number > iMax:
          try:
            iMax = int(group.number)
          except:
            pass
    self.iMin = iMin
    v.set('%d' % (iMin))

  def okay_cb(self):
    import tkMessageBox
    szMin = self.ebIndex.get()
    session = self.session
    iMin = self.iMin
    try:
      iUserMin = int(szMin)
    except:
      iUserMin = -9999
    if iUserMin == -9999:
      tkMessageBox.showerror('Error', 'Please type a number.')
      return
    if iUserMin < 1:  
      tkMessageBox.showerror('Error', 'Minimum should be larger than zero.')
      return

    iGap = iUserMin - iMin

    for spectrum in session.project.spectrum_list():
      for peak in spectrum.peak_list():
        #if peak.is_assigned != 1: continue
        try:
          pAssign = sputil.parse_assignment(peak.assignment)  # ((M1, CA), (
        except:
          continue
        try:
          for i in range(len(pAssign)):  # (M1, CA)
            tAssign = pAssign[i]
            try:
              szSeq = filter(str.isalpha, tAssign[0])
              iSeq = int(filter(str.isdigit, tAssign[0]))
            except:          
              continue
            iSeq = iSeq + iGap
            nAssign = '%s%d' % (szSeq, iSeq)
            peak.assign(i, nAssign, tAssign[1])
        except:
          pass
    # Mary Clay from SJCH suggestion.        
    # Check to see if session.project.save_path + '.seq' exist 
    # and update or create it
    seq_path = session.project.save_path + '.seq'
    if os.path.exists(seq_path):
      result = tkMessageBox.askokcancel('Stored sequence file found.', \
                'Do you want to overwrite to stored sequence file?')
      if result is True:
        f = open(seq_path,'r')
        lines = f.readlines()
        f.close()
        text = ''
        for line in lines:
          sp = line.strip().split()
          if len(sp) != 2: continue
          try:
            text = text + '%-4s %4d\n' % (sp[0], int(sp[1])+iGap)
          except:
            continue
        f = open(seq_path,'w')
        f.write(text)
        f.close()

    tkMessageBox.showinfo('Finished', \
        'Renumbered. Type dr to remove unused resonances.')
    self.close_cb()

# -----------------------------------------------------------------------------
def PineSeqFormatting(session):
  readSeq = ReadSequence(session)
  if len(readSeq) == 0: return
  file_opt = options = {}
  options['defaultextension'] = '.seq'
  options['filetypes'] = [('3-letter-code sequence file without indices', '.txt'), ('1-letter-code sequence file without indices', '.TXT')]
  options['title'] = 'Name your new sequence file in PINE format'
  szFileName = tkFileDialog.asksaveasfilename(**file_opt)

  if szFileName == '':
    return
  f = open(szFileName, 'w')
  if f == None:
    return

  userseq = ''
  for seq in readSeq:
    userseq = userseq + seq[1]
    if szFileName.endswith(".txt"):
      szAAA = a2aaa(seq[1].upper())
      f.write(szAAA+'\n')
    else:
      f.write(seq[1])
  f.close()
  import tkMessageBox
  tkMessageBox.showinfo('Finished', 'PINE sequence formatting finished: ' + userseq)
# -----------------------------------------------------------------------------
def GetBiomoleculeTypeByFasta(fasta):
  for i in range(len(Ponly)):
    if fasta.find(Ponly[i]) != -1:
      return 'p'
  return 'n'
  
# -----------------------------------------------------------------------------
# Read Sequence File
# isThree
#   1: three-letter
#   0: fasta
# return is list of (1, 'A')
def ReadSequence(session):

  # check if sequence file exists
  try:
    persist_path = session.project.save_path + '.seq'
  except:
    persist_path = ''

  szFileName = ''
  import tkMessageBox
  if os.path.exists(persist_path):
    result = tkMessageBox.askokcancel('Stored sequence file found.', 
                        'Do you want to use stored sequence file?')
    if result is True:
      szFileName = persist_path

  if not os.path.exists(szFileName):
    file_opt = options = {}
    options['defaultextension'] = '.seq'
    options['filetypes'] = [('3-letter-code sequence file with indices', '.seq'), ('1-letter-code sequence file', '.fasta'), ('3-letter-code sequence file without indices', '.txt')]
    options['title'] = 'Select a sequence file to read'
    szFileName = tkFileDialog.askopenfilename(**file_opt)

  if szFileName == '':
    return []
  f = open(szFileName, 'r')
  if f == None:
    return []

  if szFileName.endswith(".seq") or szFileName.endswith(".SEQ") or szFileName.endswith(".Seq"):
    isThree = 1
  elif szFileName.endswith(".txt") or szFileName.endswith(".TXT") or szFileName.endswith(".Txt"):
    isThree = 2
  else:
    isThree = 0

  pszLines = f.readlines()
  f.close()

  # set sequences
  readsequence = []

  # three letter code
  if isThree > 0:
    iFirstIdx = -9999
    iCurIdx = -9999
    iType = 0
    for szLine in pszLines:
      if szLine == '': continue
      if szLine.strip()[:1] == '#': continue

      szSplited = szLine.split()
      if len(szSplited) == 2 and iFirstIdx == -9999:
        try:
          iFirstIdx = int(szSplited[0])
          iType = 0
        except:
          try:
            iFirstIdx = int(szSplited[1])
            iType = 1
          except:
            iFirstIdx = 1
            iType = 2
        iCurIdx = iFirstIdx
      elif iFirstIdx == -9999:
        iFirstIdx = 1
        iCurIdx = iFirstIdx
        iType = 1

      if iType == 0:  szA = aaa2a(szSplited[1].upper())
      else:           szA = aaa2a(szSplited[0].upper())

      readsequence.append( [iCurIdx, szA] )
      iCurIdx = iCurIdx + 1
  # one letter code
  else:
    iFirstIdx = 1
    iCurIdx = 1
    for szLine in pszLines:
      if szLine == '': continue
      if szLine.strip()[:1] == '#': continue
      if szLine.strip()[:1] == '>': continue
      for szA in szLine:
        szAAA = a2aaa(szA)
        if szAAA == 'XXX': continue
        readsequence.append( [iCurIdx, szA] )
        iCurIdx = iCurIdx + 1


  sort_list = sorted(readsequence, key=getFirstKey)

  if persist_path != '':
    WriteSequenceToFile(persist_path, sort_list)

  return sort_list
# -----------------------------------------------------------------------------
def WriteSequenceToFile(szFileName, readsequence):
  fasta = ''
  for i in range(len(readsequence)):
    fasta = fasta + readsequence[i][1]
  bt =  GetBiomoleculeTypeByFasta(fasta)
  try:
    f = open(szFileName, 'w')
    for (iCurIdx, szA) in readsequence:
      szAAA = a2aaa(szA)
      if bt == 'n': szAAA = aaa2na_aaa(szAAA)
      f.write('%s %5d\n' % (szAAA, iCurIdx))
      iCurIdx = iCurIdx + 1
    f.close()
  except:
    pass
# -----------------------------------------------------------------------------
def getFirstKey(item):
  return item[0]

# -----------------------------------------------------------------------------
# Read Sequence from File
# isThree
#   1: three-letter
#   0: fasta
# return is list of (1, 'A')
def ReadSequenceFromFile(szFileName):
  if szFileName == '':
    return []
  f = open(szFileName, 'r')
  if f == None:
    return []


  if szFileName.endswith(".seq") or szFileName.endswith(".SEQ") or szFileName.endswith(".Seq"):
    isThree = 1
  elif szFileName.endswith(".txt") or szFileName.endswith(".TXT") or szFileName.endswith(".Txt"):
    isThree = 2
  else:
    isThree = 0

  pszLines = f.readlines()
  f.close()

  # set sequences
  readsequence = []

  # three letter code
  if isThree > 0:
    iFirstIdx = -9999
    iCurIdx = -9999
    iType = 0
    for szLine in pszLines:
      if szLine == '': continue
      if szLine.strip()[:1] == '#': continue

      szSplited = szLine.split()
      if len(szSplited) == 2 and iFirstIdx == -9999:
        try:
          iFirstIdx = int(szSplited[0])
          iType = 0
        except:
          try:
            iFirstIdx = int(szSplited[1])
            iType = 1
          except:
            iFirstIdx = 1
            iType = 2
        iCurIdx = iFirstIdx
      elif iFirstIdx == -9999:
        iFirstIdx = 1
        iCurIdx = iFirstIdx
        iType = 1

      if iType == 0:
        szA = aaa2a(szSplited[1].upper())
      else:
        szA = aaa2a(szSplited[0].upper())
      readsequence.append( (iCurIdx, szA) )
      iCurIdx = iCurIdx + 1
  # one letter code
  else:
    iFirstIdx = 1
    iCurIdx = 1
    for szLine in pszLines:
      if szLine == '': continue
      if szLine.strip()[:1] == '#': continue
      if szLine.strip()[:1] == '>': continue
      for szA in szLine:
        szAAA = a2aaa(szA)
        if szAAA == 'XXX': continue
        readsequence.append( (iCurIdx, szA) )

        iCurIdx = iCurIdx + 1
  sort_list = sorted(readsequence, key=getFirstKey)
  return sort_list
# -----------------------------------------------------------------------------
# accepts ( (1,'A' ) and returns same
def FillSequenceGap(cur_sequence, template_sequence):
  # try to fill the gap
  iDiff = -9999
  iStart = -9999
  szReadSeq = ''

  for i in range(len(cur_sequence)):
    szReadSeq = szReadSeq + cur_sequence[i][1]

  iUserSeqFirst = template_sequence[0][0]
  szUserSeq = ''
  for i in range(len(template_sequence)):
    szUserSeq = szUserSeq + template_sequence[i][1]

  # find 10->4 continuous sequences...
  for j in range(7):
    d = 10-j
    if len(template_sequence)-d < 1: continue
    for i in range(len(template_sequence)-d):
      szUserPartSeq = szUserSeq[i: i+d]
      iDiff = szReadSeq.find(szUserPartSeq)
      if iDiff != -1: 
        iStart = i
        break
    if iDiff != -1: break
    
  if iDiff == -1: return None
  
  retSeq = []
  
 
  for i in range(len(szReadSeq)):
    retSeq.append( (iUserSeqFirst+iStart-iDiff+i, szReadSeq[i]) )


  # there are a few sequences at N'
  #if iDiff != 0: 
  #  for i in range(iDiff-iStart):
  #    retSeq.append( (iUserSeqFirst-iDiff+iStart+i, szReadSeq[i]) )

  #for i in range(len(template_sequence)):
  #  seq = template_sequence[i]
  #  if seq[1] != 'X':
  #    retSeq.append(seq)
  #    continue
  #  if (i+iDiff-iStart) > (len(cur_sequence)-1):
  #    return retSeq # end here
  #  retSeq.append( (seq[0], szReadSeq[i+iDiff]) )
    
  # there are a few sequences at C'
  #if len(szReadSeq) > len(szUserSeq)-iDiff+iStart:
  #  for i in range(len(szReadSeq) - (len(szUserSeq)+iDiff)):
  #    retSeq.append( (iUserSeqFirst+len(szUserSeq)+i, szReadSeq[len(szUserSeq)+iDiff-iStart+i] ) )
  return retSeq

# -----------------------------------------------------------------------------
# Build Sequence from resonance stored in NMRFAM-SPARKY
# iMode:
#   0: 'AXSAGADSCBSD' -> regular 1-letter-code
#   1: ('A', 'S', 'X'...) -> 1-letter-code in list
#   2: ('ALA', 'SER', 'XXX'....) -> 3-letter-code in list
#   3: ( (1,'A')) -> my group list
#   4: ( ('A',1)) -> my group list, used in tan.py
def BuildSequence(session, iMode):
  sequence_from_session = []

  iMin = 9999
  iMax = -9999
  for molecule in session.project.molecule_list():
    for group in molecule.group_list():
      sequence_from_session.append( (group.number, group.name[0]) )
      if group.number < iMin:
        try:
          iMin = int(group.number)
        except:
          pass
      if group.number > iMax:
        try:
          iMax = int(group.number)
        except:
          pass

  szSequence = ''
  sequence_list = []

  for i in range(iMin, iMax+1):
    iFound = 0
    for seq_group in sequence_from_session:
      if seq_group[0] != i: continue
      if iMode == 0:
        szSequence = szSequence + seq_group[1]
      elif iMode == 1:
        sequence_list.append(seq_group[1])
      elif iMode == 2:
        szSequence = szSequence + seq_group[1]
        aaa = a2aaa(seq_group[1])
        sequence_list.append(aaa)
      elif iMode == 3:
        sequence_list.append( (seq_group[0], seq_group[1]) )
      elif iMode == 4:
        sequence_list.append( (seq_group[1], seq_group[0]) )
      iFound = 1
    if iFound != 1:
      if iMode == 0:
        szSequence = szSequence + 'X'
      elif iMode == 1:
        sequence_list.append('X')
      elif iMode == 2:
        sequence_list.append('XXX')
      elif iMode == 3:
        sequence_list.append( (seq_group[0], 'X') )
      elif iMode == 4:
        sequence_list.append( ('X', seq_group[0]) )
      iFound = 1
  if iMode == 2: # treat N.A.
    bt = GetBiomoleculeTypeByFasta(szSequence)    
    if bt == 'n':
      for i in range(len(sequence_list)):
        aaa = sequence_list[i]
        sequence_list[i] = aaa2na_aaa(aaa)
  return sequence_list

# -----------------------------------------------------------------------------
# Build chemical shift list in NMRFAM-SPARKY
# Seq ID, Seq ID, Seq, Atom, Atom type, Isotop, CS, CS_Dev, 2
def BuildResonance(session):
  groups = []
  fasta = ''
  for condition in session.project.condition_list():
    for resonance in condition.resonance_list():
      if resonance == None: continue
      if resonance.group == None: continue
      if resonance.group.number == None: continue
      aaa = a2aaa(resonance.group.symbol)
      if aaa == '': continue

      if resonance.atom.name.find('_s') != -1: continue # this is simulated assignment
      fasta = fasta + resonance.group.symbol
      atom_type = resonance.atom.name[0:1]
      if (atom_type == 'Q') or (atom_type == 'M'): atom_type = 'H'
      isotope = 1
      if atom_type == 'C': isotope = 13
      elif atom_type == 'N': isotope = 15
      elif atom_type == 'P': isotope = 31

      group = [resonance.group.number, aaa, resonance.atom.name,
              atom_type, isotope, resonance.frequency, resonance.deviation]
      groups.append(group)
  bt = GetBiomoleculeTypeByFasta(fasta)
  if bt == 'n':
    for i in range(len(groups)):
      groups[i][1] = aaa2na_aaa(groups[i][1])
  groups.sort()
  return groups

# -----------------------------------------------------------------------------
# Get attached heavy atom from protons.
#
# This dictionary is Mary Clay's
HeavyAtomDict = {
'A': ['CA', 'CB'],
'C': ['CA', 'CB', 'N'],
'E': ['CA', 'CB', 'CD', 'CG'],
'D': ['CA', 'CB', 'CG'],
'G': ['CA', 'N'],
'F': ['CA', 'CB', 'CD1', 'CD2', 'CE1', 'CE2', 'CG', 'CZ'],
'I': ['CA', 'CB', 'CD1', 'CG1', 'CG2'],
'H': ['CA', 'CB', 'CD2', 'CE1', 'CG', 'ND1', 'NE2'],
'K': ['CA', 'CB', 'CD', 'CE', 'CG', 'NZ', 'QZ'],
'M': ['CA', 'CB', 'CE', 'CG'], 
'L': ['CA', 'CB', 'CD1', 'CD2', 'CG'], 
'N': ['CA', 'CB', 'CG', 'N', 'ND2'], 
'P': ['CA', 'CB', 'CD', 'CG'], 
'Q': ['CA', 'CB', 'CD', 'CG', 'N', 'NE2'], 
'R': ['CA', 'CB', 'CD', 'CG', 'CZ', 'NE', 'NH1', 'NH2'], 
'S': ['CA', 'CB'], 
'T': ['CA', 'CB', 'CG2'], 
'W': ['CA', 'CB', 'CD1', 'CD2', 'CE2', 'CE3', 'CG', 'CH2', 'CZ2', 'CZ3', 'NE1'], 
'V': ['CA', 'CB', 'CG1', 'CG2'], 
'Y': ['CA', 'CB', 'CD1', 'CD2', 'CE1', 'CE2', 'CG', 'CZ']} 


def GetAttachedHeavyAtom(szA, szAtom):
  if (szAtom == "HN") or (szAtom == "H") or ("HT" in szAtom):
    return "N"

  if len(szA) == 3:
    szA = aaa2a(szA.upper())

  if len(szAtom) < 2:
    return ""

  if szAtom[1] == "A": return "CA"
  if szAtom[1] == "B": return "CB"

  if szA == "R":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "D": return "CD"
    if szAtom[1] == "Z": return "CZ"
    if szAtom[1] == "E": return "NE"
    if szAtom[1] == "H":
      if len(szAtom) == 2: return "NH"
      if szAtom[2] == "1": return "NH1"
      if szAtom[2] == "2": return "NH2"
  elif szA == "N":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "D": return "ND2"
  elif szA == "D":
    if szAtom[1] == "G": return "CG"
  elif szA == "Q":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "E": return "NE2"
  elif szA == "E":
    if szAtom[1] == "G": return "CG"
  elif szA == "H":
    if szAtom[1] == "G": return "CG"
    if len(szAtom) < 3: return ""
    if szAtom[1] == "D" and szAtom[2] == "2": return "CD2"
    if szAtom[1] == "D" and szAtom[2] == "1": return "NE1"
    if szAtom[1] == "E" and szAtom[2] == "1": return "CE1"
    if szAtom[1] == "E" and szAtom[2] == "2": return "NE2"
  elif szA == "I":
    if szAtom[1] == "G" and len(szAtom) == 2: return "CG"
    if szAtom[1] == "D" and len(szAtom) == 2: return "CD"
    if len(szAtom) < 3: return ""
    if szAtom[1] == "G" and szAtom[2] == "1": return "CG1"
    if szAtom[1] == "G" and szAtom[2] == "2": return "CG2"
    if szAtom[1] == "D" and szAtom[2] == "1": return "CD1"
  elif szA == "L":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "D" and len(szAtom) == 2: return "CD"
    if len(szAtom) < 3: return ""
    if szAtom[1] == "D" and szAtom[2] == "1": return "CD1"
    if szAtom[1] == "D" and szAtom[2] == "2": return "CD2"
  elif szA == "K":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "D": return "CD"
    if szAtom[1] == "E": return "CE"
    if szAtom[1] == "Z": return "NZ"
  elif szA == "M":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "E": return "CE"
  elif szA == "F":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "D" and len(szAtom) == 2: return "CD"
    if szAtom[1] == "E" and len(szAtom) == 2: return "CE"
    if len(szAtom) < 3: return ""
    if szAtom[1] == "D" and szAtom[2] == "1": return "CD1"
    if szAtom[1] == "D" and szAtom[2] == "2": return "CD2"
    if szAtom[1] == "E" and szAtom[2] == "1": return "CE1"
    if szAtom[1] == "E" and szAtom[2] == "2": return "CE2"
    if szAtom[1] == "Z": return "CZ"
  elif szA == "P":
    if szAtom[1] == "G" and len(szAtom) == 2: return "CG"
    if szAtom[1] == "D" and len(szAtom) == 2: return "CD"
  elif szA == "T":
    if len(szAtom) < 3: return ""
    if szAtom[1] == "G" and szAtom[2] == "2": return "CG2"
  elif szA == "W":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "D" and len(szAtom) == 2: return "CD"
    if szAtom[1] == "E" and len(szAtom) == 2: return "CE"
    if szAtom[1] == "Z" and len(szAtom) == 2: return "CZ"
    if szAtom[1] == "H" and len(szAtom) == 2: return "CH"
    if len(szAtom) < 3: return ""
    if szAtom[1] == "D" and szAtom[2] == "1": return "CD1"
    if szAtom[1] == "D" and szAtom[2] == "2": return "CD2"
    if szAtom[1] == "E" and szAtom[2] == "1": return "NE1"
    if szAtom[1] == "E" and szAtom[2] == "2": return "CE2"
    if szAtom[1] == "E" and szAtom[2] == "3": return "CE3"
    if szAtom[1] == "Z" and szAtom[2] == "1": return "CZ1"
    if szAtom[1] == "Z" and szAtom[2] == "2": return "CZ2"
    if szAtom[1] == "Z" and szAtom[2] == "3": return "CZ3"
    if szAtom[1] == "H" and szAtom[2] == "1": return "CH1"
    if szAtom[1] == "H" and szAtom[2] == "2": return "CH2"
  elif szA == "Y":
    if szAtom[1] == "G": return "CG"
    if szAtom[1] == "D" and len(szAtom) == 2: return "CD"
    if szAtom[1] == "E" and len(szAtom) == 2: return "CE"
    if len(szAtom) < 3: return ""
    if szAtom[1] == "D" and szAtom[2] == "1": return "CD1"
    if szAtom[1] == "D" and szAtom[2] == "2": return "CD2"
    if szAtom[1] == "E" and szAtom[2] == "1": return "CE1"
    if szAtom[1] == "E" and szAtom[2] == "2": return "CE2"
  elif szA == "V":
    if szAtom[1] == "G" and len(szAtom) == 2: return "CG"
    if len(szAtom) < 3: return ""
    if szAtom[1] == "G" and szAtom[2] == "1": return "CG1"
    if szAtom[1] == "G" and szAtom[2] == "2": return "CG2"
  return ""
