# -----------------------------------------------------------------------------
# BMRB support files
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
#
# Last updated: April 21, 2020
# 
#
# -----------------------------------------------------------------------------
#
# 1. generate sequence file
# 2. generate resonance list file
# 3. generate peak lists
# the way we do: generate new or add to the existing file

import os
import tkutil
import sputil
import pynmrstar
import Tkinter
import tkMessageBox

oneTOthree = {'I': 'ILE', 'Q': 'GLN', 'G': 'GLY', 'E': 'GLU', 'C': 'CYS',
            'D': 'ASP', 'S': 'SER', 'K': 'LYS', 'P': 'PRO', 'N': 'ASN',
            'V': 'VAL', 'T': 'THR', 'H': 'HIS', 'W': 'TRP', 'F': 'PHE',
            'A': 'ALA', 'M': 'MET', 'L': 'LEU', 'R': 'ARG', 'Y': 'TYR',
            '?': '.'} # To convert one letter to 3 letter for standard amino acids

threeTOone = {'ILE': 'I', 'GLN': 'Q', 'GLY': 'G', 'GLU': 'E', 'CYS': 'C',
            'ASP': 'D', 'SER': 'S', 'LYS': 'K', 'PRO': 'P', 'ASN': 'N',
            'VAL': 'V', 'THR': 'T', 'HIS': 'H', 'TRP': 'W', 'PHE': 'F',
            'ALA': 'A', 'MET': 'M', 'LEU': 'L', 'ARG': 'R', 'TYR': 'Y',
            '?': '.'} # To convert one letter to 3 letter for standard amino acids
nuc_map = {'H': '1H', 'C': '13C', 'N': '15N', 'F': '19F', 'P':'31P'}
iso_map = {1: '1H', 13: '13C', 15: '15N', 19: '19F', 31:'31P'}
rev_nuc_map = {'1H': 'H', '13C': 'C', '15N': 'N', '19F': 'F', '31P': 'P'}
rev_iso_map = {'1H': 1, '13C': 13, '15N': 15, '19F': 19, '31P': 31}

def read_str(fname=None, ename=None):
  if fname != None:
    strentry = pynmrstar.Entry.from_file(fname)
  elif ename != None:  
    strentry = pynmrstar.Entry.from_database(ename)
  else:
    return None
  return strentry

def parse_sequence_from_star(strentry):
  sq_result_sets = []
  for seq_loop in strentry.get_loops_by_category("Entity_comp_index"):
    sq_result_sets.append(seq_loop.get_tag(['ID', 'Auth_seq_ID', 'Comp_ID']))
  
  result_list = []
  for sq_result in sq_result_sets:
    if len(sq_result) < 1: continue
    result_list.append([])
    for row in sq_result:
      if row[1] == '.':
        result_list[-1].append('%3s %3s' % (row[2], row[0]))
      else:
        result_list[-1].append('%3s %3s' % (row[2], row[1]))
  return result_list
  
def parse_peaks_from_star(strentry):
  pk_result_sets = []
  tag_list = [ 'Comp_ID_', 'Comp_index_ID_', 'Atom_ID_', 'Position_']
  for peak_loop in strentry.get_loops_by_category("Peak_row_format"):
    for i in range(4, 0, -1):
      cur_tags = []
      for j in range(1, i+1):
        for tag in tag_list:
          cur_tag.append('%s' + str(j))
      try:    
        pk_result_sets.append(peak_loop.get_tag(cur_tags))
      except:
        continue
  result_list = []
  
  for pk_result in pk_result_sets:
    if len(pk_result) < 1: continue
    ndim = pk_result[0] / 4
    header = '   Assignment        '
    for i in range(ndim):
      header += ' w%-7d' % (i+1)
    result_list.append([header, ''])
    for row in pk_result:
      # make assignment label
      asnlbl = ''
      poslbl = ''
      for i in range(ndim):
        try:
          asnlbl += '%s%d%s-' % (threeTOone[row[0]], int(row[1]), row[2])
        except:
          asnlbl += '?-'
        try:
          poslbl += ' %8.3f' % (float(row[3]))
        except:
          poslbl += '  999.999'
      if poslbl.find('999.999'): continue
      asnlbl = asnlbl[:-1]
      line = '%21s %s' % (asnlbl, poslbl)
      result_list[-1].append(line)

  return result_list
    
