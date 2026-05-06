# Messages

A LECO Message is one set of data transmitted from one Component to another.
It is either a control, data, or logging message.
A Message consists of a Header with some metadata (e.g. routing information needed for message delivery), and an optional Payload.

:::{admonition} Note
A heartbeat message might not need a payload.
:::

## Common elements

All LECO messages share the following conventions regardless of category:

- **Frames**: All messages are composed of one or more ZMQ frames (byte sequences), with frame boundaries serving as delimiters.
- **String encoding**: Name and topic fields are restricted to printable ASCII bytes (0x20–0x7E, excluding 0x2E `.`) and encoded without length prefixes or null terminators; ZMQ frame boundaries delimit the data. JSON content frames are UTF-8 encoded.
- **Integer encoding**: Multi-byte integers in binary headers use big-endian (network) byte order.
