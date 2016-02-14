JDI Format
==========

Message Schema
--------------

All JDI messages are composed of a root dictionary.  There are a number of
standard top-level keys, but applications may use their own top-level keys as
long as they don't interfere with the keys defined by JDI.

Most applications will use two variations of JDI message schemas: requests and
responses.  Requests are messages sent by clients (usually over HTTP) to
request complex actions on the server (e.g. storing/updating persistent
information).  Responses are messages sent by servers to provide structured
information for immediate use in a client application.

Both message types share a few top-level keys, but they differ enough in
purpose to require some distinction.

### JDI Requests

    {
        "context" : {
            "action" : "greet"
        },
        "layout"  : "string",
        "payload" : "Hello World"
    }

#### `context`

The `context` key indicates information the application needs to handle the
request.  In this case, an `action` is the verb used by the server to map it
to the appropriate request handler.

#### `layout`

The `layout` key formally declares the structure of the message to allow
consumers a chance to validate the message contents before passing it to
type-sensitive handler routines.  All formally-defined layouts are discussed
in a later section of this document.

#### `payload`

The `payload` key is where the contents of the message are placed.  The
payload's structure must match the declared layout.

### JDI Responses

Responses may be used to communicate the result of a mutation request or the
retrieval of information provided by the server.  A well-specified response
will contain five root keys:

    {
        "status"  : 0,
        "message" : "Ok",
        "query"   : {},
        "layout"  : "string",
        "payload" : "Hello World"
    }

#### `status`

`status` provides a simple way to evaluate the status of the response.  This
field's possible values are ultimately defined by the application, but the
following table shows the normal status codes and their meanings.

| Code | Message            | Meaning                                       |
| ----:| ------------------ | --------------------------------------------- |
|   0  | Ok                 | Request successful                            |
|   1  | No Data            | Request valid, but response contains no data  |
|   2  | No Change          | Request valid, but results in no changes      |
|  10  | Not Authorized     | Action not supported for unauthorized clients |
|  11  | Invalid Request    | Invalid request received from client          |
|  30  | Server Unavailable | Server resource is currently unavailable      |
|  31  | Retrieval Error    | Error retrieving requested information        |
|  99  | Unknown Error      | An unspecified error occurred                 |

Note: Most error statuses will be accompanied by a `string` payload that
contains additional information about the error.  The intent is that these
messages are helpful for client application developers if the status code is
between 10 and 29.  If the status code is 30 or more, there is probably a
problem on the remote server, and the contents of those messages may not be
helpful for client applications.

Status codes are not meant to be absolute.  However, by convention, client
applications are encouraged to use the space from 100 to 199 as internal
status messages if the local message handling stack is improved with more
customized or specific statuses.

#### `message`

`message` is a textual representation of the same information provided by the
`status` field.  This may be helpful for development purposes.

#### `query`

`query` echoes the query information that generated the request.  This gives
the client the ability to make parallel stateless requests and be able to
correctly map the responses to the appropriate client routines.  Additionally,
the query is echoed exactly as-is without regard for the needs of the server.
In other words, you may pass keys that the server doesn't understand or use,
and those keys will be in the response.

When JDI is transported over HTTP, the URL query parameters are used to build
the `query` item in the response.  The following (overly-simplified) HTTP
request example illustrates this.

    GET /?action=greet&key=value HTTP/1.1
    Host example.com

The `query` item in the response would be:

    { "action" : "greet", "key" : "value" }

#### `layout`

`layout` contains a hint at the contents of the JDI message payload.  This
field is used in both requests and responses.  The following table lists the
JDI-defined layouts.  Applications may define their own layouts, as needed.

| Key | Meaning | Example |
| --- | ------- | ------- |
| `null` or omitted | Layout must be inferred from payload | |
| `string` | Payload is a string | `"Hello World"` |
| `array` | Payload is an ordered list of values | `[ 1, 2, "three" ]` |
| `hash` | Payload is a key-value dictionary | `{ "k" : "v", "answer" : 42 }` |
| `document` | Payload is a document intended for the user.  Document layouts are objects that must contain two fields: `type` and `content` | `{ "type" : "text/plain", "content" : "Hello World" }` |
| `record` | Payload contains a single data record | (see below ) |
| `recordset` | Payload contains a set of data records | (see below ) |
| `schema` | Payload contains a record schema suitable for constructing data entry forms and/or checking submitted data before submitting to the server | (see below) |

