#rb = radio.button_row(w, 'Choose pichoose', ('One', 'one'), ('Two', 'two'), ('Three', 'three'))

import Tkinter
import tkutil
import pyutil

# ----------------------------------------------------------------------------
#
class interleaved_radiobutton:

  def __init__(self, parent, title, *kw):

    f = Tkinter.Frame(parent)
    self.frame = f
    radiobuttons = []
    c = 0
    r = 0

    if title:
      label = Tkinter.Label(f, text = title)
      label.grid(row = r, column = c, sticky = 'w')
      c = c + 1

    v = Tkinter.IntVar(parent)
    self.variable = v
    v.set(None)

    for text, value in kw:
#      b = Tkinter.Radiobutton(f, text = text, variable = v, value = value, highlightthickness = 0, command = self.update_entry)
      b = iradiobutton(f, text = text, v = v, value = value)
      b.radiobutton.grid(row = r, column = c)
      c = c + 1
      radiobuttons.append(b)

    self.radiobuttons = radiobuttons

  # ---------------------------------------------------------------------------
  #
  def update(self):

    pass

# ----------------------------------------------------------------------------
#
class iradiobutton:

  def __init__(self, f, text = None, v = None, value = None):

    b = Tkinter.Radiobutton(f, text = text, variable = v, value = value, highlightthickness = 0)
    self.variable = v
    self.radiobutton = b

  # ---------------------------------------------------------------------------
  #
  def add_callback(self, cb):

    tkutil.variable_set_callback(self.radiobutton, self.variable, cb)

  # ---------------------------------------------------------------------------
  #
  def map_hide_widget(self, popup):

    self.add_callback(pyutil.precompose(self.hide_widget_cb, popup))
    
  # ---------------------------------------------------------------------------
  #
  def map_show_widget(self, popup):

    self.add_callback(pyutil.precompose(self.show_widget_cb, popup))
    
  # ---------------------------------------------------------------------------
  #
  def show_widget_cb(self, w, show):

    if show:
      w.pack(side = 'top', anchor = 'w')
    else:
      w.pack_forget()

  # ---------------------------------------------------------------------------
  #
  def hide_widget_cb(self, w, hide):

    if hide:
      w.pack_forget()
    else:
      w.pack(side = 'top', anchor = 'w')

# ----------------------------------------------------------------------------
#
class button_row:

  def __init__(self, parent, title, *kw):

    f = Tkinter.Frame(parent)
    self.frame = f

    c = 0
    r = 0

    if title:
      label = Tkinter.Label(f, text = title)
      label.grid(row = r, column = c, sticky = 'w')
      c = c + 1

    v = Tkinter.StringVar(parent)
    self.variable = v
    v.set(None)

    for text, value in kw:
      b = Tkinter.Radiobutton(f, text = text, variable = v, value = value, highlightthickness = 0, command = self.update_entry)
      b.grid(row = r, column = c)
      c = c + 1

    ef = tkutil.entry_field(f, None, width = 35)
    ef.frame.grid(row = r, column = c)
    self.entry_field = ef

  def update_entry(self):

    self.entry_field.entry.delete('0', 'end')
    self.entry_field.entry.insert('end', self.variable.get())

# ----------------------------------------------------------------------------
#
class data_type_field:

  def __init__(self, parent, title, fid_frame, f, interleaved, alpha_dialog, beta_dialog, id_frame, handling_frame, *kw):

    f = Tkinter.Frame(parent)
    self.frame = f

    self.fid_frame = fid_frame
    self.f = f
    self.interleaved = interleaved
    self.alpha_dialog = alpha_dialog
    self.beta_dialog = beta_dialog
    self.id_frame = id_frame
    self.handling_frame = handling_frame

    c = 0
    r = 0

    if title:
      label = Tkinter.Label(f, text = title)
      label.grid(row = r, column = c, sticky = 'w')
      c = c + 1

    v = Tkinter.IntVar(parent)
    self.variable = v
    v.set(None)

    for text, value in kw:
      b = Tkinter.Radiobutton(f, text = text, variable = v, value = value, highlightthickness = 0, command = self.update_cb)
      b.grid(row = r, column = c)
      c = c + 1


  def update_cb(self):

     print self.variable.get()
     if self.variable.get() == 2:
       self.interleaved.set_value(0)
       self.id_frame.pack_forget()
       self.fid_frame.pack_forget()
       self.handling_frame.pack_forget()
     elif self.variable.get() == 1:
       self.interleaved.set_value(0)
       self.id_frame.pack_forget()
       self.fid_frame.pack_forget()
       self.alpha_dialog.pack_forget()
       self.beta_dialog.pack_forget()
       self.alpha_dialog.pack(side = 'top', anchor = 'w')
       self.beta_dialog.pack(side = 'top', anchor = 'w')
       self.handling_frame.pack(side = 'top', anchor = 'w')
     else:
       self.alpha_dialog.pack_forget()
       self.beta_dialog.pack_forget()
       self.handling_frame.pack_forget()
       self.id_frame.pack(side = 'top', anchor = 'w')
       self.alpha_dialog.pack(side = 'top', anchor = 'w')
       self.beta_dialog.pack(side = 'top', anchor = 'w')
       self.fid_frame.pack(side = 'top', anchor = 'w')
       self.handling_frame.pack(side = 'top', anchor = 'w')

  def get_value(self):

    self.variable.get()

  def set_value(self, v):

    self.variable.set(v)
    self.update_cb()

