# ----------------------------------------------------------------------------
# Sparky utility routines and classes
#

import pyutil
import re
import string
import sys
import Tkinter
import tkutil
import types

import sparky

# ----------------------------------------------------------------------------
#
def spectra_for_peaks(peaks):
  return pyutil.unique_attribute_values(peaks, 'spectrum')

# ----------------------------------------------------------------------------
#
def selected_condition(session):
  s = session.selected_spectrum()
  if s:
    return s.condition
  return None

# ----------------------------------------------------------------------------
# If an assignment along an axis has the same group as the previous axis
# then the group name is not shown.
#
def assignment_name(resonances):
  a = ''
  last_group = None
  for r in resonances:
    if r:
      if r.group == last_group:
	a = a + r.atom.name + '-'
      else:
	a = a + r.name + '-'
      last_group = r.group
    else:
      a = a + '?-'
  return a[:-1]

# -----------------------------------------------------------------------------
# Are all axes unassigned?
#
def is_peak_unassigned(peak):
  for r in peak.resonances():
    if r != None:
      return 0
  return 1

# -----------------------------------------------------------------------------
#
def unassign_spectrum(spectrum):
  for p in spectrum.peak_list():
    rlist = p.resonances()
    for axis in range(spectrum.dimension):
      if rlist[axis]:
        p.assign(axis, '', '')

# -----------------------------------------------------------------------------
#
def assignment_range(assignment):

  gmin = None
  gmax = None
  for r in assignment:
    g = r.group.number
    if g != None:
      if gmin == None or g < gmin: gmin = g
      if gmax == None or g > gmax: gmax = g

  if gmin == None:
    return None

  return gmax - gmin

# -----------------------------------------------------------------------------
#
def molecule_group_atom_list(molecule):
  group_atom_list = []
  for a in molecule.atom_list():
    group_atom_list.append((a.group.name, a.name))
  return group_atom_list

# -----------------------------------------------------------------------------
#
def resonance_group_atom(r):
  return (r.group.name, r.atom.name)

# -----------------------------------------------------------------------------
#
def group_atom_assignment(res):
  return tuple(map(resonance_group_atom, res))

# -----------------------------------------------------------------------------
# Assignment is tuple of (group name, atom name) pairs
#
def group_atom_assignment_name(assignment):
  text = ''
  for group, atom in assignment:
    text = text + group + atom + '-'
  return text[:-1]

# -----------------------------------------------------------------------------
# Assignment is tuple of (group name, atom name) pairs
#
def group_atom_resonances(condition, assignment):
  molecule = condition.molecule
  res = []
  for group_atom in assignment:
    r = group_atom_resonance(group_atom, condition)
    if r == None:
      return None
    res.append(r)
  return res

# -----------------------------------------------------------------------------
#
def group_atom_resonance(group_atom, condition):
  return apply(condition.find_resonance, group_atom)

# -----------------------------------------------------------------------------
#
def number_group_atom(ga):
  return (group_number(ga[0]),) + ga

# -----------------------------------------------------------------------------
#
def group_number(g):
  if g:
    s = re.search('[0-9]+', g)
    if s:
      return string.atoi(s.group())
  return None

# -----------------------------------------------------------------------------
#
def compare_groups(g1, g2):
  return cmp(g1.number, g2.number) or cmp(g1.name, g2.name)

# -----------------------------------------------------------------------------
#
def compare_atoms(a1, a2):
  return compare_groups(a1.group, a2.group) or cmp(a1.name, a2.name)

# -----------------------------------------------------------------------------
#
def compare_resonances(r1, r2):
  return compare_groups(r1.group, r2.group) or cmp(r1.atom.name, r2.atom.name)

# -----------------------------------------------------------------------------
#
def sort_peaks_by_assignment(peaks, stoppable):
  return tkutil.stoppable_sort_by_key(peaks, assignment_sort_key, stoppable)

