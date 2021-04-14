class OrderListReq:
    """
    The order update received by request of order list.

    :member
        symbol: The symbol you subscribed.
        timestamp: The UNIX formatted timestamp generated by server in UTC.
        topic: request topic
        data : OrderListItem

    """

    def __init__(self):
        self.ts = 0
        self.topic = ""
        self.data = list()

    def print_object(self, format_data=""):
        from huobi.utils.print_mix_object import PrintBasic

        PrintBasic.print_basic(self.ts, format_data + "Timestamp")
        PrintBasic.print_basic(self.topic, format_data + "Channel")
        print("Order List as below : count " + str(len(self.data)))
        if len(self.data):
            for orderlistitem_obj in self.data:
                orderlistitem_obj.print_object("\t ")
                print()
