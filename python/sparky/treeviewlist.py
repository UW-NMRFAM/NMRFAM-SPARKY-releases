# -----------------------------------------------------------------------------
# Tree View List
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
import sputil
import tkutil
import tkFont


# hierarchical order
# (session- project) molecule- condition
#  2D/3D/4D NMR- Spectrum- View 
#  Resonances

class treeviewlist_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'Tree View')
    # buttons & filter
    topfrm = Tkinter.Frame(self.top)
    topfrm.pack(side='top', fill = 'both', expand = 0)
    # treeview
    btmfrm = Tkinter.Frame(self.top)
    btmfrm.pack(side='bottom', fill = 'both', expand = 1)

    # Update, Show/Hide, Settings... Close
    self.br = tkutil.button_row(topfrm,
			   ('Update', self.update_cb),
         #('Fold', self.hide_cb),
         #('Unfold', self.show_cb),
         ('Show', self.show_cb),
         ('Hide', self.hide_cb),
         ('Settings...', self.setting_cb),
         #('Close', self.close_cb),
         )
    self.br.frame.pack(side = 'top', anchor = 'w', expand = 0)
    self.filter = tkutil.entry_field(topfrm, 'Molecule/condition: ', width=10)
    self.filter.entry.bind('<Return>', self.update_cb)
    self.filter.frame.pack(side='top', fill = 'x', expand = 1)


    # treeview. we will use scrolling list to mimic
    tmp_fntfam = tkFont.families()
    tree = tkutil.scrolling_list(btmfrm, '* Right-click to show setting window.', 
                                10, True)
    tree.listbox['selectmode'] =  'single'
    tree.frame.pack(side='top', fill = 'both', expand = 1)
    tree.listbox.bind('<Double-Button-1>', self.rev_state_cb) # show/hide
    tree.listbox.bind('<Button-1>', self.select_cb)
    tree.listbox.bind('<Button-2>', self.ctsetting2_cb)
    tree.listbox.bind('<Button-3>', self.setting2_cb)
    self.tree = tree

    suggested_fonts = ['Arial', 'NotoSans', 'Ubuntu', 'SegoeUI', 'Helvetica', 
                      'Calibri', 'Verdana', 'DejaVuSans', 'FreeSans']
    for fnt in suggested_fonts:
      if fnt in tmp_fntfam:
        tree.listbox['font'] = (fnt, 10)
        tree.heading['font'] = (fnt, 10)
        break

    self.update_tree()
    tree.listbox['height'] = min(max(len(tree.line_data), 5), 30)

    session.notify_me('removed spectrum from project', self.update_tree_cb)
    session.notify_me('added spectrum to project', self.update_tree_cb)
  
  def update_tree_cb(self, event):
    self.update_tree()
  def update_cb(self, event=None):
    self.update_tree()
  def update_tree(self):
    # (session- project) molecule- condition
    #  2D/3D/4D NMR- Spectrum- View 
    #  Resonances
    t = self.tree
    s = self.session
    p = s.project
    t.clear()
    if p == None: return

    # get molecules
    mol_list = p.molecule_list()
    mol_list.sort(key=lambda x: x.name, reverse=False)
    # get conditions
    cond_list = p.condition_list()
    cond_list.sort(key=lambda x: x.name, reverse=False)
    # get spectra
    spec_list = p.spectrum_list()
    spec_list.sort(key=lambda x: x.name, reverse=False)
    # get views
    view_list = p.view_list()
    view_list.sort(key=lambda x: x.name, reverse=False)

    filter = self.filter.variable.get()
    filterup = filter.upper()

    for mol in mol_list:
      name = mol.name
      molname = name
      if name == '': name = '- (undefined molecule)'
      else: name = '- ' + name
      # type, name, self, parent, visible
      t.append(name, ['mol', name, mol, p, True]) 
      curline = t.count()
      for cond in cond_list:
        if not cond in mol.condition_list(): continue
        name = cond.name
        condname = name
        if condname.find(filterup) == -1 and molname.find(filterup) == -1: 
          continue
        if name == '': name = ' ' * 4 + '- (undefined condition)'
        else: name = ' ' * 4 + '- ' + name
        t.append(name, ['con', name, cond, mol, True])
        num = [0, 0, 0]
        for dim in [2, 3, 4]:
          name = ' ' * 8 + '- %dD Spectrum/View(s)' % (dim)
          t.append(name, ['sep', name, None, cond, True])
          for spec in spec_list:
            if spec.dimension != dim: continue
            if spec.condition != cond or spec.molecule != mol: continue
            name = ' ' * 12 + '- ' + spec.name
            t.append(name, ['spe', name, spec, cond, True])
            num[dim-2] += 1
            for view in view_list:
              if view.spectrum != spec: continue
              if view.is_top_level_window != 1: continue
              if view.is_shown == 1:
                name = ' ' * 16 + '+ ' + view.name
              else:
                name = ' ' * 16 + '- ' + view.name
              t.append(name, ['vie', name, view, spec, True])
              if view.is_shown == 0:
                t.listbox.itemconfig(t.count()-1, {'fg':'red',
                                        'selectforeground':'red'})

          if num[dim-2] == 0: t.delete_by_number(t.count()-1)
        if sum(num) == 0: t.delete_by_number(t.count()-1)  
      if curline == t.count(): t.delete_by_number(t.count()-1)
      
  def rev_state_cb(self, event):
    # mol, con, spe, vie
    # type, name, self, parent, visibility
    data_list = self.tree.selected_line_data()
    if len(data_list) < 1: return
    idx = self.tree.selected_line_numbers()[0]
    if data_list[0][0] == 'vie': 
      v = data_list[0][2]
      v.is_shown = (v.is_shown + 1) % 2
      self.update_tree()
      self.tree.listbox.selection_set(idx)
      self.tree.listbox.see(idx)
      return
    #if data_list[0][1].strip()[0] == '+': self.hide_cb()
    #else: self.show_cb()

  def setting2_cb(self, event):
    self.setting_cb()

  def ctsetting2_cb(self, event):
    self.ctsetting_cb()

  def get_child_views(self):
    data_list = self.tree.selected_line_data()
    if len(data_list) < 1: return [], None
    idx = self.tree.selected_line_numbers()[0]
    mode_list = ['mol', 'con', 'sep', 'spe', 'vie']
    view_list = []
    try:
      curmode_idx = mode_list.index(data_list[0][0])
    except:
      return [], idx
    for i in range(idx, len(self.tree.line_data)):
      mode = self.tree.line_data[i][0]
      try:
        mode_idx = mode_list.index(mode)
      except:
        break
      if mode_idx == 4: # view
        view_list.append(self.tree.line_data[i][2])
      if mode_idx == curmode_idx:
        if i != idx or mode_idx == 4: break
    return view_list, idx

  def showhide(self, visibility):
    view_list, idx = self.get_child_views()
    if idx == None: return
    for v in view_list:
      v.is_shown = visibility
    self.update_tree()
    self.tree.listbox.selection_set(idx)
    self.tree.listbox.see(idx)
  # fold
  def hide_cb(self):
    self.showhide(0)
    pass

  # unfold
  def show_cb(self):
    self.showhide(1)
    pass

  def select_cb(self, event):
    # selected view???
    pass

  def ctsetting_cb(self):
    data_list = self.tree.selected_line_data()
    if len(data_list) < 1: return
    if data_list[0][0] == 'vie':
      v = data_list[0][2]
      if v.is_shown == 0: return
      tkutil.tk_call(self.session.tk, 'focus', v.frame)
      v.got_focus()
      self.session.command_characters('ct')

  def setting_cb(self):
    data_list = self.tree.selected_line_data()
    if len(data_list) < 1: return
    idx = self.tree.selected_line_numbers()[0]
    if data_list[0][0] == 'vie':
      v = data_list[0][2]
      if v.is_shown == 0: return
      tkutil.tk_call(self.session.tk, 'focus', v.frame)
      v.got_focus()
      self.session.command_characters('vt')
      return
    if data_list[0][0] == 'spe':
      dt = self.tree.line_data[idx+1]
      if dt[0] == 'vie':
        v = dt[2]
        tkutil.tk_call(self.session.tk, 'focus', v.frame)
        v.got_focus()
        self.session.command_characters('st')
        return
    pass
def show_treeviewlist_dialog(session):
  sputil.the_dialog(treeviewlist_dialog, session).show_window(1)
