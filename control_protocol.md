# Control protocol

The control protocol transmits messages via its {ref}`control_protocol.md#transport-layer` from one Component to another.
The {ref}`control_protocol.md#message-layer` is the common language to understand commands, thus creating a remote procedure call.

## Transport layer

The transport layer ensures that a message arrives at its destination.

### Protocol basics

#### Socket Configuration

Each {ref}`Coordinator <components.md#coordinator>` SHALL offer one {ref}`ROUTER <appendix.md#router-sockets>` socket, bound to an address.
The address consists of a host (this can be the host name, an IP address of the device, or "\*" for all IP addresses of the device) and a port number, for example `*:12345` for all IP addresses at the port `12345`.

{ref}`Components <components.md#components>` SHALL have one DEALER socket connecting to one Coordinator's ROUTER socket.

Coordinators SHALL have one DEALER socket per other Coordinator in the Network.
This DEALER socket SHALL connect to the other Coordinator's ROUTER socket.

:::{note}
While the number of DEALER sockets thus required scales badly with the number of Coordinators in a LECO Network, the scope of the protocol means that at most a few Coordinators will be involved.
:::

Communicating with a Coordinator, messages MUST be sent to a Coordinator's ROUTER socket.
Only for acknowledging a {ref}`control_protocol.md#coordinator-sign-in`, a Coordinator MAY send a response via its DEALER socket (i.e. the reply may arrive from the DEALER socket the requesting Coordinator connected to, rather than via the ROUTER socket).

#### Naming scheme

Each Component MUST have an individual name, given by the user, the _Component name_.
Component names MUST be unique in a {ref}`Node <network-structure.md#node>`, i.e. among the Components (except other Coordinators) connected to a single Coordinator.
A Coordinator itself MUST have the Component name `COORDINATOR`.

Similarly, every Node MUST have a name, the _Namespace_.
Every Namespace MUST be unique in the Network.

A Component name or a Namespace MUST be a series of printable ASCII characters (byte values 0x20 to 0x7E), without the character "." (byte value 0x2E).

As each Component belongs to exactly one Node, it is fully identified by the combination of Namespace and Component name, which is globally unique.
This _Full name_ is the composition of Namespace, ".", and Component name.
For example `N1.CA` is the Full name of the Component `CA` in the Node `N1`.

The receiver of a message MAY be specified by Component name alone if the receiver belongs to the same Node as the sender.
In all other cases, the receiver of a message MUST be specified by the Full name.

The sender of a message MUST be specified by Full name, except for the `sign_in` message, when the Component name alone is sufficient.

#### Message composition

A message consists of 4 or more ZMQ frames.

1. **Protocol version** (abbreviated with "V" in examples): a single byte, for example `0` (`0x00`).
2. **Receiver**: the receiver Full name or Component name as appropriate, encoded as printable ASCII bytes (no length prefix, no null terminator; the ZMQ frame boundary delimits the string), as defined in the {ref}`naming scheme <control_protocol.md#naming-scheme>`.
3. **Sender**: the sender Full name, encoded as printable ASCII bytes (same framing as receiver).
4. **Content header** (abbreviated with "H" in examples): a single ZMQ frame of exactly 20 bytes, laid out as follows:

   | Offset | Length | Field             | Encoding                                       |
   |--------|--------|-------------------|------------------------------------------------|
   | 0      | 16     | `conversation_id` | UUIDv7, 16 bytes in network (big-endian) order |
   | 16     | 3      | `message_id`      | Unsigned 24-bit integer, big-endian            |
   | 19     | 1      | `message_type`    | Unsigned 8-bit integer                         |

5. **Message content**: 0 or more additional ZMQ frames constituting the payload.

##### Envelope vs. JSON-RPC body

The first three frames (protocol version, receiver, sender) and the content header form the **LECO envelope**. They carry routing and metadata information processed by Coordinators and the transport layer.

The JSON-RPC body in the first content frame carries the **application-level** request, response, or error. JSON-RPC parameters carry method arguments and results; they MUST NOT duplicate information that is already present in the envelope (e.g., sender or receiver names).

