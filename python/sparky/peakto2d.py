# -----------------------------------------------------------------------------
# Copy peaks from one spectrum to another possibly reducing dimension.
# Only create new peaks that are sufficiently far from existing peaks.
#
import Tkinter

import axes
import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox

# -----------------------------------------------------------------------------
#
class peak_projection_dialog(tkutil.Dialog):

  # ---------------------------------------------------------------------------
  #
  def __init__(self, session):

    self.session = session
    
    tkutil.Dialog.__init__(self, session.tk, 'Peak Projection')

    self.from_spectrum = sputil.spectrum_menu(session, self.top, 'From: ')
    self.from_spectrum.frame.pack(side = 'top', anchor = 'w')

    self.to_spectrum = sputil.spectrum_menu(session, self.top, 'To: ')
    self.to_spectrum.frame.pack(side = 'top', anchor = 'w')
    self.to_spectrum.add_callback(self.chose_spectrum_cb)

    er = tkutil.entry_row(self.top, 'Minimum separation (ppm): ',
                          ('w1', '', 4), ('w2', '', 4))
    self.separation = er.variables
    er.frame.pack(side = 'top', anchor = 'w')

    self.message = Tkinter.Label(self.top, anchor = 'w')
    self.message.pack(side = 'top', fill = 'x', expand = 1)

    br = tkutil.button_row(self.top,
			   ('Ok', self.ok_cb),
			   ('Apply', self.apply_cb),
			   ('Close', self.close_cb),
			   )
    br.frame.pack(side = 'top', anchor = 'w')
  # ---------------------------------------------------------------------------
  #
  def chose_spectrum_cb(self, name):
    if self.to_spectrum.spectrum() == None:
      return
    sep = ['0.3','0.3']
    for i in range(2):
      if self.to_spectrum.spectrum().nuclei[i] == '1H':
        sep[i] = '0.03'
      self.separation[i].set(sep[i])

  # ---------------------------------------------------------------------------
  #
  def apply_cb(self):

    from_spect = self.from_spectrum.spectrum()
    to_spect = self.to_spectrum.spectrum()
    axes_list = self.axis_map(from_spect, to_spect)

    if axes_list == None:
      return
    
    w1_sep, w2_sep = tkutil.float_variable_values(self.separation)
    cluster = pyutil.cluster((w1_sep, w2_sep))

    for peak in to_spect.peak_list():
      cluster.add_point(peak.frequency, peak)

    a1, a2 = axes_list
    peaks = []
    for peak in from_spect.peak_list():
      freq = (peak.frequency[a1], peak.frequency[a2])
      if not cluster.has_nearby_point(freq):
        p = to_spect.place_peak(freq)
        p.note = 'from ' + from_spect.name
        cluster.add_point(freq, p)
        peaks.append(p)

    if peaks:
      self.session.unselect_all_ornaments()
    for peak in peaks:
      peak.selected = 1

    self.message['text'] = 'Created %d peaks' % len(peaks)

  # ---------------------------------------------------------------------------
  #
  def axis_map(self, from_spect, to_spect):

    if from_spect == None or to_spect == None or to_spect.dimension != 2:
      return None

    axes_list = []
    for nucleus in to_spect.nuclei:
      a = axes.unique_nucleus_axis(from_spect, nucleus)
      if a == None:
        self.message['text'] = "Can't map %s axis" % nucleus
        return None
      axes_list.append(a)

    return axes_list

# -----------------------------------------------------------------------------
#
def show_dialog(session):
  sputil.the_dialog(peak_projection_dialog,session).show_window(1)

