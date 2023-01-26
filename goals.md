# Goals
To guide the design of the specification, here we have articulated the high-level goals of this protocol.

## Tying diverse solutions together
First and foremost, we want to enable various, existing solutions in the lab automation niche to interoperate, irrespective of programming language, application niche (GUI, driver, orchestration, data storage,...) or project origin.

In the past, we have [observed](https://github.com/pymeasure/python-lab-automation-landscape) that the lab automation landscape, at least in Python, is quite fragmented.
As it has turned out unrealistic to unify/agglomerate these efforts into larger, and thus more resilient, projects, we have changed tack.
We want to enable users to pick drivers from some instrument control libraries with a reasonably homogeneous/simple API, a nice GUI from another project, and a data storage solution from elsewhere, and tie them together to serve the needs of _their_ setup.

[PyMeasure](https://pymeasure.readthedocs.io) is our project, so we know it best, and this will surely influence the design effort.
Also, we plan a reference implementation in Python that will also probably be primarily tested with PyMeasure.
However, we intend PyMeasure to be only one of _many_ "customer" libraries that can interface with ECP.

This specification will be independent of the programming language its Components are written in, so it will be possible to mix-and-match.
Instead of implementing all the necessary Components, we want to give the communication tools to connect everything, to balance on the shoulders of giants.

## Small to medium-sized use cases
We want ECP to serve laboratory setups of up to approximately 50 participants on one or more computation Nodes on a common network.
For example, you might have up to ~dozens of instruments, a few data acquisition nodes, one or several GUIs and control nodes.

## Flexible and modular
"LEGO"-like modularity is important. We want to reassemble, change the constellation of devices, easily adapt to changing experiments, data rate needs, etc.

We want people to easily be able to write their own software implementing (parts of) this protocol, for example to create just the GUI tool that they need.

We want ECP to be very lightly coupled to the used software (like instrument driver libraries) -- we want to thinly wrap these with some interface code that is written (ideally) _once_.
Given some instrument control library with a reasonably homogeneous/simple API, it should be easy to write an Actor variant to connect that library's Drivers with our Actor interface.

## Simple, yet powerful
You can send a message to any Component by specifying its (possibly human-readable) name or ID, similar to email.

We will have a default interpretation of the message content to implement remote procedure call (RPC), i.e. to set/read properties or call methods.

## Fast yet reliable
We want to communicate asynchronously and concurrently: The Director might want to send several commands to different devices at the same time, without waiting for the answer of a (slow) instrument before writing to the next one.
This way, communication delays will be determined by the slowest instrument, not by the number of instruments.

Messages should be reliably delivered by the protocol and not lost (barring network problems, crashing Components, hardware failure, etc.).

A failing node should not corrupt the measurement data acquired until then.

## Onboarding experience
We want to leave the entry threshold as low as possible, the learning curve flat, and the usability of ECP modular.

For simple measurements, a user should just need to download a package, write a little code to connect to the hardware with an Actor and a Driver from some instrument control library (e.g. a `pymeasure.Instrument`), and measure some things using the Actor interface.
This assumes that an Actor variant interfacing to the given instrument control library has already been implemented.

It should be possible to slowly scale up -- start with a single instrument that you exchange messages with, then add more Actors, a data sink, and a Director for control.

## Non-goals
It's also important to be aware of what _not_ to do.
This is our list:

Huge setups: We don't want to scale to large setups above O(50-100) Components.
Such deployments are probably better served by projects like Tango, EPICS, Sardana, Bluesky, etc..

Deployment of individual Components: We currently have no plans to specify how the various Components, possibly across multiple programming languages and operating systems, should be deployed/compiled/brought up. At first at least, this specification concerns itself with the interoperation of the various participants in the network.

Unit conversion: Getting involved with unit conversion or computations with units is out of scope.
Propagating unit information is possible and optional, but the specification will not deal with unit conversion or computation.