#### `payload`

The `payload` contains the primary message contents of the response.  The
following section describes the non-trivial payloads in detail.

Data Retrieval Payloads
-----------------------

Data retrieval is expected to be the most common and frequent interaction of
an application implementing the JDI message conventions. Each of the payloads
are intended to allow compact, yet expressive retrieval of information
flexible enough to be used for everything from automation to GUIs.

### `record`

A single record from the host resource is declared as a `record` layout.

    {
        "status"  : 0,
        "message" : "Ok",
        "query"   : { "action" : "access" },
        "layout"  : "record",
        "payload" : {
            "info"   : {},
            "fields" : [
                "id",
                "name",
                "color"
            ],
            "values" : [
                42,
                "John Doe",
                "green"
            ]
        }
    }

The `record` payload contains three fields:

- `info` contains a varying amount of meta data that is both context sensitive
  and largely defined by the application. More about the `info` field is
  explained below.

- `fields` is a list of each field name in the record.

- `values` contains a list of the record's values in the same order as
  declared in the `fields` list. It is important to note that the type of each
  field is implied by the type used in the JSON-encoded value. Therefore, if a
  value is sent as `42`, the field is a numeric (integer) type. If a value is
  sent as `"42"`, the field is a `string` type.

### `recordset`

A set of records from the host resource is declared as a `recordset` layout:

    {
        "status"  : 0,
        "message" : "Ok",
        "query"   : { "action" : "access" },
        "layout"  : "recordset",
        "payload" : {
            "info"   : {},
            "fields" : [
                "id",
                "name",
                "color"
            ],
            "records" : [
                [ 1, "Adam",    "red"   ],
                [ 2, "Baker",   "green" ],
                [ 3, "Charlie", "blue"  ]
            ]
        }
    }

The `recordset` layout replaces the `values` field with a `records` field. The
`records` field is simply an array of values arrays.

### `schema`

JDI is also concerned with exchanging type information about the records that
can be accessed and modified by the client application. To allow clients to
implement as little application-specific logic as necessary, they may request a
type's schema. The response is declared as a `schema` layout:

    {
        "status"  : 0,
        "message" : "Ok",
        "query"   : { "action" : "type", "id" : "3" },
        "layout"  : "schema",
        "payload" : {
            "info" : {},
            "keys" : [
                "field",
                "type",
                "default",
                "limits",
                "options",
                "required",
                "access"
            ],
            "values" : [
                [ "id",    "integer", null,   null,   null, "nyy", "yyy" ],
                [ "name",  "string",  "",     [3,48], null, "yyx", "yyx" ],
                [ "color", "string",  "blue", [0,31], null, "oox", "yyx" ]
            ]
        }
    }

#### Type Keys

Types will always minimally specify the field name for every field in the
type. The other declarations are specified as indicated in the `keys` array.
All keys besides `field` may not be present in all types. The example above
shows a highly-specified type.

The keys may be specified in any order. The corresponding items in the given
`values` lists will be in the same order as that specified in the `keys` list.

If a field declares one of its values to be `null` for a particular key, that
item is considered _unspecified_.

If a field's values list is shorter than the keys list, the missing values are
assumed to be _unspecified_; the same as if the values list was padded with
`null` declarations.

Various declarations assume different default behaviors when unspecified. See
each key's description below for default behaviors.

The `values` given in a type can be treated similarly to the `recordset`'s
`records` item. Each array in the `values` array represents a single field in
the type.  The information contained in one of the field arrays is identified
by the corresponding key in the `keys` list. The following describes the
purpose of
each key.

- `field` represents the field's name. The value given will be the same as is
  used in a record's `fields` to identify each value. Field names are always
  unique within a type. Field names are usually safe to use as a program
  symbol (e.g. they won't contain whitespace or punctuation that isn't an
  underscore).

- `type` hints at the expected type of data that will be contained in this
  field. Types are specified as a string that declares one of the following:

  - `integer`
  - `double`
  - `string`
  - `array`
  - `boolean`

- `default` gives the field's default value when it is not specified in a
  retrieval response or a mutation request.

