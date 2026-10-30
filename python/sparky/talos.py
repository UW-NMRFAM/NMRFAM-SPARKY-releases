# -----------------------------------------------------------------------------
# Talos support
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Feb 20, 2020
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import myseq
import string
import os.path
import tkMessageBox
import tkFileDialog

# ----------------------------------------------------------------------------
def ReadTalos(talos_output):
  if not os.path.isfile(talos_output):
    return {}
    
  f = open(talos_output, 'r')    
  talos_read = f.readlines()
  f.close()  
  
  iTalosVer = -1  # -1: Not defined, 0: original, 1: TALOS+, 2: TALOS-N
  bStart = 0
  
  dictReturn = {}
  for szLine in talos_read:
    pszParsed = szLine.split()
    if len(pszParsed) < 9: continue
    if bStart == 0:      
      ## look for "FORMAT %4d %s %8.3f %8.3f ......."
      if pszParsed[0] == 'FORMAT':
        bStart = 1
        continue
      continue  
        
    if len(pszParsed) == 9:  iTalosVer = 0
    elif len(pszParsed) == 10: iTalosVer = 1
    elif len(pszParsed) == 11: iTalosVer = 2
    else: continue
              
    iSeqIdx = int(pszParsed[0])  
    szA = pszParsed[1]
    szAAA = myseq.a2aaa(szA)
    if szAAA == 'XXX': continue
        
    dPhi = float(pszParsed[2])  
    dPsi = float(pszParsed[3])  
    dPhiDev = float(pszParsed[4])  
    dPsiDev = float(pszParsed[5])  
    szConf = pszParsed[8+iTalosVer] # Good, Strong, Generous

    dictReturn[iSeqIdx] = (szAAA, szA, dPhi, dPsi, dPhiDev, dPsiDev, szConf)
  
  return dictReturn  
# ----------------------------------------------------------------------------  
def export_talos(session):
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
      return
      
  import tkutil    
  path = tkutil.save_file(session.tk, "Save TALOS-N input file", "Save TALOS-N input file")
  if not path: return
  if WriteTalos(session, path, sequence) == 0:
    tkMessageBox.showinfo('TALOS', 'Error writing TALOS-N file.') 
  else:  
    #if tkMessageBox.askyesno('Export','Finished. Do you want to run TALOS-N web server?'):
    import webbrowser
    webbrowser.open('http://spin.niddk.nih.gov/bax/nmrserver/talosn/')

# ----------------------------------------------------------------------------  
def export_ncspc(session):
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
      return
      
  import tkutil
  path = tkutil.save_file(session.tk, "Save TALOS-N file for ncSPC", "Save TALOS-N file for ncSPC")
  if not path: return
  if WriteTalos(session, path, sequence) == 0:
    tkMessageBox.showinfo('ncSCP', 'Error writing TALOS-N file.') 
  else:  
    #if tkMessageBox.askyesno('Export','Finished. Do you want to run TALOS-N web server?'):
    import webbrowser
    webbrowser.open('http://nmr.chem.rug.nl/ncSPC/cgi-bin/start_session_file.py')
    
# ----------------------------------------------------------------------------
# Generate TALOS
def GenerateTalos(session, sequence):
  if len(sequence) == 0:
    return ''    # 0 is false
    
  line_queue = []
  line_queue.append('REMARK NMRFAM-SPARKY generated TALOS input file\n\n')  
  talos_atoms = ['HA', 'HA2', 'HA3', 'C', 'CA', 'CB', 'N', 'HN']
  
  # create DATA SEQUENCE
  seq = sequence[0]
  iFirstIdx = seq[0]
  line_queue.append('DATA FIRST_RESID %d\n\n' % (iFirstIdx))
  szSeq = 'DATA SEQUENCE '
  for i in range(len(sequence)):
    szSeq  = szSeq + sequence[i][1]
    if (i+1) % 10 == 0: szSeq = szSeq + ' '
    if (i+1) % 50 == 0 and i != len(sequence)-1: szSeq = szSeq + '\nDATA SEQUENCE '

  line_queue.append(szSeq)
  line_queue.append('\n\nVARS   RESID RESNAME ATOMNAME SHIFT\n')
  line_queue.append('FORMAT %4d   %1s     %4s      %8.3f\n\n')  
    
  # add chemical shifts  
  szOutput = ''
  try:
    for seq in sequence:  
      for atom in talos_atoms:
        for condition in session.project.condition_list():
          group_name = '%s%d' % (seq[1], seq[0])
          if atom == 'HN' or atom == 'H':
            resonance = condition.find_resonance(group_name, 'HN')
            if resonance == None:
              resonance = condition.find_resonance(group_name, 'H')          
          else:
            resonance = condition.find_resonance(group_name, atom)
          if resonance == None: continue
          if atom == 'HN' or atom == 'H':            
            line_queue.append('%4d %1s %4s %8.3f\n' % (seq[0], seq[1], 'HN', resonance.frequency))
          else:
            line_queue.append('%4d %1s %4s %8.3f\n' % (seq[0], seq[1], atom, resonance.frequency))

    #f = open(talos_input, 'w')
    for line in line_queue:
      #f.write(line)
      szOutput = szOutput + line
    #f.close()
  except:
    return ''
  #return 1
  return szOutput
  
