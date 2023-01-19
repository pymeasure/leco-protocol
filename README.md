# experiment_control_protocol
Design notes for a generic communication protocol to control experiments and measurement hardware.

This initiative was born out of a desire of PyMeasure developers, contributors and users to achieve improved and more flexible experiment orchestration/execution, and to achieve (better) interoperation with other instrument control libraries.

ECP is meant to be a specification for a (programming-language-independent) protocol to enable users to run experiments with a number of hardware devices, including logging, data storage, plotting, and GUI.
Communication will happen via messages (probably using [zeromq](https://zeromq.org/)) between participants in a single application or distributed over the network.

[PyMeasure](https://pymeasure.readthedocs.io) is an obvious candidate for working with this protocol, and as such will influence the design somewhat, but we will take pains to make sure the protocol will be agnostic to the actual interface package (or language) used.
The authors draw on their varied experience setting up such solutions in a homebrew fashion.
