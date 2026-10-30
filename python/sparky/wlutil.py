# -----------------------------------------------------------------------------
# Woonghee Lee's utils
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Sep 16, 2019

#
#
# -----------------------------------------------------------------------------

import os
import nmrfam
import sparky
import tkutil
import Tkinter
import tkMessageBox
import shutil, errno

# PDB <-> mmCIF/PDBx conversion
def generate_mmcif_from_pdb(session):
  import pdb2cif
  
  ftypes = [('PDB files', '*.pdb'), ('All files', '*')]
  ftypes2 = [('mmCIF(PDBx) files', '*.cif'), ('All files', '*')]
  
  
  pdb_file = tkutil.load_file2(session.tk, 'Select a PDB to convert', 
                'cif2pdb', '.pdb', ftypes, os.environ["SPARKYHOME"])
  
  if not os.path.exists(pdb_file):
    return
  cur_dir = os.path.dirname(pdb_file)

  cif_file = tkutil.save_file2(session.tk, 'New mmCIF(PDBx) file name', 
                  'pdb2cif', '.cif', ftypes2, cur_dir)
  
  if cif_file == '': 
    return
  if not pdb2cif.pdb2cif(pdb_file, cif_file, HETATM=True):
    tkMessageBox.showerror('Error', 'Generate a mmCIF(PDBx) file failed. Check and simplify your PDB file.')

def generate_pdb_from_mmcif(session):
  import cif2pdb
  ftypes = [('mmCIF(PDBx) files', '*.cif'), ('All files', '*')]
  ftypes2 = [('PDB files', '*.pdb'), ('All files', '*')]
  
  cif_file = tkutil.load_file2(session.tk, 'Select a mmCIF(PDBx) to convert', 
                'pdb2cif', '.cif', ftypes, os.environ["SPARKYHOME"])
  
  if not os.path.exists(cif_file):
    return

  cur_dir = os.path.dirname(cif_file)
  pdb_file = tkutil.save_file2(session.tk, 'New PDB file name', 
                  'cif2pdb', '.pdb', ftypes2, cur_dir)
                                          
  if pdb_file == '': 
    return
  
  if not cif2pdb.cif2pdb(cif_file, pdb_file, HETATM=True):
    tkMessageBox.showerror('Error', 'Generate a PDB file failed. Check and simplify your mmCIF/PDBx file.')


# advanced selection
def select_height(session, mode):
  if session.selected_spectrum() == None:
    tkMessageBox.showerror('Select by heights', 'Please select a spectrum.')
    return
  if len(session.selected_spectrum().selected_peaks()) != 1:
    tkMessageBox.showerror('Select by heights', 'Please select one peak to set height threshold.')
    return  
  thres = session.selected_spectrum().selected_peaks()[0].data_height
  iCount = 0
  for peak in session.selected_spectrum().peak_list():
    if peak.data_height == None: continue
    
    if mode == 0 and peak.data_height >= thres: 
      peak.selected = 1
      iCount = iCount+1
    elif mode == 1 and peak.data_height <= thres: 
      peak.selected = 1
      iCount = iCount+1
    elif mode == 2 and abs(peak.data_height) >= abs(thres) and (peak.data_height*thres) >= 0: 
      peak.selected = 1
      iCount = iCount+1
    elif mode == 3 and abs(peak.data_height) <= abs(thres) and (peak.data_height*thres) >= 0: 
      peak.selected = 1
      iCount = iCount+1      
    else: 
      peak.selected = 0

  tkMessageBox.showinfo('Select by heights', 'Finished. %d peak(s) selected' % iCount)

def select_big(session):
  select_height(session, 0)
  
def select_small(session):
  select_height(session, 1)
  
def select_big_same_sign(session):
  select_height(session, 2)
  
def select_small_same_sign(session):
  select_height(session, 3)  

def unzip(source_filename, dest_dir):
  with zipfile.ZipFile(source_filename) as zf:
    for member in zf.infolist():
      # Path traversal defense copied from
      # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
      words = member.filename.split('/')
      path = dest_dir
      for word in words[:-1]:
        while True:
          drive, word = os.path.splitdrive(word)
          head, word = os.path.split(word)
          if not drive:
            break
        if word in (os.curdir, os.pardir, ''):
          continue
        path = os.path.join(path, word)
      zf.extract(member, path)  

