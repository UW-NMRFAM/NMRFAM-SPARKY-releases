# -----------------------------------------------------------------------------
# Command to put peak labels on all assigned peaks.
#

# -----------------------------------------------------------------------------
#
def label_assigned_peaks(session):

  if session.selected_spectrum() == None:
    return
  
  import sputil
  spectrum = session.selected_spectrum()
  for p in spectrum.peak_list():
    if not sputil.is_peak_unassigned(p):
      p.show_assignment_label()
