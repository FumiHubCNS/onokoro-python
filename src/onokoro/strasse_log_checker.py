"""!
@file test
@version 1
@author Fumutaka ENDO
@date 2025-06-28T18:50:58+09:00
@brief log viewer
"""
import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz
import sys
import os
import argparse 

def parse_temperature_log(file_path):
    """!
    @brief parse strasse log file

    @param efile_path input file path

    @return DataFrame
    """
    data_lines = []

    in_comment_block = False
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # コメントブロックのトグル
            if line.startswith("///"):
                in_comment_block = not in_comment_block
                continue
            if in_comment_block or line == '':
                continue
            data_lines.append(line)

    # データをタブで分割してDataFrame化
    df = pd.DataFrame([line.split("\t") for line in data_lines])

    # 列名付与（1列目: timestamp、以降 val_1, val_2, ...）
    df.columns = ["timestamp"] + [f"val_{i}" for i in range(1, len(df.columns))]

    return df

def check_log_onokoro57(input_path=None):
    """!
    @brief read and plot logs

    @param input_path input file path
    """
    # ログファイルをすべて読み込む
    log_files = sorted(glob.glob(input_path))  # 例：カレントディレクトリにある .txt ファイルすべて

    all_data = pd.concat([parse_temperature_log(f) for f in log_files], ignore_index=True)

    new_columns = ["Timestamp","Target Holder (bottom)","Target Holder (1/3)","Target Holder (top)","Cold Head (stage 1)","Feed-Through (Supply)","Feed-Through (Return)","2nd stage CH (SD)","2nd stage CH (PT)","Setpoint(1)","PT02 (Cryostat filling line)","PT01 (Buffer Tank)","Target Chamber","Cryostat Chamber","Gas System Pump","heater output 1","heater output 2","Cold Valve (ON=100%/OFF=0%)","Compressor (ON=100%/OFF=0%)","H2 Filling (ON=100%/OFF=0%)"]

    all_data.columns = new_columns

    # 数値列を float に変換（非数は NaN）
    for col in all_data.columns[1:]:
        all_data[col] = pd.to_numeric(all_data[col], errors='coerce')

    all_data['Timestamp'] = all_data['Timestamp'].str.replace("h/", ":", regex=False)\
                                 .str.replace("m/", ":", regex=False)\
                                 .str.replace("s", "", regex=False)

    all_data['Timestamp'] = pd.to_datetime(all_data['Timestamp'], format="%Y/%m/%d_%H:%M:%S")
    # 1. まずドイツ時間をローカライズ（夏時間あり：Europe/Berlin）
    all_data['Timestamp'] = all_data['Timestamp'].dt.tz_localize('Europe/Berlin')
    # 2. 日本時間（JST）に変換
    all_data['Timestamp'] = all_data['Timestamp'].dt.tz_convert('Asia/Tokyo')


    # x軸列（timestampなど）
    x_col = all_data.columns[0]

    plot_y_labels = ["Temperatures [K]", "Pressures [bar]", "tatus / heater output [%]"]

    # 描画する列グループ（例：2〜10列、11〜15列、16〜20列）
    groups = [
        all_data.columns[2:11],
        all_data.columns[11:16],
        all_data.columns[16:21],
    ]

    # サブプロットを作成（行数 = グループ数）
    fig = make_subplots(rows=len(groups), cols=1, shared_xaxes=False, vertical_spacing=0.05)

    # 各グループを描画
    for i, group in enumerate(groups):
        for col in group:
            fig.add_trace(
                go.Scatter(
                    x=all_data[x_col],
                    y=all_data[col],
                    mode='lines',
                    name=col,
                    showlegend=(i >= 0)  # 最初の行だけに凡例を表示
                ),
                row=i + 1,
                col=1
            )
        fig.update_yaxes(title_text=f"{plot_y_labels[i]}", row=i + 1, col=1)

    # レイアウト調整
    fig.update_layout(
        height=300 * len(groups),
        title_text="STRASSE log viewr",
        legend=dict(
            orientation="v",
            x=1.05,
            y=1,
            xanchor='left',
            yanchor='top'
        )
    )

    fig.show()

def check_log():
    """!
    @brief log plot method for uv command 

    CLI argument:
    @arg input files path for loading
    @arg experiment-number experiment number
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-in","--input", help="files path for loading", type=str, default="./data/onokoro57/logs/*.txt")
    parser.add_argument("-en","--experiment-number", help="experiment number", type=int, default=57)
    args = parser.parse_args()

    input_path: str = args.input
    experiment_number: int = args.experiment_number

    if experiment_number == 57:
        check_log_onokoro57(input_path)
    else:
        print('experiment number does not exist')