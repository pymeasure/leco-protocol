# Messages

A LECO Message is one set of data transmitted from one Component to another.
It is either a control, data, or logging message.
A Message consists of a Header with some metadata (e.g. routing information needed for message delivery), and an optional Payload.

:::{admonition} Note
A heartbeat message might not need a payload.
:::
