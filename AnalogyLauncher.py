
from Config import Config
import Utility
from BaseChart import *

from bokeh.io import output_file
from bokeh.io import show
from bokeh.layouts import column
from bokeh.io.state import curstate

import os
from datetime import datetime

class AnalogyLauncher:

    configs = [
        {'Market': 'Dukascopy', 'Symbol': 'EURUSD', 'TimeFrame': 'D1'},
        {'Market': 'Dukascopy', 'Symbol': 'GBPUSD', 'TimeFrame': 'D1'},
    ]

    def __init__(self):

        data_list_dr = []
        for i in range(len(self.configs)):
            conf = self.configs[i]
            data_list_dr.append(f"Data/{conf['Market']}/{Config.categories_list[conf['Symbol']]}/"
                                f"{conf['Symbol']}/{conf['TimeFrame']}.csv")

        self.data_frames = Utility.csv_to_df(data_list_dr)

        for i in range(len(self.data_frames)):
            start_time = datetime.strptime(Config.start_date, Config.date_format)
            end_time = datetime.strptime(Config.end_date, Config.date_format)
            start_index = Utility.index_date(self.data_frames[i], start_time)
            end_index = Utility.index_date(self.data_frames[i], end_time)
            self.data_frames[i] = self.data_frames[i].iloc[start_index:end_index + 1]

        output_name = ""
        for i in range(len(self.configs)):
            conf = self.configs[i]
            output_name += f"[{conf['Market']}-{conf['Symbol']}-{conf['TimeFrame']}]"
        output_dir = f"Outputs/"
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        output_file(output_dir + output_name + ".html")

        title = ""
        for i in range(len(self.configs)):
            title += f"[{self.configs[i]['Symbol']}]"
        curstate().file.title = title

    def show(self):
        figs = []
        for i in range(len(self.configs)):
            figs.append(get_base_fig(self.data_frames[i], self.configs[i]['Symbol'], Config.height))

        if Config.zoom_synchronization:
            for i in range(1, len(figs)):
                figs[i].x_range = figs[0].x_range
            set_figs_sync(self.data_frames, figs)

        show(column(figs, sizing_mode='stretch_both'))


analogy = AnalogyLauncher()
analogy.show()


