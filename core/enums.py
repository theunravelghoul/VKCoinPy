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
    CPU_STACK = "cpu_stack"
    COMPUTER = "computer"
    SERVER_VK = "server_vk"
    QUANTUM_PC = "quantum_pc"
    DATACENTER = "datacenter"
