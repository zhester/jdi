#=============================================================================
#
# jdi Module Unit Tests
#
#=============================================================================

"""
jdi Module Unit Tests
=====================
"""


import json
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import jdi


__version__ = '0.0.0'


#=============================================================================
class JDITests( unittest.TestCase ):
    """
    Tests the JDI module.
    """


    #=========================================================================
    # Common test inputs.

    DMSG = { 'layout' : 'string', 'payload' : 'Hello World' }
    SMSG = json.dumps( DMSG )


    #=========================================================================
    def setUp( self ):
        """
        Performs test case setup.
        """
        pass


    #=========================================================================
    def test_message_init_dict( self ):
        """
        Tests Message object initialization from a dictionary.
        """
        message = jdi.Message( self.DMSG )
        self.assertEqual( message.layout,  self.DMSG[ 'layout' ]  )
        self.assertEqual( message.payload, self.DMSG[ 'payload' ] )


    #=========================================================================
    def test_message_init_flo( self ):
        """
        Tests Message object initialization from a FLO.
        """
        flo     = StringIO( self.SMSG )
        message = jdi.Message( flo )
        self.assertEqual( message.layout,  self.DMSG[ 'layout' ]  )
        self.assertEqual( message.payload, self.DMSG[ 'payload' ] )


    #=========================================================================
    def test_message_init_object( self ):
        """
        Tests Message object initalization from another object.
        """

        # Source message for initialization
        source         = jdi.Message()
        source.layout  = self.DMSG[ 'layout' ]
        source.payload = self.DMSG[ 'payload' ]

        # Initialize from existing message
        message = jdi.Message( source )

        # Test proper initialization
        self.assertEqual( message.layout,  self.DMSG[ 'layout' ]  )
        self.assertEqual( message.payload, self.DMSG[ 'payload' ] )


    #=========================================================================
    def test_message_init_string( self ):
        """
        Tests Message object initialization from a string.
        """
        message = jdi.Message( self.SMSG )
        self.assertEqual( message.layout,  self.DMSG[ 'layout' ]  )
        self.assertEqual( message.payload, self.DMSG[ 'payload' ] )


    #=========================================================================
    def test_message_str( self ):
        """
        Tests Message object serialization.
        """
        message = jdi.Message( self.DMSG )
        string  = str( message )
        parsed  = json.loads( string )
        self.assertEqual( self.DMSG, parsed )


    #=========================================================================
    def test_message_sub_get( self ):
        """
        Tests subscript-notation item retrieval.
        """
        message = jdi.Message( self.DMSG )
        self.assertEqual( message[ 'layout' ], self.DMSG[ 'layout' ] )
        self.assertEqual( message[ 'payload' ], self.DMSG[ 'payload' ] )
        self.assertRaises( KeyError, lambda: message[ 'fake' ] )


    #=========================================================================
    def test_message_sub_set( self ):
        """
        Tests subscript-notation item updating.
        """
        message = jdi.Message( self.DMSG )
        layout  = 'list'
        payload = [ 1, 2, 3 ]
        message[ 'layout' ]  = layout
        message[ 'payload' ] = payload
        self.assertEqual( message[ 'layout' ], layout )
        self.assertEqual( message[ 'payload' ], payload )
        def bad_set( m ):
            m[ 'fake' ] = 'value'
        self.assertRaises( KeyError, bad_set, message )


    #=========================================================================
    def test_message_detect( self ):
        """
        Tests payload layout detection.
        """
        dl = jdi.Message.detect_layout
        self.assertEqual( dl( None ),                'null'    )
        self.assertEqual( dl( True ),                'boolean' )
        self.assertEqual( dl( 42 ),                  'integer' )
        self.assertEqual( dl( 3.14159 ),             'double'  )
        self.assertEqual( dl( 'Hello World' ),       'string'  )
        self.assertEqual( dl( [ 1, 2 ] ),            'array'   )
        self.assertEqual( dl( { 'a' : 1, 'b' : 2 } ), 'hash'   )

