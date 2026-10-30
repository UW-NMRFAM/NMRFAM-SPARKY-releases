# -----------------------------------------------------------------------------
# Show an extra "crosshair" like marker whose position is related to the
# position of the mouse.
#
# This is used for reduced dimensionality experiments where a peak appears
# at y-delta, y, and y+delta.  If you place a peak marker on the center peak
# and select it, then this code will show a crosshair-like marker at y-offset
# when the mouse is placed at y+offset.
#
# If you save a session with this extension active, the peak markers will
# be saved in the session file -- probably not what you want.
#

# -----------------------------------------------------------------------------
#
class mouse_tracker:

  def __init__(self, session):

    self.session = session

    self.delay = .1             # update time in seconds
    self.markers = {}           # maps spectrum to peak
    self.stop_checking = 0

    self.check_motion()
    
  # ---------------------------------------------------------------------------
  #
  def check_motion(self):

    if self.stop_checking:
      return
      
    self.move_marker()

    import Tkinter
    msec = int(1000 * self.delay)
    Tkinter._default_root.after(msec, self.check_motion)
    
  # ---------------------------------------------------------------------------
  #
  def move_marker(self):

    s = self.session

    peaks = s.selected_peaks()
    if len(peaks) != 1:
      self.remove_markers()
      return
    central_peak = peaks[0]
    nuclei = central_peak.spectrum.nuclei
    
    view = self.view_with_mouse()
    if view == None or view.spectrum.nuclei != nuclei:
      return

    mouse_pos = view.pointer_position
    if mouse_pos == None:
      return

    central_pos = central_peak.position
    axis = view.axis_order[1]           # screen y axis
    offset = mouse_pos[axis] - central_pos[axis]
    marker_pos = list(mouse_pos)
    marker_pos[axis] = central_pos[axis] - offset

    self.place_markers(marker_pos, nuclei)

  # ---------------------------------------------------------------------------
  #
  def view_with_mouse(self):

    s = self.session
    v = s.selected_view()
    if v.pointer_position:
      return v

    for v in s.project.view_list():
      if v.pointer_position:
        return v

    return None
  
  # ---------------------------------------------------------------------------
  # Place markers in all spectra which have matching nuclei on
  # each spectrum axis.
  #
  def place_markers(self, marker_pos, nuclei):

    remove = filter(lambda sp, n=nuclei: sp.nuclei != n, self.markers.keys())
    if remove:
      self.remove_markers()

    spectra = filter(lambda sp, n=nuclei: sp.nuclei == n,
                     self.session.project.spectrum_list())

    for sp in spectra:
      if self.markers.has_key(sp):
        self.markers[sp].position = marker_pos
      else:
        self.markers[sp] = sp.place_peak(marker_pos)

  # ---------------------------------------------------------------------------
  # Select the marker peak and send the delete key command.
  # This is to work around the fact that there is no Python interface to
  # delete a peak marker.
  #
  def remove_markers(self):

    peaks = self.markers.values()
    if peaks:
      s = self.session
      s.unselect_all_ornaments()
      escape = ''
      s.command_characters(escape)      # clear any partial command
      for p in peaks:
        p.selected = 1
      delete = ''
      s.command_characters(delete)
    self.markers = {}
    
  # ---------------------------------------------------------------------------
  #
  def quit(self):

    self.remove_markers()
    self.stop_checking = 1

# -----------------------------------------------------------------------------
#
mtracker = None
def make_crosshair(session):

  global mtracker
  if mtracker == None:
    mtracker = mouse_tracker(session)
  else:
    mtracker.quit()
    mtracker = None
