# Control protocol

The control protocol transmits messages via its {ref}`transport-layer` from one Component to another one.
The {ref]}`message-layer` is the common language to understand commands, thus creating a remote procedure call.


(transport-layer)=
## Transport layer

The transport layer ensures that a message arrives at its destination.


### Protocol basics

#### Socket Configuration

Each {ref}`Coordinator <components.md#coordinator>` shall offer one {ref}`ROUTER<appendix.md#router-sockets>` socket, bound to an address.
The address consists of a host (this can be the host name, an IP address of the device, or "\*" for all IP addresses of the device) and a port number, for example `*:12345` for all IP addresses and the port `12345`.

{ref}`Components <components.md#components>` shall have one DEALER socket connecting to one Coordinator's ROUTER socket.

Coordinators shall have one DEALER socket per other Coordinator in the Network.
This DEALER socket shall connect to the other Coordinator's ROUTER socket.

:::{note}
While the number of DEALER sockets thus required scales badly with the number of Connectors in a LECO Network, the scope of the protocol means that at most a few Coordinators will be involved.
:::

Messages must be sent to a Coordinator's ROUTER socket.


#### Naming scheme

Each Component must have an individual name, given by the user, the _Component name_.
A Component name must be a series of bytes, without the ASCII character "." (byte value 46).
Component names must be unique in a {ref}`Node <network-structure.md#node>`, i.e. among the Components (except other Coordinators) connected to a single Coordinator.
A Coordinator itself must have the Component name `COORDINATOR` (ASCII encoded).

Similarly, every Node must have a name, the _Namespace_.
Every Namespace must be unique in the Network.
As each Component belongs to exactly one Node, it is fully identified by the combination of Namespace and Component name, which is globally unique.
This _Full name_ is the composition of Namespace, ".", and Component name.
For example `N1.CA` is the Full name of the Component `CA` in the Node `N1`.

The receiver of a message may be specified by Component name alone if the receiver belongs to the same Node as the sender.
In all other cases, the receiver of a message must be specified by Full name.


#### Message composition

A message consists of 4 or more frames.
1. The protocol version (abbreviated with "V" in examples).
2. The receiver Full name or Component name, as appropriate.
3. The sender Full name.
4. A content header (abbreviated with "H" in examples).
5. Message content: The optional payload, which can be 0 or more frames.


#### Directory

Each Coordinator shall have a list of the Components (including other Connectors) connected to it.
This is its _Directory_.

The _Glossary_ is the combination of the Directories of all Coordinators in a Network.


### Conversation protocol

In the protocol examples, `CA`, `CB`, etc. indicate Component names.
`N1`, `N2`, etc. indicate Node Namespaces and `Co1`, `Co2` their corresponding Coordinators.

Here the Message content is expressed in plain English, for the exact definition see {ref}`message-layer`.

In the exchange of messages, only the messages over the wire are shown, the connection identity used by the ROUTER socket is not shown.


#### Communication with the Coordinator

(sign-in)=
##### Initial connection

After connecting to a Coordinator (`Co1`), a Component (`CA`) shall send a SIGNIN message indicating its Component name.
The Coordinator shall indicate success/acceptance with an ACKNOWLEDGE response, giving the Namespace and other relevant information, or reply with an ERROR, e.g. if the Component name is already taken.
In that case, the Coordinator may indicate a suitable still available variation on the indicated Component name.
The Component may retry SIGNIN with a different chosen name.

After a successful handshake, the Coordinator shall store the (zmq) connection identity and corresponding Component name in its {ref}`directory`.
It shall also notify the other Coordinators in the network that this Component signed in, see {ref}`Coordinator coordination<coordinator-coordination>`.
Similarly, the Component shall store the Namespace and use it from this moment to generate its Full name.

If a Component does send a message to someone without having signed in, the Coordinator shall refuse message handling and return an error.

:::{mermaid}
sequenceDiagram
    Note over CA,N1: Name "CA" is still free
    participant N1 as N1.COORDINATOR
    CA ->> N1: V|COORDINATOR|CA|H|SIGNIN
    Note right of N1: Connection identity "IA"
    Note right of N1: Stores "CA" with identity "IA"
    N1 ->> CA: V|N1.CA|N1.COORDINATOR|H|ACKNOWLEDGE: Namespace is "N1"
    Note left of CA: Stores "N1" as Namespace
    Note over CA,N1: Name "CA" is already used
    CA ->> N1: V|COORDINATOR|CA|H|SIGNIN
    N1 ->> CA: V|CA|N1.COORDINATOR|H|ERROR: Name "CA" is already used.
    Note left of CA: May retry with another Name
    Note over CA,N1: "CA" has not send SIGNIN
    Note left of CA: Wants to send a message to CB
    CA ->> N1: V|N1.CB|CA|H|Content
    Note right of N1: Does not know CA
    N1 ->> CA: V|CA|N1.COORDINATOR|H|ERROR:I do not know you
    Note left of CA: Must send a SIGNIN message before further messaging.
