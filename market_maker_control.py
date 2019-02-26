import itertools as it

import bokeh.embed
import bokeh.layouts
import bokeh.models
import bokeh.plotting
import bokeh.resources
import pandas as pd
import numpy as np


def poisson_times(rate, end_time):
    exps = it.repeat(np.random.exponential)
    times = it.accumulate((e(1/rate) for e in exps))
    return it.takewhile(lambda t: t <= end_time, times)

def order_rate_func(delta, A, k):
    return A*np.exp(-k*np.abs(delta))

def order_arrivals(order_rate, A, k, end_time):
    return np.array(list(poisson_times(order_rate, end_time)))

def trade_times(deltas, A, k, end_time):
    order_rates = order_rate_func(deltas_ask, A, k)
    order_rates_inc = np.concatenate([order_rates[[0]], np.diff(order_rates)])

    times_inc = (order_arrivals(r, A, k, end_time) for r in order_rates_inc)
    return it.accumulate(times_inc, lambda acc, x: np.concatenate([acc, x]))

def align_to_grid(xs, grid):
    return np.unique([grid[grid <= x][-1] for x in xs])


np.random.seed(42)

sigma, A, k, gamma = 0.3, 0.9, 0.3, 0.01
end_time = 60

time_grid = pd.Index(np.linspace(0, end_time, 200), name='Time')
time_step = time_grid[1] - time_grid[0]

skews = np.linspace(-2, 2, 21)
spreads = np.linspace(2, 10, 21)
deltas_ask = np.linspace(5, 1, 21)
deltas_bid = -deltas_ask
deltas = np.concatenate([deltas_bid, deltas_ask])
deltas_w_zero = np.concatenate([[0], deltas])

reference_price = pd.Series(100 + np.cumsum(
    sigma*np.sqrt(time_step)*np.random.randn(len(time_grid))), time_grid)
prices = pd.concat([reference_price + d for d in deltas_w_zero],
                   keys=deltas_w_zero, axis=1)

times_bid_misaligned = trade_times(deltas_bid, A, k, end_time)
times_bid = pd.Series([align_to_grid(ts, time_grid)
                       for ts in times_bid_misaligned], deltas_bid)
trades_bid = pd.concat([prices[d][times_bid[d]] for d in deltas_bid],
                       keys=deltas_bid, axis=1)

times_ask_misaligned = trade_times(deltas_ask, A, k, end_time)
times_ask = pd.Series([align_to_grid(ts, time_grid)
                       for ts in times_ask_misaligned], deltas_ask)
trades_ask = pd.concat([prices[d][times_ask[d]] for d in deltas_ask],
                       keys=deltas_ask, axis=1)

trades = pd.concat([trades_bid, trades_ask], axis=1)

inventory_skew_inc = pd.DataFrame(0, time_grid, columns=skews)
for i in range(len(skews)):
    inventory_skew_inc.loc[times_ask[deltas_ask[i]], skews[i]] -= 1
    inventory_skew_inc.loc[times_bid[deltas_bid[-i-1]], skews[i]] += 1
inventory_skew = inventory_skew_inc.cumsum()

inventory_spread_inc = pd.DataFrame(0, time_grid, columns=spreads)
for i in range(len(spreads)):
    inventory_spread_inc.loc[times_ask[deltas_ask[-i-1]], spreads[i]] -= 1
    inventory_spread_inc.loc[times_bid[deltas_bid[-i-1]], spreads[i]] += 1
inventory_spread = inventory_spread_inc.cumsum()

delta_grid = pd.Index(np.linspace(-5, 5, 101), name='delta')
rate_bid = pd.Series(order_rate_func(delta_grid[delta_grid<=0], A, k),
                     delta_grid[delta_grid<=0], name='Bid')
rate_ask = pd.Series(order_rate_func(delta_grid[delta_grid>=0], A, k),
                     delta_grid[delta_grid>=0], name='Ask')
rates = pd.concat([rate_bid, rate_ask], axis=1)
rates_skew = pd.concat([pd.Series(
    order_rate_func(np.array([s - 3, s + 3]), A, k),
    pd.Index([s - 3, s + 3], name='delta'), name=s) for s in skews], axis=1)
rates_spread = pd.concat([pd.Series(
    order_rate_func(np.array([-s/2, s/2]), A, k),
    pd.Index([-s/2, s/2], name='delta'), name=s) for s in spreads], axis=1)

prices.columns = ['{:.1f}'.format(d) for d in prices.columns]
prices['Bid'], prices['Ask'] = prices['-3.0'], prices['3.0']
bokeh_prices = bokeh.models.ColumnDataSource(prices)

trades.columns = ['{:.1f}'.format(d) for d in trades.columns]
trades['Bid'], trades['Ask'] = trades['-3.0'], trades['3.0']
bokeh_trades = bokeh.models.ColumnDataSource(trades)

inventory_skew.columns = ['{:.1f}'.format(s) for s in inventory_skew.columns]
inventory_skew['Current'] = inventory_skew['0.0']
bokeh_inventory_skew = bokeh.models.ColumnDataSource(inventory_skew)

rates_skew.columns = ['{:.1f}'.format(s) for s in rates_skew.columns]
rates_skew['Current'] = rates_skew['0.0']
bokeh_rates_skew = bokeh.models.ColumnDataSource(rates_skew)

p1 = bokeh.plotting.figure(plot_height=300, y_axis_label='Price',
                           y_range=(prices.min().min(), prices.max().max()),
                           x_range=(0, end_time))
