import numpy as np
import pandas as pd
import glob
import plotly.graph_objects as go
import os
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.io as pio

pio.templates.default = "plotly_white"

class maps():
    def __init__(self):
        path0 = r"Fit_Data/"
        semi = "test/"
        
        folders = ["2D_AP2/", "2D_DC2/"]
        
        subfolders = ["2D_rdata/", "FT_camp/", "FT_camp_wtoint/", "FT_ramp/", "FT_iamp/"]
        
        scan_points = np.arange(-3000, +3000, 1)
        
        self.data = {"2D_AP2/":
                     {"2D_rdata/":{}, "FT_camp/":{}, "FT_camp_wtoint/":{}, "FT_ramp/":{}, "FT_iamp/":{}},
                    "2D_DC2/":
                     {"2D_rdata/":{}, "FT_camp/":{}, "FT_camp_wtoint/":{}, "FT_ramp/":{}, "FT_iamp/":{}}}

        for folder in folders:
            for subfolder in subfolders:
                print("Loading {}, {} data".format(folder, subfolder))
                path1 = path0 + folder + semi + subfolder
                
                for point in scan_points:
                    try:
                        temp = np.loadtxt(path1 + "{}.txt".format(point))
                        self.data[folder][subfolder][str(point)] = temp
                    except OSError:
                        pass
                    
        self.maxpoints = {"2D_AP2/":{}, "2D_DC2/":{}}
        for folder in folders:
            for subfolder in subfolders:
                array = []
                for matrix in list(self.data[folder][subfolder].values()):
                    array.append(matrix[1:, 1:].max())
                self.maxpoints[folder][subfolder] = max(array) 
                
        colorbar = dict(
            title='Amplitude',  # title here
            titleside='right',
            nticks=100,
            titlefont=dict(
                size=14,
                family='Arial, sans-serif'))
        
        # RUN DASH
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

        app.title = "Beating maps analysis!"

        app.layout = html.Div(
            children=[
                html.Div(
                    children=[
                        html.H1(
                            children="Beating maps analysis", className="header-title"
                        ),
                        html.P(
                            children="Analyze the beating maps",
                            className="header-description",
                        ),
                    ],
                    className="header",
                ),
                html.Label('Experiment'),
                dcc.Dropdown(
                    id='folder',
                    options=[{'label': i, 'value': i} for i in folders],
                    value='2D_AP2/',
                    style={"width": "50%"}
                ),
                html.Label('Type of information'),
                dcc.Dropdown(
                    id='subfolder',
                    options=[{'label': i, 'value': i} for i in subfolders],
                    optionHeight=20,
                    value='FT_camp/',
                    style={"width": "50%"}
                ),
                html.Label('Frequency Beating'),
                dcc.Dropdown(
                    id='point',
                    options=[{'label': i, 'value': i} for i in self.data["2D_AP2/"]["FT_camp/"].keys()],
                    optionHeight=20,
                    value='-342',
                    style={"width": "50%"}
                ),
                html.Label('Normalize'),
                dcc.Dropdown(
                    id='norm',
                    options=[{'label': i, 'value': i} for i in ["Yes", "No"]],
                    optionHeight=20,
                    value='Yes',
                    style={"width": "50%"}
                ),
                html.Div(dcc.Graph(id='indicator-graphic'),
                         ),
            ],
        )


        @app.callback(
            Output('indicator-graphic', 'figure'),
            Input('folder', 'value'),
            Input('subfolder', 'value'),
            Input('point', 'value'),
            Input('norm', 'value'))
            
        def update_graph(folder_name, subfolder_name, point_name, norm_name):
            temporal_data = self.data[folder_name][subfolder_name][point_name]
            zmax = self.maxpoints[folder_name][subfolder_name]

            if norm_name == "Yes":
                fig = go.Figure(data=go.Contour(x=temporal_data[0, 1:], y=temporal_data[1:, 0], z=temporal_data[1:, 1:]/zmax,
                                                colorscale="Hot_r",
                                                colorbar=colorbar,
                                                contours=dict(start=0, end=1, size=0.1)
                                                ))
            if norm_name == "No":
                fig = go.Figure(data=go.Contour(x=temporal_data[0, 1:], y=temporal_data[1:, 0], z=temporal_data[1:, 1:]/zmax,
                                                colorscale="Hot_r",
                                                colorbar=colorbar
                                                ))
            fig.update_layout(width=600, height=600)

            return fig


        app.run_server(mode="external", debug=False)                    

