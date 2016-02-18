#=============================================================================
#
# JDI: JSON Data Interchange
#
#=============================================================================

"""
JDI: JSON Data Interchange
==========================

Provides a Pythonic interface for working with JDI messages.

See [docs/format.md](docs/format.md) for message format conventions.
"""


import collections
import json


__version__ = '0.0.0'


#=============================================================================
class Message( object ):
    """
    Models a generic JDI message.
    """


    #=========================================================================

    # Field specification information
    # `compact` is True if the field is included in compact messages
    _field_spec = collections.namedtuple(
        '_field_spec',
        [ 'default', 'compact' ]
    )


    #=========================================================================

    # Python type to layout map
    type2layout = {
        type( None ) : 'null',
        bool         : 'boolean',
        int          : 'integer',
        float        : 'double',
        str          : 'string',
        list         : 'array',
        dict         : 'hash'
    }

    # Layout to Python type map
    layout2type = dict( ( v, k ) for k, v in type2layout.items() )
    layout2type.update(
        {
            'decimal'   : float,
            'vector'    : list,
            'list'      : list,
            'document'  : dict,
            'record'    : dict,
            'recordset' : dict,
            'schema'    : dict
        }
    )

    # Base status message table
    status_message = {
        0  : 'Ok',
        1  : 'No Data',
        2  : 'No Change',
        10 : 'Not Authorized',
        11 : 'Invalid Request',
        30 : 'Server Unavailable',
        31 : 'Retrieval Error',
        99 : 'Unknown Error'
    }


    #=========================================================================
    def __init__( self, init = None, compact = False ):
        """
        Initializes a message object.

        @param init
        @param compact
        """

        # Set output compaction flag.
        self.compact = compact

        # Initialize from FLO.
        if hasattr( init, 'read' ):
            self._init = json.load( init )

        # Initialize from string.
        elif type( init ) is str:
            self._init = json.loads( init )

        # Initialize from dictionary-like-object.
        elif hasattr( init, 'get' ):
            self._init = init

        # Initialize from any other object.
        elif hasattr( init, '__dict__' ):
            self._init = init.__dict__

        # Initialize from empty message.
        else:
            self._init = {}

        # Set base message fields.
        self._fields = {}
        self._declare_field( 'layout', default = 'null' )
        self._declare_field( 'payload' )


    #=========================================================================
    def __contains__( self, key ):
        """
        Tests the message for field membership.
        Note: This is sensitive to the `compact` flag.

        @param key The name of the root key for which to test
        @return    True if the root key should be present in the message
        """

        # Key is not valid for this message.
        if key not in self._fields:
            return False

        # The message is not compact.
        if self.compact == False:
            return True

        # The key is enabled for compact messages.
        if self._fields[ key ].compact == True:
            return True

        # Message is compact, and the key is not enabled for compact messages.
        return False


    #=========================================================================
    def __getitem__( self, key ):
        """
        Supports subscript notation for root keys in the message.

        @param key The name of the requested key
        @return    The value of the requested item
        """
        try:
            value = getattr( self, key )
        except AttributeError:
            raise KeyError( key )
        return value


    #=========================================================================
    def __iter__( self ):
        """
        Supports iteration to allow the message to act like a dictionary.
        Note: This is sensitive to the `compact` flag.

        @return The iterator of the message's root keys.
        """

        # Scan through all message fields.
        for key in self._fields.keys():

            # Ensure this key is available for the message.
            if self.__contains__( key ):

                # Allow this field to be iterated.
                yield key


    #=========================================================================
    def __setitem__( self, key, value ):
        """
        Supports subscript notation for root keys in the message.

        @param key   The name of the requested key
        @param value The value to set for the requested key
        @return      The value of the requested item
        """
        if hasattr( self, key ) == False:
            raise KeyError( key )
        setattr( self, key, value )


    #=========================================================================
    def __str__( self ):
        """
        Serializes the object for use in message output.

        @return A JSON string representing the message
        """
        return json.dumps( self )


    #=========================================================================
    @classmethod
    def detect_layout( cls, payload ):
        """
        Attempts to auto-detect the layout of a message given a payload.

        TODO: Add type checking to the payload inspection.

        @param payload The payload value
        """

        # Convert data type to JDI layout string.
        layout = cls.type2layout.get( type( payload ), None )

        # Check hash layouts for known fields.
        if layout == 'hash':

            # documents have type and content.
            if ( 'type' in payload ) and ( 'content' in payload ):
                layout = 'document'

            # records and recordsets have lists of fields.
            elif 'fields' in payload:

                # records have lists of values.
                if 'values' in payload:
                    layout = 'record'

                # recordsets have lists of value lists.
                elif 'records' in payload:
                    layout = 'recordset'

            # schemas have keys and lists of field lists.
            elif ( 'keys' in payload ) and ( 'values' in payload ):
                layout = 'schema'

        # Return the layout we detected.
        return layout


    #=========================================================================
    def to_json( self ):
        """
        Allows this class to be serialized using a JSON encoder.

        @return A dictionary to use for JSON serialization
        """

        # Temporary container to help JSON serialization
        content = {}

        # Scan through declared fields.
        for name, spec in self._fields.items():

            # Ensure this field should be present in the message.
            if self.__contains__( name ):

                # Fetch the value of this field.
                data = getattr( self, name )

                # Set the value in the field in the message contents.
                content[ name ] = data

        # Return the message contents.
        return content


    #=========================================================================
    def _declare_field( self, name, default = None, compact = False ):
        """
        Declares a new field in the message.

        @param name    The name of the field (root key)
        @param default The default value of the field (if not initalized)
        @param compact True if this field is present in "compact" messages
        """

        # Add field specifier.
        self._fields[ name ] = self._field_spec( default, compact )

        # Set initial value of the field.
        setattr( self, name, self._init.get( name, default ) )


#=============================================================================
class Request( Message ):
    """
    Models a JDI request message.
    """


    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes a Request object.
        """
        super( Request, self ).__init__( *args, **kwargs )
        self._declare_field( 'context' )


#=============================================================================
class Response( Message ):
    """
    Models a JDI response message.
    """


    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes a Response object.
        """
        super( Response, self ).__init__( *args, **kwargs )
        self._declare_field( 'status', default = 0 )
        self._declare_field(
            'message',
            default = self.status_message.get(
                self._init.get( 'status', 0 ),
                'Ok'
            )
        )



#=============================================================================
def _auto_encoder( self, obj ):
    """
    Provides a patched JSON encoder method to allow JSON methods to be used
    without requiring the user to manually specify the correct encoder when
    serializing JDI messages.  The statements following this monkey-patches
    the function as the new default method.

    Non-trivial objects can implement a quasi-magical method named `to_json()`
    that is used to retrieve an object that is a type that can be serialized
    by the default encoder.

    @param obj The object that is being serialized by the JSON module
    @return    An object that can be serialized by the JSON module
    """

    # If the object has a `to_json()` method use it.  Otherwise, use the usual
    # encoder method.
    return getattr( obj.__class__, 'to_json', _default_encoder )( obj )


# Monkey-patch JSON's default encoder method.
_default_encoder = json.JSONEncoder.default
json.JSONEncoder.default = _auto_encoder

