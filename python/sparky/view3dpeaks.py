# -----------------------------------------------------------------------------
# Display 3 orthogonal views for each peak in a 3-d spectrum.
# The 3 views for each peak appear in a column and you can scroll through
# the columns.  This is designed for fast inspection after peak picking
# 3-d spectra.
#

import Tkinter
import sparky
import sputil
import tkutil

# -----------------------------------------------------------------------------
#
class view_3d_peaks(tkutil.Dialog):

  def __init__(self, session):

    tkutil.Dialog.__init__(self, session.tk, '3D Peak Views')

    self.strips = []
    self.first_strip_index = 0
    self.strip_width = 100
    self.strip_gap = 10

    sf = self.create_strip_frame(self.top)
    sf.pack(side = 'top', anchor = 'nw', fill = 'both', expand = 1)
    
    self.strips_frame.bind('<Configure>', self.resize_cb, 1)
  
  # ---------------------------------------------------------------------------
  #
  def create_strip_frame(self, parent):

    sf = Tkinter.Frame(parent)
    
    sf.rowconfigure(0, weight = 1)
    sf.columnconfigure(0, weight = 1)

    strips = Tkinter.Frame(sf, width = 200, height = 600)
    strips.grid_propagate(0)
    strips.grid(row = 0, column = 0, sticky = 'news')
    self.strips_frame = strips
    
    hbar = Tkinter.Scrollbar(sf, orient = 'horizontal',
                             command = self.shift_strips)
    hbar.grid(row = 1, column = 0, sticky = 'ew')
    hbar.set(0, 1)
    self.hbar = hbar

    return sf

  # ---------------------------------------------------------------------------
  #
  def resize_cb(self, event):

    self.strip_width = self.strips_frame.winfo_height() / 3
    for strip in self.strips:
      strip.resize(self.strip_width)
      
    self.change_visible_strips()
    
  # ---------------------------------------------------------------------------
  #
  def replace_strips(self, strips):

    self.strips = strips
    self.first_strip_index = 0
    self.change_visible_strips()

  # ---------------------------------------------------------------------------
  #
  def shift_strips(self, *args):

    steps_per_page = self.visible_strip_count()
    tkutil.adjust_scrollbar(self.hbar, args, steps_per_page)
    (f1, f2) = self.hbar.get()
    self.first_strip_index = int(round(f1 * len(self.strips)))
    self.change_visible_strips()
    
  # ---------------------------------------------------------------------------
  #
  def change_visible_strips(self):

    first_index = self.first_strip_index
    count = self.visible_strip_count()
    for i in range(count):
      self.strips[first_index + i].set_column(i)
    for strip in self.strips[:first_index]:
      strip.set_column(None)
    for strip in self.strips[first_index+count:]:
      strip.set_column(None)

    self.update_horizontal_scrollbar()

  # ---------------------------------------------------------------------------
  #
  def update_horizontal_scrollbar(self):

    self.top.update_idletasks()      # Make sure view geometry is correct

    first = self.first_strip_index
    count = self.visible_strip_count()
    tkutil.set_scrollbar(self.hbar, first, first + count, 0, len(self.strips))

  # ---------------------------------------------------------------------------
  #
  def visible_strip_count(self):

    frame_width = self.strips_frame.winfo_width()
    max_strips = len(self.strips) - self.first_strip_index
    count = max(1, frame_width / self.strip_width)
    return min(max_strips, count)
    
  # ---------------------------------------------------------------------------
  #
  def show_peaks(self, view):

    spectrum = view.spectrum
    width = self.strip_width
    strips = []
    count = 0
    for peak in spectrum.peak_list():
      center = peak.position
      count = count + 1
      label = '%d' % count
      s = strip(self.strips_frame, width, self.strip_gap, view, center, label)
      strips.append(s)
    self.replace_strips(strips)
    
