# -----------------------------------------------------------------------------
# Show calculated chemical shift
#
#       cs = cs0 + k * offset
#
# where offset is the ppm distance from mouse pointer to selected peak along
# a specified axis and cs0 and k are specified constants.
#
import Tkinter

import sputil
import tkutil
  
# -----------------------------------------------------------------------------
#
class shift_calculator_dialog(tkutil.Dialog):

  def __init__(self, session):

      self.session = session

      tkutil.Dialog.__init__(self, session.tk, 'Calculate Chemical Shift')

      explain = ('Calculate chemical shift from mouse position:\n\n' +
                 '    cs = cs0 + k * offset\n\n' +
                 'where offset is the ppm distance from mouse pointer\n'
                 'to the selected peak along a specified axis.')
      w = Tkinter.Label(self.top, text = explain, justify = 'left')
      w.pack(side = 'top', anchor = 'w')

      er = tkutil.entry_row(self.top, '',
                            ('cs0 = ', '0', 6), ('  k = ', '1', 6))
      er.frame.pack(side = 'top', anchor = 'w')
      self.cs0, self.k = er.variables

      ax = tkutil.option_menu(self.top, 'Spectrum axis: ',
                              ('w1', 'w2', 'w3', 'w4'))
      ax.frame.pack(side = 'top', anchor = 'w')
      self.axis_menu = ax

      ol = Tkinter.Label(self.top, text = 'Offset = ', justify = 'left')
      ol.pack(side = 'top', anchor = 'w')
      self.offset = ol

      cs = Tkinter.Label(self.top, text = 'Chemical shift = ',
                         justify = 'left')
      cs.pack(side = 'top', anchor = 'w')
      self.chemical_shift = cs

      br = tkutil.button_row(self.top,
                             ('Close', self.close_cb),
                             )
      br.frame.pack(side = 'top', anchor = 'w')

      self.top.bind('<Map>', self.check_motion)

  # ---------------------------------------------------------------------------
  #
  def check_motion(self, event = None):

    if self.is_window_destroyed() or not self.top.winfo_viewable():
        return

    offset = self.pointer_offset()
    self.show_chemical_shift(offset)
    
    import Tkinter
    delay = 100         # milliseconds
    self.top.after(delay, self.check_motion)

  # ---------------------------------------------------------------------------
  #
  def pointer_offset(self):

      axis_name = self.axis_menu.get()
      axis_number = {'w1':0, 'w2':1, 'w3':2, 'w4':3}
      if axis_number.has_key(axis_name):
          axis = axis_number[axis_name]
      else:
          axis = 0

      peak_pos = self.selected_peak_position(axis)
      if peak_pos == None:
          return None

      pointer_pos = self.pointer_position(axis)
      if pointer_pos == None:
          return None

      return pointer_pos - peak_pos

  # ---------------------------------------------------------------------------
  #
  def selected_peak_position(self, axis):

      peaks = self.session.selected_peaks()
      if len(peaks) != 1:
          return None

      peak = peaks[0]
      pos = peak.position
      if axis < len(pos):
          return pos[axis]

      return None

  # ---------------------------------------------------------------------------
  #
  def pointer_position(self, axis):

      views = self.session.project.view_list()
      for view in views:
          pos = view.pointer_position
          if pos != None:
              if axis < len(pos):
                  return pos[axis]
      return None

  # ---------------------------------------------------------------------------
  #
  def show_chemical_shift(self, offset):

      if offset == None:
          self.offset['text'] = 'Offset = '
          self.chemical_shift['text'] = 'Chemical shift = '
          return

      try:
          cs0 = float(self.cs0.get())
      except ValueError:
          cs0 = 0

      try:
          k = float(self.k.get())
      except ValueError:
          k = 1

      cs = cs0 + k * offset

      self.offset['text'] = 'Offset = %6.3f' % offset
      self.chemical_shift['text'] = 'Chemical shift = %6.3f' % cs
    
# -----------------------------------------------------------------------------
#
def show_shift_dialog(session):
    sputil.the_dialog(shift_calculator_dialog,session).show_window(1)
