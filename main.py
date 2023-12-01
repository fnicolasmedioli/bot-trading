import datetime
import os.path
import sys
import backtrader as bt

cantidad_transacciones = 0


class RSIStrategy(bt.Strategy):

    params = (
        ("sobrecompra", 50),
        ("sobreventa", 20),
    )

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex()

    def next(self):
        if self.rsi < self.params.sobreventa:
            self.buy()

        elif self.rsi > self.params.sobrecompra:
            self.sell()


class BollingerStrategy(bt.Strategy):

    params = (
        ("period", 20),
        ("devfactor", 2),
    )

    def __init__(self):

        self.dataclose = self.datas[0].close
        self.sma = bt.indicators.SimpleMovingAverage(self.dataclose, period=self.params.period)
        self.stddev = bt.indicators.StandardDeviation(self.dataclose, period=self.params.period)
        self.bollinger_top_band = self.sma + self.params.devfactor * self.stddev
        self.bollinger_low_band = self.sma - self.params.devfactor * self.stddev

    def next(self):

        global cantidad_transacciones

        if not self.position:
            if self.dataclose < self.bollinger_low_band:
                self.buy()
                cantidad_transacciones += 1

        elif self.dataclose > self.bollinger_top_band:
            self.sell()
            cantidad_transacciones += 1


class HombreColgadoStrategy(bt.Strategy):

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low

    def next(self):
        if self.dataclose[0] == self.datalow[0]:
            self.sell()


def main():

    cerebro = bt.Cerebro()

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))

    datapath = os.path.join(modpath, './data/orcl-1995-2014.txt')

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2002, 12, 31),
        reverse=False
    )

    cerebro.adddata(data)

    cerebro.addstrategy(BollingerStrategy, period=20, devfactor=0.05)
    cerebro.addstrategy(HombreColgadoStrategy)
    cerebro.addstrategy(RSIStrategy, sobrecompra=30, sobreventa=15)

    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)

    print('Dinero inicial: %.2f' % cerebro.broker.getvalue())

    money_inic = cerebro.broker.getvalue()

    cerebro.run()
    print()
    print('Dinero final: %.2f' % cerebro.broker.getvalue())

    money_finish = cerebro.broker.getvalue()

    dif_money = money_finish - money_inic
    print('Diferencia de dinero total: $%.2f' % dif_money)

    print("Cantidad de transacciones realizadas: " + str(cantidad_transacciones))


if __name__ == '__main__':
    main()
