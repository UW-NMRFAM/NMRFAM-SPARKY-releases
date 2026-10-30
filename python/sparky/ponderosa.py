# -----------------------------------------------------------------------------
# PONDEROSA-C/S dialog for NMRFAM Ponderosa Web Server
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Oct 29, 2018
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
import os
import tkutil
import sputil
import Tkinter
import tkFileDialog
import tkMessageBox
import myseq

szTemplatePackedInputs = """[START]-[parameters.ini]
[USERINFO]
USERPROJ=ponderosa_project
USERDEPT=ponderosa_institute
USERMAIL1=ponderosa_usermail1
USERMAIL2=ponderosa_usermail2
USERNAME1=ponderosa_username1
USERNAME2=ponderosa_username2
USERPHONE1=
USERPHONE2=
[PONDEROSA]
CONSTCOUNT=0
NOESYCOUNT=0
SEQFILE=/home/ponderosa/nmrfamsparky.seq
CSTABLE=/home/ponderosa/nmrfamsparky.prot
WORKDIR=/home/ponderosa
[TOLERANCE]
H_PPM=$HTOLERANCE
C_PPM=$CTOLERANCE
N_PPM=$NTOLERANCE
[WEIGHT]
RAMA=50.000000
VIOL=50.000000
RMSD=50.000000
[CYCLE]
STEP=1
TIER=1
[PERFORMANCE]
CPUCOUNT=20
[REFINEMENT]
FINALIZE=PONDEROSA-X
[DISULPHIDE]
SS=$SSBOND
[SERVER]
URL=localhost
[END]
[END]-[parameters.ini]

"""

def axis_order_for_ponderosa(spec, spec_type):
  spec_order = ['', -1]
  if spec.dimension > 2:
    if (spec.nuclei[0] == '15N') or (spec.nuclei[0] == '13C'):
      if abs(spec.spectrum_width[1] - spec.spectrum_width[2]) < 3.0:
        if spec.data_size[1] < spec.data_size[2]:           spec_order = ['NhH', 1]
        else:                                               spec_order = ['NHh', 0]    
      else:
        if spec.spectrum_width[1] > spec.spectrum_width[2]: spec_order = ['NhH', 1]
        else:                                               spec_order = ['NHh', 0]
    elif (spec.nuclei[1] == '15N') or (spec.nuclei[1] == '13C'):
      if abs(spec.spectrum_width[0] - spec.spectrum_width[2]) < 3.0:  
        if spec.data_size[0] < spec.data_size[2]:           spec_order = ['hNH', 3]
        else:                                               spec_order = ['HNh', 2]    
      else:
        if spec.spectrum_width[0] > spec.spectrum_width[2]: spec_order = ['hNH', 3]
        else:                                               spec_order = ['HNh', 2]
    elif (spec.nuclei[2] == '15N') or (spec.nuclei[2] == '13C'):
      if abs(spec.spectrum_width[0] - spec.spectrum_width[1]) < 3.0:  
        if spec.data_size[0] < spec.data_size[1]:           spec_order = ['hHN', 5]
        else:                                               spec_order = ['HhN', 4]    
      else:
        if spec.spectrum_width[0] > spec.spectrum_width[1]: spec_order = ['hHN', 5]
        else:                                               spec_order = ['HhN', 4]
  elif (spec.nuclei[0] == '1H') and (spec.nuclei[1] == '1H'):
    if abs(spec.spectrum_width[0] - spec.spectrum_width[1]) < 3.0:      spec_order = ['Hh', 0]
    elif abs(spec.spectrum_width[0] - spec.spectrum_width[1]) < 3.0:    spec_order = ['hH', 1]    
    else:                                                               spec_order = ['hH', 1]    
    return tuple(spec_order)
     
  if spec_type != 0:
    spec_order[0] = spec_order[0].replace("N", "C")
  return tuple(spec_order)
  
def spec_type_in_string(spec_type):
  if spec_type == 0:
    return '15N-NOESY'  
  elif spec_type == 1:
    return '13C-NOESY'  
  elif spec_type == 2:
    return '13C-AROMATIC-NOESY'
  elif spec_type == 3:
    return '2D-NOESY'    
  return ''


  
# -----------------------------------------------------------------------------
# INPUTS:
#      
#        Chemical shifts
#        Sequences
#        NOESY peak lists
#

