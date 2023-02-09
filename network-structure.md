# Network structure

## Message Layer
The Message Layer is the communication layer that concerns itself with (de)composition, validation, serialisation, etc. of LECO Messages (see {ref}`messages.md#messages`).

## Transport Layer
The Transport Layer is the communication layer that transports LECO Messages between Components, making use of routing information in the Message header.
This uses zeromq or simpler localised methods, see the section "Message Transport Mode".

## Node
A Node is a local context in which (part of) a LECO deployment runs. 
This may be a single application using one or more threads or processes. 

A LECO network has one or more Nodes.
Components within a Node use the Distributed Message Transport (DMT/"distributed mode", the default) or the Local Message Transport (LMT/"local mode") to communicate with each other, see below.
All Components of a Node must use the same Message Transport Mode.

:::{admonition} Note
LMT details are still notional and undefined, for now the spec focuses on DMT. 
In the future this might be relaxed, so that Components within a Node might operate in different modes.
:::
:::{admonition} TODO
Decide how we track which Node a Component belongs to, and how the mode information propagates within a Node.
:::

## Multi-Node networks
Every Component (except for Control Coordinators) is connected to exactly one Control Coordinator. 
The Control Coordinators are connected to each other, such that any Component may only send a message to any other Component via their respective Control Coordinators.
Put differently, Components may only communicate to outside their Node via a Control Coordinator in their Node.

In this graph, messages would pass from `Component1` to `Coordinator1` to `Coordinator2` to the destination `Component4`.

:::{mermaid}
flowchart LR

    subgraph Node1
        Component1 -- "connects to" --- Coordinator1
        Component2 -- "connects to" --- Coordinator1
    end
    Coordinator1 -- "coordinates with" --- Coordinator2
    subgraph Node2
        Coordinator2 -- "connects to" --- Component3
        Coordinator2 -- "connects to" --- Component4
    end
:::

Control Coordinator to Control Coordinator communication always uses DMT.

## Message Transport Mode (LMT/DMT)

The Node-local Message Layer can have a local or distributed mode.

### Distributed Message Transport (DMT)

The Distributed Message Transport works within or across Nodes.
It uses [Zmq](https://zeromq.org/) sockets for the communication. For more details see the [zmq guide](https://zguide.zeromq.org/) or [zmq API](http://api.zeromq.org/)

Zmq messages consist in a series of frames, each is a byte sequence.
In this documentation, the separation between frames is indicated by `|`.
An empty frame is indicated with two frame separators `||`, even at the beginning or end of a message.
For example, the message `||Second frame|Third frame||Fifth frame` consists of 5 frames, with the first and fourth frames being empty frames.

For some useful information see our {ref}`appendix.md#zmq`.


### Local Message Transport (LMT)

The Local Message Transport only works within a Node _and_ within a process.
Local Message Transport options include queues between threads/processes and zeromq inproc.
:::{admonition} Warning
LMT details are still notional and not to be relied upon this will be fleshed out at a later date. 
The list of LMT options is not definitive yet.
:::