For example, in the `sign_in` method, the Component name is carried in the sender frame of the envelope (Component name only, since the Namespace is not yet known). The JSON-RPC `sign_in` request has no parameters. Upon success, the Coordinator replies with its own Full name as the sender (e.g. `N1.COORDINATOR`); the Component deduces its Namespace by extracting the Namespace portion from that sender Full name. The JSON-RPC `result` is `null`.

##### Wire format test vectors

The following hex dumps show complete encoded messages with frame boundaries marked by `|`. Each frame is a contiguous byte sequence; the `|` separator is for readability only and is not transmitted.

**Test vector 1: `sign_in` request from Component `CA`**

Assumptions: protocol version = `0x00`, conversation_id = `0190a2b3c4d5e6f7a8b9c0d1e2f3a4b5` (example UUIDv7), message_id = `0x000001`, message_type = `0x01` (JSON).

```
00 | 434F4F5244494E41544F52 | 4341 | 0190a2b3c4d5e6f7a8b9c0d1e2f3a4b5 000001 01 | 7B226A736F6E727063223A22322E30222C226D6574686F64223A227369676E5F696E222C226964223A317D
```

Frame breakdown:
- Frame 1 (`0x00`): protocol version 0
- Frame 2 (`COORDINATOR`): receiver
- Frame 3 (`CA`): sender (Component name only, as per sign_in convention)
- Frame 4 (20 bytes): content header
- Frame 5: `{"jsonrpc":"2.0","method":"sign_in","id":1}`

**Test vector 2: `sign_in` result from Coordinator `N1.COORDINATOR` to `N1.CA`**

The Component deduces its Namespace (`N1`) from the sender frame of the envelope (`N1.COORDINATOR`).

```
00 | 4E312E4341 | 4E312E434F4F5244494E41544F52 | 0190a2b3c4d5e6f7a8b9c0d1e2f3a4b5 000001 01 | 7B226A736F6E727063223A22322E30222C22726573756C74223A6E756C6C2C226964223A317D
```

Frame 5 decoded: `{"jsonrpc":"2.0","result":null,"id":1}`

#### Directory

Each Coordinator SHALL have a list of the Components connected to it.
This is its _local Directory_.

They SHALL also keep a list of the addresses of all Coordinators, they are connected to.

Additionally, they SHALL maintain a _global Directory_, which is a Coordinator's copy of the union of the local Directories of all Coordinators in a Network.

### Component lifecycle state machine

A Component progresses through the following states when interacting with a Coordinator:

| State          | Description                                                 |
|----------------|-------------------------------------------------------------|
| `DISCONNECTED` | Not connected to any Coordinator.                           |
| `CONNECTED`    | ZMQ connection established, but not yet signed in.          |
| `SIGNED_IN`    | Successfully signed in; normal messaging is allowed.        |
| `SIGNED_OUT`   | Signed out gracefully; only `sign_in` messages MAY be sent. |

State transitions:

| From           | To             | Trigger                             | Action                                             |
|----------------|----------------|-------------------------------------|----------------------------------------------------|
| `DISCONNECTED` | `CONNECTED`    | ZMQ connection established          | —                                                  |
| `CONNECTED`    | `SIGNED_IN`    | `sign_in` result received           | Store Namespace; begin normal messaging            |
| `CONNECTED`    | `CONNECTED`    | `sign_in` error (name taken)        | MAY retry with a different Component name          |
| `SIGNED_IN`    | `SIGNED_OUT`   | `sign_out` result received          | Stop all messaging except `sign_in`                |
| `SIGNED_IN`    | `DISCONNECTED` | Connection lost / heartbeat timeout | Coordinator removes Component from local Directory |
| `SIGNED_OUT`   | `CONNECTED`    | Ready to re-sign-in                 | MAY send a new `sign_in` message                   |

A Coordinator receiving a message from a Component in the `CONNECTED` state (not signed in) MUST respond with a routing error (`-32090`, see {ref}`control_protocol.md#routing-errors`).

### Coordinator-to-Coordinator state machine

A Coordinator connection to another Coordinator follows a similar lifecycle:

| State          | Description                                                      |
|----------------|------------------------------------------------------------------|
| `DISCONNECTED` | No ZMQ connection to the remote Coordinator.                     |
| `CONNECTED`    | DEALER socket connected, but not yet signed in.                  |
| `SIGNED_IN`    | Mutual sign-in complete; Directory and node addresses exchanged. |
| `SIGNED_OUT`   | Signed out; DEALER socket MAY be disconnected.                   |

