# -----------------------------------------------------------------------------
# PLUQIN-SPARKY dialog
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee partially based on Rienstra's PLUQ plugin
# This module is designed to interact with NMRFAM PluqIn Web Server
# Web Server interaction is based on PINE-SPARKY.2 codes
#
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: May 19, 2018
# 
#
# -----------------------------------------------------------------------------
# CITATIONS:
#   PLUQIN-SPARKY: 
#     Lee, Woonghee et al. in preparation
#
#   PINE-SPARKY.2:
#     Lee, Woonghee & John Markley. (2018) Bioinformatics 34(9): 1586-1588
#     "PINE-SPARKY.2 for automated NMR-based protein structure research"
#     https://doi.org/10.1093/bioinformatics/btx785
#
#   PLUQ-IN:
#     Fritzsching, Keith et al. (2016) J Biomol NMR 64(2): 115-130
#     "Conformationally selective multidimensional chemical shift ranges in 
#     proteins from a PACSY database purged using intrinsic quality criteria"
#     https://doi.org/10.1007/s10858-016-0013-5
#
#   PLUQ:
#     Fritzsching, Keith et al. (2013) J Biomol NMR 56(2): 155-167
#     "Practical use of chemical shift databases for protein solid-state NMR:
#     2D chemical shift maps and amino-acid assignment with 
#     secondary-structure information"
#     https://doi.org/10.1007/s10858-013-9732-z
#
#   PACSY:
#     Lee, Woonghee et al. (2012) J Biomol NMR 54(2): 169-179
#     "PACSY, a relational database management system for protein structure
#     and chemical shift analysis"
#     https://doi.org/10.1007/s10858-012-9660-3
#
# -----------------------------------------------------------------------------

import os
import Tkinter
import sparky
import sputil
import tkutil
import tkMessageBox
import myseq
import nmrfam        
import itertools

# for token
import time
import random