# ----------------------------------------------------------------------------
# Check Sequence needs to be called before this  
def WriteTalos(session, talos_input, sequence):
  if len(sequence) == 0:
    return 0    # 0 is false
    
  szOutput = GenerateTalos(session, sequence)  
  if szOutput == '': return 0
  f = open(talos_input, 'w')
  f.write(szOutput)
  f.close()
  
  return 1  
  
# ----------------------------------------------------------------------------
def make_talosn_ss_ndpplot(file_name, ss_list):
  iMin = ss_list[0][0]
  iMax = ss_list[-1][0]
  f = open(file_name, 'w')
  f.write('[GENERAL_START]\n')
  f.write('TITLE=TALOS-N secondary structure prediction\n')
  f.write('XLABEL=Residue Number\n')    
  f.write('YLABEL=Propensity\n')        
  f.write('XMIN=%d\n' % iMin)
  f.write('XMAX=%d\n' % iMax)
  f.write('YMIN=-1.0\n')
  f.write('YMAX=1.0\n')
  f.write('XSCALE=INT\n')
  window_width = min(max(len(ss_list) * 5 + 500, 1000), 2000)
  f.write('WINDOW_WIDTH=%d\n' % (window_width))
  f.write('[GENERAL_END]\n')
 
  # Helix
  f.write('[SERIES1_START]\n')
  f.write('NAME=Helix\n')
  f.write('PLOTTYPE=BAR\n')
  f.write('COLORCOUNT=10\n')
  f.write('DATACOUNT=%d\n' % (len(ss_list)))
  for i in range(1, 11):
    f.write('COLOR_%d=%d,%d,%f,%f,%d_255_%d\n' % (i, iMin, iMax, float(i)*0.1-0.1,float(i)*0.1,275-25*i,275-25*i))
  for i in range(iMin, iMax+1):
    #if ss_list[i-iMin][3] == 'H' or ss_list[i-iMin][3] == 'h':
    f.write('DATA_%d=%d,%s,0,%s%d\n' % (i-iMin+1, i, ss_list[i-iMin][2], ss_list[i-iMin][1], i))
    #else:
    #  f.write('DATA_%d=%d,%f,0,%s%d\n' % (i-iMin+1, i, 0.0, ss_list[i-iMin][1], i))
  f.write('[SERIES1_END]\n')

  # Strand
  f.write('[SERIES2_START]\n')
  f.write('NAME=Strand\n')
  f.write('PLOTTYPE=BAR\n')
  f.write('COLORCOUNT=10\n')
  f.write('DATACOUNT=%d\n' % (len(ss_list)))
  for i in range(1, 11):
    f.write('COLOR_%d=%d,%d,%f,%f,%d_%d_255\n' % (i, iMin, iMax, -0.1*float(i),0.1-float(i)*0.1,275-25*i,275-25*i))  

  for i in range(iMin, iMax+1):
    #if ss_list[i-iMin][3] == 'E' or ss_list[i-iMin][3] == 'e':
    f.write('DATA_%d=%d,-%s,0,%s%d\n' % (i-iMin+1, i, ss_list[i-iMin][3], ss_list[i-iMin][1], i))
    #else:
    #  f.write('DATA_%d=%d,%f,0,%s%d\n' % (i-iMin+1, i, 0.0, ss_list[i-iMin][1], i))
  f.write('[SERIES2_END]\n')

  ## middle line
  f.write('[SERIES3_START]\n')
  f.write('NAME=Middle\n')
  f.write('PLOTTYPE=LINE\n')
  f.write('COLORCOUNT=1\n')
  f.write('DATACOUNT=2\n')  
  f.write('COLOR_1=%d,%d,%f,%f,SILVER\n' % (iMin, iMax, -1.0,1.0))
  f.write('DATA_1=%d,0\n' % (iMin))
  f.write('DATA_2=%d,0\n' % (iMax))  
  f.write('[SERIES3_END]\n')  
  f.close()
  
