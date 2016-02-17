JDI Message Compacting
======================

JDI allows a more compact representation for common values of the root items.
The compaction is handled, primarily, by assuming a default value is present
if not specified.  The assumed defaults (and example messages) are documented
herein.

Default Values
--------------

### `status`

When not given, the `status` field assumes a default of `0` (no errors or
unusual events encountered handling the request).

### `message`

When not given, the `message` field should be derived from the value of a
given `status` field.  If neither are present, the `status` field defaults to
`0`.  Thus, the `message` field would be set to `"Ok"`.

### `query`

There is no guarantee that all messages must have a `query` field.  The
recipient may fill this in if it can correlate the response with the request
through other means (e.g. the timing of message receipt vs. request).  This
field is considered a convenience field for highly asynchronous applications.

### `layout`

When not given, it is expected that a message recipient will attempt to sanely
detect the layout type by examining the contents of the `payload`.  In this
case, it is not the responsibility of the recipient to be 100% accurate in its
determination.  I best-guess is allowed.  The originator should specify this
field if there is the possibility of ambiguity.

### `payload`

When not given, the `payload` field assumes a default of `null` (empty
response contents).  This would correspond to a `layout` of `null`, as well.

Examples
--------

A valid, complete response that indicates a successful transaction can be an
empty dictionary.

    {}

This expands to:

    {
        "status"  : 0,
        "message" : "Ok",
        "layout"  : "null",
        "payload" : null
    }

A generic error with no context or additional information can be condensed to
a single root pair.

    {
        "status" : 99
    }