class PluqIn_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.residue_num = None
    self.session = session
    self.dimension = self.session.selected_spectrum().dimension
    self.selected_peaks = []
    self.pluqin_result = None

    self.dim_selection = [Tkinter.BooleanVar() for x in range(self.dimension)]
    for entry in self.dim_selection:
      entry.set(True)
    self.dim_modified = False

    tkutil.Dialog.__init__(self, session.tk, 'PluqIn-Sparky')
    self.create_ui()
    
  def create_ui(self):
    # User name
    user_name_ef = tkutil.entry_field(self.top, 'Your name: ', initial = '', width = 30)
    user_name_ef.frame.pack(side = 'top', anchor = 'w', expand = 0)
    self.user_name = user_name_ef.variable
    
    # User email
    user_email_ef = tkutil.entry_field(self.top, 'Your email: ', initial = '', width = 30)
    user_email_ef.frame.pack(side = 'top', anchor = 'w')
    self.user_email = user_email_ef.variable    

    # Separator
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    # Guess button and dimension selections
    top_row = Tkinter.Frame(self.top)
    guess_button = Tkinter.Button(top_row, text = "Guess", command = self.guess_cb)
    guess_button.pack(side = 'left', anchor = 'w')

    for i in range(self.dimension):
      dim_check_box = Tkinter.Checkbutton(top_row, text = "W"+str(i+1), variable = self.dim_selection[i], command = self.dim_modified_cb)
      dim_check_box.var = self.dim_selection[i]
      dim_check_box.pack(side = 'left', anchor = 'w', fill = 'y')
    top_row.pack(side = 'top', anchor = 'w')

    # Separator
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    # token & buttons
    # User name
    token_frame = Tkinter.Frame(self.top, width = 600, height = 25)
    token_frame.pack(side='top', anchor='w')
    token_ef = tkutil.entry_field(token_frame, 'Key: ', initial = '', width = 20)
    token_ef.frame.pack(side = 'left', anchor = 'w', expand = 0)
    self.token = token_ef.variable
    self.br2 = tkutil.button_row(token_frame,
        ('Check', self.check_wrap_cb),
        ('Browse...', self.pluqin_browse_cb),
        )      
    self.br2.frame.pack(side = 'top', anchor = 'e', expand = 0)             
    tkutil.create_hint(self.br2.buttons[0], 'Check PluqIn job status and import the results.')
    tkutil.create_hint(self.br2.buttons[1], 'Import the results in the local machine.')    

    # Separator
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    # PluqIn scrolling list
    pluqin_result = tkutil.scrolling_list(self.top, heading = 'PluqIn Assignments', height = 9)
    pluqin_result.frame['width']=120
    pluqin_result.frame.pack(side = 'top', anchor = 'w', fill = 'both', expand = 1)

    # Buttons
    br = tkutil.button_row(self.top,
                 ('Comment', self.comment_cb),
                 ('Assign', self.assign_cb),
                 ('Close', self.but_close_cb),
                 )
    br.frame.pack(side = 'top', anchor = 'w')
    self.pluqin_result = pluqin_result

  # -----------------------------------------------------------------------------
  #    
  def dim_modified_cb(self):
    self.dim_modified = True

  # -----------------------------------------------------------------------------
  #    
  def check_wrap_cb(self):  
    self.check_cb(1)
  # -----------------------------------------------------------------------------
  #    
  def pluqin_browse_cb(self):
    self.check_cb(2)
  # -----------------------------------------------------------------------------
  #    
  def check_cb(self, clicked):
    if clicked == 2: # directory mode
      import tkFileDialog
      pluqin_dir = tkFileDialog.askdirectory(initialdir = self.session.project.sparky_directory,
                                title = 'Select a PluqIn output directory',
                                mustexist = 1)
      if pluqin_dir == '': return
      self.token.set(pluqin_dir)
      
    if self.token.get() == '':
      if clicked == 1:
        tkMessageBox.showinfo('PluqIn job sumitted.', 'No submitted PluqIn job found.')
      return
          
    # retrieve PluqIn URL + token path.
    try:
      import urllib2
    except:
      tkMessageBox.showerror('urllib2', 'You do not have openssl installed or set properly.\nPlease check your email instead.')
      return

    pluqin_root_url = 'http://pine3.nmrfam.wisc.edu/pluqin/queue/%s/' % (self.token.get())
    pluqin_token_url = pluqin_root_url + 'token_status.txt'
    pluqin_result_url = pluqin_root_url + 'pluqin_results.txt'
    
    if clicked == 2:
      pluqin_root_url = 'file://%s/' % (self.token.get())
      pluqin_result_url = pluqin_root_url
      
    if self.token.get() == None:
      tkMessageBox.showwarning("Error", "Nothing to check")
      return
         
    pluqin_status_lines = ['waiting',]
    if clicked == 1:
      try: 
        pluqin_status = urllib2.urlopen(pluqin_token_url, timeout=2)
        pluqin_status_lines = pluqin_status.readlines()
        if len(pluqin_status_lines) == 0:
          if clicked == 1:
            tkMessageBox.showerror('Retrieve error', 'Unknown error during retrieving data from NMRFAM. Please check your email instead.')      
          else: 
            tkMessageBox.showerror('Retrieve error', 'Unknown error during retrieving data from NMRFAM. Please check your email instead.')                        
      except:
        if clicked == 1:
          tkMessageBox.showerror('Retrieve error', 'It seems your job is not finished yet.')
        return    

    if clicked == 2 or pluqin_status_lines[0].strip() == 'finished':
      pluqin_dir = os.path.join(sparky.installation_path(), self.session.project.sparky_directory, 'Lists')
      pluqin_path = os.path.join(pluqin_dir, 'pluqin_results.txt')
      try:
        if not os.path.exists(pluqin_dir):
          os.makedirs(pluqin_dir)
        pluqin_response = urllib2.urlopen(pluqin_result_url, timeout=15)
        pluqin_html = pluqin_response.read()
        f = open(pluqin_path, 'w')
        f.write(pluqin_html)
        f.close()
      except:
        tkMessageBox.showerror("Error", "PluqIn results could not be retrieved or could not be unpacked. Check Lists directory if you have pluqin_results.txt file.")
        return

      self.pluqin_result.clear()
      pluqin_lines = pluqin_html.split("\n")
      if len(pluqin_lines) < 2:
        tkMessageBox.showerror("Error", "PluqIn results does not look good.")
        return

      for line in pluqin_lines:
        line2 = replacer(line, ['input:','experiment:', '[', ']', '(',')',"'",','], ' ')
        line3 = replacer(line, ['[', ']', '(',')',"'",','], ' ')     
        if line.find('input') != -1 or line.find('experiment') != -1:   
          self.pluqin_result.append(line.strip(), tuple(line2.strip().split()))
        else:        
          # split and format by 5s
          sline3 = line3.strip().split()
          line4 = ''
          for piece in sline3:
            line4 = line4 + ' %-5s' % (piece)
          self.pluqin_result.append(line4.strip(), tuple(line2.strip().split()))
    elif clicked == 1 and pluqin_status_lines[0].strip() == 'failed':    
      tkMessageBox.showerror("Error", "PluqIn results does not look good.")

  # -----------------------------------------------------------------------------
  #    
  def is_ready_to_guess(self):
    tot_select_dim = sum([x.get() for x in self.dim_selection])
    if (len(self.selected_peaks) * tot_select_dim < 2):
      tkMessageBox.showwarning("Error", "Too few peaks or dimensions selected")
      return False
    else:
      if len(self.selected_peaks) > 25:
        tkMessageBox.showwarning("Error", "Too many peaks selected")
        return False
      return True

  # -----------------------------------------------------------------------------
  #    
  def guess_cb(self):
    self.selected_peaks = self.session.selected_peaks()
    if (not self.is_ready_to_guess()):
      return
    self.input_frequencies = self.get_input_frequencies(self.selected_peaks)
    self.input_experiment_type = self.get_input_experiment_type
    pluqin_args = '-e ' + self.input_experiment_type(self.selected_peaks) + ' '
    for freq in self.input_frequencies:
      pluqin_args = pluqin_args + '-p %.3f ' % (freq)
    self.pluqin_result.clear()
    random.seed()        
    token = time.strftime("%y%m%d_%H%M%S_") + "%06d" % random.randrange(0,1000000)        

    # check if available name and email exist
    szUserName = self.user_name.get()
    szUserEmail = self.user_email.get()
    
    if szUserName == '':
      szUserName = 'Unknown'

    if (szUserEmail == '') or (szUserEmail.find('@') == -1):
      szUserEmail = 'nobody@nobody.com'

    szUserName = replacer(szUserName, [',','"',"'","/","\\"], ' ')
    szUserEmail = replacer(szUserName, [',','"',"'","/","\\"], ' ')
  
    fields = [['username', szUserName],
              ['useremail', szUserEmail],
              ['pluqin_args', pluqin_args],
              ['nmrfamsparky_token', token]]
    self.token.set(token)
    pluqin_url = 'pine3.nmrfam.wisc.edu'
    pluqin_selector = '/cgi-bin/pluqin_uploader.cgi'

    self.dim_modified = False
    
    try:
      import posthtml
      text=posthtml.post_multipart(pluqin_url, pluqin_selector, fields, [])
      tkMessageBox.showinfo('PluqIn job sumitted.', 'PluqIn job submitted. Check your result in this window or in your email inbox after a few seconds.')
    except:
      tkMessageBox.showerror('Error', 'PluqIn job submission failed. Check your internet connection and contact Woonghee (pinesparky@gmail.com)')

  # -----------------------------------------------------------------------------
  #    
  def get_input_experiment_type(self, peaks):
    return 'c'
