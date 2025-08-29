# LECO - Laboratory Experiment Control Protocol
Design notes for a generic communication protocol to control experiments and measurement hardware.


## Introduction

This initiative was born out of a desire of PyMeasure developers, contributors and users to achieve improved and more flexible experiment orchestration/execution, and to achieve (better) interoperation with other instrument control libraries.

LECO is meant to be a specification for a (programming-language-independent) protocol to enable users to run experiments with a number of hardware devices, including logging, data storage, plotting, and GUI.

[PyMeasure](https://pymeasure.readthedocs.io) is an obvious candidate for working with this protocol, and as such will influence the design somewhat, but we will take pains to make sure the protocol will be agnostic to the actual interface package (or language) used.
The authors draw on their varied experience setting up such solutions in a number of research laboratories.


## Overview

This is an overview over the LECO protocol.
See the [documentation](https://leco-laboratory-experiment-control-protocol.readthedocs.io/en/latest/) for a more exhaustive description of the protocol and its elements.

Communication happens via messages (using [zeromq](https://zeromq.org/)) between participants (called _Component_) in a single application or distributed over the network.

There exist two different communication protocols in LECO.
1. The _control protocol_ allows to exchange messages between any two _Components_ in a LECO network, which is useful for controlling devices.
   The default implementation uses _remote procedure calls_ according to [JSON-RPC](https://www.jsonrpc.org/specification).
2. The _data protocol_ is a broadcasting protocol to send information to all those, who want to receive it, which is useful for regular measurement data or for log entries.
   It allows to implement event notifications.

A LECO network needs at least one _Coordinator_ (server), which routes the messages among the connected _Components_.

Each _Component_ has a name unique in the network, by which it may be addressed.
This name consists of the name of the _Coordinator_ (_Namespace_) they are connected to and their own name.
For example `N1.component1` is the full name of `component1` connected to the _Coordinator_ of the _Namespace_ `N1`.
That _Coordinator_ itself is called `N1.COORDINATOR`, as _Coordinators_ are always called `COORDINATOR`.


## Implementations

There are LECO implementations in the following languages:

- **Python**: [PyLECO](https://github.com/pymeasure/pyleco), a complete suite of Coordinators and Component building blocks.
- **Rust**: [RuLECO](https://github.com/BenediktBurger/ruleco), Coordinator and a few Component building blocks.
- **Labview**: [Labview Python Interfaces](https://git.rwth-aachen.de/nloqo/labview-python-interfaces), contains a data protocol publisher.


## Building Documentation

This repository contains the source files for the LECO protocol documentation.
To build the documentation locally, you'll need to set up a Python environment with the required dependencies.

### Using Conda (Recommended for consistency with Read the Docs)

1. Install [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge)
2. Create the environment from the provided `environment.yml`:
   ```bash
   mamba env create -f environment.yml
   ```
3. Activate the environment:
   ```bash
   mamba activate leco-protocol
   ```

### Using Pip

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the environment:
   ```bash
   # On Linux/macOS:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```

### Building the Documentation

Once you have set up the environment using either method above, you can build the documentation:

```bash
make html
```

The built documentation will be available in the `_build/html` directory.
Open `_build/html/index.html` in your browser to view it.