- `limits` provides hints at how the host resource will validate the value
  being submitted for mutation. For integers and doubles, the limits indicate
  minimum and maximum values. For strings, the limits indicate minimum and
  maximum string lengths. For arrays, the limits indicate the minimum and
  maximum number of items that can be submitted.

  If a field's limit is unspecified, it implies there are no limits on the
  input, or that the input will be clipped in a reasonably appropriate way.
  For example, a lack of a limit on a string does not imply a string may be
  a million characters long. A long string will simply be clipped before
  being stored.

- `options` provides a way for a field to specify all possible options that
  are valid values for the field. This will usually be presented to the user
  in a selection-style widget, or a list of exclusive selections (e.g. radio
  buttons)

  If the field is declared as an integer, the `options` item gives a list of
  bit names that are declared started at bit 0. The final value should then be
  a bitwise "OR" of the bits that are considered selected/asserted/active.
  Unspecified or `null` bits will always be set to 0 before being stored.

  If the field is declared as a `string`, the `options` item gives a list of
  allowed string values. If a string is submitted that is not one of the
  options, the default string is used instead. If no default string is
  specified, the submitted string _might_ be stored, but it is more likely
  that an internal default (`null` or empty string) will be stored instead.

  If the field is declared as an `array`, the `options` item gives a list of the
  possible values that can be combined into the submitted array. The elements
  within an array may be of any type in the request, but are, generally,
  assumed to be presented as a string. When specifying defaults for arrays,
  the value will contain an array of indexes into the `options` item for
  options that are considered selected/asserted/active. Without a default, an
  array field should consider all options de-asserted.

  If the field is declared as a `boolean`, the `options` item allows the host
  to hint at the words to use for boolean "true" and "false." Consider
  situations where it is easier for the user to select between "Yes" and "No"
  or "Ok" and "Cancel." Boolean-type options are given as a two-element array
  where the "false" label is first, and the "true" label is second.

- `required` declares if this field is required for mutation requests. This
  declaration is specified as a three-characters that codify the requirements
  as such:

  - `y`: required, and requests will fail without it
  - `n`: not required, and will not be used as input
  - `o`: optional, and may be used as input
  - `x`: explicitly marked as unused or do-not-care

  Each character in the string represents each of the three mutation requests.
  The order of the characters is: insert, update, delete.

  All fields default to _not_ required for all mutation requests (i.e. "nnn")
  if not specified. Any missing characters (e.g. if there are 0, 1, or 2
  characters) are assumed to indicate the field is not required for that
  mutation request.

- `access` provides hints to the client to indicate what kind of mutation
  access is available to the current user. This can be used to hide certain
  fields, but still submit them in requests. The string encodes access as
  follows:

  - `y`: modification allowed
  - `n`: no modification allowed
  - `x`: explicitly marked as unused or do-not-care

  The order of the characters is the same as that specified in the `required`
  declaration. Submission of unmodifiable fields is not treated as a failure
  in the request. They will simply be ignored by the host resource.

  The record's unique ID has special meaning for access rules. If unspecified,
  the default assumption is that the current user does not have permission to
  insert, update, or delete records for the type in question. If it is
  specified, the access declaration applies to entire records (not just the ID
  field). In the insert position, a "y" indicates the user is allowed to add
  new records. In the update position, a "y" indicates the user is allowed to
  modify fields in this type that are also declared with a "y". In the delete
  position, a "y" indicates the user is allowed to remove existing records.

  Keep in mind that access rules given in types are considered the access
  granted for the type in question, and does not always apply to all records
  for a given type. The type information is only intended to give enough
  information to create a rich UI without application-specific logic. The host
  can, and will, have the final say if the user can actually perform their
  request. This may include preventing them from adding, modifying, or
  removing a particular record of a type that would appear to be accessible to
  the current user.

  If unspecified, the field (or record) is not accessible to the user.

- `repos` can declare a list of regular expressions that can be used to prove
  that a value is of an acceptable format. To note:

  - integers and doubles are converted to strings before matching
  - arrays are evaluated per item

- `reneg` can declare a list of of regular expressions that can be used to
  prove that a value is not of an acceptable format.

- `label` allows the host to recommend a human-friendly label to display to
  the user when entering information into a form.

