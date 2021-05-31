
from pandas.plotting import register_matplotlib_converters
import pandas as pd
from bokeh.plotting import figure
from bokeh.io.state import curstate
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, NumeralTickFormatter, Arrow, VeeHead, Range1d

register_matplotlib_converters()


def get_base_fig(df, name, height):
    # Select the datetime format for the x axis depending on the timeframe
    df = df.reset_index()

    xaxis_dt_format = '%d.%m.%Y %H:%M:%S'
    if name[-3:] == "JPY":
        number_format1 = '%0.3f'
    elif name == "XAUUSD":
        number_format1 = '%0.2f'
    else:
        number_format1 = '%0.5f'
    # if df['Time'][start].hour > 0:
    #     xaxis_dt_format = '%d %b %Y, %H:%M:%S'

    pad_x = 100
    fig = figure(sizing_mode='stretch_width',
                 plot_height=height,
                 tools="xpan,xwheel_zoom,reset,save",
                 active_drag='xpan',
                 active_scroll='xwheel_zoom',
                 x_axis_type='linear',
                 x_range=Range1d(df.index[0] - pad_x, df.index[-1] + pad_x, bounds="auto"),
                 title=name
                 )
    fig.yaxis[0].formatter = NumeralTickFormatter(format="7.5f")
    inc = df.Close > df.Open
    dec = ~inc

    # # Color scheme for increasing and descending candles
    # increasing_color = '#17BECF'
    # decreasing_color = '#7F7F7F'
    increasing_color = '#FFFFFF'
    decreasing_color = '#000000'
    shadow_color = '#000000'
    # # sizing settings
    candle_width = 0.5

    inc_source = ColumnDataSource(data=dict(
        x1=df.index[inc],
        top1=df.Open[inc],
        bottom1=df.Close[inc],
        high1=df.High[inc],
        low1=df.Low[inc],
        date1=df.Time[inc]
    ))

    dec_source = ColumnDataSource(data=dict(
        x2=df.index[dec],
        top2=df.Open[dec],
        bottom2=df.Close[dec],
        high2=df.High[dec],
        low2=df.Low[dec],
        date2=df.Time[dec]
    ))

    # # Plot candles

    # High and low
    fig.segment(x0='x1', y0='high1', x1='x1', y1='low1', source=inc_source, color=shadow_color)
    fig.segment(x0='x2', y0='high2', x1='x2', y1='low2', source=dec_source, color=shadow_color)

    # Open and close
    r1 = fig.vbar(x='x1', width=candle_width, top='top1', bottom='bottom1', source=inc_source,
                  fill_color=increasing_color, line_color="black")
    r2 = fig.vbar(x='x2', width=candle_width, top='top2', bottom='bottom2', source=dec_source,
                  fill_color=decreasing_color, line_color="black")

    # Set up the hover tooltip to display some useful Data
    fig.add_tools(HoverTool(
        renderers=[r1],
        tooltips=[
            ("Open", "@top1{" + number_format1 + "}"),
            ("High", "@high1{" + number_format1 + "}"),
            ("Low", "@low1{" + number_format1 + "}"),
            ("Close", "@bottom1{" + number_format1 + "}"),
            ("Date", "@date1{" + xaxis_dt_format + "}")
        ],
        formatters={
            '@date1': 'datetime',
            '@top1': 'printf',
            '@high1': 'printf',
            '@low1': 'printf',
            '@bottom1': 'printf'
        }))

    fig.add_tools(HoverTool(
        renderers=[r2],
        tooltips=[
            ("Open", "@top2{" + number_format1 + "}"),
            ("High", "@high2{" + number_format1 + "}"),
            ("Low", "@low2{" + number_format1 + "}"),
            ("Close", "@bottom2{" + number_format1 + "}"),
            ("Date", "@date2{" + xaxis_dt_format + "}")
        ],
        formatters={
            '@date2': 'datetime',
            '@top2': 'printf',
            '@high2': 'printf',
            '@low2': 'printf',
            '@bottom2': 'printf'
        }))

    # Add date labels to x axis
    fig.xaxis.major_label_overrides = {
        i: date.strftime(xaxis_dt_format) for i, date in enumerate(pd.to_datetime(df["Time"], utc=True))
    }

    # JavaScript callback function to automatically zoom the Y axis to
    # view the Data properly
    source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low})
    callback = CustomJS(args={'y_range_candle': fig.y_range, 'source': source}, code='''
                   clearTimeout(window._autoscale_timeout);
                   var Index_candle = source.data.Index,
                       Low = source.data.Low,
                       High = source.data.High,
                       start = cb_obj.start,
                       end = cb_obj.end,
                       min_candle = Infinity,
                       max_candle = -Infinity;
                   for (var i=0; i < Index_candle.length; ++i) {
                       if (start <= Index_candle[i] && Index_candle[i] <= end) {
                           max_candle = Math.max(High[i], max_candle);
                           min_candle = Math.min(Low[i], min_candle);
                       }
                   }
                   var pad_candle = (max_candle - min_candle) * .1;
                   window._autoscale_timeout = setTimeout(function() {
                       y_range_candle.start = min_candle - pad_candle;
                       y_range_candle.end = max_candle + pad_candle;
                   });
               ''')

    # Finalise the figure
    fig.x_range.js_on_change('start', callback)

    return fig