# -----------------------------------------------------------------------------
# Return assignment as ((residue #, residue symbol, atom name), ...)
# for sorting.
#
def assignment_sort_key(peak):
  a = []
  for r in peak.resonances():
    if r == None:
      a.append(None)
    else:
      a.append((r.group.number, r.group.symbol, r.atom.name))
  return tuple(a)

# -----------------------------------------------------------------------------
#
def parse_group_name(g):
  s = re.search('[0-9]+', g)
  if s:
    return g[:s.start()], string.atoi(s.group())
  return g, None
# -----------------------------------------------------------------------------
# this parses chain identifier, too
def parse_group_name_chain(g):
  s = re.search('[0-9]+', g)
  if s:
    return g[:s.start()], string.atoi(s.group()), g[s.end():]
  return g, None, None
# ---------------------------------------------------------------------------
# Parse assignment of form g1a1-g2a2 to get ((g1, a1), (g2, a2))
# Or g1a1-a2 to get ((g1, a1), (g1, a2))
# A '?' component is translated to ('', '')
#
def parse_assignment(assignment):
  res = assignment.split('-')
  assignment = []
  last_group = None
  for s in res:
    ga = split_group_atom(s)
    if ga == None:
      if last_group:  ga = (last_group, s)
      else:           return None
    assignment.append(ga)
    last_group = ga[0]
  return tuple(assignment)

# this makes assignment label to have full group name name and numbers
def complete_assignment(assignment):
  tup = parse_assignment(assignment)
  lbl = ''
  for g, a in tup:
    if g != '': lbl += g
    else: lbl += '?'
    if a != '': lbl += a
    elif g != '': lbl += '?'
    lbl += '-'
  return lbl[:-1]
# ---------------------------------------------------------------------------
# parse group number and symbol as well
#
def parse_assignment_entirely(assignment):
  pa = parse_assignment(assignment)  # ((g1, a1), (g2, a2))
  if pa == None: return None
  assignment = []
  for s in pa:
    ga = parse_group_name(s[0])
    if len(s) > 1:  assignment.append((ga[0], ga[1], s[1]))
    else:           assignment.append((ga[0], ga[1], ''))
  return tuple(assignment)
# ---------------------------------------------------------------------------
def parse_assignment_chain_entirely(assignment):
  pa = parse_assignment(assignment)  # ((g1, a1), (g2, a2))
  if pa == None: return None
  assignment = []
  for s in pa:
    ga = parse_group_name_chain(s[0])
    if len(s) > 1:  assignment.append((ga[0], ga[1], ga[2], s[1]))
    else:           assignment.append((ga[0], ga[1], ga[2], ''))
  return tuple(assignment)
# -----------------------------------------------------------------------------
# Skip to first digit, then skip to first H|C|N to find start of atom name.
#
def split_group_atom(group_atom):
  s = re.search('[0-9]', group_atom)
  if s:
    first_digit = s.start()
    s = re.search('[hHcCnNqQmM]', group_atom[first_digit:])
    if s:
      HCNQM_offset = s.start()
      d = first_digit + HCNQM_offset
      return (group_atom[:d], group_atom[d:])
  if group_atom == '?':
    return ('', '')
  return None
# -----------------------------------------------------------------------------
# Skip to first digit, then skip to first H|C|N to find start of atom name.
# This is modified version by Woonghee.
def split_group_atom2(group_atom):
  s = re.search('[0-9]', group_atom)
  if s:
    first_digit = s.start()
    s = re.search('[hHcCnNqQmM]', group_atom[first_digit:])
    if s:
      HCNQM_offset = s.start()
      d = first_digit + HCNQM_offset
      return (group_atom[:d], group_atom[d:])
    else:
      HCNQM_offset = 0
      d = first_digit + HCNQM_offset
      return (group_atom[:d], group_atom[d:])      
  if group_atom == '?':
    return ('', '')
  return None

# ----------------------------------------------------------------------------
#
def is_complete_assignment(resonances):
  for r in resonances:
    if r == None:
      return 0
  return 1

