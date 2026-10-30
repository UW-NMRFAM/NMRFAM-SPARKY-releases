# -----------------------------------------------------------------------------
#
# The "Add single quote note" command qn goes through the peaks in all open
# spectra and adds notes.  If a peak assignment contains a group with a suffix
# ' (single quote char) then it adds a ' (single quote char) to the end of the
# note for that peak.
#
# This was written to flag peaks in peak lists with alternate resonance
# assignments so they can be filtered out based on their note.
#

def add_single_quote_note(session=session):
  for s in session.project.spectrum_list():
    for p in s.peak_list():
      has_quote = 0
      for r in p.resonances():
        if r and r.group.suffix == "'":
          has_quote = 1
      if has_quote:
        p.note = p.note + " '"

