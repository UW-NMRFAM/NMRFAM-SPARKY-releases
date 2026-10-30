# -----------------------------------------------------------------------------
# All the additional functions
# -----------------------------------------------------------------------------
#
# Updated by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Feb 12, 2019
#
# Usage:
#
#
# -----------------------------------------------------------------------------
# Sparky site initialization file.  The initialize_session routine in this
# file is invoked when a Sparky session is started.  We add menu entries
# for standard extensions.
#
import sys

import sparky

# -----------------------------------------------------------------------------
#
def initialize_session(session):
  nme = nmrfam_menu_entries()
  add_menu_entries(session, nme)
  sme = standard_menu_entries()
  add_menu_entries(session, sme)

# -----------------------------------------------------------------------------
#
def nmrfam_menu_entries():
  pine_menu = (
    ('n1', '>>> Automated BB and SC assignment: I-PINE',  ('nmrfam', 'about_pine')),
    ('ep', 'Run I-PINE automated assignment (PINE-SPARKY 2)',  ('pinenmr', 'run_pine')),
    ('ip', 'Convert I-PINE to SPARKY resonance list file', ('pineassign', 'convert_pine_to_sparky')),
    ('fp', 'I-PINE sequence formatting',  ('myseq', 'PineSeqFormatting')),
    ('n2', '>>> Visual verification: PINE-SPARKY', ('nmrfam', 'about_pinesparky')),
    ('p2', 'Run PINE2SPARKY converter',   ('nmrfam', 'run_pine2sparky')),
    ('pr', 'Pine assigner',               ('pineassign', 'show_pine_assigner')),
    ('pp', 'Pine graph assigner',         ('pinegraph', 'show_pine_graph')),
    ('ab', 'Assign the best by I-PINE',   ('pineassign', 'best_assign')),
    ('se', 'Select all floating I-PINE labels',('selector', 'select_all_float_labels')),
  )
  fastassignment_menu = (
    ('n3', '>>> Superfast assignment with PACSY',       ('nmrfam', 'about_nmrfamsparky')),
    ('dg', 'Dummy graph',                               ('pinegraph', 'show_dummy_graph')),
    ('ta', 'Transfer and simulate assignments',         ('tan','TAN')),
    ('ut', 'Untag _s',                                  ('tan','UNTAG_S')),
    ('cu', 'Center and Untag _s',                       ('tan','CENTER_AND_UNTAG_S')),
    ('su', 'Select unconfirmed peaks with _s tag', ('selector', 'select_unconfirmed')),
    ('mt', 'Merge two assignments to a pseudoatom',     ('tan','MERGE_TWO_H')),
    ('va', 'Versatile assigner',              ('aapredict','show_aa_predictor')),
    ('E1', '>>> Structure based chemical shift predictor: SHIFTX2 from Wishart Lab.',  ('nmrfam', 'about_shiftx2')),
    ('PA', 'About PACSY...', ('nmrfam', 'about_pacsy')),
  )
  validate_menu = (
    ('LA', '>>> Assignment outlier detection and correction of errors in referencing: LACS',    ('nmrfam', 'about_lacs')),
    ('lv', 'Run LACS validation',                   ('strpredict', 'run_lacs')),
    ('AA', '>>> Assessment of the reliability of chemical shift assignments: ARECA',    ('nmrfam', 'about_areca')),
    ('ea', 'Run ARECA chemical shift validator',                 ('ponderosa', 'ponderosa_cs')),
    ('ar', 'Use ARECA output list',                                  ('areca', 'show_areca')),
  )
  structcalc_menu = (
    ('n4', '>>> Automated structure calculation: PONDEROSA',  ('nmrfam', 'about_ponderosa')),
    ('c3', 'Calculate 3D structure by PONDEROSA',       ('ponderosa', 'ponderosa_cs')),
    ('cp', 'Run Ponderosa Client',                      ('nmrfam', 'run_ponderosa_client')),
    ('up', 'Ponderosa Connector',                       ('connect_ponderosa', 'connect_ponderosa_analyzer')),
    ('gd', 'Generate Distance Constraints and White Lists for PONDEROSA', ('upl_lol', 'generate_upl_lol')),
    ('cy', 'Cyana2Sparky format',       ('readcyana','read_cyana_peak_list')),
    ('xe', 'XEASY, DYANA format',       ('xeasy','show_dialog')),
    ('xf', 'Manual restraint format',   ('xplor','show_dialog')),
    ('sr', 'Extract phi-psi and accessible surface info from PDB with STRIDE', ('nmrfam','run_stride')),
    ('hd', 'HADDOCK docking webserver', ('nmrfam','go_haddock')),
  )
  structpred_menu = (
    ('n5', '>>> Structure prediction',  ('nmrfam', 'about_pecan')),
#    ('n6', 'Export to PECAN and go PECAN webserver',  ('strpredict', 'export_pecan')),
    ('n6', 'Run PECAN 2D structure prediction',  ('strpredict', 'run_pecan')),
    ('gb', '2D structure prediction with GetSBY', ('getsby', 'run_getsby')),
    ('gc', 'Secondary chemical shift analysis', ('scshift', 'show_scshift')),
    ('gp', 'Export to PACSY-ALIGN and go PACSY-ALIGN webserver',  ('strpredict', 'export_pacsyalign')),
    ('ce', '3D structure prediction with CS-Rosetta (BMRB)', ('csrosetta', 'export_csrosetta')),
#    ('nm', 'NMR-like 3D structure prediction with PONDEROSA', ('nmrfam', 'go_ponderosamodel')),
    ('nm', 'NMR-like 3D structure prediction with PONDEROSA', ('pondpred', 'run_pondpred')),
    ('tl', 'phi-psi prediction with TALOS-N (NIH)', ('talos', 'export_talos')),
    ('tn', 'Generate NDP-PLOT and PyMOL files with TALOS-N files', ('talos', 'generate_ndpplots_for_talosn')),
    ('PP', 'Secondary structure prediction with PSIPRED (UCL)', ('nmrfam', 'run_psipred')),
    ('dp', 'Detect proline isomerization state', ('proline_state', 'proline_cis_trans')),
  )
  largeprot_menu = (
    ('n7', '>>> SCAssign from Yang Lab for large proteins', ('nmrfam', 'about_SCAssign')),
    ('sn', 'Sidechain assignment with 4D-NOESY and CCH-TOCSY', ('sidechain_assign', 'show_sidechain_assign_dialog')),
  )
  idpprot_menu = (
    ('n8', '>>> ncIDP-assign from Mulder Lab for IDP proteins', ('nmrfam', 'about_ncidpassign')),
    ('RS', 'ncIDP Repositioner 1.2b',       ('reposition_ncIDP', 'show_repositioner')),
    ('SG', 'ncIDP Spin Graph 1.2b',         ('assigngraph_ncIDP','show_assigner')),
    ('nc', 'ncSPC Propensity Calculator',   ('talos', 'export_ncspc')),
  )
  nucleicacid_menu = (
    ('N1', '>>> Nucleic acid analysis',  ('nmrfam', 'about_rnapairs')),
    ('ER', 'Export to RNA-PAIRS input files', ('rnapairs', 'export_rnapairs')),
    ('SE', 'Show statistical ellipses for RNA analysis', ('nucleicacid', 'show_ellipse_dialog')),
    ('DG', 'Dummy graph for nucleic acids',       ('pinegraph', 'show_dummy_graph_for_na')),
  )
  perturb_menu = (
    ('FA', 'Assign N-HSQC arbitrarily', ('npdplot', 'fake_assign')),
    ('np', 'NMR Perturbation Plot', ('npdplot', 'show_npd_dialog')),
    ('ni', 'NMR Titration Plot', ('ntdplot', 'show_ntd_dialog')),
    ('rh', 'Peak Height Analysis', ('relax', 'show_peak_heights')),
    ('eo', 'Easy overlay dialog', ('adv_overlay', 'show_adv_overlay')),
    ('ec', 'Easy contour dialog', ('adv_contour', 'show_adv_contour')),
    ('rd', 'RDC tool', ('rdctool', 'show_rdc_dialog')),
    ('ch', 'CHESCA-SPARKY', ('chesca_sparky', 'show_chesca_dialog')),
    ('cH', 'CHESPA-SPARKY', ('chesca_sparky', 'show_chespa_dialog')),
  )
  ssnmr_menu = (
    ('PS', 'PISA-SPARKY: automated PISA wheel analysis',
           ('bagel_sparky', 'show_dialog')),
  )
  util_menu = (
    ('do', 'Paste files in the clipboard to open all at once', 	('dropopen','drop_open')),
    ('ae', 'Automated peak picking by APES', ('apes','show_apes')),
    ('ca', 'Check protein assignment nomenclature', ('check_nomen', 'check_protein_nomen')),
    ('ck', 'Check resonance deviations', ('checkres', 'show_res_dialog')),
    ('TB', 'Assignment table', ('asgntbl', 'show_assignment_table')),
    ('cm', 'Assignment Completeness', ('completeness', 'show_assignment_completeness')),
    ('ir', 'Import BMRB reference views', ('nmrfam', 'import_reference_view')),
    ('sq', 'Molecule sequence',         ('sequence','show_sequence_dialog')),
    ('rn', 'Renumber sequence indices', ('myseq', 'RenumberSeqIndices')),
    ('od', '1D inspector', ('one_dim_inspect','show_1D_inspect')),
    ('er', 'Convert XEASY prot to SPARKY resonance list file', ('xeasyprot', 'ConvertProtToSparky')),
    ('gx', 'Generate XEASY prot file', ('xeasyprot', 'GenerateXeasyProt')),
    ('Pm', 'Generate a mmCIF(PDBx) file from a PDB file', ('wlutil','generate_mmcif_from_pdb')),
    ('Pp', 'Generate a PDB file from a mmCIF(PDBx) file', ('wlutil','generate_pdb_from_mmcif')),
    ('fP', 'Format PostScripts', ('format_postscripts','show_formatPS_dialog')),
#    ('ip', 'Integrate Peak List', ('integratepeaklist', 'IntegratePeakList')),
    ('Pu', 'Easy pipe2ucsf', ('nmrfam','run_pipe2ucsf')),
    ('Bu', 'Easy bruk2ucsf', ('nmrfam','run_bruk2ucsf')),
    ('Du', 'Easy ucsfdata', ('nmrfam','run_ucsfdata')),
    ('dn', 'Deposit NMR data to BMRB', ('nmrfam', 'deposit_data')),
    ('cf', 'Command finder', ('command_finder', 'show_commandfind_dialog')),
    ('RD', 'Change SPARKYHOME', ('nmrfam', 'change_sparkyhome')),
    ('LF', 'Change look and feel', ('lookfeel', 'show_look_and_feel')),
  )
  universal_format_menu = (
    ('ns', 'Convert NMRSTAR 3.1 chemical shift to SPARKY resonance list file', ('nmrstar', 'ConvertBmrbToSparky')),
    #('cn', 'Convert NMRSTAR 3.1 peak list to SPARKY peak list file', ('nmrstar', 'ConvertNmrStarPeak')),
    ('es', 'Generate NMRSTAR 3.1 chemical shift file', ('nmrstar', 'GenerateNmrStar')),
    ('bp', 'Parse NMRSTAR 3.2 file', ('bmrbfile', 'show_bmrb_parse')),
    ('bg', 'Generate NMRSTAR 3.2 file', ('bmrbfile', 'GenerateNmrStar32')),
    #('en', 'Generate NMRSTAR 3.1 peak list file', ('nmrstar', 'GenerateNmrStarPeak')),
    ('ef', '>>> About NMR Exchange Format', ('nmrfam', 'about_nef')),
    ('e1', 'Export sequence only to NEF', ('nmref', 'export_nef_seq')),
    ('e2', 'Export sequence and chemical shifts to NEF', ('nmref', 'export_nef_seq_cs')),
#    ('e3', 'Export peak lists', ('nmref', 'export_nef_peaks')),
    ('i1', 'Convert NEF sequence to 3-letter-code format', ('nmref', 'export_nef_to_seq')),
    ('i2', 'Convert NEF chemical shifts to Sparky resonance list', ('nmref', 'export_nef_to_rlist')),
#    ('i3', 'Convert NEF peak list to Sparky peak list', ('nmref', 'export_nef_to_plist')),
  )
  aboutnmrfam_menu = (
    ('n9', '>>> Support NMRFAM',  ('nmrfam', 'about_nmrfam')),
    ('n0', 'Citations...',        ('nmrfam', 'credit_nmrfam_dialog')),
    ('nN', 'NMRFAM webpage',      ('nmrfam', 'about_nmrfam')),
    ('nM', 'NMRFAM-SPARKY manual',('nmrfam', 'about_nmrfamsparky')),
    ('TT', 'Video Tutorials',     ('nmrfam', 'videotutorial_nmrfam')),
    ('LC', 'NMRFAM-SPARKY Basics', ('lectures', 'show_protein_nmr_lecture_dialog')),
    ('SF', 'Sparky user forum',   ('nmrfam', 'sparkyforum')),
    ('dN', 'Download NMRFAM software packages',  ('nmrfam', 'download_nmrfam')),
  )
  separate_menu = (
    ('99', 'NMRFAM menu start', ('nmrfam', 'about_nmrfam')),
  )
  separate_menu2 = (
    ('00', 'NMRFAM menu end', ('nmrfam', 'about_nmrfam')),
  )

  menus = (
    ('', separate_menu),
    ('Automated assignment', pine_menu),
    ('Superfast assignment', fastassignment_menu),
    ('Chemical shift validation', validate_menu),
    ('Structure calculation', structcalc_menu),
    ('Structure prediction', structpred_menu),
    ('Large protein analysis', largeprot_menu),
    ('Disordered protein analysis', idpprot_menu),
    ('Perturbation analysis', perturb_menu),
    ('Nucleic acid analysis', nucleicacid_menu),
    ('Solid-state NMR spectroscopy', ssnmr_menu),
    ('Utilities', util_menu),
    ('Universal NMR formats', universal_format_menu),
    ('About NMRFAM-SPARKY', aboutnmrfam_menu),
    ('', separate_menu2),
    )
  return menus
