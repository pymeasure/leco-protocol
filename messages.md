# Messages
A LECO Message is one set of data transmitted from one Component to another. 
It consists of a Header with some metadata (e.g. routing information needed for message delivery), an optional Payload, and a checksum to verify Message integrity.

:::{admonition} Note
A heartbeat message might not need a payload.
:::

:::{admonition} TODO
Confirm if we need to include a checksum.
:::
