# -----------------------------------------------------------------------------
# Pointer mode radio button dialog.
#
import tkutil

# -----------------------------------------------------------------------------
#
class pointer_mode_dialog(tkutil.Dialog):

  def __init__(self, session):

    self.session = session
    
    tkutil.Dialog.__init__(self, session.tk, 'Mode')

    import Tkinter
    v = Tkinter.StringVar(self.top)
    self.mode_variable = v

    row = 0
    mode_names = ('select', 'center', 'addGridBoth', 'addGridHorz',
		  'addGridVert', 'addLabel', 'addLine', 'findAddPeak',
		  'integrate', 'zoom', 'duplicateZoom', 'assignCopy',
		  'assignGuess')
    for name in mode_names:
      b = Tkinter.Radiobutton(self.top, text = name,
			      variable = v, value = name,
			      command = self.change_mode_cb)
      b.grid(row = row, column = 0, sticky = 'w')
      row = row + 1

    br = tkutil.button_row(self.top,
			   ('Close', self.close_cb),
			   )
    br.frame.grid(row = row, column = 0, sticky = 'w')

    session.notify_me('pointer mode changed', self.mode_changed_cb)

  # ---------------------------------------------------------------------------
  #
  def mode_changed_cb(self):

    mode_name = self.session.pointer_mode
    self.mode_variable.set(mode_name)

  # ---------------------------------------------------------------------------
  #
  def change_mode_cb(self):

    self.session.pointer_mode = self.mode_variable.get()

# -----------------------------------------------------------------------------
#
def show_pointer_mode_dialog(session):

  import sputil
  d = sputil.the_dialog(pointer_mode_dialog, session)
  d.show_window(1)
  return d