class ponderosa_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'PONDEROSA-C/S structure calculation')
    self.verbose = 1
    self.session = session
    
    # username
    self.username = tkutil.entry_field(self.top, 'Your name: ', '', 30)
    self.username.frame.pack(side = 'top', fill = 'both', expand = 1)
    # email
    self.email = tkutil.entry_field(self.top, 'Email: ', '', 30)
    self.email.frame.pack(side = 'top', fill = 'both', expand = 1)
    # project name
    self.prjname = tkutil.entry_field(self.top, 'Project: ', '', 30)
    self.prjname.frame.pack(side = 'top', fill = 'both', expand = 1)
    # separator
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    # spectra
    self.spec_list = []
    
    for i in range(0,4):
      spec_frame = Tkinter.Frame(self.top, width = 500, height = 25)
      spec_frame.pack(side = 'top', anchor = 'nw')
      spec = sputil.spectrum_menu(session, spec_frame, 'Spectrum: ')
      spec.frame.pack(side = 'top', anchor = 'w')
      type_list = ('DO NOT APPLY', '15N-NOESY', '13C-NOESY (ali)', '13C-NOESY (aro)', '2D-NOESY')
      type_om = tkutil.option_menu(spec_frame, "Type: ", type_list, 'DO NOT APPLY')
      type_om.frame.pack(side = 'top', anchor = 'nw')
      self.spec_list.append( (spec, type_om) )
      sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
      sep.pack(fill="both", padx=5,pady=5, side = 'top')
      
      
    #auto_list = ('Use current peaks and assignments', 'Use automatically picked peaks')
    #self.auto_om = tkutil.option_menu(self.top, "NOEs: ", auto_list, 'Use current peaks and assignments')
    #self.auto_om.frame.pack(side = 'top', anchor = 'nw')
    
    # Disulfide bond
    self.ssbond = tkutil.entry_field(self.top, 'Disulfide bonds (e.g. 5-13,2-34): ', '', 25)
    self.ssbond.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # White list
    self.whitelist = tkutil.entry_field(self.top, 'White lists (e.g. 5-13,2-34): ', '', 30)
    self.whitelist.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # Black list
    self.blacklist = tkutil.entry_field(self.top, 'Black lists (e.g. 5-13,2-34): ', '', 30)
    self.blacklist.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # Buttons
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    self.br = tkutil.button_row(self.top,
#         ('Find peaks', self.ponderosapeak_cb),
			   ('Run', self.call_submit_cb),
         ('Refine', self.call_pick_cb),
         ('ARECA', self.call_areca_cb),			   
			   ('Check', self.ponderosacheck_cb),
         ('Stop', self.stop_cb),
	   	   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')
    
    tkutil.create_hint(self.br.buttons[0], 'Start 3D structure calculation by NMRFAM PONDEROSA-C/S with PONDEROSA-X refinement option. If you want to use other options including using user constraints, please use Ponderosa Client (cp) program. If you check apply peak picking option below, this will automatically pick peaks, too. Also, if you know you have similar structures are in the PDB, using PACSY may improve the results.')
    tkutil.create_hint(self.br.buttons[1], 'Refine existing NOE peaks by restricting with current chemical shifts. If you check apply peak picking option below, this will automatically pick peaks, too.')    
    tkutil.create_hint(self.br.buttons[2], 'Run NMRFAM ARECA chemical shift validation. If you check apply peak picking option below, this will automatically pick peaks, too.')    
    tkutil.create_hint(self.br.buttons[3], 'Check current status of PONDEROSA-C/S job. It will be sent to your email inbox.')    
            
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
    self.m_pacsyoption = Tkinter.IntVar()
    self.m_pacsyoption.set(1)
    pacsytype_cb = Tkinter.Checkbutton(self.top, text = 'Use PACSY supportive scores', variable = self.m_pacsyoption, onvalue=1, offvalue = 0)
    pacsytype_cb.pack(side = 'top', anchor = 'w')
    
    self.m_pickoption = Tkinter.IntVar()
    self.m_pickoption.set(1)
    picktype_cb = Tkinter.Checkbutton(self.top, text = 'Apply auto peak picking', variable = self.m_pickoption, onvalue=1, offvalue = 0)
    picktype_cb.pack(side = 'top', anchor = 'w')
    
    tol_frame = Tkinter.Frame(self.top)
    tol_frame.pack(side = 'top', fill='both')
       
    self.ntol = tkutil.entry_field(tol_frame, 'N tol.:', initial = 0.350, width = 5)
    self.ntol.frame.grid(row = 0, column=0)     
    self.ntol_ppm = self.ntol.variable
          
    self.ctol = tkutil.entry_field(tol_frame, ', C tol.:', initial = 0.350, width = 5)
    self.ctol.frame.grid(row = 0, column=2)
    self.ctol_ppm = self.ctol.variable     
         
    self.htol = tkutil.entry_field(tol_frame, ', H tol.:', initial = 0.025, width = 5)
    self.htol.frame.grid(row=0, column=4)    
    self.htol_ppm = self.htol.variable
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
    self.notice_text = Tkinter.StringVar()    
    self.notice_text.set("* Please follow BMRB nomenclature (Use 'ca' tool).")    
    self.notice = Tkinter.Label(self.top, textvariable = self.notice_text, anchor = 'w', justify = 'left')		
    self.notice.pack(side = 'top', anchor = 'w')
    
    self.notice_text2 = Tkinter.StringVar()    
    self.notice_text2.set("* Just detach the last digit for pseudoatom.")    
    self.notice2 = Tkinter.Label(self.top, textvariable = self.notice_text2, anchor = 'w', justify = 'left')		
    self.notice2.pack(side = 'top', anchor = 'w')
    
    #self.notice2_text = Tkinter.StringVar()    
    #self.notice2_text.set(" to obtain NOESY peaks first.")    
    #self.notice2 = Tkinter.Label(self.top, textvariable = self.notice2_text, anchor = 'w', justify = 'left')		
    #self.notice2.pack(side = 'top', anchor = 'w')    
    
    self.progress_label = Tkinter.Label(self.top, anchor = 'nw')
    self.progress_label.pack(side = 'top', anchor = 'w')    
    
    tkutil.Stoppable.__init__(self, self.progress_label, self.br.buttons[4])
    self.packedfile = os.path.join(os.path.expanduser("~"), 'packed_inputs.txt')
    
  def call_submit_cb(self):
    self.stoppable_call(self.ponderosasubmit_cb)
  
  def call_pick_cb(self):
    self.stoppable_call(self.ponderosapick_cb)

  def call_areca_cb(self):
    self.stoppable_call(self.arecasubmit_cb)    
    
  def IsSequential(self, peak, resonancegroup_list, axis_order):
    # get two proton chemical shifts
    if len(peak.frequency) == 3:
      if axis_order < 2:
        cs = peak.frequency[0]
        cs2 = peak.frequency[1]
      elif axis_order < 4:
        cs = peak.frequency[0]
        cs2 = peak.frequency[2]
      else:
        cs = peak.frequency[1]
        cs2 = peak.frequency[2]
    elif len(peak.frequency) == 2:
      cs = peak.frequency[0]
      cs2 = peak.frequency[1]
      
    # get index for one
    iSeq = -1
    iSeq2 = -1
    for resonancegroup in resonancegroup_list:
      if abs(resonancegroup[5] - cs) < self.hppm:
        iSeq = resonancegroup[0]
        break
      
    # find sequential
    for resonancegroup in resonancegroup_list:
      if abs(resonancegroup[0]-iSeq) > 1: continue
      if abs(resonancegroup[5] - cs2) < self.hppm:
        return 1
    return 0      
    
  def bmrb_cb(self):
    import webbrowser
    webbrowser.open('http://bmrb.wisc.edu/ref_info/statsel.htm')      
    
  def submission(self, web_mode):
    if self.m_pickoption.get() == 1:
      if self.verbose == 1:
        tkMessageBox.showinfo('Notification', 'Please wait a few minutes to pick and refine peaks.')
    else:
      if self.verbose == 1: 
        tkMessageBox.showinfo('Notification', 'Please wait a few seconds to refine peaks.')
      
    try:
      htol = float(self.htol_ppm.get())
      ctol = float(self.ctol_ppm.get())
      ntol = float(self.ntol_ppm.get())
      self.hppm = htol
      self.cppm = ctol
      self.nppm = ntol
    except:
      if self.verbose == 1:   
        tkMessageBox.showerror('Error', 'Tolerance value is set improperly.')
      return
              
    session = self.session
    # check inputs
    # username
    szUserName=self.username.variable.get()
    if szUserName == '' and web_mode != -1:
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Your name is necessary to receive results.')
      return      
    if szUserName.find(',') != -1:  
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Please use regular alphabets.')
      return      
    # email
    szEmail = self.email.variable.get()
    if ((szEmail == '') or (szEmail.find('@') == -1)) and (web_mode != -1): 
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Your email is necessary to receive results.')
      return      
    if szEmail.find(',') != -1:  
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Please use regular alphabets.')
      return      
    # prj
    szPrj = self.prjname.variable.get()
    if szPrj == '' and web_mode != -1: 
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Your project name is necessary to receive results.')
      return      
    if szPrj.find(',') != -1 and web_mode != -1:  
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Please use regular alphabets.')
      return
    # spectra
    spec_list = []
    for (spec,type_om) in self.spec_list:
      if type_om.get() == 'DO NOT APPLY':        continue
      if spec == None: continue
      if spec.spectrum().dimension > 3: continue      # 4D not supported for now
      if type_om.get() == '15N-NOESY': spec_type = 0
      elif type_om.get() == '13C-NOESY (ali)': spec_type = 1
      elif type_om.get() == '13C-NOESY (aro)': spec_type = 2
      elif type_om.get() == '2D-NOESY': spec_type = 3
      
      # find axis order
      axis_order = axis_order_for_ponderosa(spec.spectrum(), spec_type)
      if axis_order[0] == '': continue
      
      if (spec.spectrum().name.find(':') != -1): 
        if self.verbose == 1: tkMessageBox.showerror('Warning', 'Duplicated view (%s) is not preferred for PONDEROSA. However, keep proceeding...' % (spec.spectrum().name))      
      
      spec_list.append((spec.spectrum(), spec_type, spec.spectrum().name, axis_order))
    if len(spec_list) == 0:
      if self.verbose == 1: tkMessageBox.showerror('Error', 'No available NOESY found.')
      return      
          
    # sequence
    seqgroup_list = myseq.BuildSequence(self.session, 3)
    seqgroup_list = myseq.CheckSequence(seqgroup_list) # sort and fill the gap
    if myseq.GapInSequence(seqgroup_list) == 1: # there is a gap
      if self.verbose == 1: tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
      seqgroup_list = myseq.LoadSeq(session, seqgroup_list)
      if myseq.GapInSequence(seqgroup_list) == 1:
        if self.verbose == 1: tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
        return

    # ssbond
    szSSbond = self.ssbond.variable.get().strip()
    szSSline = ''
    try:
      if szSSbond != '':
        sslist = szSSbond.split(',')
        for ss in sslist:
          s_and_s = ss.strip().split('-')
          szSSline = szSSline + ',%d-%d' % (int(s_and_s[0]), int(s_and_s[1]))
        szSSline = szSSline[1:]
    except:
      tkMessageBox.showerror('Disulfide bond', 'Disulfide bond setting is wrong.')
      return
      
    # whitelist
    szWhiteList = self.whitelist.variable.get().strip()
    white_list = []
    try:
      if szWhiteList != '':
        wlist = szWhiteList.split(',')
        for ww in wlist:
          w_and_w = ww.strip().split('-')
          wline = '%3d XXX %3d XXX' % (int(w_and_w[0]), int(w_and_w[1]))
          white_list.append(wline)
    except:
      tkMessageBox.showerror('Whitelist', 'Whitelist setting is wrong.')
      return
      
    # blacklist
    szBlackList = self.blacklist.variable.get().strip()
    black_list = []
    try:
      if szBlackList != '':
        blist = szBlackList.split(',')
        for bb in blist:
          b_and_b = bb.strip().split('-')
          bline = '%3d XXX %3d XXX' % (int(b_and_b[0]), int(b_and_b[1]))
          black_list.append(bline)
    except:
      tkMessageBox.showerror('Blacklist', 'Blacklist setting is wrong.')
      pass
      
    for peak in self.session.selected_peaks():
      if peak == None: continue
      peak.selected = 0    
      
    iSeqCount = len(seqgroup_list)
    iHour = int(float(iSeqCount) / 70.0 * 2.0)
    seqlines = ['[START]-[nmrfamsparky.seq]']
    # build sequence
    for seqgroup in seqgroup_list:
      line = '%7s %4d' % (myseq.a2aaa(seqgroup[1]), seqgroup[0])
      seqlines.append(line.strip())
    seqlines.append('[END]-[nmrfamsparky.seq]')  
    if len(seqlines) == 2:
      if self.verbose == 1: tkMessageBox.showerror('Error', 'No available sequence found.')
      return
    # build chemical shift
    # group.number, aaa, atom.name, atom_type, isotope, frequency, deviation
    resonancegroup_list = myseq.BuildResonance(self.session)
    iCurIdx = 1
    cslines = ['[START]-[nmrfamsparky.prot]']
    
    n_group_list = []
    c_group_list = []
    aro_group_list = []
    h_group_list = []
    
    for resonancegroup in resonancegroup_list:
      line = '%4d %8.3f %8.3f %5s %d' % (iCurIdx, resonancegroup[5], resonancegroup[6], resonancegroup[2], resonancegroup[0])
      cslines.append(line.strip())
      iCurIdx = iCurIdx + 1
    
      if resonancegroup[3] == 'N': 
        n_group = [resonancegroup, []]
        for resonancegroup2 in resonancegroup_list:
          if resonancegroup2[3] != 'H': continue
          if resonancegroup[0] != resonancegroup2[0]: continue
          if resonancegroup[2] == 'N':
            if resonancegroup2[2] == 'H' or resonancegroup2[2] == 'HN': n_group[1].append(resonancegroup2) 
          else:
            if resonancegroup2[2][1:].find(resonancegroup[2][1:]) != -1: n_group[1].append(resonancegroup2)
        n_group_list.append(n_group)    
      elif resonancegroup[3] == 'C' and len(resonancegroup[2]) > 1 and resonancegroup[2] != 'CO':
        c_group = [resonancegroup, []]
        for resonancegroup2 in resonancegroup_list:
          if resonancegroup2[3] != 'H': continue
          if resonancegroup[0] != resonancegroup2[0]: continue
          if resonancegroup2[2][1:].find(resonancegroup[2][1:]) != -1: c_group[1].append(resonancegroup2)
        if resonancegroup[5] < 85: c_group_list.append(c_group)       
        else: aro_group_list.append(c_group)
        
    cslines.append('[END]-[nmrfamsparky.prot]')    
    if len(seqlines) == 2:
      if self.verbose == 1: tkMessageBox.showerror('Error', 'No available chemical shift found.')
      return
 
    iPeakCount = 0
         
    # spectra
    upl_list = []
    pks_list = []
    
    iAroOn = 0
    for (spec, spec_type, spec_name, axis_order) in spec_list:
      # check auto picking
      if self.m_pickoption.get() == 1:
        # negative
        self.progress_report(spec.name + ' local maxima: neg' )         
          
        regions = spec.region
        
        if spec.dimension == 3:
          if (regions[1][0] > regions[1][1]) and (regions[1][0] > regions[1][2]):          iNC = 0
          elif (regions[1][1] > regions[1][0]) and (regions[1][1] > regions[1][2]):        iNC = 1
          else:          iNC = 2    
          
          if iNC == 0:
            if spec.sweep_width[1] / spec.sweep_width[2] > 1.3: iH = 2
            elif spec.sweep_width[2] / spec.sweep_width[1] > 1.3: iH = 1
            elif spec.data_size[1] > spec.data_size[2]: iH = 2
            else: iH = 1
          elif iNC == 1:
            if spec.sweep_width[0] / spec.sweep_width[2] > 1.3: iH = 2
            elif spec.sweep_width[2] / spec.sweep_width[0] > 1.3: iH = 0
            elif spec.data_size[0] > spec.data_size[2]: iH = 2
            else: iH = 0
          elif iNC == 2:
            if spec.sweep_width[1] / spec.sweep_width[0] > 1.3: iH = 0
            elif spec.sweep_width[0] / spec.sweep_width[1] > 1.3: iH = 1
            elif spec.data_size[1] > spec.data_size[0]: iH = 0
            else: iH = 1  
        min_linewidth = spec.pick_minimum_linewidth
        min_dropoff = spec.pick_minimum_drop_factor    
        view = self.get_view(spec)
        
        region = [] 

        for regions2 in regions:
          region.append(list(regions2))
  
        if spec_type == 0: # N
          group_list = n_group_list
          heavytol = ntol
        elif spec_type == 1: # C
          group_list = c_group_list
          heavytol = ctol
        elif spec_type == 2: # aro
          group_list = aro_group_list
          heavytol = ctol  
          iAroOn = 1
        else: group_list = []
        
        for i in range(len(group_list)):          
          group = group_list[i]
          self.progress_report(spec.name + ' local maxima: %d / %d' % (i+1, len(group_list)) )        
          height_thresholds = (view.negative_levels.lowest, view.positive_levels.lowest)
          if len(group[1]) == 0: continue
          region[0][iNC] = group[0][5]-heavytol
          region[1][iNC] = group[0][5]+heavytol 
          for resonancegroup in group[1]:
            region[0][iH] = resonancegroup[5]-htol
            region[1][iH] = resonancegroup[5]+htol 
            spec.pick_peaks(region, height_thresholds, min_linewidth, min_dropoff)

        if spec_type == 3: # 2D
          height_thresholds = (view.negative_levels.lowest, view.positive_levels.lowest)
          spec.pick_peaks(region, height_thresholds, min_linewidth, min_dropoff)
                  
      # select only one sign..
      self.progress_report(spec_name + ' filtering...')      
      iPos = 0
      for peak in spec.peak_list():
        if peak.data_height == None: continue      
        if peak.data_height > 0: iPos = iPos + 1
        else: iPos = iPos - 1
      
      for peak in spec.peak_list():
        if peak.data_height == None: peak.selected = 1
        elif peak.data_height * iPos > 0: peak.selected = 0
        else: peak.selected = 1
      self.session.command_characters("") # delete selected peaks
      import time
      time.sleep(2)                                
      
      peak_list = []
      # filter by chemical shift first
      for peak in spec.peak_list():
        peak.selected = 1
        peak.color = 'yellow'
        if spec.dimension == 2:
          valid = [0,0,1]
        else:
          valid = [0,0,0]
                    
        # filtering
        for resonancegroup in resonancegroup_list:
          if valid == [1,1,1]: break
          if (resonancegroup[2][0:1] == 'H') or (resonancegroup[2][0:1] == 'Q') or (resonancegroup[2][0:1] == 'M'): tol = htol
          elif resonancegroup[2][0:1] == 'N': tol = ntol
          else: tol = ctol
          for i in range(len(peak.frequency)):
            #if spec.nuclei[i].find(resonancegroup[2]) == -1: continue
            #group.number, aaa, atom.name, atom_type, isotope, frequency, deviation
            if abs(peak.frequency[i]-resonancegroup[5]) < tol:
              valid[i] = 1
              
        if valid == [1,1,1]:
          peak.selected = 0
          peak.color = 'white'
          peak_list.append(peak)  
      
      iPeakCount = iPeakCount + len(peak_list)
      
      
      if web_mode == -1: continue

      
      self.progress_report(spec_name + ' analyzing...')    
      # generate pks1, pks2, pks3
      pks1_list = []
      pks2_list = []
      pks3_list = []
      pks1_list.append('[START]-[%s.pks1]' % spec_name)
      pks2_list.append('[START]-[%s.pks2]' % spec_name)
      pks3_list.append('[START]-[%s.pks3]' % spec_name)
      pks1_list.append('NOESYTYPE %d %s' % (spec_type, spec_type_in_string(spec_type)))
      pks2_list.append('NOESYTYPE %d %s' % (spec_type, spec_type_in_string(spec_type)))
      pks3_list.append('NOESYTYPE %d %s' % (spec_type, spec_type_in_string(spec_type)))
      pks1_list.append('AXISORDER %d %s' % (axis_order[1], axis_order[0]))
      pks2_list.append('AXISORDER %d %s' % (axis_order[1], axis_order[0]))
      pks3_list.append('AXISORDER %d %s' % (axis_order[1], axis_order[0]))
      pks1_list.append('')
      pks2_list.append('')
      pks3_list.append('')
      
      for peak in peak_list:
        if peak.data_height == None: continue
        
        if spec.dimension == 3:
          szLine = '%8.3f %8.3f %8.3f %11.3f %8s %8s %8s' % (peak.frequency[0], peak.frequency[1], peak.frequency[2], abs(peak.data_height), 'X', 'X', 'X')          
          # diagonal
          if (abs(peak.frequency[0] - peak.frequency[1]) < htol) or (abs(peak.frequency[0] - peak.frequency[2]) < htol) or (abs(peak.frequency[1] - peak.frequency[2]) < htol):
            pks1_list.append(szLine)
            continue
          
        elif spec.dimension == 2:
          szLine = '%8.3f %8.3f %11.3f %8s %8s' % (peak.frequency[0], peak.frequency[1], abs(peak.data_height), 'X', 'X')
          # diagonal
          if (abs(peak.frequency[0] - peak.frequency[1]) < htol):
            pks1_list.append(szLine)
            continue
          
        # sequential
        if self.IsSequential(peak, resonancegroup_list, axis_order[1]) == 1:
          pks2_list.append(szLine)
        # inter          
        else:
          pks3_list.append(szLine)
          
      pks1_list.append('[END]-[%s.pks1]' % spec_name)
      pks2_list.append('[END]-[%s.pks2]' % spec_name)
      pks3_list.append('[END]-[%s.pks3]' % spec_name)
      
      pks_list.append((pks1_list, pks2_list, pks3_list))
      
      # build external upl
      for peak in peak_list:
        if peak.is_assigned == 0: continue
        if peak.resonances() == None: continue
        if len(peak.resonances()) == 3:
          if axis_order[1] < 2:
            resonance1 = peak.resonances()[1]
            resonance2 = peak.resonances()[2]
          elif axis_order[1] < 4:  
            resonance1 = peak.resonances()[0]
            resonance2 = peak.resonances()[2]
          else:  
            resonance1 = peak.resonances()[0]
            resonance2 = peak.resonances()[1]
        elif len(peak.resonances()) == 2:    
            resonance1 = peak.resonances()[0]
            resonance2 = peak.resonances()[1]        
            
        # only use non sequential
        if abs(resonance1.group.number - resonance2.group.number) < 2: continue
        
        # generate upl file- 5.5A * 120%
        szLine = '%3d %3s %5s  %3d %3s %5s 6.6' % (resonance1.group.number, myseq.a2aaa(resonance1.group.symbol), resonance1.atom.name, resonance2.group.number, myseq.a2aaa(resonance2.group.symbol), resonance2.atom.name)
        upl_list.append(szLine)
        
    if iPeakCount < iSeqCount * 5 :
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Not enough NOESY peak found.')
      return    


    if web_mode == -1: 
      self.session.command_characters("") # delete selected peaks      
      tkMessageBox.showinfo('Finished', 'Peak picking and refining finished.')
      return        
    
    ponderosa_template = szTemplatePackedInputs.split()
    # name
    iLine = ponderosa_template.index('USERNAME1=ponderosa_username1')
    ponderosa_template[iLine] = 'USERNAME1=%s' % (szUserName)
    # email
    iLine = ponderosa_template.index('USERMAIL1=ponderosa_usermail1')
    ponderosa_template[iLine] = 'USERMAIL1=%s' % (szEmail)
    # proj
    iLine = ponderosa_template.index('USERPROJ=ponderosa_project')
    ponderosa_template[iLine] = 'USERPROJ=%s' % (szPrj)
    # NOESY -> NOESYCOUNT=0
    iLine = ponderosa_template.index('NOESYCOUNT=0')
    ponderosa_template[iLine] = 'NOESYCOUNT=%d' % (len(pks_list))
    # CONST -> CONSTCOUNT=0
    # how many constraints?
    iConstFile = 0
    if len(upl_list) != 0:    iConstFile = iConstFile + 1
    if len(white_list) != 0:  iConstFile = iConstFile + 1
    if len(black_list) != 0:  iConstFile = iConstFile + 1
    
    iLine = ponderosa_template.index('CONSTCOUNT=0')
    ponderosa_template[iLine] = 'CONSTCOUNT=%d' % (iConstFile)
    
    # Tolerance
    iLine = ponderosa_template.index('H_PPM=$HTOLERANCE')
    ponderosa_template[iLine] = 'H_PPM=%f' % (htol)
    iLine = ponderosa_template.index('C_PPM=$CTOLERANCE')
    ponderosa_template[iLine] = 'C_PPM=%f' % (ctol)
    iLine = ponderosa_template.index('N_PPM=$NTOLERANCE')
    ponderosa_template[iLine] = 'N_PPM=%f' % (ntol)
    # SSbond
    iLine = ponderosa_template.index('SS=$SSBOND')
    ponderosa_template[iLine] = 'SS=%s' % (szSSbond)
      
    # fill header for files
    self.progress_report('Creating packed_inputs.txt...')
    iLine = ponderosa_template.index('[END]-[parameters.ini]')
    iCurIdx = 1    
    for (spec, spec_type, spec_name, axis_order) in spec_list:
      ponderosa_template.insert(iLine, "[NOESY_%d]" % (iCurIdx))
      iCurIdx = iCurIdx + 1
      ponderosa_template.insert(iLine+1, "[END]")
      ponderosa_template.insert(iLine+1, "NOESYTYPE=%d" % (spec_type))
      ponderosa_template.insert(iLine+1, "AXISTYPE=%d" % (axis_order[1]))
      ponderosa_template.insert(iLine+1, "AXISORDER=%s" % (axis_order[0]))
      ponderosa_template.insert(iLine+1, "RANGE2=100.000000")
      ponderosa_template.insert(iLine+1, "RANGE1=100.000000")
      ponderosa_template.insert(iLine+1, "UCSFPATH=/home/ponderosa")
      clean_spec_name = spec_name
      clean_spec_name.replace(":", "_")
      ponderosa_template.insert(iLine+1, "UCSFNAME=%s.peaks" % (clean_spec_name))
      
    iConstFile = 1
    if len(upl_list) != 0:
      iLine = ponderosa_template.index('[END]-[parameters.ini]')
      ponderosa_template.insert(iLine, "[CONST_%d]" % (iConstFile))
      ponderosa_template.insert(iLine+1, "[END]")
      ponderosa_template.insert(iLine+1, "CONSTTYPE=1")
      ponderosa_template.insert(iLine+1, "CONSTPATH=/home/ponderosa")
      ponderosa_template.insert(iLine+1, "CONSTNAME=nmrfamsparky.upl")
      iConstFile = iConstFile + 1
    
    if len(white_list) != 0:
      iLine = ponderosa_template.index('[END]-[parameters.ini]')
      ponderosa_template.insert(iLine, "[CONST_%d]" % (iConstFile))
      ponderosa_template.insert(iLine+1, "[END]")
      ponderosa_template.insert(iLine+1, "CONSTTYPE=6")
      ponderosa_template.insert(iLine+1, "CONSTPATH=/home/ponderosa")
      ponderosa_template.insert(iLine+1, "CONSTNAME=nmrfamsparky.wlt")
      iConstFile = iConstFile + 1
      
    if len(black_list) != 0:
      iLine = ponderosa_template.index('[END]-[parameters.ini]')
      ponderosa_template.insert(iLine, "[CONST_%d]" % (iConstFile))
      ponderosa_template.insert(iLine+1, "[END]")
      ponderosa_template.insert(iLine+1, "CONSTTYPE=5")
      ponderosa_template.insert(iLine+1, "CONSTPATH=/home/ponderosa")
      ponderosa_template.insert(iLine+1, "CONSTNAME=nmrfamsparky.blt")
      iConstFile = iConstFile + 1
  
    iLine = ponderosa_template.index('[END]-[parameters.ini]') + 1
    ponderosa_template = ponderosa_template[0:iLine] + seqlines + ponderosa_template[iLine:]
    iLine = ponderosa_template.index('[END]-[parameters.ini]') + 1
    ponderosa_template = ponderosa_template[0:iLine] + cslines + ponderosa_template[iLine:]
    
      
    # fill files  
    iLine = ponderosa_template.index('[END]-[parameters.ini]') + 1
    if len(upl_list) != 0:  
      upl_list.insert(0, '[START]-[nmrfamsparky.upl]')
      upl_list.append('[END]-[nmrfamsparky.upl]')
      ponderosa_template = ponderosa_template[0:iLine] + upl_list + ponderosa_template[iLine:]
      
    iLine = ponderosa_template.index('[END]-[parameters.ini]') + 1
    if len(white_list) != 0:  
      white_list.insert(0, '[START]-[nmrfamsparky.wlt]')
      white_list.append('[END]-[nmrfamsparky.wlt]')
      ponderosa_template = ponderosa_template[0:iLine] + white_list + ponderosa_template[iLine:]
      
    iLine = ponderosa_template.index('[END]-[parameters.ini]') + 1
    if len(black_list) != 0:  
      black_list.insert(0, '[START]-[nmrfamsparky.blt]')
      black_list.append('[END]-[nmrfamsparky.blt]')
      ponderosa_template = ponderosa_template[0:iLine] + black_list + ponderosa_template[iLine:]
      
    iLine = ponderosa_template.index('[END]-[parameters.ini]')+1  
    for (pks1_list, pks2_list, pks3_list) in pks_list:      
      ponderosa_template = ponderosa_template[0:iLine] + pks1_list + pks2_list + pks3_list + ponderosa_template[iLine:]
    
    # save
    f=open(self.packedfile, 'w')
    for line in ponderosa_template:
      f.write("%s\n" % line)
    f.close()
    
    import posthtml
    import httplib
    
    if web_mode == 0:
      ponderosa_url = 'ponderosa.nmrfam.wisc.edu'
      ponderosa_selector = '/cgi-bin/ponderosauploader.cgi'
      content = posthtml.get_file_content(self.packedfile)

      if self.m_pacsyoption.get() == 1:
        fields = ( ('pdb_id','AUTO'),
                   ('chain_id','AUTO'),
                   ('username','guest'), 
                   ('keyphrase','guest'), 
                   ('use_pacsy','use_pacsy'), 
                  )
      else:        
        fields = ( ('pdb_id','AUTO'),
                   ('chain_id','AUTO'),
                   ('username','guest'), 
                   ('keyphrase','guest'), 
                   ('use_pacsy','no_pacsy'), 
                  )    
      files=[['packed_input','packed_inputs.txt',content],]
      text=posthtml.post_multipart(ponderosa_url, ponderosa_selector, fields, files)
      if self.m_pickoption.get() == 1:
        self.session.command_characters("") # delete selected peaks
      if self.verbose == 1: tkMessageBox.showinfo("PONDEROSA-X job submitted.","Check your email. Approx. calc. time: %d h. Use Ponderosa Client/Analyzer to experience full PONDEROSA-C/S features." % iHour) 
    elif web_mode == 1: # areca
      areca_url = 'areca.nmrfam.wisc.edu'
      areca_selector = '/upload_file.php'
      content = posthtml.get_file_content(self.packedfile)

      if iAroOn == 0:
        fields = ( ('FORMAT','POND'), ('VTYPE','BBali'), )
      else:  
        fields = ( ('FORMAT','POND'), ('VTYPE','BBaliaro'), )      
      files=[['Ass','packed_inputs.txt',content],]
      text=posthtml.post_multipart(areca_url, areca_selector, fields, files)
      if self.verbose == 1: tkMessageBox.showinfo("ARECA job submitted.","Check your email periodically.")

  def arecasubmit_cb(self):
    self.submission(1)
    pass
        
  def ponderosasubmit_cb(self):
    self.submission(0)
    pass
  def ponderosapick_cb(self):
    self.submission(-1)
    pass
  def ponderosacheck_cb(self):
    # email
    szEmail = self.email.variable.get()
    if (szEmail == '') or (szEmail.find('@') == -1): 
      if self.verbose == 1: tkMessageBox.showerror('Error', 'Your email is necessary to check PONDEROSA status.')
      return      
    
    import posthtml
    import httplib
    ponderosa_url = 'ponderosa.nmrfam.wisc.edu'
    ponderosa_selector = '/cgi-bin/ponderosacheck.cgi'
    content = posthtml.get_file_content(self.packedfile)

    fields = ( ('check_email',szEmail),)
    files=[]
    text=posthtml.post_multipart(ponderosa_url, ponderosa_selector, fields, files)
    
    if self.verbose == 1: tkMessageBox.showinfo("Ponderosa Status Check.","Check your email.") 
    
    
    pass
    
  # ---------------------------------------------------------------------------
  #
  def get_view(self, spectrum):
    view = None
    for i in range(len(self.session.project.view_list())):
      view = self.session.project.view_list()[i]
      if view.spectrum == spectrum:
        return view
    return None    
  


# -----------------------------------------------------------------------------
#
def ponderosa_cs(session):
  sputil.the_dialog(ponderosa_dialog,session).show_window(1)
