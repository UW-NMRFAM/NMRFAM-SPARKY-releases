import Tkinter
import types
import re
import math as m
import pyutil
import sparky
import sputil
import tkutil
import expectedpeaks

#################
#
# Updated by : Mary Clay PhD
# e-mail: mary.clay@stjude.org
# St Jude Children's Research Hospital 
# Department of Structural Biology Memphis, TN 
#
# Last updates: Feb 25, 2020
#
#
# -----------------------------------------------------------------------------
#
AAA_dict = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
 "GLU": "E", "GLN": "Q", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L",
 "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T",
 "TRP": "W", "TYR": "Y", "VAL": 'V' }

class obj:
  pass

class assignment_distance_dialog(tkutil.Dialog, tkutil.Stoppable):

  # ---------------------------------------------------------------------------
  #
  def __init__(self, session):

    self.session = session
    self.selection_notice = None
    tkutil.Dialog.__init__(self, session.tk, '3D NOESY assignment from PDB')

    explain = ('To autoassign 3D NOESY using assignments and protein structure: \n' +
               '(last edits Jan 18, 2018)\n')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.pack(side = 'top', anchor = 'w')

    explain = ('PDB does NOT need 1H')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.pack(side = 'top', anchor = 'w')        
    ep = tkutil.file_field(self.top, 'PDB file full pathway: ', 'Browse...', 35)
    self.pdb_path = ep.variable
    ep.frame.pack(side = 'top', anchor = 'w')

    explain = ('Distance threshold for het. atom to het. atom')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.pack(side = 'top', anchor = 'w')
    e = tkutil.entry_field(self.top, 'distance cutoff: ', '', 5)
    self.max_dist = e.variable
    e.frame.pack(side = 'top', anchor = 'w')

    explain = ('Specify which chain(s) should be used,limit 2')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.pack(side = 'top', anchor = 'w')
    ch = tkutil.entry_field(self.top, 'Use Chain(s): ', '', 5)
    self.chains = ch.variable
    ch.frame.pack(side = 'top', anchor = 'w')

    explain = ('NOESY data')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.pack(side = 'top', anchor = 'w')    
    self.spectrum_choice_3DNOESY = sputil.spectrum_menu(session, self.top, '3D NOESY:    ')
    self.spectrum_choice_3DNOESY.frame.pack(side = 'top', anchor = 'w')

###REFERENCE SPECTRUM
    explain = ('To define the editing plane')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.pack(side = 'top', anchor = 'w')
    self.spectrum_choice_ref = sputil.spectrum_menu(session, self.top, '2D editing: ')
    self.spectrum_choice_ref.frame.pack(side = 'top', anchor = 'w')
