# -----------------------------------------------------------------------------
# Dialog for visual amino acid prediction and assignment
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Sep 30, 2019
# 
# Usage:
#
#    1. Select reference view to use
#    2. Select peaks
#    3. Click predict
# 
# -----------------------------------------------------------------------------

import myseq
import atomnames
import shiftstats
import sputil
import tkutil
import itertools
import Tkinter
import os.path
import tkMessageBox

# Sequence order: ARDNCEQGHILKMFPSTWYV
# count is from PACSY DB as of Feb 2018
count_list=[39726, 27240, 31228, 22498, 12179, 41361, 22897, 42432, 14146, 
  28732, 46960, 39176, 12753, 19909, 23522, 38329, 29719, 6740, 17291, 36953]
#avg_pacsy = 27689.55
avg_pacsy = sum(count_list)

dilute_factor = 2.
sequence_factor = 0.2

# Make this frequency-based initial probabilities do not influence too much.
# Because we will also use user-sequence information as well.

# reduce effect by dilute factor
for i in range(20): count_list[i] = count_list[i] + dilute_factor * avg_pacsy 
avg_pacsy = sum(count_list)

weight_list=[]
for count in count_list: weight_list.append(float(count)/avg_pacsy)
aaa_3 = "ALA ARG ASP ASN CYS GLU GLN GLY HIS ILE LEU LYS MET PHE PRO SER " + \
        "THR TRP TYR VAL"
singlea = "ARDNCEQGHILKMFPSTWYV"
aaa_list = aaa_3.split()

def valid_frequency(aa, atm, freq):
  ast = shiftstats.atom_statistics(aa, atm)
  if freq < ast.minimum_shift or freq > ast.maximum_shift: 
    return 0
  return 1