def user_and_seq(tkdg, OPTIONAL = False, USERINFO = True):
  session = tkdg.session
  if not OPTIONAL:
    yn = 'Your name: '
    ye = 'Your email: '
  else:
    yn = 'Your name (optional): '
    ye = 'Your email (optional): '
  # User name
  user_name_ef = tkutil.entry_field(tkdg.top, yn, initial = '', width = 11+len(yn))
  user_name_ef.frame.pack(side = 'top', anchor = 'w', expand = 0)
  tkdg.user_name = user_name_ef.variable
  
  # User email
  user_email_ef = tkutil.entry_field(tkdg.top, ye, initial = '', width = 10+len(ye))
  user_email_ef.frame.pack(side = 'top', anchor = 'w')
  tkdg.user_email = user_email_ef.variable
  
  sep = Tkinter.Frame(tkdg.top, height=2, bd=1, relief="ridge")
  sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
  
  # Sequence file    
  user_seq_ff = tkutil.file_field2(tkdg.top, 'Sequence file: ', '', 
                  file_type=[('3-letter-code sequence file with indices', '.seq'), 
                            ('1-letter-code sequence file', '.fasta'), 
                            ('3-letter-code sequence file without indices', '.txt')], 
                  default_ext='.seq', width = 25)
  user_seq_ff.frame.pack(side = 'top', anchor = 'w')
  tkdg.user_seq = user_seq_ff.variable
  sep = Tkinter.Frame(tkdg.top, height=2, bd=1, relief="ridge")
  sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)   
  # check if file exists
  if session.project != None:
    if session.project.sparky_directory != '' and os.path.exists(session.project.save_path):
      seq_path = session.project.save_path + '.seq'
      if os.path.exists(seq_path):
        user_seq_ff.variable.set(seq_path)
  
  if not USERINFO:
    user_name_ef.frame.pack_forget()
    user_email_ef.frame.pack_forget()
  return user_name_ef, user_email_ef, user_seq_ff

# gives sum, avg and stddev
def stdstat(pdata):
  dSum = sum(pdata)
  dMean = dSum / float(len(pdata))
  dSumDev = 0.
  for data in pdata:
    dSumDev = dSumDev + ((data-dMean)**2)
  dDev = (dSumDev / float(len(pdata))) ** 0.5
  return dSum, dMean, dDev

def corrcoef(pdata, pdata2):
  if len(pdata) != len(pdata2):
    return 0.
  dSum, dMean, dDev =    stdstat(pdata)
  dSum2, dMean2, dDev2 = stdstat(pdata2)

  if dDev == 0.0 or dDev2 == 0.0: return 0.

  # calculate z
  pdZx = list(map(lambda x: [], range(len(pdata))))
  pdZy = list(map(lambda x: [], range(len(pdata))))
  pdCrossZxZy = list(map(lambda x: [], range(len(pdata))))
  for i in range(len(pdata)):
    pdZx[i] = (pdata[i]-dMean) / dDev
    pdZy[i] = (pdata2[i]-dMean2) / dDev2
    pdCrossZxZy[i] = pdZx[i] * pdZy[i]
  dSumCross = sum(pdCrossZxZy)
  dR = dSumCross / float(len(pdata))
  return dR

def transpose(ppdata):
  # transpose
  ncol = len(ppdata[0])
  nrow = len(ppdata)
  t_ppdata = list(map(lambda x: map(lambda y: 0.0, range(nrow)), range(ncol)))
  for i in range(nrow):
    for j in range(ncol):
      t_ppdata[j][i] = ppdata[i][j]
  return t_ppdata

def corrmat(ppdata, hvmode):
  # hvmode 0: horizontal, hvmode 1: vertical
  ncol = len(ppdata[0])
  nrow = len(ppdata)
  if hvmode == 0:
    r_mat = list(map(lambda x: map(lambda y: 0.0, range(ncol)), range(ncol)))
    # transpose
    t_ppdata = list(map(lambda x: map(lambda y: 0.0, range(nrow)), range(ncol)))
    for i in range(ncol):
      for j in range(ncol):
        dR = corrcoef(t_ppdata[i], t_ppdata[j])
        r_mat[i][j], r_mat[j][i] = dR, dR
  else:
    r_mat = list(map(lambda x: map(lambda y: 0.0, range(nrow)), range(nrow)))
    for i in range(nrow):
      for j in range(nrow):
        dR = corrcoef(ppdata[i], ppdata[j])
        r_mat[i][j], r_mat[j][i] = dR, dR
  return r_mat

def snapinterval(value, interval, mode): # mode 0: lower bound, 1: upper bound
  val_list = []
  idx = int(float(value) / float(interval))
  if value < 0:
    val = float(idx+1) * interval
    while True:
      val_list.append(val)
      if val < value: break
      val = val - interval
    if mode == 0: return val_list[-1]
    else: return val_list[-2]
  else:
    val = float(idx-1) * interval
    while True:
      val_list.append(val)
      if val > value: break
      val = val + interval
    if mode == 0: return val_list[-2]
    else: return val_list[-1]

def snapintervals(min_value, max_value, interval):
  min_value2 = snapinterval(min_value, interval, 0)
  max_value2 = snapinterval(max_value, interval, 1)
  return min_value2, max_value2

