
import sparky
import tkutil
# -----------------------------------------------------------------------------
#
def set_default_contour_levels(session):
  v = session.selected_view()
  if v == None:
    return
  
  lev = sparky.Contour_Levels()

  lev.lowest = v.spectrum.noise * 10 #5
  lev.factor = 1.4
  lev.levels = 14
  lev.color = 'red'

  v.positive_levels = lev

  lev.lowest = v.spectrum.noise * -10 # must be <0 to set negative levels
  lev.factor = 1.4
  lev.levels = 14
  lev.color = 'limegreen'

  v.negative_levels = lev

# -----------------------------------------------------------------------------
# Use uniform width and height
#
def uniform_size(session):
  v = session.selected_view()
  if v == None:
    return
  w, h, x, y = tkutil.get_view_geometry(session, v)
  vl = session.project.view_list()
  for v2 in vl:
    if v == v2: continue
    if v2.is_top_level_window != 1: continue
    w2, h2, x2, y2 = tkutil.get_view_geometry(session, v2)
    #geo = '%dx%d+%d+%d' % (w, h, x2, y2)
    tkutil.set_view_geometry(session, v2, w, h, x2, y2)
  
def uniform_view_windows(session):
  #uniform_size(session)
  #return
  v = session.selected_view()
  if v == None:
    return
  s = v.spectrum
  vl = session.project.view_list()
  nuc = ''
  for i in range(s.dimension):
    nuc += s.nuclei[v.axis_order[i]]
  for v2 in vl:
    if v == v2: continue
    if v2.is_top_level_window != 1: continue
    s2 = v2.spectrum
    if s.dimension != s2.dimension: continue
    nuc2 = ''
    for i in range(s2.dimension):
      nuc2 += s2.nuclei[v2.axis_order[i]]
    if nuc != nuc2: continue
    v2.center = v.center
    v2.pixel_size = v.pixel_size

# -----------------------------------------------------------------------------
# Use contour settings of current spectrum to set others uniformly.
#
def uniform_contours(session):
  v = session.selected_view()
  if v == None:
    return
  
  vp = v.positive_levels
  vn = v.negative_levels  

  vl = session.project.view_list()
  
  for v2 in vl:
    if v == v2: continue
    if v2.is_top_level_window != 1: continue
    # positive
    v2p = v2.positive_levels
    v2p.lowest = vp.lowest
    v2p.factor = vp.factor
    v2p.levels = vp.levels
    v2.positive_levels = v2p

    # negative
    v2n = v2.negative_levels
    v2n.lowest = vn.lowest
    v2n.factor = vn.factor
    v2n.levels = vn.levels
    v2.negative_levels = v2n
