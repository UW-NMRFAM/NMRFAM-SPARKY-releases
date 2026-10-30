# -----------------------------------------------------------------------------
# Easy contour tool
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Jan 14, 2016
# 
#
#
# -----------------------------------------------------------------------------

import Tkinter

import pinegraph
import sparky
import sputil
import tkutil
import random
import tkMessageBox

contour_color_dict = {
    1:"red", 2:"orange", 3:"yellow", 4:"green", 5:"blue", 6:"dark blue", 7:"purple", 
    8:"pink", 9:"beige", 10:"coral", 11:"cyan", 12:"gold", 13:"gray",
    14:"light blue", 15:"light green", 16:"light yellow", 17:"magenta", 18:"maroon", 
    19:"tomato", 20:"turquoise", 21:"dark green", 22:"dark orange",  23:"green-blue",
    24:"red-blue", 25:"red-yellow", 26:"blue-red", 27:"blue-green", 28:"yellow-red"
}

# -----------------------------------------------------------------------------
#
class adv_contour_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    self.session = session  
    tkutil.Dialog.__init__(self, session.tk, 'Easy contour dialog')

    self.selected_views = []
    self.lb = pinegraph.modified_listbox(self.top, 'Contour settings: ', 45, 7, "extended")
    self.lb.listbox.config(font='Courier 10')    
    self.lb.frame.pack(fill = 'both', side = 'top', expand = 1)
    self.lb.listbox.bind('<Double-Button-1>', self.contour_setting)
    self.lb.listbox.bind('<Button-2>', self.spec_setting)
    self.lb.listbox.bind('<Button-3>', self.view_setting)

    self.clear_lb()
            
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')
        
    self.button_frame = Tkinter.Frame(self.top, width = 300, height = 60)
    self.button_frame.pack(side='bottom', anchor='w')    
    
    br = tkutil.button_row(self.button_frame,
			   ('Update', self.update_cb),
			   ('Select all', self.selectall_cb),			   
			   ('Invert select', self.invertselect_cb),
			   ('Spray colors', self.spray_cb),
			   ('Random color', self.random_cb),			   			   
			   ('Set default', self.default_cb),
			   ('Uniform', self.uniform_cb),
			   )
    for btn in br.buttons:
		  btn.config(font='Courier 10')
    br.frame.pack(anchor = 'w', side = 'top')   			   
			   
    br2 = tkutil.button_row(self.button_frame,
			   ('^ (+) lowest', self.increase_positive_lowest_cb),
			   ('^ (+) level', self.increase_positive_level_cb),
			   ('^ (+) factor', self.increase_positive_factor_cb),			   
			   ('^ (-) lowest', self.increase_negative_lowest_cb),
			   ('^ (-) level', self.increase_negative_level_cb),
			   ('^ (-) factor', self.increase_negative_factor_cb),
			   )
    for btn in br2.buttons:
		  btn.config(font='Courier 10')			   
    br2.frame.pack(anchor = 'w', side = 'top')   			   
			   
    br3 = tkutil.button_row(self.button_frame,			   
			   ('v (+) lowest', self.decrease_positive_lowest_cb),			   
			   ('v (+) level', self.decrease_positive_level_cb),  
			   ('v (+) factor', self.decrease_positive_factor_cb),  
			   ('v (-) lowest', self.decrease_negative_lowest_cb),			   
			   ('v (-) level', self.decrease_negative_level_cb),  
			   ('v (-) factor', self.decrease_negative_factor_cb),  
         )
    for btn in br3.buttons:
		  btn.config(font='Courier 10')         
    br3.frame.pack(anchor = 'w', side = 'top')            
         			   	
  def update_cb(self):
    self.clear_lb()
    pass

  def increase_positive_lowest_cb(self):
    self.change_contour(1, 1, 0)
    pass
    
  def increase_positive_level_cb(self):  
    self.change_contour(1, 1, 1)  
    pass 
    
  def increase_positive_factor_cb(self):  
    self.change_contour(1, 1, 2)  
    pass 
         
  def increase_negative_lowest_cb(self):
    self.change_contour(1, 0, 0)
    pass
    
  def increase_negative_level_cb(self):  
    self.change_contour(1, 0, 1)  
    pass 
    
  def increase_negative_factor_cb(self):
    self.change_contour(1, 0, 2)  
    pass 

  def decrease_positive_lowest_cb(self):
    self.change_contour(-1, 1, 0)  
    pass
    
  def decrease_positive_level_cb(self):  
    self.change_contour(-1, 1, 1)  
    pass 
    
  def decrease_positive_factor_cb(self): 
    self.change_contour(-1, 1, 2)   
    pass 
         
  def decrease_negative_lowest_cb(self):
    self.change_contour(-1, 0, 0)
    pass
    
  def decrease_negative_level_cb(self):  
    self.change_contour(-1, 0, 1)  
    pass 
    
  def decrease_negative_factor_cb(self):  
    self.change_contour(-1, 0, 2)  
    pass 
        
  def spray_cb(self):
    # for all spectra
    idx = 0
    for data in self.lb.line_data:
      if data == None: continue
      view = data[0]      
      idx2 = idx % 22 + 1
      idx3 = 22 - idx % 22
      col = contour_color_dict[idx2]
      col2 = contour_color_dict[idx3]      
      pos_contour = view.positive_levels
      neg_contour = view.negative_levels
      pos_contour.color = col
      neg_contour.color = col2      
      view.positive_levels = pos_contour
      view.negative_levels = neg_contour
      idx = idx + 1      
    self.update_cb()
    
  def random_cb(self):
    # for selected view
    if len(self.lb.selected_line_data()) == 0:
      tkMessageBox.showerror('Selection error', 'No view selected.')
      return
    for data in self.lb.selected_line_data():
      if data == None: continue
      view = data[0]
      idx = random.randrange(1, 23)    
      idx2 = random.randrange(1, 23)          
      col = contour_color_dict[idx]
      col2 = contour_color_dict[idx2]      
      pos_contour = view.positive_levels
      neg_contour = view.negative_levels
      pos_contour.color = col
      neg_contour.color = col2      
      view.positive_levels = pos_contour
      view.negative_levels = neg_contour
    self.update_cb()
        
  def default_cb(self):
    # for selected soectra  
    # level: 14, factor: 1.4, color: red & green
    # lowest: (+/-)10 * noise
    if len(self.lb.selected_line_data()) == 0:
      tkMessageBox.showerror('Selection error', 'No view selected.')
      return    
    
    for data in self.lb.selected_line_data():
      if data == None: continue
      view = data[0]
      spec = view.spectrum
      if spec == None: continue
      pos_contour = view.positive_levels
      neg_contour = view.negative_levels
      pos_contour.factor = 1.4
      neg_contour.factor = 1.4      
      pos_contour.levels = 14
      neg_contour.levels = 14
      pos_contour.color = 'red'
      neg_contour.color = 'green'
      pos_contour.lowest = spec.noise * 10
      neg_contour.lowest = spec.noise * -10      
      view.positive_levels = pos_contour
      view.negative_levels = neg_contour

    self.update_cb()
    
  def change_contour(self, iInc, iPos, iMode):
    # level: +/- 1  -> 1, factor: +/- 0.1 -> 2
    # lowest: 10% -> 0
    if len(self.lb.selected_line_data()) == 0:
      tkMessageBox.showerror('Selection error', 'No view selected.')
      return    
    for data in self.lb.selected_line_data():
      if data == None: continue
      view = data[0]
      spec = view.spectrum
      if spec == None: continue    
      
      if iPos == 1: contour = view.positive_levels
      else:         contour = view.negative_levels
      
      diff = 0
      if iMode == 0:
        diff = contour.lowest * 0.1 * iInc
        contour.lowest = contour.lowest + diff
      elif iMode == 1:  
        diff = 1 * iInc
        contour.levels = contour.levels + diff
      elif iMode == 2:
        diff = 0.1 * iInc
        contour.factor = contour.factor + diff
      
      if iPos == 1: view.positive_levels = contour
      else: view.negative_levels = contour  
      
    self.update_cb()

  def invertselect_cb(self):
    selected = []
    for data in self.lb.selected_line_data():
      if data == None: continue
      selected.append(data[3])
      self.lb.listbox.select_clear(data[3])
    for data in self.lb.line_data:
      if data == None: continue
      try:
        idx = selected.index(data[3])
        continue
      except:
        self.lb.listbox.select_set(data[3])
        self.lb.listbox.see(data[3])
          
  def selectall_cb(self):
    for data in self.lb.line_data:
      if data == None: continue
      self.lb.listbox.selection_set(data[3])
      self.lb.listbox.see(data[3])
                            			   			   			   
  def clear_lb(self):
    session = self.session
    
    # selected views?
    self.selected_views = []
    self.focused_view = None
    
    for data in self.lb.selected_line_data():
      if data == None: continue
      self.selected_views.append(data)
    
    self.lb.clear()
    
    if session.project == None: return
    view_list = session.project.view_list()

    iMax = 0    
    if len(view_list) == 0: iMax = 5
    
    # longest view name?
    for v in view_list:
      size = len(v.name)
      if size > iMax: iMax = size
    
    sname = 'View'
    sname2 = 'Name'
    sname3 = ''    
    diff = iMax - len(sname)
    for i in range(diff):
      sname = sname + ' '
      sname2 = sname2 + ' '      
    for i in range(iMax):
      sname3 = sname3 + '-'
      
    vlbl =  '%s|Positive                           |Negative                           ' % (sname)
    vlbl2 = '%s|Color       |Lowest  |Level|Factor |Color       |Lowest  |Level|Factor ' % (sname2)
    vlbl3 = '%s+------------+--------+-----+-------+------------+--------+-----+-------' % (sname3)    
    self.lb.append(vlbl, None)
    self.lb.append(vlbl2, None)    
    self.lb.append(vlbl3, None)  
    
    self.lb.listbox.itemconfig(0, {'bg':'yellow', 'selectbackground':'yellow', 'selectforeground':'black'})      
    self.lb.listbox.itemconfig(1, {'bg':'yellow', 'selectbackground':'yellow', 'selectforeground':'black'})      
    self.lb.listbox.itemconfig(2, {'bg':'yellow', 'selectbackground':'yellow', 'selectforeground':'black'})          
    
    idx = 3
    for v in view_list:
      if v.is_top_level_window == 0: continue
      pc = v.positive_levels
      nc = v.negative_levels
      sname = v.name
      size = len(sname)
      diff = iMax - size
      for i in range(diff):
        sname = sname + ' '
      vlbl = '%s|%12s %8.2g %5d %6.2f |%12s %8.2g %5d %6.2f' % (sname, pc.color, pc.lowest, pc.levels, pc.factor, nc.color, nc.lowest, nc.levels, nc.factor)
      
    # label format
    # name    color lowest level factor  color lowest level factor
    # %iMaxs  %11s    %8g   %5d   %4.2f   %11s    %8g   %5d   %4.2f   => iMax + 62
    #   
      self.lb.append(vlbl, [v, pc, nc, idx]) 
      if v.is_shown == 0:
        self.lb.listbox.itemconfig(self.lb.count()-1, {'fg':'red',
                                        'selectforeground':'red'})

      idx = idx + 1
      
    for data in self.selected_views:
      if data == None: continue
      self.lb.listbox.selection_set(data[3])
      self.lb.listbox.see(data[3])

    
  # setting single contour level
  def contour_setting(self, event):
    data_list = self.lb.selected_line_data()
    if len(data_list) < 1: return
    idx = self.lb.selected_line_numbers()[0]
    if idx < 3: return
    v = data_list[0][0]
    if v.is_shown == 0: return
    tkutil.tk_call(self.session.tk, 'focus', v.frame)
    v.got_focus()
    self.session.command_characters('ct')

  def view_setting(self, event):
    data_list = self.lb.selected_line_data()
    if len(data_list) < 1: return
    idx = self.lb.selected_line_numbers()[0]
    if idx < 3: return
    v = data_list[0][0]
    if v.is_shown == 0: return
    tkutil.tk_call(self.session.tk, 'focus', v.frame)
    v.got_focus()
    self.session.command_characters('vt')

  def spec_setting(self, event):
    data_list = self.lb.selected_line_data()
    if len(data_list) < 1: return
    idx = self.lb.selected_line_numbers()[0]
    if idx < 3: return
    v = data_list[0][0]
    if v.is_shown == 0: return
    tkutil.tk_call(self.session.tk, 'focus', v.frame)
    v.got_focus()
    self.session.command_characters('st')

  def uniform_cb(self):
    session = self.session
    data_list = self.lb.selected_line_data()
    if len(data_list) < 2: return
    selected = self.lb.selected_line_numbers()
    idx = selected[0]
    if idx < 3: return
    rv = data_list[0][0]
    if rv.is_shown == 0: return
    rs = rv.spectrum
    rw, rh, rx, ry = tkutil.get_view_geometry(session, rv)
    snuc = ''
    for i in range(rs.dimension):
      snuc += rs.nuclei[rv.axis_order[i]]
    rvp = rv.positive_levels
    rvn = rv.negative_levels

    for data in data_list[1:]:
      v = data[0]
      s = v.spectrum
      if rs.dimension != s.dimension: continue
      nuc = ''
      for i in range(s.dimension):
        nuc += s.nuclei[v.axis_order[i]]
      if nuc != snuc: continue
      w, h, x, y = tkutil.get_view_geometry(session, v)
      tkutil.set_view_geometry(session, v, rw, rh, x, y)
      v.center = rv.center
      v.pixel_size = rv.pixel_size

      vp = v.positive_levels
      vp.lowest = rvp.lowest
      vp.factor = rvp.factor
      vp.levels = rvp.levels
      v.positive_levels = vp
 
      vn = v.negative_levels
      vn.lowest = rvn.lowest
      vn.factor = rvn.factor
      vn.levels = rvn.levels
      v.negative_levels = vn
    self.update_cb()

# -----------------------------------------------------------------------------
#
def show_adv_contour(session):
  sputil.the_dialog(adv_contour_dialog,session).show_window(1)
