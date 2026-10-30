# -----------------------------------------------------------------------------
# Import the Sparky C++ module called spy, and define start_session().
#
# The module 'spy' written in C++ defines the classes and functions for
# accessing Sparky data.  See the python directory README file for a
# description of the spy interface.
#
import os
import sys
import types
import threading

#
# Sparky 3.113 fails to start on Windows Vista ("python.exe stopped working"
# message) unless Tkinter is imported before spy module.  This may be related
# to initialization of the Tcl/Tk libraries.
#
import Tkinter

from spy import *

# -----------------------------------------------------------------------------
# Add user Python directory to the sparky module search path.
# This allows the user to copy extensions to their Sparky home directory
# and modify them, and have them override the distribution code.
#
user_python_path = os.path.join(user_sparky_directory, 'Python')
__path__.insert(0, user_python_path)

# -----------------------------------------------------------------------------
# Sparky session objects.  Multiple Sparky sessions can be run in the same
# Python interpretter.  This variable is primarily for data exploration in
# the Python shell.  You need a Session object to explore the Sparky data.
# However, we do not really run multiple sessions IRL. 
session_list = []
main_session = None

# -----------------------------------------------------------------------------
# Start the Sparky user interface and Python shell dialog.
# The Python shell dialog imports the site and user startup code.
#
def start_session(use_command_line = 1, redirect_stdio = 1,
                  start_event_loop = 1):

  if use_command_line:
    args = sys.argv[1:]
  else:
    args = []

  argv = ['sparky'] + args

  import tkutil
  tk = tkutil.initialize_tk(argv)
  
  # -----------------------------------------------------------------------------
  # Try to obtaion NMRFAM news
  #
  import nmrfam
  news_file = os.path.join(user_sparky_directory, 'nmrfam_news')
  nmrfam_msg = nmrfam.retrieve_nmrfam_news(news_file)    

  session = Session(tk)
  session.tk = tk
  session_list.append(session)
  main_session = session # map main_session

  import lookfeel
  lookfeel.handle_arabic(main_session)
  
  import pythonshell
  pythonshell.initialize_shell(session, redirect_stdio)

  if nmrfam_msg == '': # too short
    nmrfam_msg = """
Fonts, colors, panel sizes adjustable (type LF)
Find more commands (type cf)

Modern laptops: holding a Fn key may be required for pointer mode.

Please cite NMRFAM-SPARKY paper to support this development.
Lee et al. Bioinformatics 2015 Apr; 31(8):1325-7

To share the thoughts, visit Sparky user forum (Type SF).
New user group: https://groups.google.com/forum/#!forum/nmr-sparky
"""
    your_build = nmrfam.check_install_date(__file__)
    nmrfam_msg += your_build
  main_session.report_information(nmrfam_msg)

  for file in args:
    session.open_file(file)

  if start_event_loop:
    Tkinter.mainloop()              # Returns when user quits Sparky
          
# -----------------------------------------------------------------------------
# Specify what object attributes to return when repr(object) called.
#
def object_pretty_print():

  show_attributes(Project, 'save_path')
  show_attributes(Spectrum, 'name', 'dimension', 'data_size', 'nuclei',
                  'region', 'condition', 'molecule', 'data_path', 'save_path')
  show_attributes(Peak, 'assignment', 'frequency', 'spectrum',
                  'data_height', 'volume')
  show_attributes(Resonance, 'name', 'frequency', 'deviation', 'condition')
  show_attributes(Label, 'text', 'selected', 'color')
  show_attributes(Line, 'start', 'end', 'selected', 'color')
  show_attributes(Grid, 'position', 'axis', 'selected', 'color')
  show_attributes(Molecule, 'name')
  show_attributes(Group, 'name', 'number', 'symbol', 'molecule')
  show_attributes(Atom, 'name', 'group', 'molecule')
  show_attributes(Condition, 'name', 'molecule')
  show_attributes(View, 'name', 'spectrum', 'is_shown', 'center', 'pixel_size')

# -----------------------------------------------------------------------------
# Set an object's __repr__ method to a function showing the specified
# attributes.
#
def show_attributes(c, *attr):

  c.pretty_string_attributes = attr
  c.__dict__['__repr__'] = pretty_instance_string

# -----------------------------------------------------------------------------
# Return a pretty string representation for a class instance
# The pretty_string_attributes member of the instance lists the attributes
# to include in the string.
#
# A bug in Tkinter 1.127 causes the event loop to exit if an exception
# is thrown in a callback, and printing that exception throws another
# exception.  Printing some exceptions, like KeyError causes a value,
# possibly a Sparky object to be printed.  If that object no longer
# exists in C++ this code will throw an exception.  This code must
# avoid throwing exceptions to prevent improper event loop exits.
#
def pretty_instance_string(instance):

  lines = ''

  if object_exists(instance):
    for attr in instance.pretty_string_attributes:
      value = getattr(instance, attr)
      if type(value) == types.InstanceType:
        classname = value.__class__.__name__
        vstring = '<' + classname
        if hasattr(value, 'name'):
          vstring = vstring + ' ' + value.name
        vstring = vstring + '>'
      else:
        vstring = repr(value)
      lines = lines + '  ' + attr + ' : ' + vstring + '\n'
  else:
    lines = '  deleted Sparky object\n'

  classname = instance.__class__.__name__

  return '< ' + classname + '\n' + lines + '>'

# -----------------------------------------------------------------------------
#
object_pretty_print()
