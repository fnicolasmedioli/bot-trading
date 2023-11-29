import datetime
import os.path
import sys
import backtrader as bt
import math

########   Date,Open,High,Low,Close,Adj Close,Volume  #####################

class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):

        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        # if self.order:
        #     return
        # Check if we are in the market

        # Ventana tempora
        ventana_temporal = 5

        MM50 = self.calcular_SMA(50)
        MM200 = self.calcular_SMA(200)
        desviacion_estandar = self.calcular_desviacion_estandar(20)
        bolu = MM50 + 1 * desviacion_estandar
        bold = MM50 - 1 * desviacion_estandar

        if not self.position:

            if (self.dataclose[0] < bold):
                # Momento de comprar
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()

            #if MM50 > MM200:
            #    self.log('BUY CREATE, %.2f' % self.dataclose[0])
            #    self.order = self.buy()

        else:

            if (self.dataclose[0] > bolu):
                # Momento de vender
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

            # Already in the market ... we might sell
            #if len(self) >= (self.bar_executed + 5):
            # SELL, SELL, SELL!!! (with all possible default parameters)
            #    self.log('SELL CREATE, %.2f' % self.dataclose[0])
            #    # Keep track of the created order to avoid a 2nd order
            #    self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("Se completo una compra")
                #self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log("Se completo una venta")
                #MM50 = self.calcular_SMA(50)
                #MM200 = self.calcular_SMA(200)
                #if MM50 < MM200:
                #    self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self) # Saving when the order was executed

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
                # Write down: no pending order
        self.order = None


    def calcular_SMA(self, ventana):

        return self.calcular_media_de_cierre(ventana)
    

    def calcular_media_de_cierre(self, ventana):

        assert type(ventana) == int, "ventana debe ser int, se recibió un " + str(type(ventana))

        suma = 0

        for i in range(-ventana + 1, 1):
            suma += self.dataclose[i]

        return suma / ventana
    

    def calcular_desviacion_estandar(self, ventana):

        media = self.calcular_media_de_cierre(ventana)

        suma_cuadrada = 0

        for i in range(-ventana + 1, 1):
            suma_cuadrada += math.pow(self.dataclose[i] - media, 2)
        
        return math.sqrt(suma_cuadrada/ventana)


if __name__ == '__main__':

    cerebro = bt.Cerebro()

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))

    datapath = os.path.join(modpath, './data/yhoo-1996-2014.txt')
    
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2000, 1, 1),
        # Do not pass values after this date
        todate=datetime.datetime(2000, 12, 31),
        reverse=False
    )

    cerebro.adddata(data)

    cerebro.addstrategy(TestStrategy)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    moneyInic = cerebro.broker.getvalue()
    # Run over everything
    cerebro.run()
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    moneyFinish = cerebro.broker.getvalue()

    difMoney = moneyFinish - moneyInic
    print('Diferencia de dinero total: %.2f' % difMoney)
