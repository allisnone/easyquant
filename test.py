# -*- coding:utf-8 -*-
import easyquotation
import easytrader
from easyquant.push_engine.clock_engine import ClockEngine
import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine
import datetime


#print('easyquant 测试 DEMO')
"""
print('请输入你使用的券商:')
choose = input('1: 华泰 2: 佣金宝 3: 银河 4: 雪球模拟组合\n:')

broker = 'ht'
if choose == '2':
    broker = 'yjb'
elif choose == '3':
    broker = 'yh'
elif choose == '4':
    broker = 'xq'


def get_broker_need_data(choose_broker):
    need_data = input('请输入你的帐号配置文件路径(直接回车使用 %s.json)\n:' % choose_broker)
    if need_data == '':
        return '%s.json' % choose_broker
    return need_data


need_data = get_broker_need_data(broker)
"""
def get_push_stocks(additional_stocks=[]):
    broker = 'yh'
    need_data = 'yh.json'
    user = easytrader.use('yh')
    user.prepare('yh.json')
    holding_stocks = user.position['证券代码'].values.tolist()
    #print('holding_stocks',holding_stocks)
    init_push_stocks = list(set( holding_stocks) | set(additional_stocks))
    return init_push_stocks


def get_stop_stocks(given_stocks=[]):
    quotation = easyquotation.use('sina')
    stop_stocks = []
    if given_stocks:
        this_quotation = quotation.stocks(given_stocks)
    else:
        this_quotation = quotation.all
    for stock_code in (this_quotation.keys()):
        if this_quotation[stock_code]['buy']==0 and this_quotation[stock_code]['sell']==0:
            stop_stocks.append(stock_code)
        else:
            pass
    return stop_stocks

init_push_stocks = get_push_stocks(additional_stocks=['000002','300162'])
#stop_stocks = get_stop_stocks(push_stocks)
#print('stop_stocks=', stop_stocks)
#print(len(stop_stocks))
#push_stocks = list(set(push_stocks).difference(set(stop_stocks)))
#print('push_stocks=%s' % push_stocks)

class LFEngine(PushBaseEngine):
    EventType = 'lf'

    def init(self):
        self.source = easyquotation.use('lf')
    
    def get_push_stocks(self):
        quotation = easyquotation.use('qq')
        holding_stocks = self.user.position['证券代码'].values.tolist()
        #print('holding_stocks',holding_stocks)
        init_push_stocks = list(set( holding_stocks) | set(self.stocks))
        if init_push_stocks:
            this_quotation = quotation.stocks(init_push_stocks)
        else:
            this_quotation = quotation.all
        stop_stocks = []
        for stock_code in (this_quotation.keys()):
            if this_quotation[stock_code]['buy']==0 and this_quotation[stock_code]['sell']==0:
                stop_stocks.append(stock_code)
            else:
                pass
        push_stocks = list(set(init_push_stocks).difference(set(stop_stocks)))
        return push_stocks

    def fetch_quotation(self):
        #return self.source.stocks(['162411', '000002','300162'])
        global init_push_stocks
        init_push_stocks = self.stocks
        #print('init_push_stocks=',init_push_stocks)
        stop_stocks = get_stop_stocks(init_push_stocks)
        #print('stop_stocks=', stop_stocks)
        #print(len(stop_stocks))
        push_stocks = list(set(init_push_stocks).difference(set(stop_stocks)))
        push_stocks = self.get_push_stocks()
        #print('push_stocks=%s' % push_stocks)
        return self.source.stocks(push_stocks)

#quotation_choose = input('请输入使用行情引擎 1: sina 2: leverfun 十档 行情(目前只选择了 162411, 000002)\n:')
quotation_choose = 2
quotation_engine = DefaultQuotationEngine if quotation_choose == '1' else LFEngine

push_interval = int(input('请输入行情推送间隔(s)\n:'))
quotation_engine.PushInterval = push_interval

#log_type_choose = input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录到指定文件\n: ')
#log_type = 'stdout' if log_type_choose == '1' else 'file'
log_type = 'stdout'
this_time = datetime.datetime.now()
date_str = this_time.strftime('%Y%m%d')
#log_filepath = input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''
log_filepath = 'strategy_log_%s.txt' % date_str

log_handler = DefaultLogHandler(name='测试', log_type=log_type, filepath=log_filepath)


m = easyquant.MainEngine(broker='yh', need_data='yh.json', quotation_engines=[quotation_engine], log_handler=log_handler,stocks=init_push_stocks)
m.load_strategy()
m.start()