# -----------------------------------------------------------------------------
#
def selected_peak(session):
  peaks = session.selected_peaks()
  if len(peaks) == 0:
    session.stdout.write('selected_peak(): 0 peaks selected.\n')
  elif len(peaks) > 1:
    session.stdout.write('selected_peak(): 2 or more peaks selected.\n')
  else:
    return peaks[0]
  return None

# -----------------------------------------------------------------------------
#
def show_peak(peak):
  if peak:
    show_spectrum_position(peak.spectrum, peak.position)

# -----------------------------------------------------------------------------
#
def show_spectrum_position(spectrum, pos):
  v = preferred_view(spectrum)
  if v:
    v.center = pos
    v.set_crosshair_position(pos)
    tk = v.session.tk
    tkutil.raise_named_widget(tk, v.frame)

# -----------------------------------------------------------------------------
#
def select_peak(peak):

  if peak:
    peak.spectrum.session.unselect_all_ornaments()
    peak.selected = 1
# -----------------------------------------------------------------------------
# tolerances should be dictionary '15N', '13C', '1H'
# return will be a list of tuples, [(peak1, dist1), ...]
def find_peak_by_position(spec, position, tolerances):
  peaks = spec.peak_list()
  found_peaks = []
  tol_list = []
  for nucleus in spec.nuclei:
    tol_list.append(tolerances[nucleus])
  
  for peak in peaks:
    dist = 0
    for i in range(spec.dimension):
      dist += abs(peak.frequency[i] - position[i]) / tol_list[i]
    if dist > 3: continue
    found_peaks.append((peak, dist))

  # sort by euclidean distance
  sort_list = sorted(found_peaks, key=lambda x: x[1])
  return sort_list
# -----------------------------------------------------------------------------
#
def peak_height(peak):

  h = peak.data_height
  if h == None:
    # peak group
    h = 0
    for p in peak.peaklets():
      h += p.data_height

  return h

# -----------------------------------------------------------------------------
#
def select_assignment(assignment, spectrum):

  if assignment and spectrum:
    select_peak(spectrum.find_peak(assignment))

# -----------------------------------------------------------------------------
#
def show_assignment(assignment, spectrum):

  if assignment and spectrum:
    peak = spectrum.find_peak(assignment)
    if peak:
      show_peak(peak)
    else:
      pos = assignment_position(assignment, spectrum)
      show_spectrum_position(spectrum, pos)

# -----------------------------------------------------------------------------
# Alias assignment frequency onto spectrum.
#
def assignment_position(assignment, spectrum):

  freq = pyutil.attribute_values(assignment, 'frequency')
  return alias_onto_spectrum(freq, spectrum)

# -----------------------------------------------------------------------------
# Alias frequency onto spectrum returning the position.
# If the frequency is on the spectrum then the returned position
# exactly equals the specified frequency.
#
def alias_onto_spectrum(freq, spectrum):
  
  region = spectrum.region
  pos = []
  for a in range(len(freq)):
    swidth = spectrum.sweep_width[a]
    max_ppm = region[1][a]
    min_ppm = max_ppm - swidth
    f = freq[a]
    if f >= min_ppm and f <= max_ppm:
      p = f
    else:
      p = min_ppm + (f - min_ppm) % swidth
    pos.append(p)
  return tuple(pos)

# -----------------------------------------------------------------------------
# Alias frequency onto spectrum.
# If the frequency is on the spectrum then the returned position
# exactly equals the specified frequency.
#
def alias_axis_onto_spectrum(freq, axis, spectrum):
  
  region = spectrum.region
  swidth = spectrum.sweep_width[axis]
  max_ppm = region[1][axis]
  min_ppm = max_ppm - swidth
  if freq >= min_ppm and freq <= max_ppm:
    return freq
  return min_ppm + (freq - min_ppm) % swidth

# -----------------------------------------------------------------------------
#
def closest_peak(freq, peak_list, ranges):

  min_offset = None
  closest = None
  for p in peak_list:
    peak_freq = p.frequency
    offset = 0
    for axis in range(len(freq)):
      offset = offset + abs(peak_freq[axis] - freq[axis]) / ranges[axis]
    if min_offset == None or offset < min_offset:
      min_offset = offset
      closest = p
  return closest

