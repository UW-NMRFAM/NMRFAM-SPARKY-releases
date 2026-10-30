# -----------------------------------------------------------------------------
# CHESCA-SPARKY
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: March 31, 2020 - in progress
# 
#
# -----------------------------------------------------------------------------
# CITATION:
#          TBA
# -----------------------------------------------------------------------------

import os
import Tkinter

import sparky
import sputil
import tkutil
import wlutil
import shutil
import myseq
import nmrfam
import chescautil
import tkMessageBox
import tkFileDialog
import tkSimpleDialog
import posthtml

# for token
import time
import random

class chespa_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'CHESPA-SPARKY automation')
    user_name_ef, user_email_ef, user_seq_ff = \
                              wlutil.user_and_seq(self, USERINFO=False)
    # for now, invisible
    user_seq_ff.frame.pack_forget()

    topfrm = Tkinter.Frame(self.top)
    topfrm.pack(side='top', fill = 'both', expand = 0)

    # canvas
    canvasfrm = Tkinter.Frame(topfrm)
    canvasfrm.pack(side='right', fill = 'both', expand = 0)
    sc = Tkinter.Canvas(canvasfrm, width=150, height=150, bd=0)
    sc.pack()
    self.sc = sc
    self.draw_vectors(1)
    
    specfrm = Tkinter.Frame(topfrm)
    specfrm.pack(side='top', fill = 'both', expand = 0)

    vec2 = Tkinter.Label(specfrm, text = 'Reference vector (B, 1 --> 2):', 
                                anchor = 'w', justify = 'left')
    vec2.pack(side = 'top', anchor = 'w')
    self.sp1 = sputil.spectrum_menu(session, specfrm, \
                          'State 1: ', allow_no_choice = True) # Apo-mutant
    self.sp2 = sputil.spectrum_menu(session, specfrm, \
                          'State 2: ', allow_no_choice = True) # Holo-mutant
    self.sp1.frame.pack(side = 'top', anchor = 'w')
    self.sp2.frame.pack(side = 'top', anchor = 'w')

    sep = Tkinter.Frame(specfrm, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    vec = Tkinter.Label(specfrm, text = 'Perturbation vector (A):', 
                                anchor = 'w', justify = 'left')
    vec.pack(side = 'top', anchor = 'w')
    self.sp3 = sputil.spectrum_menu(session, specfrm, \
                          'State 3: ', allow_no_choice = True) # Apo-wildtype
    self.sp3.frame.pack(side = 'top', anchor = 'w')

    # Options
    # Perturbation
    ptfrm = Tkinter.Frame(self.top)
    ptfrm.pack(side='top', fill='both', expand = 0)
    pt_label = Tkinter.Label(ptfrm, text='Perturbation vector options: ' \
                            ).pack(anchor='w',side='left')
    self.pt_mode = Tkinter.IntVar()
    self.pt_mode.set(1)
    rb_1 = Tkinter.Radiobutton(ptfrm, text='1 --> 3 ',
            variable=self.pt_mode, value=1, command=self.set_vector_cb
            ).pack(anchor='w',side='left')
    rb_2 = Tkinter.Radiobutton(ptfrm, text='2 --> 3 ',
            variable=self.pt_mode, value=2, command=self.set_vector_cb
            ).pack(anchor='w',side='left')

    # filtering option
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    param_frame = Tkinter.Frame(self.top, width = 600)
    param_frame.pack(side='top', anchor='nw', expand = 0)

    # interpeak minimum difference option
    ipfilter_frame = Tkinter.Frame(param_frame)
    ipfilter_frame.pack(side='bottom', anchor='sw', expand = 0)
    ipfilters = ['Not used', 'User', 'Avg. line width']
    # three options. 1. do not apply, 2. user defined, 3. avg. line width
    self.ipfilter_om = tkutil.option_menu(ipfilter_frame, 
                                'Inter-peak min diff: ',
                                ipfilters, initial = 'Not used')
    self.ipfilter_om.frame.pack(side = 'left', anchor = 'nw')
    self.ipfilter_om.menu.bind('<<MenuSelect>>', self.ipfilter_callback)
    # inputs for user inputs
    self.ipppmcut_ef = tkutil.entry_field(ipfilter_frame, \
        ', min diff (ppm):', initial = '0.05', width = 4)
    self.ipppmcut = self.ipppmcut_ef.variable

    # intraresidue minimum difference option    
    # N scale
    nscale_ef = tkutil.entry_field(param_frame, 'N-to-H:', initial = '0.2', \
                                    width = 4)
    nscale_ef.frame.pack(side = 'left', anchor = 'n', expand = 0)
    self.nscale = nscale_ef.variable

    # PPM cutoff- 0.02
    ppmcut_ef = tkutil.entry_field(param_frame, ', Pert. min diff (ppm):', \
                                    initial = '0.05', width = 4)
    ppmcut_ef.frame.pack(side = 'left', anchor = 'n', expand = 0)
    self.ppmcut = ppmcut_ef.variable

    ppmcut2_ef = tkutil.entry_field(param_frame, ', Ref. min diff (ppm):', \
                                    initial = '0.05', width = 4)
    ppmcut2_ef.frame.pack(side = 'left', anchor = 'n', expand = 0)
    self.ppmcut2 = ppmcut2_ef.variable

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    self.br = tkutil.button_row(self.top,
			   ('Analyze', self.run_chespa_cb),
         ('Save', self.save_chespa_cb),
         ('Load', self.load_chespa_cb),
         ('Plot', self.plot_chespa_cb),
         ('PyMOL', self.pymol_cb),
         ('CHESCA-SPARKY', self.open_chesca_cb))
    self.br.frame.pack(side = 'top', anchor = 'w', expand = 0)
    
    tkutil.create_hint(self.br.buttons[0], 'Analyze a state against others.')
    tkutil.create_hint(self.br.buttons[1], 'Save current results.')
    tkutil.create_hint(self.br.buttons[2], 'Load previous results.')
    tkutil.create_hint(self.br.buttons[3], 'Plot bar charts.')
    tkutil.create_hint(self.br.buttons[4], 'Illustrate on 3D structures.')
    tkutil.create_hint(self.br.buttons[5], 'Open CHESCA-SPARKY window.')

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    sort_label = Tkinter.Label(self.top, text='Sort by ',
                                anchor = 'w', justify = 'left')
    sort_label.pack(side = 'top', anchor = 'w')    

    self.br2 = tkutil.button_row(self.top,
        ('ID', self.sort_ID_cb),
        ('Pert. Vec.(A)', self.sort_diff_cb),
        ('Ref. Vec.(B)', self.sort_diff2_cb),
        ('|Frac. Act.(X)|', self.sort_X_cb),
        ('|Cos(theta)|', self.sort_cos_cb),
        )
    self.br2.frame.pack(side = 'top', anchor = 'w', expand = 0)

    # Result 
    header = 'RES.  DIFF_A   DIFF_B   FRAC_ACT COS_THETA'
    self.resultbox = tkutil.scrolling_list(self.top, \
                  'CHESPA results\n%s' % (header), 5, xscrollbar=True)
    self.resultbox.listbox.bind('<ButtonRelease-1>', self.select_chespa_cb)
    self.resultbox.listbox.bind('<Double-Button-1>', self.chespa_center_cb)
    self.resultbox.listbox['selectmode'] = 'extended'
    self.resultbox.frame.pack(side='top', fill = 'both', expand = 1)

    self.notice_text = Tkinter.StringVar()
    self.notice_text.set("* Dbl-click to show the corresponding peak.")
    self.notice = Tkinter.Label(self.top, \
                                textvariable = self.notice_text, 
                                anchor = 'w', justify = 'left')
    self.notice.pack(side = 'bottom', anchor = 'w')    

    self.init_variables()
  # -----------------------------------------------------------------------------  
  # ipfilter callback to just pack & forget self.ipppmcut_ef
  def ipfilter_callback(self, event):
    if self.ipfilter_om.get() == 'User':
      self.ipppmcut_ef.frame.pack(side = 'left', anchor = 'w', expand = 0)
    else:
      self.ipppmcut_ef.frame.forget()
  # -----------------------------------------------------------------------------  
  def init_variables(self):
    self.chespa_job_dir = ''
    self.sequence = list(map(lambda x: 'X', range(1000)))
    self.sequence2 = list(map(lambda x: 'X', range(1000)))
    self.sequence3 = list(map(lambda x: 'X', range(1000)))
    self.min_seq, self.max_seq = 9999, -9999
    self.min_X, self.max_X = 9999, -9999
    self.min_Adiff, self.max_Adiff = 9999, -9999
    self.min_Bdiff, self.max_Bdiff = 9999, -9999
    self.min_cth, self.max_cth = 9999, -9999
  # -----------------------------------------------------------------------------  
  def draw_vectors(self, pt_mode):
    sc = self.sc
    self.sc.delete('all')
    if pt_mode == 1:
      # horz
      sc.create_line(20, 120, 130, 120)
      sc.create_line(125, 115, 130, 120)
      sc.create_line(125, 125, 130, 120)
      # X
      sc.create_line(100, 30, 100, 120, fill="red", dash=(4, 4))
      # diag
      sc.create_line(20, 120, 100, 30)
      sc.create_line(100, 30, 95, 30)
      sc.create_line(100, 30, 100, 35)
      # Labels
      sc.create_text(20, 130, anchor="center", text = "1")
      sc.create_text(125, 130, anchor="center", text = "2")
      sc.create_text(100, 20, anchor="center", text = "3")
      sc.create_text(70, 130, anchor="center", text = "B")
      sc.create_text(60, 55, anchor="center", text = "A")
      sc.create_text(55, 110, anchor="center", text = "theta")
      sc.create_text(100, 130, anchor="center", text = "X", fill="red")
    else:
      # horz
      sc.create_line(20, 120, 130, 120)
      sc.create_line(125, 115, 130, 120)
      sc.create_line(125, 125, 130, 120)
      sc.create_line(130, 120, 150, 120, fill="gray", dash=(4, 4))
      # X
      sc.create_line(100, 30, 100, 120, fill="red", dash=(4, 4))
      # diag
      sc.create_line(130, 120, 100, 30)
      sc.create_line(100, 30, 105, 30)
      sc.create_line(100, 30, 100, 35)
      # Labels
      sc.create_text(20, 130, anchor="center", text = "1")
      sc.create_text(125, 130, anchor="center", text = "2")
      sc.create_text(100, 20, anchor="center", text = "3")
      sc.create_text(70, 130, anchor="center", text = "B")
      sc.create_text(120, 55, anchor="center", text = "A")
      sc.create_text(100, 110, anchor="center", text = "PI-theta")
      sc.create_text(100, 130, anchor="center", text = "X", fill="red")

  def open_chesca_cb(self):
    sputil.the_dialog(chesca_dialog, self.session).show_window(1)    

  def export_csv(self, path):
    if len(self.resultbox.line_data) == 0:
      return

    if self.pt_mode == 1:
      lines = 'RES.,DIFF_A,DIFF_B,FRAC_ACT,COS_THETA\n'
    else:
      lines = 'RES.,DIFF_A,DIFF_B,FRAC_INH,COS_THETA\n'
    for data in self.resultbox.line_data:
      sp = data[0].strip().split()
      line = wlutil.StringListToCSV(sp) + '\n'
      lines += line

    f = open(path, 'w')
    f.write(lines)
    f.close()

  # -----------------------------------------------------------------------------
  def set_vector(self, verbose = False):
    sp1 = self.sp1.spectrum()
    sp2 = self.sp2.spectrum()
    sp3 = self.sp3.spectrum()
    if None in [sp1, sp2, sp3]:
      if verbose:
        tkMessageBox.showerror('Error', \
                  'Please set states.')
        return None, None, None, None
    pt_mode = self.pt_mode.get()
    self.draw_vectors(pt_mode)

    #
    if pt_mode == 1:
      self.br2.buttons[3]['text'] = '|Frac. Act.(X)|'
      header = 'RES.  DIFF_A   DIFF_B   FRAC_ACT COS_THETA'
    else:
      self.br2.buttons[3]['text'] = '|Frac. Inh.(X)|'
      header = 'RES.  DIFF_A   DIFF_B   Frac_Inh COS_THETA'
    header2 = 'CHESPA results\n%s' % (header)
    self.resultbox.heading['text'] = header2
      
    if pt_mode == 1:
        return sp1, sp2, sp3, sp1
    return sp1, sp2, sp3, sp2
  # -----------------------------------------------------------------------------
  #
  def set_vector_cb(self, event=None):
    sp1, sp2, sp3, sp4 = self.set_vector(verbose = False)

  # -----------------------------------------------------------------------------  
  # CHESPA run- calculate 
  # sp1: apo wt
  # sp2: holo wt
  # sp3: apo mut
  # sp4: holo mut
  def run_chespa_cb(self):
    sp1, sp2, sp3, sp4 = self.set_vector(verbose = True)
    pt_mode = self.pt_mode.get()
    if sp1 == None: return

    try:
      nratio = float(self.nscale.get())
    except:
      tkMessageBox.showerror('Error', \
                  'N-to-H ratio must be a floating value.')
      return
    try:  
      ppmcut = float(self.ppmcut.get())
      ppmcut2 = float(self.ppmcut2.get())
    except:
      tkMessageBox.showerror('Error', \
                  'Minimum difference must be a floating value.')
      return

    self.chespa_dir = os.path.join(self.session.project.sparky_directory, \
                                  'CHESPA')
    if not os.path.exists(self.chespa_dir):     
      os.makedirs(self.chespa_dir)
      
    self.chespa_job_id = time.strftime('%y%m%d_%H%M%S_') + \
                            '%06d' % random.randrange(0,1000000)        

    self.sequence = list(map(lambda x: 'X', range(1000)))
    self.sequence2 = list(map(lambda x: 'X', range(1000)))
    self.sequence3 = list(map(lambda x: 'X', range(1000)))

    # run - 1. ppm_difference, 2. fractional_shift, 3. cosine_theta
    # make 1000 empty peaks
    peak_list = list(map(lambda x: [999, 999, 999], range(1000))) 
    peak2_list = list(map(lambda x: [999, 999, 999], range(1000))) 
    peak3_list = list(map(lambda x: [999, 999, 999], range(1000)))
    sumlw_list = []

    peak_list_list = [peak_list, peak2_list, peak3_list]
    sp_list = [sp1, sp2, sp3, sp4]
    seq_list = [self.sequence, self.sequence2, self.sequence3]

    # collect shift information
    min_seq, max_seq = 9999, -9999
    self.init_variables()
    # three different spectra
    for i in range(3):
      cur_peak_list, cur_spec = \
        peak_list_list[i], sp_list[i]
      for peak in cur_spec.peak_list():
        if peak.is_assigned != 1: continue
        # parse assignment
        asgn = sputil.parse_assignment_entirely(peak.assignment)
        if asgn == None: continue # parsing failed
        seqidx = asgn[0][1]
        a = asgn[0][0]
        min_seq = min(seqidx, min_seq)
        max_seq = max(seqidx, max_seq)
        seq_list[i][seqidx] = asgn[0][0]
        if peak.frequency[0] > peak.frequency[1]: # N, H, scaled N order
          cur_peak_list[seqidx] = [peak.frequency[0], peak.frequency[1], \
                                    nratio * peak.frequency[0]]
          if peak.line_width != None: # integrated
            lw = chescautil.calc_pseudo_ppm(nratio, peak.line_width[0], \
                                    peak.line_width[1])
            sumlw_list.append(lw)                            
        else:
          cur_peak_list[seqidx] = [peak.frequency[1], peak.frequency[0], \
                                    nratio * peak.frequency[1]]
          if peak.line_width != None: # integrated
            lw = chescautil.calc_pseudo_ppm(nratio, peak.line_width[1], \
                                    peak.line_width[0])
            sumlw_list.append(lw)
    if pt_mode == 1: # 1->3
      peak_list_list.append(peak_list_list[0])
      seq_list.append(seq_list[0])
    else: # 2->3
      peak_list_list.append(peak_list_list[1])
      seq_list.append(seq_list[1])
    self.min_seq, self.max_seq = min_seq, max_seq


    if self.ipfilter_om.get() == 'User':
      try:
        ipcut = float(self.ipppmcut.get())
      except:
        tkMessageBox.showerror('Error', \
          'User defined min. inter-peak distance should be a numberic value.')
        return
    elif self.ipfilter_om.get() == 'Avg. line width':
      try:
        ipcut = sum(sumlw_list)/float(len(sumlw_list))
      except:
        tkMessageBox.showerror('Error', \
          'No integrated peak found.')
        return
    # make ipppmfilter mask
    ipppm_mask = []
    if self.ipfilter_om.get() != 'Not used':
      for i in range(3):
        cur_peak_list = peak_list_list[i]
        for seqidx in range(self.min_seq, self.max_seq):
          peak = cur_peak_list[seqidx]
          if peak[0] > 500 and seqidx not in ipppm_mask:
            ipppm_mask.append(seqidx) # no assign and add to mask list
            continue
          for seqidx2 in range(seqidx+1, self.max_seq+1):
            peak2 = cur_peak_list[seqidx2]
            if peak2[0] > 500: continue # just skip. this will be added in seqidx
            # calc distance
            ipdiff = chescautil.calc_pseudo_ppm_difference(nratio, 
                      [peak[0], peak[1]], [peak2[0], peak2[1]])
            # if distance is smaller than ipcut, mask both peaks out
            if ipdiff < ipcut:
              if seqidx not in ipppm_mask:
                ipppm_mask.append(seqidx)
              if seqidx2 not in ipppm_mask:
                ipppm_mask.append(seqidx2)
    
    # analysis and write down in result_list
    self.resultbox.clear()
    for i in range(min_seq, max_seq+1):
      if i in ipppm_mask: continue # masked out
      peak, peak2, peak3, peak4 = peak_list_list[0][i], peak_list_list[1][i], \
                                  peak_list_list[2][i], peak_list_list[3][i]
      if peak[0] > 500 or peak2[0] > 500 or peak3[0] > 500: continue # no data
      #if seq_list[0][i] != seq_list[1][i]: continue # sp1 and sp2 should be same
      # ppm difference: A- perturbation, B- reference
      Adiff = chescautil.calc_pseudo_ppm_difference(nratio, peak3[0:2], peak4[0:2])
      Bdiff = chescautil.calc_pseudo_ppm_difference(nratio, peak[0:2], peak2[0:2])
      
      if Adiff > ppmcut and Bdiff > ppmcut2:
        if peak[0:2] != peak4[0:2]: rpeak = peak
        else: rpeak = peak2
        # fractional shift
        frac_shift = chescautil.calc_fractional_shift(nratio, peak4[0:2], \
                                                      peak3[0:2], rpeak[0:2])
        # cosine theta
        cos_theta = chescautil.calc_cosine_theta(nratio, peak4[0:2], \
                                                peak3[0:2], rpeak[0:2])
        if pt_mode != 1:
          frac_shift *= -1.0
          cos_theta *= -1.0
      else:
        frac_shift, cos_theta = 0, 0 # purged
      self.min_Adiff = min(self.min_Adiff, Adiff)
      self.max_Adiff = max(self.max_Adiff, Adiff)
      self.min_Bdiff = min(self.min_Bdiff, Bdiff)
      self.max_Bdiff = max(self.max_Bdiff, Bdiff)
      self.min_X = min(self.min_X, frac_shift)
      self.max_X = max(self.max_X, frac_shift)
      self.min_cth = min(self.min_cth, cos_theta)
      self.max_cth = max(self.max_cth, cos_theta)

      # result_list data
      # seqidx, a, a2, Adiff, Bdiff, X, theta, [peak1, peak2, peak3]
      a = seq_list[0][i] # perturbation
      a2 = seq_list[2][i] # from reference
      wta = '%s%d' % (a, i)
      if a != a2: mta = '%s%d%s' % (a, i, a2)
      else: mta = wta
      if Adiff > ppmcut and Bdiff > ppmcut:
        line = '%5s %8.3f %8.3f %8.3f %8.3f' % (mta, Adiff, Bdiff, \
                                        frac_shift, cos_theta)
      else:
        line = '%5s %8.3f %8.3f %8s %8s' % (mta, Adiff, Bdiff, \
                                        '   -', '   -')

      data = [line, i, a, a2, Adiff, Bdiff, frac_shift, cos_theta, \
              peak, peak2, peak3, peak4]
      self.resultbox.append(line, data)

    # make ndpplots
    # ppm
    if pt_mode == 1:  yti = 'State 1 to 3'
    else:             yti = 'State 2 to 3'
    prefixPPM = chescautil.ndp2d_chespa_ppm_prefix(min_seq, max_seq, 
    #              self.min_Adiff, self.max_Adiff, ytitle = yti)
                  0, 1.0, ytitle = yti)
    postfixPPM = ''

    # ppm
    yti = 'State 1 to 2'
    prefixPPM2 = chescautil.ndp2d_chespa_reference_ppm_prefix(\
#                  min_seq, max_seq, self.min_Bdiff, self.max_Bdiff,
                  min_seq, max_seq, 0, 1.0,
                  ytitle = yti)
    postfixPPM2 = ''

    # X
    if pt_mode == 1:  
      xti = 'CHESPA FRACTIONAL ACTIVITY PLOT'
      yti = 'X (Fractional Activ.)'
    else:
      xti = 'CHESPA FRACTIONAL INHIBITION PLOT'
      yti = 'X (Fractional Inhib.)'
    prefixX = chescautil.ndp2d_chespa_fractional_shift_prefix(min_seq, max_seq, 
                  -1.0, 1.0, xtitle=xti, ytitle=yti)
#                  self.min_X, self.max_X, ytitle=yti)
    postfixX = ''
    # cos 
    prefixCTH = chescautil.ndp2d_chespa_cosine_theta_prefix(min_seq, max_seq, 
                                        -1.0, 1.0)
#                                        self.min_cth, self.max_cth)
    postfixCTH = ''
    iCur = 1
    iPrevSeqIdx = -9999
    for data in self.resultbox.line_data:
      seqidx, a, a2 = data[1], data[2], data[3]
      Adiff, Bdiff, X, cth = data[4], data[5], data[6], data[7]
      wta = '%s%d' % (a, seqidx)
      if a != a2: mta = '%s%d%s' % (a, seqidx, a2)
      else: mta = wta
      if iPrevSeqIdx != -9999 and iPrevSeqIdx < seqidx-1:
        for i in range(iPrevSeqIdx+1, seqidx):
          # fake zero data to keep the bar low
          line = 'DATA_%d=%d,0,0,-\n' % (iCur, i)
          postfixPPM += line  # ppm 
          postfixPPM2 += line # reference ppm 
          postfixX += line    # X
          postfixCTH += line  # cos
          iCur += 1
      # ppm 
      line = 'DATA_%d=%d,%f,0,%s:%f\n' % (iCur, seqidx, Adiff, mta, Adiff)
      postfixPPM += line
      # reference ppm 
      line = 'DATA_%d=%d,%f,0,%s:%f\n' % (iCur, seqidx, Bdiff, mta, Bdiff)
      postfixPPM2 += line
      # X
      line = 'DATA_%d=%d,%f,0,%s:%f\n' % (iCur, seqidx, X, mta, X)
      postfixX += line
      # cos
      line = 'DATA_%d=%d,%f,0,%s:%f\n' % (iCur, seqidx, cth, mta, cth)
      postfixCTH += line
      iCur += 1
      iPrevSeqIdx = seqidx

    # replace $DATACOUNT to iCur-1 and $DATALIST and postfixes
    tmp_ndp_ppm = prefixPPM.replace('$DATACOUNT', '%d' % (iCur-1))
    ndp_ppm = tmp_ndp_ppm.replace('$DATALIST', postfixPPM)

    tmp_ndp_ppm2 = prefixPPM2.replace('$DATACOUNT', '%d' % (iCur-1))
    ndp_ppm2 = tmp_ndp_ppm2.replace('$DATALIST', postfixPPM2)

    tmp_ndp_X = prefixX.replace('$DATACOUNT', '%d' % (iCur-1))
    ndp_X = tmp_ndp_X.replace('$DATALIST', postfixX)

    tmp_ndp_CTH = prefixCTH.replace('$DATACOUNT', '%d' % (iCur-1))
    ndp_CTH = tmp_ndp_CTH.replace('$DATALIST', postfixCTH)

    # write to a file
    self.chespa_job_dir = os.path.join(self.chespa_dir, \
                                  self.chespa_job_id)
    if not os.path.exists(self.chespa_job_dir):     
      os.makedirs(self.chespa_job_dir)

    self.ndp_ppm_path = os.path.join(self.chespa_job_dir, \
                                    'ndpplot_chespa_ppm.ini')
    self.ndp_ref_ppm_path = os.path.join(self.chespa_job_dir, \
                                    'ndpplot_chespa_ref_ppm.ini')
    self.ndp_X_path = os.path.join(self.chespa_job_dir, \
                                    'ndpplot_chespa_X_activ.ini')
    self.ndp_cos_path = os.path.join(self.chespa_job_dir, \
                                    'ndpplot_chespa_cos_theta.ini')
    
    f = open(self.ndp_ppm_path, 'w')
    f.write(ndp_ppm)
    f.close()

    f = open(self.ndp_ref_ppm_path, 'w')
    f.write(ndp_ppm2)
    f.close()

    f = open(self.ndp_X_path, 'w')
    f.write(ndp_X)
    f.close()

    f = open(self.ndp_cos_path, 'w')
    f.write(ndp_CTH)
    f.close()

    # save csv
    self.csv_path = os.path.join(self.chespa_job_dir, \
                                    'chespa_results.csv')
    self.export_csv(self.csv_path)

    # save peaks
    for sp in [sp1, sp2, sp3]:
      path = os.path.join(self.chespa_job_dir, sp.name + '.list')
      wlutil.WritePeakList(sp, path)

    # write CHESPA INI
    # 4 spectrum, selected mode, Nratio, Cutoff, data
    #data = [line, i, a, a2, Adiff, Bdiff, frac_shift, cos_theta, \
    #          peak, peak2, peak3]
    chespa_ini = os.path.join(self.chespa_job_dir, 'chespa.ini')
    self.make_chespa_ini(chespa_ini)

    tkMessageBox.showinfo('CHESPA-SPARKY', 
        'CHESPA job finished. ' + \
        'Click Plot button to visualize the results.')
  # -----------------------------------------------------------------------------    
  def save_chespa_cb(self):
    if self.chespa_job_dir == '':
      tkMessageBox.showerror('Error', 'You have not run a job yet.')
      return
    cur_dir = os.path.basename(self.chespa_job_dir)
    chespa_dir = os.path.dirname(self.chespa_job_dir)
    new_dir = tkSimpleDialog.askstring('New directory',
        'Please type preferred directory name.', 
        initialvalue = cur_dir)
    if new_dir == None or new_dir == '':
      return
    if new_dir.strip() != '':
      new_path = os.path.join(chespa_dir, new_dir)
      if new_path != self.chespa_job_dir:
        #os.rename(self.chespa_job_dir, new_path)
        try:
          wlutil.copyanything(self.chespa_job_dir, new_path)
        except:
          tkMessageBox.showerror('Error', 'Already existing directory.')
          return
        self.chespa_job_id = new_dir
        self.chespa_job_dir = new_path

  def load_chespa_cb(self):
    chespa_job_dir = tkFileDialog.askdirectory(initialdir = \
                              self.session.project.sparky_directory,
                              title = 'Select a CHESPA job directory',
                              mustexist = 1)
    if chespa_job_dir == '': return
    # check if ini file exists
    path = os.path.join(chespa_job_dir, 'chespa.ini')
    if not os.path.exists(path):
      tkMessageBox.showerror('Error', 'Please select a CHESPA job directory.')
      return

    self.chespa_job_dir = chespa_job_dir
    self.ndp_ppm_path = os.path.join(self.chespa_job_dir, \
                                    'ndpplot_chespa_ppm.ini')
    self.ndp_ref_ppm_path = os.path.join(self.chespa_job_dir, \
                                    'ndpplot_chespa_ref_ppm.ini')
    self.ndp_X_path = os.path.join(self.chespa_job_dir, \
                                    'ndpplot_chespa_X_activ.ini')
    self.ndp_cos_path = os.path.join(self.chespa_job_dir, \
                                    'ndpplot_chespa_cos_theta.ini')

    # load chespa ini
    self.load_chespa_ini(path)

  def load_chespa_ini(self, path):
    self.sp1.set(None)
    self.sp2.set(None)
    self.sp3.set(None)
    self.resultbox.clear()

    # 4 spectrum, selected mode, Nratio, Cutoff, data
    #data = [line, i, a, a2, Adiff, Bdiff, frac_shift, cos_theta, \
    #          peak, peak2, peak3]
    nscale = wlutil.LoadIniString(path, 'OPTIONS', 'NSCALE')
    self.nscale.set(nscale)

    cutoff = wlutil.LoadIniString(path, 'OPTIONS', 'PERT_CUTOFF')
    self.ppmcut.set(cutoff)

    cutoff = wlutil.LoadIniString(path, 'OPTIONS', 'REF_CUTOFF')
    self.ppmcut2.set(cutoff)

    cutoff = wlutil.LoadIniString(path, 'OPTIONS', 'IPFILTER')
    self.ipfilter_om.set(cutoff)

    cutoff = wlutil.LoadIniString(path, 'OPTIONS', 'IPOUTLIER')
    try:
      if cutoff != '': self.ipppmcut.set(float(cutoff))
    except:
      pass
    self.ipfilter_callback(None)

    specs = ['SPEC1', 'SPEC2', 'SPEC3', 'SPEC4']
    sps = [self.sp1, self.sp2, self.sp3]
    for i in range(4):
      sp_name = wlutil.LoadIniString(path, 'OPTIONS', specs[i])
      if sp_name != '':
        sp = wlutil.SpectrumByName(self.session, sp_name)
        if sp != None and i != 3: sps[i].set(sp_name)
    ptmode = wlutil.LoadIniString(path, 'OPTIONS', 'PTMODE')
    self.pt_mode.set(int(ptmode))
    count = int(wlutil.LoadIniString(path, 'OPTIONS', 'COUNT'))

    self.resultbox.clear()
    for i in range(count):
      sect = 'CHESPA%d' % (i+1)
      line = wlutil.LoadIniString(path, sect, 'LINE')
      nseq = int(wlutil.LoadIniString(path, sect, 'ID'))
      seq = wlutil.LoadIniString(path, sect, 'SEQ')
      seq2 = wlutil.LoadIniString(path, sect, 'SEQ2')
      Adiff = float(wlutil.LoadIniString(path, sect, 'ADIFF'))
      Bdiff = float(wlutil.LoadIniString(path, sect, 'BDIFF'))
      X = float(wlutil.LoadIniString(path, sect, 'X'))
      COS = float(wlutil.LoadIniString(path, sect, 'COS'))
      pk1 = wlutil.LoadIniString(path, sect, 'PEAK1')
      pk2 = wlutil.LoadIniString(path, sect, 'PEAK2')
      pk3 = wlutil.LoadIniString(path, sect, 'PEAK3')
      pk4 = wlutil.LoadIniString(path, sect, 'PEAK4')
      # split pk1, 2, 3, 4
      pk_list = []
      for pk in [pk1, pk2, pk3, pk4]:
        pk_list.append([])
        pkpos_list = pk.split(',')
        for pos in pkpos_list:
          pk_list[-1].append(float(pos))
      self.resultbox.append(line, [line, nseq, seq, seq2, \
              Adiff, Bdiff, X, COS, pk_list[0], pk_list[1], \
              pk_list[2], pk_list[3]])

  def make_chespa_ini(self, path):
    # CHESPA
    wlutil.SaveIniString(path, 'OPTIONS', 'NSCALE', self.nscale.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'PERT_CUTOFF', self.ppmcut.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'REF_CUTOFF', self.ppmcut.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'IPFILTER', self.ipfilter_om.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'IPOUTLIER', self.ipppmcut.get())

    specs = ['SPEC1', 'SPEC2', 'SPEC3', 'SPEC4']
    if self.pt_mode.get() == 1:
      sps = [self.sp1.spectrum(), self.sp2.spectrum(), \
            self.sp3.spectrum(), self.sp1.spectrum()]
    else:
      sps = [self.sp1.spectrum(), self.sp2.spectrum(), \
            self.sp3.spectrum(), self.sp2.spectrum()]

    for i in range(4):
      if sps[i] == None:
        wlutil.SaveIniString(path, 'OPTIONS', specs[i], 'None')
      else:
        wlutil.SaveIniString(path, 'OPTIONS', specs[i], \
                            sps[i].name)
    wlutil.SaveIniString(path, 'OPTIONS', 'PTMODE', \
                          '%d' % (self.pt_mode.get()))
    wlutil.SaveIniString(path, 'OPTIONS', 'COUNT', \
                    '%d' % (len(self.resultbox.line_data)))

    for i in range(len(self.resultbox.line_data)):
      data = self.resultbox.line_data[i]
      sect = 'CHESPA%d' % (i+1)
      wlutil.SaveIniString(path, sect, 'LINE', data[0])
      wlutil.SaveIniString(path, sect, 'ID', '%d' % (data[1]))
      wlutil.SaveIniString(path, sect, 'SEQ', data[2])
      wlutil.SaveIniString(path, sect, 'SEQ2', data[3])
      wlutil.SaveIniString(path, sect, 'ADIFF', '%f' % (data[4]))
      wlutil.SaveIniString(path, sect, 'BDIFF', '%f' % (data[5]))
      wlutil.SaveIniString(path, sect, 'X', '%f' % (data[6]))
      wlutil.SaveIniString(path, sect, 'COS', '%f' % (data[7]))
      wlutil.SaveIniString(path, sect, 'PEAK1', '%f,%f,%f' % \
                                (data[8][0], data[8][1], data[8][2]))
      wlutil.SaveIniString(path, sect, 'PEAK2', '%f,%f,%f' % \
                                (data[9][0], data[9][1], data[9][2]))
      wlutil.SaveIniString(path, sect, 'PEAK3', '%f,%f,%f' % \
                                (data[10][0], data[10][1], data[10][2]))
      wlutil.SaveIniString(path, sect, 'PEAK4', '%f,%f,%f' % \
                                (data[11][0], data[11][1], data[11][2]))

  def plot_chespa_cb(self):
    try:
      plot_files = [self.ndp_ppm_path, self.ndp_ref_ppm_path, \
                    self.ndp_X_path, self.ndp_cos_path]
    except:
      tkMessageBox.showerror('Error', 'CHESPA job has not been run.')
      return
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')  
    for plot_file in plot_files:
      if not os.path.exists(plot_file): continue
      shutil.copyfile(plot_file, ini_path)
      if tkMessageBox.askokcancel('CHESPA plots','Do you want to plot %s' % \
                                (os.path.basename(plot_file))):
        nmrfam.run_ndpplot(self.session)
        time.sleep(3)

  # -----------------------------------------------------------------------------
  # chespa sort option
  def sort_by(self, mode): # ID, Diff, Fract. Activ., Proj.
    result_list = list(self.resultbox.line_data)
    self.resultbox.clear()
    if mode == 1:
      sort_list = sorted(result_list, key=lambda x: x[mode], \
                        reverse=False)
    else:
      sort_list = sorted(result_list, key=lambda x: abs(x[mode]), \
                        reverse=True)
    for item in sort_list:
      self.resultbox.append(item[0], item)

  def sort_ID_cb(self):
    self.sort_by(1)
  def sort_diff_cb(self):
    self.sort_by(4)
  def sort_diff2_cb(self):
    self.sort_by(5)
  def sort_X_cb(self):
    self.sort_by(6)
  def sort_cos_cb(self):
    self.sort_by(7)
  # -----------------------------------------------------------------------------    
  def select_chespa_cb(self, event):
    pymol_prefix = chescautil.pymol_prefix4
    data_list = self.resultbox.selected_line_data()
    if len(data_list) == 0: return

    content = ''
    for data in data_list:
      ress = data[1]
      sp = data[0].split()
      tmp = pymol_prefix.replace('$ID', '%d' % (ress))
      tmp2 = tmp.replace('$FA', 'X=%s' % (sp[3]))
      tmp3 = tmp2.replace('$COS', 'COS=%s' % (sp[4]))
      content = content + tmp3
    f = open(os.path.join(self.chespa_job_dir, 'p'), 'w')
    f.write(content)
    f.close()

  def chespa_center_cb(self, event):
    # also center the residue?
    data_list = self.resultbox.selected_line_data()
    if len(data_list) == 0: return
    data = data_list[0]
    s1 = self.sp1.spectrum()
    s2 = self.sp2.spectrum()
    s3 = self.sp3.spectrum()
    for v in self.session.project.view_list():
      if v.spectrum in [s1, s2, s3]:
        for p in v.spectrum.peak_list():
          if p.is_assigned == 0: continue
          asn = sputil.parse_assignment_entirely(p.assignment)
          if asn[0][1] == data[1]:
            sputil.show_peak(p)
            break
  # -----------------------------------------------------------------------------
  #
  def seq_align(self, pdb_file):
    if self.chespa_job_dir == '': return
    chespa_pdb_path = os.path.join(self.chespa_job_dir, 'chespa.pdb')
    wlutil.make_aligned_pdb(self.session, pdb_file, chespa_pdb_path)
  # -----------------------------------------------------------------------------
  #
  def pymol_cb(self):
    # launch pymol with chesca.pdb
    if self.chespa_job_dir == '': return
    chespa_pdb_path = os.path.join(self.chespa_job_dir, 'chespa.pdb')
    # ask if you want to use current pdb file?
    user_pdb_path = ''
    if os.path.exists(chespa_pdb_path):
      result = tkMessageBox.askokcancel('Stored PDB file found.', 
                        'Do you want to use the stored PDB file?')
      if result is False:
        user_pdb_path = tkFileDialog.askopenfilename(
              initialdir = self.chespa_job_dir,
              title = 'Select a PDB file for CHESPA-SPARKY analysis')
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
            initialdir = self.chespa_job_dir,
            title = 'Select a PDB file for CHESPA-SPARKY analysis')
      if os.path.exists(user_pdb_path):
        if user_pdb_path[-4:] == '.cif':
          import cif2pdb
          cif2pdb.cif2pdb(user_pdb_path, user_pdb_path[0:-3]+'pdb', HETATM=True)
          user_pdb_path = user_pdb_path[0:-3]+'pdb'
        self.seq_align(user_pdb_path)
        self.launch_pymol()
    pass

  def launch_pymol(self):
    chespa_pdb_path = os.path.join(self.chespa_job_dir, 'chespa.pdb')
    msg = 'Please update your PyMOL by typing @p in PyMOL command-line'

    cmd = "cd %s; load chespa.pdb" % (self.chespa_job_dir)
    self.session.tk.clipboard_clear()
    self.session.tk.clipboard_append(cmd)
    msg = msg + '\n Manually run PyMOL and do "%s"' % \
                (cmd)
    msg = msg + ' if PyMOL does not launch correctly. The command is in your clipboard now.'

    tkMessageBox.showinfo('Launching PyMOL...', msg)
    return nmrfam.run_pymol(self.session, chespa_pdb_path)

