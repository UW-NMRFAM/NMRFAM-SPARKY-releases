# -----------------------------------------------------------------------------
# PISA-SPARKY dialog
# -----------------------------------------------------------------------------
#
# PISA-SPARKY developed by Woonghee Lee
#
# This module is designed to interact with NMRFAM Pisa Web Server
# PISA.py is developed by Daniel Weber from Veglia group (U of Minnesota)
#
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: November 12, 2019
# 
#
# -----------------------------------------------------------------------------
# CITATIONS:
#
# -----------------------------------------------------------------------------

import os
import platform
import Tkinter
import sparky
import sputil
import tkutil
import tkMessageBox
import myseq
import nmrfam
import posthtml
import wlutil
import shutil
import swalign
import itertools


# for token
import time
import random
import multiprocessing

arg_all="""24  -o ORDER           General order parameter {1.0}
28  --pas PAS [PAS ...]    N15 principal axis system in ppm {57.3 81.2 228.1}
24  --rho_start START  Residue to reference rho (the first sequence number)
24  -t TAU             Helical tilt angle in degrees {20.0}
24  -r RHO0            Azimuthal angle of starting residue {0.0}
24  --beta BETA        Beta rotation for PAS with respect to amide plane in degrees {17.0}
24  --negative_dc      Output all dipolar couplings as negative values in output files
24  -f PEAKS           Currently selected peaks or all peaks in the spectrum if nothing selected {pisa_peaks.list}
24  --dc DC            Maximal NH dipolar coupling {10.735}
24  --flip FLIP        Angle of membrane to B0 in degrees {0.0}
44  --show_only [SHOW_ONLY ...]            Display only these residues in the output files (none)

24  --period PERIOD    Number of residues per helical rotation {3.6}
24  --phi PHI          Phi dihedral angle for ideal helix in degrees {-63.0}
24  --psi PSI          Psi dihedral angle for ideal helix in degrees {-42.0}
24  --aCaCN ACACN      Angle of Ca-C-N in degrees {116.0}
24  --aCNCa ACNCA      Angle of C-N-Ca in degrees {124.0}
24  --aNCaC ANCAC      Angle of N-Ca-C in degrees {107.4}
24  --aCaNH ACANH      Angle of Ca-N-H in degrees {116.0}
24  --bCaC BCAC        Length of Ca-C bond in angstroms {1.52}
24  --bCN BCN          Length of C-N bond in angstroms {1.35}
24  --bNCa BNCA        Length of N-Ca bond in angstroms {1.45}

44  --fit_tau FIT_TAU [FIT_TAU ...]        Min., max. and step to fit tilt angle {0.0 90.0 1.0}
44  --fit_rho0 FIT_RHO0 [FIT_RHO0 ...]     Min., max. and step to fit azimuthal angle {0.0 360.0 4.0}
44  --fit_order FIT_ORDER [FIT_ORDER ...]  Min., max. and step to fit order parameter {0.85 0.85 0.1}
44  --fit_only FIT_ONLY [FIT_ONLY ...]     Only fit wheel to these residues (none)
49  --fit_exclude FIT_EXCLUDE [FIT_EXCLUDE ...] Exclude these residues from fitting (none)
24  --scalar SCALAR    Value to scale up dipolar couplings to match chemical shift dispersion {10.0}
24  --explore          Specify to explore combinations of tau, rho0 and order for best fit
34  --errors ERRORS [ERRORS ...] Error analysis. Specify three numbers: number of replicates (int),  average linewidth of CS (ppm) and average linewidth of DC (kHz).
44  --quickfit QUICKFIT [QUICKFIT ...]     Min. shift, max. shift, min. couple, max. couple. Explore combinations of tau and order for best fit bounds.
24  --procs CPUs       Number of CPUs {32}.

24  CUSTOM PARAMETER   Use a custom parameter"""
#24  -n NRES            Number of residues (18 or length of --s)

non_used="""24  --out_log OUT_LOG  Filename to save log file with per-residue shifts and couplings {pisa_log.dat}
28  --out_wave OUT_WAVE    Filename to save continuous wheel of simulated shifts and couplings {pisa_wave.dat}
24  --out_fit OUT_FIT  Filename to save fit score for every tau, rho0 and order tested (pisa_fit.dat)
"""
# split arguments
arg_section_types = ['GENERAL', 'ANGLES & LENGTHS', 
                      'FITTING', 'CUSTOM'] #  'COUPLINGS', 
arg_sections = arg_all.split('\n\n')
#arg_lines = arg_all.split('\n')
arg_section_list = []
arg_list = []
#for i in range(len(arg_lines)):
for i in range(len(arg_sections)):
  arg_section_list.append([])
  arg_lines = arg_sections[i].split('\n')
  for j in range(len(arg_lines)):
    arg_line = arg_lines[j]
    desc_len = int(arg_line[0:2])
    arg = arg_line[2:desc_len-1].strip()
    arg_desc = arg_line[desc_len-1:].strip()
    arg_list.append([arg, arg_desc])
    arg_section_list[-1].append([arg, arg_desc])
  
# log column dictionary
col_dict = {'resname':0, 'index':1, 'rho':2, 'shift_calc':3, 'coupling_calc':4, \
        'shift_exp':5, 'coupling_exp':6, 'score':7, 'shift_raw':8, 'coupling_raw':9}

AAA_dict = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
     'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
     'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W',
     'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}
A_dict = {'C': 'CYS', 'D': 'ASP', 'S': 'SER', 'Q': 'GLN', 'K': 'LYS',
     'I': 'ILE', 'P': 'PRO', 'T': 'THR', 'F': 'PHE', 'N': 'ASN',
     'G': 'GLY', 'H': 'HIS', 'L': 'LEU', 'R': 'ARG', 'W': 'TRP',
     'A': 'ALA', 'V':'VAL', 'E': 'GLU', 'Y': 'TYR', 'M': 'MET'}

  
def get_value(lines, key, idx1=None, idx2=None):
  if len(key) < 3: return False, []   # A key should be longer than 3 characters
  iStart, iEnd = 0, len(lines)
  if idx1 != None: iStart = idx1
  if idx2 != None: iEnd = idx2
  
  for i in range(iStart, iEnd):
    line = lines[i]
    if len(line) < len(key): continue
    if line[0:len(key)] != key: continue
    temp = wlutil.replace_all(line[len(key):], ['[',']','(',')',','], [' '])
    return True, temp.split()
  return False, []

def read_text_file(text_file):
  if not os.path.exists(text_file):
    return False, []
    
  f = open(text_file)
  lines = f.readlines()
  f.close()
  return True, lines
  
