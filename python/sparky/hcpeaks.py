# -----------------------------------------------------------------------------
# Create peaks on a 2D C13 HSQC spectrum for all protons attached to carbons
# where proton and carbon resonances are both assigned.
#
import Tkinter

import atoms
import pyutil
import sputil
import tkutil



arom_dict = {
  "H":(["CD2", "HD2"], ["CE1", "HE1"]),
  "F":(["CD1", "HD1"], ["CD2", "HD2"], ["CE1", "HE1"], ["CE2", "HE2"], 
       ["CZ", "HZ"]),
  "W":(["CD1", "HD1"], ["CE3", "HE3"], ["CH2", "HH2"], 
       ["CZ2", "HZ2"], ["CZ3", "HZ3"]),
  "Y":(["CD1", "HD1"], ["CD2", "HD2"], ["CE1", "HE1"], ["CE2", "HE2"])}
  
# -----------------------------------------------------------------------------
#
def is_aromatic(seq, atm):
  if 'HFWY'.find(seq) == -1: return False
  if len(atm) < 2: return False
  if 'DEHZ'.find(atm[1]) != -1: return True
  return False

# -----------------------------------------------------------------------------
#
class hc_peak_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    tkutil.Dialog.__init__(self, session.tk, 'Place HC Peaks from Resonances')

    explain = ('Create and label peaks on a 2D C13 HSQC spectrum\n' +
               'for all protons attached to carbons, if both proton\n' +
               'and carbon resonances are assigned and labeled\n' +
               'correctly.\n\nPlease use two-letter-code "dr" if you need to\n'
               +  'remove unused resonances before do this.\n')

    w = Tkinter.Label(self.top, text = explain, justify = 'left')
    w.pack(side = 'top', anchor = 'w')

    m = sputil.spectrum_menu(session, self.top, 'Spectrum: ')
    m.frame.pack(side = 'top', anchor = 'w')
    self.spectrum_menu = m
    
    opt = Tkinter.Frame(self.top, height=10, bd=0)
    opt.pack(padx=0,pady=0, anchor='w', side = 'top', expand = 1)
    self.use_mode = Tkinter.IntVar()
    self.use_mode.set(1)
    Tkinter.Radiobutton(opt, text="aliphatic", variable=self.use_mode, value=1).pack(anchor='w',side='left')
    Tkinter.Radiobutton(opt, text="aromatic", variable=self.use_mode, value=2).pack(anchor='w',side='top')

    progress_label = Tkinter.Label(self.top, anchor = 'nw')
    progress_label.pack(side = 'top', anchor = 'w')
    
    self.count_text = Tkinter.StringVar()    
    count_label = Tkinter.Label(self.top, anchor = 'nw', textvariable = self.count_text)
    count_label.pack(side = 'top', anchor = 'w')
    self.count_label = count_label

    br = tkutil.button_row(self.top,
			   ('Place peaks', self.place_cb),
			   ('Stop', self.stop_cb),
			   ('Close', self.close_cb),
                           ('Help', sputil.help_cb(session, 'HCPeaks')),
			   )
    br.frame.pack(side = 'top', anchor = 'w')

    tkutil.Stoppable.__init__(self, progress_label, br.buttons[1])

    keypress_cb = pyutil.precompose(sputil.command_keypress_cb, session)

    self.top.bind('<KeyPress>', keypress_cb)

    
  # ---------------------------------------------------------------------------
  #
  def place_cb(self):

    spectrum = self.spectrum_menu.spectrum()
    if spectrum == None:
      return

    self.stoppable_call(self.place_peaks, spectrum)
    
  # ---------------------------------------------------------------------------
  #
  def place_peaks(self, spectrum):
    
    hc_axes = pyutil.order(('1H', '13C'), spectrum.nuclei)
    if spectrum.dimension != 2 or hc_axes == None:
      self.progress_report('Spectrum must 2D with H and C axes.')
      return

    molecule = spectrum.molecule
    condition = spectrum.condition
    self.stoppable_loop('resonances', 50)

    iCount = 0
    for rH in condition.resonance_list():
      self.check_for_stop()
      if rH.atom.nucleus == '1H':
        catom = atoms.attached_heavy_atom(rH.atom, molecule)
        if catom and catom.nucleus == '13C':
          if self.use_mode == 1 and is_aromatic(rH.group.symbol, rH.atom.name):
            continue
          if self.use_mode == 2 and not is_aromatic(rH.group.symbol, rH.atom.name):
            continue
          rC = condition.find_resonance(catom)
          if rC:
            assignment = pyutil.permute((rH, rC), hc_axes)
            if not spectrum.find_peak(assignment):
              freq = pyutil.permute((rH.frequency, rC.frequency), hc_axes)
              pos = sputil.alias_onto_spectrum(freq, spectrum)
              peak = spectrum.place_peak(pos)
              peak.assign(hc_axes[0], rH.group.name, rH.atom.name)
              peak.assign(hc_axes[1], rC.group.name, rC.atom.name)
              if freq != pos:
                peak.alias = pyutil.subtract_tuples(freq, pos)
              peak.show_assignment_label()
              iCount = iCount+1
    self.count_text.set("Added: %d peak(s)" % (iCount))
  
# -----------------------------------------------------------------------------
#
def show_dialog(session):
  sputil.the_dialog(hc_peak_dialog,session).show_window(1)