# -----------------------------------------------------------------------------
# 
def resonance_offset_string(frequency, resonances):
  offset = ''
  for a in range(len(frequency)):
    r = resonances[a]
    if r:
      offset = offset + ' %7.4f' % (frequency[a] - r.frequency)
    else:
      offset = offset + ' %7s' % ''
  return offset

# -----------------------------------------------------------------------------
#
def preferred_view(spectrum):

  session = spectrum.session
  v = session.selected_view()
  if v and v.spectrum == spectrum and v.is_top_level_window:
    return v
  vlist = session.project.view_list()
  vlist = filter(lambda v, s=spectrum:
                 v.spectrum == s and v.is_top_level_window,
                 vlist)
  for v in vlist:
    if v.is_shown:
      return v
  if vlist:
    return vlist[0]
  return None

# -----------------------------------------------------------------------------
#
def hydrogen_atoms(molecule):
  atoms = molecule.atom_list()
  protons = []
  for atom in atoms:
    if atom.name[0] in 'HMQ':
      protons.append(atom)
  return protons

# -----------------------------------------------------------------------------
#
def inter_residue_peaks(peaks, axis1, axis2):

  inter = []
  for peak in peaks:
    r = peak.resonances()
    r1 = r[axis1]
    r2 = r[axis2]
    if r1 and r2:
      n1 = r1.group.number
      n2 = r2.group.number
      if n1 != None and n2 != None and n1 != n2:
	inter.append(peak)
  return inter

# ----------------------------------------------------------------------------
# Create an option menu listing spectra in the current project.
#
class spectrum_menu(tkutil.option_menu):

  def __init__(self, session, parent, label, allow_no_choice = 0):

    self.session = session
    self.allow_no_choice = allow_no_choice
    self.names = self.spectrum_names()
    tkutil.option_menu.__init__(self, parent, label,
                                self.names, self.default_spectrum_name())
    self.menu['postcommand'] = self.update_menu_cb

  # --------------------------------------------------------------------------
  #
  def spectrum_names(self):

    spectra = self.session.project.spectrum_list()
    names = pyutil.attribute_values(spectra, 'name')
    if self.allow_no_choice:
      names = ('',) + names
    return names

  # --------------------------------------------------------------------------
  #
  def default_spectrum_name(self):

    return pyutil.attribute(self.session.selected_spectrum(), 'name', '')

  # --------------------------------------------------------------------------
  #
  def update_menu_cb(self):

    current_names = self.spectrum_names()
    if current_names != self.names:
      self.names = current_names
      self.remove_all_entries()
      for name in self.names:
        self.add_entry(name)
      if not self.get() in self.names:
        self.set(self.default_spectrum_name())

  # --------------------------------------------------------------------------
  #
  def spectrum(self):

    return name_to_spectrum(self.get(), self.session)

# ----------------------------------------------------------------------------
#
def name_to_spectrum(name, session):

  slist = session.project.spectrum_list()
  for s in slist:
    if s.name == name:
      return s
  return None
    
# ----------------------------------------------------------------------------
# Create an option menu listing views in the current project.
#
class view_menu(tkutil.option_menu):

  def __init__(self, session, parent, label):

    self.session = session
    self.names = self.view_names()
    tkutil.option_menu.__init__(self, parent, label,
                                self.names, self.default_view_name())
    self.menu['postcommand'] = self.update_menu_cb

  # --------------------------------------------------------------------------
  #
  def view_names(self):

    views = self.session.project.view_list()
    return pyutil.attribute_values(views, 'name')

  # --------------------------------------------------------------------------
  #
  def default_view_name(self):

    return pyutil.attribute(self.session.selected_view(), 'name', '')

  # --------------------------------------------------------------------------
  #
  def update_menu_cb(self):

    current_names = self.view_names()
    if current_names != self.names:
      self.names = current_names
      self.remove_all_entries()
      for name in self.names:
        self.add_entry(name)
      if not self.get() in self.names:
        self.set(self.default_view_name())

  # --------------------------------------------------------------------------
  #
  def view(self):

    return name_to_view(self.get(), self.session)