# ----------------------------------------------------------------------------
#
class interleaved_field:

  def __init__(self, parent, title, widget, after, *kw):

    f = Tkinter.Frame(parent)
    self.frame = f

    self.widget = widget
    self.after = after

    c = 0
    r = 0

    if title:
      label = Tkinter.Label(f, text = title)
      label.grid(row = r, column = c, sticky = 'w')
      c = c + 1

    v = Tkinter.IntVar(parent)
    self.variable = v
    v.set(None)

    for text, value in kw:
      b = Tkinter.Radiobutton(f, text = text, variable = v, value = value, highlightthickness = 0, command = self.update_cb)
      b.grid(row = r, column = c)
      c = c + 1


  def update_cb(self):

     if self.variable.get():
       self.widget.pack_forget()
     else:
       self.widget.pack(side = 'top', anchor = 'w', after = self.after)

  def get_value(self):

    self.variable.get()

  def set_value(self, v):

    self.variable.set(v)
    self.update_cb()

# ----------------------------------------------------------------------------
#
class button_field:

  def __init__(self, parent, title, default, *kw):

    self.kw = kw
    self.default = default
    f = Tkinter.Frame(parent)
    self.frame = f
    r = 0
    c = 0

    if title:
      label = Tkinter.Label(f, text = title)
      label.pack(side = 'top', anchor = 'w')

    v = Tkinter.StringVar(parent)
    self.variable = v

    ef = tkutil.entry_field(f, None, width = 35)
    ef.frame.pack(side = 'top', anchor = 'nw')
    self.entry_field = ef

    if kw[default][1]:
      v.set(kw[default][1])
      self.update_entry()
    else:
      v.set(None)

    w = Tkinter.Frame(f)
    w.pack(side = 'top', anchor = 'w')
    
    if len(kw) <= 3:
      dc = 3
    else:
      dc = len(kw) / 3 + 1

    for text, value in kw:
      b = Tkinter.Radiobutton(w, text = text, variable = v, value = value, highlightthickness = 0, command = self.update_entry)
      b.grid(row = r, column = c, sticky = 'nw')
      c = c + 1
      if c / dc == 1:
        r = r + 1
	c = 0

  def update_entry(self):

    self.entry_field.entry.delete('0', 'end')
    self.entry_field.entry.insert('end', self.variable.get())

  def reset_cb(self):

    if self.kw[self.default][1]:
      self.variable.set(self.kw[self.default][1])
      self.update_entry()
    elif self.kw[self.default][1] == None:
      self.variable.set('')
      self.update_entry()

# ----------------------------------------------------------------------------
#
class phase_correction_dialog:

  def __init__(self, parent, title):

    f = Tkinter.Frame(parent)
    self.frame = f

    if title:
      label = Tkinter.Label(f, text = title)
      label.pack(side = 'top', anchor = 'nw')

    p0 = tkutil.entry_field(f, 'Zero-order phase correction ', '0', 6)
    p0.frame.pack(side = 'top', anchor = 'e')
    self.efp0 = p0
    self.p0 = p0.variable

    p1 = tkutil.entry_field(f, 'First-order phase correction ', '0', 6)
    p1.frame.pack(side = 'top', anchor = 'e')
    self.efp1 = p1
    self.p1 = p1.variable

    dicb = tkutil.checkbutton(f, 'Delete current imaginaries', 1)
    dicb.button.pack(side = 'top', anchor = 'ne')
    self.dicb = dicb
    self.di = dicb.variable
      
  def reset_cb(self):

    self.efp0.entry.delete('0', 'end')
    self.efp0.entry.insert('end', '0')

    self.efp1.entry.delete('0', 'end')
    self.efp1.entry.insert('end', '0')

    self.dicb.set_state(1)

