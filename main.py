import datetime
import os.path
import sys
import backtrader as bt
import math

cantidad_transacciones = 0

# Date,Open,High,Low,Close,Adj Close,Volume

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        self.order = None
        self.dataclose = self.datas[0].close

        self.sma50 = bt.indicators.SimpleMovingAverage(self.dataclose, period=50)
        self.sma50_pesada = bt.indicators.WeightedAverage(self.dataclose, period=50)

        self.sma200 = bt.indicators.SimpleMovingAverage(self.dataclose, period=200)
        self.sma200_pesada = bt.indicators.WeightedAverage(self.dataclose, period=200)

        self.sma20 = bt.indicators.SimpleMovingAverage(self.dataclose, period=20)
        self.sma20_pesada = bt.indicators.WeightedAverage(self.dataclose, period=20)

        self.stddev20 = bt.indicators.StandardDeviation(self.dataclose, period=20)
        self.stddev50 = bt.indicators.StandardDeviation(self.dataclose, period=50)

        self.bollinger50_top_band = self.sma50 + 0.5 * self.stddev50
        self.bollinger50_low_band = self.sma50 - 0.5 * self.stddev50

        self.bollinger20_top_band = self.sma20 + 0.5 * self.stddev20
        self.bollinger20_low_band = self.sma20 - 0.5 * self.stddev20

    def next(self):

        global cantidad_transacciones

        self.log('Close, %.2f' % self.dataclose[0])

        if not self.position:

            if self.data.close < self.bollinger20_low_band:
                # Momento de comprar
                self.log('Pedido de compra por $%.2f' % self.dataclose[0])
                self.order = self.buy()
                cantidad_transacciones += 1

        else:

            if self.data.close > self.bollinger20_top_band:
                # Momento de vender
                self.log('Pedido de venta por $%.2f' % self.dataclose[0])
                self.order = self.sell()
                cantidad_transacciones += 1

    def notify_order(self, order):

        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("Se completo una compra por $%.2f" % order.executed.price)
            elif order.issell():
                self.log("Se completo una venta por $%.2f" % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None


def main():

    cerebro = bt.Cerebro()

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))

    datapath = os.path.join(modpath, './data/yhoo-1996-2014.txt')

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2001, 1, 1),
        # Do not pass values after this date
        todate=datetime.datetime(2001, 12, 31),
        reverse=False
    )

    cerebro.adddata(data)

    cerebro.addstrategy(TestStrategy)

    cerebro.broker.setcash(100000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    money_inic = cerebro.broker.getvalue()

    cerebro.run()
    print()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    money_finish = cerebro.broker.getvalue()

    dif_money = money_finish - money_inic
    print('Diferencia de dinero total: $%.2f' % dif_money)

    print("Cantidad de transacciones realizadas: " + str(cantidad_transacciones))


if __name__ == '__main__':
    main()
