<?php

spl_autoload_register(
    function( $name ) {
        echo $name . "\n";
        error_log( "DIAG: $name" );
        #include $name . '.php';
        class JDIMessage {
            public function __toString() {
                return 'hello!';
            }
        }
    }
);

$message = new JDIMessage();

header( 'Content-Type: text/json' );
echo $message;

