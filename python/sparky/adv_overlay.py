# -----------------------------------------------------------------------------
# Easy overlay tool
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Nov. 7, 2019
# 
#
#
# -----------------------------------------------------------------------------

import Tkinter

import pinegraph
import sparky
import sputil
import tkutil
import tkMessageBox

# -----------------------------------------------------------------------------
#
class adv_overlay_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    self.session = session  
    tkutil.Dialog.__init__(self, session.tk, 'Easy overlay dialog')
    
    onto_view = sputil.view_menu(session, self.top, 'Onto: ')
    onto_view.frame.pack(fill = 'both', side = 'top')
    onto_view.menu.bind("<<MenuSelect>>", self.update_callback)
    self.onto_view = onto_view
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    overlaid_listbox = pinegraph.modified_listbox(self.top, 'Overlaid views: ', 25, 10, "extended")
    self.overlaid_listbox = overlaid_listbox
    overlaid_listbox.frame.pack(fill = 'both', side = 'top', expand = 1)

    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')

    br = tkutil.button_row(self.top,
			   ('Update', self.update_cb),
			   ('Apply', self.apply_cb),
			   ('Select all', self.selectall_cb),			   
			   ('Invert select', self.invertselect_cb),
			   ('^', self.moveup_cb),
			   ('v', self.movedown_cb),
			   ('Close', self.close_cb),
			   )
			   
    br.frame.pack(fill = 'both', side = 'top')   

    proj = self.session.project
    v = self.onto_view.view()    
    if proj == None or v == None:
      return
      
    self.update_cb()          

  # ---------------------------------------------------------------------------
  #
  def selectall_cb(self):
    for (view, idx) in self.overlaid_listbox.line_data:
      self.overlaid_listbox.listbox.selection_set(idx)
      self.overlaid_listbox.listbox.see(idx)
  # ---------------------------------------------------------------------------
  #
  def invertselect_cb(self):
    selected = []
    for (view, idx) in self.overlaid_listbox.selected_line_data():
      selected.append(idx)
      self.overlaid_listbox.listbox.select_clear(idx)
    for (view, idx) in self.overlaid_listbox.line_data:
      try:
        idx2 = selected.index(idx)
        continue
      except:
        self.overlaid_listbox.listbox.select_set(idx)
        self.overlaid_listbox.listbox.see(idx)
  # ---------------------------------------------------------------------------
  #
  def focus_view(self):        
    if self.session.selected_view() != None:
      self.onto_view.set(self.session.selected_view().name)
  # ---------------------------------------------------------------------------
  def moveup_cb(self):
    idx_list = self.overlaid_listbox.selected_line_numbers()
    if len(idx_list) != 1: return
    idx = idx_list[0]
    if idx > 0:
      self.overlaid_listbox.exchange(idx-1, idx)
      self.overlaid_listbox.listbox.selection_set(idx-1)
      self.overlaid_listbox.listbox.see(idx-1)

  def movedown_cb(self):
    idx_list = self.overlaid_listbox.selected_line_numbers()
    if len(idx_list) != 1: return
    idx = idx_list[0]
    if idx < len(self.overlaid_listbox.line_data)-1:
      self.overlaid_listbox.exchange(idx, idx+1)
      self.overlaid_listbox.listbox.selection_set(idx+1)
      self.overlaid_listbox.listbox.see(idx+1)
  # ---------------------------------------------------------------------------
  #
  def update_cb(self):
    self.overlaid_listbox.clear()
    # check selected onto spectrum
    proj = self.session.project
    v = self.onto_view.view()
    if proj == None or v == None:
      return
      
    # list all view
    viewlist_sort = []
    
    for view in proj.view_list():
      if v == view or v.is_top_level_window == 0: 
        continue
      viewlist_sort.append( (view.name, view) )  
      
    viewlist = sorted(viewlist_sort)

    idx = 0    
    for (viewname, view) in viewlist:  
      self.overlaid_listbox.append(view.name, (view, idx))
      if view.is_shown == 0:
        self.overlaid_listbox.listbox.itemconfig(
                self.overlaid_listbox.count()-1, 
                    {'fg':'red', 'selectforeground':'red'})

      idx = idx+1
      
    # set selection
    overlaid_views = []
    
    ol_list = proj.overlay_list()
    for ol in ol_list:
      if ol.overlay_onto != v: continue
      overlaid_views.append(ol.overlay_from)
      for (view, idx) in self.overlaid_listbox.line_data:
        if ol.overlay_from == view:
          self.overlaid_listbox.listbox.selection_set(idx)          
          self.overlaid_listbox.listbox.see(idx)
  # ---------------------------------------------------------------------------
  #
  def update_callback(self, event):
    self.update_cb()
  # ---------------------------------------------------------------------------
  #
  def apply_cb(self):
    proj = self.session.project
    v = self.onto_view.view()
    if proj == None or v == None:
      return
    
    # clear overlay
    for ol in proj.overlay_list():
      if ol.overlay_onto != v: continue
      proj.remove_overlay(ol.overlay_from, v)

    for (view, idx) in self.overlaid_listbox.selected_line_data():
      proj.add_overlay(view, v)
    
# -----------------------------------------------------------------------------
#
def show_adv_overlay(session):
  diag = sputil.the_dialog(adv_overlay_dialog,session)
  diag.focus_view()
  diag.update_cb()
  diag.show_window(1)

