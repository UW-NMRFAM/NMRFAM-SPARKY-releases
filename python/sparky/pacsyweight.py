# -----------------------------------------------------------------------------
# Layouts for weighting PACSY
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: September 8, 2014
#
# Usage:
#
#
# -----------------------------------------------------------------------------

#prev, curr, next, ss, phi, psi, buriedness, temp, ph, total
pacsy_weight_layout = {
  "C": (0.4, 0.6, 2.3, 8.1, 5.8, 13.9, 4.2, 0.0, 0.1, 35.4),
  "CA": (0.1, 11.6, 1.0, 0.1, 11.0, 10.4, 0.3, 0.0, 0.0, 34.5),
  "CB": (0.1, 0.3, 15.4, 0.1, 8.1, 5.7, 0.4, 0.0, 0.6, 30.7),
  "H": (0.4, 0.5, 0.3, 0.1, 4.4, 5.3, 0.0, 0.5, 0.6, 12.1),
  "HA": (0.2, 0.8, 0.7, 0.6, 29.9, 3.8, 0.6, 0.1, 0.2, 36.9),
  "N": (2.9, 3.4, 0.3, 0.0, 4.5, 7.1, 0.5, 0.0, 0.0, 18.7),
  "other": (0.1, 0.3, 15.4, 0.1, 8.1, 5.7, 0.4, 0.0, 0.6, 30.7),
}
pacsy_weight_type = ['prev', 'curr', 'next', 'ss', 'phi', 'psi', 'buriedness', 'temp', 'ph', 'total']