def parse_shifts_from_star(strentry):
  cs_result_sets = []
  for chemical_shift_loop in strentry.get_loops_by_category("Atom_chem_shift"):
    cs_result_sets.append(chemical_shift_loop.get_tag(
          [ 'Comp_index_ID', 
            'Comp_ID', 
            'Atom_ID', 
            'Atom_type', 
            'Val']))
  result_list = []

  for cs_result in cs_result_sets:
    result_list.append([' Group  Atom   Nuc    Shift     SDev  Assignments',''])
    for row in cs_result:
      try:
        line = '%4s%-3d %-5s %-5s %8.3f   0.000      0' % \
          (threeTOone[row[1]], int(row[0]), row[2], nuc_map[row[3]], 
            float(row[4]))
        result_list[-1].append(line)
      except:
        pass
  return result_list

def parse_angle_restraints_from_star(strentry, seq_dict = None):
  angle_result_sets = []
  for angle_loop in \
          strentry.get_loops_by_category("torsion_angle_constraints"):
    angle_result_sets.append(angle_loop.get_tag(
      ['Auth_seq_ID_1', 'Auth_comp_ID_1', 'Auth_atom_ID_1',
       'Auth_seq_ID_2', 'Auth_comp_ID_2', 'Auth_atom_ID_2',
       'Auth_seq_ID_3', 'Auth_comp_ID_3', 'Auth_atom_ID_3',
       'Auth_seq_ID_4', 'Auth_comp_ID_4', 'Auth_atom_ID_4',
       'lower', 'upper'
      ]))

  if len(angle_result_sets) == 0: return [], []  

  result_list = []

  for ang_result in angle_result_sets:
    result_list.append([])
    for row in ang_result:
      if [row[1], row[4], row[7], row[10]] != ['C', 'N', 'CA', 'C'] and \
        [row[1], row[4], row[7], row[10]] != ['N', 'CA', 'C', 'N']: continue
      try:
        if seq_dict != None:
          if row[0] != row[3]:
            line = '%-4s %-4s PHI %8.3f %8.3f' % \
              (row[3], seq_dict[int(row[3])][0], float(row[-2]), float(row[-1]))
          else:
            line = '%-4s %-4s PSI %8.3f %8.3f' % \
              (row[3], seq_dict[int(row[3])][0], float(row[-2]), float(row[-1]))
        else:
          if row[0] != row[3]:
            line = '%-4s %-4s PHI %8.3f %8.3f' % \
              (row[3], row[4], float(row[-2]), float(row[-1]))
          else:
            line = '%-4s %-4s PSI %8.3f %8.3f' % \
              (row[3], row[4], float(row[-2]), float(row[-1]))
        result_list[-1].append(line)
      except:
        pass
  return result_list

def parse_distance_restraints_from_star(strentry, seq_dict = None):
  dist_result_sets = []
  for dist_loop in \
          strentry.get_loops_by_category("general_distance_constraints"):
    dist_result_sets.append(dist_loop.get_tag(
      ['Chem_comp_index_ID_1', 'Chem_comp_ID_1', 'Atom_ID_1',
       'Chem_comp_index_ID_2', 'Chem_comp_ID_2', 'Atom_ID_2',
       'Upper_linear_limit', 'Lower_linear_limit']))

  if len(dist_result_sets) == 0: return [], []  
  upl_result_list = []
  lol_result_list = []

  for dist_result in dist_result_sets:
    upl_result_list.append([])
    lol_result_list.append([])
    for row in dist_result:
      try:
        if seq_dict != None:
          line = '%-4s %-4s %-4s %-4s %-4s %-4s %s' % \
              (row[0], seq_dict[int(row[0])][0], row[2], 
              row[3], seq_dict[int(row[3])][0], row[5], row[6])
          line2 = '%-4s %-4s %-4s %-4s %-4s %-4s %s' % \
              (row[0], seq_dict[int(row[0])][0], row[2], 
              row[3], seq_dict[int(row[3])][0], row[5], row[7]) # lower
        else:
          line = '%-4s %-4s %-4s %-4s %-4s %-4s %s' % \
              (row[0], row[1], row[2], 
              row[3], row[4], row[5], row[6])
          line2 = '%-4s %-4s %-4s %-4s %-4s %-4s %s' % \
              (row[0], row[1], row[2], 
              row[3], row[4], row[5], row[7])     # lower
        upl_result_list[-1].append(line)
        lol_result_list[-1].append(line2)
      except:
        pass
  return upl_result_list, lol_result_list

