# -----------------------------------------------------------------------------
# Fit peak heights or volumes in a series of spectra to a decaying exponential.
#
import math
import re
import string
import Tkinter

import curvefit
import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox
import nmrfam
import os
import os.path    
import random

# -----------------------------------------------------------------------------
# NMRFAM-SPARKY enhancement
#
# Updated by Woonghee Lee (whlee@nmrfam.wisc.edu)
# All on/off toggle added
# Last update: Jan 24, 2019
# Added box mode in relaxbox.py from UCSF version
# TO DO: vertical scroll bar in the spectrum table?

# -----------------------------------------------------------------------------
# Parameters for sum over box mode.  Spectrum values are taken at nearest
# spectrum grid point.
box_samples = (9, 9)
box_size_ppm = (0.2, 0.5)  # PPM box size along w1, w2 axes.

# -----------------------------------------------------------------------------
#
class relaxation_dialog(tkutil.Dialog, tkutil.Stoppable):

  HEIGHTS_MODE = 'heights at same position in each spectrum'
  ASSIGNED_HEIGHTS_MODE = 'heights at assigned peak positions if available'
  ASSIGNED_HEIGHTS_ONLY_MODE = 'heights at assigned peak positions only'
  ASSIGNED_FHEIGHTS_ONLY_MODE = 'fit heights at assigned peak positions only'  
  VOLUMES_MODE = 'volumes of assigned peaks only'
  BOX_MODE = 'sum over box for selected peaks'
  NOTES_MODE = 'notes of assigned peaks only'

  def __init__(self, session):

    self.session = session
    self.spectrum_times = []
    self.last_spectrum_times = []
    self.error_estimate_trials = 5
    self.fit_mode = 1
    self.relax_mode = 1
    
    tkutil.Dialog.__init__(self, session.tk, 'Peak Height Analysis')

    pl = tkutil.scrolling_list(self.top, heading = '', height = 5)
    pl.frame.pack(side = 'top', fill = 'both', expand = 1)
    pl.listbox.config(selectmode='extended')
    #pl.listbox.bind('<ButtonRelease-1>', self.show_fit_cb)
    pl.listbox.bind('<Double-ButtonRelease-1>', self.show_fit_cb)
    pl.listbox.bind('<KeyPress-Delete>', pl.delete_selected_cb)
    # The following is needed so key press is received by list box.
    pl.listbox.bind('<ButtonRelease-1>', pl.set_focus_cb)
    self.peak_list = pl

    md = tkutil.option_menu(self.top, 'Use ',
                            (self.HEIGHTS_MODE,
                             self.ASSIGNED_HEIGHTS_MODE,
                             self.ASSIGNED_HEIGHTS_ONLY_MODE,
                             self.ASSIGNED_FHEIGHTS_ONLY_MODE,
                             self.VOLUMES_MODE,
                             self.BOX_MODE,
                             self.NOTES_MODE))
    md.frame.pack(side = 'top', anchor = 'w')
    self.mode = md.variable

    progress_label = Tkinter.Label(self.top, anchor = 'nw')
    progress_label.pack(side = 'top', anchor = 'w')

    br = tkutil.button_row(self.top,
                           ('Update', self.update_cb),    
                           ('Update no fit', self.update_no_fit_cb),
                           ('Setup...', self.setup_cb),
                           ('Save', self.peak_list.save_cb),
                           ('Append', self.peak_list.append_cb),
                           ('Clear', self.clear_cb),
                           ('Stop', self.stop_cb),
                           ('Help', sputil.help_cb(session, 'RelaxFit')),
                           ('Close', self.close_cb),                           
         )
    
    br.frame.pack(side = 'top', anchor = 'w')     
    br2 = tkutil.button_row(self.top,
                           ('Plot T-decay', self.plot_cb),    
                           ('Plot 1/T-decay', self.plot_cb2),
                           ('Plot heights by residue', self.plot_res_cb),
                           ('Plot heights by spectrum', self.plot_spec_cb),
                           ('Nessy', self.nessy_cb),
			   )
    br2.frame.pack(side = 'top', anchor = 'w')
    tkutil.Stoppable.__init__(self, progress_label, br.buttons[6])

  # ---------------------------------------------------------------------------
  #
  def setup_cb(self):

    setup_dialog = sputil.the_dialog(relax_setup_dialog, self.session)
    settings = {'spectrum-times': self.spectrum_times,
                'error-estimate-trials': self.error_estimate_trials}
    setup_dialog.set_parent_dialog(self, settings, self.set_params)
    setup_dialog.show_window(1)

  # ---------------------------------------------------------------------------
  #
  def set_params(self, settings):

    self.spectrum_times = settings['spectrum-times']
    self.error_estimate_trials = settings['error-estimate-trials']

  # ---------------------------------------------------------------------------
  #
  def clear_cb(self):

    self.peak_list.clear()

  # ---------------------------------------------------------------------------
  #
  def show_fit_cb(self, event):

    (fit, p, line) = self.peak_list.event_line_data(event)
    if fit:
      curvefit.show_fit(self.session, fit.name, fit, self.show_peak_cb)

  # ---------------------------------------------------------------------------
  #
  def show_peak_cb(self, fit, n):

    # Need to skip spectra where no fit height was available.
    sh_pairs = map(lambda th, st: (st[0], th[1]),
                   fit.th_pairs, fit.spectrum_times)
    fit_sh = filter(lambda sh: sh[1] != None, sh_pairs)
    fit_spectra = map(lambda sh: sh[0], fit_sh)
    
    sputil.show_spectrum_position(fit_spectra[n], fit.peak_position)
  # ---------------------------------------------------------------------------
  #
  def update_cb(self):
    self.show_peak_heights(1)    
  # ---------------------------------------------------------------------------
  #
  def update_no_fit_cb(self):
    self.show_peak_heights(0)
  # ---------------------------------------------------------------------------
  #
  def nessy_cb(self):
    if len(self.spectrum_times) < 2:
      tkMessageBox.showerror('Error', 'Click Setup button and check at least two spectra to analyze.')
      return          
  
    options = {}
    options['title'] = 'Select a directory to save peak lists to run NESSY.'
    options['initialdir'] = self.session.project.sparky_directory
    import tkFileDialog
    path = tkFileDialog.askdirectory(**options)
    if not (path) and not (os.path.isdir(path)):
      return
      
    for i in range(len(self.spectrum_times)):
      s, t = self.spectrum_times[i]
      save_lines = ' Assignment         w1         w2         Data Height\n\n'
      for j in range(len(self.peak_list.line_data)):
        fit, p, line = self.peak_list.line_data[j]
        line = '%15s %9.3f %9.3f %20d\n' % (fit.name, fit.peak_position[0], fit.peak_position[1], fit.th_pairs[i][1])
        save_lines = save_lines + line
      save_path = os.path.join(path, s.name + '.list')
      f = open(save_path, 'w')
      f.write(save_lines)
      f.close()
    tkMessageBox.showinfo('Save', '%d peak list files saved.\n Press F9 in the NESSY to import' % (len(self.spectrum_times)))
    nmrfam.run_nessy(self.session)
    
  # ---------------------------------------------------------------------------
  #
  def show_peak_heights(self, fit_mode):

    if not self.top.winfo_ismapped():
      self.show_window(1)
    else:    
      if len(self.spectrum_times) < 2:
        tkMessageBox.showerror('Error', 'Click Setup button and check at least two spectra to analyze.')
        return          
      if len(self.session.selected_peaks()) == 0:
        tkMessageBox.showerror('Error', 'Select peaks on the spectrum view.')
        return


    self.fit_mode = fit_mode
    if self.spectrum_times:
      if self.spectrum_times != self.last_spectrum_times:
        self.last_spectrum_times = self.spectrum_times
        self.show_heading(self.spectrum_times)
      peaks = self.session.selected_peaks()

      count = self.stoppable_call(self.show_peaks, peaks, self.spectrum_times)
      try:
        not_fit = len(peaks) - count
        if not_fit:
          self.peaks_not_fit_warning(not_fit)
      except:
        pass
    
  # ---------------------------------------------------------------------------
  #
  def peaks_not_fit_warning(self, not_fit):

    if not_fit > 0:
      if not_fit > 1:  plural = 's'
      else:            plural = ''
      if self.mode.get() == self.VOLUMES_MODE:   h_or_v = 'volumes'
      elif self.mode.get() == self.BOX_MODE:     h_or_v = 'box sums'
      elif self.mode.get() == self.NOTES_MODE:   h_or_v = 'notes'
      elif self.mode.get() == self.ASSIGNED_FHEIGHTS_ONLY_MODE: h_or_v = 'fheights'      
      else:                                      h_or_v = 'heights'
      msg = ('%d peak%s with less than 2 %s not fit.'
             % (not_fit, plural, h_or_v))
      self.progress_report(msg)
  # ---------------------------------------------------------------------------
  #
  def show_peaks(self, peaks, spectrum_times):

    value_mode = self.mode.get()
    self.stoppable_loop(' peaks', 1)
    count = 0
    
    iMin = 999999999
    iMax = -999999999
    
    peak_list = []
    for p in self.session.selected_peaks(): 
      if p == None: continue
      if p.resonances() == None: continue
      if p.is_assigned == 0:
        peak_list.append(p)
        continue
        
      if iMin > p.resonances()[0].group.number: iMin = p.resonances()[0].group.number
      if iMax < p.resonances()[0].group.number: iMax = p.resonances()[0].group.number  
    
    if iMin <= iMax:
      try:
        for i in range(iMin, iMax+1):
          for p in self.session.selected_peaks():
            if p == None: continue
            if p.resonances() == None: continue
            if p.is_assigned == 0: continue
            self.check_for_stop()
            if i == p.resonances()[0].group.number: 
              peak_list.append(p)
      except:
        for p in self.session.selected_peaks():
          if p == None: continue
          if p.resonances() == None: continue
          if p.is_assigned == 0: continue
          self.check_for_stop()
          peak_list.append(p)
    #else:
    #  for p in self.session.selected_peaks():
    #    if p == None: continue
    #    if p.resonances() == None: continue
    #    self.check_for_stop()
    #    peak_list.append(p)
        
    #for p in self.session.selected_peaks():

    # check if there is different signed peak
    pos_peaks = []
    neg_peaks = []
    proceed = 1
    if self.fit_mode == 1:
      for p in peak_list:
        if p.data_height >= 0: pos_peaks.append(p)
        else: neg_peaks.append(p)
    if len(pos_peaks) * len(neg_peaks) != 0:
      if not tkMessageBox.askokcancel('Warning', 'Inconsistent intensity sign detected. Do you want to proceed? It is recommended to save before proceeding because it can cause convergence error which may run forever.'):
        proceed = 0
    
    for p in peak_list:
      if p == None: continue
      if p.resonances() == None: continue

      self.check_for_stop()
      th_pairs = self.time_height_pairs(p, value_mode, spectrum_times)
      
      if self.fit_mode == 1 and proceed == 1:
        fit = self.fit_exponential(th_pairs)
        if fit == None:
          continue
        fit.name = p.assignment
        fit.peak_position = p.position
        fit.spectrum_times = spectrum_times
        fit.th_pairs = th_pairs
        line = self.peak_line(p, fit)
        self.peak_list.append(line, (fit, p, line))
        self.peak_list.listbox.see('end')
        count = count + 1
      else:
        htext = ''
        for t, h in th_pairs:
          if h == None:
            htext = htext + '%10s ' % 'N/A'
          else:
            htext = htext + '%10.4g ' % h
        ftext = '%15s %9.4g %-8.3g ' % (p.assignment, 0, 0)
        line = ftext + htext
        self.peak_list.append(line, (None, p, line))
        self.peak_list.listbox.see('end')
        count = count + 1
          
    return count

      
  # ---------------------------------------------------------------------------
  #
  def show_heading(self, spectrum_times):

    self.peak_list.clear()
    heading = '%15s %9s %-8s ' % ('Assignment', 'T-decay', 'SD')
    for s, t in spectrum_times:
      st = '%s/%.3g' % (s.name, t)
      heading = heading + '%10s ' % st
    self.peak_list.heading['text'] = heading

  # ---------------------------------------------------------------------------
  #
  def time_height_pairs(self, peak, value_mode, spectrum_times):

    pos = peak.position

    if peak.is_assigned and value_mode != self.HEIGHTS_MODE:
      assignment = peak.assignment
    else:
      assignment = None

    th_pairs = []
    for s, t in spectrum_times:
      h = None
      if assignment:
        p = s.find_peak(assignment)
      else:
        p = None
      if value_mode == self.HEIGHTS_MODE:
        h = s.data_height(pos)
      elif value_mode == self.ASSIGNED_HEIGHTS_MODE:
        if p:
          h = s.data_height(p.position)
        else:
          h = s.data_height(pos)
      elif value_mode == self.ASSIGNED_HEIGHTS_ONLY_MODE:
        if p:
          h = s.data_height(p.position)
      elif value_mode == self.VOLUMES_MODE:
        if p and p.volume != None:
          h = p.volume
      elif value_mode == self.ASSIGNED_FHEIGHTS_ONLY_MODE:
        if p and p.fit_height != None:
          h = p.fit_height
      elif value_mode == self.BOX_MODE:
        px, py = pos
        box_sum = 0
        bsi, bsj = box_samples
        isz, jsz = box_size_ppm
        for i in range(0, bsi):
          dx = isz * (i - .5*(bsi-1)/(bsi-1))
          for j in range(0, bsj):
            dy = jsz * (j - .5*(bsj-1)/(bsj-1))
            box_sum += s.data_height((px+dx, py+dy))
        h = box_sum
      elif value_mode == self.NOTES_MODE:
        if p and p.note != '':
          try:
            h = float(p.note)
          except:
            pass  
      th_pairs.append((t, h))

    return th_pairs

  # ---------------------------------------------------------------------------
  #
  def fit_exponential(self, th_pairs):

    fit_th_pairs = filter(lambda th: th[1] != None, th_pairs)
    if len(fit_th_pairs) < 2:
      return None
    
    exp_func = a_exp_bx_function()
    
    h_values = map(lambda th: th[1], fit_th_pairs)
    h_middle = .5 * (max(h_values) + min(h_values))
    params = (h_middle, 0)
    trials = self.error_estimate_trials

    fit = curvefit.least_squares_fit(fit_th_pairs, exp_func, params, 1e-6)
    fit.estimate_parameter_error(fit.point_sd, trials)

    self.calculate_decay_time(fit)

    return fit

  # ---------------------------------------------------------------------------
  # The error estimate for T is not the standard deviation over fits with
  # gaussian random y errors added.  I believe such a standard deviation is
  # divergent because the flat fit (T = infinity) case has codimension 1.
  # So instead I take the SD of the rate constant (1/T) and convert this
  # to an equivalent T error.
  #
  def calculate_decay_time(self, fit):

    if fit.converged and fit.params[1] != 0:
      t_decay = -1 / fit.params[1]
      t_sd = abs(t_decay * fit.param_sd[1] /  fit.params[1])
    else:
      t_decay = 0
      t_sd = 0
    
    fit.t_decay = t_decay
    fit.t_sd = t_sd

  # ---------------------------------------------------------------------------
  #
  def peak_line(self, peak, fit):

    htext = ''
    for t, h in fit.th_pairs:
      if h == None:
        htext = htext + '%10s ' % 'N/A'
      else:
        htext = htext + '%10.4g ' % h

    ftext = '%15s %9.4g %-8.3g ' % (peak.assignment, fit.t_decay, fit.t_sd)
    line = ftext + htext
    
    return line
  # ---------------------------------------------------------------------------
  def plot_res_cb(self):
    self.plot_intensity(0)
    
  def plot_spec_cb(self):
    self.plot_intensity(1)
        
  # This function draws intensities onto NPDplot. iMode 0: all, iMode 1: selected
  def plot_intensity(self, iMode):
    #if iMode == 0: line_data = self.peak_list.line_data
    #else: line_data = self.peak_list.selected_line_data()
    
    line_data = self.peak_list.line_data
    
    if len(line_data) == 0:
      tkMessageBox.showerror('Error', 'No available data to plot...');      
      return
        
    heading_list = self.peak_list.heading['text'].split()[3:]
    tm_list = []
    view_list = []
    for head in heading_list:
      spec = head.split('/')[0]    
      tm = head.split('/')[1]
      view_list.append(sputil.name_to_view(spec, self.session))
      tm_list.append(float(tm))   
       
    filter_list = []
    for (fit, p, line) in self.peak_list.line_data:  
      if p.is_assigned == 0: continue # unassigned
      
      intensities = line.split()[3:]
      if len(intensities) == 0: continue
      
      # change to numbers        
      intensity_list = []
      for intensity in intensities:
        try:
          nintensity = int(float(intensity))
        except:
          nintensity = 0
        intensity_list.append(nintensity)  
        
      filter_list.append((fit,p,line,intensity_list))
      
    if len(filter_list) == 0:
      tkMessageBox.showerror('Error', 'No data to plot.')
      return            
      
    if len(filter_list) > 15 and iMode == 1:
      tkMessageBox.showerror('Error', 'Intensity analysis by spectrum is restricted by under 15 residues.')
      return      
      
    if len(intensity_list) == 0:
      tkMessageBox.showerror('Error', 'No data to plot.')
      return      

    if len(intensity_list) > 15 and iMode == 0:
      tkMessageBox.showerror('Error', 'Intensity analysis by residue is restricted by under 15 spectra.')
      return
            
    data_list = []
    
    if iMode == 0:
      # if all (iMode == 0), X: residue numbers, Y: intensities, stack of spectrum
      for i in range(len(tm_list)):
        data_list.append([tm_list[i]])  # number of spectrum
        
      for (fit, p, line, intensity_list) in filter_list:
        for i in range(len(intensity_list)):
          # data_list = [ [spec, res_id, intensity, label, res_id2, intensity2, label2], [spec2,..]...]
          data_list[i].append(p.resonances()[0].group.number)
          data_list[i].append(intensity_list[i])                  
          #data_list[i].append('[%s]%s-%f' % (str(data_list[i][0]), p.assignment, intensity_list[i]))
          data_list[i].append('[spec-%s]%s' % (str(tm_list[i]), p.assignment))
    
    elif iMode == 1:
    # else, X: spectrum, Y: intensities, stack of residues
      for (fit,p,line,intensity_list) in filter_list:
        data_list.append([p.resonances()[0].group.number])  # number of residue
        
      seq_list = data_list  
      for i in range(len(seq_list)):
        for (fit, p, line, intensity_list) in filter_list:
          if seq_list[i][0] != p.resonances()[0].group.number: continue
          
          for j in range(len(intensity_list)):
            # data_list = [ [res_id, spec, intensity, label, spec2, intensity2, label2], [res_id2,..]...]          
            data_list[i].append(tm_list[j])
            data_list[i].append(intensity_list[j])
            #data_list[j].append('[%s]%s-%f' % (p.assignment, str(data_list[j][0]), intensity_list[j]))
            data_list[i].append('[spec-%s]%s' % (str(tm_list[j]), p.assignment))                        
        
    if len(data_list) == 0:
      tkMessageBox.showerror('Error', 'No data to plot.')
      return
        
      
    # find min, max
    xmin = 99999999999
    xmax = -99999999999    
    ymin = 99999999999  
    ymax = -99999999999
    
    for data in data_list:
      for i in range(len(data)):
        if i % 3 == 1: 
          if xmin > data[i]: xmin = data[i]
          if xmax < data[i]: xmax = data[i]
        elif i % 3 == 2:
          if ymin > data[i]: ymin = data[i]
          if ymax < data[i]: ymax = data[i]
        
    # let's generate npdplot file.      
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    f = open(ini_path, 'w')
    
    f.write('[GENERAL_START]\n')

    if iMode == 0:
      f.write('TITLE=Intensity Analysis (per residue)\n')    
      f.write('XLABEL=Sequence Index\n')    
    elif iMode == 1:
      f.write('TITLE=Intensity Analysis (per spectrum)\n')        
      f.write('XLABEL=Spectrum Condition\n')          
    f.write('YLABEL=Peak Intensity\n')        
    #f.write('SEQUENCE=%s\n' % sequence)
    #f.write('FIRSTSEQ=%d\n' % iMin)
    f.write('XMIN=%f\n' % xmin)
    f.write('XMAX=%f\n' % xmax)
    f.write('YMIN=%f\n' % ymin)
    f.write('YMAX=%f\n' % ymax)
    f.write('XSCALE=FLOAT\n')    
    f.write('[GENERAL_END]\n')
    
    iSeries = 1
    for data in data_list:
      f.write('[SERIES%d_START]\n' % (iSeries))
      if iMode == 0:
        f.write('NAME=SEQ-%s\n' % (data[0]))
      else:
        f.write('NAME=SPEC-%s\n' % (data[0]))        
      f.write('PLOTTYPE=DOT\n')
      f.write('COLORCOUNT=1\n')
      f.write('DATACOUNT=%d\n' % (len(data[1:]) / 3))
      # color
      
      while True:
        r = random.randrange(0,256)
        g = random.randrange(0,256)
        b = random.randrange(0,256)                
        if r+g+b < 550: break
          
      f.write('COLOR_1=%f,%f,%f,%f,%d_%d_%d\n' % (xmin-1, xmax+1, ymin-0.1, ymax+1, r, g, b))
      # data        
      for i in range(len(data[1:]) / 3):
        x = data[1+3*i] # x
        y = data[2+3*i] # y
        z = data[3+3*i] # label
        f.write('DATA_%d=%f,%f,0,%s\n' % (i+1, x, y, z))
      f.write('[SERIES%d_END]\n' % (iSeries))
      
      iSeries = iSeries + 1
      
    f.close()
    nmrfam.run_npdplot(self.session)                  
  # ---------------------------------------------------------------------------
  # This function draws R1/R2 relaxation rates onto NPDplot
  def plot_cb2(self):                         
    self.plot_relaxation(1)
  # ---------------------------------------------------------------------------
  # This function draws T1/T2 relaxation rates onto NPDplot  
  def plot_cb(self):                           
    self.plot_relaxation(0)
  # ---------------------------------------------------------------------------    
  # 
  def plot_relaxation(self, mode):
    data_list = []
    filter_list = []    
    iMin = 999999999
    iMax = -999999999
    dMin = 99999999999
    dMax = -99999999999
    if len(self.peak_list.line_data) == 0:
      tkMessageBox.showerror('Error', 'No available data to plot...');      
      return
      
    for (fit, p, line) in self.peak_list.line_data:
      if not fit: continue # no fitting
      if p.is_assigned == 0: continue # not assigned
      #if (p.resonances()[0].atom.name != 'N') and (p.resonances()[1].atom.name != 'N'): continue # No N-H
      if (p.resonances()[0].group.symbol != '') and (len(p.resonances()[0].group.symbol) == 1):
        data_list.append((p.resonances()[0].group.symbol, p.resonances()[0].group.number, fit.t_decay, fit.t_sd, p.assignment))
      else:
        data_list.append(('X', p.resonances()[0].group.number, fit.t_decay, fit.t_sd, p.assignment))      
      if iMin > p.resonances()[0].group.number: iMin = p.resonances()[0].group.number
      if iMax < p.resonances()[0].group.number: iMax = p.resonances()[0].group.number      
      
    if iMin > iMax:
      tkMessageBox.showerror('Error', 'No available data to plot...');  
      
    # fill empty residue  
    sequence = ''
    for i in range(iMin, iMax+1):
      iFound = 0
      for (seq, seqidx, t_decay, t_sd, assgn) in data_list:
        if seqidx == i:
          iFound = 1
          filter_list.append((seq, seqidx, t_decay, t_sd, assgn))
          
          if mode == 0:     # T1/T2
            if dMax < t_decay: dMax = t_decay
            if dMin > t_decay: dMin = t_decay
          elif mode == 1:   # R1/R2
            if t_decay != 0:
              if dMax < 1.0 / t_decay: dMax = 1.0 / t_decay
              if dMin > 1.0 / t_decay: dMin = 1.0 / t_decay
          sequence = sequence + seq
          break
      if iFound == 0:
        filter_list.append(('X', i, 0, 0, 'X'))
        sequence = sequence + 'X'

    if dMax < dMin:
      dTemp = dMax
      dMax = dMin
      dMin = dTemp

    dMax = int(dMax / 10.0 + 1)*10.0
    dMin = int(dMin / 10.0)*10.0
    
    if dMax > 0 and dMin > 0: dMin = 0
    elif dMax < 0 and dMin < 0: dMax = 0
    
    if dMin == dMax:
      dMin = dMin - 1
      dMax = dMax + 1
    
    #for i in range(20):
    #  dDiv = dMax / float(pow(10,i))
    #  if dDiv < 10: break
    #dMax = float((int(dDiv)+1)) * float(pow(10,i))
    
    
    # let's generate npdplot file.      
    ini_path = os.path.join(os.path.expanduser("~"), 'ndpplot.ini')
    f = open(ini_path, 'w')
    
    f.write('[GENERAL_START]\n')
    if mode == 0:     # T1/T2        
      f.write('TITLE=T-decay Relaxation\n')
    elif mode == 1:
      f.write('TITLE=1/T-decay Relaxation\n')    
    f.write('XLABEL=Sequence Index\n')    
    if mode == 0:     # T1/T2    
      f.write('YLABEL=T-decay\n')        
    elif mode == 1:   # R1/R2
      f.write('YLABEL=1/T-decay\n')        
          
    #f.write('SEQUENCE=%s\n' % sequence)
    #f.write('FIRSTSEQ=%d\n' % iMin)
    f.write('XMIN=%d\n' % iMin)
    f.write('XMAX=%d\n' % iMax)
    f.write('YMIN=%f\n' % dMin)
    f.write('YMAX=%f\n' % dMax)
    f.write('XSCALE=INT\n')    
    f.write('[GENERAL_END]\n')
    f.write('[SERIES1_START]\n')
    f.write('NAME=T-decay Relaxation\n')
    f.write('PLOTTYPE=DOT\n')
    f.write('COLORCOUNT=2\n')
    f.write('DATACOUNT=%d\n' % len(filter_list))
    f.write('COLOR_1=%d,%d,%f,%f,NAVY\n' % (iMin, iMax, 0.0001, dMax))
    f.write('COLOR_2=%d,%d,%f,%f,255_255_255\n' % (iMin, iMax, 0.0, 0.0001))    
    
    for i in range(1, len(filter_list) + 1):
      (seq, seqidx, t_decay, t_sd, assgn) = filter_list[i-1]
      # f.write('DATA_%d=%d,%f,0,%s%d\n' % (i, seqidx, t_decay, seq,seqidx))
      if mode == 0:     # T1/T2          
        f.write('DATA_%d=%d,%f,0,%s\n' % (i, seqidx, t_decay, assgn))
      elif mode == 1:   # R1/R2
        if t_decay == 0.0:
          f.write('DATA_%d=%d,%f,0,%s\n' % (i, seqidx, 0, assgn))                    
        else:
          f.write('DATA_%d=%d,%f,0,%s\n' % (i, seqidx, 1.0/t_decay, assgn))            
      # update scroll_list
    f.write('[SERIES1_END]\n')
    f.close()
    nmrfam.run_npdplot(self.session)    
    pass    
