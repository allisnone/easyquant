
from custom import fixedmainengine

m = fixedmainengine.FixedMainEngine(broker='yh', need_data='yh.json', ext_stocks=['159915'])
m.load_strategy()
m.start()