# -----------------------------------------------------------------------------

class chesca_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'CHESCA-SPARKY automation')
    user_name_ef, user_email_ef, user_seq_ff = \
                              wlutil.user_and_seq(self, USERINFO=False)
    # for now, invisible
    user_seq_ff.frame.pack_forget()

    # state name
    self.state_name_ef = tkutil.entry_field(self.top, 'State name: ', initial = '', width = 30)
    self.state_name_ef.frame.pack(side = 'top', anchor = 'w', expand = 0)
    self.state_name = self.state_name_ef.variable

    # spectrum list on specfrm
    specfrm = Tkinter.Frame(self.top)
    specfrm.pack(side='top', fill = 'both', expand = 1)
                            
    self.specbox = tkutil.scrolling_list(specfrm, 'Spectrum list', 7)
    self.specbox.listbox['selectmode'] = 'extended'
    self.specbox.frame.pack(side='top', fill = 'both', expand = 1)
    
    # Options
    param_frame = Tkinter.Frame(self.top, width = 600, height = 50)
    param_frame.pack(side='top', anchor='w')

    # interpeak minimum difference option
    ipfilter_frame = Tkinter.Frame(param_frame)
    ipfilter_frame.pack(side='bottom', anchor='sw', expand = 0)
    ipfilters = ['Not used', 'User', 'Avg. line width']
    # three options. 1. do not apply, 2. user defined, 3. avg. line width
    self.ipfilter_om = tkutil.option_menu(ipfilter_frame, 
                                'Inter-peak min diff: ',
                                ipfilters, initial = 'Not used')
    self.ipfilter_om.frame.pack(side = 'left', anchor = 'nw')
    self.ipfilter_om.menu.bind('<<MenuSelect>>', self.ipfilter_callback)
    # inputs for user inputs
    self.ipppmcut_ef = tkutil.entry_field(ipfilter_frame, \
        ', min diff (ppm):', initial = '0.05', width = 4)
    self.ipppmcut = self.ipppmcut_ef.variable


    # N scale
    nscale_ef = tkutil.entry_field(param_frame, 'N-to-H:', initial = '0.2', width = 4)
    nscale_ef.frame.pack(side = 'left', anchor = 'n', expand = 0)
    self.nscale = nscale_ef.variable

    # R cutoff- 0.98
    rcut_ef = tkutil.entry_field(param_frame, ', R cutoff:', initial = '0.98', width = 4)
    rcut_ef.frame.pack(side = 'left', anchor = 'n', expand = 0)
    self.rcut = rcut_ef.variable

    # R cutoff- 0.98
    rcut2_ef = tkutil.entry_field(param_frame, ', Cluster cutoff:', initial = '0.98', width = 4)
    rcut2_ef.frame.pack(side = 'left', anchor = 'n', expand = 0)
    self.rcut2 = rcut2_ef.variable

    # Hz cutoff for N and H
    outlier_n_ef = tkutil.entry_field(param_frame, ', N cutoff (Hz):', initial = '5', width = 3)
    outlier_n_ef.frame.pack(side = 'left', anchor = 'n', expand = 0)
    self.outlier_n = outlier_n_ef.variable
    outlier_h_ef = tkutil.entry_field(param_frame, ', H cutoff (Hz):', initial = '10', width = 3)
    outlier_h_ef.frame.pack(side = 'left', anchor = 'n', expand = 0)
    self.outlier_h = outlier_h_ef.variable

    ### Linewidth filtering

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    # buttons
    self.br = tkutil.button_row(self.top,
			   ('New', self.new_wrap_cb),
			   ('Add', self.add_cb),
		#	   ('Update', self.update_cb), # not really needed
			   ('Delete', self.delete_cb),
			   ('Clear', self.clear_cb),
			   ('^', self.up_cb),
			   ('v', self.down_cb),
			   ('Run', self.run_cb),
			   ('Load', self.load_states_cb),
			   ('Save', self.save_states_cb),
         ('CHESPA-SPARKY', self.open_chespa_cb),
		#	   ('Close', self.close_cb), # removed to save screen space
			   )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 0)
    tkutil.create_hint(self.br.buttons[0], 'Prepare to add a new state.')
    tkutil.create_hint(self.br.buttons[1], 'Add a state set comprised of multiple spectra. Multi-select by using CTRL key and click.')
    #tkutil.create_hint(self.br.buttons[2], 'Update selected state set with currently selected spectra.')
    tkutil.create_hint(self.br.buttons[2], 'Delete selected state set.')
    tkutil.create_hint(self.br.buttons[3], 'Clear all states.')
    tkutil.create_hint(self.br.buttons[4], 'Move selected state up.')
    tkutil.create_hint(self.br.buttons[5], 'Move selected state down.')
    tkutil.create_hint(self.br.buttons[6], 'Run a CHESCA-SPARKY job.')
    tkutil.create_hint(self.br.buttons[7], 'Load States.')
    tkutil.create_hint(self.br.buttons[8], 'Save States.')
    tkutil.create_hint(self.br.buttons[9], 'Open CHESPA-SPARKY window.')
    #tkutil.create_hint(self.br.buttons[9], 'Close this window.')
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0) 
    
    self.statebox = tkutil.scrolling_list(self.top, \
                                    'State list (ref. state at the top)', 3)
    self.statebox.listbox.bind('<ButtonRelease-1>', self.select_state_cb)
    self.statebox.listbox.bind('<ButtonRelease-3>', self.show_state_spectra_cb)
    self.statebox.frame.pack(side='top', fill = 'both', expand = 1)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0) 
    
    self.cs_label_text = Tkinter.StringVar()    
    self.cs_label_text.set("- CHESCA-SPARKY: CHESCA-SPARKY importer -")
    self.cs_label = Tkinter.Label(self.top, textvariable = self.cs_label_text, anchor = 'w', justify = 'left')		
    self.cs_label.pack(side = 'top', anchor = 'w')
    
    # token
    # User name
    token_frame = Tkinter.Frame(self.top, width = 600, height = 25)
    token_frame.pack(side='top', anchor='w')
    token_ef = tkutil.entry_field(token_frame, 'Job ID: ', initial = '', width = 20)
    token_ef.frame.pack(side = 'left', anchor = 'w', expand = 0)
    self.token = token_ef.variable        
    self.br2 = tkutil.button_row(token_frame,
        ('Check', self.check_wrap_cb),
        ('Browse...', self.chesca_browse_cb),
        )
    self.br2.frame.pack(side = 'top', anchor = 'e', expand = 0)
    tkutil.create_hint(self.br2.buttons[0], 
          'Check CHESCA-SL/CL and SVD job status and import the results.')
    tkutil.create_hint(self.br2.buttons[1], 
          'Import the results in the local machine.')

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    rfrm = Tkinter.Frame(self.top)
    rfrm.pack(side='top', fill='both', expand = 1)

    rtfrm = Tkinter.Frame(rfrm)
    rtfrm.pack(side='top', fill='both', expand = 1)

    # CHESCA, CHESCA-CL/SL or SVD ?
    self.use_mode = Tkinter.IntVar()
    self.use_mode.set(1)
    self.rb_1 = Tkinter.Radiobutton(rtfrm, text='CHESCA', variable=self.use_mode, 
              value=1, command=self.show_chesca_cb).pack(anchor='w',side='left')
    self.rb_2 = Tkinter.Radiobutton(rtfrm, text='CHESCA-SL', variable=self.use_mode, 
              value=2, command=self.show_chesca_sl_cb).pack(anchor='w',side='left')
    self.rb_3 = Tkinter.Radiobutton(rtfrm, text='CHESCA-CL', variable=self.use_mode, 
              value=3, command=self.show_chesca_cl_cb).pack(anchor='w',side='left')
    self.rb_4 = Tkinter.Radiobutton(rtfrm, text='SVD', variable=self.use_mode, 
              value=4, command=self.show_svd_cb).pack(anchor='w',side='left')

    self.resultbox = tkutil.scrolling_list(rfrm, 'CHESCA results', 3)
    self.resultbox.listbox.bind('<ButtonRelease-1>', self.select_chesca_cb)
    self.resultbox.listbox.bind('<Double-Button-1>', self.interresidue_plot_cb)
    self.resultbox.listbox['selectmode'] = 'extended'
    self.resultbox.frame.pack(side='top', fill = 'both', expand = 1)

    self.resultbox2 = tkutil.scrolling_list(rfrm, 'CHESCA-SL results', 3, xscrollbar=True)
    self.resultbox2.listbox.bind('<ButtonRelease-1>', self.select_chesca_sl_cb)
    self.resultbox2.listbox.bind('<Double-Button-1>', self.cluster_plot_cb)
    self.resultbox2.listbox['selectmode'] = 'extended'

    self.resultbox3 = tkutil.scrolling_list(rfrm, 'CHESCA-CL results', 3, xscrollbar=True)
    self.resultbox3.listbox.bind('<ButtonRelease-1>', self.select_chesca_cl_cb)
    self.resultbox3.listbox.bind('<Double-Button-1>', self.cluster_cl_plot_cb)
    self.resultbox3.listbox['selectmode'] = 'extended'

    self.resultbox4 = tkutil.scrolling_list(rfrm, 'SVD results', 3, xscrollbar=True)
    self.resultbox4.listbox.bind('<ButtonRelease-1>', self.select_svd_cb)
    self.resultbox4.listbox.bind('<Double-Button-1>', self.svd_plot_cb)
    self.resultbox4.listbox['selectmode'] = 'extended'

    self.br3 = tkutil.button_row(self.top,
        ('Sort by ID1', self.sort_ID1_cb),
        ('Sort by ID2', self.sort_ID2_cb),
        ('Sort by R', self.sort_R_cb),
        ('Sort by |R|', self.sort_absR_cb),
        ('Plot R', self.plot_chesca_cb),
        ('PyMOL', self.pymol_cb),
        )
    self.br3.frame.pack(side = 'top', anchor = 'w', expand = 0)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    self.notice_text = Tkinter.StringVar()
    self.notice_text.set("* Dbl-click to show the interresidue plot.")
    self.notice = Tkinter.Label(self.top, textvariable = self.notice_text, 
                                          anchor = 'w', justify = 'left')
    self.notice.pack(side = 'bottom', anchor = 'w')    

    # current state. None for New
    self.new_cb(1)
    self.result_mode = 1
  # -----------------------------------------------------------------------------  
  # ipfilter callback to just pack & forget self.ipppmcut_ef
  def ipfilter_callback(self, event):
    if self.ipfilter_om.get() == 'User':
      self.ipppmcut_ef.frame.pack(side = 'left', anchor = 'w', expand = 0)
    else:
      self.ipppmcut_ef.frame.forget()
  # -----------------------------------------------------------------------------  
  def open_chespa_cb(self):
    sputil.the_dialog(chespa_dialog, self.session).show_window(1)  
  # -----------------------------------------------------------------------------
  # three different CHESCA results- chesca, chesca-sl/cl, svd
  def show_chesca_cb(self):
    self.resultbox2.frame.forget()
    self.resultbox3.frame.forget()
    self.resultbox4.frame.forget()
    self.resultbox.frame.pack(side='top', fill = 'both', expand = 1)
    self.result_mode = 1
    for i in range(4):  self.br3.buttons[i]['state'] = 'active'
    self.notice_text.set("* Dbl-click to show the CHESCA interresidue plot.")
  # -----------------------------------------------------------------------------  
  def show_chesca_sl_cb(self):
    self.resultbox.frame.forget()
    self.resultbox3.frame.forget()
    self.resultbox4.frame.forget()
    self.resultbox2.frame.pack(side='top', fill = 'both', expand = 1)
    self.result_mode = 2
    for i in range(4):  self.br3.buttons[i]['state'] = 'disabled'
    self.notice_text.set("* Dbl-click to show the CHESCA-SL interresidue plot.")
  # -----------------------------------------------------------------------------  
  def show_chesca_cl_cb(self):
    self.resultbox.frame.forget()
    self.resultbox2.frame.forget()
    self.resultbox4.frame.forget()
    self.resultbox3.frame.pack(side='top', fill = 'both', expand = 1)
    self.result_mode = 3
    for i in range(4):  self.br3.buttons[i]['state'] = 'disabled'
    self.notice_text.set("* Dbl-click to show the CHESCA-CL interresidue plot.")
  # -----------------------------------------------------------------------------  
  def show_svd_cb(self):
    self.resultbox.frame.forget()
    self.resultbox2.frame.forget()
    self.resultbox3.frame.forget()
    self.resultbox4.frame.pack(side='top', fill = 'both', expand = 1)  
    self.result_mode = 4
    for i in range(4):  self.br3.buttons[i]['state'] = 'disabled'
    self.notice_text.set("* Dbl-click to show the SVD plot.")

  # -----------------------------------------------------------------------------
  # regular sort option
  def sort_by(self, mode):
    result_list = list(self.resultbox.line_data)
    self.resultbox.clear()
    if mode < 3:
      sort_list = sorted(result_list, key=lambda x: x[mode])
    else:
      sort_list = sorted(result_list, key=lambda x: x[mode], reverse=True)
    #sort_list = sorted(result_list, key=wlutil.getKey(mode))
    for item in sort_list:
      self.resultbox.append(item[0], item)

  def sort_ID1_cb(self):
    self.sort_by(1)
  
  def sort_ID2_cb(self):
    self.sort_by(2)
  
  def sort_R_cb(self):
    self.sort_by(3)

  def sort_absR_cb(self):
    self.sort_by(4)
  # -----------------------------------------------------------------------------
  # draw cluster plot
  def cluster_plot(self, data_list):
    if len(data_list) == 0: return
    full_path = data_list[0][3]
    if not os.path.exists(full_path):
      tkMessageBox.showerror('error', '%s not found' % (full_path))
      return
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    shutil.copyfile(full_path, ini_path)
    # open ndpplot
    nmrfam.run_ndpplot(self.session)
  # -----------------------------------------------------------------------------
  # draw single linkage clustering plot
  def cluster_plot_cb(self, event):
    data_list = self.resultbox2.selected_line_data()
    self.cluster_plot(data_list)
  # -----------------------------------------------------------------------------
  # draw complete linkage clustering plot
  def cluster_cl_plot_cb(self, event):
    data_list = self.resultbox3.selected_line_data()
    self.cluster_plot(data_list)
  # -----------------------------------------------------------------------------
  # draw svd ndpplot
  def svd_plot_cb(self, event):
    data_list = self.resultbox4.selected_line_data()
    if len(data_list) == 0: return
    full_path = data_list[0][3]
    if not os.path.exists(full_path):
      tkMessageBox.showerror('error', '%s not found' % (full_path))
      return
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    shutil.copyfile(full_path, ini_path)
    # open ndpplot
    nmrfam.run_ndpplot(self.session)
  # -----------------------------------------------------------------------------
  # draw R ndpplot
  def interresidue_plot_cb(self, event):
    chesca_pw_dir = os.path.join(self.chesca_job_dir, 'pairwise')
    data_list = self.resultbox.selected_line_data()
    if len(data_list) != 1: return
    data = data_list[0]
    id1 = data[1]
    id2 = data[2]
    R = data[3]
    file_path = 'ndpplot_rcmf_%d_%d.ini' % (id1, id2)
    full_path = os.path.join(chesca_pw_dir, file_path)
    if not os.path.exists(full_path):
      tkMessageBox.showerror('error', '%s not found' % (full_path))
      return
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    shutil.copyfile(full_path, ini_path)
    # open ndpplot
    nmrfam.run_ndpplot(self.session)
  # -----------------------------------------------------------------------------
  # States
  def load_chesca_ini(self, path):
    self.new_cb(1)
    self.statebox.clear()
    self.resultbox.clear()
    
    tmp = wlutil.LoadIniString(path, 'OPTIONS', 'NSCALE')
    if tmp != '': self.nscale.set(tmp)
    
    tmp = wlutil.LoadIniString(path, 'OPTIONS', 'RCUTOFF')
    if tmp != '': self.rcut.set(tmp)

    tmp = wlutil.LoadIniString(path, 'OPTIONS', 'R2CUTOFF')
    if tmp != '': self.rcut2.set(tmp)

    tmp = wlutil.LoadIniString(path, 'OPTIONS', 'NOUTLIER')
    if tmp != '': self.outlier_n.set(tmp)

    tmp = wlutil.LoadIniString(path, 'OPTIONS', 'HOUTLIER')
    if tmp != '': self.outlier_h.set(tmp)

    cutoff = wlutil.LoadIniString(path, 'OPTIONS', 'IPFILTER')
    self.ipfilter_om.set(cutoff)

    cutoff = wlutil.LoadIniString(path, 'OPTIONS', 'IPOUTLIER')
    try:
      if cutoff != '': self.ipppmcut.set(float(cutoff))
    except:
      pass 
    self.ipfilter_callback(None)

    for i in range(1, 20):
      section = 'STATE%d' % (i)
      state_name = wlutil.LoadIniString(path, section, 'NAME')
      if state_name == '': break
      spec_list = []
      for j in range(1, 10):
        key = 'SPEC%d' % (j)
        spec_name = wlutil.LoadIniString(path, section, key)
        if spec_name == '': break
        spec = wlutil.SpectrumByName(self.session, spec_name)
        spec_list.append(spec)
      line = state_name + ':['
      hz_per_ppm_list = []
      for spec in spec_list:
        line = line + spec.name + ','
        if spec.hz_per_ppm[0] < spec.hz_per_ppm[1]: # N - H
          hz_per_ppm = [spec.hz_per_ppm[0], spec.hz_per_ppm[1]]
        else:
          hz_per_ppm = [spec.hz_per_ppm[1], spec.hz_per_ppm[0]]
        hz_per_ppm_list.append(hz_per_ppm)  
      line = '%s]' % (line[:-1])
      self.statebox.append(line, [line, state_name, spec_list, hz_per_ppm_list])
    self.new_cb(1)

  def make_chesca_ini(self, path):
    wlutil.SaveIniString(path, 'OPTIONS', 'NSCALE', self.nscale.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'RCUTOFF', self.rcut.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'R2CUTOFF', self.rcut2.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'NOUTLIER', self.outlier_n.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'HOUTLIER', self.outlier_h.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'IPFILTER', self.ipfilter_om.get())
    wlutil.SaveIniString(path, 'OPTIONS', 'IPOUTLIER', self.ipppmcut.get())

    for i in range(len(self.statebox.line_data)):
      state_data = self.statebox.line_data[i]
      section = 'STATE%d' % (i+1)
      wlutil.SaveIniString(path, section, 'NAME', state_data[1])
      wlutil.SaveIniString(path, section, 'NHZPERPPM', state_data[3][0][0])
      wlutil.SaveIniString(path, section, 'HHZPERPPM', state_data[3][0][1])
      for j in range(len(state_data[2])):
        key = 'SPEC%d' % (j+1)
        wlutil.SaveIniString(path, section, key, state_data[2][j].name)

  def load_states_cb(self):
    path = tkutil.load_file(self.top, 'Load CHESCA-SPARKY states', 
                            'chesca_sparky_states')
    if path:
      try:
        self.load_chesca_ini(path)
      except:
        tkMessageBox.showinfo('Error', 'Experiment(s) listed in your ' + \
          'CHESCA-SPARKY configuration file could not be found. ' + \
          'Please open your experiment(s) first.')

  def save_states_cb(self):
    path = tkutil.save_file2(self.top, 'Save CHESCA-SPARKY states', 'chesca_sparky_states',
                            '.ini', [('CHESCA-SPARKY States', '*.ini')])
    if path:
      self.make_chesca_ini(path)

  # -----------------------------------------------------------------------------
  def highlight_chesca_sl_cl(self, data_list):
    pymol_prefix = chescautil.pymol_prefix2
    if len(data_list) == 0: return

    ress = ''
    for data in data_list:
      res_list = data[2]
      for res in res_list:
        ress = ress + '%d+' % (res)
    ress = ress[:-1]
    tmp = pymol_prefix.replace('$IDS', ress)
    content = tmp.replace('$CORR', '%.4f' % (data_list[0][1]))
    f = open(os.path.join(self.chesca_job_dir, 'p'), 'w')
    f.write(content)
    f.close()
  # -----------------------------------------------------------------------------
  # highlight selected chesca-sl results
  def select_chesca_sl_cb(self, event):
    data_list = self.resultbox2.selected_line_data()
    self.highlight_chesca_sl_cl(data_list)
  # -----------------------------------------------------------------------------
  # highlight selected chesca-cl results
  def select_chesca_cl_cb(self, event):
    data_list = self.resultbox3.selected_line_data()
    self.highlight_chesca_sl_cl(data_list)
  # -----------------------------------------------------------------------------
  # highlight selected chesca-cl results
  def select_svd_cb(self, event):
    pymol_prefix = chescautil.pymol_prefix3
    data_list = self.resultbox4.selected_line_data()
    if len(data_list) == 0: return

    ress = ''
    for data in data_list:
      res_list = data[2]
      for res in res_list:
        ress = ress + '%d+' % (res)
    ress = ress[:-1]
    tmp = pymol_prefix.replace('$IDS', ress)
    content = tmp.replace('$PC', 'PC%d%d' % \
      (data_list[0][1][2], data_list[0][1][3]))
    f = open(os.path.join(self.chesca_job_dir, 'p'), 'w')
    f.write(content)
    f.close()

  # -----------------------------------------------------------------------------
  # highlight selected chesca results
  def select_chesca_cb(self, event):
    data_list = self.resultbox.selected_line_data()
    if len(data_list) == 0: return
    if len(data_list) == 1:
      pymol_prefix = chescautil.pymol_prefix
    else:
      pymol_prefix = chescautil.pymol_multi_prefix

    content = ''  
    for data in data_list:
      id1 = data[1] # + self.seq_align_dict['dict12']
      id2 = data[2] # + self.seq_align_dict['dict12']
      R = '%f' % (data[3])
      temp = wlutil.replace_all(pymol_prefix, ['$ID1', '$ID2', '$CORR'], 
                    ['%d' % (id1), '%d' % (id2), R])
      content = content + temp
    
    f = open(os.path.join(self.chesca_job_dir, 'p'), 'w')
    f.write(content)
    f.close()

  # -----------------------------------------------------------------------------
  # highlight spectra when selecting a state    
  def show_state_spectra_cb(self, event):
    proj = self.session.project
    if proj == None:
      return
    hsqc_list = []
    for spec_box_data in self.specbox.selected_line_data():
      sp = spec_box_data[1]
      hsqc_list.append(sp)
    for vw in proj.view_list():
      if not vw.spectrum in hsqc_list: continue
      peak = sputil.closest_peak(vw.center, vw.spectrum.peak_list(), (100, 100))
      sputil.show_peak(peak)
  # -----------------------------------------------------------------------------
  # highlight spectra when selecting a state
  def select_state_cb(self, event):
    # what is selected?
    selected_data = self.statebox.selected_line_data()
    proj = self.session.project
    if len(selected_data) == 0 or proj == None:
      self.new_cb(1)
      return
    self.new_cb(0)
    data = selected_data[0]
    id = self.statebox.selected_line_numbers()[0]
    #self.statebox.listbox.selection_set(id)
    self.current_state = data
    
    # set state name
    self.state_name.set(data[1])

    # get my experiments and set highlights
    enabled_exp_list = []
    disabled_exp_list = []
    for spec in proj.spectrum_list():
      if spec in data[2]:
        enabled_exp_list.append(spec)
      else:
        disabled_exp_list.append(spec)
    idx = 0
    for spec in enabled_exp_list:
      self.specbox.append(spec.name, [spec.name, spec, idx])
      self.specbox.listbox.selection_set(idx)
      self.specbox.listbox.see(idx)
      idx = idx + 1
    for spec in disabled_exp_list:
      self.specbox.append(spec.name, [spec.name, spec, idx])        
    #self.statebox.listbox.selection_set(id) # refocus
    pass
  # -----------------------------------------------------------------------------
  def up_cb(self):
    if self.current_state == None: return
    idx = self.statebox.line_data.index(self.current_state)
    if idx == 0: return
    self.statebox.exchange(idx, idx-1)
  # -----------------------------------------------------------------------------
  def down_cb(self):
    if self.current_state == None: return
    idx = self.statebox.line_data.index(self.current_state)
    if idx == self.statebox.count()-1: return
    self.statebox.exchange(idx, idx+1)
  # -----------------------------------------------------------------------------
  def new_cb(self, mode):
    self.state_name.set('')
    self.specbox.clear()
    self.current_state = None
    #self.chesca_job_dir = ''
    self.sequence = list(map(lambda x: 'X', range(1000)))
    if mode == 1:
      self.list_spec()
    pass
  # -----------------------------------------------------------------------------
  def list_spec(self):
    proj = self.session.project
    idx = 0
    for spec in proj.spectrum_list():
      self.specbox.append(spec.name, [spec.name, spec, idx])
      idx = idx + 1
  # -----------------------------------------------------------------------------
  # new state set
  def new_wrap_cb(self):
    self.new_cb(1) # list on

  # -----------------------------------------------------------------------------
  # add a state set
  def add_cb(self):
    state_name_list = [] # all the other state names
    #hsqc_list = [] # all the other HSQCs in other states
    selected_hsqc_list = [] # newly selected HSQCs for this state
    hz_per_ppm_list = []
    for state in self.statebox.line_data:
      state_name_list.append(state[1])
    #  for hsqc in state[2]:
    #    hsqc_list.append(hsqc)
    # state name should exist and not overlap with other state names
    state_name = self.state_name.get()
    if state_name == '':
      tkMessageBox.showerror('Error', 'State name is not set.')
      return
    if state_name in state_name_list:
      tkMessageBox.showerror('Error', 'This state name is already used.')
      return
    # at least three hsqcs selected
    selected_spec_data = self.specbox.selected_line_data()
    if len(selected_spec_data) < 2:
      tkMessageBox.showerror('Error', 'At least two HSQCs should be selected.')
      return
    # selected hsqcs should not be in other states
    line = state_name + ':['
    for spec_data in selected_spec_data:
    #  if spec_data[1] in hsqc_list:
    #    tkMessageBox.showerror('Error', '%s is already being used in other state.' % (spec_data[1].name))
    #    return
      selected_hsqc_list.append(spec_data[1])
      line = line + spec_data[1].name + ','
      # we just assume all the data were colected on same magnet
      if spec_data[1].hz_per_ppm[0] < spec_data[1].hz_per_ppm[1]: # N - H
        hz_per_ppm = [spec_data[1].hz_per_ppm[0], spec_data[1].hz_per_ppm[1]]
      else:
        hz_per_ppm = [spec_data[1].hz_per_ppm[1], spec_data[1].hz_per_ppm[0]]
      hz_per_ppm_list.append(hz_per_ppm)  
    # common peaks should have been integrated - this will be checked later
    line = '%s]' % (line[:-1])
    self.statebox.append(line, [line, state_name, selected_hsqc_list, hz_per_ppm_list])
    self.new_cb(1)
    pass
  # -----------------------------------------------------------------------------
  # update a state set
  #def update_cb(self):
  #  if self.current_state == None:
  #    tkMessageBox.showerror('Error', 'No state is being selected.')
  #    return
  #  
  #  pass
  # -----------------------------------------------------------------------------
  #    
  def delete_cb(self):
    if self.current_state == None:
      tkMessageBox.showerror('Error', 'No state is being selected.')
      return
    idx = self.statebox.line_data.index(self.current_state)
    self.statebox.delete_by_number(idx)
    self.new_cb(1)
    pass
  # -----------------------------------------------------------------------------
  #    
  def clear_cb(self):
    self.statebox.clear()
    self.new_cb(1)
    pass
  # -----------------------------------------------------------------------------
  def peak_stats(self, peaks):
    if len(peaks) < 2: return None, None
    sum_n, sum_h, avg_n, avg_h, dev_n, dev_h = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    for peak in peaks:
      sum_n = sum_n + peak[0]
      sum_h = sum_h + peak[1]
    avg_n = sum_n / float(len(peaks))
    avg_h = sum_h / float(len(peaks))
    # calculate deviation
    sum_n, sum_h = 0.0, 0.0
    for peak in peaks:
      sum_n = sum_n + ((peak[0]-avg_n)**2)
      sum_h = sum_h + ((peak[1]-avg_h)**2)
    dev_n = (sum_n / float(len(peaks))) ** 0.5
    dev_h = (sum_h / float(len(peaks))) ** 0.5
    return [avg_n, avg_h], [dev_n, dev_h]

  # -----------------------------------------------------------------------------
  # actual peak handling
  def run_cb(self):
    if len(self.statebox.line_data) == 0:
      tkMessageBox.showerror('Error', 'Please define states first.')
      return
    try:
      nratio = float(self.nscale.get())
    except:
      tkMessageBox.showerror('Error', 'N-to-H ratio must be a floating value.')
      return
    try:
      rcut = float(self.rcut.get())
    except:
      tkMessageBox.showerror('Error', 'R cutoff must be a floating value between 0 and 1.')
      return
    try:
      rcut2 = float(self.rcut2.get())
    except:
      tkMessageBox.showerror('Error', 'Cluster cutoff must be a floating value between 0 and 1.')
      return  
    try:
      outlier_n = float(self.outlier_n.get())
      outlier_h = float(self.outlier_h.get())
    except:
      tkMessageBox.showerror('Error', 'N and H cutoffs must be floating values in hertz.')
      return
    # check if every state has same number of hsqcs- not necessary
    #hsqc_count = len(self.statebox.line_data[2])
    #for state_data in self.statebox.line_data:
    #  if len(state_data[2]) != hsqc_count:
    #    tkMessageBox.showerror('Error', 'The number of spectrum in %s is %d.' % (hsqc_count))
    #    return

    min_seq, max_seq = 10000, -10000

    random.seed()        
    token = time.strftime("%y%m%d_%H%M%S_") + "%06d" % random.randrange(0,1000000)        
    self.token.set(token)
    chesca_job_id = token
    chesca_dir = os.path.join(self.session.project.sparky_directory, 'CHESCA')
    chesca_job_dir = os.path.join(chesca_dir, chesca_job_id)

    chesca_pw_dir = os.path.join(chesca_job_dir, 'pairwise')
    chesca_pw_pc_dir = os.path.join(chesca_pw_dir, 'poor_corr')
    chesca_svd_dir = os.path.join(chesca_job_dir, 'svd')
    chesca_svd_mean_dir = os.path.join(chesca_job_dir, 'svd_mean')
    chesca_cl_dir = os.path.join(chesca_job_dir, 'cluster')
    chesca_path = os.path.join(chesca_job_dir, 'all_results.zip')
    chesca_ini_path = os.path.join(chesca_job_dir, 'chesca.ini')

    try:
      if not os.path.exists(chesca_dir):     os.makedirs(chesca_dir)
      if not os.path.exists(chesca_job_dir): os.makedirs(chesca_job_dir)
      if not os.path.exists(chesca_pw_dir):  os.makedirs(chesca_pw_dir)
      if not os.path.exists(chesca_pw_pc_dir):  os.makedirs(chesca_pw_pc_dir)
      if not os.path.exists(chesca_svd_dir):  os.makedirs(chesca_svd_dir)
      if not os.path.exists(chesca_svd_mean_dir):  os.makedirs(chesca_svd_mean_dir)
      if not os.path.exists(chesca_cl_dir):   os.makedirs(chesca_cl_dir)
    except:
      tkMessageBox.showerror("Error", "CHESCA directory could not be created.")
      return

    # make chesca ini file
    self.make_chesca_ini(chesca_ini_path)

    # calculate average line width
    lw_list = []
    for state in self.statebox.line_data:
      hsqc_list = state[2]
      for i in range(len(hsqc_list)):
        hsqc = hsqc_list[i]
        for peak in hsqc.peak_list():
          if peak.is_assigned != 1: continue
          if peak.line_width == None: continue
          if peak.frequency[0] > peak.frequency[1]: # N, H, scaled N order
            lw = chescautil.calc_pseudo_ppm(nratio, peak.line_width[0], \
                                    peak.line_width[1])
          else:
            lw = chescautil.calc_pseudo_ppm(nratio, peak.line_width[1], \
                                    peak.line_width[0])
          lw_list.append(lw)
    
    state_name_list = []
    for state in self.statebox.line_data:
      state_name_list.append(state[1])

    ipcut = 0 # accept all.
    if self.ipfilter_om.get() == 'User':
      try:
        ipcut = float(self.ipppmcut.get())
      except:
        tkMessageBox.showerror('Error', \
          'User defined min. inter-peak distance should be a numberic value.')
        return
    elif self.ipfilter_om.get() == 'Avg. line width':
      try:
        ipcut = sum(lw_list)/float(len(lw_list))
      except:
        tkMessageBox.showerror('Error', \
          'No integrated peak found.')
        return

    # make shift matrix first
    self.notice['text'] = 'Making a chemical shift matrix...'
    shift_list = []
    min_avg_list = list(map(lambda x: [9999, 9999], range(1000))) # make 1000 list
    max_avg_list = list(map(lambda x: [-9999, -9999], range(1000))) # make 1000 list
    for state_data in self.statebox.line_data:
      hsqc_list = state_data[2]
      hz_per_ppm_list = state_data[3]
      peak_list = list(map(lambda x: [], range(1000))) # make 1000 list
      avg_list = list(map(lambda x: [], range(1000))) # make 1000 list
      dev_list = list(map(lambda x: [], range(1000))) # make 1000 list

      shift_list.append([peak_list, avg_list, dev_list])
      hz_per_ppm = hz_per_ppm_list[0] # we should consider all collected in same magnet
      for i in range(len(hsqc_list)):
        hsqc = hsqc_list[i]
        for peak in hsqc.peak_list():
          if peak.is_assigned != 1: continue
          # parse assignment
          asgn = sputil.parse_assignment_entirely(peak.assignment)
          if asgn == None: continue # parsing failed
          seqidx = asgn[0][1]
          min_seq = min(seqidx, min_seq)
          max_seq = max(seqidx, max_seq)
          self.sequence[seqidx] = asgn[0][0]
          if peak.frequency[0] > peak.frequency[1]: # N - H order
            peak_list[seqidx].append([peak.frequency[0], peak.frequency[1]])
          else:
            peak_list[seqidx].append([peak.frequency[1], peak.frequency[0]])

      # make average and deviation
      for i in range(1000):
        avg, dev = self.peak_stats(peak_list[i])
        if avg == None: continue
        avg_list[i] = avg_list[i] + avg
        dev_list[i] = dev_list[i] + dev
        n_hz_avg, h_hz_avg = avg[0] * hz_per_ppm[0], avg[1] * hz_per_ppm[1]
        min_avg_list[i][0] = min(min_avg_list[i][0], n_hz_avg)
        max_avg_list[i][0] = max(max_avg_list[i][0], n_hz_avg)
        min_avg_list[i][1] = min(min_avg_list[i][1], h_hz_avg)
        max_avg_list[i][1] = max(max_avg_list[i][1], h_hz_avg)

    for i in range(1000):
      iUse = 1
      n_diff = max_avg_list[i][0] - min_avg_list[i][0]
      h_diff = max_avg_list[i][1] - min_avg_list[i][1]
      #f.write('%f, %f\n' % (n_diff, h_diff))
      if n_diff < outlier_n and h_diff < outlier_h: # not enough differential
        iUse = 2
      else:
        for j in range(len(self.statebox.line_data)): # check if we have all assigned peaks
          state_data = self.statebox.line_data[j]
          shift = shift_list[j]
          peak_list, avg_list, dev_list = shift
          peaks = peak_list[i]
          # this should be same as experiments
          if len(peaks) != len(state_data[2]) or len(peaks) == 0: 
            iUse = 0
            break
          
      if iUse != 1:
        for j in range(len(self.statebox.line_data)):
          shift_list[j][0][i] = [] # peak
          shift_list[j][1][i] = [] # avg
          shift_list[j][2][i] = [] # dev

    # masking by linewidth
    ipppm_mask = []
    for k in range(len(self.statebox.line_data)):
      state_data = self.statebox.line_data[k]
      shift = shift_list[k]
      peak_list, avg_list, dev_list = shift
      for i in range(min_seq, max_seq):
        if len(shift_list[0][0][i]) == 0: continue
        peaks = peak_list[i]
        for j in range(i+1, max_seq+1):
          if len(shift_list[0][0][j]) == 0: continue
          peaks2 = peak_list[j]
          for m in range(len(peaks)):
            ipdiff = chescautil.calc_pseudo_ppm_difference(nratio, 
                    [peaks[m][0], peaks[m][1]], [peaks2[m][0], peaks2[m][1]])
            if ipdiff < ipcut:
              if i not in ipppm_mask:
                ipppm_mask.append(i)
              if j not in ipppm_mask:
                ipppm_mask.append(j)
    for i in ipppm_mask:
      for j in range(len(self.statebox.line_data)):
        shift_list[j][0][i] = [] # peak
        shift_list[j][1][i] = [] # avg
        shift_list[j][2][i] = [] # dev

    """
    # make consensus assignments throughout states
    ref_peak_list = shift_list[0][0]
    wlutil.write_list('/home/whlee/shift_list.log', shift_list)
    for seqidx in range(1000):
      iUse = 1
      for shift in shift_list:
        peak_list = shift[0]
        if len(ref_peak_list[seqidx]) != len(peak_list[seqidx]) or \
            len(ref_peak_list[seqidx]) == 0:
          iUse = 0
          break
      if iUse == 0:
        for shift in shift_list:
          shift[0][seqidx] = [] # delete peaks if not agreeing
          shift[1][seqidx] = [] # delete avgs if not agreeing
          shift[2][seqidx] = [] # delete devs if not agreeing
      else:
        tkMessageBox.showinfo('survived', seqidx)"""

    # write a sequence file in case needed
    chesca_seq_path = os.path.join(chesca_job_dir, 'chesca_seq.txt')
    wlutil.write_list(chesca_seq_path, self.sequence, 'w')
    # generate M-matrix. N * nratio + H
    # rn: residue #, dm: 33.0347 33.0408 33.0253 33.0293 33.0213
    # idm: residue# 33.0347 33.0408 33.0253 33.0293 33.0213
    # dme: 0.000763953 0.00095219 0.000986576 0.000783156 0.00023094
    m_list = [] # (N*nratio+H)   X   state matrix => dm
    e_list = [] # (dN*nratio+dH) X   state matrix => dme
    n_list = [] # contains sequence indices       => rn
    nm_list = []  # ( (N-Nr)*nratio + (H-Hr)*nratio => dm for svd
    nmi_list = [] # ( (N-Nr)*nratio + (H-Hr)*nratio => dm for svd

    for seqidx in range(1000):
      if len(shift_list[0][0][seqidx]) == 0: continue
      m_col_list = list(map(lambda x: [], range(len(shift_list))))
      e_col_list = list(map(lambda x: [], range(len(shift_list))))
      # regular dm
      for i in range(len(shift_list)):
        shift = shift_list[i]
        # if nratio > 1000.0, just disregard H
        if nratio < 1000:
          m_col_list[i] = shift[1][seqidx][0] * nratio + \
                          shift[1][seqidx][1]
          e_col_list[i] = shift[2][seqidx][0] * nratio + \
                          shift[2][seqidx][1]
        else:
          m_col_list[i] = shift[1][seqidx][0]
          e_col_list[i] = shift[2][seqidx][0]
      m_list.append(m_col_list)
      e_list.append(e_col_list)
      n_list.append(seqidx)

      # for svd- external reference
      nm_col_list = list(map(lambda x: [], range(len(shift_list)-1))) # one less clm
      ref_shift = shift_list[0]
      for i in range(len(shift_list)-1):
        shift = shift_list[i+1]
        if nratio < 1000:
          nm_col_list[i] = (shift[1][seqidx][0]-ref_shift[1][seqidx][0]) * \
              nratio + (shift[1][seqidx][1]-ref_shift[1][seqidx][1])
        else:
          nm_col_list[i] = shift[1][seqidx][0]-ref_shift[1][seqidx][0]
      nm_list.append(nm_col_list)

      # for svd- internal reference
      nmi_col_list = list(map(lambda x: [], range(len(shift_list)))) # using mean
      # make reference mean
      nppm_list = []
      hppm_list = []
      for i in range(len(shift_list)):
        shift = shift_list[i]
        nppm_list.append(shift[1][seqidx][0])
        hppm_list.append(shift[1][seqidx][1])
      ref_n = sum(nppm_list) / float(len(shift_list))
      ref_h = sum(hppm_list) / float(len(shift_list))
      for i in range(len(shift_list)):
        shift = shift_list[i]
        if nratio < 1000:
          nmi_col_list[i] = (shift[1][seqidx][0]-ref_n) * nratio + \
                         (shift[1][seqidx][1]-ref_h)
        else:
          nmi_col_list[i] = (shift[1][seqidx][0]-ref_n)
      nmi_list.append(nmi_col_list)

    #wlutil.write_list('/home/whlee/m_list.log', m_list)
    # generate R-matrix: residue correlation matrix (rcm)
    # calculate R among peaks and select >= 0.98 or <= -0.98
    self.notice['text'] = "Calculating correlation coefficients..."
    r_mat = wlutil.corrmat(m_list, 1) # Pearson's R in vertical mode
    # corr_ana_e.awk does R cut off application and xmgrace plotting
    # and generates rcmf.mat (positive), rcmfn.mat (negative)
    # and rcmf_1_2.dat:   shift shift #
    # rcmf_1_2_e.dat:     shift shift dev dev
    # rcmf_pc_1_2_e.dat:  shift shift dev dev for poor correlation
    # we will make ndpplot instead of xmgrace plot files.

    rcmf_list = []
    rcmfn_list = []
    # make rcmf.mat and rcmfn.mat
    rcmf_path = os.path.join(chesca_job_dir, 'rcmf.mat')
    rcmfn_path = os.path.join(chesca_job_dir, 'rcmfn.mat')
    rcmf, rcmfn = '', ''
    for i in range(len(r_mat)):
      for j in range(len(r_mat[0])):
        line = '%-4d %-4d %f\n' % (n_list[i], n_list[j], r_mat[i][j])
        if r_mat[i][j] >= rcut:
          rcmf = rcmf + line
        elif r_mat[i][j] <= -1.0 * rcut:
          rcmfn = rcmfn + line
    f = open(rcmf_path, 'w')
    f.write(rcmf)
    f.close()
    f = open(rcmfn_path, 'w')
    f.write(rcmfn)
    f.close()
    
    # make pairwise shift files
    self.notice['text'] = 'Making pairwise pseudochemical shifts...'
    for i in range(len(r_mat)):
      x = n_list[i] # sequence number
      for j in range(len(r_mat[0])):
        y = n_list[j] # sequence number
        # 32.5557 29.4882 1
        # 32.5557 29.4882 0.00278699 0.00247232
        pw, pwe = '', ''
        for k in range(len(m_list[i])):
          pw = pw + ('%-7.4f %-7.4f %d\n' % (m_list[i][k], m_list[j][k], k+1))
          pwe = pwe + ('%-7.4f %-7.4f %f %f\n' % (m_list[i][k], \
                    m_list[j][k], e_list[i][k], e_list[i][k]))
        if r_mat[i][j] >= rcut or r_mat[i][j] <= -1.0 * rcut:
          pw_path = os.path.join(chesca_pw_dir, 'rcmf_%d_%d.dat' % (x, y))
          pwe_path = os.path.join(chesca_pw_dir, 'rcmf_%d_%d_e.dat' % (x, y))
          f = open(pwe_path, 'w')
          f.write(pwe)
          f.close()
        else:
          pw_path = os.path.join(chesca_pw_pc_dir, 'rcmf_pc_%d_%d_e.dat' % (x, y))
        f = open(pw_path, 'w')
        f.write(pw)
        f.close()
    
    # make 2D ndpplot files- in chesca_job_dir
    # 2D residue by residue plot- red (+) or blue (-)
    self.notice['text'] = 'Making CHESCA plots...'
    ndp2d_path = os.path.join(chesca_job_dir, 'ndpplot_chesca.ini')
    ndp2d_legend_path = os.path.join(chesca_job_dir, 'ndpplot_chesca_l.ini')
    self.make_ndp2d(rcmf_path, rcmfn_path, ndp2d_path, min_seq, max_seq)
    self.make_ndp2d_legend(ndp2d_legend_path)

    # make pairwise 2D ndpplot files
    # 2D shift by shift for pairwise
    self.make_ndp_pairwise2d(chesca_pw_dir, r_mat, n_list, state_name_list)

    # make idm_cls.txt for cluster 3.0. tab-delimited style (in cluster sub-dir)
    idm_cls_path = os.path.join(chesca_cl_dir, 'idm_cls.txt')
    f = open(idm_cls_path, 'w')
    f.write('id')
    for sn in state_name_list:
      f.write('\t%s' % (sn))
    #for i in range(len(state_name_list)):
    #  f.write('%s' % (sn))
    #  if i != len(state_name_list)-1: f.write('\t')
    f.write('\n')
    for i in range(len(n_list)):
      seqidx = n_list[i]
      avg_list = m_list[i]
      f.write('%d' % (seqidx))
      for avg in avg_list:
      #for j in range(len(avg_list)):
      #  avg = avg_list[j]
        f.write('\t%f'% (avg))
      #  if j != len(avg_list)-1: f.write('\t')
      f.write('\n')
    f.close()

    # cluster 3.0 replaced by PyCluster
    #
    # SVD/PCA analysis
    # make M' matrix (ndm file)
    #
    # we will make two version- 
    # 1. using the first state as antagonist- nm_list
    # 2. using the mean as reference- nmi_list

    # first state reference version
    # get the mean center first
    mc_list = list(map(lambda x: 0.0, range(len(state_name_list)-1)))
    for i in range(len(nm_list)):
      for j in range(len(nm_list[i])):
        mc_list[j] = mc_list[j] + nm_list[i][j]
    for i in range(len(mc_list)):
      mc_list[i] = mc_list[i] / float(len(nm_list)) # make center mean
      
    ndm_path = os.path.join(chesca_svd_dir, 'ndm')
    f = open(ndm_path, 'w')
    #f.write('id')
    #for sn in state_name_list[1:]:
    #  f.write('\t%s' % (sn))
    #f.write('\n')
    for i in range(len(nm_list)):
      #seqidx = n_list[i]
      #f.write('%d' % (seqidx))
      avg_list = nm_list[i]
      for j in range(len(avg_list)):
        avg = avg_list[j]
        f.write('\t%f'% (avg-mc_list[j]))
      f.write('\n')
    f.close()

    # mean reference version
    # get the mean center first
    mc_list = list(map(lambda x: 0.0, range(len(state_name_list))))
    for i in range(len(nmi_list)):
      for j in range(len(nmi_list[i])):
        mc_list[j] = mc_list[j] + nmi_list[i][j]
    for i in range(len(mc_list)):
      mc_list[i] = mc_list[i] / float(len(nmi_list)) # make center mean

    ndm_mean_path = os.path.join(chesca_svd_mean_dir, 'ndm_mean')
    f = open(ndm_mean_path, 'w')
    #f.write('id')
    #for sn in state_name_list:
    #  f.write('\t%s' % (sn))
    #f.write('\n')
    for i in range(len(nmi_list)):
      #seqidx = n_list[i]
      #f.write('%d' % (seqidx))
      avg_list = nmi_list[i]
      for j in range(len(avg_list)):
        avg = avg_list[j]
        f.write('\t%f'% (avg-mc_list[j]))
      f.write('\n')
    f.close()

    # make octave script
    svd_ndm_path = os.path.join(chesca_svd_dir, 'svd_ndm')
    f = open(svd_ndm_path, 'w')
    f.write('%% This is the OCTAVE/MATLAB script to conduct SVD analysis.\n')
    f.write('%% %s has been used as a reference column.\n' % (state_name_list[0]))
    f.write('load ndm\n[u,s,v]=svd(ndm);\nscore=u*s;\n')
    f.write('save s s\nsave score score\nsave v v\nsave svd.octave\n')
    f.close()

    svd_ndm_mean_path = os.path.join(chesca_svd_mean_dir, 'svd_ndm_mean')
    f = open(svd_ndm_mean_path, 'w')
    f.write('%% This is the OCTAVE/MATLAB script to conduct SVD analysis.\n')
    f.write('%% Internal reference (mean) has been used.\n')
    f.write('load ndm_mean\n[u,s,v]=svd(ndm_mean);\nscore=u*s;\n')
    f.write('save s s\nsave score score\nsave v v\nsave svd.octave\n')
    f.close()

    # if octave exists, auto-run
    #if wlutil.is_tool('octave') and os.name == 'posix':
    #  os.system('cd %s; octave svd_ndm' % (chesca_svd_dir))
    #  os.system('cd %s; octave svd_ndm_mean' % (chesca_svd_mean_dir))
    #else: # if not, submit to server?

    #    tkMessageBox.showinfo('CHESCA-SPARKY', 
    #            'CHESCA calculation finished. ' + \
    #            'CHESCA-CL and CHESPA jobs will be submitted.')

    # CHESCA-CL & CHESPA inputs?
    # svd_ndm, svd_ndm_mean, idm_cls.txt, ndm, ndm_mean, 
    # chesca_seq.txt, chesca.ini
    chesca_url = 'pine3.nmrfam.wisc.edu'    
    chesca_selector = '/cgi-bin/chesca_uploader.cgi'

    contents = []
    fields = [ ['nmrfamsparky_token', chesca_job_id] ]
    upload_list = [ndm_path, ndm_mean_path, svd_ndm_path, svd_ndm_mean_path,
              idm_cls_path, chesca_seq_path, chesca_ini_path]
    upload_name_list = ['ndm', 'ndm_mean', 'svd_ndm', 'svd_ndm_mean',
              'idm_cls.txt', 'chesca_seq.txt', 'chesca.ini']
    label_list = ['ndm', 'ndm_mean', 'svd_ndm', 'svd_ndm_mean',
              'idm_cls', 'chesca_seq', 'chesca_ini']
    for i in range(len(upload_list)):
      filename = upload_name_list[i]
      filepath = upload_list[i]
      lbl = label_list[i]
      f = open(filepath, 'r')
      content = f.read()
      f.close()
      contents.append( [lbl, filename, content])
      fields.append([lbl+'_file', filename])

    text = posthtml.post_multipart(chesca_url, chesca_selector, \
                                  fields, contents)
    self.notice['text'] = "* Dbl-click to show the interresidue plot."
    tkMessageBox.showinfo('CHESCA-SPARKY', 
        'CHESCA job finished. Clustering and SVD analysis jobs submitted. ' + \
        'Click Check button below to obtain the results.')

  # -----------------------------------------------------------------------------
  #   
  def make_ndp_pairwise2d(self, chesca_pw_dir, r_mat, n_list, state_name_list):
    prefix = chescautil.pairwise2d_prefix
    color_list = chescautil.pairwise2d_color_list
    nratio = float(self.nscale.get())
    if nratio >= 1000:
      prefix = prefix.replace('N-H pseudoshift','N chemical shift (ppm)')
    for i in range(len(r_mat)):
      x = n_list[i] # sequence number
      for j in range(len(r_mat[0])):
        y = n_list[j] # sequence number
        # 32.5557 29.4882 1
        pw_path = os.path.join(chesca_pw_dir, 'rcmf_%d_%d_e.dat' % (x, y))
        if not os.path.exists(pw_path): continue
        ndp_path = os.path.join(chesca_pw_dir, 'ndpplot_rcmf_%d_%d.ini' % (x, y))
        f=open(pw_path, 'r')
        lines = f.readlines()
        f.close()
        # make ndpplot
        xlbl = '%s%d' % (self.sequence[x], x)
        ylbl = '%s%d' % (self.sequence[y], y)
        prefix2 = prefix.replace('$XLABEL', xlbl)
        prefix3 = prefix2.replace('$YLABEL', ylbl)
        data_content = ''
        xmin, ymin, xmax, ymax = 10**5, 10**5, -10**5, -10**5
        datacontent, colorcontent = '', ''
        for k in range(len(lines)):
          sp = lines[k].strip().split()
          if len(sp) < 3: continue # cs1 cs2 e_cs1 e_cs2
          cs1 = float(sp[0])
          cs2 = float(sp[1])
          e_cs1 = float(sp[2])
          e_cs2 = float(sp[3])
          state = k+1 #int(sp[2])
          xmin = min(xmin, cs1)
          xmax = max(xmax, cs1)
          ymin = min(ymin, cs2)
          ymax = max(ymax, cs2)
          state_name = state_name_list[state-1]
          colorline = 'COLOR_%d=%f,%f,%f,%f,%s\n' % (k+1, cs1-0.0001, 
                    cs1+0.0001, cs2-0.0001, cs2+0.0001, color_list[k])
          dataline = 'DATA_%d=%f,%f,$ERR:%f:%f,%s[%.4f(%.4f)-%.4f(%.4f)]\n' % \
                    (k+1, cs1, cs2, e_cs1, e_cs2, state_name, cs1, e_cs1, \
                    cs2, e_cs2)
          colorcontent = colorcontent + colorline
          datacontent = datacontent + dataline

        xmin, xmax = wlutil.snapintervals(xmin, xmax, 0.1)
        ymin, ymax = wlutil.snapintervals(ymin, ymax, 0.1)
        prefix4 = prefix3.replace('$XMIN', '%f' % (xmin))
        prefix5 = prefix4.replace('$XMAX', '%f' % (xmax))
        prefix6 = prefix5.replace('$YMIN', '%f' % (ymin))
        prefix7 = prefix6.replace('$YMAX', '%f' % (ymax))
        prefix8 = prefix7.replace('$COLORCOUNT', '%d' % (len(lines)))
        prefix9 = prefix8.replace('$DATACOUNT', '%d' % (len(lines)))
        prefix10 = prefix9.replace('$COLORLIST', colorcontent)
        content = prefix10.replace('$DATALIST', datacontent)
        f = open(ndp_path, 'w')
        f.write(content)
        f.close()
  # -----------------------------------------------------------------------------
  #   
  def make_ndp2d_legend(self, ndp2d_legend_path):
    try:
      rcut = float(self.rcut.get())
    except:
      rcut = 0.98
    prefix = chescautil.legend_prefix
    lines1, clines1, lines2, clines2 = '', '' ,'', ''
    diff = (1.0-rcut) / 100.0
    for i in range(0, 101):
      if rcut < 1.0:
        lvl = int(220 - float(i) * 2.20)
      else:
        lvl = 0
      cor = rcut + diff * float(i)
      lbColor1 = '255_%d_%d' % (lvl, lvl)
      lbColor2 = '%d_%d_255' % (lvl, lvl)
      line1 = 'DATA_%d=%f,1,-1,%s,%s\n' % (i, cor, lbColor1, lbColor1)
      line2 = 'DATA_%d=%f,-1,-1,%s,%s\n' % (i, cor, lbColor2, lbColor2)
      cline1 = 'COLOR_%d=%f,%f,0,2,%s\n' % (i, cor-0.0001, cor+0.0001, lbColor1)
      cline2 = 'COLOR_%d=%f,%f,-2,0,%s\n' % (i, cor-0.0001, cor+0.0001, lbColor2)
      lines1 = lines1 + line1
      clines1 = clines1 + cline1
      lines2 = lines2 + line2
      clines2 = clines2 + cline2

    prefix2 = prefix.replace('$COLORLIST1', clines1)
    prefix3 = prefix2.replace('$DATALIST1', lines1)
    prefix4 = prefix3.replace('$COLORLIST2', clines2)
    prefix5 = prefix4.replace('$DATALIST2', lines2)
    content = prefix5.replace('$XMIN', self.rcut.get())
    f = open(ndp2d_legend_path, 'w')
    f.write(content)
    f.close()
  # -----------------------------------------------------------------------------
  #   
  def make_ndp2d(self, rcmf_path, rcmfn_path, ndp2d_path, min_seq, max_seq):
    try:
      rcut = float(self.rcut.get())
    except:
      rcut = 0.98
    f = open(rcmf_path, 'r')
    rcmf_lines = f.readlines()
    f.close()
    f = open(rcmfn_path, 'r')
    rcmfn_lines = f.readlines()
    f.close()
    data_lines = rcmf_lines + rcmfn_lines
    prefix = chescautil.ndp2d_prefix(min_seq, max_seq, min_seq, max_seq)
    
    idx = 1
    lines = ''
    clines = ''
    for data in data_lines:
      sp = data.strip().split()
      if len(sp) < 3: continue
      n1 = int(sp[0])
      n2 = int(sp[1])
      s1 = self.sequence[n1]
      s2 = self.sequence[n2]
      cor = float(sp[2])
      lbl = '%s%d-%s%d[%s]' % (s1, n1, s2, n2, sp[2])
      if rcut < 1.0:
        lvl = 220 - int((abs(cor) - rcut) / (1.0-rcut) * 220.0)
      else:
        lvl = 0

      if cor < 0:
        lbColor = '%d_%d_255' % (lvl, lvl)
      else:
        lbColor = '255_%d_%d' % (lvl, lvl)

      line = 'DATA_%d=%d,%d,%s,%s,%s\n' % (idx, n1, n2, sp[2], lbl, lbColor)
      cline = 'COLOR_%d=%f,%f,%f,%f,%s\n' % (idx, -0.1+n1, 0.1+n1, -0.1+n2, 
                                              0.1+n2, lbColor)
      idx = idx + 1
      lines = lines + line
      clines = clines + cline

    prefix2 = prefix.replace('$COLORCOUNT', '%d' % (idx-1))
    prefix3 = prefix2.replace('$DATACOUNT', '%d' % (idx-1))
    prefix4 = prefix3.replace('$COLORLIST', clines)
    content = prefix4.replace('$DATALIST', lines)
    f = open(ndp2d_path, 'w')
    f.write(content)
    f.close()
  # -----------------------------------------------------------------------------
  #    
  def check_wrap_cb(self):
    self.check_cb(1)
    pass
  # -----------------------------------------------------------------------------
  #    
  def chesca_browse_cb(self):
    self.check_cb(2)
    pass
  # -----------------------------------------------------------------------------
  #    
  def check_cb(self, clicked):

    if clicked == 2: # directory mode
      chesca_job_dir = tkFileDialog.askdirectory(
            initialdir = self.session.project.sparky_directory,
            title = 'Select a CHESCA-SPARKY output directory',
            mustexist = 1)
      if not os.path.exists(chesca_job_dir): return
      rcmf_path = os.path.join(chesca_job_dir, 'rcmf.mat')
      rcmfn_path = os.path.join(chesca_job_dir, 'rcmfn.mat')
      if not os.path.exists(rcmf_path) and not os.path.exists(rcmfn_path):
        tkMessageBox.showerror('Error', 'Not a valid CHESCA-SPARKY directory.')
        return  
      self.token.set(chesca_job_dir)
      chesca_job_id = os.path.basename(chesca_job_dir)
    else:  
      chesca_dir = os.path.join(self.session.project.sparky_directory, 'CHESCA')
      chesca_job_id = self.token.get()
      chesca_job_dir = os.path.join(chesca_dir, chesca_job_id)
    self.chesca_job_dir = chesca_job_dir

    rcmf_path = os.path.join(chesca_job_dir, 'rcmf.mat')
    rcmfn_path = os.path.join(chesca_job_dir, 'rcmfn.mat')
    chesca_pw_dir = os.path.join(chesca_job_dir, 'pairwise')
    chesca_pw_pc_dir = os.path.join(chesca_pw_dir, 'poor_corr')
    chesca_cl_dir = os.path.join(chesca_job_dir, 'cluster')
    chesca_svd_dir = os.path.join(chesca_job_dir, 'svd')
    chesca_svd_mean_dir = os.path.join(chesca_job_dir, 'svd_mean')
    chesca_seq_path = os.path.join(chesca_job_dir, 'chesca_seq.txt')
    chesca_ndpplot_path = os.path.join(chesca_job_dir, 'ndpplot_chesca.ini')
    chesca_ndpplot_l_path = os.path.join(chesca_job_dir, 'ndpplot_chesca_l.ini')
    svd_ini_path = os.path.join(chesca_job_dir, 'chesca.ini')
    try:
      self.load_chesca_ini(svd_ini_path)
    except:
      tkMessageBox.showinfo('Error', 'Experiment(s) listed in your ' + \
          'CHESCA-SPARKY configuration file could not be found. ' + \
          'Please open your experiment(s) first.')
      return

    # download saving target
    chesca_path = os.path.join(chesca_job_dir, 'all_results.zip')

    if chesca_job_id == '':
      tkMessageBox.showerror('Error', 'No job ID or result directory is set.')
      return

    # even if download mode, local version should exist
    if clicked == 1: # download mode
      if not os.path.exists(rcmf_path) and not os.path.exists(rcmfn_path):
        tkMessageBox.showerror('Error', 'Not a valid CHESCA-SPARKY directory.')
        return  
    
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    
    #if clicked == 2:
    #  chesca_root_url = 'file://%s/' % (self.token.get())
    #  chesca_result_url = chesca_root_url + 'results/'
    #chesca_package_url = chesca_result_url + 'all_results.zip'
    chesca_status_lines = ['waiting',]

    # update CHESCA listbox
    self.resultbox.clear()

    # sequence
    try:
      f = open(chesca_seq_path, 'r')
      seq = f.read()
      f.close()
      for i in range(1000):
        self.sequence[i] = seq[i]
    except:
      tkMessageBox.showerror("Error", 
        "%s can not be found or is corrupted." % (chesca_seq_path))
      return

    # positive R
    try:
      f = open(rcmf_path, 'r')
      lines = f.readlines()
      f.close()
      if len(lines) == 0:
        tkMessageBox.showerror("Error", 
          "%s is corrupted." % (rcmf_path))
        return
    except:
      tkMessageBox.showerror("Error", 
          "%s can not be found or is corrupted." % (rcmf_path))
      return

    for line in lines:
      sp = line.strip().split()
      s1 = self.sequence[int(sp[0])]
      s2 = self.sequence[int(sp[1])]
      cline = '%3s%-6s %3s%-6s %s' % (s1, sp[0], s2, sp[1], sp[2])
      self.resultbox.append(cline, 
          [cline, int(sp[0]), int(sp[1]), float(sp[2]), abs(float(sp[2]))])

    # negative R
    try:
      f = open(rcmfn_path, 'r')
      lines = f.readlines()
      f.close()
      if len(lines) == 0:
        tkMessageBox.showerror("Error", 
          "%s is corrupted." % (rcmfn_path))
        return
    except:
      tkMessageBox.showerror("Error", 
          "%s can not be found or is corrupted." % (rcmfn_path))
      return

    for line in lines:
      sp = line.strip().split()
      s1 = self.sequence[int(sp[0])]
      s2 = self.sequence[int(sp[1])]
      cline = '%3s%-6s %3s%-6s %s' % (s1, sp[0], s2, sp[1], sp[2])
      self.resultbox.append(cline, 
          [cline, int(sp[0]), int(sp[1]), float(sp[2]), abs(float(sp[2]))])

    if tkMessageBox.askokcancel('CHESCA finished',
            'Do you want to plot CHESCA covariance matrix?'):
      try:
        if not os.path.exists(chesca_ndpplot_path):
          tkMessageBox.showerror('Error',
              '%s could not be found.' % (chesca_ndpplot_path))
          return
        shutil.copyfile(chesca_ndpplot_path, ini_path)
        # open ndpplot
        nmrfam.run_ndpplot(self.session)
        time.sleep(3)
      except:
        tkMessageBox.showerror('Error',
              'NDPPLOT could not be executed.')
        return

      if tkMessageBox.askokcancel('LEGENDS','Do you want to show legends?'):
        try: # LEGENDS
          if not os.path.exists(chesca_ndpplot_l_path):
            tkMessageBox.showerror('Error',
                '%s could not be found.' % (chesca_ndpplot_l_path))
            return
          shutil.copyfile(chesca_ndpplot_l_path, ini_path)
          # open ndpplot
          nmrfam.run_ndpplot(self.session)
        except:
          tkMessageBox.showerror('Error',
                'NDPPLOT could not be executed.')
          return

    # download the stuffs
    if clicked == 1: 
      status_url = 'http://i-pine.nmrfam.wisc.edu/chesca/queue/' + \
                  chesca_job_id + '/token_status.txt'
      chesca_url = 'http://i-pine.nmrfam.wisc.edu/chesca/queue/' + \
                  chesca_job_id + '/all_results.zip'

      try:
        import urllib2
      except:
        tkMessageBox.showerror('urllib2', 
          'You do not have openssl installed or set properly.\n' + \
          'Check open this URL in your web browser: \n %s' % (chesca_url))
        return

      try:
        chesca_status = urllib2.urlopen(status_url, timeout=2)
        chesca_status_line = chesca_status.read()
        if len(chesca_status_lines) == 0:
          tkMessageBox.showerror('Error', \
              'Unknown error during retrieving data from NMRFAM. ' + \
              'Please check your inputs.')      
      except:
        tkMessageBox.showinfo('Running', \
            'It seems your job is not finished yet.')
        return      

      if chesca_status_line.find('finished') < 0:
        tkMessageBox.showerror('Calculation error', \
          'Your job failed. Please check your inputs.')
        return

      try:
        chesca_response = urllib2.urlopen(chesca_url, timeout=45)
        chesca_html = chesca_response.read()
        f = open(chesca_path, 'wb')
        f.write(chesca_html)
        f.close()

        import zipfile
        zip_ref = zipfile.ZipFile(chesca_path, 'r')
        zip_ref.extractall(chesca_job_dir)
        zip_ref.close()
      except:
        tkMessageBox.showerror("Error", 
"Check if %s exists. Try to uncompress manually and use browse button if exists." % (chesca_path))
        return

    # UPDATE CHESCA-SL/CL & SVD listbox
    # CHESCA-SL
    # CLUSTER1[0.xxxx]: #, #, #, #, #, .....
    # [cl_line, cc, res_list, cl_ndp_full_path, cl_ndp_path]
    self.resultbox2.clear()
    for i in range(1, 1000):
      cl_path = 'cluster%d' % (i)
      cl_full_path = os.path.join(chesca_cl_dir, cl_path)
      cl_ndp_path = 'ndpplot_cluster%d.ini' % (i)
      cl_ndp_full_path = os.path.join(chesca_cl_dir, cl_ndp_path)
      cl_ndp_overlay_path = 'ndpplot_overlaid_cluster%d.ini' % (i)
      cl_ndp_overlay_full_path = os.path.join(chesca_cl_dir, cl_ndp_overlay_path)

      if not os.path.exists(cl_full_path): break
      f = open(cl_full_path)
      cl_lines = f.readlines()
      f.close()
      cc = cl_lines[-1].strip().split()[-1]
      res_line = ''
      res_list = []
      for j in range(len(cl_lines)-1):
        res_line = res_line + cl_lines[j].strip().split()[-1] + ', '
        res_list.append(int(cl_lines[j].strip().split()[-1]))
      res_line = res_line[:-2]
      cl_line = '%s[%.4f]: %s' % (cl_path.upper(), float(cc), res_line)
      #content = wlutil.overlay_ndpplots(cl_ndp_full_path, chesca_ndpplot_path, 
      #                                  GENERAL='file1')
      content = wlutil.overlay_ndpplots(chesca_ndpplot_path, cl_ndp_full_path,
                                        GENERAL='file2')
      f = open(cl_ndp_overlay_full_path, 'w')
      f.write(content)
      f.close()
      self.resultbox2.append(cl_line, \
          [cl_line, float(cc), res_list, cl_ndp_overlay_full_path, cl_ndp_overlay_path])

    # complete linkage
    self.resultbox3.clear()
    for i in range(1, 1000):
      cl_path = 'cluster_cl%d' % (i)
      cl_full_path = os.path.join(chesca_cl_dir, cl_path)
      cl_ndp_path = 'ndpplot_cluster_cl%d.ini' % (i)
      cl_ndp_full_path = os.path.join(chesca_cl_dir, cl_ndp_path)
      cl_ndp_overlay_path = 'ndpplot_overlaid_cluster_cl%d.ini' % (i)
      cl_ndp_overlay_full_path = os.path.join(chesca_cl_dir, cl_ndp_overlay_path)

      if not os.path.exists(cl_full_path): break
      f = open(cl_full_path)
      cl_lines = f.readlines()
      f.close()
      cc = cl_lines[-1].strip().split()[-1]
      res_line = ''
      res_list = []
      for j in range(len(cl_lines)-1):
        res_line = res_line + cl_lines[j].strip().split()[-1] + ', '
        res_list.append(int(cl_lines[j].strip().split()[-1]))
      res_line = res_line[:-2]
      cl_line = '%s[%.4f]: %s' % (cl_path.upper(), float(cc), res_line)
      content = wlutil.overlay_ndpplots(cl_ndp_full_path, chesca_ndpplot_path, 
                                        GENERAL='file1')
      f = open(cl_ndp_overlay_full_path, 'w')
      f.write(content)
      f.close()
      self.resultbox3.append(cl_line, \
          [cl_line, float(cc), res_list, cl_ndp_overlay_full_path, cl_ndp_overlay_path])

    # SVD
    # REF STATE1, MEAN
    # SVD_REF: PC12 (std: x.xxxx, x.xxxx)
    # [svd_line, stat_list, res_list, svd_ndp_full_path, svd_ndp_path]
    self.resultbox4.clear()
    for svd_dir in [chesca_svd_dir, chesca_svd_mean_dir]:
      if svd_dir == chesca_svd_dir:
        ref_name = wlutil.LoadIniString(svd_ini_path, 'STATE1', 'NAME')
      else: ref_name = 'mean'
      for i in range(1, 9):
        for j in range(1, 9):
          svd_score_path = 'pc%d%d_score' % (i, j)
          svd_score_full_path = os.path.join(svd_dir, svd_score_path)
          svd_ndp_path = 'ndpplot_pc%d%d.ini' % (i, j)
          svd_ndp_full_path = os.path.join(svd_dir, svd_ndp_path)
          svd_stat_path = 'pc%d%d_stats' % (i, j)
          svd_stat_full_path = os.path.join(svd_dir, svd_stat_path)
          if not os.path.exists(svd_score_full_path): continue
          f = open(svd_score_full_path)
          svd_lines = f.readlines()
          f.close()
          res_line = ''
          res_list = []
          for k in range(len(svd_lines)-1):
            res_line = res_line + svd_lines[k].strip().split()[-1] + ', '
            res_list.append(int(svd_lines[k].strip().split()[-1]))
          res_line = res_line[:-2]
          f = open(svd_stat_full_path)
          stat_lines = f.readlines()
          f.close()
          x_avg = float(stat_lines[0].strip().split()[0])
          x_dev = float(stat_lines[0].strip().split()[1])
          y_avg = float(stat_lines[1].strip().split()[0])
          y_dev = float(stat_lines[1].strip().split()[1])
          svd_line = 'SVD_%s: PC%d%d (std: %.4f, %.4f)- %s' \
            % (ref_name, i, j, x_dev, y_dev, res_line)
          self.resultbox4.append(svd_line, \
                    [svd_line, [x_dev, y_dev, i, j], \
                    res_list, svd_ndp_full_path, svd_ndp_path])
          
    # if this was web crawling, ask a user if different name preferred.
    if clicked == 1:
      if tkMessageBox.askokcancel('Rename directory', 
          'Do you want to rename CHESCA-SPARKY results directory?'):
        new_dir = tkSimpleDialog.askstring('New directory',
            'Please type preferred directory name.', 
            initialvalue = chesca_job_id)
        if new_dir == None or new_dir == '':
          return
        if new_dir.strip() != '':
          new_path = os.path.join(chesca_dir, new_dir)
          if new_path != chesca_job_dir:
            try:
              wlutil.copyanything(chesca_job_dir, new_path)
            except:
              tkMessageBox.showerror('Error', 'Already existing directory.')
              return
            self.token.set(new_dir)
            self.chesca_job_dir = new_path

  # -----------------------------------------------------------------------------          
  def plot_chesca_cb(self):
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    chesca_ndpplot_path = os.path.join(self.chesca_job_dir, 'ndpplot_chesca.ini')
    chesca_ndpplot_l_path = os.path.join(self.chesca_job_dir, 'ndpplot_chesca_l.ini')
    if not os.path.exists(chesca_ndpplot_path):
      tkMessageBox.showerror('Error',
          '%s could not be found.' % (chesca_ndpplot_path))
      return
    try:
      shutil.copyfile(chesca_ndpplot_path, ini_path)
      # open ndpplot
      nmrfam.run_ndpplot(self.session)
      time.sleep(3)
    except:
      tkMessageBox.showerror('Error',
            'NDPPLOT could not be executed.')
      return
    if tkMessageBox.askokcancel('LEGENDS','Do you want to show legends?'):
      try: # LEGENDS
        if not os.path.exists(chesca_ndpplot_l_path):
          tkMessageBox.showerror('Error',
              '%s could not be found.' % (chesca_ndpplot_l_path))
          return
        shutil.copyfile(chesca_ndpplot_l_path, ini_path)
        # open ndpplot
        nmrfam.run_ndpplot(self.session)
      except:
        tkMessageBox.showerror('Error',
              'NDPPLOT could not be executed.')
        return
  # -----------------------------------------------------------------------------
  #
  def seq_align(self, pdb_file):
    if self.chesca_job_dir == '': return
    chesca_pdb_path = os.path.join(self.chesca_job_dir, 'chesca.pdb')
    wlutil.make_aligned_pdb(self.session, pdb_file, chesca_pdb_path)

  # -----------------------------------------------------------------------------
  #
  def pymol_cb(self):
    # launch pymol with chesca.pdb
    if self.chesca_job_dir == '': return
    chesca_pdb_path = os.path.join(self.chesca_job_dir, 'chesca.pdb')
    # ask if you want to use current pdb file?
    user_pdb_path = ''
    if os.path.exists(chesca_pdb_path):
      result = tkMessageBox.askokcancel('Stored PDB file found.', 
                        'Do you want to use the stored PDB file?')
      if result is False:
        user_pdb_path = tkFileDialog.askopenfilename(
              initialdir = self.chesca_job_dir,
              title = 'Select a PDB file for CHESCA-SPARKY analysis')
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
            initialdir = self.chesca_job_dir,
            title = 'Select a PDB file for CHESCA-SPARKY analysis')
      if os.path.exists(user_pdb_path):
        if user_pdb_path[-4:] == '.cif':
          import cif2pdb
          cif2pdb.cif2pdb(user_pdb_path, user_pdb_path[0:-3]+'pdb', HETATM=True)
          user_pdb_path = user_pdb_path[0:-3]+'pdb'
        self.seq_align(user_pdb_path)
        self.launch_pymol()
    pass

  def launch_pymol(self):
    chesca_pdb_path = os.path.join(self.chesca_job_dir, 'chesca.pdb')
    msg = 'Please update your PyMOL by typing @p in PyMOL command-line'

    cmd = "cd %s; load chesca.pdb" % (self.chesca_job_dir)
    self.session.tk.clipboard_clear()
    self.session.tk.clipboard_append(cmd)
    msg = msg + '\n Manually run PyMOL and do "%s"' % (cmd)
    msg = msg + \
      ' if PyMOL does not launch correctly. The command is in your clipboard.'

    tkMessageBox.showinfo('Launching PyMOL...', msg)

    return nmrfam.run_pymol(self.session, chesca_pdb_path)
# -----------------------------------------------------------------------------
#
def show_chesca_dialog(session):
  sputil.the_dialog(chesca_dialog, session).show_window(1)    
def show_chespa_dialog(session):
  sputil.the_dialog(chespa_dialog, session).show_window(1)