# -----------------------------------------------------------------------------
#
class strip:

  def __init__(self, parent, strip_width, strip_gap,
               mimic_view, center, label_text):

    self.parent = parent
    self.strip_width = strip_width
    self.strip_gap = strip_gap
    self.mimic_view = mimic_view
    self.center = center
    self.label_text = label_text

    self.column = None
    self.label = None
    self.views = None
    self.needs_update = 0

  # ---------------------------------------------------------------------------
  #
  def __del__(self):

    self.delete_label()
    self.delete_views()

  # ---------------------------------------------------------------------------
  #
  def set_column(self, column):

    if column != self.column:
      self.column = column
      self.position_label()
      self.request_view_position()
    
  # ---------------------------------------------------------------------------
  # Defer view creation and deletion so scrolling through many strips
  # by dragging the slider remains responsive.
  #
  views_to_update = []
  def request_view_position(self):
    self.views_to_update.append(self)
    self.needs_update = 1
    if len(self.views_to_update) == 1:
      tkutil.after_idle(self.parent, self.update_views)
  def update_views(self):
    if self.views_to_update:
      strip = self.views_to_update[-1]
      del self.views_to_update[-1]
      if strip.needs_update:
        strip.position_views()
        strip.needs_update = 0
      if self.views_to_update:
        tkutil.after_idle(self.parent, self.update_views)
        
  # ---------------------------------------------------------------------------
  #
  def position_label(self):

    if self.column == None:
      self.delete_label()
    else:
      self.parent.columnconfigure(self.column, minsize = self.strip_width)
      self.create_label(self.parent, self.column)
      self.label.grid(row = 3, column = self.column, sticky = 'news')
        
  # ---------------------------------------------------------------------------
  #
  def create_label(self, parent, column):

    if self.label == None:
      self.label = Tkinter.Label(parent, text = self.label_text)

  # ---------------------------------------------------------------------------
  #
  def delete_label(self):

    if self.label:
      self.label.destroy()
      self.label = None

  # ---------------------------------------------------------------------------
  #
  def position_views(self):

    if self.column == None:
      self.delete_views()
    else:
      if self.views == None:
        self.views = self.create_views(self.parent)
      for v in range(3):
        self.parent.tk.call('grid', 'configure', self.views[v].frame,
                            '-row', v, '-column', self.column,
                            '-sticky', 'news',
                            '-padx', self.strip_gap/2,
                            '-pady', self.strip_gap/2)

  # ---------------------------------------------------------------------------
  #
  def create_views(self, parent):

    views = []
    axis_order = (0, 1, 2)

    for v in range(3):
      view = self.create_view(parent, axis_order)
      axis_order = axis_order[1:] + (axis_order[0],)  # Permute axis order
      views.append(view)

    return views

  # ---------------------------------------------------------------------------
  #
  def create_view(self, parent, axis_order):

    spectrum = self.mimic_view.spectrum
    session = spectrum.session
    view = session.create_view(parent, spectrum)
    view.axis_order = axis_order
    view.center = self.center

    self.copy_view_options(self.mimic_view, view)

    #
    # Set the view frame size.
    # Don't listen to resize requests from view
    #
    size = self.view_height()
    tk = parent
    tkutil.tk_call(tk, view.frame, 'configure',
                   '-width', size, '-height', size)
    tkutil.tk_call(tk, 'grid', 'propagate', view.frame, 0)

    return view
  
  # ---------------------------------------------------------------------------
  #
  def resize(self, strip_width):

    self.strip_width = strip_width
    if self.views:
      size = self.view_height()
      for view in self.views:
        tk = view.session.tk
        tkutil.tk_call(tk, view.frame, 'configure',
                       '-width', size, '-height', size)
  
  # ---------------------------------------------------------------------------
  #
  def view_height(self):

    label_height = self.label.winfo_height()
    return self.strip_width - self.strip_gap - label_height / 3
  
  # ---------------------------------------------------------------------------
  #
  def copy_view_options(self, from_view, to_view):

    copy_attributes = ('pixel_size', 'visible_depth',
                       'positive_levels', 'negative_levels',
                       'show_ornaments', 'show_peaks', 'show_peakgroups',
                       'show_labels', 'show_lines', 'show_grids',
                       'show_crosshair', 'show_crosshair_from_other_views')
    
    for attr in copy_attributes:
      setattr(to_view, attr, getattr(from_view, attr))
  
  # ---------------------------------------------------------------------------
  #
  def delete_views(self):

    if self.views:
      for view in self.views:
        view.destroy()
      self.views = None

# -----------------------------------------------------------------------------
#
def show_peaks(session):

  view = session.selected_view()
  if view:
    d = sputil.the_dialog(view_3d_peaks, session)
    d.show_window(1)
    d.show_peaks(view)