###REFERENCE SPECTRUM

    explain = ('Select 2D spectra that contain assignments\n for w1 dimenion of 3D, nuclei with which NOEs occur')
    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.pack(side = 'top', anchor = 'w')    
    self.sc = self.spectrum_choice_table(self.top)
    self.sc.pack(side = 'top', anchor = 'w')

    # explain = ('PPM tolerance for maching quality factor calculation (optional)')
    # w = Tkinter.Label(self.top, text = explain, justify = 'left')
    # w.pack(side = 'top', anchor = 'w') 
    # er = tkutil.entry_row(self.top, 'PPM tolerance: ',
    #        ('w1', '.01', 4), ('w2', '.01', 4), ('w3', '.01', 4))
    # self.ppm_range = er.variables
    # self.w3_range_widget = er.entries[2].frame
    # er.frame.pack(side = 'top', anchor = 'w')

    ib = tkutil.checkbutton(self.top, 'With diagonal peaks?', 0)
    ib.button.pack(side = 'top', anchor = 'w')
    self.diagonal = ib

    self.line_format = '%15s %s %7s %s'

    # self.spectrum_3d(self.spectrum_choice_3DNOESY.get())

    br = tkutil.button_row(self.top,
                           ('Generate peaklist', self.Generate_NOESY_cb),
                           ('Close', self.close_cb))
    br.frame.pack(side = 'top', anchor = 'w')
  
    self.settings = self.get_settings()


  # ---------------------------------------------------------------------------
  #
  def spectrum_choice_table(self, parent):

    headings = ('')
    st = sputil.spectrum_table(self.session,parent,headings,self.add_spectrum, self.remove_spectrum)
    st.spectrum_to_checkbutton = {}
    st.chosen_spectra = []
    st.spectrum_epeak_menus = {}
    st.axis_order_menu = {}
    self.spectrum_table = st
    
    spectra = self.session.project.spectrum_list()
    for spectrum in spectra:
      if spectrum.dimension == 2:
        st.add_spectrum(spectrum)
    return st.frame

  def add_spectrum(self, spectrum, table, row):

    pat_name, pat_axes = expectedpeaks.recall_pattern(spectrum)

    #
    # Make spectrum checkbutton
    #
    cb = tkutil.checkbutton(table.frame, spectrum.name, 0)
    #cb.button['selectcolor'] = sputil.spectrum_color(spectrum)
    choose_cb = pyutil.precompose(sputil.choose_spectrum_cb, spectrum, table.chosen_spectra)
    cb.add_callback(choose_cb)
    cb.button.grid(row = row, column = 0, sticky = 'w')
    if pat_name:
      cb.set_state(1)
    table.spectrum_to_checkbutton[spectrum] = cb

  def remove_spectrum(self, spectrum, table):

    cb = table.spectrum_to_checkbutton[spectrum]
    cb.set_state(0)
    cb.button.destroy()
    del table.spectrum_to_checkbutton[spectrum]

    table.spectrum_epeak_menus[spectrum].frame.destroy()
    del table.spectrum_epeak_menus[spectrum]

    table.axis_order_menu[spectrum].frame.destroy()
    del table.axis_order_menu[spectrum]

  # ---------------------------------------------------------------------------
  #
  # def spectrum_3d(self, name):

  #   spectrum = sputil.name_to_spectrum(name, self.session)
  #   if spectrum == None:
  #     return

  #   if spectrum.dimension == 3:
  #     self.w3_range_widget.pack(side = 'left', anchor = 'w')
  #     self.line_format = '%20s %s %7s %s'
  #   else:
  #     self.w3_range_widget.pack_forget()
  #     self.line_format = '%15s %s %7s %s'

  #   default_ppm_range = {'1H':.02, '13C':.2, '15N':.2}
  #   for a in range(spectrum.dimension):
  #     nucleus = spectrum.nuclei[a]
  #     if default_ppm_range.has_key(nucleus):
  #       ppm_range = default_ppm_range[nucleus]
  #     else:
  #       ppm_range = .02
  #     self.ppm_range[a].set('%.2f' % ppm_range)

  # ---------------------------------------------------------------------------
  #
  def get_settings(self):
  
    settings = pyutil.generic_class()
    settings.spectrum_ref = self.spectrum_choice_ref.spectrum()   
    settings.spectrum_3DNOESY = self.spectrum_choice_3DNOESY.spectrum()    
    spectra = self.spectrum_table.chosen_spectra
    settings.spectrum_noe_list=[spectrum for spectrum in spectra]
    settings.pdb_path = self.pdb_path.get()   
    settings.diagonal=self.diagonal.state()
    settings.max_distance = pyutil.string_to_float(self.max_dist.get())
    settings.chains = self.chains.get().replace(',','')
    # if settings.spectrum_3DNOESY:
    #   dim = settings.spectrum_3DNOESY.dimension
    #   settings.ppm_range = tkutil.float_variable_values(self.ppm_range)[:dim]
    # else:
    #   settings.ppm_range = None
    return settings

  # ---------------------------------------------------------------------------
  #
  def Generate_NOESY_cb(self):

    s = self.get_settings()
    print s.spectrum_ref.label_list()
    print s.spectrum_ref.peak_list()
    Freq_dict = {}
    atoms_list_ref = []
    for peak in s.spectrum_ref.peak_list():
      if "?" not in peak.assignment:
        resn = re.search('[A-Z]([0-9]*)[A-Z]', peak.assignment).group()[:-1]
        ra1 = re.search('[0-9]+(\w*)-',peak.assignment).group(1)
        ra2 = re.search('-(\w*)', peak.assignment).group(1)
        atoms_list_ref.append([resn+"-"+ra1,resn+ra1, resn+ra2])
        Freq_dict[resn+ra1] = peak.frequency[0]
        Freq_dict[resn+ra2] = peak.frequency[1]

    atoms_list_noe = []
    for noe_spectrum in s.spectrum_noe_list:
      for peak in noe_spectrum.peak_list():
          if "?" not in peak.assignment:
            resn = re.search('[A-Z]([0-9]*)[A-Z]', peak.assignment).group()[:-1]
            resn2 = resn[0] + str(int(resn[1:])+1000)
            na1 = re.search('[0-9]+(\w*)-', peak.assignment).group(1)
            na2 = re.search('-(\w*)', peak.assignment).group(1)
            if s.spectrum_3DNOESY.nuclei[0] != '1H':
              atoms_list_noe.append([resn+"-"+ na1,resn+ na1])
              Freq_dict[resn+na1] = peak.frequency[0]
              if len(s.chains) == 2:
                atoms_list_noe.append([resn2+"-"+ na1,resn2+ na1])
                Freq_dict[resn2+na1] = peak.frequency[0]
            if s.spectrum_3DNOESY.nuclei[0] == '1H':
              atoms_list_noe.append([resn+"-"+ na1,resn+na2])
              Freq_dict[resn+na2] = peak.frequency[1]
              if len(s.chains) == 2:
                atoms_list_noe.append([resn2+"-"+ na1,resn2+ na2])
                Freq_dict[resn2+na2] = peak.frequency[1]
    save_path_new = str(s.spectrum_3DNOESY.save_path+'SIM')
    save_new = open(save_path_new, 'w')
    save_content = open(s.spectrum_3DNOESY.save_path, 'r')
    for line in save_content.readlines():
      line = line.replace('name ' + s.spectrum_3DNOESY.name ,'name '+ s.spectrum_3DNOESY.name + '_sim')
      if (line=='<end view>\n'): 
        break
      save_new.write(line)
    save_new.write('<end view>\n<ornament>\n<end ornament>\n<end spectrum>\n')
    save_new.close()

    self.session.open_spectrum(save_path_new)

    spectrums=self.session.project.spectrum_list()
    spectrum_ref_name=s.spectrum_3DNOESY.name

    for spectrum in spectrums:
      if (spectrum.name==spectrum_ref_name+'_sim'):
        noe_peak_list = self.distances(s.pdb_path, s.max_distance, s.chains, s.diagonal, atoms_list_ref, atoms_list_noe)
        for (tassignment,w1,w2,w3,d) in noe_peak_list:
          assignment = sputil.parse_assignment(tassignment)
          frequency = [Freq_dict[w1],Freq_dict[w2],Freq_dict[w3]]
          note = str(d)
          if d == 0.0:
            color = "red"
          if d <= 4.0 and d != 0.0:
            color = 'green'
          if d > 4.0: 
            color = "white"
          self.create_peak(assignment,frequency, note, color, spectrum)
          print '------ '+str(tassignment.replace(w3,assignment[2][1]))+' ------'
          print "%14.1f" %d 
        for (label, peak) in zip(spectrum.label_list(), spectrum.peak_list()):
          label.color = peak.color

 # #
