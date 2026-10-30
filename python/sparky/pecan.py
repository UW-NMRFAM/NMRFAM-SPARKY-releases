# -----------------------------------------------------------------------------
# Pecan support
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: July 21, 2014
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import string
import os.path


# -----------------------------------------------------------------------------
AAA_dict = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
     'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N', 
     'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 
     'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}
A_dict = {'C': 'CYS', 'D': 'ASP', 'S': 'SER', 'Q': 'GLN', 'K': 'LYS',
     'I': 'ILE', 'P': 'PRO', 'T': 'THR', 'F': 'PHE', 'N': 'ASN', 
     'G': 'GLY', 'H': 'HIS', 'L': 'LEU', 'R': 'ARG', 'W': 'TRP', 
     'A': 'ALA', 'V':'VAL', 'E': 'GLU', 'Y': 'TYR', 'M': 'MET'}     
     
'''output is dict:
 {1: ("MET", "M", helix prob, strand prob, loop prob),
  2: ("SER", "S", helix prob, strand prob, loop prob)
  ...
 }
''' 
def aaa2a(szAAA):
  if len(szAAA) <> 3:
    return 'X'
  if not AAA_dict.has_key(szAAA.upper()):
    return "X"
  return AAA_dict[szAAA.upper()]

def a2aaa(szA):
  if len(szA) <> 1:
    return 'XXX'
  if not A_dict.has_key(szA.upper()):
    return "XXX"
  return A_dict[szA.upper()]
    
def ReadPecan(pecan_output):
  if not os.path.isfile(pecan_output):
    return {}
    
  f = open(pecan_output, 'r')    
  pecan_read = f.readlines()
  f.close()  
  bStart = 0
  
  dictReturn = {}
  
  for szLine in pecan_read:
    if bStart == 0:      
      ## look for "_PECAN.Helix_boundary_designator"
      print szLine
      if szLine.strip() == '_PECAN.Helix_boundary_designator':
        bStart = 1
        continue
      continue 
    if szLine == '': continue
    pszParsed = szLine.split()
    if len(pszParsed) <> 6: continue
    iSeqIdx = int(pszParsed[0])  
    szAAA = pszParsed[1]
    szA = aaa2a(szAAA)
    if szA == 'X': continue
    dSheet = float(pszParsed[2])  
    dHelix = float(pszParsed[3])  
    dLoop = 1.0 - dSheet - dHelix
    dictReturn[iSeqIdx] = (szAAA, szA, dHelix, dSheet, dLoop)
  
  return dictReturn  
    