State transitions:

| From           | To             | Trigger                                       | Action                                                                                |
|----------------|----------------|-----------------------------------------------|---------------------------------------------------------------------------------------|
| `DISCONNECTED` | `CONNECTED`    | DEALER socket connects to remote ROUTER       | —                                                                                     |
| `CONNECTED`    | `SIGNED_IN`    | `coordinator_sign_in` result received         | Exchange Directories and node addresses; sign in to any newly discovered Coordinators |
| `CONNECTED`    | `CONNECTED`    | `coordinator_sign_in` error (Namespace taken) | MAY retry or abort                                                                    |
| `SIGNED_IN`    | `SIGNED_OUT`   | `coordinator_sign_out` sent/received          | Remove remote Namespace from global Directory; disconnect DEALER                      |
| `SIGNED_IN`    | `DISCONNECTED` | Connection lost / heartbeat timeout           | Remove remote Namespace entries from global Directory                                 |

### Conversation protocol

In the protocol examples, `CA`, `CB`, etc. indicate Component names.
`N1`, `N2`, etc. indicate Node Namespaces and `Co1`, `Co2` their corresponding Coordinators.

Here the Message content is expressed in plain English and placed in the Content frame, for the exact definition see {ref}`control_protocol.md#message-layer`.

:::{note}
The conversation protocol examples below use a human-readable notation for message content. For exact byte-level encodings, see the {ref}`wire format test vectors <control_protocol.md#wire-format-test-vectors>`.
:::

In the exchange of messages, only the messages over the wire are shown, the connection identity used by the ROUTER socket is not shown.

#### Communication with the Coordinator

##### Signing-in

After connecting to a Coordinator (`Co1`), a Component (`CA`) SHALL send a `sign_in` message (see {ref}`methods.md#coordinator`) indicating its Component name in the sender frame of the envelope.

