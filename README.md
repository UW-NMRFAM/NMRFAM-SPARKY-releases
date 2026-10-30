# NMRFAM-Sparky

NMRFAM-Sparky is a graphical program for the analysis of multidimensional NMR spectra, maintained by the National Magnetic Resonance Facility at Madison (NMRFAM), University of Wisconsin-Madison.

This repository contains the latest Linux release, including its own bundled Python 2.7, so no separate Python installation is needed.

## Requirements

- Ubuntu 20.04 LTS or newer
- `sudo` permissions

## Installation

1. Download this repository: click the green **Code** button above and choose **Download ZIP**, or clone it:

   ```bash
   git clone https://github.com/UW-NMRFAM/NMRFAM-SPARKY-releases.git
   ```

2. Extract the contents (if you downloaded the ZIP).

3. Open a terminal and go to the directory where you extracted the installer:

   ```bash
   cd NMRFAM-SPARKY-releases
   ```

4. Run the installer with the bundled Python, giving the destination directory. For example, to install in `/usr/local/sparky`:

   ```bash
   sudo python2.7/bin/python2.7 ./install.py /usr/local/sparky/
   ```

5. After the installation is complete, you should be able to run the program with the command:

   ```bash
   sparky
   ```

### If the `sparky` command is not found

Add the `bin` directory of your installation to your `PATH`. Using the example destination above:

- **tcsh/csh** — add this line to `~/.cshrc`:

  ```tcsh
  setenv PATH /usr/local/sparky/bin:${PATH}
  ```

- **bash** — add this line to `~/.bashrc`:

  ```bash
  export PATH=/usr/local/sparky/bin:$PATH
  ```

Then open a new terminal (or log out and back in).

## Possible issues during installation

You may need to install some additional libraries.

### PNG12 library

- 64-bit:

  ```bash
  sudo wget -q -O /tmp/libpng12.deb http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_amd64.deb && sudo dpkg -i /tmp/libpng12.deb
  ```

- 32-bit:

  ```bash
  sudo wget -q -O /tmp/libpng12.deb http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_i386.deb && sudo dpkg -i /tmp/libpng12.deb
  ```

### 32-bit compatibility libraries

Run these commands in a `bash` shell. Replace `<NMRFAM-SPARKY>` with your installation directory (for example, `/usr/local/sparky`):

```bash
sudo apt-get install lib32ncurses5 lib32stdc++6 lib32z1 lib32gcc1 libxrender1:i386 libx11-6:i386 libxft2:i386 gtk2-engines:i386 gtk2-engines-*:i386 libcanberra-gtk-module:i386 libgtkmm-2.4*:i386 libatk-adaptor:i386 libgail-common:i386
sudo cp /usr/lib32/libz.so.1 <NMRFAM-SPARKY>/lib/libz.so
```

## License

See the [LICENSE](LICENSE) file.