# ----------------------------------------------------------------------------
#
def name_to_view(name, session):

  vlist = session.project.view_list()
  for v in vlist:
    if v.name == name:
      return v
  return None

# ----------------------------------------------------------------------------
# Used for color coding spectra.  Provides the same colors for spectra to
# all extensions that want to color code (eg spin graphs and strip plots).
#
def spectrum_color(spectrum):

  if not hasattr(spectrum, 'key_color'):

    spectrum_colors = ('green', 'blue', 'red', 'cyan',
                       'magenta', 'yellow', 'orange',
                       'brown', 'gold', 'pink', 'purple')

    session = spectrum.session
    if not hasattr(session, 'next_spectrum_color'):
      session.next_spectrum_color = 0

    spectrum.key_color = spectrum_colors[session.next_spectrum_color]
    ncolor = len(spectrum_colors)
    session.next_spectrum_color = (session.next_spectrum_color + 1) % ncolor
    
  return spectrum.key_color

# ----------------------------------------------------------------------------
# Make a scrollable table of spectra, one spectrum per row.
# Callback routines create the widgets for each row.
#
class scrollable_spectrum_table:

  def __init__(self, session, parent, headings,
               add_spectrum_cb, remove_spectrum_cb):

    f = Tkinter.Frame(parent, borderwidth = 5)
    self.frame = f
    
    self.c = Tkinter.Canvas(f)
    self.c.pack(side='left')    
    
    self.scrollbar = Tkinter.Scrollbar(f, command=self.c.yview)
    self.scrollbar.pack(side='left', fill='y')
    
    self.c.config(yscrollcommand=self.scrollbar.set)
    self.c.bind('<Configure>', self.on_configure)
    
    self.cf = Tkinter.Frame(self.c)
    self.c.create_window((0,0), window=self.cf, anchor='nw')
    self.cf.pack(expand='y',fill='y')
        
    
    for h in range(len(headings)):
      lbl = Tkinter.Label(self.cf, text = headings[h])
      #lbl = Tkinter.Label(self.cf, text = headings[h])
      lbl.grid(row = 0, column = h)

    if headings:
      self.next_row = 1
    else:
      self.next_row = 0

    self.add_spectrum_cb = add_spectrum_cb
    self.remove_spectrum_cb = remove_spectrum_cb

    self.session = session
    
    rn = session.notify_me('removed spectrum from project',
                           self.remove_spectrum)
    an = session.notify_me('added spectrum to project', self.add_spectrum)
    self.notices = (rn, an)
    f.bind('<Destroy>', self.window_destroyed_cb, 1)

  # --------------------------------------------------------------------------
  #
  def on_configure(self, event):
    self.c.config(scrollregion=self.c.bbox("all"))          
    
  # --------------------------------------------------------------------------
  #
  def add_spectrum(self, spectrum):

    row = self.next_row
    self.next_row = row + 1
    self.add_spectrum_cb(spectrum, self, row)
    
  # --------------------------------------------------------------------------
  #
  def remove_spectrum(self, spectrum):

    self.remove_spectrum_cb(spectrum, self)

  # ---------------------------------------------------------------------------
  #
  def window_destroyed_cb(self, event):

    if str(event.widget) == str(self.frame):
      if sparky.object_exists(self.session):
        for notice in self.notices:
          self.session.dont_notify_me(notice)
      self.notices = ()
      