# -----------------------------------------------------------------------------
#
def standard_menu_entries():

  assignment_menu = (
    ('ad', 'Assignment distances',      ('distance','show_dialog')),
    ('SN', 'PDB2NOE',                   ('pdb2noe','show_dialog')),
    ('aa', 'AutoAssign',                ('autoassign','show_dialog')),
    ('cs', 'Chemical shift plot',       ('chemshift','show_shifts_dialog')),
    ('bm', 'Load BMRB STAR file',       ('bmrbstar', 'show_dialog')),   # From Chad Rienstra
    ('md', 'Mirror peak dialog',	      ('mirror','show_mirror_dialog')),
    ('mp', 'Mirror peak show',          ('mirror','show_mirror_peak')),
    ('na', 'Noesy assignment',          ('noesyassign','show_dialog')),
    ('rs', 'Reposition sequence',       ('reposition','show_repositioner')),
    ('sg', 'Spin graph',		            ('spingraph','show_spin_graph')),
    ('ga', 'Spin graph assigner',       ('assigngraph','show_assigner')),
    ('pq', 'PluqIn-Sparky',             ('sparky_pluqin','show_dialog')), # From Chad Rienstra
    ('lA', 'Label Assigned Peaks', ('labelpeaks','label_assigned_peaks')),
    )

  integration_menu = (
    ('cl', 'Copy linewidths',           ('copylinewidth',
                                         'copy_linewidths_and_positions')),
    ('lp', 'Linewidth plot',            ('linewidthplot',
                                         'show_linewidth_dialog')),
    ('rh', 'Relaxation peak heights',   ('relax','show_peak_heights')),
    ('ve', 'Volume errors',             ('volumeerror',
                                         'show_volume_error_dialog')),
    )

  molecule_menu = (
    ('ax', 'Atom name translation',     ('atoms','show_translations_dialog')),
    ('km', 'Chimera molecule view',     ('chimeraview','show_chimera_dialog')),
    ('mc', 'Midas constraints',         ('midasconstraint',
                                         'show_constraint_dialog')),
    ('ma', 'Midas atom picking',	      ('midaspick','show_atom_pick_dialog')),
    ('sq', 'Molecule sequence',         ('sequence','show_sequence_dialog')),
    ('SA', 'Sequence alignment',        ('sequencealign', 'show_sequencealignment_dialog')),
    ('pn', 'PDB atom names',            ('pdb','show_pdb_atom_dialog')),
    )

  peak_menu = (
    ('hc', 'HC peaks',                  ('hcpeaks','show_dialog')),
    ('SL', 'List selected peaks',  	    ('peaklist','show_selected_peaks')),
    ('dd', 'Delete duplicate peaks',    ('selector', 'remove_unnecessary_duplicates')),
    ('mf', 'MARDIGRAS format',          ('mardigras','show_dialog')),
    ('LT', 'Peak list',         	      ('peaklist','show_spectrum_peaks')),
    ('pb', 'Peak table',		            ('peaktable','show_peak_table')),
    ('rp', 'Read peak list',       	    ('readpeaks','read_peak_list')),
    ('kr', 'Restricted peak pick',      ('restrictedpick','show_dialog')),
    ('mv', 'Shift resonances',          ('movepeaks','show_move_peak_dialog')),
    ('tf', 'TALOS format',              ('talos2', 'show_dialog')),    # From Chad Rienstra
    ('qn', 'Add single quote note',     ('quotenote', 'add_single_quote_note')),
    ('v3', 'Show 3D peaks',             ('view3dpeaks', 'show_peaks')),
    ('p3', 'Project a 3D peak onto 2D', ('peakto2d', 'show_dialog')),
    ('TP', 'Transfer a peak',           ('peakto2d', 'show_transfer_peak_dialog')),
    ('cc', 'Coupling constants',        ('coupling', 'show_coupling_dialog')),
    ('xe', 'XEASY, DYANA format',       ('xeasy','show_dialog')),
    ('xf', 'Manual restraint format',   ('xplor','show_dialog')),
    ('z5', 'IDAP 1D NMR',               ('IDAP_1D_NMR','run')),
    ('zs', 'Display heights as a function of data point',   ('display_heights_vs_index','show_dialog')),
    ('iP', 'iPick peak picker',         ('ipick_gui_sparky', 'show_ipick_dialog')),
    )

  selection_menu = (
    ('AS', 'Advanced Selection',        ('selector', 'show_dialog')), # From Chad Rienstra
    ('sb', 'Select bigger peaks',       ('wlutil', 'select_big')),
    ('ss', 'Select smaller peaks',      ('wlutil', 'select_small')),
    ('SB', 'Select same sign bigger peaks',       ('wlutil', 'select_big_same_sign')),
    ('SS', 'Select same sign smaller peaks',      ('wlutil', 'select_small_same_sign')),
    ('sF', 'Select all floating labels',('selector', 'select_all_float_labels')),
    ('sL', 'Select all labels attached to peaks', ('selector', 'select_all_attached_labels')),
    ('sO', 'Select all ornaments',      ('selector', 'select_all_ornaments')),
    ('sG', 'Select all grids',          ('selector', 'select_all_grids')),
    ('sN', 'Select all lines',          ('selector', 'select_all_lines')),
    ('sA', 'Select all assigned peaks', ('selector', 'select_all_assigned_peaks')),
    ('Sa', 'Select all unassigned peaks',         ('selector', 'select_all_unassigned_peaks')),
    ('sB', 'Select all user-labeled peaks',  ('selector', 'select_all_userlabeled_peaks')),
    ('Sb', 'Select all non-user-labeled peaks',  ('selector', 'select_all_nonuserlabeled_peaks')),
    ('su', 'Select unconfirmed peaks with _s tag', ('selector', 'select_unconfirmed')),
    ('uP', 'Unselect all peaks',        ('selector', 'unselect_all_peaks')),
    ('Sl', 'Select labels of selected peaks',     ('selector', 'select_labels_of_selected_peaks')),
    )

  spectrum_menu = (
    ('al', 'Align spectrum',            ('align','show_shift_dialog')),
    ('cx', 'CORMA spectrum',            ('cormaspectrum',
                                         'show_corma_spectrum')),
    ('fm', 'Open multiple files', 	    ('openspectra','show_file_dialog')),
    ('la', 'Spectrum labelled axis',    ('axes','show_attached_axis_dialog')),
    ('rm', 'Spectrum region RMSD',      ('regionrmsd',
                                         'show_region_rmsd_dialog')),
    ('dc', 'Default contour levels',    ('contourdefaults', 'set_default_contour_levels')),
    )

  fold_menu = (
    ('f1', 'Add w1 sweepwidth',         ('foldspectrum',
                                         'fold_selected_spectrum', 0, 1)),
    ('f2', 'Add w2 sweepwidth',         ('foldspectrum',
                                         'fold_selected_spectrum', 1, 1)),
    ('f3', 'Add w3 sweepwidth',         ('foldspectrum',
                                         'fold_selected_spectrum', 2, 1)),
    ('f4', 'Add w4 sweepwidth',         ('foldspectrum',
                                         'fold_selected_spectrum', 3, 1)),
    ('F1', 'Subtract w1 sweepwidth',    ('foldspectrum',
                                         'fold_selected_spectrum', 0, -1)),
    ('F2', 'Subtract w2 sweepwidth',    ('foldspectrum',
                                         'fold_selected_spectrum', 1, -1)),
    ('F3', 'Subtract w3 sweepwidth',    ('foldspectrum',
                                         'fold_selected_spectrum', 2, -1)),
    ('F4', 'Subtract w4 sweepwidth',    ('foldspectrum',
                                         'fold_selected_spectrum', 3, -1)),
    )

  view_menu = (
    ('cv', 'Center view setup',         ('centerview','center_view_setup')),
    ('rx', 'Reflection crosshair',      ('crosshair', 'make_crosshair')),
    ('sp', 'Strip plot',                ('strips','show_strip_plot')),
    ('SP', 'Additional strip plot',     ('strips2','show_strip_plot')),
    ('Sp', 'Another additional strip plot',     ('strips3','show_strip_plot')),
    ('dh', 'Draw a center horizontal line', ('sputil', 'draw_horz_line_on_selected_view')),
    ('dv', 'Draw a center vertical line', ('sputil', 'draw_vert_line_on_selected_view')),
    ('tc', 'Type center chemical shifts', ('sputil', 'center_by_shifts')),
    ('uc', 'Uniform contour settings',  ('contourdefaults', 'uniform_contours')),
    ('us', 'Uniform view sizes',  ('contourdefaults', 'uniform_size')),
    ('uv', 'Uniform view extents',  ('contourdefaults', 'uniform_view_windows')),
    ('on', 'Organize neighboring views',  ('vieworganize', 'organize_neighbor_views')),
    ('da', 'Auto-adjust view ratio by peaks',   ('viewutils', 'auto_view_ratio')),
    ('PV', 'Filterable View List',      ('viewlist', 'show_viewlist_dialog')),
    ('tv', 'Tree View',      ('treeviewlist', 'show_treeviewlist_dialog')),
    )

  top_menu = (
    ('py', 'Python shell',              ('pythonshell','show_python_shell')),
    )

  additional_menu = (
    ('ms', 'Mouse chemical shift',      ('mouseshift', 'show_shift_dialog')),
    ('ob', 'Open from clipboard...',    ('openfromclipboard', 'show_open_from_clipboard')),
  )

  #
  # The menu list consists of pairs having a menu path and entry list.
  # The menu path describes where under the Extension menu the entries should
  # appear.  An empty menu path puts the entries in the Extension menu.  If
  # the menu path is 'Spectrum' the entries are put in a cascaded menu called
  # Spectrum.  A menu path of 'Spectrum/Fold' puts the entries in a Fold menu
  # cascaded under the spectrum menu.
  #
  import os
  if os.name == 'posix':
    menus = (
      ('',                        top_menu),
      ('Assignment',              assignment_menu),
      ('Integration',             integration_menu),
      ('Molecule',                molecule_menu),
      ('Peak',                    peak_menu),
      ('Spectrum',                spectrum_menu),
      ('Spectrum/Fold spectrum',  fold_menu),
      ('View',                    view_menu),
      ('Reproducibility', (
        ('au', '>>> About UCONN Connjur' ,  ('nmrfam'     , 'about_connjur'  )),
        ('re', 'Snapshot dialog' ,  ('r_main'     , 'show_snapshot_dialog'  )),
        ('rg', 'Group dialog',      ('r_group'    , 'show_group_dialog'     )),
        ),
      ),
      ('Selection',               selection_menu),    # Chad Rienstra and Woonghee Lee
      ('Additional',              additional_menu),   # Chad Rienstra and Woonghee Lee
    )
  else:
    menus = (
      ('',                        top_menu),
      ('Assignment',              assignment_menu),
      ('Integration',             integration_menu),
      ('Molecule',                molecule_menu),
      ('Peak',                    peak_menu),
      ('Spectrum',                spectrum_menu),
      ('Spectrum/Fold spectrum',  fold_menu),
      ('View',                    view_menu),
      ('Selection',               selection_menu),    # Chad Rienstra and Woonghee Lee
      ('Additional',              additional_menu),   # Chad Rienstra and Woonghee Lee
    )

  return menus

# -----------------------------------------------------------------------------
#
def add_menu_entries(session, menu_list):

  for menu_path, entries in menu_list:
    for accelerator, menu_text, function_spec in entries:

      if menu_path:
        path = menu_path + '/' + menu_text
      else:
        path = menu_text

      def func(module_name = function_spec[0],
               function_name = function_spec[1],
               session = session,
               extra_args = function_spec[2:]):
        import pythonshell
        pythonshell.invoke_module_function(session, module_name, function_name,
                                           (session,) + extra_args)

      session.add_command(accelerator, path, func)