# # >>>>>>>>>>>>>>>> Matching factor calculation <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# #
#             if noe_peak_list:
#               for noe_peak in noe_peak_list:
#                 if (freq_NOE>(noe_peak.frequency[0]-(s.ppm_range[0]/2)) and 
#                     freq_NOE<(noe_peak.frequency[0]+(s.ppm_range[0]/2))
#                    ):
#                   nb_matching=nb_matching+1
#                   match_data_height = noe_peak.data_height
#                   total_data_height_expected=total_data_height_expected+match_data_height
#                   for noe_peak_already_match in noe_peak_already_match_list:
#                     if (noe_peak.frequency[0]==noe_peak_already_match.frequency[0]):
#                       total_data_height_expected=total_data_height_expected-match_data_height
#                       break
#                   noe_peak_already_match_list.append(noe_peak)
#                   break 
#         try:
#           MFE=round(float(nb_matching)/float(nb_neighbors), 2)
#         except ZeroDivisionError:
#           MFE='nd'
#         setattr(self.getpeaks, str(peak.assignment)+'_MFE', MFE)
#         try:
#           MFA=round(float(total_data_height_expected)/float(total_data_height_actual), 2)
#         except ZeroDivisionError:
#           MFA='nd'
#         setattr(self.getpeaks, str(peak.assignment)+'_MFA', MFA)
#         print 'MFA: '+str(MFA)
#         print 'MFE: '+str(MFE)
#       except AttributeError:pass
#   
# -----------------------------------------------------------------------------
#
# >>>>> Extract distances between of interest atoms <<<<<<<
#def distances(path, Cutoff,atoms_list_ref,atoms_list_noe):
  def find_atom(self, group,plist):
    for entry in plist:
      if group in entry:
        return entry

  def distances(self, path, Cutoff, chains, diagonal, atoms_list_ref,atoms_list_noe):

    PDB_lines_ref =[]
    PDB_lines_noe =[]
    if len(chains) == 1:
      for line in open(path).readlines():
        if line[0:4] == "ATOM" or line[0:4] == 'HETA':
          if line[17:20].strip() in AAA_dict.keys() and line[21] == chains:
            group = AAA_dict[line[17:20].strip()] + line[22:26].strip() + "-" + line[12:16].strip()
            if group in [ref for (ref, rw1, rw2) in atoms_list_ref]:
              PDB_lines_ref.append(self.find_atom(group,atoms_list_ref) + [float(line[30:38]),float(line[38:46]),float(line[46:54])])
            if group in [noe for (noe, nw) in atoms_list_noe]:
              PDB_lines_noe.append(self.find_atom(group,atoms_list_noe) + [float(line[30:38]),float(line[38:46]),float(line[46:54])])
    if len(chains) == 2:
      for line in open(path).readlines():
        if line[0:4] == "ATOM" or line[0:4] == 'HETA':
          if line[17:20].strip() in AAA_dict.keys() and line[21] == chains[0]:
            group = AAA_dict[line[17:20].strip()] + line[22:26].strip() + "-" + line[12:16].strip()
            if group in [ref for (ref, rw1, rw2) in atoms_list_ref]:
              PDB_lines_ref.append(self.find_atom(group,atoms_list_ref) + [float(line[30:38]),float(line[38:46]),float(line[46:54])])
            if group in [noe for (noe, nw) in atoms_list_noe]:
              PDB_lines_noe.append(self.find_atom(group,atoms_list_noe) + [float(line[30:38]),float(line[38:46]),float(line[46:54])])
          if line[17:20].strip() in AAA_dict.keys() and line[21] == chains[1]:
            group = AAA_dict[line[17:20].strip()] + str(int(line[22:26].strip()) + 1000) + "-" + line[12:16].strip()
            if group in [noe for (noe, nw) in atoms_list_noe]:
              PDB_lines_noe.append(self.find_atom(group,atoms_list_noe) + [float(line[30:38]),float(line[38:46]),float(line[46:54])])

    NOESY3D_peaklist = []
    for (rgroup,rw1,rw2,rx,ry,rz) in PDB_lines_ref:
      for (ngroup,nw,nx,ny,nz) in PDB_lines_noe:
        if ngroup != rgroup:
          d = round(m.pow(m.pow(nx-rx, 2)+m.pow(ny-ry, 2)+m.pow(nz-rz, 2) ,0.5), 1)
          if d <= Cutoff:
            NOESY3D_peaklist.append([nw+"-"+rw1+"-"+rw2, nw, rw1, rw2, d])
    if diagonal == True:
      for (rgroup,rw1,rw2,rx,ry,rz) in PDB_lines_ref:
        for (ngroup,nw,nx,ny,nz) in PDB_lines_noe:
          if ngroup == rgroup:
            NOESY3D_peaklist.append([nw+"-"+rw1+"-"+rw2, nw, rw1, rw2, 0.0])
    return tuple(NOESY3D_peaklist)
