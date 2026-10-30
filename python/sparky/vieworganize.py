# -----------------------------------------------------------------------------
# Organize views
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Jan 1, 2020 - in progress
#
#
# -----------------------------------------------------------------------------
# CITATION:
#          TBA
# -----------------------------------------------------------------------------

import Tkinter
import sparky
import tkutil
import sputil

# This function organizes neighboring views regarding selected view.
# For instance, 
#
#   v1     v2    v3
#       +-----+                 x1, y1    x2, y2    x3, y3
#   v4  |  v  |  v5             x4, y4    cx, cy    x5, y5
#       +-----+                 x6, y6    x7, y7    x8, y8
#   v6     v7    v8
#
#    
def get_distance_sqr(x, y, x2, y2):
  return (x-x2)*(x-x2)+(y-y2)*(y-y2)

def get_view_coords(session, view):
  w, h, x, y = tkutil.get_view_geometry(session, view)
  cx, cy = x+w/2, y+h/2
  return cx, cy, x, y, w, h

def get_vertex(session, coords, mode):
  cx, cy, x, y, w, h = coords
  if mode == 1: return x, y
  elif mode == 2: return cx, y
  elif mode == 3: return x+w, y
  elif mode == 4: return x, cy
  elif mode == 5: return x+w, cy
  elif mode == 6: return x, y+h
  elif mode == 7: return cx, y+h
  elif mode == 8: return x+w, y+h
  return cx, cy

def check_validity(session, coords, mode, view):
  # view center should not be closer to other vertex
  cx, cy, w, h = coords[0], coords[1], coords[4], coords[5] # selected
  x, y = get_vertex(session, coords, mode) # edge vertex
  coords2 = get_view_coords(session, view) # closest view coords
  cx2, cy2, w2, h2 = coords2[0], coords2[1], coords2[4], coords2[5]
  mode2 = counter_mode(mode)
  x2, y2 = get_vertex(session, coords2, mode2) # edge vertex

  std_dist_sqr = get_distance_sqr(x2, y2, x, y) # dist 
  if ((w+w2)*(w+w2)+(h+h2)*(h+h2))*4 < std_dist_sqr: return False # too far
  for i in range(1,9): # loop other mode and check if closer vertex exists
    if i == mode: continue
    x, y = get_vertex(session, coords, i)
    dist_sqr = get_distance_sqr(x, y, x2, y2) # dist to other edge
    if dist_sqr < std_dist_sqr:
      return False
  if mode == 1 and (cx2 >= cx or cy2 >= cy): return False
  elif mode == 2 and (cy2 >= cy): return False
  elif mode == 3 and (cx2 <= cx or cy2 >= cy): return False
  elif mode == 4 and (cx2 >= cx): return False
  elif mode == 5 and (cx2 <= cx): return False
  elif mode == 6 and (cx2 >= cx or cy2 <= cy): return False
  elif mode == 7 and (cy2 <= cy): return False
  elif mode == 8 and (cx2 <= cx or cy2 <= cy): return False
  return True

def counter_mode(mode):
  return 9-mode

def closest_view(session, notview, vl, mode):
  coords = get_view_coords(session, notview)
  vx, vy = get_vertex(session, coords, mode)
  mode2 = counter_mode(mode)

  cv, ccoords = None, None
  for v in vl:
    if v.name == notview.name: continue
    if v.is_top_level_window != 1: continue
    coords2 = get_view_coords(session, v)
    vx2, vy2 = get_vertex(session, coords2, mode2)
    dist_sqr = get_distance_sqr(vx, vy, vx2, vy2)
    if cv == None:
      min_dist_sqr = dist_sqr
      cv = v
      ccoords = coords2
    elif dist_sqr < min_dist_sqr:
      min_dist_sqr = dist_sqr
      cv = v
      ccoords = coords2
  return cv, ccoords

def organize_neighbor_views(session):
  v = session.selected_view()
  if v == None:
    return
  tbs = tkutil.get_title_bar_size(session, v)
  wbs = tkutil.get_window_border_size(session, v)

  coords = get_view_coords(session, v)
  cx, cy, x, y, w, h = coords
  x += wbs
  #y += tbs
  vl = session.project.view_list()
  for mode in range(1,9):
    # find closest & check if worthy to organize
    cv, ccoords = closest_view(session, v, vl, mode)
    if cv == None: continue
    if not check_validity(session, coords, mode, cv): continue
    cx2, cy2, x2, y2, w2, h2 = ccoords

    # organize
    # mode1: no resize
    if mode == 1: # match cv's x2+w2 and y2+h2 to x and y
      x2 = max(0, x-w2)
      y2 = max(0, y-h2-tbs)
    # mode2: width resize
    elif mode == 2: # match cv's x2 and y2+h2 to x and y
      x2 = x
      y2 = max(0, y-h2-tbs)
      w2 = w
    # mode3: no resize
    elif mode == 3: # match cv's x2 and y2+h2 to x+w and y
      x2 = x+w
      y2 = max(0, y-h2-tbs)
    # mode4: height resize
    elif mode == 4: # match cv's x2+w2 and y2 to x and y
      x2 = max(0, x-w2)
      y2 = y
      h2 = h
    # mode5: height resize
    elif mode == 5: # match cv's x2 and y2 to x+w and y
      x2 = x+w
      y2 = y
      h2 = h
    # mode6: no resize
    elif mode == 6: # match cv's x2+w2 and y2 to x and y+h
      x2 = max(0, x-w2)
      y2 = y+h+tbs
    # mode7: width resize
    elif mode == 7: # match cv's x2 and y2 to x and y+h
      x2 = x
      y2 = y+h+tbs
      w2 = w
    # mode8: no resize
    elif mode == 8: # match cv's x2 and y2 to x+w and y+h
      x2 = x+w
      y2 = y+h+tbs

    tkutil.set_view_geometry(session, cv, w2, h2, x2, y2)