# -----------------------------------------------------------------------------
class aa_predict_dialog(tkutil.Dialog, tkutil.Stoppable):
  # ---------------------------------------------------------------------------
  #
  def __init__(self, session):
    # Initialize variables
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'Versatile Assigner')
    
    top_frame = Tkinter.Frame(self.top)
    top_frame.pack(side = 'top', fill='both')
    bottom_frame = Tkinter.Frame(self.top)
    bottom_frame.pack(side = 'bottom', fill='both')
        
    self.br = tkutil.button_row(top_frame,
                           ('Predict', self.predict_cb),
                           ('Close', self.close_cb),)
    self.br.frame.pack(side = 'top', anchor = 'w')
    #self.br.frame.grid(row = 0, column = 0)
    tkutil.create_hint(self.br.buttons[0], 
        'Predict probable amino acid types. Select multiple peaks and click.')
 
    self.ntol = tkutil.entry_field(bottom_frame, 'N tol.:', initial = 0.300, width = 5)
    self.ntol.frame.grid(row = 0, column=0)     
    #self.ntol.frame.pack(side = 'top', anchor = 'e')
    self.ntol_ppm = self.ntol.variable
          
    self.ctol = tkutil.entry_field(bottom_frame, ', C tol.:', initial = 0.400, width = 5)
    self.ctol.frame.grid(row = 0, column=2)
    #self.ctol.frame.pack(side = 'top', anchor = 'e')
    self.ctol_ppm = self.ctol.variable     
         
    self.htol = tkutil.entry_field(bottom_frame, ', H tol.:', initial = 0.030, width = 5)
    self.htol.frame.grid(row=0, column=4)
    #self.htol.frame.pack(side = 'top', anchor = 'e')
    self.htol_ppm = self.htol.variable

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    opt_root = Tkinter.Frame(self.top, height=20, bd=0)
    opt_root.pack(fill="both", padx=0,pady=0, side = 'top', expand = 1)

    opt = Tkinter.Frame(opt_root, height=10, bd=0)
    opt.pack(padx=0,pady=0, anchor='w', side = 'left', expand = 1)

    opt2 = Tkinter.Frame(opt_root, height=10, bd=0)
    opt2.pack(padx=0,pady=0, anchor='w', side = 'left', expand = 1)


    # Use NH, or W1W2W3?
    self.use_mode = Tkinter.IntVar()
    self.use_mode.set(1)
    Tkinter.Radiobutton(opt, text="", variable=self.use_mode, 
                        value=1).pack(anchor='w',side='left')
    Tkinter.Radiobutton(opt2, text="", variable=self.use_mode, 
                        value=2).pack(anchor='w',side='left')

    # Use Nitrogen
    self.useN = Tkinter.IntVar()
    self.useN.set(1)
    self.use_nitrogen_cb = Tkinter.Checkbutton(opt, text = 'Use N', 
                        variable = self.useN, onvalue=1, offvalue = 0)
    self.use_nitrogen_cb.pack(side = 'left', anchor = 'w', expand = 0)

    # Use Amide hydrogen
    self.useH = Tkinter.IntVar()
    self.useH.set(1)
    self.use_hydrogen_cb = Tkinter.Checkbutton(opt, text = 'Use high H', 
                        variable = self.useH, onvalue=1, offvalue = 0)
    self.use_hydrogen_cb.pack(side = 'left', anchor = 'w', expand = 0)
    
    # N-H attached hydrogen
    self.attachNH = Tkinter.IntVar()
    #self.attachNH.set(0)
    self.attachNH.set(1)
    self.attachNH_cb = Tkinter.Checkbutton(opt, text = 'N-H', 
                        variable = self.attachNH, onvalue=1, offvalue = 0)
    self.attachNH_cb.pack(side = 'left', anchor = 'w', expand = 0)
    
    # Use W1, W2, W3
    self.useW = []
    self.use_w_cb = []
    for i in range(3):
      self.useW.append(Tkinter.IntVar())
      self.useW[i].set(1)
      self.use_w_cb.append(Tkinter.Checkbutton(opt2, text = 'Use W%d' % (i+1), 
                        variable = self.useW[i], onvalue=1, offvalue = 0))
      self.use_w_cb[i].pack(side = 'left', anchor = 'w', expand = 0)

    # Scrolling List
    self.peak_pl = tkutil.scrolling_list(self.top, 'Used chemical shifts', 4)
    self.peak_pl.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.peak_pl.listbox.bind('<ButtonRelease-1>', self.move_to_peak_cb) # Func

    self.aa_pl = tkutil.scrolling_list(self.top, 'Amino acid predicted', 5)
    self.aa_pl.frame.pack(side = 'top', fill = 'both', expand = 0)
    self.aa_pl.listbox.bind('<ButtonRelease-1>', self.list_residues_cb)  # Func

    # Sequence file    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)    
    user_seq_ff = tkutil.file_field2(self.top, 'Sequence file: ', '', 
        file_type=[('3-letter-code sequence file with indices', '.seq'), 
                    ('1-letter-code sequence file', '.fasta'), 
                    ('3-letter-code sequence file without indices', '.txt')],
                    default_ext='.seq', width = 25)
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

    self.br2 = tkutil.button_row(self.top,
                           ('Append >5%', self.note_taking_all_cb),
                           ('Append', self.note_taking_cb),
                           ('Append all', self.note_taking_full_cb),
                           ('Push down', self.note_push_cb),
                           ('Pull up', self.note_pull_cb),
                           ('Clear', self.note_clear_cb),)
    self.br2.frame.pack(side = 'top', anchor = 'w')

    show_frm = Tkinter.Frame(self.top)
    show_frm.pack(side = 'top', fill='both', anchor = 'w')
    self.dir_btn = Tkinter.Button(show_frm, text="<->", 
                                            command=self.dir_btn_cb)
    self.dir_btn.pack(side = 'left', anchor = 'w')
    
    self.probable_label = Tkinter.StringVar()    
    self.probable_label.set("Nothing to show...")    
    self.prob_lbl = Tkinter.Label(show_frm, textvariable = self.probable_label, 
                                            anchor = 'w', justify = 'left')		
    self.prob_lbl.pack(side = 'top', anchor = 'w', expand = 1)

    self.seq_pl = tkutil.scrolling_list(self.top, 'In your sequence (i)', 5)
    self.seq_pl.frame.pack(side = 'left', fill='both', expand = 1)
    self.seq_pl.listbox.bind('<Double-ButtonRelease-1>', self.assign_cb) # Func
    self.seq_pl.listbox.bind('<ButtonRelease-3>', self.assign_cb)        # Func

    self.seq_pl2 = tkutil.scrolling_list(self.top, 'History (i-1)', 2)
    self.seq_pl2.frame.pack(side = 'top', fill='both', expand = 1)

    self.seq_pl3 = tkutil.scrolling_list(self.top, 'Pushed History (i-2)', 2)
    self.seq_pl3.frame.pack(side = 'top', fill='both', expand = 1)

    self.seq_pl4 = tkutil.scrolling_list(self.top, 'Double-pushed (i-3)', 2)
    self.seq_pl4.frame.pack(side = 'top', fill='both', expand = 1)
    
    self.seq_pl5 = tkutil.scrolling_list(self.top, 'Triple-pushed (i-4)', 2)
    self.seq_pl5.frame.pack(side = 'bottom', fill='both', expand = 1)

  def predict_cb(self):
    # check reference spectra first
    if self.session.project == None: return
    
    bbC = None
    allC = None
    allH = None

    try:
      ntol = float(self.ntol_ppm.get())
    except:
      ntol = 0.3

    try:
      ctol = float(self.ctol_ppm.get())
    except:
      ctol = 0.3

    try:
      htol = float(self.htol_ppm.get())
    except:
      htol = 0.03

    for spec in self.session.project.spectrum_list():
      if spec.save_path.find('ref_13C.save') != -1: allC = spec
      if spec.save_path.find('ref_1H.save') != -1: allH = spec
      if spec.save_path.find('ref_13C_backbone.save') != -1: bbC = spec

    if bbC == None or allC == None or allH == None:
      tkMessageBox.showerror('Error', 
                      'Reference view should exist. Please type "ir" first.')
      return

    if len(self.session.selected_peaks()) == 0:
      tkMessageBox.showerror('Error', 
                'Please select peaks to use for amino acid type prediction.') 
      return

    self.peak_pl.clear()
    self.aa_pl.clear()
    self.seq_pl.clear()
    res_list = [] # shift, nuclei, spec, peak
    c_num = 0
    C_num = 0


    for peak in self.session.selected_peaks():
      # Use all eligible resonances
      for i in range(len(peak.frequency)):
        if peak.spectrum.nuclei[i] != '13C' and \
                peak.spectrum.nuclei[i] != '1H' and \
                peak.spectrum.nuclei[i] != '15N': continue
      
        # N, H use mode
        if peak.spectrum.nuclei[i] == '15N' and \
                (self.useN.get() == 0 and self.use_mode.get() == 1): continue
        if peak.spectrum.nuclei[i] == '1H' and peak.frequency[i] > 6.0 and \
                (self.useH.get() == 0 and self.use_mode.get() == 1): continue
        # dimension use mode
        if self.use_mode.get() == 2 and self.useW[i].get() == 0: continue

        # check if the peak already exists
        iFound = 0
        for (freq2, nuc2, spec2, peak2, dim) in res_list:
          if nuc2 == '13C' and abs(peak.frequency[i]-freq2) < ctol: 
            iFound = 1
            break
          if nuc2 == '15N' and abs(peak.frequency[i]-freq2) < ntol: 
            iFound = 1
            break
          if nuc2 == '1H' and abs(peak.frequency[i]-freq2) < htol: 
            iFound = 1
            break
        if iFound == 1: continue
        res_list.append( [peak.frequency[i], peak.spectrum.nuclei[i], 
                          peak.spectrum, peak, i] )
        if peak.spectrum.nuclei[i] == '13C' and peak.frequency[i] < 45:
            c_num = c_num + 1
        if peak.spectrum.nuclei[i] == '13C' and peak.frequency[i] < 15:
            c_num = c_num + 1
        if peak.spectrum.nuclei[i] == '13C':
            C_num = C_num + 1

    if c_num > 1 or C_num > 2: refC = allC     # sidechain C
    else: refC = bbC              # only backbone C
    
    # start from 1.0
    prob_list = list(map(lambda x: 1.0, range(20)))
    prob_list2 = list(map(lambda x: 1.0, range(20)))
    for (freq, nuc, spec, peak, dim) in res_list:
      if nuc == '1H': ref = allH
      elif nuc == '13C': ref = refC
      else: ref = None

      if (nuc == '1H' and freq < 6.0) or (nuc == '13C' and freq < 80.0):
        sumHeight = 0.0
        aa_list = []
        for i in range(20):
          height = float(ref.data_height((freq, 0.25 + 0.5 * float(i))))
          height = height * 0.000001
          aa_list.append(height)
        sumHeight = sum(aa_list)

        if sumHeight == 0:
          continue # This resonance is skipped to prevent floating point error

        for i in range(20):
          prob = float(aa_list[i]) / float(sumHeight)
          # deweight everything and will do after this
          prob_list[i] = prob_list[i] * prob / weight_list[i] 
      else: # NX or CO or HN
        if nuc == '15N' and self.useN.get() == 0: continue
        if nuc == '1H' and self.useH.get() == 0: continue
        for i in range(20):
          atms = atomnames.protein_atoms_by_group_2[singlea[i]]
          pmax = 0.0
          for atm in atms:
            if atm[0] != nuc[-1]: continue # should be same nucleic
            ast = shiftstats.atom_statistics(singlea[i], atm)
            if ast == None: continue
            ptemp = shiftstats.get_pvalue(freq, ast.average_shift, 
                                  ast.shift_deviation * float(len(res_list)))
            if ptemp > pmax:
              pmax = ptemp
          prob_list2[i] = prob_list2[i] * pmax
        # normalize
        sumprob2 = sum(prob_list2)
        for i in range(20):
          prob_list2[i] = prob_list2[i] / float(sumprob2)
        
    # weight only once
    for i in range(20):
      prob_list[i] = prob_list[i] * weight_list[i]

    # apply user sequence weight if user sequence exists  
    user_seq_prob_list = self.make_user_seq_prob()
    for i in range(20):
      prob_list[i] = prob_list[i] + sequence_factor * user_seq_prob_list[i]

    # apply prob_list2
    for i in range(20):
      prob_list[i] = prob_list[i] * prob_list2[i]

    # normalize
    allProb = sum(prob_list)
    if allProb == 0.0: return
    for i in range(20):
      prob_list[i] = prob_list[i] / float(allProb)

    aa_list = []
    for i in range(20): 
      aa_list.append( [i, prob_list[i]] )

    sorted_list = sorted(aa_list, key=lambda aa: aa[1], reverse=True)

    # fill peak_pl
    for (freq, nuc, spec, peak, dim) in res_list:
      if spec.dimension == 2: 
          peak_pos = '(%.3f, %.3f)' % peak.frequency
      elif spec.dimension == 3: 
          peak_pos = '(%.3f, %.3f, %.3f)' % peak.frequency
      elif spec.dimension == 4: 
          peak_pos = '(%.3f, %.3f, %.3f)' % peak.frequency
      lbl = '%7.3f ppm - %3s : %s - %s' % (freq, nuc, peak_pos, spec.name)
      self.peak_pl.append(lbl, [spec, peak, freq, nuc, dim])

    # fill aa_pl
    for (aa, prob) in sorted_list:
      lbl = '  %s ( %s ) : %.3f %%' % (singlea[aa], aaa_list[aa], prob * 100.0)
      self.aa_pl.append(lbl, [singlea[aa], prob] )
  # -----------------------------------------------------------------------------
  # Center selected peak in the list
  def move_to_peak_cb(self, event):
    if self.peak_pl == None:
      return
    
    if len(self.peak_pl.selected_line_numbers()) == 0:
      return
    
    [spec, peak, freq, nuc, dim] = self.peak_pl.selected_line_data()[0]
    sputil.show_peak(peak)

  # -----------------------------------------------------------------------------
  def make_user_seq_prob(self):
    plist = list(map(lambda x: 0., range(20)))
    if not os.path.exists(self.user_seq.get()):
      return list(map(lambda x: 0.05, range(20)))
    try:
      readSeq = myseq.ReadSequenceFromFile(self.user_seq.get())
      for i in range(len(readSeq)):
        seq = readSeq[i][1]
        idx = singlea.index(seq)
        plist[idx] = plist[idx] + 1.
      sum_plist = sum(plist)
      for i in range(20):
        plist[i] = plist[i] / sum_plist
    except:
      return list(map(lambda x: 0.05, range(20))) # failed
    return plist
  # -----------------------------------------------------------------------------
  # List all the available residues in your sequence
  def list_residues_cb(self, event):
    if self.aa_pl == None or self.seq_pl == None:
      return
    self.seq_pl.clear()
    [prob_seq, prob_val] = self.aa_pl.selected_line_data()[0]
    # sequence
    if not os.path.exists(self.user_seq.get()):
      tkMessageBox.showerror('Sequence', 'Please set your sequence file.')
      return
    self.make_seq_list(prob_seq, prob_val)

  #
  def make_seq_list(self, prob_seq, prob_val):
    readSeq = myseq.ReadSequenceFromFile(self.user_seq.get())
    for i in range(len(readSeq)):
      seq = readSeq[i][1]
      seq3 = myseq.a2aaa(seq)
      if seq == prob_seq:
        gn = '%s%d' % (seq, readSeq[i][0])
        lbl = '%5s - ' % (gn)
        # get all the resonances related to this group atom
        for condition in self.session.project.condition_list():
          for resn in condition.resonance_list():
            if gn == resn.group.name:
              lbl = lbl + '%s(%.3f) ' % (resn.name, resn.frequency)
        if len(lbl) < 10: lbl = lbl + 'none'
        self.seq_pl.append(lbl, (seq, readSeq[i][0], gn, prob_val)) 
    lbl_list = []
    prob_list = []
    lbl = ''
    # if history has something, find matching
    # only current history available
    if len(self.seq_pl2.line_data) != 0 and len(self.seq_pl3.line_data) == 0:
      for (seq2, seqidx2, gn2, prob2) in self.seq_pl2.line_data:
        for (seq, seqidx, gn, prob) in self.seq_pl.line_data:
          if abs(seqidx-seqidx2) != 1: continue
          bValid = 1
          if self.dir_btn['text'] == '->' and seqidx < seqidx2: bValid = 0
          if self.dir_btn['text'] == '<-' and seqidx > seqidx2: bValid = 0
          if bValid == 0: continue
          if seqidx < seqidx2: lbl = '%s-%s' % (gn, gn2)
          else: lbl = '%s-%s' % (gn2, gn)
          calc_prob=prob*prob2
          lbl_list.append(lbl)
          prob_list.append(calc_prob)
    # look at both history
    if len(self.seq_pl2.line_data) != 0 and len(self.seq_pl3.line_data) != 0 \
                                        and len(self.seq_pl4.line_data) == 0:
      for (seq3, seqidx3, gn3, prob3) in self.seq_pl3.line_data:
        for (seq2, seqidx2, gn2, prob2) in self.seq_pl2.line_data:
          for (seq, seqidx, gn, prob) in self.seq_pl.line_data:
            if abs(seqidx-seqidx2) == 1 and abs(seqidx-seqidx3) == 2 \
                                        and abs(seqidx2-seqidx3) == 1: 
              bValid = 1
              if self.dir_btn['text'] == '->' and seqidx < seqidx2: bValid = 0
              if self.dir_btn['text'] == '<-' and seqidx > seqidx2: bValid = 0
              if bValid == 0: continue     
              if seqidx < seqidx2: lbl = '%s-%s-%s' % (gn, gn2, gn3)
              else: lbl = '%s-%s-%s' % (gn3, gn2, gn)
              calc_prob=prob*prob2*prob3
              lbl_list.append(lbl)
              prob_list.append(calc_prob)
    # look at three history
    if len(self.seq_pl2.line_data) != 0 and len(self.seq_pl3.line_data) != 0 \
                                        and len(self.seq_pl4.line_data) != 0 \
                                        and len(self.seq_pl5.line_data) == 0:
      for (seq4, seqidx4, gn4, prob4) in self.seq_pl4.line_data:
        for (seq3, seqidx3, gn3, prob3) in self.seq_pl3.line_data:
          for (seq2, seqidx2, gn2, prob2) in self.seq_pl2.line_data:
            for (seq, seqidx, gn, prob) in self.seq_pl.line_data:
              if abs(seqidx-seqidx2) == 1 and abs(seqidx-seqidx3) == 2 and \
                  abs(seqidx2-seqidx3) == 1 and abs(seqidx-seqidx4) == 3 and \
                  abs(seqidx3-seqidx4) == 1:      
                bValid = 1
                if self.dir_btn['text'] == '->' and seqidx < seqidx2:
                  bValid = 0
                if self.dir_btn['text'] == '<-' and seqidx > seqidx2:
                  bValid = 0
                if bValid == 0: 
                  continue
                if seqidx < seqidx2: 
                  lbl = '%s-%s-%s-%s' % (gn, gn2, gn3, gn4)
                else: 
                  lbl = '%s-%s-%s-%s' % (gn4, gn3, gn2, gn)
                calc_prob = prob * prob2 * prob3 * prob4
                lbl_list.append(lbl)
                prob_list.append(calc_prob)

    # look at four history
    if len(self.seq_pl2.line_data) != 0 and len(self.seq_pl3.line_data) != 0 \
                    and len(self.seq_pl4.line_data) != 0 \
                    and len(self.seq_pl5.line_data) != 0:
      if len(self.seq_pl.line_data) * len(self.seq_pl2.line_data) * \
          len(self.seq_pl3.line_data) * len(self.seq_pl4.line_data) * \
          len(self.seq_pl5.line_data) > 20000:
        # too big number... we will not use the last history
        for (seq4, seqidx4, gn4, prob4) in self.seq_pl4.line_data:
          for (seq3, seqidx3, gn3, prob3) in self.seq_pl3.line_data:
            for (seq2, seqidx2, gn2, prob2) in self.seq_pl2.line_data:
              for (seq, seqidx, gn, prob) in self.seq_pl.line_data:
                if abs(seqidx-seqidx2) == 1 and abs(seqidx-seqidx3) == 2 \
                    and abs(seqidx2-seqidx3) == 1 and abs(seqidx-seqidx4) == 3 \
                    and abs(seqidx3-seqidx4) == 1:
                  bValid = 1
                  if self.dir_btn['text'] == '->' and seqidx < seqidx2: 
                    bValid = 0
                  if self.dir_btn['text'] == '<-' and seqidx > seqidx2: 
                    bValid = 0
                  if bValid == 0: 
                    continue
                  if seqidx < seqidx2: 
                    lbl = '%s-%s-%s-%s' % (gn, gn2, gn3, gn4)
                  else: 
                    lbl = '%s-%s-%s-%s' % (gn4, gn3, gn2, gn)
                  calc_prob = prob * prob2 * prob3 * prob4
                  lbl_list.append(lbl)
                  prob_list.append(calc_prob)
      else:
        for (seq5, seqidx5, gn5, prob5) in self.seq_pl5.line_data:      
          for (seq4, seqidx4, gn4, prob4) in self.seq_pl4.line_data:
            for (seq3, seqidx3, gn3, prob3) in self.seq_pl3.line_data:
              for (seq2, seqidx2, gn2, prob2) in self.seq_pl2.line_data:
                for (seq, seqidx, gn, prob) in self.seq_pl.line_data:
                  if abs(seqidx-seqidx2) == 1 and abs(seqidx-seqidx3) == 2 \
                      and abs(seqidx2-seqidx3) == 1 and abs(seqidx-seqidx4) == 3 \
                      and abs(seqidx3-seqidx4) == 1 and abs(seqidx4-seqidx5) == 1 \
                      and abs(seqidx3-seqidx5) == 2: 
                    bValid = 1
                    if self.dir_btn['text'] == '->' and seqidx < seqidx2: 
                      bValid = 0
                    if self.dir_btn['text'] == '<-' and seqidx > seqidx2: 
                      bValid = 0
                    if bValid == 0: continue     
                    if seqidx < seqidx2: 
                      lbl = '%s-%s-%s-%s-%s' % (gn, gn2, gn3, gn4, gn5)
                    else: 
                      lbl = '%s-%s-%s-%s-%s' % (gn5, gn4, gn3, gn2, gn)
                    calc_prob = prob * prob2 * prob3 * prob4 * prob5
                    lbl_list.append(lbl)
                    prob_list.append(calc_prob)
          
    if lbl == '':     
      lbl = 'Nothing to show...'
    else:
      sum_prob = sum(prob_list)
      if sum_prob != 0:
        sort_list = []
        for i in range(len(prob_list)):
          prob_list[i] = prob_list[i] / sum_prob
          lbl2 = lbl_list[i]
          lbl2 = lbl2 + '[%.2f]' % (prob_list[i])
          lbl_list[i] = lbl2
          sort_list.append([prob_list[i], lbl_list[i]])
        sorted_list = sorted(sort_list, key=lambda prob: prob[0], reverse=True)
        lbl_list = []
        for i in range(len(sorted_list)):
          lbl_list.append(sorted_list[i][1])
      lbl = ''
      for i in range(len(lbl_list)):
        if i != 0: lbl = lbl + ','
        lbl = lbl + lbl_list[i]
    if len(lbl) > 60:
      lbl = lbl[0:57] + '...'
    self.probable_label.set(lbl)

  def dir_btn_cb(self):
    cur_text = self.dir_btn['text']
    if cur_text == '<->': self.dir_btn['text'] = '->'
    elif cur_text == '->': self.dir_btn['text'] = '<-'
    else: self.dir_btn['text'] = '<->'
    if self.aa_pl.selected_line_data() != None and \
        len(self.aa_pl.selected_line_data()) != 0:
      self.list_residues_cb(None)
    pass

  # -----------------------------------------------------------------------------
  # 
  def note_clear_cb(self):
    self.seq_pl2.clear()
    self.seq_pl3.clear()
    self.seq_pl4.clear()
    self.seq_pl5.clear()

  def note_push_cb(self):
    self.seq_pl5.clear()
    for i in range(len(self.seq_pl4.line_data)):
      line = self.seq_pl4.listbox.get(i)
      (seq, seqidx, gn, prob) = self.seq_pl4.line_data[i]
      self.seq_pl5.append(line, (seq, seqidx, gn, prob))

    self.seq_pl4.clear()
    for i in range(len(self.seq_pl3.line_data)):
      line = self.seq_pl3.listbox.get(i)
      (seq, seqidx, gn, prob) = self.seq_pl3.line_data[i]
      self.seq_pl4.append(line, (seq, seqidx, gn, prob))

    self.seq_pl3.clear()
    for i in range(len(self.seq_pl2.line_data)):
      line = self.seq_pl2.listbox.get(i)
      (seq, seqidx, gn, prob) = self.seq_pl2.line_data[i]
      self.seq_pl3.append(line, (seq, seqidx, gn, prob))
    self.seq_pl2.clear()

  def note_pull_cb(self):
    self.seq_pl2.clear()
    for i in range(len(self.seq_pl3.line_data)):
      line = self.seq_pl3.listbox.get(i)
      (seq, seqidx, gn, prob) = self.seq_pl3.line_data[i]
      self.seq_pl2.append(line, (seq, seqidx, gn, prob))
    self.seq_pl3.clear()

    for i in range(len(self.seq_pl4.line_data)):
      line = self.seq_pl4.listbox.get(i)
      (seq, seqidx, gn, prob) = self.seq_pl4.line_data[i]
      self.seq_pl3.append(line, (seq, seqidx, gn, prob))
    self.seq_pl4.clear()

    for i in range(len(self.seq_pl5.line_data)):
      line = self.seq_pl5.listbox.get(i)
      (seq, seqidx, gn, prob) = self.seq_pl5.line_data[i]
      self.seq_pl4.append(line, (seq, seqidx, gn, prob))
    self.seq_pl5.clear()

  def note_taking_cb(self):
    for i in range(len(self.seq_pl.line_data)):
      line = self.seq_pl.listbox.get(i)
      (seq, seqidx, gn, prob) = self.seq_pl.line_data[i]
      self.seq_pl2.append(line, (seq, seqidx, gn, prob))

  def note_taking_above(self, pcut):
    if self.aa_pl == None or self.seq_pl == None:
      return
    if not os.path.exists(self.user_seq.get()):
      tkMessageBox.showerror('Sequence', 'Please set your sequence file.')
      return
    
    for [prob_seq, prob_val] in self.aa_pl.line_data:
      if prob_val < pcut: continue
      self.seq_pl.clear()
      self.make_seq_list(prob_seq, prob_val)    
      self.note_taking_cb()
    self.seq_pl.clear()
    self.probable_label.set("Nothing to show...")   
      
  def note_taking_full_cb(self):
    self.note_taking_above(0.0)
      
  def note_taking_all_cb(self):
    self.note_taking_above(0.05)

  # -----------------------------------------------------------------------------
  # Make probabilities for given seq and atoms
  def make_prob(self, seq, atm, freq):
    prob_list = []
    ast = shiftstats.atom_statistics(seq, atm)
    prob = shiftstats.get_pvalue(freq, ast.average_shift, ast.shift_deviation)
    if freq < ast.minimum_shift or freq > ast.maximum_shift: prob = 0.0
    return prob

  # -----------------------------------------------------------------------------
  # Make probabilities for given seq and atoms
  def make_probs(self, seq, atoms, freq):
    prob_list = []
    for atm in atoms:
      ast = shiftstats.atom_statistics(seq, atm)
      prob = shiftstats.get_pvalue(freq, ast.average_shift, ast.shift_deviation)
      if freq < ast.minimum_shift or freq > ast.maximum_shift: prob = 0.0
      prob_list.append(prob*ast.count)
    # normalize
    sum_prob = sum(prob_list)
    if sum_prob == 0: return prob_list
    for i in range(len(prob_list)):
      prob_list[i] = prob_list[i] / sum_prob
    return prob_list
  # -----------------------------------------------------------------------------
  def is_duplicated(self, tup):
    dup = 0
    for i in range(len(tup)):
      for j in range(i+1, len(tup)):
        if tup[i] == tup[j]:
          return 1
    return 0
  # -----------------------------------------------------------------------------
  # Try to assign for selected sequence in seq_pl
  def assign_cb(self, event):
    # assign resonances from seq_pl
    if self.aa_pl == None or self.seq_pl == None: return
    if self.seq_pl.selected_line_data() == None or \
        len(self.seq_pl.selected_line_data()) == 0: return

    (seq, seqidx, gn, prob) = self.seq_pl.selected_line_data()[0]
    
    # get IUPAC atoms by sequence
    atoms = shiftstats.get_atoms_by_sequence(seq)

    try:
      ntol = float(self.ntol_ppm.get())
    except:
      ntol = 0.3

    try:
      ctol = float(self.ctol_ppm.get())
    except:
      ctol = 0.3

    try:
      htol = float(self.htol_ppm.get())
    except:
      htol = 0.03

    # split atoms
    C_atoms = []
    N_atoms = []  
    H_atoms = []
    bigH_atoms = []
    for atm in atoms:
      if atm[0] == 'C': C_atoms.append(atm)
      if atm[0] == 'N': N_atoms.append(atm)
      if atm[0] == 'H': 
        ast = shiftstats.atom_statistics(seq, atm)      
        if ast.average_shift < 6.5: 
          H_atoms.append(atm)
        if ast.average_shift > 6:
          bigH_atoms.append(atm)

    # get peaks
    C_peaks = []
    N_peaks = []
    H_peaks = []
    bigH_peaks = []

    # Make initial probabilities
    for [spec, peak, freq, nuc, dim] in self.peak_pl.line_data:
      if nuc == '15N': 
        probs = self.make_probs(seq, N_atoms, freq)
        N_peaks. append([freq, peak, dim, probs])
      elif nuc == '1H':
        if freq < 6.5:
          probs = self.make_probs(seq, H_atoms, freq)
          H_peaks.append([freq, peak, dim, probs])
        if freq > 6:
          probs = self.make_probs(seq, bigH_atoms, freq)
          # we will use occurrences for this especially
          if len(probs) > 1:
            for i in range(len(probs)):             
              ast = shiftstats.atom_statistics(seq, bigH_atoms[i])
              probs[i] = float(ast.count) * probs[i]
            sum_prob = sum(probs)
            if sum_prob != 0:
              for i in range(len(probs)):             
                probs[i] = probs[i] / sum_prob            
          bigH_peaks.append([freq, peak, dim, probs])
      else: 
        probs = self.make_probs(seq, C_atoms, freq)
        C_peaks.append([freq, peak, dim, probs])

    # Make prob matrix
    N_size = max(len(N_peaks), len(N_atoms))
    C_size = max(len(C_peaks), len(C_atoms))
    H_size = max(len(H_peaks), len(H_atoms))
    bigH_size = max(len(bigH_peaks), len(bigH_atoms))

    N_prob_mat = [[0 for x in range(N_size)] for y in range(N_size)]
    C_prob_mat = [[0 for x in range(C_size)] for y in range(C_size)]
    H_prob_mat = [[0 for x in range(H_size)] for y in range(H_size)]
    bigH_prob_mat = [[0 for x in range(bigH_size)] for y in range(bigH_size)]

    # N
    for i in range(len(N_peaks)):
      [freq, peak, dim, probs] = N_peaks[i]
      for j in range(len(probs)):
        N_prob_mat[i][j] = probs[j]
    # C
    for i in range(len(C_peaks)):
      [freq, peak, dim, probs] = C_peaks[i]
      for j in range(len(probs)):
        C_prob_mat[i][j] = probs[j]
    # H
    for i in range(len(H_peaks)):
      [freq, peak, dim, probs] = H_peaks[i]
      for j in range(len(probs)):
        H_prob_mat[i][j] = probs[j]

    # big H
    for i in range(len(bigH_peaks)):
      [freq, peak, dim, probs] = bigH_peaks[i]
      for j in range(len(probs)):
        bigH_prob_mat[i][j] = probs[j]

    # find maximum marginal probability using brute force.
    # if list number is more than 10, we don't do this.
    lookup_list = []

    # Nitrogens
    if len(N_peaks) != 0 and N_size < 10:
      perms = itertools.permutations(range(N_size))
      best_tuple = None
      max_margin = 0
      for tup in perms:
        #if self.is_duplicated(tup) == 1: continue
        # calculate sum
        sum_prob = 0
        for i in range(len(tup)):
          sum_prob = sum_prob + N_prob_mat[i][tup[i]]
        if sum_prob > max_margin: 
          max_margin = sum_prob
          best_tuple = tup
      if best_tuple != None: 
        for i in range(len(best_tuple)):
          if i > len(N_peaks)-1: break # over the peak limits
          if best_tuple[i] > len(N_atoms)-1: continue # no assignment
          [freq, peak, dim, probs] = N_peaks[i]
          lookup_list.append( [N_atoms[best_tuple[i]], freq, probs] )

    # Carbons
    if len(C_peaks) != 0 and C_size < 15:
      perms = itertools.permutations(range(C_size))
      best_tuple = None
      max_margin = 0
      for tup in perms:
        #if self.is_duplicated(tup) == 1: continue
        # calculate sum
        sum_prob = 0
        for i in range(len(tup)):
          sum_prob = sum_prob + C_prob_mat[i][tup[i]]
        if sum_prob > max_margin: 
          max_margin = sum_prob
          best_tuple = tup
      if best_tuple != None: 
        for i in range(len(best_tuple)):
          if i > len(C_peaks)-1: break # over the peak limits
          if best_tuple[i] > len(C_atoms)-1: continue # no assignment
          [freq, peak, dim, probs] = C_peaks[i]
          lookup_list.append( [C_atoms[best_tuple[i]], freq, probs] )

    # Protons
    if len(H_peaks) != 0 and H_size < 15:
      perms = itertools.permutations(range(H_size))
      best_tuple = None
      max_margin = 0
      for tup in perms:
        #if self.is_duplicated(tup) == 1: continue
        # calculate sum
        sum_prob = 0
        for i in range(len(tup)):
          sum_prob = sum_prob + H_prob_mat[i][tup[i]]
        if sum_prob > max_margin: 
          max_margin = sum_prob
          best_tuple = tup
      if best_tuple != None:
        for i in range(len(best_tuple)):
          if i > len(H_peaks)-1: break # over the peak limits
          if best_tuple[i] > len(H_atoms)-1: continue # no assignment
          [freq, peak, dim, probs] = H_peaks[i]
          lookup_list.append( [H_atoms[best_tuple[i]], freq, probs] )

    # big Protons
    if len(bigH_peaks) != 0 and bigH_size < 15:
      perms = itertools.permutations(range(bigH_size))
      best_tuple = None
      max_margin = 0
      for tup in perms:
        #if self.is_duplicated(tup) == 1: continue
        # calculate sum
        sum_prob = 0
        for i in range(len(tup)):
          sum_prob = sum_prob + bigH_prob_mat[i][tup[i]]
        if sum_prob > max_margin: 
          max_margin = sum_prob
          best_tuple = tup
      if best_tuple != None:
        for i in range(len(best_tuple)):
          if i > len(bigH_peaks)-1: break # over the peak limits
          if best_tuple[i] > len(bigH_atoms)-1: continue # no assignment
          [freq, peak, dim, probs] = bigH_peaks[i]
          lookup_list.append( [bigH_atoms[best_tuple[i]], freq, probs] )
    
    # Actual assignment but we will do this based on current selection
    for peak in self.session.selected_peaks():
      best_probs = []
      resN, resH = None, None
      iN, iH = -1, -1
      for i in range(len(peak.frequency)):
        if peak.resonances()[i] != None and peak.resonances()[i].name != '?': 
          continue
        frq = peak.frequency[i]
        nuclei = peak.spectrum.nuclei[i]
        if nuclei == '15N': 
          tol = ntol
          resN = peak.resonances()[i]
          iN = i
        elif nuclei == '13C': 
          tol = ctol
        else: 
          tol = htol
          if frq > 6.0:
           resH = peak.resonances()[i]
           iH = i
        best_atm = ''
        best_dist = 999
        best_prob = 0
        for [atm, frq2, probs] in lookup_list:
          if abs(frq-frq2) > tol: continue
          if valid_frequency(seq, atm, frq2) == 0: continue
          if best_dist >= abs(frq-frq2) and probs > best_prob:
            best_dist = abs(frq-frq2)
            best_atm = atm
        if best_atm != '':
          peak.assign(i, gn, best_atm)
          best_probs.append(best_prob)
      # if peak has "N" or "H", we will consider N-H connection
      # if N-H consider option is on
      if self.attachNH.get() == 1 and self.use_mode.get() == 1 \
          and resN != None and resH != None:
        # check if we have "N" or "H" with same residue number
        if resN.group.number == resH.group.number:
          peak.assign(iN, resN.group.name, 'N')
          peak.assign(iH, resN.group.name, 'H')
          
      # We will assign from resonance list if sequence index is close
      for i in range(len(peak.frequency)):
        if peak.resonances()[i] != None \
          and peak.resonances()[i].name != '?': continue
        frq = peak.frequency[i]
        nuclei = peak.spectrum.nuclei[i]
        if nuclei == '15N': 
          tol = ntol
        elif nuclei == '13C': 
          tol = ctol
        else: 
          tol = htol
        best_resn = None
        best_dist = 999
        for condition in self.session.project.condition_list():
          for resonance in condition.resonance_list():
            if abs(resonance.frequency - frq) > tol: continue
            if abs(resonance.group.number - seqidx) > 1: continue
            if best_dist > abs(resonance.frequency - frq):
              best_dist = abs(resonance.frequency - frq)
              best_resn = resonance
        if best_resn != None:
          peak.assign(i, best_resn.group.name, best_resn.atom.name)

      # This is for solution NMR
      # we will do adjustment for attached atoms for N-H
      # at least one N and one big H
