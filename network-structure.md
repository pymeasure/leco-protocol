# Network structure

## Message Layer
The Message Layer is the communication layer that concerns itself with (de)composition, validation, serialisation, etc. of ECP Messages (see {ref}`messages.md#messages`).

## Transport Layer
The Transport Layer is the communication layer that transports ECP Messages between Components, making use of routing information in the Message header.
This uses zeromq or simpler localised methods, see the section "Message Transport Mode".

## Node
A Node is a local context in which (part of) an ECP deployment runs. 
This may be a single application using one or more threads or processes. 

An ECP network has one or more Nodes.
Components within a Node may use the Local Message Transport (LMT/"local mode") or the Distributed Message Transport (DMT/"distributed mode") to communicate with each other, see below.
All Components of a Node must use the same Message Transport Mode.
:::{admonition} Note
In the future this might be relaxed, so that Components within a Node might operate in different modes.
:::
:::{admonition} TODO
Decide how we track which Node a Component belongs to, and how the mode information propagates within a Node.
:::

### Bridging Coordinator
Messages _between_ Nodes must be transferred between Nodes from the source Node's Coordinator to the destination Node's Coordinator.
Coordinator-Coordinator communication always uses DMT.
Put differently, Components may only communicate to outside their Node via a Coordinator in their Node.

## Message Transport Mode (LMT/DMT)
The Node-local Message Layer can have a local or distributed mode.
The Local Message Transport (LMT) only works within a Node.
The Distributed Message Transport (DMT, using the zeromq TCP protocol) also works across Nodes. 
Local Message Transport options include zeromq inproc, zeromq IPC, and queues between threads/processes.
:::{admonition} Note
The list of LMT options is not definitive yet.
:::