# -----------------------------------------------------------------------------
#
class a_exp_bx_function:

  def parameter_count(self):
    return 2
  def value(self, params, x):
    a, b = params
    # Multiply overflows in fit error calculation cause core dump on DEC Alpha
    bx = pyutil.bound_value(b*x, -50, 50)
    e = math.exp(bx)
    return a * e
  def parameter_derivatives(self, params, x):
    a, b = params
    e = math.exp(b*x)
    return (e, x*a*e)

# -----------------------------------------------------------------------------
# Select spectra and time constants for fitting.
#
class relax_setup_dialog(tkutil.Settings_Dialog):

  def __init__(self, session):

    tkutil.Settings_Dialog.__init__(self, session.tk, 'Spectral Series')

    br = tkutil.button_row(self.top,
                           ('Ok', self.ok_cb),
                           ('On/Off all', self.all_on_off_cb),
                           ('Apply', self.apply_cb),
                           ('Close', self.close_cb),
                           ('Help', sputil.help_cb(session, 'RelaxFit')),
			   )
    br.frame.pack(side = 'top', anchor = 'w')
    # separator
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    e = tkutil.entry_field(self.top, 'Use ', '5', 3,
                           ' random trials for error estimates.')
    e.frame.pack(side = 'top', anchor = 'w')
    self.trials = e
    # separator
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
    headings = ('Spectrum  ', 'Time/Condition parameter')
    #st = sputil.spectrum_table(session, self.top, headings,
    st = sputil.scrollable_spectrum_table(session, self.top, headings,
                               self.add_spectrum, self.remove_spectrum)
    st.frame.pack(side = 'top', fill = 'both', expand='1', anchor = 'w')
    self.spectrum_widgets = {}

    spectra = session.project.spectrum_list()
    def time_param(s, self=self):
      return pyutil.string_to_float(self.default_time_parameter(s), 0)
    spectra = pyutil.sort_by_function_value(spectra, time_param)
    for spectrum in spectra:
      st.add_spectrum(spectrum)
      
    # make scroll                           
    #yscroll = Tkinter.Scrollbar(st.frame, orient="vertical", command = self.scroll_spectra)
    #yscroll.grid(row = 1, column = 1, sticky = 'ns')
    #self.vbar = yscroll
    ##################   


  # ---------------------------------------------------------------------------
  #
  def add_spectrum(self, spectrum, table, row):

    onoff = self.default_onoff(spectrum)
    #b = tkutil.checkbutton(table.frame, spectrum.name, onoff)
    b = tkutil.checkbutton(table.cf, spectrum.name, onoff)
    b.button.grid(row = row, column = 0, sticky = 'nw')

    ttext = self.default_time_parameter(spectrum)
    #e = tkutil.entry_field(table.frame, '', ttext)
    e = tkutil.entry_field(table.cf, '', ttext)
    e.frame.grid(row = row, column = 1, sticky = 'nw')

    self.spectrum_widgets[spectrum] = (b, e)

  # ---------------------------------------------------------------------------
  #
  def remove_spectrum(self, spectrum, table):

    b, e = self.spectrum_widgets[spectrum]
    del self.spectrum_widgets[spectrum]
    b.button.destroy()
    e.frame.destroy()
    
  # ---------------------------------------------------------------------------
  #
  def default_onoff(self, spectrum):

    return spectrum.saved_value('relaxation_time_parameter') != None
  
  # ---------------------------------------------------------------------------
  #
  def default_time_parameter(self, spectrum):

    ttext = spectrum.saved_value('relaxation_time_parameter')
    if ttext:
      return ttext
    
    match = re.search('[0-9]+', spectrum.name)
    if match:
      return match.group(0)
    
    return '0'

  # ---------------------------------------------------------------------------
  #
  def show_settings(self, settings):

    stimes = {}
    for s, t in settings['spectrum-times']:
      stimes[s] = t
      
    for s, (b, e) in self.spectrum_widgets.items():
      b.variable.set(stimes.has_key(s))
      if (stimes.has_key(s) and
          pyutil.string_to_float(e.variable.get()) != stimes[s]):
        e.variable.set('%.5g' % stimes[s])
      
    self.trials.variable.set('%d' % settings['error-estimate-trials'])

  # ---------------------------------------------------------------------------
  #
  def get_settings(self):

    trials = pyutil.string_to_int(self.trials.variable.get(), 0)
    settings = {'spectrum-times': self.spectrum_times(),
                'error-estimate-trials': trials}
    return settings
  # ---------------------------------------------------------------------------
  #
  def all_on_off_cb(self):
    if len(self.spectrum_widgets.items()) == 0:
      return
    s, (b, e) = self.spectrum_widgets.items()[0]
    st = not b.state()
    for s, (b, e) in self.spectrum_widgets.items():
      b.set_state(st)
  # ---------------------------------------------------------------------------
  #
  def spectrum_times(self):

    st = []
    for s, (b, e) in self.spectrum_widgets.items():
      if b.variable.get():
        ttext = e.variable.get()
        t = pyutil.string_to_float(ttext)
        st.append((s, t))
        s.save_value('relaxation_time_parameter', ttext)
    st.sort(self.spectrum_time_order)
    return tuple(st)

  # ---------------------------------------------------------------------------
  #
  def spectrum_time_order(self, st1, st2):

    return cmp(st1[1], st2[1]) or cmp(st1[0].name, st2[0].name)

# -----------------------------------------------------------------------------
#
def show_peak_heights(session):
  sputil.the_dialog(relaxation_dialog,session).show_peak_heights(1)
