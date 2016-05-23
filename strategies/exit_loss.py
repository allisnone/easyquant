from easyquant import StrategyTemplate


def get_exit_price(codes=['300162']):
    exit_dict={'300162': {'exit_half':22.5, 'exit_all': 19.0},'002696': {'exit_half':17.10, 'exit_all': 15.60}}
    return exit_dict

class Strategy(StrategyTemplate):
    name = '止损策略'

    def strategy(self, event):
        self.log.info('\n\n止损策略触发')
        self.log.info('行情数据: 雷曼光电 %s' % event.data['300162'])
        self.log.info('检查持仓')
        self.log.info(self.user.balance)
        self.log.info(self.user.position)
        self.log.info('\n')
        holding_stock = self.user.position['证券代码'].values.tolist()
        stop_trade_code_list = ['000917','000932','002766','601009','002696']
        trade_code = list(set(holding_stock).difference(set(stop_trade_code_list)))
        self.log.info('止损检测股票：  %s'  % trade_code)
        exit_data = get_exit_price(trade_code)
        for event_code in trade_code:
            event_data = event.data[event_code]
            self.log.info('event_data：  %s'  % event_data)
            self.log.info('exit_data：  %s'  % exit_data[event_code])
            self.user.sell_stock_by_low(stock_code=event_code,exit_price=exit_data[event_code]['exit_half'],realtime_price=event_data['now'],sell_rate=0.5)
            self.user.sell_stock_by_low(stock_code=event_code,exit_price=exit_data[event_code]['exit_all'],realtime_price=event_data['now'])
                                        

