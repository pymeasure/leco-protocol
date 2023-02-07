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
sequenceDiagram
    participant Code as Message handling
    participant ROUTER as ROUTER socket
    Note over Code, ROUTER: Coordinator
    CA ->> ROUTER: "Request A"
    ROUTER ->> Code: "IA|Request A"
    Code ->> ROUTER: "IA|Reply A"
    ROUTER ->> CA: "Reply A"
    CB ->> ROUTER: "Request B"
    ROUTER ->> Code: "IB|Request B"
    Code ->> ROUTER: "IB|Reply B"
    ROUTER ->> CB: "Reply B"
:::


### Protocol basics

#### Naming scheme

Each Component has an individual name, given by the user, the _Component Name_.
A Component Name must be a series of bytes, without the ASCII character "." (byte value 46).
Component Names must be unique in a {ref}`Node <network-structure.md#node>`, i.e. among the Components connected to a single Coordinator.
The Coordinator itself has the Component Name `COORDINATOR`.
:::{note}
COORDINATOR is a placeholder for the final version.
:::

Similarly, every node has a name, the _Namespace_.
Every Namespace has to be unique in the Network.
As each Component belongs to exactly one Node, it is fully identified by the combination of Namespace and Component Name, which is globally unique.
This _full name_ is the composition of Namespace, ".", and Component Name.
For example `N1.CA` is the full name of the Component `CA` in the Node `N1`.

The receiver of a message may be specified without the Namespace, if the receiver lives in the same Node.


#### Message composition

A message consists in two or more frames.
1. The protocol version.
2. The receiver full name.
3. The sender full name.
4. A content header.
5. Message content: The optional payload, which can be 0 or more frames.


#### Directory

Each Coordinator shall have a list of the Components connected to it.
This is its _local Directory_.

The _global Directory_ is the combination of the local directories of all Coordinators in a Network.


### Conversation protocol

In the protocol examples, `CA`, `CB`, etc. indicate Component Names.
`N1`, `N2`, etc. indicate Node Namespaces and `Co1`, `Co2` their corresponding Coordinators.

Here the Message content is expressed in plain English, for the exact definition see {ref}`message-layer`.

In the exchange of messages, only the messages over the wire are shown, the connection identity of the ROUTER socket is not shown.


#### Communication with the Coordinator

(sign-in)=
##### Initial connection

After connecting to a Coordinator (`Co1`), a Component (`CA`) shall send a SIGNIN message indicating its Component Name.
The Coordinator shall respond with an ACKNOWLEDGE, giving the Namespace and other relevant information, or with an ERROR, if the Component Name is already taken.
After that successful handshake, the Coordinator shall store the connection identity and corresponding Component Name in its local {ref}`directory`.
It shall also publish to the other Coordinators in the network that this Component signed in, see {ref}`Coordinator coordination<coordinator-coordination>`.
Similarly, the Component shall store the Namespace and use it from this moment to generate its full name.

If a Component does send a message to someone without having signed in, the Coordinator shall refuse message handling and return an error.

:::{mermaid}
sequenceDiagram
    Note over CA,N1: Name "CA" is still free
    participant N1 as N1.COORDINATOR
    CA ->> N1: COORDINATOR|CA|SIGNIN
    Note right of N1: Connection identity "IA"
    Note right of N1: Stores "CA" with identity "IA"
    N1 ->> CA: N1.CA|N1.COORDINATOR|ACKNOWLEDGE: Namespace is "N1"
    Note left of CA: Stores "N1" as Namespace
    Note over CA,N1: Name "CA" is already used
    CA ->> N1: COORDINATOR|CA|SIGNIN
    N1 ->> CA: CA|N1.COORDINATOR|ERROR: Name "CA" is already used.
    Note left of CA: May retry with another Name
    Note over CA,N1: "CA" has not send SIGNIN
    Note left of CA: Wants to send a message to CB
    CA ->> N1: N1.CB|CA|Content
    Note right of N1: Does not know CA
    N1 ->> CA: CA|N1.COORDINATOR|ERROR:I do not know you
    Note left of CA: Should send a SIGNIN message
:::


##### Heartbeat

We use heartbeat to know, whether a communication partner is still online.

Every message received counts as a heartbeat.