**Success:** The Coordinator SHALL accept the sign-in with a `result` response (according to [JSON-RPC](https://www.jsonrpc.org/specification)), using its own Full name as the sender in the envelope (e.g. `N1.COORDINATOR`). The Component deduces its Namespace from the Namespace portion of that sender Full name. After a successful handshake:

- The Coordinator SHALL store the Component name in its {ref}`control_protocol.md#directory` and SHALL ensure message delivery to that Component (e.g. by storing the (zmq) connection identity with the local directory).
- The Coordinator SHALL notify the other Coordinators in the network that this Component signed in, see {ref}`control_protocol.md#coordinator-coordination`.
- The Component SHALL store the Namespace and use it from this moment on, to generate its Full name.

**Error:** If the Component name is already taken, the Coordinator SHALL reply with an ERROR. The Coordinator MAY indicate a suitable, still available variation on the indicated Component name. The Component MAY retry signing in with a different chosen name.

**Unsigned Components:** If a Component sends a message without having signed in, the Coordinator SHALL refuse message handling and return an error.

:::{mermaid}
sequenceDiagram
    Note over CA,N1: Name "CA" is still free
    participant N1 as N1.COORDINATOR
    CA ->> N1: V|COORDINATOR|CA|H|sign_in
    Note right of N1: Connection identity "IA"
    Note right of N1: Stores "CA" with identity "IA"
    N1 ->> CA: V|N1.CA|N1.COORDINATOR|H|result
    Note left of CA: Stores "N1" as Namespace
    Note over CA,N1: Name "CA" is already used
    CA ->> N1: V|COORDINATOR|CA|H|sign_in
    N1 ->> CA: V|CA|N1.COORDINATOR|H|ERROR: The name is already taken.
    Note left of CA: May retry with another Name
    Note over CA,N1: "CA" has not send sign_in
    Note left of CA: Wants to send a message to CB
    CA ->> N1: V|N1.CB|CA|H|Content
    Note right of N1: Does not know CA
    N1 ->> CA: V|CA|N1.COORDINATOR|H|ERROR: Component not signed in yet!
    Note left of CA: Must send a sign_in message<br> before further messaging.
:::

##### Heartbeat

Heartbeats are used to know whether a communication peer is still online.

Every message received counts as a heartbeat.

A Component SHOULD and a Coordinator SHALL send a `pong` request message (see {ref}`methods.md#actor`) and wait some time before considering a connection dead.
A Coordinator SHALL follow the {ref}`control_protocol.md#signing-out` for a signed in Component considered dead.

:::{note}
TBD: Heartbeat details are still to be determined.
:::

##### Signing out

A Component SHOULD send a `sign_out` message (see {ref}`methods.md#coordinator`) to its Coordinator when it stops participating in the Network.
The Coordinator SHALL acknowledge the sign-out with a `result` message and remove the Component name from its local {ref}`control_protocol.md#directory`.
It SHALL also notify the other Coordinators in the network that this Component signed out, see {ref}`control_protocol.md#coordinator-coordination`.

:::{mermaid}
sequenceDiagram
    CA ->> N1: V|COORDINATOR|N1.CA|H|sign_out
    participant N1 as N1.COORDINATOR
    N1 ->> CA: V|N1.CA|N1.COORDINATOR|H|result
    Note right of N1: Removes "CA" with identity "IA"<br> from local Directory
    Note right of N1: Notifies other Coordinators about sign-out of "CA"
    Note left of CA: Shall not send any message anymore except sign_in
:::

#### Communication with other Components

The following two examples show how a message is transferred between two components `CA`, `CB` via one or two Coordinators.

Coordinators SHALL route the message to the corresponding Coordinator or connected Component.

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

- Both Components are connected to a Coordinator and {ref}`signed in<control_protocol.md#signing-in>`.
- Both Components are either connected to the same Coordinator (example one), or their Coordinators are connected to each other (example two).

The following flow chart shows the decision scheme and message modification in the Coordinator `Co1` of Node `N1`.
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
    CnS-->|yes| Clocal{CA in <br>local Directory?}
    Clocal -->|yes| CidKnown{iA is CA's identity?}
    CidKnown -->|yes| RemIdent
    Clocal -.->|no| E1[ERROR: Component not signed in yet!] ==>|"iA|V|nS.CA|N1.COORDINATOR|H|ERROR: Component not signed in yet!"| S
    S[send] ==> WA([N1.CA DEALER])
    CidKnown -.->|no| E2[ERROR: Component not signed in yet!]==>|"iA|V|nS.CA|N1.COORDINATOR|H|ERROR: Component not signed in yet!"| S
    RemIdent[remove sender identity] == "V|nR.recipient|nS.CA|H|Content" ==> CnR
    CnR -- "is None" --> Local
    CnR{nR?} -- "== N1"--> Local
    Local{recipient<br>==<br>COORDINATOR?} -- "yes" --> Self[Message for Co1<br> itself]
    Self == "V|nR.recipient|nS.CA|H|Content" ==> SC([Co1 Message handling])
    Local -- "no" --> Local2a{recipient in local Directory?}
    Local2a -->|yes, with Identity iB| Local2
    Local2[add recipient identity iB] == "iB|V|nR.recipient|nS.CA|H|Content" ==> R1[send]
    R1 == "V|nR.recipient|nS.CA|H|Content" ==> W1([Wire to N1.recipient DEALER])
    Local2a -.->|no| E3[ERROR: Receiver is not in addresses list<br>send Error to original sender] ==>|"V|nS.CA|N1.COORDINATOR|H|<br>ERROR: N1.recipient is unknown"|CnR
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
    subgraph "Co1 DEALER socket <br>to N2.COORDINATOR"
        R2
    end
:::

#### Coordinator coordination

Coordinators are the backbone of the Network and need to coordinate themselves.

##### Coordinator sign-in

A Coordinator joins a Network by signing in to any Coordinator of that Network.
The sign-in/sign-out procedure between two Coordinators is more thorough than that of Components.
During the sign-in procedure, Coordinators exchange their local Directories and addresses of all known Coordinators.
They SHALL sign in to all Coordinators, they are not yet signed in.
The sign-in might happen because the Coordinator learns a new Coordinator address via Directory updates or at startup.
The sign-out might happen because the Coordinator shuts down.

Similarly to Component sign-in, the Coordinator SHALL refuse a sign-in request with an ERROR, if it is already connected to a Coordinator with the same Namespace as the requesting Coordinator's Namespace.

These are the sign-in/sign-out sequences between Coordinators, where `address` is for example the host name and port number of the Coordinator's ROUTER socket.

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
    d1->>r2: V|COORDINATOR|N1.COORDINATOR|H|<br>coordinator_sign_in
    Note right of r2: stores N1 identity
    r2->>d1: V|N1.COORDINATOR|N2.COORDINATOR|H|result
    Note left of d1: DEALER name <br>set to "N2"
    d1->>r2: V|N1.COORDINATOR|N2.COORDINATOR|H|<br>add_nodes(Coordinator addresses)<br>record_components
    Note right of r2: Updates global <br>Directory and signs <br>in to all unknown<br>Coordinators,<br>also N1
    Note over d1,r2: Mirror of above sign-in procedure
    activate d2
    Note left of d2: created with<br>name "N1"
    d2-->>r1: connect to address1
    d2->>r1: V|COORDINATOR|N2.COORDINATOR|H|<br>coordinator_sign_in
    Note right of r1: stores N2 identity
    r1->>d2: V|N2.COORDINATOR|N1.COORDINATOR|H|result
    Note left of d2: Name is already "N1"
    d2->>r1: V|N2.COORDINATOR|N1.COORDINATOR|H|<br>add_nodes(Coordinator addresses)<br>record_components
    Note right of r1: Updates global <br>Directory and signs <br>in to all unknown<br>Coordinators
    Note over r1,d2: Sign out between two Coordinators
    Note right of r1: shall sign out from N2
    d1->>r2: coordinator_sign_out
    Note right of r2: removes N1 identity
    d2->>-r1: coordinator_sign_out
    Note right of r1: removes N2 identity
    deactivate d1
:::

:::{note}
Note that the DEALER socket responds with the local Directory and Coordinator addresses to the received Acknowledgment.
:::

##### Coordinator updates

Each Coordinator SHALL keep an up-to-date global {ref}`control_protocol.md#directory` with the Full names of all Components in the Network.
For this, whenever a Component signs in to or out from its Coordinator, the Coordinator SHALL notify all the other Coordinators regarding this event.
The other Coordinators SHALL update their global Directory according to this message (add or remove an entry).

:::{note}
TBD: These updates have to be determined.
:::

On request, Coordinators SHALL send the Names of their local or global Directory, depending on the request type.

For the format of the Messages, see {ref}`control_protocol.md#message-layer`.

## Message layer

The message layer contains the actual information exchanged between Components.
As LECO is about controlling experiments, the message layer has to transmit commands, that is calling procedures remotely.

We use the [JSON-RPC](https://www.jsonrpc.org/specification) standard to encode these _remote procedure calls_ (RPC) and the responses.
We further use the [OpenRPC](https://open-rpc.org/) standard to describe the possibly callable methods of a Component.

Therefore, a Component MUST execute remote procedures according to JSON-RPC and return an appropriate response.
A Component MUST also offer a list of all possibly callable methods in accordance with OpenRPC.

For such a RPC message, the first content frame MUST consist in a JSON-RPC compatible content, for example a single request object or a batch of request objects.

For the definitions of methods see:

:::{toctree}
:maxdepth: 2

methods
:::

### Errors

Every error has a code and a message.
Additionally they may have a ``data`` field with more information.

According to JSONRPC, applications can define error codes between -32000 and -32099.
LECO defines the following errors.

#### Routing errors

Errors related to routing (mainly emitted by Coordinators).
Their error codes are in the range of -32090 to -32099.

| code   | message                            | data                  | description                                                                          |
|--------|------------------------------------|-----------------------|--------------------------------------------------------------------------------------|
| -32090 | Component not signed in yet!       | Name of the Component | If a Component did not sign in.                                                      |
| -32091 | The name is already taken.         | Name of the Component | A Component tries to sign in, but another Component is signed in with the same name  |
| -32092 | Node is unknown.                   | Name of the Node      | The Node to which the message should be sent, is not known to this Coordinator.      |
| -32093 | Receiver is not in addresses list. | Name of the receiver  | The Component to which the message should be sent, is not known to this Coordinator. |

#### Locking errors

Errors related to locked Resources

| code   | message          | data | description                                  |
|--------|------------------|------|----------------------------------------------|
| -32050 | Resource locked! | -    | The resource is locked by another component. |
