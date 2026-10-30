# -----------------------------------------------------------------------------
# XEASY prot file support
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Dec 10, 2015
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
import os, os.path

# -----------------------------------------------------------------------------  
def SaveSparkyResonance(sparky_file, external_cs_list):   
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
    if dCS > 500.0: continue
    szLine = '%s%d   %s   %s %7.3f   0.0     0\n' % (szA, iSeqIdx, szAtom, szNuc, dCS)
    line_queue.append(szLine)
    
  f = open(sparky_file, 'w')
  for line in line_queue:
    f.write(line)
  f.close()   
# -----------------------------------------------------------------------------  
def GenerateXeasyProt(session):
  if session.project == None:
    tkMessageBox.showerror('Error', 'No active project exists.')
    return
  
  file_opt = options = {}  
  
  # read sequence
  if session.project != None:
      readsequence = myseq.ReadSequence(session)
        
  if len(readsequence) == 0:
    tkMessageBox.showerror('Error', 'Sequence file is not correct.')
    return
            
  options['defaultextension'] = '.prot'
  options['filetypes'] = [('XEASY prot', '.prot')]
  options['title'] = 'Select XEASY prot file'  
  prot_file = tkFileDialog.asksaveasfilename(**file_opt)
  
  if prot_file == '':
    return
    
  import shiftstats
  from tan import GetFreq, WGroup
  
  f = open(prot_file, 'w')
  iLineIdx = 1
  for (iCurIdx, szA) in readsequence:
    if szA == 'X': continue
    atm_list = shiftstats.atom_dict[szA]
    #group = '%s%d' % (szA, iCurIdx)
    for atm in atm_list:
      freq, dev = GetFreq(session, WGroup(szA, iCurIdx), atm)
      if freq > 1000: freq = 999.999
      if dev > 1000: dev = 999.999
      szLine = '%6d %7.3f %7.3f %7s %3d\n' % (iLineIdx, freq, dev, atm, iCurIdx)
      f.write(szLine)
      iLineIdx = iLineIdx + 1
  f.close()
  tkMessageBox.showinfo('XEASY prot', 'XEASY prot file saved.')
# -----------------------------------------------------------------------------  
def ConvertProtToSparky(session):
  file_opt = options = {}  
  options['defaultextension'] = '.prot'
  options['filetypes'] = [('XEASY prot', '.prot')]
  options['title'] = 'Select XEASY prot file'  
  prot_file = tkFileDialog.askopenfilename(**file_opt)
  
  if prot_file == '' or not os.path.exists(prot_file):
    return
    
  options['defaultextension'] = '.seq'
  options['filetypes'] = [('3-letter sequence', '.seq')]
  options['title'] = 'Select 3-letter sequence file'  
  seq_file = tkFileDialog.askopenfilename(**file_opt)
  
  if seq_file == '' or not os.path.exists(seq_file):
    return
    
  sparky_file = tkutil.save_file(session.tk, "Save to Sparky resonance file", "resonance.list")
  if sparky_file == '' or not sparky_file:
    return
    
  f = open(seq_file, 'r')
  seq_lines = f.readlines()
  f.close()  
  
  seq_list = []

  for i in range(0, 5000):
    seq_list.append([i, 'XXX'])
    
  if len(seq_list) == 0:
    tkMessageBox.showerror('Error', 'Sequence file is not correct.')
    return

  for line in seq_lines:
    splited = line.strip().split()
    if len(splited) < 2: continue
    if splited[0][0] == '#': continue
    try:
      seq_idx = int(splited[1])
      print seq_idx
    except:
      continue
      
    seq_list[seq_idx][1] = splited[0]          
  
  f = open(prot_file, 'r')
  cs_lines = f.readlines()
  f.close()
  
  cs_list = []
  for line in cs_lines:
    splited = line.strip().split()
    if len(splited) < 5: continue
    if splited[0][0] == '#': continue
    
    if seq_list[int(splited[4])][1] == 'XXX':
      tkMessageBox.showerror('Error', 'Sequence file is not correct.')
      return
      
    try:
      record = [int(splited[4]), myseq.aaa2a(seq_list[int(splited[4])][1]), splited[3], float(splited[1])]
      cs_list.append(record)
    except:
      continue
      
  if len(cs_list) == 0:
    tkMessageBox.showerror('Error', 'Prot file is not correct.')
    return        
    
  SaveSparkyResonance(sparky_file, cs_list)
  
  tkMessageBox.showinfo('Resonance List', 'Finished. Use two-letter-code rl to read-in')  
