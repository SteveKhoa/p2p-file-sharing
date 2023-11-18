from enum import Enum

class RequestTypes(Enum):
    POST = "post"
    GET_PEER = "get_peer"
    RETURN_PEER = "return_peer"

    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
    FETCH = "fetch"
    
    PING = "ping"
    PONG = "pong"
    DISCOVER = "discover"
    REVEAL = "reveal"
    DISCONNECT = "disconnect"

    