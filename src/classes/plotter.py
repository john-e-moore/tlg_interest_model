import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import List, Union

class Plotter:
    def __init__(self, df: pd.DataFrame, output_folder: str):
        self.df = df
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
    def plot_line(self, 
                  x_col: Union[str, None], 
                  y_cols: List[str], 
                  x_axis_label: str, 
                  y_axis_label: str, 
                  marker: str = 'o', 
                  linestyle: str = '-', 
                  filename: str = 'line_plot.png', 
                  use_index: bool = False, 
                  title: str = 'Line Plot', 
                  legend_loc: str = 'best') -> None:
        plt.figure()
        if use_index:
            self.df[y_cols].plot(marker=marker, linestyle=linestyle)
            plt.xlabel('Index')
        else:
            self.df.plot(x=x_col, y=y_cols, marker=marker, linestyle=linestyle)
            plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(True)
        plt.legend(loc=legend_loc)
        plt.savefig(os.path.join(self.output_folder, filename))
        plt.close()

    def plot_stacked_area(self, 
                          x_col: Union[str, None], 
                          y_cols: List[str], 
                          x_axis_label: str, 
                          y_axis_label: str, 
                          filename: str = 'stacked_area_plot.png', 
                          use_index: bool = False, 
                          title: str = 'Stacked Area Plot', 
                          legend_loc: str = 'best') -> None:
        plt.figure()
        if use_index:
            self.df[y_cols].plot.area()
            plt.xlabel('Index')
        else:
            self.df.plot.area(x=x_col, y=y_cols)
            plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(True)
        plt.legend(loc=legend_loc)
        plt.savefig(os.path.join(self.output_folder, filename))
        plt.close()

    def plot_bar(self, 
                 x_col: Union[str, None], 
                 y_cols: List[str], 
                 x_axis_label: str, 
                 y_axis_label: str, 
                 filename: str = 'bar_plot.png', 
                 horizontal: bool = False, 
                 stacked: bool = False, 
                 use_index: bool = False, 
                 title: str = 'Bar Plot', 
                 legend_loc: str = 'best') -> None:
        plt.figure()
        if use_index:
            if horizontal:
                self.df[y_cols].plot.barh(stacked=stacked)
            else:
                self.df[y_cols].plot.bar(stacked=stacked)
            plt.xlabel('Index')
        else:
            if horizontal:
                self.df.plot.barh(x=x_col, y=y_cols, stacked=stacked)
            else:
                self.df.plot.bar(x=x_col, y=y_cols, stacked=stacked)
            plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(True)
        plt.legend(loc=legend_loc)
        plt.savefig(os.path.join(self.output_folder, filename))
        plt.close()

    def plot_histogram(self, 
                       x_col: str, 
                       num_buckets: int, 
                       filename: str = 'histogram.png', 
                       use_index: bool = False, 
                       title: str = 'Histogram') -> None:
        plt.figure()
        if use_index:
            self.df[x_col].plot.hist(bins=num_buckets)
            plt.xlabel('Index')
        else:
            self.df[x_col].plot.hist(bins=num_buckets)
            plt.xlabel(x_col)
        plt.ylabel('Frequency')
        plt.title(title)
        plt.grid(True)
        plt.savefig(os.path.join(self.output_folder, filename))
        plt.close()

# Example usage:
# df = pd.DataFrame(...)  # Your DataFrame
# plotter = Plotter(df, 'output')
# plotter.plot_line('x', ['y1', 'y2'], 'X Axis', 'Y Axis', title='Custom Line Plot', legend_loc='upper left')
