from enum import IntFlag, auto

class MoveTransform(IntFlag):
    NONE         = 0          # Simple move, no transformation
    PROMOTION    = auto()     # Fighter → Torpedo
    MERGE        = auto()     # Corvette + Corvette → Battleship
    DEMOTION     = auto()     # Battleship → Dreadnought
    DECOUPLE_CV  = auto()     # Battleship → Corvette (origin) + Corvette (dest)
    DECOUPLE_BM  = auto()     # Dreadnought → Bomber (dest) + Interceptor (origin)
    DECOUPLE_IN  = auto()     # Dreadnought → Interceptor (dest) + Bomber (origin)
    COUPLE       = auto()     # Bomber + Interceptor → Dreadnought
    BOARDING     = auto()     # Interceptor + enemy Bomber → Dreadnought
