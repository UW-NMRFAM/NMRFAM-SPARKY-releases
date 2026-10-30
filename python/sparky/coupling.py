# -----------------------------------------------------------------------------
# Display separation in Hz between the most recent two selected peaks.
#
import Tkinter

import pyutil
import sparky
import sputil
import tkutil


# -----------------------------------------------------------------------------
# January 25, 2019 by Woonghee Lee
# Added chemical shifts (ppm) & intensities as well
#
# -----------------------------------------------------------------------------
#
class coupling_constants(tkutil.Dialog):

  # ---------------------------------------------------------------------------
  #
  def __init__(self, session):

    self.session = session
    self.peaks = [None, None]

    tkutil.Dialog.__init__(self, session.tk, 'Coupling Constants')

    self.peak_lines = [Tkinter.Label(self.top, text = 'Peak 1'),
		       Tkinter.Label(self.top, text = 'Peak 2')]
    self.peak_lines[0].pack(side = 'top', anchor = 'w')
    self.peak_lines[1].pack(side = 'top', anchor = 'w')

    self.separation = Tkinter.Label(self.top, text = 'Difference (Hz): ')
    self.separation.pack(side = 'top', anchor = 'w')
    
    self.separation2 = Tkinter.Label(self.top, text = 'Difference (ppm): ')
    self.separation2.pack(side = 'top', anchor = 'w')
    
    self.separation3 = Tkinter.Label(self.top, text = 'Difference (height): ')
    self.separation3.pack(side = 'top', anchor = 'w')
    
    self.selection_notice = \
      self.session.notify_me('selection changed', self.peak_selected_cb)

    w = Tkinter.Button(self.top, text = 'Close', command = self.close_cb)
    w.pack(side = 'top', anchor = 'w')

  # ---------------------------------------------------------------------------
  #
  def peak_selected_cb(self):

    if self.is_window_destroyed():
      self.session.dont_notify_me(self.selection_notice)
      self.selection_notice = None
      return

    peaks = self.session.selected_ornaments()
    if len(peaks) != 1 or peaks[0].__class__ != sparky.Peak:
      return
    peak = peaks[0]

    self.peaks[0] = self.peaks[1]
    self.peaks[1] = peak

    self.show_peak_line(0)
    self.show_peak_line(1)

    if self.peaks[0] and self.peaks[1]:
      freq0 = self.peaks[0].frequency
      freq1 = self.peaks[1].frequency
      dh0 = self.peaks[0].data_height
      dh1 = self.peaks[1].data_height
      f = []
      cs = []
      hz_per_ppm = peak.spectrum.hz_per_ppm
      for a in range(min(len(freq0), len(freq1))):
        f.append((freq1[a] - freq0[a]) * hz_per_ppm[a])
        cs.append(freq1[a] - freq0[a])
        
      line = ('Difference (Hz): %16s' % pyutil.sequence_string(f, ' %7.3f'))
      line2 = ('Difference (ppm): %16s' % pyutil.sequence_string(cs, ' %7.3f'))
      line3 = ('Difference (height): %16d' % (dh0-dh1))
      self.separation['text'] = line
      self.separation2['text'] = line2
      self.separation3['text'] = line3

  # ---------------------------------------------------------------------------
  #
  def show_peak_line(self, n):

    peak = self.peaks[n]
    line = 'Peak %d:' % (n+1)
    if peak:
      line = line + (' %20s %16d' % (peak.assignment + \
        pyutil.sequence_string(peak.frequency, '% 7.3f'), peak.data_height))
    self.peak_lines[n]['text'] = line

# -----------------------------------------------------------------------------
#
def show_coupling_dialog(session):
  sputil.the_dialog(coupling_constants,session).show_window(1)