- `help` allows the host to recommend brief instructions to aid the user
  during data entry.

- `errors` allows the host to give the client-side application a list of
  human-friendly error messages to be used if the client decides to perform
  validation before making a mutation request to the host resource. `errors`
  are key-value declarations where each key corresponds to one of the type's
  keys (wherein a particular validation check might fail). An example of a
  field with an errors declaration follows:

    ```
    "keys" : [
        "field",
        "required",
        "limits",
        "repos",
        "reneg",
        "errors"
    ],
    "values" : [
        [
            "username",
            "yxx",
            [ 3, 48 ],
            [ "^[a-zA-Z]" ],
            [ "[^a-zA-Z0-9\"" _-]" ],
            {
                "required" : "You must specify a user name before continuing.",
                "limits" : [ "User names must be at least 3 characters long.",
                             "User names may not be longer than 48 characters." ],
                "repos" : [ "User names must start with a letter." ],
                "reneg" : [ "User names may not contain special punctuation." ]
            }
        ]
    ]
    ```

### `payload.info`

The `info` field that is present in all data responses is a common structure for
including additional information about the type of data contained in the
response. The idea is to keep details of reference and language on the server,
and allow the client to act primarily as a UI generator abstract of the
details of the content it is helping the user to maintain.

The following shows the `info` field with a typical `meta` structure for a
`recordset` response:

    {
        "status"  : 0,
        "message" : "Ok",
        "query"   : { "action" : "index" },
        "layout"  : "recordset",
        "payload" : {
            "info"   : {
                "meta" : {
                    "type_id"    : 2,
                    "type_name"  : "people",
                    "type_nouns" : [ "person", "people" ]
                }
            },
            "fields" : [
                "id",
                "cid",
                "pid",
                "name",
                "color"
            ],
            "records" : [
                [ 1, 2, "adam",    "Adam",    "red"   ],
                [ 2, 2, "baker",   "Baker",   "green" ],
                [ 3, 2, "charlie", "Charlie", "blue"  ]
            ]
        }
    }

#### `payload.info.meta`

The `meta` info field provides descriptive information about the record or
records in the response. The `meta` field is typically included in `record`,
`recordset`, and `schema` responses.

The following describes the fields within the `meta` field.

- `type_id`: An ID number that is unique across all types in the application
- `type_name`: A string that is unique across all types in the application
- `type_nouns`: See the "Common Nouns" section below.

#### `payload.info.parent` and `payload.info.range`

In the case of `recordset` responses, the host may include `parent` and
`range` items.

    "info" : {
        "meta" : {
            "type_id"    : 2,
            "type_name"  : "people",
            "type_nouns" : [ "person", "people" ]
        },
        "parent" : {
            "type_id"    : 1,
            "type_name"  : "mammals",
            "type_nouns" : [ "mammal", "mammals" ]
            "id"         : 31,
            "pid"        : "primates",
            "name"       : "Primates",
            "parent"     : null
        },
        "range" : {
            "offset"  : 0,
            "length"  : 3,
            "total"   : 3,
            "maximum" : 64
        }
    }

#### `payload.info.parent`

The `parent` item describes the parent record of the records. This is similar
to, but slightly different from the `meta` item since this does not describe
the _type_ of the parent only. It also describes the actual record contents
enough to be useful to the user.

- `type_id`: An ID number that is unique across all types in the application
- `type_name`: A string that is unique across all types in the application
- `type_nouns`: See: "Common Nouns" section below
- `id`: The value of the parent record's unique numeric ID field
- `pid`: The value of the parent record's unique string ID field
- `name`: The value of the human-readable identifier of the parent record
- `parent`: Optionally nested parent-of-parent item. Nesting is allowed all
  the way to the "root" of the hierarchy. The structure is identical to that
  of the records' immediate parent.

#### `payload.info.range`

The `range` item is intended to provide partial lists of all records in a set.
This should give the client the ability to "page" through records in a very
large list by iteratively requesting additional record sets.

- `offset`: The offset into the stored records matching the current query
- `length`: The number of records in the current record set
- `total`: The total number of stored records matching the current query
- `maximum`: The host resource's limit on how many records may be sent in a
  single recordset response.

