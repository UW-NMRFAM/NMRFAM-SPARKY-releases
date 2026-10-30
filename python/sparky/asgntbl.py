# -----------------------------------------------------------------------------
# Assignment Table
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Dec 9, 2016
# 
#
#
# -----------------------------------------------------------------------------

import sparky
import sputil
import tkutil
import pyutil
import shutil
import Tkinter
import tkMessageBox

class asgn_tbl(tkutil.Dialog):
  def __init__(self, session):
    self.session = session
    
    tkutil.Dialog.__init__(self, session.tk, 'Assignment Table')
    
    keypress_cb = pyutil.precompose(sputil.command_keypress_cb, session)
    self.top.bind('<KeyPress>', keypress_cb)        
        
    # condition
    condition_frame = Tkinter.Frame(self.top, width = 500, height = 25)
    condition_frame.pack(side = 'top', anchor = 'nw')
    
    self.get_conditions()
    self.cond_om = tkutil.option_menu(condition_frame, "Condition: ", self.condition_list, 'All*')
    self.cond_om.frame.pack(side = 'top', anchor = 'nw')
    self.cond_om.menu.bind("<<MenuSelect>>", self.update_callback)

    # sep
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
    
    # check box- chemical shift, deviation, peak_count
    self.cshift = Tkinter.IntVar()
    self.cshift.set(1)
    self.use_cshift_cb = Tkinter.Checkbutton(self.top, text = 'Show chemical shift', variable = self.cshift, onvalue=1, offvalue = 0, command=self.update_cb)
    self.use_cshift_cb.pack(side = 'top', anchor = 'w', expand = 0)

    self.dev = Tkinter.IntVar()
    self.dev.set(0)
    self.use_dev_cb = Tkinter.Checkbutton(self.top, text = 'Show deviation', variable = self.dev, onvalue=1, offvalue = 0, command=self.update_cb)
    self.use_dev_cb.pack(side = 'top', anchor = 'w', expand = 0)
            
    self.peakcount = Tkinter.IntVar()
    self.peakcount.set(0)
    self.use_peakcount_cb = Tkinter.Checkbutton(self.top, text = 'Show peak count', variable = self.peakcount, onvalue=1, offvalue = 0, command=self.update_cb)
    self.use_peakcount_cb.pack(side = 'top', anchor = 'w', expand = 0)
                
    # sep
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
                
    # assignment table- scrolling list
    self.asgn_list = tkutil.scrolling_list(self.top, 'Assignment Table', 8)
    self.asgn_list.frame.pack(side='top', fill = 'both', expand = 1)
        
    xscroll = Tkinter.Scrollbar(self.top, command = self.asgn_list.listbox.xview, orient="horizontal")
    xscroll.pack(side = 'top', fill = 'both', expand = 0)
    self.asgn_list.listbox['xscrollcommand'] = xscroll.set
    
    # sep
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)
        
    # buttons
    self.br = tkutil.button_row(self.top, 
        ('Update', self.update_cb),
        ('Write', self.write_list_cb),
        ('Close', self.close_cb),
        )
    self.br.frame.pack(side = 'top', fill = 'both', expand = 0)         
    
    self.update_cb()
  # ---------------------------------------------------------------------------
  #
  def write_file(self, mode):
    # 0- csv, 1- tab
    #if mode == 0:    sep = ','
    #else: sep = '\t'
#    try:
    path = tkutil.save_file(self.session.tk, "Save assignment table", "asgn_tbl.txt")
    if path: 
      f = open(path, 'w')
      for data in self.asgn_list.line_data:
        f.write('%s\n' % data)
      f.close()
#    except:
#      tkMessageBox.showerror('Save error', 'Saving was not successful. It can be privilege issue or space.')
#      return
    tkMessageBox.showinfo('Saved', 'Saving was successful.')      
    
  # ---------------------------------------------------------------------------
  #
  def write_list_cb(self):
    self.write_file(0)    
  # ---------------------------------------------------------------------------
  #
  def get_condition_list(self):
    cond_list = []
    if self.cond_om.get() == 'All*':
      for condition in self.session.project.condition_list():
        cond_list.append(condition)
      return cond_list

    for condition in self.session.project.condition_list():
      if self.cond_om.get() == condition.name:
        cond_list.append(condition)
        return cond_list
        
    return []
  # ---------------------------------------------------------------------------
  #
  def update_cb(self):
    # depending on what is being selected
    # what condition?
    cond_list = self.get_condition_list()
    
    # build atom list
    atom_list = []
    for cond in cond_list:
      for resn in cond.resonance_list():        
        try:
          idx = atom_list.index(resn.atom.name)
        except:
          atom_list.append(resn.atom.name)
    atom_list.sort()
                    
    # loop condition
    self.asgn_list.clear()
    
    for cond in cond_list:
      szLine = 'Condition %s' % (cond.name)
      self.asgn_list.append(szLine, (szLine))
      
      # build groups
      group_list = []
      for resn in cond.resonance_list():
        try:
          idx = group_list.index( (resn.group.number,resn.group.symbol,resn.group.name) )
        except:
          group_list.append( (resn.group.number,resn.group.symbol,resn.group.name) )
        
      # sort group
      sorted_groups = sorted(group_list, key=lambda group: group[0])
      
      # write atom names
      szLine = '{:^11}'.format('Groups')
      for atomname in atom_list:
        szLine = szLine + '{:^11}'.format(atomname)
      self.asgn_list.append(szLine)
      
      # build line  
      for (gnum, gsym, gname) in sorted_groups:
        szLine = '{:^11}'.format(gname)
        szLine2 = '{:^11}'.format(gname+'_dev') 
        szLine3 = '{:^11}'.format(gname+'_#')
        for atomname in atom_list:
          resn = cond.find_resonance(gname, atomname)	# returns resonance or None        
          if self.cshift.get() == 1:
            if resn == None:
              szLine = szLine + '     -     '
            else:
              szLine = szLine + '{:^11}'.format('%.3f' % (resn.frequency))
              
          if self.dev.get() == 1:
            if resn == None:
              szLine2 = szLine2 + '     -     '
            else:
              szLine2 = szLine2 + '{:^11}'.format('%.3f' % (resn.deviation))
              
          if self.peakcount.get() == 1:    
            if resn == None:
              szLine3 = szLine3 + '     -     '
            else:
              szLine3 = szLine3 + '{:^11}'.format('%d' % (resn.peak_count))
              
        if self.cshift.get() == 1: self.asgn_list.append(szLine, (szLine))
        if self.dev.get() == 1: self.asgn_list.append(szLine2, (szLine2))        
        if self.peakcount.get() == 1: self.asgn_list.append(szLine3, (szLine3))
                  
      self.asgn_list.append('', '') # gap between conditions

  # ---------------------------------------------------------------------------
  #    
  def get_conditions(self):
    self.condition_list = ['All*']
    for condition in self.session.project.condition_list():
      self.condition_list.append(condition.name)
      
  # ---------------------------------------------------------------------------
  #
  def update_callback(self, event):
    self.update_cb()      

  
def show_assignment_table(session):
  sputil.the_dialog(asgn_tbl, session).show_window(1)
