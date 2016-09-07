from easyquant import StrategyTemplate
from easyquant import DefaultLogHandler
from easyquant import etime
from easyquant import StockSQL,get_exit_price
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
        self.exit_data = get_exit_price(self.trade_stocks)
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
            
    def get_exit_price0(self, hold_codes=['300162']):#, has_update_history=False):
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
            self.exit_data = get_exit_price(self.monitor_stocks)
        #"""
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
        self.log.info('动态止损监测股票：  %s'  % self.monitor_stocks)
        self.log.info('止损点：  %s'  % self.exit_data)
        self.log.info('行情推行股票 ：  %s'  % list(event.data.keys()))
        if etime.is_tradetime(dt.datetime.now()) and etime.is_trade_date(dt.datetime.now()):
            for event_code in self.monitor_stocks:
                if event_code in list(event.data.keys()):
                    event_data = event.data[event_code]
                    exit_all_price = self.exit_data[event_code]['exit_all']
                    exit_half_price = self.exit_data[event_code]['exit_half']
                    exit_chg_rate = self.exit_data[event_code]['exit_rate']
                    t_rate = self.exit_data[event_code]['t_rate']
                    realtime_p =  event_data['now']
                    if exit_all_price:
                        pass
                    else:
                        last_close = event_data['close']
                        if last_close:
                            exit_all_price = last_close * (1+exit_chg_rate)
                            exit_half_price = exit_all_price
                        else:
                            pass
                    """
                    if exit_half_price > realtime_p and exit_half_price and realtime_p:# and event_code not in ['002807','601009','300431','002284']:
                        self.user.sell_stock_by_low(stock_code=event_code,exit_price=exit_half_price,realtime_price=realtime_p,sell_rate=0.5)
                    """
                    if event_code=='600152':
                        #realtime_p = 10.8
                        pass
                    if exit_all_price > realtime_p and exit_all_price and realtime_p:# and event_code not in ['002807','601009','300431','002284']:
                        self.user.sell_stock_by_low(stock_code=event_code,exit_price=exit_all_price,realtime_price=realtime_p,sell_rate=1.0)
                else:
                    self.log.info('股票  %s需要加载行情推送。'  % event_code)
                    continue
        else:
            print('Not trade time....')
            
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
        this_time = dt.datetime.now()
        date_str = this_time.strftime('%Y%m%d')
        return DefaultLogHandler(self.name, log_type='file', filepath='exit_strategry_%s.log' %date_str)

    
                                        

