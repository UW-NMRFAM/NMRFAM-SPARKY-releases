#!/usr/bin/python

try:
  import argparse
except:
  print "Too old python is installed by default."
  print "Please run this way:"
  print "    $ sudo python2.7/bin/python2.7 ./install.py /usr/local/src"
  import sys
  sys.exit(1)

ap = argparse.ArgumentParser( description = "nmrfam-sparky installer" )
ap.add_argument( "-s", "--scripted", default = False, action = "store_true",
    help = "do not ask to install libraries", dest = "scripted" )
ap.add_argument( "instdir", metavar = "INSTALLATION DIR",
    help = "installation directory" )
args = ap.parse_args()

logo = """
************************************************
*                                              *
* NMRFAM-SPARKY 1.470 powered by Sparky 3.190  *
*                                              *
* Woonghee Lee (whlee@nmrfam.wisc.edu)         *
*                                              *
* NMRFAM & Biochem Dept.                       *
* University of Wisconsin-Madison              *
*                                              *
************************************************

Usage:

 $ sudo python ./install.py [INSTALLATION DIR]
 
 or
 
 # python ./install.py [INSTALLATION DIR] 

"""
ubuntu_list = []
ubuntu_list.append("apt-get -y install build-essential libgdk-pixbuf2.0-0 libgtk2.0-0 tcsh pymol")
ubuntu_list.append("apt-get -y install libqt5widgets5")
ubuntu_list.append("apt-get -y install libqt4-gui")
ubuntu_list.append("apt-get -y install libqtgui4")
ubuntu_list.append("apt-get -y install zlib1g")
ubuntu_list.append("apt-get -y install lib32ncurses5 lib32stdc++6 lib32z1 lib32gcc1")
ubuntu_list.append("apt-get -y install libstdc++6 libxrender1 libx11-6 libxft2")
ubuntu_list.append("apt-get -y gtk2-engines gtk2-engines-* libcanberra-gtk-module libgtkmm-2.4-* libatk-adaptor libgail-common")
ubuntu_list.append("apt-get -y install ia32-libs")

redhat_list = []
redhat_list.append("yum -y install glib gtk2 libSM")
redhat_list.append("yum -y install zlib-devel")
redhat_list.append("yum -y install qt")
redhat_list.append("yum -y install tcsh")
redhat_list.append("yum -y install dejavu-sans-fonts  dejavu-fonts-common fontpackages-filesystem")
redhat_list.append("yum -y install libpng12")
redhat_list.append("yum -y install openmotif.i386 libstdc++.i386 gtk2-engines.i386 gtk-murrine-engine.i386 gtk-equinox-engine.i386")
redhat_list.append("yum -y install openmotif.i686 libstdc++.i686 gtk2-engines.i686")
redhat_list.append("yum -y install openmotif libstdc++ gtk2-engines gtk-murrine-engine gtk-equinox-engine")

ns_binaries = ["bruk2ucsf","matrix2ucsf","pine2sparky","sparky","vnmr2ucsf","easy_bruk2ucsf","ndpplot","sparky-no-python","easy_pipe2ucsf","easy_ucsfdata","peaks2ucsf","pipe2ucsf","nv2ucsf","ucsfdata","PonderosaAnalyzer","PonderosaClient"]

try:
  print logo
except:
  print('System default for python is version 3 and this script is compatiable to version 2.')
  print('Please run like the following:')
  print('  $ sudo python2.7 ./install.py [INSTALLATION DIR]')
  import sys
  sys.exit()

import os, sys

try:
  import platform
  dist_tup = platform.linux_distribution()
  major_ver = int(dist_tup[1].split('.')[0])
except:
  major_ver = 0

current_file = os.path.realpath(__file__)
current_path = os.path.dirname(current_file)

if args.scripted :
  lib_yn = 'n'
else :
  try:
    lib_yn = raw_input('Dependent library installation: Is this your first installation (Y/n) ?')
    if lib_yn.lower()[0] == 'n': lib_yn = 'n'
    else: lib_yn = 'y'
  except:
    lib_yn = 'y'   

  if os.geteuid() != 0:
    print "Root privilege required."
    print "E.g. # sudo python ./install.py /usr/local/src"
    print "Exiting..."  
    sys.exit()
  
if (os.path.exists('/etc/redhat-release')) or (os.path.exists('/etc/fedora-release')):
  print "Redhat, Fedora or CentOS found."
  target_os = 'redhat'
elif (os.path.exists('/etc/lsb-release')) or (os.path.exists('/etc/debian-release')):
  print "Ubuntu or Debian found."
  target_os = 'ubuntu'
