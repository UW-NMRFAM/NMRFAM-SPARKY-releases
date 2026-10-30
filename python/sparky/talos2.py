# -----------------------------------------------------------------------------
# Output XPLOR format restraint list
#
import Tkinter
import string

import noesy
import pyutil
import sputil
import tkutil

# -----------------------------------------------------------------------------
#
class talos_format_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'TALOS Format')
    self.create_ui()

  def create_ui(self):
    cm = sputil.condition_menu(self.session, self.top, 'Condition: ')
    cm.frame.pack(side = 'top', anchor = 'w')
    self.condition_menu = cm 

    sl = tkutil.scrolling_list(self.top, 'Chemical shift list', 20)
    sl.listbox['width'] = 15
    sl.frame.pack(fill = 'both', expand = 1)
    sl.listbox.bind('<ButtonRelease-1>', self.resonance_cb)
    self.shift_list = sl

    br = tkutil.button_row(self.top,
                           ('Update', self.update_cb),
                           ('Write', self.save_cs_cb),
                           ('Append', self.append_cs_cb),
                           ('Close', self.close_cb),
			   )

    br.frame.pack(side = 'top', anchor = 'w')
  # ---------------------------------------------------------------------------
  #
  def resonance_cb(self, event):
    
    r = self.shift_list.event_line_data(event)
    if r:
      self.session.show_resonance_peak_list(r)

  # ---------------------------------------------------------------------------
  #
  def update_cb(self):

    condition = self.condition_menu.condition()
    if condition == None:
      return

    self.show_chemical_shifts(condition)
  # ---------------------------------------------------------------------------
  #
  def save_cs_cb(self):
    
    path = tkutil.save_file(self.top, 'Save TALOS CS List', 'peaklist')
    if path:
      self.shift_list.write_file(path, 'w', write_heading = 0)
  # ---------------------------------------------------------------------------
  #
  def append_cs_cb(self):
    
    path = tkutil.load_file(self.top,
                            'Append TALOS CS List', 'peaklist')
    if path:
      self.shift_list.write_file(path, 'a+', write_heading = 0)
  # ---------------------------------------------------------------------------
  #
  def show_chemical_shifts(self, condition):

    reslist = condition.resonance_list()
    reslist.sort(sputil.compare_resonances)
      
    self.shift_list.clear()
    for r in reslist:
      if r.group.number != None:
        line = self.shift_line(r)
        self.shift_list.append(line, r)

  # ---------------------------------------------------------------------------
  #
  def shift_line(self, r):

    format = '%4d %1s %4s %8.3f'
    resid = r.group.number
    if resid == None:
        resid = 0

    resname = r.group.symbol
    if resname == None:
        resname = "?"

    atomname = r.atom.name
    shift = r.frequency

    values = (resid, resname, atomname, shift)

    return format % values

# -----------------------------------------------------------------------------
#
def show_dialog(session):
  d = sputil.the_dialog(talos_format_dialog, session)
  d.show_window(1)