:::


##### Heartbeat

Heartbeats are used to know whether a communication peer is still online.

Every message received counts as a heartbeat.

A Component should and a Coordinator shall send a PING and wait some time before considering a connection dead.
A Coordinator shall follow the {ref}`sign out routine<signing-out>` for a signed in Component considered dead.

:::{note}
TBD: Respond to every non empty message with an empty one?
:::


##### Signing out

A Component should tell a Coordinator when it stops participating in the network with a SIGNOUT message.
The Coordinator shall ACKNOWLEDGE the sign-out and remove the Name from its Directory.
It shall also notify the other Coordinators in the network that this Component signed out, see {ref}`Coordinator coordination<coordinator-coordination>`.

:::{mermaid}
sequenceDiagram
    CA ->> N1: V|COORDINATOR|N1.CA|H|SIGNOUT
    participant N1 as N1.COORDINATOR
    N1 ->> CA: V|N1.CA|N1.COORDINATOR|H|ACKNOWLEDGE
    Note right of N1: Removes "CA" with identity "IA"<br> from Directory
    Note right of N1: Notifies other Coordinators about sign-out of "CA"
    Note left of CA: Shall not send any message anymore except SIGNIN
:::


#### Communication with other Components

The following two examples show how a message is transferred between two components `CA`, `CB` via one or two Coordinators.
Coordinators shall send messages from their DEALER socket to other Coordinator's ROUTER socket.

Coordinators shall route the message to the corresponding Coordinator or connected Component.


:::{mermaid}
sequenceDiagram
    alt Full name
        CA ->> N1: V|N1.CB|N1.CA|H| Give me property A.
    else only Component name
        CA ->> N1: V|CB|N1.CA|H| Give me property A.
    end
    participant N1 as N1.COORDINATOR
    N1 ->> CB: V|N1.CB|N1.CA|H| Give me property A.
    Note left of CB: Reads property A
    CB ->> N1: V|N1.CA|N1.CB|H| Property A has value 5.
    N1 ->> CA: V|N1.CA|N1.CB|H| Property A has value 5.
:::


:::{mermaid}
sequenceDiagram
    CA ->> N1: V|N2.CB|N1.CA|H| Give me property A.
    participant N1 as N1.COORDINATOR
    Note over N1,N2: N1 DEALER socket sends to N2 ROUTER
    participant N2 as N2.COORDINATOR
    N1 ->> N2: V|N2.CB|N1.CA|H| Give me property A.
    N2 ->> CB: V|N2.CB|N1.CA|H| Give me property A.
    Note left of CB: Reads property A
    CB ->> N2: V|N1.CA|N2.CB|H| Property A has value 5.
    Note over N1,N2: N2 DEALER socket sends to N1 ROUTER
    N2 ->> N1: V|N1.CA|N2.CB|H| Property A has value 5.
    N1 ->> CA: V|N1.CA|N2.CB|H| Property A has value 5.
:::

Prerequisites of Communication between two Components are:
- Both Components are connected to a Coordinator and {ref}`signed in<sign-in>`.
- Both Components are either connected to the same Coordinator (example one), or their Coordinators are connected to each other (example two).


The following flow chart shows the decision scheme and message modification in a Coordinator `Co1` of Node `N1`.
Its Full name is `N1.Coordinator`.
`nS`, `nR` are placeholders for sender and recipient Namespaces.
`recipient` is a placeholder for the recipient Component name.
`iA` is a placeholder for the connection identity of the incoming message and `iB` that of `N1.Recipient`.
Bold arrows indicate message flow, thin lines indicate decision flow.
Thin, dotted lines indicate decision flow in case of errors.
Placeholder values are written in lowercase, while actually known values begin with an uppercase letter.

