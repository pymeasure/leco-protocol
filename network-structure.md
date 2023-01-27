# Network structure

## Node
A Node is a local context in which (part of) an ECP deployment runs. 
This may be a single application using one or more threads or processes. 
An ECP network has one or more Nodes. 
If it has a single Node, its Components may use the Local Message Transport (LMT/"local mode"), see below. 
If it has multiple Nodes, they must use the Distributed Message Transport (DMT/"distributed mode").

(TBC) Optional feature "Bridging Coordinator": In a DMT network, if the Components of a Node use local mode, only a Coordinator in that Node may use DMT to bridge messages to/from other Nodes. Put differently, Components in local mode may only communicate to outside their Node via a Coordinator in their Node.
:::{admonition} TODO
Decide if we include the Bridging Coordinator concept (I think we will).
:::
:::{admonition} TODO
Decide if the "mode" is the same for all Components in a Node, and if yes, how we track which Node a Component belongs to, and how the mode information propagates within.
:::

## Message Layer
The Message Layer is the communication layer that concerns itself with ECP message (de)composition, validation, serialisation, etc.

## Transport Layer
The Transport Layer is the communication layer that transports ECP messages between Components.
This uses zeromq or simpler localised methods, see the next section "Message Transport Mode".

## Message Transport Mode (LMT/DMT)
The Node-local Message Layer can have a local or distributed mode.
The Local Message Transport (LMT) only works within a Node.
The Distributed Message Transport (DMT, using the zeromq tcp protocol) also works across Nodes. 
Local Message Transport options include zeromq inproc, zeromq IPC, and queues between threads/processes.