class transfer_peaks(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'Transfer/assign peaks')

    self.sp2 = sputil.spectrum_menu(session, self.top, 'To: ')
    self.sp2.frame.pack(side = 'top', anchor = 'w')
    self.sp2.menu.bind("<<MenuSelect>>", self.update_axis)

    self.sp = sputil.spectrum_menu(session, self.top, 'From: ')
    self.sp.frame.pack(side = 'top', anchor = 'w')
    self.sp.menu.bind("<<MenuSelect>>", self.update_axis)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="x", padx=5,pady=5, side = 'top')

    # option_menu- w1, w2, w3, current plane, do not use
    self.axisfrm = Tkinter.Frame(self.top)
    self.axisfrm.pack(fill="both", side = 'top', expand = 0)
    self.wfrm = list(map(lambda x: Tkinter.Frame(self.axisfrm), range(4)))
    self.wom = list(map(lambda x: tkutil.option_menu(self.wfrm[x], '', []), 
                                                  range(4)))
    self.update_axis()

    # only selected?
    self.onlyselected = Tkinter.IntVar()
    self.onlyselected.set(1)
    self.use_onlyselected_cb = Tkinter.Checkbutton(self.top, \
        text = 'Use selected peaks only.', variable = self.onlyselected, \
        onvalue=1, offvalue = 0)
    self.use_onlyselected_cb.pack(side = 'top', anchor = 'w', expand = 0)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
    # buttons
    br = tkutil.button_row(self.top,
          ('Transfer', self.transfer_cb),
          ('Assign', self.assign_cb),
          ('Stop', self.stop_cb),
      )
    br.frame.pack(side = 'top', anchor = 'w')

    # separator    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    # tolerances        
    tol_frame = Tkinter.Frame(self.top)
    tol_frame.pack(side = 'top', fill='both')
       
    self.ntol = tkutil.entry_field(tol_frame, 'N tol.:', initial = 0.200, width = 5)
    self.ntol.frame.grid(row = 0, column=0)     
    self.ntol_ppm = self.ntol.variable
          
    self.ctol = tkutil.entry_field(tol_frame, ', C tol.:', initial = 0.200, width = 5)
    self.ctol.frame.grid(row = 0, column=2)
    self.ctol_ppm = self.ctol.variable     
         
    self.htol = tkutil.entry_field(tol_frame, ', H tol.:', initial = 0.020, width = 5)
    self.htol.frame.grid(row=0, column=4)    
    self.htol_ppm = self.htol.variable

    progress_label = Tkinter.Label(self.top, anchor = 'nw')
    progress_label.pack(side = 'top', anchor = 'w')
    tkutil.Stoppable.__init__(self, progress_label, br.buttons[2])
  # ---------------------------------------------------------------------------
  #
  def update_axis(self, event=None):
    spec2 = self.sp2.spectrum()
    spec = self.sp.spectrum()

    for i in range(4): 
      self.wfrm[i].forget() # clear first
      self.wom[i].frame.forget()
    if spec == None or spec2 == None: return
    axis_list = self.make_axis_list(spec)
    for i in range(spec2.dimension):
      wtitle = 'w%d (%s) <- ' % (i+1, spec2.nuclei[i])
      self.wom[i].__init__(self.wfrm[i], wtitle, axis_list)
      self.wfrm[i].pack(side = 'top', anchor = 'w')
      self.wom[i].frame.pack(side = 'top', anchor = 'w')

  # ---------------------------------------------------------------------------
  #
  def make_axis_list(self, spec):
    axis_list = []
    for i in range(spec.dimension):
      lbl = 'w%d (%s)' % (i+1, spec.nuclei[i])
      axis_list.append(lbl)
    axis_list.append('Current Z-plane')
    axis_list.append('Current A-plane')
    axis_list.append('Do not use')
    return axis_list
  # ---------------------------------------------------------------------------
  #
  def transfer_cb(self):
    self.transfer_or_assign(0)
    self.progress_report('')
  def assign_cb(self):
    self.transfer_or_assign(1)
    self.progress_report('')

  # ---------------------------------------------------------------------------
  # mode 0: transfer, 1: assign
  def transfer_or_assign(self, mode):
    spec2 = self.sp2.spectrum()
    spec = self.sp.spectrum()

    v2 = self.session.selected_view()
    if spec == None or spec2 == None: return
    match_list = []
    for i in range(spec2.dimension):
      match_list.append(self.wom[i].get())
    if 'Current Z-plane' in match_list or 'Current A-plane' in match_list:
      if self.session.selected_spectrum() != spec2:
        tkMessageBox.showerror('Error', 
          'Selected spectrum does not match with the "To:" spectrum.')
        return

    # check nuclei
    for i in range(spec2.dimension):
      if match_list[i] in ['Current A-plane', 'Current Z-plane', 'Do not use']:
        continue
      if match_list[i].find(spec2.nuclei[i]) == -1:
        tkMessageBox.showerror('Error', 
          'Nucleus does not match (%s != %s).' % \
            (self.wom[i].label['text'], match_list[i]))
        return

    if self.onlyselected.get() == 1:
      peaks = spec.selected_peaks()
    else:
      peaks = spec.peak_list()
    
    # mapper: -1: do not use, 0, 1, 2, 3: XYZA, >10: Current plane in XYZA
    match_idx = []
    for match in match_list:
      if match == 'Do not use':
        match_idx.append(-1)
        continue
      elif match == 'Current Z-plane': # get Z from v2 + 10
        match_idx.append(v2.axis_order[2] + 10)
        continue
      elif match == 'Current A-plane': # get A from v2 + 20
        match_idx.append(v2.axis_order[3] + 20)
        continue
      else:
        match_idx.append(int(match[1])-1)

    tol_dict = {'1H': float(self.htol_ppm.get()),
                '13C': float(self.ctol_ppm.get()),
                '15N': float(self.ntol_ppm.get())}

    v2c = v2.center                
    for j in range(len(peaks)):
      self.progress_report( '%d / %d' % (j+1, len(peaks)) )
      peak = peaks[j]
      peakpos = list(map(lambda x: None, range(spec2.dimension)))
      albl = list(map(lambda x: None, range(spec2.dimension)))
      # build peak position
      for i in range(len(match_idx)):
        idx = match_idx[i]
        if idx == -1: continue
        if idx < 10:
          peakpos[i] = peak.frequency[idx]
          albl[i] = peak.resonances()[idx]
        elif idx < 20: # Z
          peakpos[i] = v2c[v2.axis_order[2]]
        else: # A
          peakpos[i] = v2c[v2.axis_order[3]]

      # check if peak is deficient
      if None in peakpos:
        tkMessageBox.showerror('Error', 
          'Peak positions cannot be projected. Check your settings.')
        return

      # find matching peak
      found_peaks = sputil.find_peak_by_position(spec2, peakpos, tol_dict)
      # place a peak
      if mode == 0:
        if len(found_peaks) == 0: 
          pk = sputil.place_peak_in_spectral_region(spec2, peakpos)
          if pk != None:
            for i in range(len(albl)):
              try:
                if albl[i] != None:
                  pk.assign(i, albl.group, albl.atom)
              except:
                continue
            pk.show_assignment_label()
        continue

      if mode == 1 and len(found_peaks) == 0: continue
      # assign a peak
      resn = peak.resonances()
      for fpeak in found_peaks:
        if fpeak.is_assigned == 0: continue
        for i in range(spec2.dimension):
          if not match_idx[i] in [0, 1, 2, 3]: continue
          if resn[i] != None:
            fpeak.assign(match_idx[i], resn[i].group, resn[i].atom)
        fpeak.show_assignment_label()

def show_transfer_peak_dialog(session):
  sputil.the_dialog(transfer_peaks,session).show_window(1)