# ----------------------------------------------------------------------------
# Make a table of spectra, one spectrum per row.
# Callback routines create the widgets for each row.
#
class spectrum_table:

  def __init__(self, session, parent, headings,
               add_spectrum_cb, remove_spectrum_cb):

    f = Tkinter.Frame(parent, borderwidth = 5)
    self.frame = f
    
    #self.c = Tkinter.Canvas(f)
    #self.cf = Tkinter.Frame(self.c) 
    #self.cf.pack(fill="y")
    
    for h in range(len(headings)):
      lbl = Tkinter.Label(f, text = headings[h])
      #lbl = Tkinter.Label(self.cf, text = headings[h])
      lbl.grid(row = 0, column = h)

    if headings:
      self.next_row = 1
    else:
      self.next_row = 0

    self.add_spectrum_cb = add_spectrum_cb
    self.remove_spectrum_cb = remove_spectrum_cb

    self.session = session
    
    rn = session.notify_me('removed spectrum from project',
                           self.remove_spectrum)
    an = session.notify_me('added spectrum to project', self.add_spectrum)
    self.notices = (rn, an)
    f.bind('<Destroy>', self.window_destroyed_cb, 1)
    
  # --------------------------------------------------------------------------
  #
  def add_spectrum(self, spectrum):

    row = self.next_row
    self.next_row = row + 1
    self.add_spectrum_cb(spectrum, self, row)
    
  # --------------------------------------------------------------------------
  #
  def remove_spectrum(self, spectrum):

    self.remove_spectrum_cb(spectrum, self)

  # ---------------------------------------------------------------------------
  #
  def window_destroyed_cb(self, event):

    if str(event.widget) == str(self.frame):
      if sparky.object_exists(self.session):
        for notice in self.notices:
          self.session.dont_notify_me(notice)
      self.notices = ()

# ----------------------------------------------------------------------------
# A single column of spectrum checkbuttons.
#
class spectrum_checkbuttons(spectrum_table):
  
  def __init__(self, session, parent, heading):

    if heading:
      headings = (heading,)
    else:
      headings = ()

    spectrum_table.__init__(self, session, parent, headings,
                            self.add_spect, self.remove_spect)
    self.spectrum_to_checkbutton = {}
    self.chosen_spectra = []

    spectra = session.project.spectrum_list()
    for spectrum in spectra:
      self.add_spectrum(spectrum)

  # ---------------------------------------------------------------------------
  #
  def add_spect(self, spectrum, table, row):
    
    #
    # Make spectrum checkbutton
    #
    cb = tkutil.checkbutton(table.frame, spectrum.name, 0)
    cb.button['selectcolor'] = spectrum_color(spectrum)
    choose_cb = pyutil.precompose(choose_spectrum_cb, spectrum,
                                  table.chosen_spectra)
    cb.add_callback(choose_cb)
    cb.button.grid(row = row, column = 0, sticky = 'w')
    table.spectrum_to_checkbutton[spectrum] = cb

  # ---------------------------------------------------------------------------
  #
  def remove_spect(self, spectrum, table):

    if not table.spectrum_to_checkbutton.has_key(spectrum):
      return
    
    cb = table.spectrum_to_checkbutton[spectrum]
    cb.set_state(0)
    cb.button.destroy()
    del table.spectrum_to_checkbutton[spectrum]

# -----------------------------------------------------------------------------
#
def choose_spectrum_cb(name, names, chosen):

  if chosen:
    if not name in names:
      names.append(name)
  else:
    if name in names:
      names.remove(name)

# ----------------------------------------------------------------------------
# Create an option menu listing conditions.
#
class condition_menu(tkutil.option_menu):

  def __init__(self, session, parent, label):

    self.session = session
    self.names = self.condition_names()
    tkutil.option_menu.__init__(self, parent, label, self.names,
                                self.selected_condition_name())
    self.menu['postcommand'] = self.update_menu_cb

  # --------------------------------------------------------------------------
  #
  def update_menu_cb(self):

    current_names = self.condition_names()
    if current_names != self.names:
      self.names = current_names
      self.remove_all_entries()
      for name in self.names:
        self.add_entry(name)
      if not self.get() in self.names:
        self.set(self.selected_condition_name())

  # --------------------------------------------------------------------------
  #
  def selected_condition_name(self):

    return condition_full_name(selected_condition(self.session))

  # --------------------------------------------------------------------------
  #
  def condition_names(self):

    return map(condition_full_name, self.session.project.condition_list())

  # --------------------------------------------------------------------------
  #
  def condition(self):

    return name_to_condition(self.get(), self.session)
  
