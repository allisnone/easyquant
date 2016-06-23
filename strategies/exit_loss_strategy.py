from easyquant import StrategyTemplate
import easyhistory


class Strategy(StrategyTemplate):
    name = '止损策略'
    #exit_data ={}
    #has_update_history = False
    def get_exit_price(self, hold_codes=['300162']):#, has_update_history=False):
        #exit_dict={'300162': {'exit_half':22.5, 'exit_all': 19.0},'002696': {'exit_half':17.10, 'exit_all': 15.60}}
        has_update_history = True
        if not has_update_history:
            easyhistory.init('D', export='csv', path="C:/hist",stock_codes=hold_codes)
            easyhistory.update(path="C:/hist",stock_codes=hold_codes)
            #has_update_history = True
        his = easyhistory.History(dtype='D', path='C:/hist',codes=hold_codes)
        exit_dict = dict()
        for code in hold_codes:
            #code_hist_df = hist[code].MA(1).tail(3).describe()
            exit_data = dict()
            describe_df = his[code].MA(1).tail(3).describe()
            min_low =round(describe_df.loc['min'].low, 2)
            min_close = round(round(describe_df.loc['min'].close,2),2)
            max_close = round(describe_df.loc['max'].close,2)
            max_high = round(describe_df.loc['max'].high,2)
            exit_data['exit_half'] = min_close
            exit_data['exit_all'] = min_low
            exit_dict[code] = exit_data
        #print('exit_dict=%s' % exit_dict)
    return exit_dict

    def strategy(self, event):
        self.log.info('\n\n止损策略执行中。。。')
        self.log.info('行情数据:  %s' % event.data)
        self.log.info('检查持仓')
        self.log.info(self.user.balance)
        #self.log.info(self.user.position)
        self.log.info('\n')
        #holding_stock = self.user.position['证券代码'].values.tolist()
        #except_code_list = ['002766','601009','002696','002405','000932']
        #trade_code = list(set(holding_stock).difference(set(except_code_list)))
        trade_code = self.trade_stocks
        self.log.info('股票止损监测：  %s'  % trade_code)
        exit_data = self.get_exit_price(trade_code)
        self.log.info('止损点：  %s'  % exit_data)
        for event_code in trade_code:
            if event_code in list(event.data.keys()):
                event_data = event.data[event_code]
                if event_data['buy']!=0 and event_data['sell']!=0:
                    #self.log.info('event_data：  %s'  % event_data)
                    #self.log.info('exit_data of stock %s：  %s'  % (event_code, exit_data[event_code]))
                    self.user.sell_stock_by_low(stock_code=event_code,exit_price=exit_data[event_code]['exit_half'],realtime_price=event_data['now'],sell_rate=0.5)
                    self.user.sell_stock_by_low(stock_code=event_code,exit_price=exit_data[event_code]['exit_all'],realtime_price=event_data['now'])
                else:
                    self.log.info('股票  %s停牌。'  % event_code)
            else:
                self.log.info('股票  %s需要加载行情推送。'  % event_code)
                continue
                                        

