# Appendix

## ZMQ

Some useful hints regarding the working of the zmq package.

(router-sockets)=
### Particularities of ROUTER sockets

A small introduction to ROUTER sockets, for more details see [zmq guide chapter 3](https://zguide.zeromq.org/docs/chapter3/#Exploring-ROUTER-Sockets).

A router socket assigns a random _identity_ to each connecting peer.
If, for example, two Components `CA`, `CB` connect to the ROUTER sockets, the socket assigns the identities, which will be called `IA`, `IB` here (they can be any byte sequence).

Whenever a message is sent to the ROUTER socket from a peer, the socket prepends that identity in front of the message frames.
For example if `CA` sends the message `Request A`, the ROUTER socket will read `IA|Request A`.
That way, the answer to that message can be returned to the correct peer and not another one (a ROUTER socket can have many connected peers).
If the ROUTER's send command is called with `IA|Reply A`, the socket will send `Reply A` to the peer, whose connection is `IA`, in this case `CA`.

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

