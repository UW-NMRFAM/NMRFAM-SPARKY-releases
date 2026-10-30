# -----------------------------------------------------------------------------
# New View List
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Jan 16, 2020 - in progress
#
#
# -----------------------------------------------------------------------------
# CITATION:
#          TBA
# -----------------------------------------------------------------------------

import Tkinter
import sparky
import tkutil
import sputil

# Original setting is like this:
# View Molecule Condition Nuclei Data Size Peaks Assignments
# Show Hide Close Help
#return formatted_string("%1s %s %10.10s %10.10s %12s %14s %8d %8d",
#			  (view->shown() ? "+" : "-"),
#			  view->name().cstring(),
#			  sp->molecule()->name().cstring(),
#			  sp->condition()->name().cstring(),
#			  nucleus_types(sp).cstring(),
#			  spectrum_dimensions(sp).cstring(),
#			  sp->crosspeaks().size(),
#			  assigned_peaks(sp));
class viewlist_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'Filterable View List')
    topfrm = Tkinter.Frame(self.top)
    topfrm.pack(side='top', fill = 'both', expand = 1)
    self.spec_width = 16
    self.sl = tkutil.scrolling_list(topfrm, '-', 5, xscrollbar=True)
    self.sl.listbox.bind('<Double-Button-1>', self.rev_state_cb)
    self.sl.listbox.bind('<Button-3>', self.view_setting_cb)
    self.sl.listbox.bind('<Button-2>', self.spec_setting_cb)
    self.sl.listbox['selectmode'] = 'extended'
    self.sl.frame.pack(side='top', fill = 'both', expand = 1)
    self.filter = tkutil.entry_field(self.top, 'Filter by: ', width=10)
    self.filter.entry.bind('<Return>', self.update_cb)
    self.filter.frame.pack(side='top', fill = 'x', expand = 0)
    self.sort_mode = 0
    self.update_list()

    session.notify_me('removed spectrum from project', self.update_list_cb)
    session.notify_me('added spectrum to project', self.update_list_cb)


    self.br = tkutil.button_row(self.top,
			   ('Update', self.update_cb),
         ('Show', self.show_cb),
         ('Hide', self.hide_cb),
         ('Order', self.order_cb),
         ('View Setting', self.view_setting2_cb),
         ('Spec Setting', self.spec_setting2_cb),
         ('<-->', self.expand_cb),
         ('>--<', self.shrink_cb),
         ('Close', self.close_cb),)
    self.br.frame.pack(side = 'top', anchor = 'w', expand = 0)

  def update_list_cb(self, event):
    self.update_list()
  def shrink_cb(self):
    self.spec_width = max(4, self.spec_width-1)
    self.update_list()
  def expand_cb(self):
    self.spec_width = min(60, self.spec_width+1)
    self.update_list()
  def order_cb(self):
    self.sort_mode += 1
    self.update_list()
  def show_cb(self):
    self.set_visibility(1)

  def hide_cb(self):
    self.set_visibility(0)

  def set_visibility(self, visibility_mode):
    data_list = self.sl.selected_line_data()
    if len(data_list) < 1: return
    for data in data_list:
      try:
        data[1].is_shown = visibility_mode
      except:
        pass
    self.update_list()
    # rehighlight and focus
    idx, idx2 = -1, -1
    for data in data_list:
      try:
        idx = self.sl.line_data.index(data)
        self.sl.listbox.selection_set(idx)
        if idx2 == -1: idx2 = idx
      except:
        pass
      if idx2 != -1:
        self.sl.listbox.see(idx2)

  def update_cb(self, event=None):
    self.update_list()
  def update_list(self):
    self.sl.clear()
    self.sort_mode = self.sort_mode % 3

    # header
    vh = '{name:{fill}<{width}}'.format(name='View', fill=' ',
                      width=self.spec_width)
    header = '%1s %s %10.10s %10.10s %12s %14s %8s %s' % (
      '*', vh, 'Molecule', 'Condition', 'Nuclei', 'Data Size',
      'Peaks', 'Assignments')
    self.sl.heading['text'] = header
    self.sl.heading['font'] = ('Courier', 10)
    self.sl.listbox['font'] = ('Courier', 10)
    filter = self.filter.variable.get()
    filterup = filter.upper()

    # views
    view_list = []

    for v in self.session.project.view_list():
      if v.is_top_level_window == 0: continue
      view_list.append([v.name, v])

    if self.sort_mode == 0:
      sort_list = view_list
    elif self.sort_mode == 1:
      sort_list = sorted(view_list, key=lambda x: x[0], reverse=False)
    elif self.sort_mode == 2:
      sort_list = sorted(view_list, key=lambda x: x[0], reverse=True)

    for itm in sort_list:
      v = itm[1]
      if v.is_shown == 0: vis = '-'
      else: vis = '+'
      sp = v.spectrum
      mn = sp.molecule.name
      cn = sp.condition.name
      nc = ''
      for nuc in sp.nuclei: nc += nuc + ' '
      nc = nc.rstrip()
      ds = ''
      for das in sp.data_size: ds += ('%d ' % (das))
      ds = ds.rstrip()
      pl = sp.peak_list()
      pn = len(pl)
      an = 0
      for peak in pl:
        if peak.is_assigned == 1: an += 1
      vn = '{name:{fill}<{width}}'.format(name=v.name, fill=' ',
                      width=self.spec_width)
      if len(vn) > self.spec_width: vn = vn[0:self.spec_width]
      line = '%1s %s %10.10s %10.10s %12s %14s %8d %8d' % (
        vis, vn, mn, cn, nc, ds, pn, an)
      lineup = line.upper()
      if lineup.find(filterup) == -1: continue
      self.sl.append(line, [line, v])
      if line[0] == '-':
        self.sl.listbox.itemconfig(self.sl.count()-1, {'fg':'red',
                                        'selectforeground':'red'})


  def set_focus(self, v):
    for i in range(len(self.sl.line_data)):
      if self.sl.line_data[i][1] == v:
        self.sl.listbox.select_set(i)
        break

  def rev_state_cb(self, event):
    data_list = self.sl.selected_line_data()
    if len(data_list) != 1: return
    #try:
    v = data_list[0][1]
    v.is_shown = (v.is_shown + 1) % 2
    bSuccess = True
    #except:
    #  bSuccess = False
    self.update_list()
    # refocus
    if bSuccess:
      for i in range(len(self.sl.line_data)):
        if self.sl.line_data[i][1] == v:
          self.sl.listbox.selection_set(i)
          self.sl.listbox.see(i)
          break

  def view_setting2_cb(self):
    data_list = self.sl.selected_line_data()
    if len(data_list) != 1: return
    v = data_list[0][1]
    if v.is_shown == 0: return
    tkutil.tk_call(self.session.tk, 'focus', v.frame)
    v.got_focus()
    self.session.command_characters('vt')

  def view_setting_cb(self, event):
    self.view_setting2_cb()
  
  def spec_setting2_cb(self):
    data_list = self.sl.selected_line_data()
    if len(data_list) != 1: return
    v = data_list[0][1]
    if v.spectrum == None: return
    tkutil.tk_call(self.session.tk, 'focus', v.frame)
    v.got_focus()
    self.session.command_characters('st')

  def spec_setting_cb(self, event):
    self.spec_setting2_cb()

def show_viewlist_dialog(session):
  sputil.the_dialog(viewlist_dialog, session).show_window(1)