A Component should and a Coordinator shall send a PING and wait some time before considering a connection dead.
A Coordinator shall follow the {ref}`sign out routine<signing-out>` for a signed in Component considered dead.

:::{note}
TBD: Respond to every non empty message with an empty one?
:::


##### Signing out

A Component should tell a Coordinator, when it stops working, with a SIGNOUT message.
The Coordinator shall ACKNOWLEDGE the sign out and remove the Name from its directory.
It shall also publish to the other Coordinators in the network that this Component signed out, see {ref}`Coordinator coordination<coordinator-coordination>`.

:::{mermaid}
sequenceDiagram
    CA ->> N1: COORDINATOR|N1.CA|SIGNOUT
    participant N1 as N1.COORDINATOR
    N1 ->> CA: N1.CA|N1.COORDINATOR|ACKNOWLEDGE
    Note right of N1: Removes "CA" with identity "IA"<br> from directory
    Note left of CA: Shall not send any message anymore except SIGNIN
:::


#### Communication with other Components

The following two examples show, how a message is transferred between two components `CA`, `CB` via one or two Coordinators.
Coordinators shall send messages from their DEALER socket to other Coordinator's ROUTER socket.

Coordinators shall hand on the message to the corresponding Coordinator or connected Component.


:::{mermaid}
sequenceDiagram
    alt full name
        CA ->> N1: N1.CB|N1.CA| Give me property A.
    else only Component name
        CA ->> N1: CB|N1.CA| Give me property A.
    end
    participant N1 as N1.COORDINATOR
    N1 ->> CB: N1.CB|N1.CA| Give me property A.
    Note left of CB: Reads property A
    CB ->> N1: N1.CA|N1.CB| Property A has value 5.
    N1 ->> CA: N1.CA|N1.CB| Property A has value 5.
:::


:::{mermaid}
sequenceDiagram
    CA ->> N1: N2.CB|N1.CA| Give me property A.
    participant N1 as N1.COORDINATOR
    Note over N1,N2: N1 DEALER socket sends to N2 ROUTER
    participant N2 as N2.COORDINATOR
    N1 ->> N2: N2.CB|N1.CA| Give me property A.
    N2 ->> CB: N2.CB|N1.CA| Give me property A.
    Note left of CB: Reads property A
    CB ->> N2: N1.CA|N2.CB| Property A has value 5.
    Note over N1,N2: N2 DEALER socket sends to N1 ROUTER
    N2 ->> N1: N1.CA|N2.CB| Property A has value 5.
    N1 ->> CA: N1.CA|N2.CB| Property A has value 5.
:::

Prerequisite of Communication between two Components are:
- Both Components are connected to a Coordinator and {ref}`signed in<sign-in>`.
- Both Components are either connected to the same Coordinator (example one), or their Coordinators are connected to each other (example two).


The following flow chart shows the decision scheme and message modification in a Coordinator `Co1` of Node `N1`.
Its full name is `N1.Coordinator`.
`n0`, `nR` are placeholders for sender and recipient Namespaces.
`recipient` is a placeholder for the recipient Component name.
`IA` is the connection identity of the Component `N1.CA` (if it is directly connected to `Co1`) or of its Coordinator `n0.COORDINATOR`.
`IB` is the connection identity of `N1.Recipient`.
Bold arrows indicate message flow, thin lines indicate decision flow.
Thin, dotted lines indicate decision flow in case of errors.
Placeholder values are written in lowercase, while actually known values begin with an uppercase letter.