else:  
  print "Unsupported operating system."
  print "Please install required libraries."
  print "Note that we test this distribution on Ubuntu and CentOS."
  print "Exiting..."
  sys.exit()
    
try:  
  is_64bits = sys.maxsize > 2**32
except:
  print "Too old python is installed by default."
  print "Please run this way:"
  print "    $ sudo python2.7/bin/python2.7 ./install.py /usr/local/src"
  sys.exit()

if not is_64bits:
  print "This is 64bits version, but 32bits OS found."
  print "Exiting..."  
  sys.exit()  

# copy first
install_dir = args.instdir.rstrip('/')
install_dir = os.path.realpath(install_dir)
 
if (sys.argv[1].find('sparky') == -1) and (sys.argv[1].find('Sparky') == -1):
  install_dir = os.path.join(install_dir, 'nmrfam-sparky-linux')

install_lib_dir = os.path.join(install_dir, 'lib')
install_libs = os.path.join(install_lib_dir, 'libQt*')

if os.path.exists( os.path.join(install_dir, 'bin/sparky') ):
  # remove first
  cmd = "\\rm -rf %s" % install_dir
  print cmd
  os.system(cmd)
    
if current_path != install_dir:
  cmd = "\\cp -rf %s %s" % (current_path, install_dir)
  print cmd
  os.system(cmd)
  
# install libraries
lib_dir = os.path.join(install_dir, "lib")
bin_dir = os.path.join(install_dir, "bin")

  
if target_os == 'redhat':
  if lib_yn == 'y':
    for line in redhat_list:
      print line
      os.system(line)
    if os.path.exists('/usr/lib/libz.so.1'):
      cmd = '\\scp /usr/lib/libz.so.1 %s/libz.so' % (lib_dir)
    elif os.path.exists('/lib/libz.so.1'):
      cmd = '\\scp /lib/libz.so.1 %s/libz.so' % (lib_dir)    
    else: 
      print 'libz.so.1 not found...'
      cmd = ''
    print cmd
    os.system(cmd)
        
elif target_os == 'ubuntu':
  if lib_yn == 'y':
    print "apt-get update"
    os.system("apt-get update")
    if target_os == 'ubuntu' and major_ver >= 18:
      # png12 should be installed
      cmd = 'wget -q -O /tmp/libpng12.deb http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_amd64.deb && sudo dpkg -i /tmp/libpng12.deb'
      os.system(cmd)

    for line in ubuntu_list:
      print line
      os.system(line)
          
    if os.path.exists('/usr/lib64/libz.so.1'):
      cmd = '\\scp /usr/lib64/libz.so.1 %s/libz.so' % (lib_dir)
    elif os.path.exists('/lib/x86_64-linux-gnu/libz.so.1'):
      cmd = '\\ln -s /lib/x86_64-linux-gnu/libz.so.1 %s/libz.so' % (lib_dir)      
    else:
      print 'libz.so.1 not found...'
      cmd = ''      
    print cmd
    os.system(cmd)

# symlink...
print 'Creating sym links...'
for ns_binary in ns_binaries:
  link_path = '/usr/local/bin/' + ns_binary
  real_path = os.path.join(bin_dir, ns_binary)
  if os.path.exists(link_path):
    os.system('\\rm -rf ' + link_path)
  cmd = 'ln -s %s %s' % (real_path, link_path)
  print cmd
  os.system(cmd)
  
# QT libraries
# this is dependent on os versions
try:
  # we don't strictly install qt libraries for later release because QT4 will conflict
  if (target_os == 'redhat' and major_ver < 8) or (target_os == 'ubuntu' and major_ver < 6):
    cmd = 'cd /usr/local/lib; ln -s %s .' % (install_libs)
    print cmd
    os.system(cmd)
except:
  pass

# compile pythons
cmd = 'cd %s/python; ../python2.7/bin/python2.7 -m compileall .' % (install_dir)
print cmd
os.system(cmd)

print '\n\nPlease type sparky like the following to execute this program.\n'  
print '\n  $ sparky \n\n'  
print '\n\nPonderosa Client may need installation of QT4.8+ libraries.\n\n'  
#print '\nPlease add the following line in /etc/csh.cshrc\n\n'
#print '  setenv PATH ${PATH}:%s\n\n' % (bin_dir)
print 'Please cite the following paper:\n\n'
print '  NMRFAM-SPARKY: enhanced software for biomolecular NMR spectroscopy. Bioinformatics (2015) 31 (8): 1325-1327'
print '\n\nFinished.\n\n'


