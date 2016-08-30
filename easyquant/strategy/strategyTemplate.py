# coding:utf-8
import sys
import traceback
import dill
import easyquotation
import datetime
ACCOUNT_OBJECT_FILE = 'account.session'


class StrategyTemplate:
    name = 'DefaultStrategyTemplate'

    def __init__(self, log_handler, main_engine,stocks=[],additional_stocks=['000002'],except_stocks=['600556']):
        with open(ACCOUNT_OBJECT_FILE, 'rb') as f:
            self.user = dill.load(f)
            f.close()
        self.main_engine = main_engine
        self.clock_engine = main_engine.clock_engine
        # 优先使用自定义 log 句柄, 否则使用主引擎日志句柄
        self.log = self.log_handler() or log_handler
        self.stocks = stocks
        self.additional_stocks = additional_stocks
        self.except_stocks = except_stocks
        self.init()

    def init(self):
        # 进行相关的初始化操作
        pass
    
    @property
    def trade_stocks(self):
        return self.get_push_stocks()
    
    def get_push_stocks(self):
        quotation = easyquotation.use('qq')
        holding_stocks = self.stocks
        if not holding_stocks:
            holding_stocks = self.user.position['证券代码'].values.tolist()
        print('holding_stocks=',holding_stocks)
        init_push_stocks = list(set( holding_stocks) | set(self.additional_stocks))
        init_push_stocks = list(set(init_push_stocks).difference(set(self.except_stocks)))
        if init_push_stocks:
            this_quotation = quotation.stocks(init_push_stocks)
        else:
            this_quotation = quotation.all
        stop_stocks = []
        print(list(this_quotation.keys()))
        for stock_code in list(this_quotation.keys()):
            if this_quotation[stock_code]:
                #print(this_quotation[stock_code])
                print(this_quotation[stock_code]['bid1_volume'], this_quotation[stock_code]['ask1_volume'])
                if this_quotation[stock_code]['bid1_volume']>0 or this_quotation[stock_code]['ask1_volume']>0:
                    pass
                else:
                    print(stock_code)
                    stop_stocks.append(stock_code)
        push_stocks = list(set(init_push_stocks).difference(set(stop_stocks)))
        return push_stocks

    def strategy(self, event):
        """:param event event.data 为所有股票的信息，结构如下
        {'162411':
        {'ask1': '0.493',
         'ask1_volume': '75500',
         'ask2': '0.494',
         'ask2_volume': '7699281',
         'ask3': '0.495',
         'ask3_volume': '2262666',
         'ask4': '0.496',
         'ask4_volume': '1579300',
         'ask5': '0.497',
         'ask5_volume': '901600',
         'bid1': '0.492',
         'bid1_volume': '10765200',
         'bid2': '0.491',
         'bid2_volume': '9031600',
         'bid3': '0.490',
         'bid3_volume': '16784100',
         'bid4': '0.489',
         'bid4_volume': '10049000',
         'bid5': '0.488',
         'bid5_volume': '3572800',
         'buy': '0.492',
         'close': '0.499',
         'high': '0.494',
         'low': '0.489',
         'name': '华宝油气',
         'now': '0.493',
         'open': '0.490',
         'sell': '0.493',
         'turnover': '420004912',
         'volume': '206390073.351'}}
    
        """
    def heartbeat(self):
        if (datetime.datetime.now().minute)%3==0:
            self.log.info('维持心跳,查询持仓信息：')
            self.log.info(self.user.position)
        return

    def run(self, event):
        try:
            self.heartbeat()
            self.strategy(event)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log.error(repr(traceback.format_exception(exc_type,
                                                           exc_value,
                                                           exc_traceback)))

    
    def clock(self, event):
        pass

    def log_handler(self):
        """
        优先使用在此自定义 log 句柄, 否则返回None, 并使用主引擎日志句柄
        :return: log_handler or None
        """
        return None
