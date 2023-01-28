# Glossary

An alphabetical list of terms with a short description.
To help distinguish between the plain English meaning of these terms, and our more specific use, we Capitalize terms
from this glossary when we refer to the ECP-specific meaning, similar to a Python class.

(glossary)=
:::{glossary}

Actor  
    A Component that offers a standardized interface to the ECP network to communicate with some Device. This
    happens via a Driver contained in the Actor, see {ref}`components.md#actor`. An Actor implements the
    mapping/translation between ECP messages and the Driver's interface.

Component  
    A Component is the logical block that makes up the block diagram of an experiment control network. The different
    component types, subclasses of Component, are listed in see {ref}`components.md#components`. A Component 
    communicates with other Components over an Interface to pass Messages.

Coordinator
    A Component primarily concerned with routing/coordinating the message flow, see {ref}`components.md#coordinator`.

Device
    Hardware controlled by a Driver, for instance a test instrument.

Director
    A Component which takes part in orchestrating a (i.e. ECP-controlled) measurement setup, see
    {ref}`components.md#director`.

Driver
    An object that takes care of communicating with a Device. This object is external to ECP, for example coming from and
    instrument control library like `pymeasure`, `instrumentkit` or `yaq`. See {ref}`components.md#driver`.

ECP
    The **E**xperiment **C**ontrol **P**rotocol framework.

Interface
    The communication methods that a Component can receive or transmit to other Components. 

Network
    The web of Components communicating with each other in an ECP deployment.

Observer
    A Component that receives data from other Components, e.g. for logging, storage, or plotting, see
    {ref}`components.md#observer`.

Processor
    A Component on the ECP network which runs some kind of processing operation on one or more inputs and produces one or
    more outputs. Can be stateful or stateless. See {ref}`components.md#processor`.
:::
