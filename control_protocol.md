# Control protocol

The control protocol transmits messages via its {ref}`transport-layer` from one Component to another one.
The {ref]}`message-layer` is the common language to understand commands, thus creating a remote procedure call.


(transport-layer)=
## Transport layer

The transport layer ensures, that a message arrives its destination.


### Sockets and Connections

We use [zmq](https://zeromq.org/) sockets for our communication. For more details see the [zmq guide](https://zguide.zeromq.org/) or [zmq API](http://api.zeromq.org/)


#### Definitions

Zmq messages consist in a series of frames, each is a byte sequence.
We indicate the separation between frames with `|`.
An empty frame is indicated with two frame separators `||`, even at the beginning or end of a message.
For example `||Second frame|Third frame||Fifth frame` consists of 5 frames.
The first and fourth frames are empty frames.


#### Configuration

Each {ref}`Coordinator <components.md#coordinator>` shall offer one ROUTER socket, bound to a host name (or IP address or any address of a computer with "*") and port in the DMT.

{ref}`Components <components.md#components>` shall have one DEALER socket connecting to one Coordinator's ROUTER socket.

Coordinators shall have one DEALER socket per other Coordinator in the network.
This DEALER socket shall connect to the other Coordinator's ROUTER socket.

Messages must be sent to a Coordinator's ROUTER socket.


#### Particularities of ROUTER sockets

A small introduction to ROUTER sockets, for more details see [zmq guide chapter 3](https://zguide.zeromq.org/docs/chapter3/#Exploring-ROUTER-Sockets).

A router socket assigns a random identity to each connecting peer.
If, for example, two Components `CA`, `CB` connect to the ROUTER sockets, the socket assigns the identities, which we call `IA`, `IB` (they can be any bytes sequence).

Whenever a message is sent to the ROUTER socket from a peer, it reads as a first frame that identity.
For example if `CA` sends the message `Request A`, the ROUTER socket will read `IA|Request A`.
That way, you can return an answer to exactly the original peer and not, for example `CB`.
If you call the ROUTER's send command with `IA|Reply A`, the socket will send `Reply A` to the peer, whose connection is `IA`, in this case `CA`.

The following diagram shows this example communication with two Components:
:::{mermaid}
graph TD
    CA([CA]) -->|"Request A"| D[recv] -->|"IA|Request A"| A([Coordinator])
    CB([CB]) -->|"Request B"| C[recv] -->|"IB|Request B"| A
    subgraph ROUTER socket
        B
        C
        D
        E
    end
    A -. "IA|Reply A" .-> B
    B[send] -. "Reply A" .-> CA
    A -. "IB|Reply B" .-> E
    E[send] -. "Reply B" .-> CB
:::


### Naming scheme

Each Component has an individual ID, given by the user, the Component ID.
A Component ID must be a series of bytes, without the ASCII character "." (byte value 46).
Component IDs must be unique in a Node, i.e. among the Componets connected to a single Coordinator.

As each Component belongs to exactly one Coordinator, it is fully identified by the combination of Node ID and Component ID.
This _full ID_ is the composition of Node ID, ".", and Component ID.

The receiver of a message may be specified without the Node ID, if the receiver lives in the same Node.

:::{note}
How to address the Coordinator? I used "no Recipient".
Or a fixed name?
:::


### Message composition

A message consists in two or more frames.
1. The receiver full ID.
2. The sender full ID.
3. Message content: The optional payload, which can be 0 or more frames.


### Conversation protocol

In the protocol examples, `CA`, `CB`, etc. indicate Components.
`Co1`, `Co2`, etc. indicate Coordinators.

Here the Message content is expressed in plain English, for the exact definition see {ref}`message-layer`.

In the exchange of messages, only the messages over the wire are shown, the connection identity of the ROUTER socket is not shown.


#### Communication with the Coordinator

##### Initial connection

After connecting to a Coordinator (`Co1`), a Component (`CA`) shall send a CONNECT message indicating its ID.
The Coordinator shall respond with an ACKNOWLEDGE, giving the Node ID and other relevant information, or with an ERROR, if the ID is already taken.
After that successful handshake, the Coordinator shall store the connection identity and correspondind Component ID in its address book.
:::{note}
publish that information
:::
Similarly, the Component shall store the Node ID and use it from this moment to generate its full ID.

:::{mermaid}
sequenceDiagram
    Note over CA,Co1: ID "CA" is still free
    CA ->> Co1: ||CA|CONNECT
    Note right of Co1: Connection identity "IA"
    Note right of Co1: Stores "CA" with identity "IA"
    Co1 ->> CA: Co1.CA||ACKNOWLEDGE: Node ID is "Co1"
    Note left of CA: Stores "Co1" as Node ID
    Note over CA,Co1: ID "CA" is already used
    CA ->> Co1: ||CA|CONNECT
    Co1 ->> CA: CA||ERROR: ID "CA" is already used.
    Note left of CA: May retry with another ID
:::


##### Heartbeat

We use heartbeat to know, whether a communication partner is still online.

Every message received counts as a heartbeat.

:::{note}
TBD: Respond to every non empty message with an empty one?
:::


##### Disconnecting

A Component should tell a Coordinator, when it stops working, with a DISCONNECT message.
The Coordinator shall ACKNOWLEDGE the disconnect and remove the ID from its address book.
:::{note}
publish that information
:::

:::{mermaid}
sequenceDiagram
    CA ->> Co1: ||Co1.CA|DISCONNECT
    Co1 ->> CA: Co1.CA||ACKNOWLEDGE
    Note right of Co1: Removes "CA" with identity "IA"<br> from address book
    Note left of CA: Shall not send any message anymore
:::


#### Communication with other Components

The following two examples show, how a message is transferred between two components `CA`, `CB` via one or two Coordinators.
Coordinators shall send messages from their DEALER socket to other Coordinator's ROUTER socket.

Coordinators shall hand on the message to the corresponding Coordinator or connected Component.


:::{mermaid}
sequenceDiagram
    CA ->> Co1: Co1.CB|Co1.CA| Give me property A.
    Co1 ->> CB: Co1.CB|Co1.CA| Give me property A.
    Note left of CB: Reads property A
    CB ->> Co1: Co1.CA|Co1.CB| Property A has value 5.
    Co1 ->> CA: Co1.CA|Co1.CB| Property A has value 5.
    Note over CA,Co1: The first message could be as well:
    CA ->> Co1: CB|Co1.CA| Give me property A.
:::


:::{mermaid}
sequenceDiagram
    CA ->> Co1: Co2.CB|Co1.CA| Give me property A.
    Note over Co1,Co2: Co1.DEALER socket sends to Co2.ROUTER
    Co1 ->> Co2: Co2.CB|Co1.CA| Give me property A.
    Co2 ->> CB: Co2.CB|Co1.CA| Give me property A.
    Note left of CB: Reads property A
    CB ->> Co2: Co1.CA|Co2.CB| Property A has value 5.
    Note over Co1,Co2: Co2.DEALER socket sends to Co1.ROUTER
    Co2 ->> Co1: Co1.CA|Co2.CB| Property A has value 5.
    Co1 ->> CA: Co1.CA|Co2.CB| Property A has value 5.
:::


The following flow chart shows the decision scheme and message modification in a Coordinator.
`IA` and `IB` are the connection identities of `CA` and `Co1.Recipient`.
Bold arrows indicate message flow, thin lines indicate decision flow.

:::{mermaid}
flowchart TB
    C([CA DEALER]) == "NodeID.Recipient|Co1.CA|Content" ==> R0
    R0[Co1 ROUTER receive] == "IA|NodeID.Recipient|Co1.CA|Content" ==> Code[remove sender identity]
    Code == "NodeID.Recipient|Co1.CA|Content" ==> NS
    NS -- "is None" --> Local
    NS{NodeID} -- "== Co1"--> Local
    Local{Recipient<br> is None} -- "yes" --> Self([Message for Co1<br> itself])
    Local -- "no" --> Local2
    Local2[add Recipient identity IB] == "IB|NodeID.Recipient|Co1.CA|Content" ==> R1[send]
    R1 == "NodeID.Recipient|Co1.CA|Content" ==> W1([Wire to Co1.Recipient DEALER])
    NS -- "== connected Coordinator Co2" --> Keep
    Keep[send to Coordinator Co2] == "NodeID.Recipient|Co1.CA|Content" ==> R2[send]
    R2 == "NodeID.Recipient|Co1.CA|Content" ==> W2([Wire to Co2 ROUTER])
    NS -- "reachable via Coordinator CoX" --> Augment
    Augment[send via CoX] == "NodeID.Recipient|Co1.CA|Content" ==> R3[send]
    R3 == "NodeID.Recipient|Co1.CA|Content"==> W3([Wire to CoX ROUTER])
    subgraph Co1 ROUTER socket
        R1
    end
    subgraph Co1 DEALER socket to Co2
        R2
    end
    subgraph Co1 DEALER socket to CoX
        R3
    end
:::



(message-layer)=
## Message layer

:::{note}
TODO
:::
