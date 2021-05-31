
import pandas as pd


def csv_to_df(csv_files: list, date_format='%d.%m.%Y %H:%M:%S.%f'):
    """
    Get a list of csv files, load them and parse date column(s)...
    Returns:
        a list of pandas Data-frames.
    """
    data_frames = []
    parse_date = lambda x: pd.datetime.strptime(x, date_format)
    for f in csv_files:
        try:
            df = pd.read_csv(f)
        except:
            df = pd.read_excel(f)

        if 'Local time' in df.columns:
            df.rename(columns={'Local time': 'Time'}, inplace=True)
        if 'Gmt time' in df.columns:
            df.rename(columns={'Gmt time': 'Time'}, inplace=True)
        if 'GMT' in df.columns:
            df.rename(columns={'GMT': 'Time'}, inplace=True)
        if 'Time' in df.columns:
            try:
                df['Time'] = pd.to_datetime(df['Time'], format=date_format)
            except:
                df['Time'] = pd.to_datetime(df['Time'])
        df = df.sort_values(['Time'])
        df = df.reset_index()
        data_frames.append(df)

    return data_frames


def index_date(data, date):
    start = 0
    end = len(data) - 1
    if date < data.iloc[start]['Time'] or date > data.iloc[end]['Time']:
        return -1
    i = 0
    while start <= end:
        i = int((start + end) / 2)
        if data.iloc[i]['Time'] == date:
            return i
        elif data.iloc[i]['Time'] < date:
            start = i + 1
        elif data.iloc[i]['Time'] > date:
            end = i - 1
    if data.iloc[i]['Time'] <= date:
        return i
    else:
        return i-1