p1.line(x='Time', y='0.0', color='grey', source=bokeh_prices)
p1_ask = p1.line(x='Time', y='Bid', color='blue', source=bokeh_prices)
p1_bid = p1.line(x='Time', y='Ask', color='red', source=bokeh_prices)
p1.circle(x='Time', y='Bid', color='black', source=bokeh_trades)
p1.circle(x='Time', y='Ask', color='black', source=bokeh_trades)

p3 = bokeh.plotting.figure(plot_height=300, y_axis_label='Inventory',
                           y_range=(inventory_skew.min().min(),
                                    inventory_skew.max().max()),
                           x_range=(0, end_time))
p3.line(x='Time', y='Current', source=bokeh_inventory_skew)

p2 = bokeh.plotting.figure(plot_height=300, y_axis_label='Order rate',
                           x_range=(delta_grid[0], delta_grid[-1]))
p2.line(x='delta', y='Ask', color='red', source=rates)
p2.line(x='delta', y='Bid', color='blue', source=rates)
p2.circle(x='delta', y='Current', color='black', source=bokeh_rates_skew, size=8)

callback_code = """
   var skew = cb_obj.value;
   iv.data['Current'] = iv.data[skew.toFixed(1)];
   rs.data['Current'] = rs.data[skew.toFixed(1)];
   var d_ask = skew + 3
   var d_bid = skew - 3
   prs.data['Ask'] = prs.data[d_ask.toFixed(1)];
   prs.data['Bid'] = prs.data[d_bid.toFixed(1)];
   trs.data['Ask'] = trs.data[d_ask.toFixed(1)];
   trs.data['Bid'] = trs.data[d_bid.toFixed(1)];
   iv.change.emit();
   rs.change.emit();
   prs.change.emit();
   trs.change.emit();
"""
callback = bokeh.models.CustomJS(
    args=dict(prs=bokeh_prices, trs=bokeh_trades, iv=bokeh_inventory_skew,
              rs=bokeh_rates_skew), code=callback_code)
slider = bokeh.models.widgets.Slider(start=-2, end=2, value=0, step=.2,
                                     title="Skew")
slider.js_on_change('value', callback)

skew_plot = bokeh.layouts.gridplot([[p1, p2], [p3, slider]])
html = bokeh.embed.file_html(skew_plot, bokeh.resources.CDN)
with open('20190226/skew_plot.html', 'w') as f:
    f.write(html)


bokeh_prices = bokeh.models.ColumnDataSource(prices)
bokeh_trades = bokeh.models.ColumnDataSource(trades)

inventory_spread.columns = ['{:.1f}'.format(s) for s in inventory_spread.columns]
inventory_spread['Current'] = inventory_spread['6.0']
bokeh_inventory_spread = bokeh.models.ColumnDataSource(inventory_spread)

rates_spread.columns = ['{:.1f}'.format(s) for s in rates_spread.columns]
rates_spread['Current'] = rates_spread['6.0']
bokeh_rates_spread = bokeh.models.ColumnDataSource(rates_spread)

p1 = bokeh.plotting.figure(plot_height=300, y_axis_label='Price',
                           y_range=(prices.min().min(), prices.max().max()),
                           x_range=(0, end_time))
p1.line(x='Time', y='0.0', color='grey', source=bokeh_prices)
p1_ask = p1.line(x='Time', y='Bid', color='blue', source=bokeh_prices)
p1_bid = p1.line(x='Time', y='Ask', color='red', source=bokeh_prices)
p1.circle(x='Time', y='Bid', color='black', source=bokeh_trades)
p1.circle(x='Time', y='Ask', color='black', source=bokeh_trades)

p3 = bokeh.plotting.figure(plot_height=300, y_axis_label='Inventory',
                           y_range=(inventory_spread.min().min(),
                                    inventory_spread.max().max()),
                           x_range=(0, end_time))
p3.line(x='Time', y='Current', source=bokeh_inventory_spread)

p2 = bokeh.plotting.figure(plot_height=300, y_axis_label='Order rate',
                           x_range=(delta_grid[0], delta_grid[-1]))
p2.line(x='delta', y='Ask', color='red', source=rates)
p2.line(x='delta', y='Bid', color='blue', source=rates)
p2.circle(x='delta', y='Current', color='black', source=bokeh_rates_spread, size=8)

callback_code = """
   var spread = cb_obj.value;
   iv.data['Current'] = iv.data[spread.toFixed(1)];
   rs.data['Current'] = rs.data[spread.toFixed(1)];
   var d_ask = spread/2
   var d_bid = -spread/2
   prs.data['Ask'] = prs.data[d_ask.toFixed(1)];
   prs.data['Bid'] = prs.data[d_bid.toFixed(1)];
   trs.data['Ask'] = trs.data[d_ask.toFixed(1)];
   trs.data['Bid'] = trs.data[d_bid.toFixed(1)];
   iv.change.emit();
   rs.change.emit();
   prs.change.emit();
   trs.change.emit();
"""
callback = bokeh.models.CustomJS(
    args=dict(prs=bokeh_prices, trs=bokeh_trades, iv=bokeh_inventory_spread,
              rs=bokeh_rates_spread), code=callback_code)
slider = bokeh.models.widgets.Slider(start=2, end=10, value=6, step=.4,
                                     title="Spread")
slider.js_on_change('value', callback)

spread_plot = bokeh.layouts.gridplot([[p1, p2], [p3, slider]])
html = bokeh.embed.file_html(spread_plot, bokeh.resources.CDN)
with open('20190226/spread_plot.html', 'w') as f:
    f.write(html)