class integratedFT():
    def __init__(self):
        path0 = r"Fit_Data/"
        semi = "test/"
        
        folders = ["2D_AP2/", "2D_DC2/", "TG_AP1/", "TG_AP2/", "TG_DC1/", "TG_DC2/"]
        
        scan_files = ["integrated_ft", "integrated_ft_cross_low", "integrated_ft_cross_upp"]
        
        self.data = {"2D_AP2/":{"integrated_ft":{}, "integrated_ft_cross_low":{}, "integrated_ft_cross_upp":{}}, "2D_DC2/":{"integrated_ft":{}, "integrated_ft_cross_low":{}, "integrated_ft_cross_upp":{}},
                     "TG_AP1/":{"integrated_ft":{}, "integrated_ft_cross_low":{}, "integrated_ft_cross_upp":{}}, "TG_AP2/":{"integrated_ft":{}, "integrated_ft_cross_low":{}, "integrated_ft_cross_upp":{}},
                     "TG_DC1/":{"integrated_ft":{}, "integrated_ft_cross_low":{}, "integrated_ft_cross_upp":{}}, "TG_DC2/":{"integrated_ft":{}, "integrated_ft_cross_low":{}, "integrated_ft_cross_upp":{}}}

        for folder in folders:
            print("Loading {} data".format(folder))
            path1 = path0 + folder + semi
            for file in scan_files:                
                df = pd.read_csv(path1 + file + ".txt", header=None, sep = " ", names=["x", "y"])
                df = df.sort_values(by=["x"], ascending=True)
                df = df.reset_index(drop=True)
                df["ynor"] = df["y"] - df["y"][0:50].min()
                df["ynor"] = df["ynor"] / df["ynor"].max()
                self.data[folder][file] = df
        
        #RUN DASH
        
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

        app.title = "Integrated FT analysis!"

        app.layout = html.Div(
            children=[
                html.Div(
                    children=[
                        html.H1(
                            children="Integrated FT analysis", className="header-title"
                        ),
                        html.P(
                            children="Analyze the fourier spectra",
                            className="header-description",
                        ),
                    ],
                    className="header",
                ),
                html.Label('Experiment 1'),
                dcc.Dropdown(
                    id='folder',
                    options=[{'label': i, 'value': i} for i in folders],
                    value='2D_DC2/',
                    style={"width": "50%"}
                ),
                html.Label('Type of information 1'),
                dcc.Dropdown(
                    id='file',
                    options=[{'label': i, 'value': i} for i in scan_files],
                    optionHeight=20,
                    value='integrated_ft_cross_low',
                    style={"width": "50%"}
                ),
                html.Label('Normalize 1'),
                dcc.Dropdown(
                    id='norm',
                    options=[{'label': i, 'value': i} for i in ["Yes", "No"]],
                    optionHeight=20,
                    value='Yes',
                    style={"width": "50%"}
                ),
                 html.Label('Experiment 2'),
                dcc.Dropdown(
                    id='folder2',
                    options=[{'label': i, 'value': i} for i in folders],
                    value='2D_DC2/',
                    style={"width": "50%"}
                ),
                html.Label('Type of information 2'),
                dcc.Dropdown(
                    id='file2',
                    options=[{'label': i, 'value': i} for i in scan_files],
                    optionHeight=20,
                    value='integrated_ft_cross_upp',
                    style={"width": "50%"}
                ),
                html.Label('Normalize 2'),
                dcc.Dropdown(
                    id='norm2',
                    options=[{'label': i, 'value': i} for i in ["Yes", "No"]],
                    optionHeight=20,
                    value='Yes',
                    style={"width": "50%"}
                ),
                html.Div(dcc.Graph(id='indicator-graphic'),
                         ),
            ],
        )


        @app.callback(
            Output('indicator-graphic', 'figure'),
            Input('folder', 'value'),
            Input('file', 'value'),
            Input('norm', 'value'),
            Input('folder2', 'value'),
            Input('file2', 'value'),
            Input('norm2', 'value'))
            
        def update_graph(folder_name, file_name, norm_name, folder2_name, file2_name, norm2_name):
            temporal_data = self.data[folder_name][file_name]
            temporal_data2 = self.data[folder2_name][file2_name]

            fig = go.Figure()
            
            if norm_name == "Yes":
                fig.add_trace(go.Scatter(x=temporal_data["x"], y=temporal_data["ynor"], 
                                        name="Exp: {} Curve: {}".format(folder2_name, file2_name),
                                        line=dict(color='MediumSeaGreen')))
                
            if norm_name == "No":
                fig.add_trace(go.Scatter(x=temporal_data["x"], y=temporal_data["y"],
                                        name="Exp: {} Curve: {}".format(folder2_name, file2_name),
                                        line=dict(color='MediumSeaGreen')))
                
            if norm2_name == "Yes":
                fig.add_trace(go.Scatter(x=temporal_data2["x"], y=temporal_data2["ynor"],
                                        name="Exp: {} Curve: {}".format(folder2_name, file2_name),
                                        line=dict(color='Tomato')))
                
            if norm2_name == "No":
                fig.add_trace(go.Scatter(x=temporal_data2["x"], y=temporal_data2["y"],
                                        name="Exp: {} Curve: {}".format(folder2_name, file2_name),
                                        line=dict(color='Tomato')))
                
            fig.update_layout(width=1200, height=600)

            return fig


        app.run_server(mode="external", debug=False)    
        
                    
                    
                    