:::{mermaid}
flowchart TB
    C1([N1.CA DEALER]) == "nr.recipient|n0.CA|Content<br>(==nr.recipient|N1.CA|Content)" ==> R0
    C0([n0.COORDINATOR DEALER]) == "nr.recipient|n0.CA|Content" ==> R0
    R0[receive] == "IA|nr.recipient|n0.CA|Content" ==> Cn0{n0 == N1?}
    Cn0-->|no| RemIdent
    Cn0-->|yes| Clocal{CA in <br>local address book?}
    Clocal -->|yes| CidKnown{IA is CA's identity<br> in address book?}
    CidKnown -->|yes| RemIdent
    Clocal -.->|no| E1[ERROR: Sender did not sign in] ==>|"IA|n0.CA|N1.COORDINATOR|ERROR: Sender dit not sign in<br>(==IA|N1.CA|N1.COORDINATOR|ERROR...)"| S
    S[send] ==> WA([N1.CA DEALER])
    CidKnown -.->|no| E2[ERROR: Name and identity do not match]==>|"IA|n0.CA|N1.COORDINATOR|ERROR: Name and identity do not match<br>(==IA|N1.CA|N1.COORDINATOR|ERROR...)"| S
    RemIdent[remove sender identity] == "nr.recipient|n0.CA|Content" ==> Cnr
    Cnr -- "is None" --> Local
    Cnr{nr?} -- "== N1"--> Local
    Local{recipient<br>==<br>COORDINATOR?} -- "yes" --> Self[Message for Co1<br> itself]
    Self == "nr.recipient|n0.CA|Content<br>(==N1.COORDINATOR|n0.CA|Content)" ==> SC([Co1 Message handling])
    Local -- "no" --> Local2a{recipient in Address book?}
    Local2a -->|yes, with Identity IB| Local2
    Local2[add recipient identity IB] == "IB|nr.recipient|n0.CA|Content<br>(==IB|N1.recipient|n0.CA|Content)" ==> R1[send]
    R1 == "nr.recipient|n0.CA|Content<br>(==N1.recipient|n0.CA|Content)" ==> W1([Wire to N1.recipient DEALER])
    Local2a -.->|no| E3[ERROR recipient unknown<br>send Error to original sender] ==>|"n0.CA|N1.COORDINATOR|ERROR N1.recipient is unknown"|Cnr
    Cnr -- "== N2" --> Keep
    Keep[send to N2.COORDINATOR] == "nr.recipient|n0.CA|Content<br>(==N2.recipient|n0.CA|Content)" ==> R2[send]
    R2 == "nr.recipient|n0.CA|Content<br>(==N2.recipient|n0.CA|Content)" ==> W2([Wire to N2.COORDINATOR ROUTER])
    subgraph Co1 ROUTER socket
        R0
    end
    subgraph Co1 ROUTER socket
        R1
        S
    end
    subgraph Co1 DEALER socket <br>to N2.COORDINATOR
        R2
    end
:::


#### Coordinator coordination

Each Coordinator shall keep an up to date global {ref}`directory` with the names of all Components in the Network.
For this, Coordinators shall tell each other regarding signing in and signing out Components and Coordinators.
Coordinators shall send on request the Names of their local directory, or of their global directory, depending on the request type.

For the format of the Messages, see {ref}`message-layer`.


##### Coordinator sign in

Two Coordinators shall follow a more thorough sign in procedure, than Components:

1. Coordinator Co1 signs in to Co2
	1. Co1 creates a DEALER socket and connects to another Coordinator Co2 (ROUTER socket).
	2. Co1 sends a CO-SIGNIN message indicating its own address (host and port) to Co2.
	3. Co2 creates a DEALER socket and connects to Co1's DEALER socket.
	4. Co2 stores the the Namespace of Co1 and references it to the corresponding DEALER socket
	5. Co2 acknowledges to Co1 the Coordinator sign in.
2. Co2 signs in to Co1
	6. Co2 sends a CO-SIGNIN message to Co1.
	7. Co1 stores the Co2 Namespace and references it to the corresponding DEALER socket
	8. Co1 ackwnowledges to Co2 the Coordinator sign in.
3. Co1 and Co2 request the local address book of the other one.
4. If desired (see below), Co2 tells all its known Coordinators, that they shall sign in to Co1

In a CO-SIGNIN message, a Coordinator may indicate, that the other Coordinator shall tell all the other Coordinators, that it is present in the Network.
For example Co1 asks this from Co2 and Co2 tells Co3, Co4, etc., that they shall sign in to Co1.
That way all Coordinators are connected to all other ones.


##### Coordinator updates

Whenever a Component signs in to or out of its Coordinator, the Coordinator shall send a note regarding this event to all the other Coordinators.
The note shall contain the full name of the Component and the event type (sign in or out)
The other Coordinators shall update their global directory according to this note (add or remove an entry).



TODO Add full update (full local list)
TODO Problem: If a full list arrives after an update: On the other hand: One message after the other: Sequence should work out.



(message-layer)=
## Message layer



### Messages for Transport Layer

- SIGNIN
- SIGNOUT
- ACKNOWLEDGE
- ERROR
- PING



:::{note}
TODO
:::