#    varying_dim = self.find_varying_dimension(peaks)
#    fixed_dim = self.get_chosen_dim()
#    fixed_dim.remove(varying_dim)
#    used_nuclei = [0,0,0] # C, N, H
#    for dim in fixed_dim:
#      for peak in peaks:
#        if peak.spectrum.nuclei[dim] == '13C': used_nuclei[0] = 1
#        if peak.spectrum.nuclei[dim] == '15N': used_nuclei[1] = 1
#        if peak.spectrum.nuclei[dim] == '1H': used_nuclei[2] = 1
#    if used_nuclei[0] == 1 and used_nuclei[1] == 1: return 'cn'
#    else: return 'c'

  # -----------------------------------------------------------------------------
  #    
  def get_input_frequencies(self, peaks):
    varying_dim = self.find_varying_dimension(peaks)
    fixed_dim = self.get_chosen_dim()
    fixed_dim.remove(varying_dim)
    input_frequencies = []
    for dim in fixed_dim:
      input_frequencies.append(list_average([x.frequency[dim] for x in peaks]))
    input_frequencies += [x.frequency[varying_dim] for x in peaks] 
    return input_frequencies

  # -----------------------------------------------------------------------------
  #    
  def is_ready_to_assign(self):
    if self.dim_modified:
      tkMessageBox.showwarning("Error", "Dimension setting modified after guessing. Please Guess again.")
      return False
    if self.selected_peaks == []:
      tkMessageBox.showwarning("Error", "No peaks selected")
      return False
    if self.selected_peaks != self.session.selected_peaks():
      tkMessageBox.showwarning("Error", "Peak selection have changed since guessing")
      return False
    try:
      selected_line = self.pluqin_result.selected_line_numbers()[0] - 2
    except IndexError:
      tkMessageBox.showwarning("Error", "Assignment not selected")
      return False
    if selected_line < 0:
      tkMessageBox.showwarning("Error", "Invalid selection")
      return False
    return True

  # -----------------------------------------------------------------------------
  #    
  def assign_cb(self):
    if (not self.is_ready_to_assign()):
      return

    residue = self.pluqin_result.selected_line_data()[0][0]
    residue_num = self.residue_num

    str_cs_list = self.pluqin_result.line_data[0]
    cs_list = map(float, str_cs_list)

    pair_cs_list = []
    pair_atm_list = []

    pluqin_data = self.pluqin_result.selected_line_data()[0]
    for i in range(len(pluqin_data[1:len(cs_list)+1])):
      atm = pluqin_data[1:len(cs_list)+1][i]
      if atm == '-': continue
      pair_atm_list.append(atm)  
      pair_cs_list.append(cs_list[i])

    for peak in self.selected_peaks:
      assignment = query_assignment(peak.frequency,
                      pair_cs_list,
                      pair_atm_list)

      for dim in range(len(peak.frequency)):
        if assignment[dim] == None: continue
        if self.dim_selection[dim].get() == False: continue
        if str(residue_num) == 'None': 
          peak.assign(dim, str(residue)+'?', assignment[dim])
        else:
          peak.assign(dim, str(residue)+str(residue_num), assignment[dim])
      peak.show_assignment_label()

  # -----------------------------------------------------------------------------
  #    
  def comment_cb(self):
    if (not self.is_ready_to_assign()):
      return
    residue = self.pluqin_result.selected_line_data()[0][0]
    residue_num = self.residue_num

    str_cs_list = self.pluqin_result.line_data[0]
    cs_list = map(float, str_cs_list)

    pair_cs_list = []
    pair_atm_list = []

    pluqin_data = self.pluqin_result.selected_line_data()[0]
    for i in range(len(pluqin_data[1:len(cs_list)+1])):
      atm = pluqin_data[1:len(cs_list)+1][i]
      if atm == '-': continue
      pair_atm_list.append(atm)  
      pair_cs_list.append(cs_list[i])
    
    for peak in self.selected_peaks:
      assignment = query_assignment(peak.frequency,
                      pair_cs_list,
                      pair_atm_list)
      comment_str = ''
      for dim in range(0, self.dimension):
        if self.dim_selection[dim].get() == False: comment_str=comment_str+'?-'
        if assignment[dim] == None: comment_str=comment_str+'?-'
        if str(residue_num) == 'None':
          comment_str= comment_str+str(residue)+'?'+assignment[dim]+"-"        
        else:
          comment_str= comment_str+str(residue)+str(residue_num)+assignment[dim]+"-"
      peak.note = str(comment_str[0:-1])
    self.session.selected_spectrum().needs_save = True

  # -----------------------------------------------------------------------------
  #    
  def get_chosen_dim(self):
    chosen = []
    for i in range(self.dimension):
      if self.dim_selection[i].get():
        chosen.append(i)
    return chosen

  # -----------------------------------------------------------------------------
  #    
  def find_varying_dimension(self, peaks):
    deviation =dict() 
    chosen = self.get_chosen_dim()
    for dim in chosen:
      frequencies = [x.frequency[dim] for x in peaks]
      deviation[dim]=max(frequencies) - min(frequencies)
    return max(chosen, key = lambda dim : deviation[dim])

  # -----------------------------------------------------------------------------
  #    
  def get_residue_num(self):
    condition = sputil.selected_condition(self.session)
    resonances = condition.resonance_list()
    group_numbers = [res.group.number for res in resonances]
    max_g_num = max(group_numbers)
    return int(round(max_g_num/10.0) * 10 + 10)

  # -----------------------------------------------------------------------------
  #    
  def but_close_cb(self):
    self.close_cb()
    self.top.destroy()

# -----------------------------------------------------------------------------
#    
def replacer(orig_str, list_source_str, new_char):
  work_str = orig_str
  for src_str in list_source_str:
    work_str = work_str.replace(src_str, new_char)
  return work_str

# -----------------------------------------------------------------------------
#    
def query_assignment(frequencies, cs_pair_list, atoms_pair_list):
  dim = len(frequencies) 
  assignment= ["" for i in range(dim)] 
  
  for i in range(len(frequencies)):
    freq = frequencies[i]
    dist = 9999
    atom = ''
    for j in range(len(cs_pair_list)):
      cs = cs_pair_list[j]
      temp = abs(freq-cs)
      if temp < dist: 
        dist = temp
        atom = atoms_pair_list[j]
    if atom != '' and atom[0] != 'H' and dist < 0.4:
      assignment[i] = atom

  return assignment

# -----------------------------------------------------------------------------
#    
def show_dialog(session):
  d = sputil.the_dialog(PluqIn_dialog, session)
  d.show_window(1)

# -----------------------------------------------------------------------------
#    
def list_average(l):
  return sum(l)/float(len(l))