def parse_rdc_restraints_from_star(strentry, seq_dict = None):
  rdc_result_sets = []
  for rdc_loop in \
          strentry.get_loops_by_category("RDC_constraints"):
    rdc_result_sets.append(rdc_loop.get_tag(
      ['Auth_seq_ID_1', 'Auth_comp_ID_1', 'Auth_atom_ID_1',
       'Auth_seq_ID_2', 'Auth_comp_ID_2', 'Auth_atom_ID_2',
       'RDC_val', 'RDC_val_err', 'Entry_ID']))
  rdc_list = ['# Orientation  Magnitude  Rhombicity  ORI residue number']
  result_list = []
  entry_list = []
  if len(rdc_result_sets) == 0: return []
  for rdc_result in rdc_result_sets:
    for row in rdc_result:
      try:
        if seq_dict != None:
          line = '%-4s %-4s %-4s %-4s %-4s %6.2f %6.2f     1.00   %s' % \
              (row[0], seq_dict[int(row[0])][0], row[2], 
              row[3], seq_dict[int(row[3])][0], row[5], 
              float(row[6]), float(row[7]), row[8])
        else:
          line = '%-4s %-4s %-4s %-4s %-4s %6.2f %6.2f     1.00   %s' % \
              (row[0], row[1], row[2], 
              row[3], row[4], row[5], 
              float(row[6]), float(row[7]), row[8])
        result_list.append(line)
        entry_list.append(row[8])
      except:
        pass
  entry_list = list(set(entry_list)) # remove duplicate
  for i in range(len(entry_list)):
    line = '%6s     999         999       %3d' % (900+i)
    rdc_list.append(line)
  rdc_list.append(\
    '#  First atom      Second atom        RDC   Error  Weight Orientation')
  for line in result_list:
    rdc_list.append(line)
  return rdc_list

def parse_saxs_restraints_from_star(strentry):
  saxs_result_sets = []
  for saxs_loop in \
          strentry.get_loops_by_category("SAXS_constraints"):
    saxs_result_sets.append(saxs_loop.get_tag(
      ['Q_value', 'Intensity_val', 'Intensity_val_err']))
  result_list = []

  for saxs_result in saxs_result_sets:
    result_list.append([])
    for row in saxs_result:
      try:
        line = '%24s %24s %24s' % \
            (row[0], row[1], row[2])
        result_list[-1].append(line)
      except:
        pass
  return result_list

def deploy_to_directory(fname=None, ename=None, dirname=None, \
                        prefix='protein', overwrite=True):
  strentry = read_str(fname=fname, ename=ename)
  if strentry == None:
    return False, 'Failed to read the NMR-STAR file.'
  seq_list = parse_sequence_from_star(strentry)
  # make sequence dict
  try:
    temp_list = []
    for i in range(len(seq_list[0])):
      sp = seq_list[0][i].split()
      temp_list.append([int(sp[1]), sp[0]])
    seq_dict = dict(temp_list)
  except:
    seq_dict = None

  shift_list = parse_shifts_from_star(strentry)
  peak_list = parse_peaks_from_star(strentry)
  upl_list, lol_list = parse_distance_restraints_from_star(strentry, seq_dict)
  ang_list = parse_angle_restraints_from_star(strentry, seq_dict)
  rdc_list = parse_rdc_restraints_from_star(strentry, seq_dict)
  saxs_list = parse_saxs_restraints_from_star(strentry, seq_dict)

  if not overwrite:
    # check file names
    for i in range(len(seq_list)):
      outname = os.path.join(dirname, '%s_seq_%d.seq' % (prefix, i+1))
      if os.path.exists(outname):
        return False, '%s already exists.' % (outname)
    for i in range(len(shift_list)):
      outname = os.path.join(dirname, '%s_shifts_%d.list' % (prefix, i+1))
      if os.path.exists(outname):
        return False, '%s already exists.' % (outname)
    for i in range(len(peak_list)):
      outname = os.path.join(dirname, '%s_peaks_%d.list' % (prefix, i+1))
      if os.path.exists(outname):
        return False, '%s already exists.' % (outname)
    for i in range(len(upl_list)):
      outname = os.path.join(dirname, '%s_dist_%d.upl' % (prefix, i+1))
      if os.path.exists(outname):
        return False, '%s already exists.' % (outname)
    for i in range(len(ang_list)):
      outname = os.path.join(dirname, '%s_angle_%d.aco' % (prefix, i+1))
      if os.path.exists(outname):
        return False, '%s already exists.' % (outname)
    outname = os.path.join(dirname, '%s_dc.rdc' % (prefix))
    if os.path.exists(outname):
      return False, '%s already exists.' % (outname)
    for i in range(len(saxs_list)):
      outname = os.path.join(dirname, '%s_saxs_%d.dat' % (prefix, i+1))
      if os.path.exists(outname):
        return False, '%s already exists.' % (outname)
        
  # start writing
  from wlutil import write_list
  for i in range(len(seq_list)):
    outname = os.path.join(dirname, '%s_seq_%d.seq' % (prefix, i+1))
    write_list(outname, seq_list[i])
  for i in range(len(shift_list)):
    outname = os.path.join(dirname, '%s_shifts_%d.list' % (prefix, i+1))
    write_list(outname, shift_list[i])
  for i in range(len(peak_list)):
    outname = os.path.join(dirname, '%s_peaks_%d.list' % (prefix, i+1))
    write_list(outname, peak_list[i])
  for i in range(len(upl_list)):
    outname = os.path.join(dirname, '%s_dist_%d.upl' % (prefix, i+1))
    write_list(outname, upl_list[i])
  for i in range(len(lol_list)):
    outname = os.path.join(dirname, '%s_dist_%d.lol' % (prefix, i+1))
    write_list(outname, lol_list[i])
  for i in range(len(ang_list)):
    outname = os.path.join(dirname, '%s_angle_%d.aco' % (prefix, i+1))
    write_list(outname, ang_list[i])
  if len(rdc_list) > 3:
    outname = os.path.join(dirname, '%s_dc.rdc' % (prefix))
    write_list(outname, rdc_list)
  for i in range(len(saxs_list)):
    outname = os.path.join(dirname, '%s_saxs_%d.dat' % (prefix, i+1))
    write_list(outname, saxs_list[i])
  return True, ''