Responses to Mutation Requests
------------------------------

Requests for mutating remote data (performed using POST using JSON message
bodies), receive fairly simple responses indicating success or failure of the
request. The payload will usually contain a copy of the record created by the
mutating request (for possible verification, and the client can fetch the
record's ID when inserting).

### Insertion

    {
        "status"  : 0,
        "message" : "Ok",
        "query"   : { "action" : "insert" },
        "layout"  : "record",
        "payload" : {
            "info"   : {},
            "fields" : [
                "id",
                "name",
                "color"
            ],
            "values" : [
                42,
                "John Doe",
                "green"
            ]
        }
    }

### Updating

    {
        "status"  : 2,
        "message" : "No Change",
        "query"   : { "action" : "update" },
        "layout"  : "record",
        "payload" : {
            "info"   : {},
            "fields" : [
                "id",
                "name",
                "color"
            ],
            "values" : [
                42,
                "John Doe",
                "green"
            ]
        }
    }

Of course, if the request did change a remote value, the status would be `0`
to indicate things were succesfully changed.

### Deletion

    {
        "status"  : 0,
        "message" : "Ok",
        "query"   : { "action" : "delete" },
        "layout"  : "record",
        "payload" : {
            "info"   : {},
            "fields" : [
                "id",
                "name",
                "color"
            ],
            "values" : [
                42,
                "John Doe",
                "green"
            ]
        }
    }

JDI over HTTP
-------------

JDI is typically used to communicate between client and server applications
over HTTP. When using JDI over HTTP, there are a few conventions that can be
established to simplify the development of both applications.

### JDI Requests are Intended for Mutation

Most of the time, a client application will retrieve information in JDI
responses by initiating a GET request to the server. HTTP GET requests provide
all the expressive capability necessary to provide the server resource with
enough information to fulfill the request. For example, a client that expects
a JDI response from a server will normally make data retrieval requests using
a structured query in the URI:

    http://example.com/?action=greet

Therefore, the assumed convention is that a structured JDI request is only
used when a large amount and diversity of data needs to be sent to the server.
These requests are, generally, used to mutate data on the server.

HTTP conventions (not standards) provide for mutation requests via the POST
and PUT request methods. Sending JDI over HTTP should be for the purposes of
mutating information. Therefore, the contents of the request should, by
convention, be sent using the POST method.

The body of the POST request should be the JDI request message. The client
should also identify the Content-Type of the request as application/json to
allow server resources to distinguish between varying request formats for the
same application.

An example HTTP POST request may look like the following:

    POST /?action=greet HTTP/1.1
    Host: example.com
    Content-Type: application/json; charset=utf-8
    Content-Length: 72

    {"context":{"action":"greet"},"layout":"string","payload":"Hello World"}

### JDI Responses are Intended for Retrieval

This is pretty much the entire purpose for defining the interchange format and
schemas. Highly organized data can be fetched over HTTP in a consistent and
type-safe way without asking either end to build complex parsers and handling
mechanisms. The server doesn't incur the overhead of extremely complex (and
repetitive) document generation, and the client can use the information from
the server with more faith that the data is correctly formatted, and ready for
display in the UI.

Sending Human Words
-------------------

This protocol deals with sending words based on grammar rule invocation
frequency. If a single, all-lowercase word is sent, it is assumed to follow
the mose frequently-invoked rules for pluralization, capitalization, articles,
etc.

### Common Nouns

For the set of all common nouns, there is a very large number of rules to
produce the plural form, and proper "title case." The client relies on the
host resource to deal with those complexities (hopefully stored with the data
and/or its definitions).

When sending a common noun, a list of one or more words is sent. The list
considers the unspecified values as trivial to derive from the specified
values. For common nouns, the first word in the list is the normal case,
singular form.

The second word in the list is optional if the noun can be made plural by
appending a single "s" character. If not, the second word must specify the
plural form of the first.

The third word in the list is optional if the noun can be converted to "title
case" by the simple translation: `s/\b([a-z])/\U\1/g` (converting the first
character in each word to upper case). If not, the third word must specify the
singular, title case form of the word.

The fourth word in the list is optional if the noun can be made plural by
appending a single "s" character to the third word in the list. If not, the
fourth word must specify the title case, plural form of the word.

