# OpenDSSDirect.py
[![Travis Build Status](https://travis-ci.com/dss-extensions/OpenDSSDirect.py.svg?branch=master)](https://travis-ci.com/dss-extensions/OpenDSSDirect.py)
[![Appveyor Build Status](https://ci.appveyor.com/api/projects/status/github/dss-extensions/OpenDSSDirect.py?branch=master&svg=true)](https://ci.appveyor.com/project/PMeira/opendssdirect-py)
[![codecov](https://codecov.io/gh/dss-extensions/OpenDSSDirect.py/branch/master/graph/badge.svg)](https://codecov.io/gh/dss-extensions/OpenDSSDirect.py)
[![PyPI](https://img.shields.io/pypi/v/OpenDSSDirect.py.svg)](https://pypi.python.org/pypi/OpenDSSDirect.py/)
[![Documentation](https://img.shields.io/badge/docs-ready-blue.svg)](http://dss-extensions.github.io/OpenDSSDirect.py)

OpenDSSDirect.py is a cross-platform Python package implements a "direct" library interface to [OpenDSS](http://smartgrid.epri.com/SimulationTool.aspx) using [dss_python](https://github.com/dss-extensions/dss_python/).
OpenDSS is an open-source distribution system simulator. See [OpenDSSDirect.jl](https://github.com/dss-extensions/OpenDSSDirect.jl) for a similar package in Julia.

**This package is available for Windows, Mac and Linux.**

### Documentation

The documentation for this package can be found [here](http://dss-extensions.github.io/OpenDSSDirect.py).

### Installation

**Recommended**: Install Python using Miniconda or Anaconda

Open a command line interface and type the following.

```bash
pip install 'OpenDSSDirect.py[extras]'
```

See [installation](https://dss-extensions.github.io/OpenDSSDirect.py/notebooks/Installation.html) instructions for more information.

### Troubleshooting

It is recommended to use `conda` to install pandas, which is currently a dependency of this package.
This package interfaces with OpenDSS using the "direct" library interface, so a good understanding of OpenDSS will help troubleshooting.
There are plenty of useful resources located [here](https://sourceforge.net/p/electricdss/code/HEAD/tree/trunk/Doc/).

If you are having issues using this Python interface, feel free to open an Issue on GitHub [here](https://github.com/dss-extensions/OpenDSSDirect.py/issues/new).

### Thanks

Thanks to @tshort, Davis, @temcdrm, @GordStephen, @Muxelmann and @PMeira for their contributions.

See @Muxelmann's repo [here](https://github.com/Muxelmann/OpenDSSDirect.make) on how to build OpenDSS for Linux.

See @PMeira's repo [here](https://github.com/dss-extensions/dss_python) for the interface used in this package.

See @PMeira's repo [here](https://github.com/dss-extensions/electricdss-src) for changes to OpenDSS for maintaining cross platform compatibility.