#    nd = tkutil.button_row(processing_dialog, ('Phase using nmrDraw', self.nmrdraw_cb))
#    nd.frame.pack(side = 'top', anchor = 'ew')
# ----------------------------------------------------------------------------
#
class phase_correction_dialog2:

  def __init__(self, parent, title):

    f = Tkinter.Frame(parent)
    self.frame = f

    if title:
      label = Tkinter.Label(f, text = title)
      label.pack(side = 'top', anchor = 'nw')

    self.p0 = [None, None]
    p0 = tkutil.entry_row(f, 'Zero-order phase correction: ',
                            ('F2', '0', 6), ('F1', '0', 6))
    (self.p0[0],
     self.p0[1]) = p0.variables
    p0.frame.pack(side = 'top', anchor = 'e')
    self.efp0 = p0

    self.p1 = [None, None]
    p1 = tkutil.entry_row(f, 'First-order phase correction: ',
                            ('F2', '0', 6), ('F1', '0', 6))
    (self.p1[0],
     self.p1[1]) = p1.variables
    p1.frame.pack(side = 'top', anchor = 'e')
    self.efp1 = p1

    dicb = tkutil.checkbutton(f, 'Delete current imaginaries', 1)
    dicb.button.pack(side = 'top', anchor = 'ne')
    self.dicb = dicb
    self.di = dicb.variable
      
  def reset_cb(self):

    for entry in self.efp0.entries:
      entry.entry.delete('0', 'end')
      entry.entry.insert('end', '0')
    
    for entry in self.efp1.entries:
      entry.entry.delete('0', 'end')
      entry.entry.insert('end', '0')
    
    self.dicb.set_state(1)

#    nd = tkutil.button_row(processing_dialog, ('Phase using nmrDraw', self.nmrdraw_cb))
#    nd.frame.pack(side = 'top', anchor = 'ew')
# ----------------------------------------------------------------------------
#
class button_col:

  def __init__(self, parent, *buttons):

    self.frame = Tkinter.Frame(parent)
    self.buttons = []
    for name, cb in buttons:
      b = Tkinter.Button(self.frame, text = name, command = cb)
      b.pack(side = 'top', anchor = 'w')
      self.buttons.append(b)

    
## ----------------------------------------------------------------------------
##
#class radiobutton_row:
#
# def __init__(self, parent, label = None, *buttons):
#
#   self.frame = Tkinter.Frame(parent)
#
#   if text:
#     label = Tkinter.Label(self.frame, text = label)
#     label.pack(side = 'left', anchor = 'w')
#
#   self.buttons = []
#
#   for name, v, value, cb in buttons:
#     b = Tkinter.Radiobutton(self.frame, text = name, variable = v, value = value, highlightthickness = 0, command = cb)
#     b.pack(side = 'left', anchor = 'w')
#     self.buttons.append(b)
#
#   
# ----------------------------------------------------------------------------
#
class interleaved_checkbutton:

  def __init__(self, parent, text, onoff, after_widget = None):

    v = Tkinter.BooleanVar(parent)
    self.variable = v
    v.set(onoff)

    b = Tkinter.Checkbutton(parent, highlightthickness = 0,
#			  selectcolor = 'black',
                            text = text, variable = v)
    self.button = b
    self.after_widget = after_widget

  # ---------------------------------------------------------------------------
  #
  def state(self):

    return self.variable.get()

  # ---------------------------------------------------------------------------
  #
  def set_state(self, onoff):

    self.variable.set(onoff)
    
  # ---------------------------------------------------------------------------
  #
  def add_callback(self, cb):

    tkutil.variable_set_callback(self.button, self.variable, cb)

  # ---------------------------------------------------------------------------
  #
  def map_widget(self, popup):

    self.add_callback(pyutil.precompose(self.hide_widget_cb, popup))
    
  # ---------------------------------------------------------------------------
  #
  def hide_widget_cb(self, w, hide):

    if hide:
      w.pack_forget()
    else:
      if self.after_widget:
        w.pack(side = 'top', anchor = 'w', fill = 'x', after = self.after_widget)
      else:  
        w.pack(side = 'top', anchor = 'w')

