JDI
===

JSON Data Interchange

JDI is intended to be a re-usable set of request/response structures for
communicating loosely-structured data between hosts over a network. In most
use cases, it is expected that JDI messages will be sent over HTTP.

JDI is meant to expose a client-side application to a server-side data
management solution. Client applications are not expected to be aware of the
underlying storage mechanisms. Requests for data retrieval should be done with
a fairly high-level query system using system-wide unique identifiers and/or
keys. The server-side application then maps the unique identifiers to
extraction queries, formats the results, and responds to the query.

A Sample Message
----------------

    {
        "status"  : 0,
        "message" : "Ok",
        "layout"  : "record",
        "payload" : {
            "fields" : [ "id", "name", "color" ],
            "values" : [ 42, "John Doe", "green" ]
        }
    }

This example demonstrates a basic `record` message intended to convey a single
record from a remote data store.

For message details, see [docs/format.md](docs/format.md).