# ----------------------------------------------------------------------------
#
def name_to_condition(name, session):

  clist = session.project.condition_list()
  for c in clist:
    if condition_full_name(c) == name:
      return c
  return None

# ----------------------------------------------------------------------------
#
def condition_full_name(c):
  if c and (c.name or c.molecule.name):
    return c.molecule.name + ' / ' + c.name
  return ''

# ---------------------------------------------------------------------------
#
class peak_listbox(tkutil.scrolling_list):

  def __init__(self, parent):

    tkutil.scrolling_list.__init__(self, parent, '', 5)

  # ---------------------------------------------------------------------------
  #
  def select_peak_cb(self, event):
    select_peak(self.event_peak(event))

  # ---------------------------------------------------------------------------
  #
  def goto_peak_cb(self, event):
    show_peak(self.event_peak(event))

  # ---------------------------------------------------------------------------
  #
  def event_peak(self, event):
    return self.event_line_data(event)

# ---------------------------------------------------------------------------
#
class assignment_listbox(tkutil.scrolling_list):

  def __init__(self, session, parent):

    self.session = session
    tkutil.scrolling_list.__init__(self, parent, '', 5)

  # ---------------------------------------------------------------------------
  #
  def select_assignment_cb(self, event):
    a = self.event_assignment(event)
    s = self.session.selected_spectrum()
    if a and s:
      select_peak(s.find_peak(a))

  # ---------------------------------------------------------------------------
  #
  def goto_assignment_cb(self, event):
    a = self.event_assignment(event)
    show_assignment(a, self.session.selected_spectrum())

  # ---------------------------------------------------------------------------
  #
  def event_assignment(self, event):
    return self.event_line_data(event)

# -----------------------------------------------------------------------------
#
def cluster_peaks(peaks, axis1, range1, axis2, range2):

  c = pyutil.cluster((range1, range2))
  for peak in peaks:
    p = (peak.frequency[axis1], peak.frequency[axis2])
    c.add_point(p, peak)

  return c.clusters()

# -----------------------------------------------------------------------------
# Process pymol like residue ranges
#
def process_pymol_residue_range(value):
  # parse by ",", "+" and "-"
  residues = []
  value2 = value.strip()
  while True:
    value3 = value2.replace(' ','+')
    value4 = value3.replace(',','+')
    value5 = value4.replace('++','+')
    if value5 == value2: break
    value2 = value5
  try:
    chunks = value2.split('+')
    for chunk in chunks:
      chunks2 = chunk.split('-')
      if len(chunks2) > 2:  a = int('error') # intensional error
      elif len(chunks2) == 2:
        a = min(int(chunks2[0]), int(chunks2[1]))
        b = max(int(chunks2[0]), int(chunks2[1]))
        for i in range(a, b+1):
          residues.append(i)
      else:
        residues.append(int(chunks2[0]))
  except:
    return (False, [])
  
  return (True, sorted(list(set(residues))))
# -----------------------------------------------------------------------------  
def shift_by_resonance(session, resid, atom_name, conditions=[]):
  if len(conditions) == 0:
    cond_list = session.project.condition_list()
  else:
    cond_list = []
    for cond in session.project.condition_list():
      if cond.name in conditions:
        cond_list.append(cond)
  shift_list = []
  for cond in cond_list:
    for resn in cond.resonance_list():
      if resn.group.number == resid and resn.atom.name == atom_name:
        shift_list.append(resn.frequency)
  if len(shift_list) == 0: return None
  return sum(shift_list) / float(len(shift_list))
# -----------------------------------------------------------------------------
# Check if a peak frequency is inside spectral region.
def peak_in_spectral_region(spec, peak):
  if len(peak) != len(spec.region[0]):
    return False # not a same dimension size
  for i in range(len(peak)):
    if spec.region[0][i] > peak[i] or spec.region[1][i] < peak[i]:
      return False
  return True