class bmrb_parse_dialog(tkutil.Dialog):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'BMRB NMR-STAR parser')

    bmrb_frame = Tkinter.Frame(self.top, width = 600, height = 25)
    bmrb_frame.pack(side='top', anchor='w')
    bmrb_ef = tkutil.entry_field(bmrb_frame, 'BMRB: ', initial = '', width = 40)
    bmrb_ef.frame.pack(side = 'left', anchor = 'w', expand = 0)
    self.bmrb = bmrb_ef.variable        
    self.br = tkutil.button_row(bmrb_frame,
        ('Browse...', self.bmrb_browse_cb),
        )
    self.br.frame.pack(side = 'top', anchor = 'e', expand = 0)
    tkutil.create_hint(self.br.buttons[0], 
        'Browse a BMRB file in local. Or just type an entry ID.')

    deploy_frame = Tkinter.Frame(self.top, width = 600, height = 25)
    deploy_frame.pack(side='top', anchor='w')
    deploy_ef = tkutil.entry_field(deploy_frame, 'Target directory: ', 
                                  initial = '', width = 40)
    deploy_ef.frame.pack(side = 'left', anchor = 'w', expand = 0)
    self.deploy = deploy_ef.variable        
    self.br2 = tkutil.button_row(deploy_frame,
        ('Browse...', self.deploy_browse_cb),
        )
    self.br2.frame.pack(side = 'top', anchor = 'w', expand = 0)
    tkutil.create_hint(self.br2.buttons[0], 
        'Choose a directory to generate parsed files.')

    self.br3 = tkutil.button_row(self.top,
          ('Parse', self.parse_cb),
          ('Close', self.close_cb))
    self.br3.frame.pack(side = 'top', anchor = 'e', expand = 0)      

  def bmrb_browse_cb(self):
    path = tkutil.load_file(self.top, 'Select a NMR-STAR file', 'bmrb2sparky')
    if path == '': return
    self.bmrb.set(path)
    tkutil.remember_file_dialog_path(path, 'bmrb2sparky')

  def deploy_browse_cb(self):
    initial_dir, initial_file = tkutil.initial_file_dialog_path('bmrb2sparky')
    import tkFileDialog
    path = tkFileDialog.askdirectory(initialdir = initial_dir)
    if path == '': return
    self.deploy.set(path)
    tkutil.remember_file_dialog_path(path, 'bmrb2sparky')

  def parse_cb(self):
    bmrb = self.bmrb.get()
    try:
      ebmrb = float(bmrb)
    except:
      ebmrb = None
    if ebmrb == None and not os.path.exists(bmrb):
      tkMessageBox.showinfo('Error', 'BMRB entry/file has not been set yet.')
      return
    deploy = self.deploy.get()
    if deploy == '':
      tkMessageBox.showinfo('Error', 'Deploy directory has not been set yet.')
      return
    if ebmrb == None:
      tf, msg = deploy_to_directory(fname=bmrb, dirname=deploy)
    else:
      tf, msg = deploy_to_directory(ename=bmrb, dirname=deploy)

    if tf:
      tkMessageBox.showinfo('Deployed', 'Success.')
    else:
      tkMessageBox.showinfo('Error', msg)

