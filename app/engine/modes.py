
from typing import Literal

def adjust_thresholds(base_buy: float, base_sell: float, mode: Literal['konservativ','normal','aggressiv','normal']='normal'):
    if mode == 'konservativ':
        return base_buy + 0.1, base_sell - 0.1
    if mode == 'aggressiv':
        return base_buy - 0.15, base_sell + 0.15
    return base_buy, base_sell