def place_peak_in_spectral_region(spec, peak):
  if not peak_in_spectral_region(spec, peak):
    return None
  return spec.place_peak(peak)
# -----------------------------------------------------------------------------
# Center by manually typed chemical shifts
#
def center_by_shifts(session):
  import tkSimpleDialog
  import tkMessageBox
  selected_view = session.selected_view()
  if selected_view == None: return
  cur_shift = ''
  for ppm in selected_view.center:
    cur_shift = cur_shift + '%.3f, ' % (ppm)
  cur_shift = cur_shift[:-2]
  bnd = ''
  min_ppms = selected_view.spectrum.region[0]
  max_ppms = selected_view.spectrum.region[1]
  for i in range(len(min_ppms)):
    bnd = bnd + '%.3f-%.3f, ' % (min_ppms[i], max_ppms[i])
  bnd = bnd[:-2]
  shifts = tkSimpleDialog.askstring('Center by shifts or label (e.g. K15N-H))', \
          'Current: %s; boundary: %s' % (cur_shift, bnd), \
          initialvalue = cur_shift)
  shs = shifts.strip().split(',')
  ppms = []

  # check if this is assignment label
  if len(shs) == 1:
    asgn = parse_assignment_entirely(shifts)
    if asgn == None:
      return
    if len(asgn) != selected_view.spectrum.dimension: return
    for i in range(len(asgn)):
      rsn = asgn[i]
      ppm = shift_by_resonance(session, rsn[1], rsn[2])
      if ppm != None: 
        ppms.append(ppm)
      else:
        ppms.append(selected_view.center[i])
  else:
    for i in range(len(shs)):
      try:
        sh = float(shs[i])
      except:
        sh = selected_view.center[i]
      ppms.append(sh)

  selected_view.center = tuple(ppms)
  selected_view.set_crosshair_position(tuple(ppms))
  tk = selected_view.session.tk
  tkutil.raise_named_widget(tk, selected_view.frame)
# -----------------------------------------------------------------------------
# Draw a horizontal line in the selected view
#
def draw_horz_line_on_selected_view(session):
  v = session.selected_view()
  if v == None: return
  sp = v.spectrum
  c = v.center
  c1, c2 = list(c), list(c)
  r, x = sp.region, v.axis_order[0]
  c1[x], c2[x] = r[0][x], r[1][x]
  line = sparky.Line(sp, tuple(c1), tuple(c2))
  line.color = 'white'
  line.selected = 0
# -----------------------------------------------------------------------------
# Draw a horizontal line in the selected view
#
def draw_vert_line_on_selected_view(session):
  v = session.selected_view()
  if v == None: return
  sp = v.spectrum
  c = v.center
  r = v.region
  c1, c2 = list(c), list(c)
  r, y = sp.region, v.axis_order[1]
  c1[y], c2[y] = r[0][y], r[1][y]
  line = sparky.Line(sp, tuple(c1), tuple(c2))
  line.color = 'white'
  line.selected = 0

# -----------------------------------------------------------------------------
# Currently doesn't handle function key events.
#
def command_keypress_cb(session, event):

  session.command_characters(event.char)

# -----------------------------------------------------------------------------
#
def the_dialog(dialog_class, session):

  if not hasattr(session, 'dialogs'):
    session.dialogs = {}
  dialog_table = session.dialogs
    
  if (not dialog_table.has_key(dialog_class) or
      dialog_table[dialog_class].is_window_destroyed()):
    dialog_table[dialog_class] = dialog_class(session)

  return dialog_table[dialog_class]
  
# -----------------------------------------------------------------------------
# Return a function to be used as a help button callback.
#
def help_cb(session, extension_topic):

  manual_url = 'extensions.html#' + extension_topic
  def show_url(url = manual_url, session = session):
    session.show_manual_url(url)
  return show_url
