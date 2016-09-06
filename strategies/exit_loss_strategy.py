from easyquant import StrategyTemplate
from easyquant import DefaultLogHandler
from easyquant import StockSQL
import easyhistory
import datetime as dt
from dateutil import tz



class Strategy(StrategyTemplate):
    name = '止损策略'
    exit_data ={}
    #has_update_history = False
    monitor_stocks = []
    def init(self):
        self.log.info(self.user.position)
        self.set_monitor_stocks()
        self.exit_data = self.get_exit_price(self.trade_stocks)
        """
        clock_type = "盘前"
        moment_last = dt.time(9, 10, 0, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment(clock_type, moment_last)
        
        minute_interval = 5
        self.clock_engine.register_interval(minute_interval, trading=False)
        """
    def set_monitor_stocks(self):
        his_sql = StockSQL()
        hold_df,hold_stocks,available_sells =his_sql.get_hold_stocks(accounts=['36005'])
        self.monitor_stocks = available_sells
            
    def get_exit_price(self, hold_codes=['300162']):#, has_update_history=False):
        #exit_dict={'300162': {'exit_half':22.5, 'exit_all': 19.0},'002696': {'exit_half':17.10, 'exit_all': 15.60}}
        has_update_history = True
        hold_codes = self.monitor_stocks 
        """
        if not has_update_history:
            easyhistory.init('D', export='csv', path="C:/hist",stock_codes=hold_codes)
            easyhistory.update(path="C:/hist",stock_codes=hold_codes)
            #has_update_history = True
        """
        #his = easyhistory.History(dtype='D', path='C:/hist',codes=hold_codes)
        #data_path = 'C:/hist/day/data/'
        data_path = 'C:/中国银河证券海王星/T0002/export/' 
        his = easyhistory.History(dtype='D', path=data_path, type='csv',codes=hold_codes)
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
        #his_sql = StockSQL()
        #hold_df,hold_stocks,available_sells =his_sql.get_hold_stocks(accounts=['36005'])
        #print(datetime.datetime.now().minute)
        """
        if (datetime.datetime.now().minute)%3==0:
            self.log.info('维持心跳,查询持仓信息：')
            self.log.info(self.user.position)
        """
        #"""
        if dt.datetime.now().hour==9 and dt.datetime.now().minute==0:
            self.log.info('每天9点更新需要检测的止损股票：')
            #self.log.info(self.user.position)
            self.set_monitor_stocks()
            self.exit_data = self.get_exit_price(self.monitor_stocks)
        #"""
        #hold_stocks = self.trade_stocks
        hold_stocks = self.monitor_stocks
        print(hold_stocks)
        self.log.info('\n\n止损策略执行中。。。')
        self.log.info('行情数据:  %s' % event.data)
        self.log.info('检查资金')
        #self.log.info(self.user.balance)
        self.log.info('检查持仓')
        #self.log.info(self.user.position)
        self.log.info('\n')
        #holding_stock = self.user.position['证券代码'].values.tolist()
        #except_code_list = ['002766','601009','002696','002405','000932']
        #trade_code = list(set(holding_stock).difference(set(except_code_list)))
        #trade_code = self.trade_stocks
        self.log.info('动态止损监测股票：  %s'  % hold_stocks)
        #exit_data = self.get_exit_price(self.trade_stocks)
        #exit_data = self.get_exit_price(hold_stocks)
        self.log.info('止损点：  %s'  % self.exit_data)
        self.log.info('行情推行股票 ：  %s'  % event.data.keys())
        for event_code in hold_stocks:
            if event_code in list(event.data.keys()):
                event_data = event.data[event_code]
                """
                if self.exit_data[event_code]['exit_half'] > event_data['now'] and event_code not in ['002807','601009','300431','002284']:
                    self.user.sell_stock_by_low(stock_code=event_code,exit_price=self.exit_data[event_code]['exit_half'],realtime_price=event_data['now'],sell_rate=0.5)
                """   
                if self.exit_data[event_code]['exit_all'] > event_data['now']:# and event_code not in ['002807','601009','300431','002284']:
                    self.user.sell_stock_by_low(stock_code=event_code,exit_price=self.exit_data[event_code]['exit_all'],realtime_price=event_data['now'])
            else:
                self.log.info('股票  %s需要加载行情推送。'  % event_code)
                continue
            
    def clock(self, event):
        """
        if event.data.clock_event == '盘前':
            #更新K线，预测次日趋势，选股
            print('event.clock_event=',event.data.clock_event)
            self.set_monitor_stocks()
            self.exit_data = self.get_exit_price(self.monitor_stocks)
            self.log.info('update exit date in the morning:')
            self.log.info(self.exit_data)
        elif event.data.clock_event == 5:
            # 5 分钟的 clock
            self.log.info("%s分钟" % event.data.clock_event)
            print('event.clock_event=',event.data.clock_event)
            self.exit_data = self.get_exit_price(self.monitor_stocks)
            self.log.info("trading_state:%" % event.data.trading_state)
            if event.data.trading_state:
                print('update exit data:')
                self.log.info('event.clock_event=%s' % event.data.clock_event)
                self.exit_data = self.get_exit_price(self.monitor_stocks)
                print(self.exit_data)
                pass
            else:
                pass
        
        else:
            pass
        """
        pass
    
    def log_handler(self):
        """自定义 log 记录方式"""
        return DefaultLogHandler(self.name, log_type='file', filepath='exit_strategry.log')

    
                                        