def make_talosn_s2_ndpplot(file_name, s2_list):
  iMin = s2_list[0][0]
  iMax = s2_list[-1][0]
  f = open(file_name, 'w')
  f.write('[GENERAL_START]\n')
  f.write('TITLE=TALOS-N RCI-S2 prediction\n')
  f.write('XLABEL=Residue Number\n')    
  f.write('YLABEL=RCI-S2 Order Parameter\n')        
  f.write('XMIN=%d\n' % iMin)
  f.write('XMAX=%d\n' % iMax)
  f.write('YMIN=0\n')
  f.write('YMAX=1.0\n')
  f.write('XSCALE=INT\n')
  window_width = min(max(len(s2_list) * 5 + 500, 1000), 2000)
  f.write('WINDOW_WIDTH=%d\n' % (window_width))
  f.write('[GENERAL_END]\n')
 
  # Helix
  f.write('[SERIES1_START]\n')
  f.write('NAME=S2\n')
  f.write('PLOTTYPE=DOT\n')
  f.write('COLORCOUNT=10\n')
  f.write('DATACOUNT=%d\n' % (len(s2_list)))
  for i in range(1, 11):
    g = int((i*i*0.01)*255.0)
    r = int((1.0 - i*i*0.01)*255.0)
    f.write('COLOR_%d=%d,%d,%f,%f,%d_%d_0\n' % (i, iMin, iMax, float(i)*0.1-0.1,float(i)*0.1,r,g))
  for i in range(iMin, iMax+1):
    f.write('DATA_%d=%d,%s,0,%s%d:%s\n' % (i-iMin+1, i, s2_list[i-iMin][2], s2_list[i-iMin][1], i, s2_list[i-iMin][2]))
  f.write('[SERIES1_END]\n')
  f.close()

def make_talosn_s2_pymol(file_name, s2_list):
  iMin = s2_list[0][0]
  iMax = s2_list[-1][0]
  f = open(file_name, 'w')
  f.write('# This is PyMOL script. Load your structure and type @rci_pymol in PyMOL\n')
  f.write('# July 7, 2017 by Woonghee Lee (whlee@nmrfam.wisc.edu)\n\n')
  for i in range(iMin, iMax+1):
    rci_s2 = float(s2_list[i-iMin][2])
    g = rci_s2*rci_s2
    r = 1.0 - rci_s2*rci_s2
    f.write('set_color rci_color%d, [%f,%f,0]\n' % (i, r, g))
    f.write('color rci_color%d, i. %d\n' % (i, i))
  f.close()

def read_talosn_dir(dir_name):
  talos_predSS = os.path.join(dir_name, 'predSS.tab')
  talos_predS2 = os.path.join(dir_name, 'predS2.tab')
  talos_pred = os.path.join(dir_name, 'pred.tab')
  if not os.path.exists(talos_pred) or not os.path.exists(talos_predS2) or \
      not os.path.exists(talos_predSS):
    return None, None

  # make ndpplot
  ## Secondary structure- HhEeLc
  ss_list = []
  f=open(talos_predSS, 'r')
  ssLines = f.readlines()
  f.close()
  filteredLines = []
  for i in range(len(ssLines)):
    line = ssLines[i]
    if line.find('VARS RESID RESNAME') != -1:
      filteredLines = ssLines[i+3:]
      break
  for line in filteredLines:
    splited = line.split()
    ss_list.append([int(splited[0]), splited[1], splited[4], \
                splited[5], splited[6], splited[7], splited[8]])
                
  ## RCI-S2
  s2_list = []
  f=open(talos_predS2, 'r')
  s2Lines = f.readlines()
  f.close()
  filteredLines = []
  for i in range(len(s2Lines)):
    line = s2Lines[i]
    if line.find('VARS RESID RESNAME') != -1:
      filteredLines = s2Lines[i+3:]
      break
  for line in filteredLines:
    splited = line.split()
    s2_list.append([int(splited[0]), splited[1], splited[4]])

  return ss_list, s2_list

def generate_ndpplots_for_talosn(session):
  import lookfeel
  options = {}
  options['title'] = 'Select a TALOS-N result directory to generate NDP-PLOT inputs.'
  options['initialdir'] = lookfeel.get_sparkyhome()
  import tkFileDialog
  path = tkFileDialog.askdirectory(**options)
  if (path) and (os.path.isdir(path)):
    ss_list, s2_list = read_talosn_dir(path)
    if ss_list == None:
      tkMessageBox.showerror('Error', 'Invalid TALOS-N result directory.')
      return
    ss_ndp = os.path.join(path, 'ndpplot_talosn_ss.ini')
    s2_ndp = os.path.join(path, 'ndpplot_talosn_s2.ini')
    s2_pymol = os.path.join(path, 'rci_pymol')
    make_talosn_ss_ndpplot(ss_ndp, ss_list)
    make_talosn_s2_ndpplot(s2_ndp, s2_list)
    make_talosn_s2_pymol(s2_pymol, s2_list)
    tkMessageBox.showinfo('Success', \
            'NDP-PLOT inputs and a pymol script are generated.')
  else:
    tkMessageBox.showerror('Error', 'Invalid TALOS-N result directory.')
