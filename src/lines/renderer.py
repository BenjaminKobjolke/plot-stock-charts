"""
Chart renderer for horizontal lines.

This module handles adding horizontal line overlays to lightweight-charts.
"""

import logging
from typing import List, Tuple


class LineRenderer:
    """
    Renders horizontal lines as overlays on stock charts.
    
    Integrates with lightweight-charts-python to add horizontal line series.
    """
    
    def __init__(self):
        """Initialize the line renderer."""
        self.logger = logging.getLogger(__name__)
    
    def add_horizontal_lines_to_chart(self, chart, 
                                    lines_data: List[Tuple[str, float, str, int]]) -> None:
        """
        Add horizontal lines to the chart.
        
        Args:
            chart: lightweight-charts Chart instance
            lines_data: List of (label, value, color, width) tuples
            
        Raises:
            ValueError: If chart or data is invalid
        """
        if not chart:
            raise ValueError("Chart instance is required")
        
        if not lines_data:
            self.logger.info("No horizontal lines data to render")
            return
        
        self.logger.info(f"Adding {len(lines_data)} horizontal lines to chart")
        
        # Add each horizontal line
        for label, value, color, width in lines_data:
            try:
                self._add_horizontal_line(chart, label, value, color, width)
                
            except Exception as e:
                self.logger.error(f"Failed to add horizontal line {label}: {e}")
                # Continue with other lines
    
    def _add_horizontal_line(self, chart, label: str, value: float, 
                           color: str, width: int) -> None:
        """
        Add a single horizontal line to the chart.
        
        Args:
            chart: lightweight-charts Chart instance
            label: Line label for display
            value: Y-axis value for the horizontal line
            color: Hex color code for the line
            width: Line width in pixels
        """
        self.logger.info(f"Adding horizontal line '{label}' at {value}, color {color}, width {width}")
        
        try:
            # Create horizontal line using the correct API parameters
            line = chart.horizontal_line(
                price=value,
                color=color,
                width=width,
                style='solid',
                text=label,
                axis_label_visible=True
            )
            
            self.logger.debug(f"Successfully added horizontal line '{label}' at price {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to create horizontal line '{label}': {e}")
            raise
    
    def validate_chart_compatibility(self, chart) -> bool:
        """
        Validate that the chart instance supports horizontal lines.
        
        Args:
            chart: Chart instance to validate
            
        Returns:
            True if chart supports horizontal lines, False otherwise
        """
        try:
            # Check if chart has required methods
            if not hasattr(chart, 'horizontal_line'):
                self.logger.error("Chart does not support horizontal line creation")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Chart compatibility check failed: {e}")
            return False