def write_list(file_path, wlist, nonull=False):
  with open(file_path, 'w') as file_handler:
    for item in wlist:
      if not nonull:
        file_handler.write("{}\n".format(item))
      else:
        file_handler.write("{}".format(item))

def replace_all(text, sources, targets):
  if len(sources) != len(targets):
    if len(targets) == 1:
      target = targets[0]
      for i in range(len(sources)-1): targets.append(target)
    else: return text
  temp = text
  for i in range(len(sources)):
    temp = temp.replace(sources[i], targets[i])
  return temp

def SpectrumByName(session, spec_name):
  for spec in session.project.spectrum_list():
    if spec.name == spec_name:
      return spec
  return None

AAA_dict = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
     'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
     'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W',
     'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}

def projlist(seq_list, seqidx_list):
  if len(seq_list) == 0: return '', 9999
  s_list = list(map(lambda x: 'X', range(1000)))
  start_idx, end_idx = 9999, -9999
  for i in range(len(seq_list)):
    s, n = seq_list[i], seqidx_list[i]
    s_list[n] = s
    start_idx = min(start_idx, n)
    end_idx = max(end_idx, n)
  seq = ''
  for s in s_list[start_idx:end_idx+1]:
    seq = seq + s
  return seq, start_idx

def ExtractSequenceFromPDB(pdb_file):
  # Get sequence per chain from pdb file
  # Return:
  #  [ ['A', 'XXXXXX', 1], ['B', 'XXXXXX', 1] ]
  if not os.path.exists(pdb_file):
    return []
  f = open(pdb_file, 'r')
  lines = f.readlines()
  f.close()
  # only first models in case NMR structure
  new_lines = []
  for i in range(len(lines)):
    line = lines[i].strip()
    if len(line) < 6: continue
    elif line[0:4] == 'ATOM': new_lines.append(line)
    elif line[0:6] == 'ENDMDL': break
  lines = new_lines
  chain_list = []
  seq_list = []
  seqidx_list = []
  curch = '*'
  for line in lines:
    res_name = line[17:20].strip()
    seq_num = int(line[22:26])
    if not AAA_dict.has_key(res_name): continue
    ch = line[21:22]
    if curch != ch:
      seq, init_seq = projlist(seq_list, seqidx_list)
      if init_seq != 9999:
        chain_list.append([curch, seq, init_seq])
      curch = ch
      seq_list = []
      seqidx_list = []
    seq_list.append(AAA_dict[res_name])
    seqidx_list.append(seq_num)
  # last remainder
  seq, init_seq = projlist(seq_list, seqidx_list)
  if init_seq != 9999:
    chain_list.append([curch, seq, init_seq])
  return chain_list

def StringListToCSV(strlist):
  csv = ''
  for st in strlist:
    csv = csv + st + ','
  if csv != '':
    return csv[0:-1]
  return ''

def WritePeakList(spectrum, path, assignment=True, heights=True):  
  lines = '%25s' % ('      Assignment        ')
  unassign = ''
  for i in range(spectrum.dimension):
    lines = lines + '         w%d' % (i+1)
    unassign += '?-'
  unassign = unassign[0:-1]
  if heights:
    lines += '     Data Heights'
  lines += '\n\n'
  
  for peak in spectrum.peak_list():
    if assignment:
      lbl = '%25s' % (peak.assignment)
    else:
      lbl = unassign
    for i in range(spectrum.dimension):
      lbl += '%13.3f' % (peak.frequency[i])
    if heights:
      lbl += '%13d' % (int(peak.data_height+0.5))
    lbl += '\n'
    lines += lbl

  f = open(path, 'w')
  f.write(lines)
  f.close()
    

#####################################################################
# INI I/O IMPLEMENTATION
#####################################################################
def ReadFileLines(path):
  f = open(path, 'r')
  lines = f.readlines()
  f.close()
  return lines

def SaveFileLines(path, lines):
  f = open(path, 'w')
  for line in lines:
    f.write(line.strip() + '\n')
  f.close()
  
def FindIniSection(lines, section):
  iStart = 10**9
  iEnd = -10**9
  key_start = '[' + section + ']'
  key_end =  '[' + section + '_END]'
  for i in range(len(lines)):
    line = lines[i].strip()
    if line == key_start: iStart = i
    if line == key_end: iEnd = i
    if iEnd > iStart: break
  return iStart, iEnd

def FindIniKey(lines, section_start, section_end, key):
  for i in range(section_start, section_end+1):
    line = lines[i]
    if line.find(key + '=') != -1:
      return i
  return -1

def GetIniString(lines, section, key):
  iStart, iEnd = FindIniSection(lines, section)
  if iEnd < iStart: return ''
  iKeyIdx = FindIniKey(lines, iStart, iEnd, key)
  if iKeyIdx == -1: return ''
  return lines[iKeyIdx].replace(key+'=', '').strip()  

