"""
Chart plotter using lightweight-charts-python.

This module handles creating and displaying interactive stock charts
with OHLCV data.
"""

from lightweight_charts import Chart
import configparser
from pathlib import Path
import logging
from typing import Optional

from ..data.data_models import StockDataset


class StockChartPlotter:
    """
    Creates and displays interactive stock charts using lightweight-charts-python.
    
    Supports candlestick charts with volume data and customizable appearance.
    """
    
    def __init__(self, config_path: str = "settings.ini"):
        """
        Initialize the chart plotter with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = configparser.ConfigParser()
        
        # Load configuration
        if Path(config_path).exists():
            self.config.read(config_path)
        else:
            self.logger.warning(f"Configuration file {config_path} not found, using defaults")
        
        # Get chart settings from config
        self.width = self.config.getint('CHART', 'width', fallback=1200)
        self.height = self.config.getint('CHART', 'height', fallback=600)
        self.theme = self.config.get('CHART', 'theme', fallback='dark')
        
        self.chart = None
    
    def create_chart(self, title: str = "Stock Chart") -> Chart:
        """
        Create a new chart instance with configured settings.
        
        Args:
            title: Title for the chart
            
        Returns:
            Configured Chart instance
        """
        self.chart = Chart(
            width=self.width,
            height=self.height,
            title=title
        )
        
        # Configure chart appearance based on theme
        if self.theme.lower() == 'dark':
            self.chart.layout(
                background_color='#1e1e1e',
                text_color='#ffffff'
            )
            self.chart.grid(
                vert_enabled=True,
                horz_enabled=True,
                color='#333333'
            )
        else:
            self.chart.layout(
                background_color='#ffffff',
                text_color='#000000'
            )
            self.chart.grid(
                vert_enabled=True,
                horz_enabled=True,
                color='#e0e0e0'
            )
        
        self.logger.info(f"Created chart with dimensions {self.width}x{self.height}, theme: {self.theme}")
        return self.chart
    
    def plot_candlestick_chart(self, dataset: StockDataset, 
                             title: str = "Stock Price Chart",
                             exchange_code: str = "",
                             date_str: str = "") -> None:
        """
        Plot a candlestick chart with the given dataset.
        
        Args:
            dataset: StockDataset containing OHLCV data
            title: Chart title
            exchange_code: Exchange code for display
            date_str: Date string for display
        """
        if not dataset:
            raise ValueError("Dataset is empty, cannot create chart")
        
        # Create chart title with exchange and date info
        full_title = title
        if exchange_code and date_str:
            full_title = f"{title} - {exchange_code} ({date_str})"
        elif exchange_code:
            full_title = f"{title} - {exchange_code}"
        elif date_str:
            full_title = f"{title} ({date_str})"
        
        # Create the chart
        chart = self.create_chart(full_title)
        
        # Convert dataset to lightweight-charts format
        chart_data = dataset.to_lightweight_charts_format()
        
        # Debug: Log the first and last data points being sent to chart
        if chart_data:
            self.logger.info(f"DEBUG: Chart data time range:")
            self.logger.info(f"DEBUG: First point: {chart_data[0]['time']}")
            self.logger.info(f"DEBUG: Last point: {chart_data[-1]['time']}")
        
        # Set the data - lightweight-charts expects a pandas DataFrame
        import pandas as pd
        df = pd.DataFrame(chart_data)
        chart.set(df)
        
        # Auto-fit the chart to show all data properly
        try:
            chart.fit()
            self.logger.info("DEBUG: Applied chart.fit() to auto-scale the view")
        except Exception as e:
            self.logger.warning(f"Could not apply chart.fit(): {e}")
        
        # Log the converted timestamps being sent to the chart
        if chart_data:
            self.logger.info(f"DEBUG: Chart timestamps after timezone conversion:")
            self.logger.info(f"DEBUG: First point: {chart_data[0]['time']}")
            self.logger.info(f"DEBUG: Last point: {chart_data[-1]['time']}")
        
        self.logger.info(f"Created candlestick chart with {len(chart_data)} data points")
    
    def plot_with_volume(self, dataset: StockDataset,
                        title: str = "Stock Price & Volume Chart",
                        exchange_code: str = "",
                        date_str: str = "") -> None:
        """
        Plot a candlestick chart with volume subplot.
        
        Args:
            dataset: StockDataset containing OHLCV data
            title: Chart title
            exchange_code: Exchange code for display
            date_str: Date string for display
        """
        if not dataset:
            raise ValueError("Dataset is empty, cannot create chart")
        
        # Create chart title with exchange and date info
        full_title = title
        if exchange_code and date_str:
            full_title = f"{title} - {exchange_code} ({date_str})"
        elif exchange_code:
            full_title = f"{title} - {exchange_code}"
        elif date_str:
            full_title = f"{title} ({date_str})"
        
        # Create the chart
        chart = self.create_chart(full_title)
        
        # Convert dataset to lightweight-charts format
        chart_data = dataset.to_lightweight_charts_format()
        
        # Set the main candlestick data
        import pandas as pd
        df = pd.DataFrame(chart_data)
        chart.set(df)
        
        self.logger.info(f"Created chart with candlesticks and volume, {len(chart_data)} data points")
    
    def show_chart(self, block: bool = True) -> None:
        """
        Display the chart.
        
        Args:
            block: Whether to block execution until chart is closed
        """
        if self.chart is None:
            raise ValueError("No chart created. Call plot_candlestick_chart() or plot_with_volume() first.")
        
        self.logger.info("Displaying chart...")
        self.chart.show(block=block)
    
    def save_chart(self, filename: str) -> None:
        """
        Save the chart to a file.
        
        Note: Save functionality may not be available in all versions of lightweight-charts-python.
        
        Args:
            filename: Output filename (should end with .html)
        """
        if self.chart is None:
            raise ValueError("No chart created. Call plot_candlestick_chart() or plot_with_volume() first.")
        
        self.logger.warning("Save functionality is not available in the current version of lightweight-charts-python")
        self.logger.info("Chart will be displayed instead. You can manually save from the browser.")