class bagel_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'PISA-SPARKY: automated PISEMA analysis')
    
    self.create_ui()

    self.residue_num = None
    self.selected_peaks = []
    self.pisa_result = None

  def create_ui(self):
  
    user_name_ef, user_email_ef, user_seq_ff = wlutil.user_and_seq(self, OPTIONAL=True)
    self.user_name = user_name_ef.variable
    self.user_email = user_email_ef.variable
    self.user_seq = user_seq_ff.variable # this is just file
    self.fasta = '' # this is real fasta sequence
    self.first_seq = 1
    
    # PISEMA Spectrum
    self.sp = sputil.spectrum_menu(self.session, self.top, 'PISEMA spectrum: ')
    self.sp.frame.pack(side = 'top', fill = 'both', expand = 0)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    

    # Arguments
    arg_frm = Tkinter.Frame(self.top)
    arg_frm.pack(side = 'top', anchor = 'w')
    self.arg_frm = arg_frm
    
    # make arg types
    # general, angle length, fitting, dc, custom
    arg_section_om = tkutil.option_menu(arg_frm, "Argument type: ", arg_section_types)
    arg_section_om.frame.pack(side = 'top', anchor = 'nw')
    arg_section_om.add_callback(self.arg_section_changed_cb)
    self.arg_om_list = []
    for i in range(len(arg_section_types)):
      type_list = []
      for j in range(len(arg_section_list[i])):
        type_list.append(arg_section_list[i][j][0])
        type_list.append('    ' + arg_section_list[i][j][1])
      arg_om = tkutil.option_menu(arg_frm, "Arguments: ", type_list)
      arg_om.frame.pack(side = 'top', anchor = 'nw')
      arg_om.add_callback(self.argument_changed_cb)
      self.arg_om_list.append([arg_section_types[i], arg_om])
    self.arg_section_om = arg_section_om
    self.arg_om_dict = dict(self.arg_om_list)

    # Parameters
    param_frm = Tkinter.Frame(self.top)
    param_frm.pack(side = 'top', anchor = 'w')

    self.param_frm = param_frm
    self.arg_param_ef = tkutil.entry_field(param_frm, 'Parameter', initial = '', \
                              width = 30)
    self.arg_param = self.arg_param_ef.variable
    self.arg_param_ef.frame.pack(side = 'top', anchor = 'w')
    self.arg_desc = Tkinter.Label(param_frm, anchor = 'nw')
    self.arg_desc.pack(side = 'top', anchor = 'w')

    # Buttons
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    

    self.br = tkutil.button_row(self.top,
         ('Append', self.add_cb),
         ('Update', self.update_argument_cb),
         ('Delete', self.delete_cb),
         ('Clear', self.clear_cb),
         ('Submit', self.submit_cb),
         ('Copy', self.copy_cb),
         ('Close', self.close_cb),
         )
         
    self.br.frame.pack(side = 'top', fill = 'both', expand = 0)     
    tkutil.create_hint(self.br.buttons[0], \
                'Add new argument for running PISA-SPARKY.')
    tkutil.create_hint(self.br.buttons[1], 'Update current argument.')
    tkutil.create_hint(self.br.buttons[2], 'Delete a selected argument.')
    tkutil.create_hint(self.br.buttons[3], 'Delete all arguments.')
    tkutil.create_hint(self.br.buttons[4], 'Submit a PISA-SPARKY job.')
    tkutil.create_hint(self.br.buttons[5], \
                'Copy a pisa.py script in the clipboard.')

    # Argument list
    self.listbox = tkutil.scrolling_list(self.top, 'Argument list', 8, \
                                          xscrollbar=True)
    self.listbox.frame.pack(side='top', fill = 'both', expand = 1)
    self.listbox.listbox.bind('<ButtonRelease-1>', self.select_arg_cb)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    # Job ID
    token_frame = Tkinter.Frame(self.top, width = 600, height = 25)
    token_frame.pack(side='top', anchor='w')
    token_ef = tkutil.entry_field(token_frame, 'Job ID: ', initial = '', \
                                  width = 20)
    token_ef.frame.pack(side = 'left', anchor = 'w', expand = 0)
    self.token = token_ef.variable
    self.br2 = tkutil.button_row(token_frame,
        ('Check', self.check_wrap_cb),
        ('Browse...', self.bagel_browse_cb),
        )      
    self.br2.frame.pack(side = 'top', anchor = 'e', expand = 0)
    tkutil.create_hint(self.br2.buttons[0], \
                      'Check PISA.py job status and import the results.')
    tkutil.create_hint(self.br2.buttons[1], \
                      'Import the results in the local machine.')
    self.arg_section_changed_cb('GENERAL')
    
    self.notice_text = Tkinter.StringVar()
    self.notice_text.set("* Results will be sent to the user email if provided.")
    self.notice = Tkinter.Label(self.top, textvariable = self.notice_text, 
                                          anchor = 'w', justify = 'left')
                                          
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    self.notice.pack(side = 'bottom', anchor = 'w')   

    self.add_default_parameters()
  # -----------------------------------------------------------------------------
  # update argument with the current parameter
  def update_argument_cb(self):
    self.add_or_update_argument(0)
  # -----------------------------------------------------------------------------
  # 
  def add_default_parameter(self, param):
    idx, setting = self.get_param_value_or_default(param.split()[0], \
                                        default = True, short = True)
    if idx != -1:
      self.listbox.delete_by_number(idx)
    # update setting
    param_line = '%s %s' % (param.split()[0], setting)
    if idx == -1:
      self.listbox.append(param_line, (param_line, param, setting))
    else:
      self.listbox.insert(idx, param_line, (param_line, param, setting))

  # -----------------------------------------------------------------------------
  # we will add default parameters for handy modification
  def add_default_parameters(self):
    param_list = ['-t', '-r', '--flip', '-f']
    for param in param_list:
      self.add_default_parameter(param)

  # -----------------------------------------------------------------------------
  def select_arg_cb(self, event):
    line_data = self.listbox.selected_line_data()[0]
    idx, setting = self.get_param_value_or_default(line_data[1])
    
    for i in range(len(arg_section_types)):
      for j in range(len(arg_section_list[i])):
        if arg_section_list[i][j][0].split()[0] == line_data[1]:
          self.arg_section_om.variable.set(arg_section_types[i])
          self.arg_om_list[i][1].variable.set(arg_section_list[i][j][0])

    pass
  # -----------------------------------------------------------------------------
  # Change argument parameters interactively
  def arg_section_changed_cb(self, section_type):
    cur_sec = section_type
    sec_idx = arg_section_types.index(cur_sec)
    
    for i in range(len(arg_section_types)):
      if i != sec_idx:    self.arg_om_list[i][1].frame.pack_forget()
      else:       self.arg_om_list[i][1].frame.pack(side = 'top', anchor = 'nw')
    self.argument_changed_cb(arg_section_list[sec_idx][0][0])
    
  def argument_changed_cb(self, arg_type):
    cur_om = self.arg_om_dict[self.arg_section_om.get()]
    cur_param = arg_type
    for i in range(len(arg_list)):
      if cur_param in arg_list[i]: break
      if arg_list[i][1].find(cur_param.strip()) != -1: 
        cur_param = arg_list[i][0]
        cur_om.set(cur_param)
        cur_om.menubutton['text'] = cur_param
        break

    # parameter boxes depending on current params
    self.make_param(cur_param)
    self.arg_desc['text'] = arg_list[i][1]
    
  # -----------------------------------------------------------------------------
  #
  def get_param_value_or_default(self, param, default=False, short=False):
    # first, check if already set in scrolling list
    # if not, bringing default value from arg_list
    # line_data will have
    # (text shown, parameter name, parameters)
    iFound = -1
    if default != True:
      for i in range(len(self.listbox.line_data)):
        if short != True:
          if self.listbox.line_data[i][1] == param:
            return i, self.listbox.line_data[i][2]
        else:
          if self.listbox.line_data[i][1].strip()[0] == param:
            return i, self.listbox.line_data[i][2]
    # this parameter is not in the scrolling list
    # then we will just use default values encapsulated in brackets
    iStart = iEnd = -1
    szParam  = ''
    for i in range(len(arg_list)):
      arg = arg_list[i][0]
      if short:
        arg = arg.split()[0]
      if arg == param:
        desc = arg_list[i][1]
        # do we have default values?
        iStart = desc.find('{')
        iEnd = desc.find('}')
        if iStart != -1 and iEnd != -1:
          szParam = desc[iStart+1:iEnd]
          break
    return -1, szParam

  # -----------------------------------------------------------------------------
  #    
  def make_param(self, param):
    #self.arg_param_ef.label['text'] = param
    # get current parameter value
    idx, param_value = self.get_param_value_or_default(param)
    if param != '--negative_dc' and param != '--explore':
      self.arg_param.set(param_value)
    else:
      self.arg_param.set('N/A')
  # -----------------------------------------------------------------------------
  # get sequence
  def get_sequence(self, seq_file):
    readSeq = myseq.ReadSequenceFromFile(seq_file)
    oneline = ''
    for seq in readSeq:
      oneline = oneline+seq[1]
    return (oneline, readSeq[0][0])

  # -----------------------------------------------------------------------------
  # Check sequence
  def check_sequence(self):
    # check if sequence file is set. If not, complain and return
    seq_file = self.user_seq.get()
    if seq_file == '' or not os.path.exists(seq_file):
      tkMessageBox.showerror('Error', 'Please set a sequence file first.')
      return False
    # check if sequence is valid.
    seq, first_seq = self.get_sequence(seq_file)
    if 'X' in seq:
      tkMessageBox.showerror('Error', 'Incorrect sequence file: %s' % (seq))
      return False
    self.fasta = seq
    self.first_seq = first_seq
    
    return True
  # -----------------------------------------------------------------------------
  # 0: update, 1: new
  def add_or_update_argument(self, mode):
    arg_om = self.arg_om_dict[self.arg_section_om.get()]
    cur_param = arg_om.get().split()[0]
    if not cur_param in ['--negative_dc']:
      cur_value = self.arg_param.get()
    else:
      cur_value = ''
    
    # check if this parameter makes sense
    # angles
    if cur_param in ['-t', '-r', '--phi', '--psi', '--beta', '--aCaCN', \
                '--aCNCa', '--aNCaC', '--aCaNH', '--flip']:
      try:
        temp = float(cur_value)
      except:
        tkMessageBox.showerror('Error', 'Angle in degree expected.')
        return
      # order
    elif cur_param == '-o':
      try:
        temp = float(cur_value)
        if temp > 1.0: temp = float('error')
      except:
        tkMessageBox.showerror('Error', 'Numerical value under 1 expected.')
        return
    elif cur_param in ['--seq_start', '--rho_start', '-n', '--procs']:
      try:
        temp = int(cur_value)
        if (temp < self.first_seq or temp > len(self.fasta) + self.first_seq - 1) and \
            (cur_param != '-n' and cur_param != '--procs'): temp = int('error')
        elif cur_param == '-n' and temp > len(self.fasta): temp = int('error')
        #elif cur_param == '--procs' and temp < 1 and temp > multiprocessing.cpu_count():
        elif cur_param == '--procs' and temp < 1 and temp > 32:  
          tkMessageBox.showerror('Error', 'Available CPU setting restrained between 1 and 32.')
          #tkMessageBox.showerror('Error', 'Available CPU setting is 1 to %d.' % \
          #                      (multiprocessing.cpu_count()))
          return
      except:
        tkMessageBox.showerror('Error', 'Proper numerical value expected.')
        return
    elif cur_param in ['--dc', '--period', '--bCaC', '--bCN', '--bNCa', '--scalar']:
      try:
        temp = float(cur_value)
      except:
        tkMessageBox.showerror('Error', 'Proper numerical value expected.')
        return
    # three numbers
    elif cur_param == '--pas' or cur_param == '--errors':
      try:
        temp_list = cur_value.split()
        if len(temp_list) != 3: temp = float('error')
        value_list = map(lambda b: float(b), temp_list)
      except:
        tkMessageBox.showerror('Error', 'Three numerical values expected.')
        return
    # four numbers    
    elif cur_param == '--quickfit':
      try:
        temp_list = cur_value.split()
        if len(temp_list) != 4: temp = float('error')
        value_list = map(lambda b: float(b), temp_list)
      except:
        tkMessageBox.showerror('Error', 'Four numerical values expected.')
        return
    elif cur_param in ['--fit_tau', '--fit_rho0', '--fit_order']: 
      try:       # min, max and step.
        temp_list = cur_value.split()
        if len(temp_list) != 3: temp = float('error')
        value_list = map(lambda b: float(b), temp_list)
        if value_list[1] < value_list[0] or value_list[1] < value_list[2]:
          tkMessageBox.showerror('Error', \
                      'Max value should be larger than min and step values.')
          return
        if cur_param == '--fit_order':
          if value_list[0] < 0 or value_list[0] > 1:
            tkMessageBox.showerror('Error', \
                        'Min and max values should be between 0 and 1.')
            return
      except:
        tkMessageBox.showerror('Error', 'Three numerical values expected.')
        return
    elif cur_param in ['--fit_only', '--fit_exclude', '--show_only']:
      temp = sputil.process_pymol_residue_range(cur_value)
      if temp[0] == False:
        tkMessageBox.showerror('Error', \
              'Residue numbers are expected (e.g. 1-10+14-20).')
        return
      if min(temp[1]) < self.first_seq or \
          max(temp[1]) > len(self.fasta) + self.first_seq:
        tkMessageBox.showerror('Error', 'Residue numbers are expected.')
        return
      cur_value = ''
      for val in temp[1]:
        cur_value = cur_value + ' %d' % (val)
      cur_value.strip()

    idx, setting = self.get_param_value_or_default(cur_param)
    if idx != -1 and cur_param.split()[0] != '--negative_dc' and cur_param.split()[0] != '--explore':
      self.listbox.delete_by_number(idx)
    # update setting
    if cur_param.split()[0] != '--negative_dc' and cur_param.split()[0] != '--explore':
      param_line = '%s %s' % (cur_param.split()[0], cur_value)
    else:
      param_line = cur_param.split()[0]
    if mode == 1 or idx == -1:
      self.listbox.append(param_line, (param_line, cur_param, cur_value))
    else:
      self.listbox.insert(idx, param_line, (param_line, cur_param, cur_value))
  #-----------------------------------------------------------------------------
  # Adding a current parameter
  def add_cb(self):
    if not self.check_sequence(): return
    self.add_or_update_argument(1)
      
  # -----------------------------------------------------------------------------
  # Just delete current
  def delete_cb(self):
    selects = self.listbox.delete_selected()
  # -----------------------------------------------------------------------------
  #    
  def clear_cb(self):
    self.listbox.clear()
  # -----------------------------------------------------------------------------
  #    
  def build_peak_list(self):
    # check pisema spectra is legit.
    spec = self.sp.spectrum()
    if spec == None:
      tkMessageBox.showerror('Error', 'PISEMA spectrum not set yet.')
      return (False, [])
    if spec.dimension != 2:
      tkMessageBox.showerror('Error', 'Selected spectrum does not seem like a PISEMA.')
      return (False, [])

    # check if any peaks are selected
    if len(spec.selected_peaks()) > 2:
      peaks = spec.selected_peaks()
    else:
      peaks = spec.peak_list()
    
    # get assignment 
    peak_list = ''

    assigned_list = list(map(lambda x: [], range(1000)))
    for peak in peaks:
      if peak.is_assigned == 0: continue
      parsed = sputil.parse_assignment_entirely(peak.assignment)
      if parsed == None: continue
      if parsed[0][1] < 1 or parsed[0][1] > 999: continue
      if len(assigned_list[parsed[0][1]]) != 0:
        tkMessageBox.showerror('Error', 'Only one assignment per residue allowed.')
        return (False, [])
      min_freq = min(peak.frequency)
      max_freq = max(peak.frequency)
      assigned_list[parsed[0][1]] = ['%s%d' % (parsed[0][0], parsed[0][1]), \
                                        max_freq, min_freq]

    for i in range(0, 1000):
      if len(assigned_list[i]) != 0: 
        line = '%-8s %-8.3f %-8.3f\n' % (assigned_list[i][0], \
                      assigned_list[i][1], assigned_list[i][2])
        peak_list = peak_list + line
    return  (True, peak_list)
  # -----------------------------------------------------------------------------
  #    
  def submit_cb(self):
    if not self.check_sequence(): return

    szUserName = self.user_name.get()
    szUserEmail = self.user_email.get()
    
    if szUserName == '':  szUserName = 'anonymous'
    if (szUserEmail == '') or (szUserEmail.find('@') == -1):
      szUserEmail = 'nobody@nobody.com'      
      
    fields = [['name', szUserName], ['email', szUserEmail]]
    contents = []
    
    tf, prefix, postfix = self.make_script('single')
    if tf == False:
      tkMessageBox.showerror('Error', 'Making a PISA.py script failed: ' + \
                                        prefix + postfix)
      return
    # build peak list if peak option associated.
    tf = False
    idx, value = self.get_param_value_or_default('-f')
    peak_list = ''
    if idx != -1: # we need to make script
      tf, peak_list = self.build_peak_list()
      if tf == False: return
      contents.append( ['peak_file', value, peak_list] ) # add peak lists
      fields.append( ['peakfile', value])
    fields.append( ['script', prefix + postfix])
    
    random.seed()
    token = time.strftime("%y%m%d_%H%M%S_") + "%06d" % random.randrange(0,1000000)
    fields.append (['nmrfamsparky_token', token])
    self.token.set(token)
    
    bagel_url = 'i-pine.nmrfam.wisc.edu'
    bagel_selector = '/cgi-bin/bagel_uploader.cgi'
    
    text=posthtml.post_multipart(bagel_url, bagel_selector, fields, contents)
    tkMessageBox.showinfo('PISA.py job sumitted.', 
                          'PISA.py job submitted. ' + \
                          'Check your result in this window or in your email inbox after a few seconds.')
  # -----------------------------------------------------------------------------
  # copy bagel script in the clipboard
  def copy_cb(self):
    if not self.check_sequence(): return

    tf, prefix, postfix = self.make_script('multi')
    bagel_script = prefix + postfix
    if tf == False:
      tkMessageBox.showerror('Error', 'Making a pisa.py script failed: ' + \
                                        bagel_script)
    else:
      #self.session.tk.clipboard_clear()
      #self.session.tk.clipboard_append(prefix + postfix)
      tkutil.write_to_clipboard(self.session, prefix+postfix)

      # build peak list if peak option associated.
      tf = False
      idx, value = self.get_param_value_or_default('--peaks')
      peak_list = ''
      if idx != -1: # we need to make a peak list
        tf, peak_list = self.build_peak_list()
        if tf == False: 
          tkMessageBox.showerror('Error', 'Making a pisa.py script failed: making a peak list failed.')
          return
        bagel_dir = os.path.join(self.session.project.sparky_directory, 'PISA')
        if not os.path.exists(bagel_dir):
          os.makedirs(bagel_dir)
        bagel_peak_file = os.path.join(bagel_dir, value)
        f = open(bagel_peak_file,'w')
        f.write(peak_list)
        f.close()
        tkMessageBox.showinfo('pisa.py script', \
                      '"%s" in the clipboard. A pisa.py peak list is %s.' % \
                      (bagel_script, bagel_peak_file))
      else:
        tkMessageBox.showinfo('pisa.py script', '"%s" in the clipboard.' % \
                              (bagel_script))
  # -----------------------------------------------------------------------------
  # make a bagel script- returns (T/F, prefix, postfix). single line or multi line
  def make_script(self, line_ver='single'):
    prefix = 'python3 pisa.py'
    postfix = ''
    
    try:
      for i in range(len(self.listbox.line_data)):
        cur_param = self.listbox.line_data[i][0]
        if cur_param.find('CUSTOM') == 0:
          temp = cur_param.replace('CUSTOM', ' ')
          temp2 = temp.replace('PARAMETER', ' ')
          cur_param = temp2.strip()
        postfix = postfix + '    ' + cur_param 
        if line_ver != 'single':  postfix = postfix + ' \\\n'
    except:
      return (False, '', '')

    # add sequence
    postfix = postfix + '    --seq_start %d' % (self.first_seq)
    if line_ver != 'single':  postfix = postfix + ' \\\n'    
    postfix = postfix + '    -s %s' % (self.fasta)

    return (True, prefix, postfix)
  # -----------------------------------------------------------------------------
  #    
  def check_wrap_cb(self):  
    self.check_cb(1)
  # -----------------------------------------------------------------------------
  #    
  def bagel_browse_cb(self):
    self.check_cb(2)
  # -----------------------------------------------------------------------------
  #    
  def check_cb(self, clicked):
    sparky_proj_dir = self.session.project.sparky_directory
    bagel_root_dir = os.path.join(sparky_proj_dir, 'PISA')

    if clicked == 2: # directory mode
      import tkFileDialog
      bagel_dir = tkFileDialog.askdirectory(initialdir = sparky_proj_dir,
                                title = 'Select a PISA.py output directory',
                                mustexist = 1)
      if bagel_dir == '': return
      self.token.set(bagel_dir)
      
    if self.token.get() == '':
      if clicked == 1:
        tkMessageBox.showwarning('pisa.py job.', \
                              'Please set pisa.py job ID or directory.')
      return
    bagel_job_id = self.token.get()
          
    # retrieve BAGEL URL + token path.
    try:
      import urllib2
    except:
      tkMessageBox.showerror('urllib2', \
        'You do not have openssl installed or set properly.')
      return

    bagel_root_url = 'http://pine3.nmrfam.wisc.edu/bagel/queue/%s/' % \
                      (self.token.get())
    bagel_token_url = bagel_root_url + 'token_status.txt'
    bagel_result_url = bagel_root_url
    
    if clicked == 2:
      bagel_root_url = 'file://%s/' % (bagel_dir)
      bagel_result_url = bagel_root_url
      
    bagel_status_lines = ['waiting',]
    if clicked == 1:
      bagel_dir = os.path.join(bagel_root_dir, bagel_job_id)
      try: 
        bagel_status = urllib2.urlopen(bagel_token_url, timeout=2)
        bagel_status_lines = bagel_status.readlines()
        if len(bagel_status_lines) == 0:
          tkMessageBox.showerror('Retrieve error', \
            'Unknown error. Please check your email if you have submitted.')      
      except:
        tkMessageBox.showerror('Retrieve error', \
            'It seems your job is not finished yet.')
        return    

    if clicked == 2 or bagel_status_lines[0].strip() == 'finished':
      bagel_wave_url = os.path.join(bagel_result_url, 'pisa_wave.dat')
      bagel_log_url = os.path.join(bagel_result_url, 'pisa_log.dat')
      bagel_fit_url = os.path.join(bagel_result_url, 'pisa_fit.dat')
      bagel_peak_url = os.path.join(bagel_result_url, 'pisa_peaks.list')
      bagel_wave_path = os.path.join(bagel_dir, 'pisa_wave.dat')
      bagel_log_path = os.path.join(bagel_dir, 'pisa_log.dat')
      bagel_fit_path = os.path.join(bagel_dir, 'pisa_fit.dat')
      bagel_peak_path = os.path.join(bagel_dir, 'pisa_peaks.list')
      
      try:
        if not os.path.exists(bagel_root_dir):
          os.makedirs(bagel_root_dir)        
        if not os.path.exists(bagel_dir):
          os.makedirs(bagel_dir)
      except:
        tkMessageBox.showerror("Error", \
            "PISA directory could not be created. ")
        return

      try:
        # wave
        bagel_response = urllib2.urlopen(bagel_wave_url, timeout=15)
        bagel_html = bagel_response.read()
        f = open(bagel_wave_path, 'w')
        f.write(bagel_html)
        f.close()

        # log
        bagel_response = urllib2.urlopen(bagel_log_url, timeout=15)
        bagel_html = bagel_response.read()
        f = open(bagel_log_path, 'w')
        f.write(bagel_html)
        f.close()
      except:
        tkMessageBox.showerror("Error", \
            "PISA results could not be retrieved. Your job has failed.")
        return
      
      try:
        # fit
        bagel_response = urllib2.urlopen(bagel_fit_url, timeout=15)
        bagel_html = bagel_response.read()
        f = open(bagel_fit_path, 'w')
        f.write(bagel_html)
        f.close()
      except:
        pass # fit is fine :-)

      try:
        # peaks  
        bagel_response = urllib2.urlopen(bagel_peak_url, timeout=15)
        bagel_html = bagel_response.read()
        if len(bagel_html) > 20:
          f = open(bagel_peak_path, 'w')
          f.write(bagel_html)
          f.close()
      except:
        pass # peak is fine :-)

      bagel_lines = bagel_html.split("\n")
      if len(bagel_lines) < 2:
        tkMessageBox.showerror("Error", "PISA results does not look good.")
        return
      d = show_check_dialog(self.session)
      d.load_bagel_results(bagel_dir, self.sp)

    elif clicked == 1 and bagel_status_lines[0].strip() == 'failed':    
      tkMessageBox.showerror("Error", "pisa.py failed.")