def LoadIniString(ini_path, section, key):
  lines = ReadFileLines(ini_path)
  iStart, iEnd = FindIniSection(lines, section)
  if iEnd < iStart: return ''
  iKeyIdx = FindIniKey(lines, iStart, iEnd, key)
  if iKeyIdx == -1: return ''
  return lines[iKeyIdx].replace(key+'=', '').strip()

def SaveIniString(ini_path, section, key, value):
  if os.path.exists(ini_path):
    lines = ReadFileLines(ini_path)
  else:
    lines = []
  iStart, iEnd = FindIniSection(lines, section)
  kv = '%s=%s' % (key, value)
  # check if I have section and key
  if iStart > iEnd: # No section. Just add to the bottom
    lines.append('[' + section + ']')
    lines.append(kv)
    lines.append('[' + section + '_END]')
  else: # Section exists
    # Find value
    iKeyIdx = FindIniKey(lines, iStart, iEnd, key)
    if iKeyIdx == -1: # no key found
      lines.insert(iEnd-1, kv)
    else: # key found. just update
      lines[iKeyIdx] = kv
  SaveFileLines(ini_path, lines)

def is_tool(name):
    from distutils.spawn import find_executable
    return find_executable(name) is not None

def extract_lines(lines, start_keyword, end_keyword):
  results = []
  for i in range(len(lines)):
    line = lines[i]
    if line.find(start_keyword) != -1:
      for j in range(i, len(lines)):
        line = lines[j]
        results.append(line)
        if line.find(end_keyword) != -1:
          return results
  return results

def make_aligned_pdb(session, pdb_file, out_file):
    import swalign
    # build sequence information from resonance list
    # self.session.project.condition_list().resonance_list()
    user_seq_list = []
    user_seqidx_list = []
    for cond in session.project.condition_list():
      for res in cond.resonance_list():
        if not res.group.symbol in swalign.m_singlea: continue
        if res.group.number < 1 or res.group.number > 999: continue
        user_seq_list.append(res.group.symbol)
        user_seqidx_list.append(res.group.number)

    user_seq, user_min_seq = projlist(user_seq_list, user_seqidx_list)
        
    # read pdb. use the highest 'sum_blosum62' chain
    chain_seq_list = ExtractSequenceFromPDB(pdb_file)
    max_blosum62 = -9999999
    best_chain = None
    for chain in chain_seq_list:
      seq_align_dict = swalign.do_swalign(user_seq, user_min_seq, \
                                chain[1], chain[2])
      if seq_align_dict['sum_blosum62'] > max_blosum62:
        best_chain = chain
        max_blosum62 = seq_align_dict['sum_blosum62']

    # perform sequence alignment and set seq_align_dict
    seq_align_dict = swalign.do_swalign(user_seq, user_min_seq, 
                                              best_chain[1], best_chain[2])
    seq_align_chain = best_chain[0]

    # make chesca.pdb  
    new_lines = swalign.transform(pdb_file, \
                  seq_align_dict, seq_align_chain, HETATM=True)
    f = open(out_file, 'w')
    f.write(new_lines)
    f.close()

# overlay ndpplot and provide contents
def overlay_ndpplots(file1, file2, GENERAL='file2'):
  if not os.path.exists(file1):    return ''
  if not os.path.exists(file2):    return ''
  f = open(file1, 'r')
  ndp1 = f.readlines()
  f.close()
  f = open(file2, 'r')
  ndp2 = f.readlines()
  f.close()

  if GENERAL == 'file1':
    ndp = ndp1
  else:
    ndp = ndp2
  
  general_list = extract_lines(ndp, '[GENERAL_START]', '[GENERAL_END]')
  content_list = []

  # file1
  for i in range(1, 100):
    szStart = '[SERIES%d_START]' % (i)
    szEnd = '[SERIES%d_END]' % (i)
    ext_lines = extract_lines(ndp1, szStart, szEnd)
    if len(ext_lines) == 0: break
    content_list.append(ext_lines)

  # file2
  for i in range(1, 100):
    szStart = '[SERIES%d_START]' % (i)
    szEnd = '[SERIES%d_END]' % (i)
    ext_lines = extract_lines(ndp2, szStart, szEnd)
    if len(ext_lines) == 0: break
    content_list.append(ext_lines)

  # reorganize series numbers
  for i in range(len(content_list)):
    content_list[i][0] = '[SERIES%d_START]\n' % (i+1)
    content_list[i][-1] = '[SERIES%d_END]\n' % (i+1)
  
  content = ''
  for line in general_list:
    content = content + line
  for series_list in content_list:
    for line in series_list:
      content = content + line
  return content

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise