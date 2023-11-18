from enum import Enum

class RequestTypes(Enum):
    POST = "post"
    REQUEST_END = "request_end"
    GET_PEER = "get_peer"
    RETURN_PEER = "return_peer"

    PUBLISH = "publish"
    FETCH = "fetch"
    
    PING = "ping"
    PONG = "pong"
    DISCOVER = "discover"


    