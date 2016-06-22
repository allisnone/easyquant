# -*- coding:utf-8 -*-
from custom import fixedmainengine
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()
    m = fixedmainengine.FixedMainEngine(broker='yh', need_data='yh.json', ext_stocks=['159915'])
    m.load_strategy()
    m.start()