def get_secondary_fig(title, fig, height, df, indicators, min_indicator, max_indicator):
    secondary_fig = figure(sizing_mode="stretch_width",
                           plot_height=height,
                           tools="xpan,xwheel_zoom,reset,save",
                           active_drag='xpan',
                           active_scroll='xwheel_zoom',
                           x_axis_type='linear',
                           x_range=fig.x_range,
                           title=title)

    if indicators is not None and len(indicators) != 0:
        indicators_list = []
        number_format = '%0.3f'
        for indicator in indicators:
            df_indicator = indicator['df']
            indicators_list.append(df_indicator.to_dict('Records'))
            source = ColumnDataSource(data=dict(
                index1=df_indicator.index,
                value1=df_indicator.value
            ))
            indicator_line = secondary_fig.line(x='index1', y='value1', source=source, line_width=indicator['width'],
                                                line_color=indicator['color'])

            secondary_fig.add_tools(HoverTool(
                renderers=[indicator_line],
                tooltips=[
                    ("Value", "@value1{" + number_format + "}")
                ],
                formatters={
                    '@value1': 'printf'
                }))

        # JavaScript callback function to automatically zoom the Y axis to
        # view the Data properly
        source = ColumnDataSource({'Index': df.index, 'High': df.High, 'Low': df.Low,
                                   'Index_Indicator': max_indicator.index, 'Max_Value_Indicator': max_indicator.value,
                                   'Min_Value_Indicator': min_indicator.value})
        callback = CustomJS(args={'y_range_candle': fig.y_range, 'y_range_indicator': secondary_fig.y_range,
                                  'source': source}, code='''
                           clearTimeout(window._autoscale_timeout);
                           var indexCandle = source.data.Index,
                               low = source.data.Low,
                               high = source.data.High,
                               start = cb_obj.start,
                               end = cb_obj.end,
                               minCandle = Infinity,
                               maxCandle = -Infinity;
                           for (var i=0; i < indexCandle.length; ++i) {
                               if (start <= indexCandle[i] && indexCandle[i] <= end) {
                                   maxCandle = Math.max(high[i], maxCandle);
                                   minCandle = Math.min(low[i], minCandle);
                               }
                           }
                           var indexInd = source.data.Index_Indicator,
                                maxValue = source.data.Max_Value_Indicator,
                                minValue = source.data.Min_Value_Indicator,
                                minInd = Infinity,
                                maxInd = -Infinity;
                            for (var i=0; i < indexInd.length; ++i) {
                                if (start <= indexInd[i] && indexInd[i] <= end) {
                                    maxInd = Math.max(maxValue[i], maxInd);
                                    minInd = Math.min(minValue[i], minInd);
                                }
                            }
                           var padCandle = (maxCandle - minCandle) * .1;
                           var padInd = (maxInd - minInd) * .2;
                           window._autoscale_timeout = setTimeout(function() {
                               y_range_candle.start = minCandle - padCandle;
                               y_range_candle.end = maxCandle + padCandle;
                               y_range_be.start = minInd - padInd;
                               y_range_be.end = maxInd + padInd;
                           });
                       ''')

        # Finalise the figure
        fig.x_range.js_on_change('start', callback)

        return secondary_fig


def set_figs_sync(data_frames, figs):
    source_list = []
    for i in range(len(data_frames)):
        df = data_frames[i].reset_index()
        source_list.append(ColumnDataSource({f'Index': df.index, f'High': df.High, f'Low': df.Low}))
    args = {}
    for i in range(len(figs)):
        args[f'y_range{i}'] = figs[i].y_range
        args[f'source{i}'] = source_list[i]

    code = '''
                clearTimeout(window._autoscale_timeout);
                var start = cb_obj.start,
                end = cb_obj.end;
        '''
    for i in range(len(figs)):
        code += f'''
                   var Index_candle{i} = source{i}.data.Index,
                       Low{i} = source{i}.data.Low,
                       High{i} = source{i}.data.High,
                       min_candle{i} = Infinity,
                       max_candle{i} = -Infinity;
                   for (var i=0; i < Index_candle{i}.length; ++i) {{
                       if (start <= Index_candle{i}[i] && Index_candle{i}[i] <= end) {{
                           max_candle{i} = Math.max(High{i}[i], max_candle{i});
                           min_candle{i} = Math.min(Low{i}[i], min_candle{i});
                       }}
                   }}
                   var pad_candle{i} = (max_candle{i} - min_candle{i}) * .1;
        '''
    code += '''
        window._autoscale_timeout = setTimeout(function() {
    '''
    for i in range(len(figs)):
        code += f'''
                    y_range{i}.start = min_candle{i} - pad_candle{i};
                    y_range{i}.end = max_candle{i} + pad_candle{i};
        '''
    code += '''
        });
    '''
    callback = CustomJS(args=args, code=code)

    figs[0].x_range.js_on_change('start', callback)