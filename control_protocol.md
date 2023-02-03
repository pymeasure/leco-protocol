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

Each {ref}`Coordinator <components.md#coordinator>` shall offer one ROUTER socket, bound to a host name (or IP address or any address of a computer with "*") and port.

{ref}`Components <components.md#components>` shall have one DEALER socket connecting to one Coordinator's ROUTER socket.

Coordinators shall have one DEALER socket per other Coordinator in the Network.
This DEALER socket shall connect to the other Coordinator's ROUTER socket.

Messages must be sent to a Coordinator's ROUTER socket.


(router-sockets)=
#### Particularities of ROUTER sockets

A small introduction to ROUTER sockets, for more details see [zmq guide chapter 3](https://zguide.zeromq.org/docs/chapter3/#Exploring-ROUTER-Sockets).

A router socket assigns a random _identity_ to each connecting peer.
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


### Protocol basics

#### Naming scheme

Each Component has an individual ID, given by the user, the _Component ID_.
A Component ID must be a series of bytes, without the ASCII character "." (byte value 46).
Component IDs must be unique in a {ref}`Node <network-structure.md#node>`, i.e. among the Componets connected to a single Coordinator.
The Coordinator itself has the Component ID `COORDINATOR`.
:::{note}
COORDINATOR is a placeholder for the final version.
:::

Also every Node ID has to be unique in the Network.
As each Component belongs to exactly one Coordinator, it is fully identified by the combination of Node ID and Component ID., which is globally unique.
This _full ID_ is the composition of Node ID, ".", and Component ID.
For example `Co1.CA` is the full ID of the Component `CA` in the Node `Co1`.

The receiver of a message may be specified without the Node ID, if the receiver lives in the same Node.


#### Message composition

A message consists in two or more frames.
1. The receiver full ID.
2. The sender full ID.
3. Message content: The optional payload, which can be 0 or more frames.


(address-book)=
#### Address book

Each Coordinator shall have a list of the Components connected to it.
This is its _local address book_.

The _global address book_ is the combination of the local address books of all Coordinators in a Network.


### Conversation protocol

In the protocol examples, `CA`, `CB`, etc. indicate Component IDs.
`Co1`, `Co2`, etc. indicate Coordinators with their Node IDs.

Here the Message content is expressed in plain English, for the exact definition see {ref}`message-layer`.

In the exchange of messages, only the messages over the wire are shown, the connection identity of the ROUTER socket is not shown.


#### Communication with the Coordinator

(sign-in)=
##### Initial connection

After connecting to a Coordinator (`Co1`), a Component (`CA`) shall send a SIGNIN message indicating its ID.
The Coordinator shall respond with an ACKNOWLEDGE, giving the Node ID and other relevant information, or with an ERROR, if the ID is already taken.
After that successful handshake, the Coordinator shall store the connection identity and corresponding Component ID in its local address book.
It shall also publish to the other Coordinators in the network that this Component signed in, see {ref}`Coordinator coordination<coordinator-coordination>`.
Similarly, the Component shall store the Node ID and use it from this moment to generate its full ID.

If a Component does send a message to someone without having signed in, the Coordinator shall refuse message handling and return an error.

:::{mermaid}
sequenceDiagram
    Note over CA,Co1: ID "CA" is still free
    CA ->> Co1: COORDINATOR|CA|SIGNIN
    Note right of Co1: Connection identity "IA"
    Note right of Co1: Stores "CA" with identity "IA"
    Co1 ->> CA: Co1.CA|Co1.COORDINATOR|ACKNOWLEDGE: Node ID is "Co1"
    Note left of CA: Stores "Co1" as Node ID
    Note over CA,Co1: ID "CA" is already used
    CA ->> Co1: COORDINATOR|CA|SIGNIN
    Co1 ->> CA: CA|Co1.COORDINATOR|ERROR: ID "CA" is already used.
    Note left of CA: May retry with another ID
    Note over CA,Co1: "CA" has not send SIGNIN
    Note left of CA: Wants to send a message to CB
    CA ->> Co1: Co1.CB|CA|Content
    Note right of Co1: Does not know CA
    Co1 ->> CA: CA|Co1.COORDINATOR|ERROR:I do not know you
    Note left of CA: Should send a SIGNIN message
:::


##### Heartbeat

We use heartbeat to know, whether a communication partner is still online.

Every message received counts as a heartbeat.

A Component should and a Coordinator shall send a STATUS request and wait some time before considering a connection dead.
A Coordinator shall follow the {ref}`sign out routine<sign-out>` for a signed in Component considered dead.

:::{note}
TBD: Respond to every non empty message with an empty one?
:::


(sign-out)=
##### Signing out

A Component should tell a Coordinator, when it stops working, with a SIGNOUT message.
The Coordinator shall ACKNOWLEDGE the sign out and remove the ID from its address book.
It shall also publish to the other Coordinators in the network that this Component signed out, see {ref}`Coordinator coordination<coordinator-coordination>`.

:::{mermaid}
sequenceDiagram
    CA ->> Co1: COORDINATOR|Co1.CA|SIGNOUT
    Co1 ->> CA: Co1.CA|Co1.COORDINATOR|ACKNOWLEDGE
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

Prerequisite of Communication between two Components are:
- Both Components are connected to a Coordinator and {ref}`signed in<sign-in>`.
- Both Components are either connected to the same Coordinator (example one), or their Coordinators are connected to each other (example two).


The following flow chart shows the decision scheme and message modification in a Coordinator.
`Node0`, `NodeR` are placeholders for sender and recipient Node ID.
`Recipient` is a placeholder for the recipient Component ID.
`IA` is the connection identity of `Co1.CA` or of `Node0.COORDINATOR`.
`IB` is the connection identities of `Co1.Recipient`.
Bold arrows indicate message flow, thin lines indicate decision flow.
Thin, dotted lines indicate decision flow in case of errors

:::{mermaid}
flowchart TB
    C([Node0.CA DEALER]) == "NodeR.Recipient|Node0.CA|Content" ==> R0
    R0[receive] == "IA|NodeR.Recipient|Node0.CA|Content" ==> CN0{Node0 == Co1}
    CN0-->|no| RemIdent
    CN0-->|yes| Clocal{CA in <br>local address book?}
    Clocal -->|yes| CidKnown{IA is CA's identity<br> in address book?}
    CidKnown -->|yes| RemIdent
    Clocal -.->|no| E1[ERROR: Sender did not sign in] ==>|"IA|Node0.CA|Co1.COORDINATOR|ERROR: Sender dit not sign in"| S
    S[send] ==> WA([Node0.CA DEALER])
    CidKnown -.->|no| E2[ERROR: ID and identity do not match]==>|"IA|Node0.CA|Co1.COORDINATOR|ERROR: ID and identity do not match"| S
    RemIdent[remove sender identity] == "NodeR.Recipient|Node0.CA|Content" ==> CNR
    CNR -- "is None" --> Local
    CNR{NodeR} -- "== Co1"--> Local
    Local{Recipient<br>==<br>COORDINATOR} -- "yes" --> Self([Message for Co1<br> itself])
    Local -- "no" --> Local2a{Recipient in Address book}
    Local2a -->|yes, with Identity IB| Local2
    Local2[add Recipient identity IB] == "IB|NodeR.Recipient|Node0.CA|Content" ==> R1[send]
    R1 == "NodeR.Recipient|Node0.CA|Content" ==> W1([Wire to Co1.Recipient DEALER])
    Local2a -.->|no| E3[ERROR Recipient unknown<br>send Error to original sender] ==>|"Node0.CA|Co1.COORDINATOR|ERROR Co1.Recipient is unknown"|CNR
    CNR -- "== connected Coordinator Co2" --> Keep
    Keep[send to Coordinator Co2] == "NodeR.Recipient|Node0.CA|Content" ==> R2[send]
    R2 == "NodeR.Recipient|Node0.CA|Content" ==> W2([Wire to Co2 ROUTER])
    CNR -- "reachable via Coordinator CoX" --> Augment
    Augment[send via CoX] == "NodeR.Recipient|Node0.CA|Content" ==> R3[send]
    R3 == "NodeR.Recipient|Node0.CA|Content"==> W3([Wire to CoX ROUTER])
    subgraph Co1 ROUTER socket
        R0
    end
    subgraph Co1 ROUTER socket
        R1
        S
    end
    subgraph Co1 DEALER socket to Co2
        R2
    end
    subgraph Co1 DEALER socket to CoX
        R3
    end
:::


(coordinator-coordination)=
#### Coordinator coordination

Each Coordinator shall keep an up to date {ref}`global address book<address-book>` with the IDs of all Components in the Network.
For this, Coordinators shall tell each other regarding signing in and signing out Components and Coordinators.
Coordinators shall send on request the IDs of their local address book, or of their global address book, depending on the request type.


Necessary information:
- Event type (connect or disconnect)
- Full ID (Node ID and Component ID) of the Component

:::{note}
TODO decide whether via Control or Data protocol.
TODO add the log in of a Coordinator
:::



(message-layer)=
## Message layer

:::{note}
TODO
:::
