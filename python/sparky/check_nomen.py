# -----------------------------------------------------------------------------
# Check assignment nomenclature
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: November 18, 2015
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
# Check assignment nomenclature with BMRB naming convention
# -----------------------------------------------------------------------------
#
import string
import Tkinter

import sparky
import sputil
import tkutil
import pinegraph
import atomnames

# -----------------------------------------------------------------------------
#
class show_check_protein_nomen_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Check protein nomenclature')
    
    self.session = session

    # List box
    ll = pinegraph.modified_listbox(self.top, 'Non-BMRB assignments', 52, 8, "single")
    ll.listbox.bind('<ButtonRelease-1>', self.select_peak_cb)
    ll.listbox.bind('<ButtonRelease-2>', self.move_to_selected_cb)
    ll.listbox.bind('<Double-ButtonRelease-1>', self.move_to_selected_cb)
    ll.listbox.bind('<ButtonRelease-3>', self.move_to_selected_cb)
    self.label_list = ll
    self.label_list.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    # Parsed assignment
    lbl= Tkinter.Label(self.top, text = 'Selected peak:')
    lbl.pack(side = 'top', anchor = 'w')
    
    f = Tkinter.Frame(self.top)
    f.pack(side = 'top', anchor = 'w')

    self.group_list = []
    self.atom_list = []
        
    col = 0
    for axis in ['w1','w2','w3']:
      lbl = Tkinter.Label(f, text = axis)
      lbl.grid(row=0, column=col*3, sticky = 'w')
      e = tkutil.entry_field(f, '', '', 6)      
      e.frame.grid(row=0, column = col*3+1, sticky = 'w')      
      self.group_list.append(e)
      e = tkutil.entry_field(f, '', '', 6)            
      e.frame.grid(row=0, column = col*3+2, sticky = 'w')            
      self.atom_list.append(e)      
      col = col + 1

    # Buttons
    self.br = tkutil.button_row(self.top,
			   ('Update', self.update_cb),
			   ('Assign', self.assign_cb),			   
			   ('Unassign', self.unassign_cb),
			   ('HX1/2 -> HX2/3', self.hx1_3_cb),			   
			   ('HX1/2 -> HX2/3 (All)', self.hx1_3_all_cb),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')
    
    if self.session.project != None:
      self.update_cb()
         
    # dr!!!! 
  # ---------------------------------------------------------------------------
  #    
  def clear_boxes(self):
    for atoms in self.atom_list:
      atoms.variable.set('')
    for groups in self.group_list:
      groups.variable.set('')      
  # ---------------------------------------------------------------------------
  #    
  def select_peak_cb(self, event):
    self.session.unselect_all_ornaments()
    self.clear_boxes()
    
    pitem = self.label_list.event_line_data(event)
    if pitem == None:
        return
            
    pitem[1].selected = 1
    for i in range(len(pitem[1].resonances())):
      res = pitem[1].resonances()[i]
      self.group_list[i].variable.set(res.group.name)
      self.atom_list[i].variable.set(res.atom.name)
      if pitem[2][i] == 0:
        self.group_list[i].entry.configure(fg="red")
        self.atom_list[i].entry.configure(fg="red")        
      else:
        self.group_list[i].entry.configure(fg="black")
        self.atom_list[i].entry.configure(fg="black")        
           
  # ---------------------------------------------------------------------------
  #    
  def move_to_selected_cb(self, event):
    pitem = self.label_list.event_line_data(event)
    if pitem == None:
        return
        
    sputil.show_peak(pitem[1])

  # ---------------------------------------------------------------------------
  #
  def update_cb(self):
    self.label_list.clear()  
    self.clear_boxes()
    # find wrong assignment
    for spec in self.session.project.spectrum_list():
      for peak in spec.peak_list():
        if peak.is_assigned == 0: continue
        validity = []
        for resn in peak.resonances():
          if atomnames.protein_atoms_by_group_2.has_key(resn.group.symbol):
            atom_list = atomnames.protein_atoms_by_group_2[resn.group.symbol]
            try:
              idx = atom_list.index(resn.atom.name)
              validity.append(1)
            except:
              validity.append(0)            
          else:
            validity.append(0)
        if len(validity) == 0: continue
        
        try:
          idx = validity.index(0)
          grp = [spec, peak, validity]
          self.label_list.append(spec.name + ':' + peak.assignment, grp)
        except:
          pass

  # ---------------------------------------------------------------------------
  #  
  def assign_cb(self):
    for pitem in self.label_list.selected_line_data():
      for i in range(pitem[0].dimension):
          gn = self.group_list[i].variable.get()
          an = self.atom_list[i].variable.get()
          pitem[1].assign(i, gn, an)
      self.update_cb()          
      return    
                
  # ---------------------------------------------------------------------------
  #  
  def unassign_cb(self):
    for pitem in self.label_list.selected_line_data():
      for i in range(pitem[0].dimension):
          pitem[1].assign(i, '', '')
      self.update_cb()          
      return    

  # ---------------------------------------------------------------------------
  #
  def hx1_3_cb(self):
    for pitem in self.label_list.selected_line_data():
      for i in range(len(pitem[1].resonances())):
        szHX = atomnames.s12tos32(pitem[1].resonances()[i].group.symbol, pitem[1].resonances()[i].atom.name)
        pitem[1].assign(i, pitem[1].resonances()[i].group.name, szHX)
        
    self.update_cb()          
    return    
    
  def hx1_3_all_cb(self):
    for pitem in self.label_list.line_data:
      for i in range(len(pitem[1].resonances())):
        szHX = atomnames.s12tos32(pitem[1].resonances()[i].group.symbol, pitem[1].resonances()[i].atom.name)
        pitem[1].assign(i, pitem[1].resonances()[i].group.name, szHX)
        
    self.update_cb()            
    pass

# -----------------------------------------------------------------------------
#
def check_protein_nomen(session):
  sputil.the_dialog(show_check_protein_nomen_dialog,session).show_window(1)
