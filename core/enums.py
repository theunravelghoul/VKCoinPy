class ResponseMessageTypes(object):
    INIT = 'INIT'
    NOT_ENOUGH_COINS = 'NOT_ENOUGH_COINS'
    SELF_DATA = 'SELF_DATA'
    MISS = 'MISS'
    BROKEN = 'BROKEN'
    TRANSFER = 'TR'
    TRANSACTION_IN_PROGRESS = "ANOTHER_TRANSACTION_IN_PROGRESS"


class RequestMessageTypes(object):
    GET_PLACE = "X"
    GET_SCORE = "GU"
    BUY_ITEM = "B"
    TICK = "TICK"
    TRANSFER = "T"


class ItemTypes(object):
    CURSOR = "cursor"
    CPU = "cpu"
    CPU_STACK = "CPU_STACK"
    COMPUTER = "COMPUTER"
    SERVER_VK = "SERVER_VK"
    QUANTUM_PC = "QUANTUM_PC"
    DATACENTER = "DATACENTER"
