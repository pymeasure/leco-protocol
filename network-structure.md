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
Components within a Node may use the Local Message Transport (LMT/"local mode") or the Distributed Message Transport (DMT/"distributed mode") to communicate with each other, see below.
All Components of a Node must use the same Message Transport Mode.
:::{admonition} Note
In the future this might be relaxed, so that Components within a Node might operate in different modes.
:::
:::{admonition} TODO
Decide how we track which Node a Component belongs to, and how the mode information propagates within a Node.
:::

## Multi-Node networks
Every Component (except for Coordinators) is connected to exactly one Coordinator. 
The Coordinators are connected to each other, such that any Component may only send a message to any other Component via their respective Coordinators.
Put differently, Components may only communicate to outside their Node via a Coordinator in their Node.

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

Coordinator-Coordinator communication always uses DMT.

## Message Transport Mode (LMT/DMT)
The Node-local Message Layer can have a local or distributed mode.
The Local Message Transport (LMT) only works within a Node.
The Distributed Message Transport (DMT, using the zeromq TCP protocol) works within or across Nodes.
Local Message Transport options include zeromq inproc, zeromq IPC, and queues between threads/processes.
:::{admonition} Note
The list of LMT options is not definitive yet.
:::
