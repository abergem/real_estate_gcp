# -*- coding: utf-8 -*-

# General imports
import numpy as np
import pandas as pd
import textwrap

import sys
from tornado.ioloop import IOLoop

# GCP imports
from google.cloud import bigquery
from google.cloud import bigquery_storage_v1beta1

# Bokeh imports
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON_RETINA
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.models import ColumnDataSource, HoverTool, Select
from bokeh.palettes import small_palettes
from bokeh.transform import transform, factor_cmap
from bokeh.models.widgets import Tabs, Panel
from bokeh.layouts import column

from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.server.server import Server


def modify_doc(doc):   
    
    # Make clients
    bq_client = bigquery.Client()
    bq_storage_client = bigquery_storage_v1beta1.BigQueryStorageClient()

    query_string = '''
    SELECT *
    FROM `advance-nuance-248610`.real_estate.processed_finn_ads
    '''
    df = bq_client.query(query_string).result().to_dataframe(bqstorage_client=bq_storage_client)

    df['price_sqm'] = df['price'].astype(float) / df['net_internal_area'].astype(float) / 1000
    
    def wgs84_to_web_mercator(df, long, lat):
        """Converts decimal longitude/latitude to Web Mercator format"""
        k = 6378137
        df['x'] = df[long] * (k * np.pi/180.0)
        df['y'] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
        return df
    
    df = wgs84_to_web_mercator(df, 'longitude', 'latitude')
    
    # Set df as source
    source = ColumnDataSource(df)
    # source.remove('index')
    
    # web mercator coordinates
    # x_range, y_range = ((10.6e5, 10.9e5), (59.84e5, 59.98e5))
    x_range, y_range = ((1e5, 32e5), (80e5, 115e5))
    
    # *********************************
    # Tab 1: Prices per square meter
    
    # Customize hover tool
    hover = HoverTool(
        tooltips=[
            ('Address', '@address'),
            ('price / sqm', '@price_sqm'),
            ('price', '@price'),
            ('sqm', '@gross_internal_area'),
            ('floor', '@floor')
            ])
    
    # Create glyph
    p1 = figure(width=800, height=800,
                tools=['pan', 'wheel_zoom', hover],
                active_scroll='wheel_zoom',
                toolbar_location='above',
                x_range=x_range,
                y_range=y_range,
                x_axis_type="mercator",
                y_axis_type="mercator")
    
    # Add map tile
    p1.add_tile(CARTODBPOSITRON_RETINA)
    
    # Define palette for sealice
    palette = small_palettes['OrRd'][3][::-1]
    
    # Create color mapper
    color_mapper = LinearColorMapper(palette=palette, 
                                     low=50,
                                     high=150)
    
    # Add circle on glyph for localities
    p1.circle(x='x', 
              y='y',
              color=transform('price_sqm', color_mapper),
              fill_alpha=0.8,
              size=8,
              source=source)
    
    # Create color bar object
    color_bar = ColorBar(color_mapper=color_mapper, 
                         label_standoff=12, 
                         location=(0, 0),
                         title='price/sqm')
    
    # Add color bar to glyph
    p1.add_layout(color_bar, 'right')
    
    # Create widget for selecting property type
    select1 = Select(title='Property_type', value='type', options=['Include all']+(df.type.unique().tolist()))
    
    def select_callback1(attr, old, new):
        selected = select1.value
        if selected == 'Include all':
            new_data = df
        else:
            new_data = df[df.type == selected]
        
        source.data = ColumnDataSource(new_data).data
    
    select1.on_change('value', select_callback1)
    
    # # *********************************
    # # Tab2 : PD 

    # # Customize hover tool
    # hover = HoverTool(
    #     tooltips=[
    #              ('Locality', '@LocalityName'),
    #              ('PD', '@PD')
    #              ])
    
    # # Create glyph
    # p2 = figure(width=800, height=800,
    #             tools=['pan', 'wheel_zoom', hover],
    #             active_scroll='wheel_zoom',
    #             toolbar_location='above',
    #             x_range=x_range,
    #             y_range=y_range,
    #             x_axis_type="mercator",
    #             y_axis_type="mercator")
    
    # # Add map tile
    # p2.add_tile(CARTODBPOSITRON_RETINA)
    
    # # Define palette for PD
    # palette = ['darkred', 'orange']

    # # Create color mapper
    # colors = factor_cmap('PD', palette=palette, factors=['Proven', 'Suspicion'], nan_color = 'linen')
    
    # # Add circle on glyph for localities
    # p2.circle(x='x', 
    #           y='y',
    #           color=colors,
    #           fill_alpha=0.5,
    #           legend='PD',
    #           size=8,
    #           source=source)
    
    # p2.legend.location = "bottom_right"
    
    # # Create widget for selecting owner filter
    # select2 = Select(title='Owner', value='OwnerName', options=['Include all']+(df.OwnerName.unique().tolist()))
    
    # def select_callback2(attr, old, new):
    #     selected = select2.value
    #     if selected == 'Include all':
    #         new_data = df
    #     else:
    #         new_data = df[df.OwnerName == selected]
            
    #     source.data = ColumnDataSource(new_data).data
    
    # select2.on_change('value', select_callback2)
    
    # *********************************
    
    # Add figure and widget to the document
    l1 = column(select1, p1)
    # l2 = column(select2, p2)
    
    tab1 = Panel(child=l1, title="Property prices in Oslo")
    # tab2 = Panel(child=l2, title="Pancreas Disease")
    tabs = Tabs(tabs=[tab1])
    
    doc.add_root(tabs)


def old_main(_):
    

    io_loop = IOLoop.current()
    bokeh_app = Application(FunctionHandler(modify_doc))
    server_kwargs = {'port': 8830}
    server = Server({'/': bokeh_app}, io_loop=io_loop, **server_kwargs)

    server.start()

    io_loop.add_callback(server.show, "/")


def main():
    """Launch the server and connect to it.
    """
    print("Preparing a bokeh application.")
    io_loop = IOLoop.current()
    bokeh_app = Application(FunctionHandler(modify_doc))

    server = Server({"/": bokeh_app}, io_loop=io_loop)
    server.start()
    print("Opening Bokeh application on http://localhost:5006/")

    io_loop.add_callback(server.show, "/")
    io_loop.start()


if __name__ == '__main__':
    #main(sys.argv[1:])
    print('hi')
    main()
