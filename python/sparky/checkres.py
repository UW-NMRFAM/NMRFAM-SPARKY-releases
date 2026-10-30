# -----------------------------------------------------------------------------
# Eiso's resonance deviation checker
#
# Added to NMRFAM-SPARKY Oct 12, 2016 (by Woonghee Lee)
#
#
# -----------------------------------------------------------------------------
# Read PDB file atom coordinates
#
import os
import string
import types

import atomnames
import atoms
import noesy
import pyutil
import sputil
import tkutil

# 
# -----------------------------------------------------------------------------
# Show Sparky resonances without corresponding pdb atoms
#
class res_dialog(tkutil.Dialog):

  def __init__(self, session):

    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'Resonance Deviation Check')

    cm = sputil.condition_menu(session, self.top, 'Condition: ')
    cm.frame.pack(side = 'top', anchor = 'w')
    self.condition_menu = cm

    #pf = tkutil.file_field(self.top, 'PDB File: ', 'pdb')
    #pf.frame.pack(side = 'top', anchor = 'w')
    #self.pdb_path = pf

    er = tkutil.entry_row(self.top, 'PPM tolerance: ',
                       ('13C', '.1', 4), ('15N', '.1', 4), ('1H', '.01', 4))
    self.ppm_range = er.variables
    self.w3_range_widget = er.entries[2].frame
    er.frame.pack(side = 'top', anchor = 'w')

    al = tkutil.scrolling_list(self.top, 'Resonances with large deviation', 5)
    al.frame.pack(fill = 'both', expand = 1)
    al.listbox.bind('<ButtonRelease-1>', self.select_resonance_cb)
    #al.listbox.bind('<ButtonRelease-2>', self.goto_peak_or_assignment_cb)
    #al.listbox.bind('<Double-ButtonRelease-1>', self.goto_peak_or_assignment_cb)
    self.atom_list = al

    br = tkutil.button_row(self.top,
                           ('Update', self.update_cb),
                           ('Close', self.close_cb),
                           ('Help', sputil.help_cb(session, 'CheckRes')),
                           )
    br.frame.pack(side = 'top', anchor = 'w')
    
  # ---------------------------------------------------------------------------
  #
  def select_resonance_cb(self, event):

    resonance = self.atom_list.event_line_data(event)
    print resonance
    if type(resonance) == types.InstanceType:
      print 'selected',resonance
      self.session.show_resonance_peak_list(resonance)

  # ---------------------------------------------------------------------------
  #
  def select_assignment_cb(self, event):

    r = self.peak_list.event_line_data(event)
    print type(pora)
    print pora
    print dir(pora)
    #if type(pora) == types.InstanceType:
    #  sputil.select_peak(pora)
    #elif type(pora) == types.TupleType or type(pora) == types.ListType:
    #  sputil.select_peak(self.settings.spectrum.find_peak(pora))

  # ---------------------------------------------------------------------------
  #
  def update_cb(self):

    #pdb_path = self.pdb_path.get()
    cond = self.condition_menu.condition()
    #mod = model(self.session, pdb_path)
    if cond:
      mol = cond.molecule
      self.atom_list.clear()
      rlist = []
      for r in cond.resonance_list():
        a = r.atom
        n = r.atom.nucleus
        d = r.deviation
        (dppmC,dppmN,dppmH)=tkutil.float_variable_values(self.ppm_range)
        
        #print rr        
        if a.nucleus == '13C' and d>dppmC:
          rlist.append(r)
        elif a.nucleus == '15N' and d>dppmN:
          rlist.append(r)
        elif a.nucleus == '1H' and d>dppmH:
          rlist.append(r)
      rlist.sort(sputil.compare_atoms)
      for r in rlist:
        a=r.atom
        line = '%5s %5s %8.3f %5.3f' % (a.group.name, a.name, r.frequency,r.deviation)
        self.atom_list.append(line,r)
      heading = '%d resonances with deviation higher than tolerance' % len(rlist)
      heading = heading+'\nGroup  Atom     Freq   Dev'
      self.atom_list.heading['text'] = heading

    
# -----------------------------------------------------------------------------
#
def show_res_dialog(session):
  d = sputil.the_dialog(res_dialog, session)
  d.show_window(1)