#      if peak.is_assigned == 1 and len(best_probs) == len(peak.frequency): # all axes assigned and probs are guessed
#        resns = peak.resonances()
#        # dim 1 and 2, not N or not H
#        if resns[0].group == resns[1].group and (len(resn[0].atom.name) != 1 or len(resn[1].atom.name) != 1):
#          self.check_nh(peak, best_probs, 0, 1)
#        if len(resns) == 3:
#          if resns[0].group == resns[2].group and (len(resn[0].atom.name) != 1 or len(resn[2].atom.name) != 1):
#            self.check_nh(peak, best_probs, 0, 2)
#          if resns[1].group == resns[2].group:
#            self.check_nh(peak, best_probs, 1, 2)      

      peak.show_assignment_label()  

  def check_nh(self, peak, best_probs, dim1, dim2):
    cur_sumprob = best_probs[dim1]+best_probs[dim2]
    if resns[dim1].atom.nucleus == '1H' \
        and resns[dim2].atom.nucleus == '15N': 
      dims = [dim1, dim2]
    elif resns[dim2].atom.nucleus == '1H' \
        and resns[dim1].atom.nucleus == '15N': 
      dims = [dim2, dim1]
    else: 
      return
    Hprobs = self.make_probs(resns[dims[0]].group.symbol, 
                              ['H'], peak.frequency[dims[0]])
    Nprobs = self.make_probs(resns[dims[1]].group.symbol, 
                              ['N'], peak.frequency[dims[1]])
    nh_sumprob = Hprobs[0]+Nprobs[0]
    if cur_sumprob < nh_sumprob:
      peak.assign(dims[0], resns.group.name, 'H')
      peak.assign(dims[1], resns.group.name, 'N')
    
def show_aa_predictor(session):
  sputil.the_dialog(aa_predict_dialog,session).show_window(1)