# -----------------------------------------------------------------------------
#    
def show_dialog(session):
  d = sputil.the_dialog(bagel_dialog, session)
  d.show_window(1)

class bagel_check_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'PISA RESULTS')

    # textbox- using scrolling_list
    self.textbox = tkutil.scrolling_list(self.top, 'Double-click to show the peak', 
                                          10, xscrollbar=True)
    #self.textbox.text['wrap'] = 'none'
    self.textbox.listbox['font'] = 'Courier 10'
    self.textbox.listbox.bind('<ButtonRelease-1>', self.select_residue_cb)
    self.textbox.listbox.bind('<Double-Button-1>', self.moveto_residue_cb)
    self.textbox.listbox['selectmode'] = 'extended'
    self.textbox.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # buttons
    self.br = tkutil.button_row(self.top,
         ('Save', self.save_cb),
         ('Draw a wheel', self.draw_cb),
         ('Plot Waves', self.plot_waves_cb),
         ('Export to CSV', self.export_csv_cb),
         ('Export Waves to CSV', self.export_waves_csv_cb),
         ('Export DC', self.export_dc_cb),
         ('PyMOL', self.pymol_cb),
         ('Close', self.close_cb),
         )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 0)     
    tkutil.create_hint(self.br.buttons[0], 'Save pisa.py results.')
    tkutil.create_hint(self.br.buttons[1], 'Draw a PISA wheel on the PISEMA spectrum.')
    tkutil.create_hint(self.br.buttons[2], \
      'Plot 15N shifts and dipolar couplings as a function of residue number.')
    tkutil.create_hint(self.br.buttons[3], 'Export all results in CSV format.')
    tkutil.create_hint(self.br.buttons[4], 'Export waves in CSV format.')
    tkutil.create_hint(self.br.buttons[5], 'Export DC constraints for PONDEROSA calculation.')
    tkutil.create_hint(self.br.buttons[6], 'Launch PyMOL and highlight selected residues.')
    tkutil.create_hint(self.br.buttons[7], 'Close.')
    
    self.bagel_spec = None
    self.bagel_dir = ''
    self.pdb_path = ''
    self.wave_path = ''
    self.log_path = ''
    self.shift_ini_path = ''
    self.dc_ini_path = ''
    self.fasta = ''
    self.init_seq = 1
    self.default_ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
  # -----------------------------------------------------------------------------
  # 
  def set_bagel_dir(self, bagel_dir):
    if not os.path.isdir(bagel_dir):
      tkMessageBox.showerror('Error', '%s directory not exists.' % (bagel_dir))
      return False
    wave_path = os.path.join(bagel_dir, 'pisa_wave.dat')
    log_path = os.path.join(bagel_dir, 'pisa_log.dat')
    if not os.path.exists(wave_path):
      tkMessageBox.showerror('Error', 'pisa_wave.dat not found.')
      return False
    if not os.path.exists(log_path):  
      tkMessageBox.showerror('Error', 'pisa_log.dat not found.')
      return False

    self.bagel_dir = bagel_dir
    self.wave_path = wave_path
    self.log_path = log_path
    self.job_id = os.path.basename(bagel_dir.rstrip(os.path.sep))
    self.pdb_path = os.path.join(bagel_dir, 'pisa.pdb')
    self.shift_ini_path = os.path.join(bagel_dir, 'pisa_shift_plot.ini')
    self.dc_ini_path = os.path.join(bagel_dir, 'pisa_dc_plot.ini')
    return True
  # -----------------------------------------------------------------------------
  # 
  def load_bagel_results(self, bagel_dir, bagel_spec):
    self.set_bagel_dir(bagel_dir)
    self.bagel_spec = bagel_spec
    self.read_log_file()

  # -----------------------------------------------------------------------------
  #    
  def save_cb(self):
    path = tkutil.save_file(self.top, 'Save PISA outputs', 'pisa_directory')
    if path:
      #contents = self.textbox.get(0.0, 'end')
      content = ''
      for line_data in self.textbox.line_data:
        content = content + line_data[0] + '\n'
      f = open(path, 'w')
      f.write(contents)
      f.close()
  # -----------------------------------------------------------------------------
  # Parse pisa log
  def parse_pisa_log(self):
    tf, lines = read_text_file(self.log_path)
    if tf == False:
      return False, ['Drawing failed.']
    lines2 = []
    for line in lines:
      if len(line.strip()) == 0: continue
      if line.strip()[0] == '#':
        if line.find('# Importing sequence:') != -1:
          self.fasta = line.strip().split()[-1]
        if line.find('# Sequence starts') != -1:
          try:
            self.first_seq = int(line.strip().split()[-1])
          except:
            self.first_seq = 1
        continue
      lines2.append(line.strip())

    #result_list = list(map(lambda x: [], range(1000)))
    result_list = []
    for line in lines2:
      col_list = line.split()
      a = col_list[0][0]
      aaa = A_dict[col_list[0][0]]
      seqidx = int(col_list[0][1:])
      temp_list = col_list + [aaa, a, seqidx]
      #result_list[seqidx] = temp_list
      result_list.append(temp_list)
    return True, result_list
  # -----------------------------------------------------------------------------
  # Parse pisa wave
  def parse_pisa_wave(self):
    tf, lines = read_text_file(self.wave_path)
    if tf == False:
      return False, ['Drawing failed.']
    lines2 = []
    for line in lines: # seq (x), rho, ppm, hz
      if len(line.strip()) == 0: continue
      if line.strip()[0] == '#': continue
      lines2.append(line.strip().split())

    return True, lines2
  # -----------------------------------------------------------------------------
  # Extract pisa wave
  def extract_pisa_wave(self, wave_lines, min_seqid, max_seqid):
    wave_list = []
    for line in wave_lines:
      if float(line[0]) < min_seqid or float(line[0]) > max_seqid: continue
      wave_list.append(line)
    return wave_list

  # -----------------------------------------------------------------------------
  #    
  def draw_cb(self):
    tf, org_wave_lines = self.parse_pisa_wave()
    if tf == False or len(org_wave_lines) < 3:
      tkMessageBox.showerror('Error', 'pisa_wave.dat does not look valid.')
      return tf, org_wave_lines

    tf, org_log_lines = self.parse_pisa_log()
    if tf == False or len(org_log_lines) < 3:
      tkMessageBox.showerror('Error', 'pisa_log.dat does not look valid.')
      return tf, org_log_lines  

    if self.bagel_spec == None or self.bagel_spec.spectrum() == None:
      tkMessageBox.showerror('Error', 'PISEMA spectrum is not selected.')
      return tf, None  

    sp = self.bagel_spec.spectrum()

    iCrude = 1 
    #iDiv = 10
    iDiv = 11
    
    for i in range(len(org_wave_lines)/iCrude):
      wave = org_wave_lines[iCrude*i]
      try:
        wave2 = org_wave_lines[iCrude*(i+1)]
      except:
        wave2 = org_wave_lines[iCrude*(i+1)-1]
      x = float(wave[2])
      y = float(wave[3])
      x2 = float(wave2[2])
      y2 = float(wave2[3])
      xdiff = (x2-x) / float(iDiv)
      ydiff = (y2-y) / float(iDiv)

      #for j in range(0, iDiv):
      #  x3 = x + xdiff * (j-0.5)
      #  y3 = y + ydiff * (j-0.5)
      #  x4 = x + xdiff * (j+0.5)
      #  y4 = y + ydiff * (j+0.5)
      #  if sp.region[1][0] > sp.region[1][1]: # check max ppm 
      #    line = sparky.Line(sp, (max(x3,y3), min(x3,y3)), 
      #                          (max(x4,y4), min(x3,y3)))
      #    line2 = sparky.Line(sp, (max(x4,y4), min(x3,y3)), 
      #                          (max(x4,y4), min(x4,y4)))
      #  else:
      #    line = sparky.Line(sp, (min(x3,y3), max(x3,y3)), 
      #                          (min(x4,y4), max(x3,y3)))
      #    line2 = sparky.Line(sp, (min(x4,y4), max(x3,y3)), 
      #                          (min(x4,y4), max(x4,y4)))
      if sp.region[1][0] > sp.region[1][1]:
        line = sparky.Line(sp, (max(x,y), min(x,y)), 
                                (max(x2,y2), min(x2,y2)))
      else:
        line = sparky.Line(sp, (min(x,y), max(x,y)), 
                                (min(x2,y2), max(x2,y2)))
      line.color = 'coral'
      line.selected = 0
      #  line2.color = 'coral'
      #  line2.selected = 0
    
    # draw peak markers
    for i in range(len(org_log_lines)):
      log_list = org_log_lines[i]
      Nppm = float(log_list[col_dict['shift_calc']])
      DCppm = float(log_list[col_dict['coupling_calc']])
      a = log_list[-2]
      seqidx = log_list[-1]
      if sp.region[1][0] > sp.region[1][1]: # check max ppm 
        pk = sp.place_peak(( max(DCppm, Nppm), min(DCppm, Nppm) ))
      else:
        pk = sp.place_peak(( min(DCppm, Nppm), max(DCppm, Nppm) ))

      #pk.assign(0, '%s%d_s' % (a, seqidx), sp.nuclei[0][-1]) # w/ simulation tag
      #pk.assign(1, '%s%d_s' % (a, seqidx), sp.nuclei[1][-1]) # w/ simulation tag
      pk.selected = 0
      pk.note = 'PISA fitting [%s]' % (self.job_id)
      pk.color = 'coral'
      #lbl = pk.show_assignment_label()
      lbl = pk.show_label('%s%d_s' % (a, seqidx))
      lbl.color = 'coral'
      lbl.selected = 0
    tkMessageBox.showinfo('Finished', \
              'You can select a wheel by "sN" and markers by "sB"')

  # -----------------------------------------------------------------------------
  # Export DC constraints for PONDEROSA-C/S calculation
  def export_dc_cb(self):
    tf, org_log_lines = self.parse_pisa_log()
    if tf == False or len(org_log_lines) < 3:
      tkMessageBox.showerror('Error', 'pisa_log.dat does not look valid.')
      return tf, org_log_lines

    # Largest sequence number + something..
    max_seqnum = self.first_seq + len(self.fasta) - 1 
    for i in range(1,10):
      ani_num = max_seqnum + i
      if ani_num % 10: break

    rdc_temp="""#Orientation  Magnitude  Rhombicity  ORI residue number
       1        999      999           %d
# First atom Second atom  RDC Error Weight Orientation
$CONTENT""" % (ani_num)

    content = ''
    for i in range(len(org_log_lines)):
      log_list = org_log_lines[i]
      if log_list[col_dict['coupling_raw']] == 'nan': continue
      try:
        DCppm = float(log_list[col_dict['coupling_raw']])
      except:
        continue
      a = log_list[-2]
      aaa = myseq.a2aaa(a)
      if aaa == 'XXX': continue
      seqidx = log_list[-1]
      line = '%3d %3s    H    %3d %3s    N %10.2f 1.000   1.000   1\n' % \
              (seqidx, aaa, seqidx, aaa, DCppm)
      content = content + line
    rdc_temp = rdc_temp.replace('$CONTENT', content)
    # file dialog
    path = tkutil.save_file2(self.top, 'Save a DC file', 'pisema_rdc',
            '.rdc', [('DC file', '*.rdc')])

    f = open(path, 'w')
    f.write(rdc_temp)
    f.close()

  # -----------------------------------------------------------------------------
  # Making a NDPPLOT and open. 
  # There are two kinds: fit (N vs DC), wave (seqid vs DC or N)
  def draw_pisa_log(self):

    ndpplot_prefix = """[GENERAL_START]
TITLE=$TITLE
XLABEL=$XLABEL
YLABEL=$YLABEL
XMIN=$XMIN
XMAX=$XMAX
YMIN=$YMIN
YMAX=$YMAX
XSCALE=FLOAT
[GENERAL_END]
[SERIES1_START]
NAME=$SERIES1_NAME
PLOTTYPE=LINE
$SERIES1_COUNT
$SERIES1_COLOR
$SERIES1_DATA
[SERIES1_END]
[SERIES2_START]
NAME=$SERIES2_NAME
PLOTTYPE=DOT
$SERIES2_COUNT
$SERIES2_COLOR
$SERIES2_DATA
[SERIES2_END]"""

    tf, log_lines = self.parse_pisa_log()
    if tf == False or len(log_lines) < 3:
      return tf, log_lines
    tf, org_wave_lines = self.parse_pisa_wave()
    if tf == False or len(org_wave_lines) < 3:
      return tf, org_wave_lines

    min_seqid = log_lines[0][-1]
    max_seqid = log_lines[-1][-1]
    min_shift = 9999
    max_shift = -9999
    min_shift2 = 9999
    max_shift2 = -9999
    min_dc = 9999
    max_dc = -9999
    min_dc2 = 9999
    max_dc2 = -9999
    wave_lines = self.extract_pisa_wave(org_wave_lines, min_seqid, max_seqid)

    # draw waves- exp data- dot, fit data- line
    # shift wave
    shift_prefix = ndpplot_prefix.replace('$TITLE', 'PISA 15N SHIFT WAVE')
    shift_prefix = shift_prefix.replace('$XLABEL', 'Residue number')
    shift_prefix = shift_prefix.replace('$YLABEL', '15N shift (ppm)')
    shift_prefix = shift_prefix.replace('$SERIES1_NAME', 'SHIFT_CALC')
    shift_prefix = shift_prefix.replace('$SERIES2_NAME', 'SHIFT_EXP')

    # fitting data
    # count
    count_lines = 'COLORCOUNT=1\nDATACOUNT=%d' % (len(wave_lines))
    shift_prefix = shift_prefix.replace('$SERIES1_COUNT', count_lines)

    # data
    data_lines = ''
    iIdx = 1
    for wave in wave_lines:
      x = float(wave[0])
      y = float(wave[2])
      min_shift = min(min_shift, y)
      max_shift = max(max_shift, y)
      #line = 'DATA_%d=%f,%f,0,%f_%f_CALC' % (iIdx, x, y, x, y)
      line = 'DATA_%d=%f,%f,0,%f_%f' % (iIdx, x, y, x, y)
      if data_lines != '':
        data_lines = data_lines + '\n' + line
      else:
        data_lines = line
      iIdx = iIdx + 1
    shift_prefix = shift_prefix.replace('$SERIES1_DATA', data_lines) 

    # color
    color_line = 'COLOR_1=%d,%d,%f,%f,SILVER' % (min_seqid, max_seqid, min_shift, max_shift)
    shift_prefix = shift_prefix.replace('$SERIES1_COLOR', color_line)

    # with found min & max
    shift_prefix = shift_prefix.replace('$XMIN', '%f' % (min_seqid))
    shift_prefix = shift_prefix.replace('$XMAX', '%f' % (max_seqid))
    shift_prefix = shift_prefix.replace('$YMIN', '%f' % (min_shift))
    shift_prefix = shift_prefix.replace('$YMAX', '%f' % (max_shift))

    # exp data: SERIES2
    # we have to count for exp data because not always we have all the data from exp.
    data_lines = ''
    iIdx = 1
    for cur_seqid in range(min_seqid, max_seqid+1):
      idx = cur_seqid - min_seqid
      if len(log_lines[idx]) < 12: continue
      try:  
        nppm = float(log_lines[idx][col_dict['shift_exp']])
        if nppm < -9999 or nppm > 9999: continue
      except:
        continue # exp data can be none
      min_shift2 = min(min_shift2, nppm)
      max_shift2 = max(max_shift2, nppm)  
      #line = 'DATA_%d=%d,%f,0,%s%d_EXP' % \
      line = 'DATA_%d=%d,%f,0,%s%d' % \
              (iIdx, cur_seqid, nppm, log_lines[idx][-2], cur_seqid)
      if data_lines != '':
        data_lines = data_lines + '\n' + line
      else:
        data_lines = line
      iIdx = iIdx + 1
    # we have data count now.
    count_lines = 'COLORCOUNT=1\nDATACOUNT=%d' % (iIdx-1)
    shift_prefix = shift_prefix.replace('$SERIES2_COUNT', count_lines)
    shift_prefix = shift_prefix.replace('$SERIES2_DATA', data_lines) 
    color_line = 'COLOR_1=%d,%d,%f,%f,RED' % (min_seqid, max_seqid, min_shift2, max_shift2)
    shift_prefix = shift_prefix.replace('$SERIES2_COLOR', color_line)
    # save a file in a path
    f = open(self.shift_ini_path, 'w')
    f.write(shift_prefix)
    f.close()

    # copy wave_ini_path to openable position and launch ndpplot
    shutil.copyfile(self.shift_ini_path, self.default_ini_path)
    nmrfam.run_npdplot(self.session)
    time.sleep(3)

    # we need to wait a second
    # dc wave
    # DC wave
    dc_prefix = ndpplot_prefix.replace('$TITLE', 'PISA DIPOLAR COUPLING WAVE')
    dc_prefix = dc_prefix.replace('$XLABEL', 'Residue number')
    dc_prefix = dc_prefix.replace('$YLABEL', 'Dipolar coupling (kHz)')
    dc_prefix = dc_prefix.replace('$SERIES1_NAME', 'DC_CALC')
    dc_prefix = dc_prefix.replace('$SERIES2_NAME', 'DC_EXP')
    # data
    data_lines = ''
    iIdx = 1
    for wave in wave_lines:
      x = float(wave[0])
      y = float(wave[3])
      min_dc = min(min_dc, y)
      max_dc = max(max_dc, y)
      #line = 'DATA_%d=%f,%f,0,%f_%f_CALC' % (iIdx, x, y, x, y)
      line = 'DATA_%d=%f,%f,0,%f_%f' % (iIdx, x, y, x, y)
      if data_lines != '':
        data_lines = data_lines + '\n' + line
      else:
        data_lines = line
      iIdx = iIdx + 1
    # count
    count_lines = 'COLORCOUNT=1\nDATACOUNT=%d' % (iIdx-1)
    dc_prefix = dc_prefix.replace('$SERIES1_COUNT', count_lines)
    dc_prefix = dc_prefix.replace('$SERIES1_DATA', data_lines)
    # color
    color_line = 'COLOR_1=%d,%d,%f,%f,SILVER' % (min_seqid, max_seqid, min_dc, max_dc)
    dc_prefix = dc_prefix.replace('$SERIES1_COLOR', color_line)

    # with found min & max
    dc_prefix = dc_prefix.replace('$XMIN', '%f' % (min_seqid))
    dc_prefix = dc_prefix.replace('$XMAX', '%f' % (max_seqid))
    dc_prefix = dc_prefix.replace('$YMIN', '%f' % (min_dc))
    dc_prefix = dc_prefix.replace('$YMAX', '%f' % (max_dc))

    # exp data: SERIES2
    # we have to count for exp data because not always we have all the data from exp.
    data_lines = ''
    iIdx = 1
    for cur_seqid in range(min_seqid, max_seqid+1):
      idx = cur_seqid - min_seqid
      if len(log_lines[idx]) < 12: continue
      try:  
        dc = float(log_lines[idx][col_dict['coupling_exp']])
      except:
        continue # exp data can be none
      min_dc2 = min(min_dc2, dc)
      max_dc2 = max(max_dc2, dc)  
      #line = 'DATA_%d=%d,%f,0,%s%d_EXP' % (iIdx, cur_seqid, dc, log_lines[idx][-2], cur_seqid)
      line = 'DATA_%d=%d,%f,0,%s%d' % (iIdx, cur_seqid, dc, log_lines[idx][-2], cur_seqid)
      if data_lines != '':
        data_lines = data_lines + '\n' + line
      else:
        data_lines = line
      iIdx = iIdx + 1
    # we have data count now.
    count_lines = 'COLORCOUNT=1\nDATACOUNT=%d' % (iIdx-1)
    dc_prefix = dc_prefix.replace('$SERIES2_COUNT', count_lines)
    dc_prefix = dc_prefix.replace('$SERIES2_DATA', data_lines) 
    color_line = 'COLOR_1=%d,%d,%f,%f,RED' % (min_seqid, max_seqid, min_dc2, max_dc2)
    dc_prefix = dc_prefix.replace('$SERIES2_COLOR', color_line)
    # save a file in a path
    f = open(self.dc_ini_path, 'w')
    f.write(dc_prefix)
    f.close()

    # copy dc_ini_path to openable position and launch ndpplot
    shutil.copyfile(self.dc_ini_path, self.default_ini_path)
    nmrfam.run_npdplot(self.session)
  # -----------------------------------------------------------------------------
  #    
  def plot_waves_cb(self):
    if self.bagel_dir == '':  
      tkMessageBox.showerror('Error', 'PISA directory not set yet.')
      return # not yet set
    # read log
    if not os.path.exists(self.log_path):
      tkMessageBox.showerror('Error', 'pisa_log.dat file not exists.')
      return
    # read log file in
    result = self.draw_pisa_log()
    pass
    
  def export_csv_cb(self):
    if self.bagel_dir == '':  
      tkMessageBox.showerror('Error', 'PISA directory not set yet.')
      return # not yet set
    # read log
    if not os.path.exists(self.log_path):
      tkMessageBox.showerror('Error', 'pisa_log.dat file not exists.')
      return
    tf, log_lines = self.parse_pisa_log()
    if tf == False or len(log_lines) < 3:
      tkMessageBox.showerror('Error', 'pisa_log.dat file does not seem correct.')
      return

    # process csv
    # write csv
    content = 'AA,SEQNUM,RHO,SHIFT_CALC,DC_CALC,SHIFT_EXP,DC_EXP,SCORE,SHIFT_RAW,DC_RAW'
    for line in log_lines:
      tmpln = line[-2] + ',' +  ('%d' % (line[-1])) + ',' + line[col_dict['rho']] + ',' + \
            line[col_dict['shift_calc']] + ',' + line[col_dict['coupling_calc']] + ',' + \
            line[col_dict['shift_exp']] + ',' + line[col_dict['coupling_exp']] + ',' + \
            line[col_dict['score']] + ',' + line[col_dict['shift_raw']] + ',' + \
            line[col_dict['coupling_raw']]
      content = content + '\n' + tmpln
    # file dialog
    path = tkutil.save_file2(self.top, 'Save a CSV file', 'pisa_log_csv',
            '.csv', [('Comma-separated values', '*.csv')])

    f = open(path, 'w')
    f.write(content)
    f.close()
    pass

  def export_waves_csv_cb(self):
    if not os.path.exists(self.wave_path): 
      tkMessageBox.showerror('Error', 'pisa_wave.dat file not exists.')
      return
    f = open(self.wave_path)
    lines = f.readlines()
    f.close()
    content = ''
    for line in lines:
      line2 = line.strip()
      if line2 == '': continue
      content = content + line2.replace(' ', ',') + '\n'
    if content != '': content = content[:-1]
    # file dialog
    path = tkutil.save_file2(self.top, 'Save a CSV file', 'pisa_wave_csv',
            '.csv', [('Comma-separated values', '*.csv')])
    if path:
      f = open(path, 'w')
      f.write(content)
      f.close()  

    pass
  # -----------------------------------------------------------------------------
  #    
  def read_log_file(self):
    tf, lines = read_text_file(self.log_path)
    try:
      self.textbox.clear()
      #self.textbox.text.delete('0.0', 'end')
    except:
      pass
    self.fasta = ''
    self.init_seq = -1
    if tf:
      iStart = len(lines)
      for i in range(len(lines)):
        line = lines[i]
        if line.find('# resname') == 0:
          iStart = i
          break
        self.textbox.append(line.rstrip(), [line.rstrip()])
        #self.textbox.text.insert('end', line)
      cols = lines[iStart].replace('#', '').replace(',', '').strip()
      col_list = cols.split()
      col_line = '# '
      for col in col_list:
        col_line = col_line + '%-7s ' % (col)
      self.textbox.append(col_line, [col_line])
      #self.textbox.text.insert('end', col_line + '\n')
      for i in range(iStart+1, len(lines)):
        line = lines[i]
        try:
          if line.strip()[0] == '#':
            self.textbox.append(line.rstrip(), [line.rstrip()])
            continue
        except:
          self.textbox.append(line.rstrip(), [line.rstrip()])
          continue
        row_list = line.strip().split()
        line2 = '  '
        for j in range(len(row_list)):
          row = row_list[j]
          col = col_list[j]
          mrg = len(col) - 7
          line2 = line2 + '%-7s ' % (row)
          if mrg > 0:
            for k in range(mrg):
              line2 = line2 + ' '
          # parse sequence
          if row[0] in swalign.m_singlea:
            self.fasta = self.fasta + row[0]
            if j == 0 and self.init_seq < 0: 
              self.init_seq = int(row[1:])
        self.textbox.append(line2, [line2])    
        #self.textbox.text.insert('end', line2 + '\n')
  # -----------------------------------------------------------------------------
  #
  def seq_align(self, pdb_file):
    if self.bagel_dir == '':  return
    bagel_pdb_path = os.path.join(self.bagel_dir, 'pisa.pdb')

    # build sequence information from resonance list
    # self.session.project.condition_list().resonance_list()
    user_seq_list = []
    user_seqidx_list = []
    for i in range(len(self.fasta)):
      user_seq_list.append(self.fasta[i])
      user_seqidx_list.append(self.init_seq+i)

    user_seq, user_min_seq = self.fasta, self.init_seq
        
    # read pdb. use the highest 'sum_blosum62' chain
    chain_seq_list = wlutil.ExtractSequenceFromPDB(pdb_file)
    max_blosum62 = -9999999
    best_chain = None
    for chain in chain_seq_list:
      seq_align_dict = swalign.do_swalign(user_seq, user_min_seq, \
                                chain[1], chain[2])
      if seq_align_dict['sum_blosum62'] > max_blosum62:
        max_dict = seq_align_dict
        best_chain = chain
        max_blosum62 = seq_align_dict['sum_blosum62']

    pdb_seq_list = list(map(lambda x: 'X', range(1000)))

    # perform sequence alignment and set seq_align_dict
    self.seq_align_dict = swalign.do_swalign(user_seq, user_min_seq, 
                                              best_chain[1], best_chain[2])
    self.seq_align_chain = best_chain[0]

    # make pisa.pdb  
    new_lines = swalign.transform(pdb_file, \
                  self.seq_align_dict, self.seq_align_chain, HETATM=True)
    f = open(bagel_pdb_path, 'w')
    f.write(new_lines)
    f.close()
  # -----------------------------------------------------------------------------
  #
  def pymol_cb(self):
    # launch pymol with pisa.pdb
    if self.bagel_dir == '': return
    import tkFileDialog
    bagel_pdb_path = os.path.join(self.bagel_dir, 'pisa.pdb')
    # ask if you want to use current pdb file?
    user_pdb_path = ''
    if os.path.exists(bagel_pdb_path):
      result = tkMessageBox.askokcancel('Stored PDB file found.', 
                        'Do you want to use the stored PDB file?')
      if result is False:
        user_pdb_path = tkFileDialog.askopenfilename(
              initialdir = self.bagel_dir,
              title = 'Select a PDB file for PISA-SPARKY analysis')
        if os.path.exists(user_pdb_path):
          if user_pdb_path[-4:] == '.cif':
            import cif2pdb
            cif2pdb.cif2pdb(user_pdb_path, user_pdb_path[0:-3]+'pdb', HETATM=True)
            user_pdb_path = user_pdb_path[0:-3]+'pdb'
          self.seq_align(user_pdb_path)
          self.launch_pymol()
      else:
        self.launch_pymol()
    else:
      user_pdb_path = tkFileDialog.askopenfilename(
            initialdir = self.bagel_dir,
            title = 'Select a PDB file for PISA-SPARKY analysis')
      if os.path.exists(user_pdb_path):
        if user_pdb_path[-4:] == '.cif':
          import cif2pdb
          cif2pdb.cif2pdb(user_pdb_path, user_pdb_path[0:-3]+'pdb', HETATM=True)
          user_pdb_path = user_pdb_path[0:-3]+'pdb'
        self.seq_align(user_pdb_path)
        self.launch_pymol()
    pass

  def launch_pymol(self):
    # check if chesca.pdb exists
    bagel_pdb_path = os.path.join(self.bagel_dir, 'pisa.pdb')
    if not os.path.exists(bagel_pdb_path):
      tkMessageBox.showerror('Error', \
                'PDB file not found in PISA-SPARKY directory.')
      return False

    msg = 'Type @p in the PyMOL command-line to visualize your selection.'
    if platform.system() == 'Darwin':
      cmd = "cd %s; load pisa.pdb" % (self.bagel_dir)
      self.session.tk.clipboard_clear()
      self.session.tk.clipboard_append(cmd)
      
      msg = msg + '\n Manually run PyMOL and do "%s"' % \
                  (cmd)
      msg = msg + ' if PyMOL does not launch correctly.'
      msg = msg + ' The command is in your clipboard.'
    tkMessageBox.showwarning('Launching PyMOL...', msg)  
    return nmrfam.run_pymol(self.session, bagel_pdb_path)

  def select_residue_cb(self, event):
    pymol_prefix = """select pisa-sparky, pisa and (n. CA and i. $IDS)
color wheat, pisa-sparky
center pisa-sparky
zoom center, 15
label
label pisa-sparky, "%s-%s[CA]" % (resn, resi)
"""
    pymol_prefix2 = """set label_dihedral_digits, 2
dihedral pisa-sparky-phi, $ID1/C, $ID2/N, $ID2/CA, $ID2/C
dihedral pisa-sparky-psi, $ID2/N, $ID2/CA, $ID2/C, $ID3/N
"""


    data_list = self.textbox.selected_line_data()
    if len(data_list) == 0: return
    
    ress = ''
    res1 = -9999
    for data in data_list:
      if len(data[0].strip()) == 0: continue
      lbl = data[0].strip().split()[0]
      if len(lbl) == '#': continue
      if not lbl[0] in swalign.m_singlea: continue
      try:
        res = int(lbl[1:])
        if res1 == -9999: res1 = res
        ress = ress + '%d+' % (res)
      except:
        pass
    if len(ress) < 2: return
    ress = ress[:-1]
    content = pymol_prefix.replace('$IDS', ress)
    if len(data_list) == 1:
      tmp2 = pymol_prefix2.replace('$ID1', '%d' % (res1-1))
      tmp3 = tmp2.replace('$ID2', '%d' % (res1))
      tmp4 = tmp3.replace('$ID3', '%d' % (res1+1))
      content = content + tmp4

    f = open(os.path.join(self.bagel_dir, 'p'), 'w')
    f.write(content)
    f.close()
    pass

  def moveto_residue_cb(self, event):
    data_list = self.textbox.selected_line_data()
    if len(data_list) != 1: 
      return
    data = data_list[0]
    lbl = data[0].strip().split()[0]
    if len(lbl) == 0: 
      return
    if len(lbl[0]) == '#': return
    if not lbl[0] in swalign.m_singlea: 
      return
    try:
      res = int(lbl[1:])
    except:
      return
    sp = self.bagel_spec.spectrum()
    if sp == None: 
      tkMessageBox.showerror('Error', \
          'PISEMA spectrum should have been selected.')
      return
    for peak in sp.peak_list():
      if peak.is_assigned != 1: continue
      asgn = sputil.parse_assignment_entirely(peak.assignment)
      if asgn[0][1] == res:
        sputil.show_peak(peak)
        return
      
# -----------------------------------------------------------------------------
#    
def show_check_dialog(session):
  d = sputil.the_dialog(bagel_check_dialog, session)
  d.show_window(1)
  return d