#
# -----------------------------------------------------------------------------
#
  def create_peak(self, assignment, frequency, note, color, spectrum):

    peak = spectrum.place_peak(frequency)
    self.move_peak_onto_spectrum(peak)

    assigned = 0
    for a in range(spectrum.dimension):
      group_name, atom_name = assignment[a]
      if group_name or atom_name:
        peak.assign(a, group_name, atom_name)
        assigned = 1
    if assigned:
      peak.show_assignment_label()

    if color:
      peak.color = color

    if note:
      peak.note = note


    return
  def move_peak_onto_spectrum(self, peak):

    freq = peak.frequency
    pos = sputil.alias_onto_spectrum(freq, peak.spectrum)
    if pos != freq:
      peak.position = pos
      peak.alias = pyutil.subtract_tuples(freq, pos)

# def Extract_Peaks(distances, peak_list_3d, peak_list_ref, peak_list_noe, nuclei, tolerance):
#   w1tol = tolerance[0]
#   w2tol = tolerance[1]
#   w3tol = tolerance[2]
#   Noe_nuclei=nuclei[0]
#   Ref_nuclei=nuclei[1]
#   getpeaks=obj()
#   for peak in peak_list_ref:
#     if peak.is_assigned:
#       whet_ref=float(peak.frequency[0])
#       wh_ref=float(peak.frequency[1])
#       setattr(getpeaks, str(peak.assignment)+'_freq', peak.frequency)
# #
# # ----------------------- extract all peaks from the plan (w2,w3) ---------------
# #
#       noesy_peaks=[]
#       for peaknoesy in peak_list_3d:    
#         wnoe=float(peaknoesy.frequency[0])  
#         whet=float(peaknoesy.frequency[1])
#         wh=float(peaknoesy.frequency[2])
#         if (abs(whet - whet_ref) < w2tol and abs(wh-wh_ref) < w3tol):

#           if (Noe_nuclei=='1H' and abs(wnoe-wh) < w1tol): noesy_peaks.append(peaknoesy)
#           elif (Noe_nuclei!='1H' and abs(wnoe - whet) < w1tol): noesy_peaks.append(peaknoesy)
#       setattr(getpeaks, str(peak.assignment)+'_3dpeaks', noesy_peaks)
# #
# # ----------------------- then extract assigned neighbor nucleus ----------------------
# #
#       neighbors=[]
#       for line in distances:
#         if line.split()[0]==peak.resonances()[0].name:
#           for peaknoe in peak_list_noe:
#             if peaknoe.is_assigned:
#               if line.split()[1]==peaknoe.resonances()[0].name:
#                 neighbors.append((peaknoe,line.split()[2]))
#       setattr(getpeaks, str(peak.assignment)+'_neighbors', neighbors)
#   return getpeaks

#
# ----------------------------------------------------------------------------------------
#
def show_dialog(session):
  sputil.the_dialog(assignment_distance_dialog,session).show_window(1)
