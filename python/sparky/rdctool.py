# -----------------------------------------------------------------------------
# RDC-SPARKY tool
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: woonghee.lee AT ucdenver.edu
# Department of Chemistry, University of Colorado at Denver
#
# Last updated: Oct. 11, 2020
# 
# Usage:
#
# Note:
#        FIT HEIGHT WILL BE USED IF A PEAK IS INTEGRATED.
# 
# 
# -----------------------------------------------------------------------------
#
import Tkinter
import sparky
import sputil
import tkutil
import tkMessageBox
import math
import myseq
import os
# -----------------------------------------------------------------------------
#
class show_rdctool_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'RDC-SPARKY')

    self.session = session

    # Sequence file    
    user_seq_ff = tkutil.file_field2(self.top, 'Sequence file: ', '', \
            file_type=[ ('3-letter-code sequence file with indices', '.seq'), \
                    ('1-letter-code sequence file', '.fasta'), \
                    ('3-letter-code sequence file without indices', '.txt')], \
                    default_ext='.seq', width = 30)
    user_seq_ff.frame.pack(side = 'top', anchor = 'w')
    self.user_seq = user_seq_ff.variable
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    
    # check if file exists
    if session.project != None:
      if session.project.sparky_directory != '' and \
                    os.path.exists(session.project.save_path):
        seq_path = session.project.save_path + '.seq'
        if os.path.exists(seq_path):
          user_seq_ff.variable.set(seq_path)

    # IPAP or ARTSY or coupled?
    opt_root = Tkinter.Frame(self.top, height=20, bd=0)
    opt_root.pack(fill="both", padx=0,pady=0, side = 'top', expand = 0)
    self.pp_mode = Tkinter.IntVar()
    self.pp_mode.set(1)
    
    Tkinter.Radiobutton(opt_root, text="", variable=self.pp_mode, value=1, \
                      command=self.artsyset_cb).pack(anchor='w',side='left')
    Tkinter.Button(opt_root, text="ARTSY", \
                      command=self.artsy_cb).pack(anchor='w',side='left')
    Tkinter.Radiobutton(opt_root, text="", variable=self.pp_mode, value=2, \
                      command=self.ipapset_cb).pack(anchor='w',side='left')
    Tkinter.Button(opt_root, text="IPAP", \
                      command=self.ipap_cb).pack(anchor='w',side='left')
    Tkinter.Radiobutton(opt_root, text="", variable=self.pp_mode, value=3, \
                      command=self.coupledset_cb).pack(anchor='w',side='left')
    Tkinter.Button(opt_root, text="COUPLED", \
                      command=self.coupled_cb).pack(anchor='w',side='left')
    
    self.opt_root = opt_root
    
    self.JInput = tkutil.entry_field(opt_root, 'J coupling (Hz): ', '92.0', 5)
    self.JInput.frame.pack(anchor='e', side = 'right', \
                            fill = 'both', expand = 0)
    self.Jcoupling = self.JInput.variable
    
    self.DelayInput = tkutil.entry_field(opt_root, 'Delay (ms): ', '10.7', 5)
    self.DelayInput.frame.pack(anchor='e', side = 'right', \
                            fill = 'both', expand = 0)
    self.delay_time = self.DelayInput.variable
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    # spectrum list
    aniso_root = Tkinter.Frame(self.top, bd=0)
    aniso_root.pack(fill="both", padx=0,pady=0, side = 'top', expand = 0)
    self.aniso_root = aniso_root
    self.sp = sputil.spectrum_menu(session, aniso_root, 'Upfield anisotropic: ')
    self.sp.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp_ = sputil.spectrum_menu(session, aniso_root, \
                                'Downfield anisotropic: ', allow_no_choice = 1)
    self.sp_.frame.pack(side = 'top', fill = 'both', expand = 0)
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    iso_root = Tkinter.Frame(self.top, bd=0)
    iso_root.pack(fill="both", padx=0,pady=0, side = 'top', expand = 0)
    self.iso_root = iso_root
    self.sp2 = sputil.spectrum_menu(session, iso_root, 'Upfield isotropic: ')
    self.sp2.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp2_ = sputil.spectrum_menu(session, iso_root, \
                                'Downfield isotropic: ', allow_no_choice = 1)
    self.sp2_.frame.pack(side = 'top', fill = 'both', expand = 0)
        
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    # buttons
    self.br = tkutil.button_row(self.top,
          ('Analyze', self.analyze_cb),
          ('Set error', self.error_cb),
          ('Delete', self.delete_cb),
          ('Plot...', self.plot_cb),
          ('Close', self.close_cb),
          )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 0)
    
    self.br2 = tkutil.button_row(self.top,
          ('Export (PONDEROSA/CYANA)', self.export_pc_cb),
          ('Export (XPLOR/CNS)', self.export_xc_cb),
          ('Export (CSV)', self.export_csv_cb),
          )
    self.br2.frame.pack(side = 'top', fill = 'both', expand = 0)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    # scroll_list
    self.listbox = tkutil.scrolling_list(self.top, 'RDC Data', 10)
    self.listbox.frame.pack(side = 'top', fill = 'both', expand = 1)
    self.listbox.listbox.bind('<Double-Button-1>', self.move_cb)
    
    self.readSeq = None
    self.artsyset_cb()
  # ----------------------------------------------------------------------------
  #  
  def forgetall(self):
    self.sp.frame.pack_forget()
    self.sp2.frame.pack_forget()
    self.sp_.frame.pack_forget()
    self.sp2_.frame.pack_forget()
  # ----------------------------------------------------------------------------
  #  
  def artsyset_cb(self):
    #self.JInput.frame.pack(anchor='e', side = 'right', \
    #                      fill = 'both', expand = 0)
    self.JInput.frame.pack_forget()    
    self.DelayInput.frame.pack(anchor='e', side = 'right', \
                          fill = 'both', expand = 0)
    self.forgetall()
    self.sp.label['text'] = 'Attenuated anisotropic: '
    self.sp_.label['text'] = 'Reference anisotropic: '
    self.sp2.label['text'] = 'Attenuated isotropic: '
    self.sp2_.label['text'] = 'Reference isotropic: '
    self.sp.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp2.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp_.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp2_.frame.pack(side = 'top', fill = 'both', expand = 0)


  def ipapset_cb(self):
    self.JInput.frame.pack_forget()
    self.DelayInput.frame.pack_forget()
    self.forgetall()
    self.sp.label['text'] = 'Upfield anisotropic: '
    self.sp_.label['text'] = 'Downfield anisotropic: '
    self.sp2.label['text'] = 'Upfield isotropic: '
    self.sp2_.label['text'] = 'Downfield isotropic: '
    self.sp.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp_.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp2.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp2_.frame.pack(side = 'top', fill = 'both', expand = 0)
    
  def coupledset_cb(self):
    self.JInput.frame.pack_forget()
    self.DelayInput.frame.pack_forget()
    self.forgetall()
    self.sp.label['text'] = 'Coupled anisotropic: '
    self.sp2.label['text'] = 'Coupled isotropic: '
    self.sp.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.sp2.frame.pack(side = 'top', fill = 'both', expand = 0)
  # ----------------------------------------------------------------------------
  # Show paper web pages
  def artsy_cb(self):
    import webbrowser
    webbrowser.open('https://www.ncbi.nlm.nih.gov/pubmed/20694505')
    
  def ipap_cb(self):
    import webbrowser
    webbrowser.open('https://www.ncbi.nlm.nih.gov/pubmed/9571116')
    
  def coupled_cb(self):
    import webbrowser
    webbrowser.open('https://doi.org/10.1016/0022-2364(87)90102-8')
  # ----------------------------------------------------------------------------
  #  
  def get_peaks(self, spec, spec_, seqidx):
    peaks = list(spec.peak_list())
    if self.pp_mode.get() == 2 or self.pp_mode.get() == 3:
      peaks_ = spec_.peak_list()
      for peak in peaks_:
        peaks.append(peak)
    ga_list = []
    re_list = []
    for peak in peaks:
      if peak.is_assigned != 1: continue
      gas = sputil.parse_assignment(peak.assignment)
      gn1 = sputil.parse_group_name(gas[0][0])
      if gn1[1] != seqidx: continue
      iFound = 0
      for ga in ga_list:
        if ga[0] == peak.assignment:
          iFound = 1
          ga[1].append(peak)
          break
      if iFound == 0:
        ga_list.append([peak.assignment, [peak,]])
      
    # check if two in IPAP case 
    if self.pp_mode.get() == 2 or self.pp_mode.get() == 3:
      for ga in ga_list:
        if len(ga[1]) != 2: continue
        # non H
        fga1 = []
        fga2 = []
        for i in range(len(spec.hz_per_ppm)):
          fga1.append(ga[1][0].frequency[i] * spec.hz_per_ppm[i])
          fga2.append(ga[1][1].frequency[i] * spec.hz_per_ppm[i])
        frq1 = max(fga1)
        frq2 = max(fga2)
        # if pulse sequence using one spectrum (coupled)
        if self.pp_mode.get() == 3:
          if ga[1][0].data_height > ga[1][1].data_height: 
            rdc_data = [ga[0], frq1-frq2, ga[1][0], frq1, ga[1][1], frq2]
          else: 
            rdc_data = [ga[0], frq2-frq1, ga[1][1], frq2, ga[1][0], frq1]
        else:
            rdc_data = [ga[0], frq1-frq2, ga[1][0], frq1, ga[1][1], frq2]
        re_list.append(rdc_data)
    else: # ARTSY
      for ga in ga_list:
        if len(ga[1]) != 1: continue
        # find counterpart if spec_ is not null.
        ref_peaks = spec_.peak_list()
        for i in range(len(ref_peaks)):
          rp = ref_peaks[i]
          if rp.is_assigned != 1: continue
          if ga[0] == rp.assignment:
            re_list.append([ga[0], [ga[1][0], rp]])
            break
    return re_list
  # ----------------------------------------------------------------------------
  #  
  def calc_rdc(self, seqidx, rdc_spec, ref_spec, rdc_spec_, ref_spec_):
    rdc_peaks = self.get_peaks(rdc_spec, rdc_spec_, seqidx)
    ref_peaks = self.get_peaks(ref_spec, ref_spec_, seqidx)
    
    if len(rdc_peaks) != len(ref_peaks) or len(rdc_peaks) == 0:
      return []
    rdc_list = []
    temp_list = []
    temp_list2 = []
    if self.pp_mode.get() == 2 or self.pp_mode.get() == 3: # IPAP or coupled
      for i in range(len(rdc_peaks)):
        rdc = rdc_peaks[i] # we should same thing in ref_peaks
        ref = None
        for j in range(len(ref_peaks)):
          if rdc[0] == ref_peaks[j][0]:
            ref = ref_peaks[j]
            break
        if ref != None:
          rdc_data = [rdc[0], rdc[1]-ref[1], 1.00, rdc[2]]
          rdc_list.append(rdc_data)
    elif self.pp_mode.get() == 1: # ARTSY
    
      # Anisotropic
      for i in range(len(rdc_peaks)):
        rdc = rdc_peaks[i] # we should do same thing in ref_peaks
        # rdc[0] assignment label
        # rdc[1][0] attenuated
        # rdc[1][1] reference

        # If integrated, fit height will be used.
        ph0 = rdc[1][0].data_height
        ph1 = rdc[1][1].data_height
        if rdc[1][0].fit_height != None: ph0 = rdc[1][0].fit_height
        if rdc[1][1].fit_height != None: ph1 = rdc[1][1].fit_height
        
        if ph1 == 0: continue
        R = ph0 / ph1 # intensity ratio
        if abs(R) > 1: continue
        bdt = self.dt / 1000.0 # millisecond to second
        fnoise = rdc_spec.noise / abs(ph1) # 1 / SNR
        #dnh = (-1.0/bdt) + float(self.Jcoupling.get()) + \
        #      (2.0 / (math.pi * bdt)) * math.asin(R/2.0)
        dnh = (-1.0/bdt) + (2.0 / (math.pi * bdt)) * math.asin(R/2.0)
        err_ratio = (1.0 + R*R)/(4.0 - R*R)
        err = 2.0*fnoise/math.pi/bdt*math.sqrt(err_ratio)
        rdc_data = [rdc[0], dnh, err, rdc[1]]
        temp_list.append(rdc_data)
          
      # Isotropic
      for i in range(len(ref_peaks)):
        rdc = ref_peaks[i] # we should do same thing in ref_peaks
        # If integrated, fit height will be used.
        ph0 = rdc[1][0].data_height
        ph1 = rdc[1][1].data_height
        if rdc[1][0].fit_height != None: ph0 = rdc[1][0].fit_height
        if rdc[1][1].fit_height != None: ph1 = rdc[1][1].fit_height
        
        if ph1 == 0: continue
        R = ph0 / ph1 # intensity ratio
        if abs(R) > 1: continue
        bdt = self.dt / 1000.0 # millisecond to second
        fnoise = rdc_spec.noise / abs(ph1) # 1 / SNR

        #dnh = (-1.0/bdt) + float(self.Jcoupling.get()) + \
        #      (2.0 / (math.pi * bdt)) * math.asin(R/2.0)
        dnh = (-1.0/bdt) + (2.0 / (math.pi * bdt)) * math.asin(R/2.0)
        err_ratio = (1.0 + R*R)/(4.0 - R*R)
        err = 2.0*fnoise/math.pi/bdt*math.sqrt(err_ratio)
        rdc_data = [rdc[0], dnh, err, rdc[1]]
        temp_list2.append(rdc_data)

      # Subtract
      for i in range(1000):
        anisotropic = None
        isotropic = None
        # check anisotropic
        for j in range(len(temp_list)):
          rdc_data = temp_list[j]
          gas = sputil.parse_assignment(rdc_data[0])
          gn1 = sputil.parse_group_name(gas[0][0])
          if gn1[1] != i: continue
          anisotropic = rdc_data
          break
        # check isotropic
        for j in range(len(temp_list2)):
          rdc_data = temp_list2[j]
          gas = sputil.parse_assignment(rdc_data[0])
          gn1 = sputil.parse_group_name(gas[0][0])
          if gn1[1] != i: continue
          isotropic = rdc_data
          break
        if anisotropic == None or isotropic == None: continue
        r_data = [anisotropic[0], anisotropic[1] - isotropic[1], \
                    anisotropic[2], anisotropic[3][0]]
        rdc_list.append(r_data)
    return rdc_list
  # -----------------------------------------------------------------------------
  #  
  def analyze_cb(self):
    # do I have two spectra?
    rdc_spec = self.sp.spectrum()      # ANISO
    rdc_spec_ = self.sp_.spectrum()    # ANISO
    ref_spec = self.sp2.spectrum()     # ISO
    ref_spec_ = self.sp2_.spectrum()   # ISO
    
    if rdc_spec == None or ref_spec == None:
      tkMessageBox.showerror('RDC setting error', 'Spectra are not set.')
      return
  
    # sequence
    if not os.path.exists(self.user_seq.get()):
      tkMessageBox.showerror('Sequence error', self.msg)
      return
    readSeq = myseq.ReadSequenceFromFile(self.user_seq.get())
    self.readSeq = readSeq
     
    # delay time
    try:
      self.dt = float(self.delay_time.get())
    except:
      tkMessageBox.showerror('Delay time error', 'Delay time is not correct')
      return
    
    # loop and calculate RDCs
    self.listbox.clear()
    hdr = 'NUM1  SEQ1  ATOM1 NUM2  SEQ2  ATOM2     RDC   ERROR'
    self.listbox.append(hdr, [hdr,hdr])
    for seqidx, seq in readSeq:
      rdcs = self.calc_rdc(seqidx, rdc_spec, ref_spec, rdc_spec_, ref_spec_)
      for rdc in rdcs:
        gas = sputil.parse_assignment(rdc[0])
        #tkMessageBox.showinfo('gas', gas)
        gn1 = sputil.parse_group_name(gas[0][0])
        gn2 = sputil.parse_group_name(gas[1][0])
        line = '%-5d %-5s %-5s %-5d %-5s %-5s %7.3f %7.3f' % (gn1[1], gn1[0],
          gas[0][1], gn2[1], gn2[0], gas[1][1], rdc[1], rdc[2])
        self.listbox.append(line, [line, rdc])

  # -----------------------------------------------------------------------------
  #  
  def error_cb(self):
    import tkSimpleDialog
    user_error = tkSimpleDialog.askstring('Uniform error', \
                              'Please type the error.', initialvalue = '1.00')
    try:
      err = float(user_error)
    except:
      return
    new_data = list(self.listbox.line_data)
    self.listbox.clear()
    for i in range(len(new_data)):
      if i == 0: 
        self.listbox.append(new_data[i][0], new_data[i])
        continue
      slist = new_data[i][0].split()
      slist[-1] = '%.3f' % (err)
      line = '%-5s %-5s %-5s %-5s %-5s %-5s %7s %7s' % (slist[0], slist[1],
            slist[2], slist[3], slist[4], slist[5], slist[6], slist[7])
      self.listbox.append(line, [line, new_data[i][1]])
    
  # -----------------------------------------------------------------------------
  #  'ponderosa', 'xplor', 'csv'
  def export_rdc(self, rdc_file, rdc_type):
    if self.readSeq == None: return
    # max sequence number
    max_seq = self.readSeq[-1][0]
    min_seq = self.readSeq[0][0]
    ori = max_seq + 10

    # max RDC ?
    max_rdc = 0
    for i in range(len(self.listbox.line_data)):
      if i == 0: continue
      slist = self.listbox.line_data[i][0].split()
      max_rdc = max(abs(float(slist[6])), max_rdc)

    # header
    wrt_list = []
    if rdc_type == 'ponderosa':
      wrt_list.append('#Orientation Magnitude Rhombicity ORI residue number')
      wrt_list.append(' 1           999       999        %d' % (ori))
      wrt_list.append('# First atom Second atom  RDC Error Weight Orientation')
    elif rdc_type == 'csv':
      wrt_list.append('NUM1,SEQ1,ATOM1,NUM2,SEQ2,ATOM2,RDC,ERROR')
    elif rdc_type == 'ndpplot':
      wrt_list.append('[GENERAL_START]')
      wrt_list.append('TITLE=RDC Plot')
      wrt_list.append('XLABEL=Residue number')
      wrt_list.append('YLABEL=RDC (Hz)')
      wrt_list.append('XMIN=%d' % (min_seq))
      wrt_list.append('XMAX=%d' % (max_seq))
      wrt_list.append('YMIN=%f' % (max_rdc * -1.0))
      wrt_list.append('YMAX=%f' % (max_rdc))
      wrt_list.append('XSCALE=INT')
      wrt_list.append('[GENERAL_END]')
      wrt_list.append('[SERIES1_START]')
      wrt_list.append('NAME=RDC Plot')
      wrt_list.append('PLOTTYPE=DOT')
      wrt_list.append('COLORCOUNT=1')
      wrt_list.append('DATACOUNT=%d' % (len(self.listbox.line_data)-1))
      wrt_list.append('COLOR_1=%d,%d,%f,%f,NAVY' % (min_seq, max_seq, 
                                                      max_rdc * -1.0, max_rdc))
    # data
    for i in range(len(self.listbox.line_data)):
      if i == 0: continue
      sl = self.listbox.line_data[i][0].split()
      if rdc_type == 'ponderosa':
        aaa1 = myseq.a2aaa(sl[1])
        aaa2 = myseq.a2aaa(sl[4])
        line = '%3s %3s %3s %3s %3s %3s %7s %7s 1.00 1' % (sl[0], aaa1, sl[2], 
                                              sl[3], aaa2, sl[5], sl[6], sl[7])
      elif rdc_type == 'xplor':
        if sl[2] == 'H': sl[2] = 'HN'
        if sl[5] == 'H': sl[5] = 'HN'
        line = """assign ( resid  %3d and name OO   )
       ( resid  %3d and name Z    )
       ( resid  %3d and name X    )
       ( resid  %3d and name Y    )
       ( resid  %3s and name %-3s  )
       ( resid  %3s and name %-3s  )  %7s  %7s
""" % (ori, ori, ori, ori, sl[0], sl[2], sl[3], sl[5], sl[6], sl[7])

      elif rdc_type == 'csv':
        line = '%s,%s,%s,%s,%s,%s,%s,%s' % (sl[0], sl[1], sl[2], sl[3], sl[4],
                                          sl[5], sl[6], sl[7])
      elif rdc_type == 'ndpplot':
        line = 'DATA_%d=%s,%s,0,%s%s%s-%s%s%s' % (i, sl[0], sl[6], sl[1], sl[0],
                                                  sl[2], sl[4], sl[3], sl[5])
      wrt_list.append(line)
        
    # closure
    if rdc_type == 'ndpplot':
      wrt_list.append('[SERIES1_END]')
    # write a file
    f = open(rdc_file, 'w')
    for line in wrt_list:
      f.write(line+'\n')
    f.close()
    
  # ----------------------------------------------------------------------------
  #  
  def plot_cb(self):
    if self.readSeq == None: return
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    self.export_rdc(ini_path,'ndpplot')
    if os.path.exists(ini_path):
      import nmrfam
      nmrfam.run_npdplot(self.session)
  # ----------------------------------------------------------------------------
  #  
  def export_pc_cb(self):
    if self.readSeq == None: return
    path = tkutil.save_file(self.session.tk, "Export RDC (PONDEROSA/CYANA)", \
                                              "export_rdc")
    if not path: return
    self.export_rdc(path, 'ponderosa')
  # ----------------------------------------------------------------------------
  #  
  def export_xc_cb(self):
    if self.readSeq == None: return
    path = tkutil.save_file(self.session.tk, "Export RDC (XPLOR/CNS)", \
                                              "export_rdc")
    if not path: return
    self.export_rdc(path, 'xplor')
  # ----------------------------------------------------------------------------
  #  
  def export_csv_cb(self):
    if self.readSeq == None: return
    path = tkutil.save_file(self.session.tk, "Export RDC (CSV)", "export_rdc")
    if not path: return
    self.export_rdc(path, 'csv')
  # ----------------------------------------------------------------------------
  #  
  def delete_cb(self):
    if self.listbox.selected_line_data() == None: return
    sel_nums = self.listbox.selected_line_numbers()
    sel_nums.sort()
    sel_nums.reverse()
    for line_number in sel_nums:
      if line_number == 0: continue # not header
      # delete from listbox
      del self.listbox.line_data[line_number]
      self.listbox.listbox.delete(line_number)

  # ----------------------------------------------------------------------------
  # move to the place
  def move_cb(self, *args):
    # get assignment from spec
    # center it.
    ds = self.listbox.selected_line_data()
    if len(ds) != 1:
      return
    if len(ds[0][1]) < 3: return
    sputil.show_peak(ds[0][1][3])
    
def show_rdc_dialog(session):
  sputil.the_dialog(show_rdctool_dialog,session).show_window(1)
