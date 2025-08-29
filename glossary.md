# Glossary

An alphabetical list of terms with a short description.
To help distinguish between the plain English meaning of these terms, and our more specific use, we Capitalize terms from this glossary when we refer to the LECO-specific meaning.

:::{glossary}

Actor
    An Actor offers a standardized interface to the LECO network to communicate with some Device. This happens via a Driver contained in the Actor, see {ref}`components.md#actor`. An Actor implements the mapping/translation between LECO messages and the Driver's interface.

Component
    A type of entity, a set of which make up the LECO communication Network, see {ref}`components.md#components`.

Component name
    The individual name in a Node, under which a Component can be addressed, see {ref}`control_protocol.md#naming-scheme`.

Coordinator
    A Component primarily concerned with routing/coordinating the message flow between other Components, see {ref}`components.md#coordinator`.
    There are Control Coordinators, Data Coordinators, and Logging Coordinators.

Device
    Some piece of hardware controlled by a Driver.

Director
    A Component which takes part in orchestrating a (i.e. LECO-controlled) measurement setup, see {ref}`components.md#director`.

Directory
    Each Coordinator maintains a local Directory with all the Components connected to it (i.e. other Coordinators and the Components of its own Node), and a global Directory with all Components in the whole Network, see {ref}`control_protocol.md#directory`.

Driver
    An object that takes care of communicating with a Device. This object is external to LECO, for example coming from and instrument control library like `pymeasure`, `instrumentkit` or `yaq`. See {ref}`components.md#driver`.

Full name
    The name of a Component unique for the whole setup.
    It consists of the namespace and component-name, see {ref}`control_protocol.md#naming-scheme`.

LECO
    The **L**aboratory **E**xperiment **CO**ntrol protocol framework.

Message
    A LECO Message is one set of data transmitted from one Component to another, see {ref}`messages.md#messages`.
    Messages are broadly divided into three categories or "channels": control, data, and logging messages.

Message Layer
    The Message Layer is the communication layer that concerns itself with LECO message (de)composition, validation, serialisation, etc., see {ref}`network-structure.md#message-layer`.
    :::{admonition} TODO
    This is maybe gonna use Avro, but we still need to hash that out.
    :::

Message Transport Mode (LMT/DMT)
    The Node-local Message Layer can have a local or distributed mode, see {ref}`network-structure.md#message-transport-mode-lmtdmt`.

Namespace
    The name of a Node in the Network, see {ref}`control_protocol.md#naming-scheme`.

Node
    A Node is a local context in which (part of) a LECO deployment runs.
    This may be a single application using one or more threads or processes.
    A LECO network has one or more Nodes, see {ref}`network-structure.md#node`.

Network
    The web of Components communicating with each other in a LECO deployment.

Observer
    A Component that receives data from other Components, e.g. for logging, storage, or plotting, see {ref}`components.md#observer`.

Processor
    A Component on the LECO network which runs some kind of processing operation on one or more inputs and produces one or more outputs. Can be stateful or stateless. See {ref}`components.md#processor`.

Transport Layer
    The Transport Layer is the communication layer that transports LECO messages between Components.
    This uses zeromq or simpler localised methods, see Message Transport Mode above. See {ref}`network-structure.md#transport-layer`.

:::