# -----------------------------------------------------------------------------
#
def show_bmrb_parse(session):
  sputil.the_dialog(bmrb_parse_dialog, session).show_window(1)

# -----------------------------------------------------------------------------
# BMRB NMR-STAR 3.2 generator
#
# SEQUENCE
# CHEMICAL SHIFTS
# PEAK LISTS
# 
def SaveNmrStar32(session, path):
  iFirst = 99999
  lines = []
  groups = []

  from nmrstar import GetBiomoleculeType
  bt = GetBiomoleculeType(session)
  if bt != 'p':
    tkMessageBox.showerror('Error', 'Only protein is supported at this moment.')
    return
  
  import SPARKYtoNMRSTAR 
  import myseq
  
  sc = SPARKYtoNMRSTAR.SPARKYtoNMRSTAR()
  saveframe_list = []
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

      group = [resonance.group.number, aaa, resonance.atom.name, 
              atom_type, isotope, resonance.frequency, 
              resonance.deviation]
      groups.append(group)

  groups.sort()
  
  group_list2 = myseq.BuildSequence(session, 3)
  group_list2 = myseq.CheckSequence(group_list2) # sort and fill the gap
  
  if myseq.GapInSequence(group_list2) == 1: # there is a gap
    tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
    group_list2 = myseq.LoadSeq(session, group_list2) # this fills a gap
    if group_list2 == None:
      tkMessageBox.showerror('Sequence', 
                    'Sequence information is not satisfactory.')
      return
  
  # sequence
  lines = ''
  for group in group_list2:
    lines += '%s %d\n' % (oneTOthree[group[1]], group[0])
  tag_list, d = sc.read_dyana_sequence(content=lines)
  sf = sc.generate_sequence_saveframe('nmrfam_sparky_sequence', '1', 
                                tag_list, d)
  saveframe_list.append(sf)

  # chemical shifts
  lines = ' Group   Atom  Nuc    Shift   SDev  Assignments\n\n'
  for group in groups:
    line = ''
    try:
      line = ' %s%-4d %4s %4s %8.3f %8.3f    0' % \
          (group[1], group[0], group[2], nuc_map[group[4]], group[5], group[6])
    except:
      continue
    lines += line + '\n'
  tag_list, d = sc.read_sparky_resonance_list(content=lines)
  sf = sc.generate_assigned_cs_list_saveframe(pl_name = 'cs_list', pl_id=1, 
          tag_list=tag_list, data = d)
  saveframe_list.append(sf)

  # peak lists
  id = 1
  for spec in session.project.spectrum_list():
    peaks = spec.peak_list()
    if len(peaks) == 0: continue
    nuclei_list, isotope_list, atom_list = [], [], []
    try:
      for nuc in spec.nuclei:
        nuclei_list.append(rev_nuc_map[nuc])
        isotope_list.append(rev_iso_map[nuc])
        atom_list.append('%s*' % (rev_nuc_map[nuc]))
    except:
      continue
    lines = ''
    for peak in peaks:
      res = peak.resonances()
      line = '%30s ' % (sputil.complete_assignment(peak.assignment))
      for freq in peak.frequency:
        line += '%12.3f ' % (freq)
      line += '%f\n' % (peak.data_height)
      lines += line
    
    if spec.dimension == 2:
      tag_list, d = sc.read_pine_sparky_2D_peak_list(content=lines, 
                                                    p=False, h=True)
    elif spec.dimension == 3:
      tag_list, d = sc.read_pine_sparky_3D_peak_list(content=lines, 
                                                    p=False, h=True)
    elif spec.dimension == 4:
      tag_list, d = sc.read_pine_sparky_4D_peak_list(content=lines, 
                                                    p=False, h=True)
    else: continue

    pln = 'peak_list_%d_%s' % (id, spec.name)

    sf = sc.generate_peak_list_saveframe(experiment_name=spec.name,
            dimensions=spec.dimension, atom_type=nuclei_list,
            peak_list_name = pln, isotope = isotope_list,
            region = atom_list, pl_id = id, tag_list = tag_list, data = d)

    saveframe_list.append(sf)
    id += 1
  if len(saveframe_list) != 0:
    key_code = os.path.realpath(session.project.save_path).split('/')[-1]
    sc.write_star_file(saveframe_list, data_set_name=key_code,
      file_name=path)

def GenerateNmrStar32(session):
  path = tkutil.save_file(session.tk, "Save to NMRSTAR 3.2 file", 
                          "nmrstar.str")

  if not path: return
  SaveNmrStar32(session, path)
  
