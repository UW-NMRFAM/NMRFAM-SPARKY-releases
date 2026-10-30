# #################################################################
# Output XPLOR/CYANA/PONDEROSA format restraint list
#
###################################################################
#
#  Updated Nov. 22, 2017 by Woonghee Lee (whlee@nmrfam.wisc.edu)
#
#  Support for PONDEROSA/CYANA restraints
#
###################################################################

import Tkinter
import string

import noesy
import pyutil
import sputil
import tkutil
import myseq

# -----------------------------------------------------------------------------
#
class xplor_format_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    tkutil.Dialog.__init__(self, session.tk, 'XPLOR/CYANA/PONDEROSA Restraints')

    sc = sputil.spectrum_menu(session, self.top, 'Spectrum: ')
    sc.frame.pack(side = 'top', anchor = 'w')
    self.spectrum_choice = sc
    
    self.restraint_mode = 0 # 0: Xplor, 1: CYANA/PONDEROSA

    pl = sputil.peak_listbox(self.top)
    pl.frame.pack(fill = 'both', expand = 1)
    pl.heading['text'] = 'Restraint list'
    pl.listbox.bind('<ButtonRelease-1>', pl.select_peak_cb)
    pl.listbox.bind('<ButtonRelease-2>', pl.goto_peak_cb)
    pl.listbox.bind('<Double-ButtonRelease-1>', pl.goto_peak_cb)
    self.peak_list = pl

    bt = tkutil.entry_field(self.top, 'Bounds text (e.g. 5.5 4.0 0.0 or 5.5) ', width = 15)
    bt.frame.pack(side = 'top', anchor = 'w')
    self.bounds_text = bt

    nb = tkutil.checkbutton(self.top, 'Show peak notes?', 0)
    nb.button.pack(side = 'top', anchor = 'w')
    self.note = nb
    
    ns = tkutil.checkbutton(self.top, 'Omit sequential peaks?', 0)
    ns.button.pack(side = 'top', anchor = 'w')
    self.sequential = ns

    hb = tkutil.entry_row(self.top, 'Only peaks with height',
                          (' >= ', '', 8), (' and < ', '', 8))
    hb.frame.pack(side = 'top', anchor = 'w')
    self.height_min, self.height_max = hb.variables

    vb = tkutil.entry_row(self.top, 'Only peaks with volume',
                          (' >= ', '', 8), (' and < ', '', 8))
    vb.frame.pack(side = 'top', anchor = 'w')
    self.volume_min, self.volume_max = vb.variables

    eh1 = Tkinter.Label(self.top, text = 'Omit peak if note has a word from:')
    eh1.pack(side = 'top', anchor = 'w')
    ef1 = tkutil.entry_field(self.top, '  ', width = 30)
    ef1.frame.pack(side = 'top', anchor = 'w')
    self.exclude_note_words = ef1
    
    eh2 = Tkinter.Label(self.top, text = 'or if it has no word from:')
    eh2.pack(side = 'top', anchor = 'w')
    ef2 = tkutil.entry_field(self.top, '  ', width = 30)
    ef2.frame.pack(side = 'top', anchor = 'w')
    self.require_note_words = ef2
    
    et = Tkinter.Label(self.top, text = '(space separated list of words)')
    et.pack(side = 'top', anchor = 'w')
    
    
    progress_label = Tkinter.Label(self.top, anchor = 'nw')
    progress_label.pack(side = 'top', anchor = 'w')

    br = tkutil.button_row(self.top,
                           ('Update(Xplor)', self.update_cb),
                           ('Update(Cyana/Ponderosa)', self.update2_cb),                           
                           ('Write Restraints', self.save_peaks_cb),
			   )
    br.frame.pack(side = 'top', anchor = 'w')
    br2 = tkutil.button_row(self.top,
                           ('Append', self.append_peaks_cb),
			                     ('Close', self.close_cb),
                           ('Stop', self.stop_cb),                           			                     
                           ('Help', sputil.help_cb(session, 'XplorFormat')),
			   )
    br2.frame.pack(side = 'top', anchor = 'w')    

    tkutil.Stoppable.__init__(self, progress_label, br2.buttons[2])
  # ---------------------------------------------------------------------------
  #
  def update_shared(self):
    spectrum = self.spectrum_choice.spectrum()
    if spectrum == None:
      return
    
    show_note = self.note.state()
    bounds_text = self.bounds_text.variable.get()
    hmin = pyutil.string_to_float(self.height_min.get())
    hmax = pyutil.string_to_float(self.height_max.get())
    vmin = pyutil.string_to_float(self.volume_min.get())
    vmax = pyutil.string_to_float(self.volume_max.get())
    exclude_note_words = string.split(self.exclude_note_words.variable.get())
    exculde_note_words = filter(lambda w: len(w) > 0, exclude_note_words)
    require_note_words = string.split(self.require_note_words.variable.get())
    require_note_words = filter(lambda w: len(w) > 0, require_note_words)

    peaks = sputil.sort_peaks_by_assignment(spectrum.peak_list(), self)
    self.stoppable_call(self.show_peaks, peaks, show_note,
                        hmin, hmax, vmin, vmax,
                        exclude_note_words, require_note_words,
                        bounds_text)  
  # ---------------------------------------------------------------------------
  #
  def update_cb(self):
    self.restraint_mode = 0
    self.update_shared()
                        
  # ---------------------------------------------------------------------------
  #
  def update2_cb(self):
    self.restraint_mode = 1
    self.update_shared()
        
  # ---------------------------------------------------------------------------
  #
  def save_peaks_cb(self):
    
    path = tkutil.save_file(self.top, 'Save Restraint List', 'peaklist')
    if path:
      self.peak_list.write_file(path, 'w', write_heading = 0)

  # ---------------------------------------------------------------------------
  #
  def append_peaks_cb(self):
    
    path = tkutil.load_file(self.top,
                            'Append Restraint List', 'peaklist')
    if path:
      self.peak_list.write_file(path, 'a+', write_heading = 0)

  # ---------------------------------------------------------------------------
  #
  def show_peaks(self, peaks, show_note,
                 ht_min, ht_max, vol_min, vol_max,
                 exclude_note_words, require_note_words, bounds_text):

    self.peak_list.clear()
    
    self.stoppable_loop('peaks', 100)
    
    for peak in peaks:
      self.check_for_stop()
      show = (peak.is_assigned and
              (ht_min == None or sputil.peak_height(peak) >= ht_min) and
              (ht_max == None or sputil.peak_height(peak) < ht_max) and
              (vol_min == None or
               (peak.volume != None and peak.volume >= vol_min)) and
              (vol_max == None or
               (peak.volume != None and peak.volume < vol_max)) and
              (not exclude_note_words or
               not pyutil.string_contains_word(peak.note, exclude_note_words))
              and 
              (not require_note_words or
               pyutil.string_contains_word(peak.note, require_note_words))
              )
      if show:
        line = self.peak_line(peak, bounds_text)
        if line:
          self.peak_list.append(line, peak)
          if show_note and peak.note:
            note = '{%s}' % peak.note
            self.peak_list.append(note, peak)

  # ---------------------------------------------------------------------------
  #
  def peak_line(self, peak, bounds_text):

    r1, r2 = noesy.proton_resonances(peak)

    if r1 == None or r2 == None:
      return None

    if r1.group == None or r2.group == None:
      return None
      
    if r1.atom == None or r2.atom == None:
      return None
            
    if r1.group.number == None or r2.group.number == None:
      return None
      
    if r1.atom.name == None or r2.atom.name == None:
      return None
      
    use_sequential = self.sequential.state()
    if use_sequential != 0:
      if abs(r1.group.number-r2.group.number) < 2:
        return None
      
    aaa = myseq.a2aaa(r1.group.symbol)
    aaa2 = myseq.a2aaa(r2.group.symbol)    
    
    if (r1.atom.name.find("_s") > 1) or (r2.atom.name.find("_s") > 1): # skip simulated peaks
      return None
      
    # skip diagonals
    if (r1.group.name == r2.group.name) and (r1.atom.name == r2.atom.name):
      return None

    if self.restraint_mode == 0:
      line = ('assign (residue %d and name %s) (residue %d and name %s) %s'
            % (r1.group.number, r1.atom.name,
               r2.group.number, r2.atom.name,
               bounds_text))
    else:
      if (aaa == 'X') or (aaa2 == 'X'):
        return None
      line = ('%5d %4s %5s %5d %4s %5s %s'
            % (r1.group.number, aaa, r1.atom.name,
               r2.group.number, aaa2, r2.atom.name,
               bounds_text))
                       
    return line

# -----------------------------------------------------------------------------
#
def show_dialog(session):
  d = sputil.the_dialog(xplor_format_dialog, session)
  d.show_window(1)
