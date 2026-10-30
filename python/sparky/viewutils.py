# -----------------------------------------------------------------------------
# View utils
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: November 23, 2019
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import tkMessageBox

# automatically set aspect ratio using selected peaks
def auto_view_ratio(session):
  selected_view = session.selected_view()
  if selected_view == None: 
    tkMessageBox.showerror('No peaks', 'No selected peaks to look over.')
    return
  spec = selected_view.spectrum
  selected_peaks = spec.selected_peaks()
  fit_peaks, unfit_peaks, used_peaks = [], [], []
  for peak in selected_peaks:
    if peak.fit_height != None:
      fit_peaks.append(peak)
      used_peaks.append(peak)
      peak.selected = 0
    else:
      unfit_peaks.append(peak)
      peak.fit(selected_view)
      if peak.fit_height != None:
        used_peaks.append(peak)
        peak.selected = 1
      else:
        peak.selected = 0

  if len(used_peaks) == 0: 
    tkMessageBox.showerror('No peaks', 'No selected peaks to look over.')
    return

  # use averaged linewidth 
  avg_lw = list(map(lambda x: 0.0, range(spec.dimension)))
  ratio = list(map(lambda x: 1.0, range(spec.dimension)))
  for peak in used_peaks:
    for i in range(spec.dimension):
      avg_lw[i] += peak.line_width[i]
  session.command_characters("pU")
  for i in range(spec.dimension):
    avg_lw[i] /= float(len(used_peaks))
    ratio[i] = avg_lw[i] / avg_lw[0]
  cur_pixels = selected_view.pixel_size
  new_pixels = list(cur_pixels)
  for i in range(spec.dimension):
    new_pixels[i] = cur_pixels[0] * ratio[i]
  selected_view.pixel_size = tuple(new_pixels)