:::{mermaid}
flowchart TB
    C1([N1.CA DEALER]) == "V|nR.recipient|nS.CA|H|Content" ==> R0
    C0([nS.COORDINATOR DEALER]) == "V|nR.recipient|nS.CA|H|Content" ==> R0
    R0[receive] == "iA|V|nR.recipient|nS.CA|H|Content" ==> CnS{nS == N1?}
    CnS-->|no| RemIdent
    CnS-->|yes| Clocal{CA in <br>Directory?}
    Clocal -->|yes| CidKnown{iA is CA's identity<br> in Directory?}
    CidKnown -->|yes| RemIdent
    Clocal -.->|no| E1[ERROR: Sender unknown] ==>|"iA|V|nS.CA|N1.COORDINATOR|H|ERROR: Sender unknown"| S
    S[send] ==> WA([N1.CA DEALER])
    CidKnown -.->|no| E2[ERROR: Name and identity do not match]==>|"iA|V|nS.CA|N1.COORDINATOR|H|ERROR: Name and identity do not match"| S
    RemIdent[remove sender identity] == "V|nR.recipient|nS.CA|H|Content" ==> CnR
    CnR -- "is None" --> Local
    CnR{nR?} -- "== N1"--> Local
    Local{recipient<br>==<br>COORDINATOR?} -- "yes" --> Self[Message for Co1<br> itself]
    Self == "V|nR.recipient|nS.CA|H|Content" ==> SC([Co1 Message handling])
    Local -- "no" --> Local2a{recipient in Directory?}
    Local2a -->|yes, with Identity iB| Local2
    Local2[add recipient identity iB] == "iB|V|nR.recipient|nS.CA|H|Content" ==> R1[send]
    R1 == "V|nR.recipient|nS.CA|H|Content" ==> W1([Wire to N1.recipient DEALER])
    Local2a -.->|no| E3[ERROR recipient unknown<br>send Error to original sender] ==>|"V|nS.CA|N1.COORDINATOR|H|ERROR N1.recipient is unknown"|CnR
    CnR -- "== N2" --> Keep
    Keep[send to N2.COORDINATOR] == "V|nR.recipient|nS.CA|H|Content" ==> R2[send]
    R2 == "V|nR.recipient|nS.CA|H|Content" ==> W2([Wire to N2.COORDINATOR ROUTER])
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

Each Coordinator shall keep an up-to-date {ref}`Glossary<directory>` with the Names of all Components in the Network.
For this, Coordinators shall notify each other about sign-ins and sign-outs of Components and Coordinators.
On request, Coordinators shall send the Names of their Directory, or of their Glossary, depending on the request type.

For the format of the Messages, see {ref}`message-layer`.


##### Coordinator sign-in

A Coordinator `Co1`joining a network follows a few steps:
1. It signs in to one Coordinator `Co2` of the Network.
2. It sends a CO_TELL_ALL message to `Co2`, to tell all other Coordinators about `Co1`s address.
3. `Co2` tells all the Coordinators signed in (`Co3`, `Co4`...) about `Co1` with a CO_NEW message.
4. These other Coordinators (`Co3`, `Co4`...) sign in to `Co1`.
5. All Coordinators are connected to all others.

Two Coordinators shall follow a more thorough sign-in/sign-out procedure than Components (address is for example host and port).
The sign-in might happen because of a CO_NEW message arrived or at startup.
The sign-out might happen because the Coordinator shuts down.

:::{mermaid}
sequenceDiagram
    participant r1 as ROUTER
    participant d1 as DEALER
    participant r2 as ROUTER
    participant d2 as DEALER
    Note over r1,d1: N1 Coordinator<br>at address1
    Note over r2,d2: N2 Coordinator<br>at address2
    Note over r1,d2: Sign in between two Coordinators
    Note right of r1: shall connect<br>to address2
    activate d1
    Note left of d1: created with<br> name "temp-NS"
    d1-->>r2: connect to address2
    d1->>r2: CO_SIGNIN<br>N1, address1,<br>ref:temp-NS
    par
        d1->>r2: GET Directory
    and
        Note right of r2: stores N1 identity
        activate d2
        Note left of d2: created with<br>name "N1"
        d2-->>r1: connect to address1
        d2->>r1: CO_SIGNIN<br>N2, address2<br>your ref:temp-NS
        Note right of r1: stores N2 identity
        Note left of d1: name changed<br>from "temp-NS"<br>to "N2"
        d2->>r1: GET Directory
    end
    d2->>r1: Here is my<br>Directory
    Note right of r1: Updates<br>Glossary
    d1->>r2: Here is my<br>Directory
    Note right of r2: Updates<br>Glossary
    Note over r1,d2: Sign out between two Coordinators
    Note right of r1: shall sign out from N2
    d1->>r2: CO_SIGNOUT
    Note right of r2: removes N1 identity
    d2->>-r1: CO_SIGNOUT
    Note right of r1: removes N2 identity
    deactivate d1
:::


##### Coordinator updates

Whenever a Component signs in to or out of its Coordinator, the Coordinator shall send a CO_UPDATE message regarding this event to all the other Coordinators.
The message shall contain the Full name of the Component and the event type (sign in or out)
The other Coordinators shall update their Glossary according to this message (add or remove an entry).


(message-layer)=
## Message layer



### Messages for Transport Layer

- SIGNIN
- SIGNOUT
- ACKNOWLEDGE
- ERROR
- PING
- CO_SIGNIN
- CO_SIGNOUT
- CO_TELL_ALL
- CO_NEW
- CO_UPDATE



:::{note}
TODO
:::
