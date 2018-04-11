'''
This module can be run from the CLI or imported as a library.
When imported as library it will provide the following functions:

IPFS2PID( value ) - Convert an IPFS hash to a payment id
PID2IPFS( value ) - Convert a payment id to IPFS hash
'''

from binascii import hexlify, unhexlify
from itertools import takewhile

_B58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
_HEX_ALPHABET = '0123456789abcdef'

def _b58_encode( value ):
    '''Encode big-endian hex as a Base58 string'''
    value = unhexlify( value )
    v, z, r = int. from_bytes( value, 'big' ), sum( 1 for _ in takewhile( int( 0 ). __eq__, value )), ''
    while v:
        v, c = divmod( v, 58 )
        r = _B58_ALPHABET[ c ] + r
    return '1' * z + r

def _b58_decode( value ):
    '''Decode Base58 string into big-endian hex'''
    r = 0
    while value:
        r, value = r * 58 + _B58_ALPHABET. find( value[ 0 ]), value[ 1: ]
    return hexlify( r. to_bytes(( r. bit_length() + 7 ) // 8, byteorder = 'big' )). decode( 'latin-1' )

def IPFS2PID( value ):
    '''Convert an IPFS hash to a payment id'''
    return _b58_decode( value )[ 4: ]

def PID2IPFS( value ):
    '''Convert a payment id to IPFS value'''
    return _b58_encode( '1220' + value )

def _input( message, choice, length = None ):
    '''
    Get user input
    
    message - The message to display
    choice - The list of characters which are valid for input
    length - Number of characters expected in the response
    
    If the user input is invalid None is returned.
    If the user presses BREAK (CTRL-C on Windows) or EOF (CTRL-Z on Windows) the program terminates gracefully.
    Otherwise the entered string is returned.
    '''
    try:
        inp = input( message )
    except ( EOFError, KeyboardInterrupt ):
        exit( 0 )
    if length != None and len( inp ) != length:
        print( '\nBad input value - wrong number of characters\n' )
        return None
    elif not all( i in choice for i in inp ):
        print( '\nBad input value - illegal characters\n' )
        return None
    return inp

if '__main__' == __name__:
    while True:
        print( '1. IPFS to payment ID' )
        print( '2. Payment ID to IPFS' )
        print( 'To quit enter q\n' )
        inp = _input( 'Please enter your choice: ', '12qQ', 1 )
        if inp == None:
            continue
        elif inp in 'qQ':
            exit( 0 )
        elif inp == '1':
            ipfs = _input( 'Please enter a Base58 IPFS hash (46 digits): ', _B58_ALPHABET, 46 )
            if ipfs == None:
                continue
            else:
                result = IPFS2PID( ipfs )
        else:
            pid = _input( 'Please enter a hex payment ID (64 digits): ', _HEX_ALPHABET, 64 )
            if pid == None:
                continue
            else:
                result = PID2IPFS( pid )
        print( '\n' + result + '\n' )
