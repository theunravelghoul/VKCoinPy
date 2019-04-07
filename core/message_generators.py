from core.enums import RequestMessageTypes


class RequestMessageGenerator(object):
    @staticmethod
    def generate_pack(*args, **kwargs):
        messages_sent = kwargs['messages_sent']
        pack = "P{} {}".format(
            messages_sent, ' '.join([str(arg) for arg in args]))
        return pack

    @staticmethod
    def generate_get_place_message() -> str:
        return RequestMessageTypes.GET_PLACE

    @staticmethod
    def generate_get_score_message() -> str:
        return RequestMessageTypes.GET_SCORE

    @staticmethod
    def generate_buy_item_message(**kwargs) -> str:
        item_id = kwargs['item_id']
        return RequestMessageGenerator.generate_pack(RequestMessageTypes.BUY_ITEM, item_id, **kwargs)

    @staticmethod
    def generate_transfer_message(**kwargs):
        amount = kwargs['amount']
        user_id = kwargs['user_id']
        return RequestMessageGenerator.generate_pack(RequestMessageTypes.TRANSFER, user_id, amount, **kwargs)

    @staticmethod
    def generate_tick_message(**kwargs) -> str:
        random_id = kwargs['random_id']
        messages_sent = kwargs['messages_sent']
        return "C{} {} 1".format(messages_sent, random_id)
