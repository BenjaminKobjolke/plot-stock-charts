"""
Indicator argument parser for command line interface.

This module handles parsing and validation of the --indicators parameter.
"""

import re
import logging
from typing import List, Tuple, Optional


class IndicatorParser:
    """
    Parses and validates indicator specifications from command line arguments.
    
    Supports format: "ema_50|red,ema_200|#00FF00"
    """
    
    def __init__(self):
        """Initialize the indicator parser."""
        self.logger = logging.getLogger(__name__)
        
        # Supported indicator types
        self.supported_indicators = {'ema'}
        
        # Named color mappings
        self.named_colors = {
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'orange': '#FFA500',
            'purple': '#800080',
            'cyan': '#00FFFF',
            'magenta': '#FF00FF',
            'black': '#000000',
            'white': '#FFFFFF',
            'gray': '#808080',
            'grey': '#808080'
        }
    
    def parse_indicators(self, indicators_str: str) -> List[Tuple[str, int, str]]:
        """
        Parse indicators string into structured data.
        
        Args:
            indicators_str: String like "ema_50|red,ema_200|#00FF00"
            
        Returns:
            List of tuples: [(indicator_type, period, color), ...]
            
        Raises:
            ValueError: If parsing fails or validation errors occur
        """
        if not indicators_str or not indicators_str.strip():
            return []
        
        indicators = []
        
        # Split by comma and process each indicator
        for indicator_spec in indicators_str.split(','):
            indicator_spec = indicator_spec.strip()
            if not indicator_spec:
                continue
                
            try:
                indicator_type, period, color = self._parse_single_indicator(indicator_spec)
                indicators.append((indicator_type, period, color))
                
            except ValueError as e:
                self.logger.error(f"Failed to parse indicator '{indicator_spec}': {e}")
                raise ValueError(f"Invalid indicator specification '{indicator_spec}': {e}")
        
        if not indicators:
            raise ValueError("No valid indicators found in specification")
        
        self.logger.info(f"Parsed {len(indicators)} indicators: {indicators}")
        return indicators
    
    def _parse_single_indicator(self, spec: str) -> Tuple[str, int, str]:
        """
        Parse a single indicator specification.
        
        Args:
            spec: String like "ema_50|red" or "ema_200|#00FF00"
            
        Returns:
            Tuple of (indicator_type, period, normalized_color)
            
        Raises:
            ValueError: If parsing or validation fails
        """
        # Split by pipe character
        if '|' not in spec:
            raise ValueError("Missing color specification (use format: indicator_period|color)")
        
        parts = spec.split('|')
        if len(parts) != 2:
            raise ValueError("Invalid format (use: indicator_period|color)")
        
        indicator_part, color_part = parts[0].strip(), parts[1].strip()
        
        # Parse indicator type and period
        indicator_type, period = self._parse_indicator_and_period(indicator_part)
        
        # Validate and normalize color
        normalized_color = self._validate_and_normalize_color(color_part)
        
        return indicator_type, period, normalized_color
    
    def _parse_indicator_and_period(self, indicator_part: str) -> Tuple[str, int]:
        """
        Parse indicator type and period from string like "ema_50".
        
        Args:
            indicator_part: String like "ema_50"
            
        Returns:
            Tuple of (indicator_type, period)
            
        Raises:
            ValueError: If parsing or validation fails
        """
        if '_' not in indicator_part:
            raise ValueError("Missing period specification (use format: indicator_period)")
        
        parts = indicator_part.split('_')
        if len(parts) != 2:
            raise ValueError("Invalid indicator format (use: indicator_period)")
        
        indicator_type, period_str = parts[0].lower().strip(), parts[1].strip()
        
        # Validate indicator type
        if indicator_type not in self.supported_indicators:
            raise ValueError(f"Unsupported indicator '{indicator_type}'. Supported: {list(self.supported_indicators)}")
        
        # Parse and validate period
        try:
            period = int(period_str)
        except ValueError:
            raise ValueError(f"Invalid period '{period_str}'. Period must be a positive integer.")
        
        if period <= 0:
            raise ValueError(f"Period must be positive, got {period}")
        
        if period > 1000:  # Reasonable upper limit
            raise ValueError(f"Period {period} is too large (maximum: 1000)")
        
        return indicator_type, period
    
    def _validate_and_normalize_color(self, color: str) -> str:
        """
        Validate and normalize color specification.
        
        Args:
            color: Color string (named color or hex code)
            
        Returns:
            Normalized hex color code (e.g., "#FF0000")
            
        Raises:
            ValueError: If color is invalid
        """
        color = color.strip().lower()
        
        # Check if it's a named color
        if color in self.named_colors:
            return self.named_colors[color]
        
        # Check if it's a hex color code
        if color.startswith('#'):
            hex_color = color.upper()
            
            # Validate hex format
            if not re.match(r'^#[0-9A-F]{6}$', hex_color):
                raise ValueError(f"Invalid hex color '{color}'. Use format #RRGGBB")
            
            return hex_color
        
        # Try without # prefix
        if re.match(r'^[0-9A-Fa-f]{6}$', color):
            return f"#{color.upper()}"
        
        # Invalid color
        available_colors = list(self.named_colors.keys())
        raise ValueError(f"Invalid color '{color}'. Use named colors ({available_colors}) or hex codes (#RRGGBB)")
    
    def validate_periods_against_data(self, indicators: List[Tuple[str, int, str]], 
                                    data_length: int) -> List[Tuple[str, int, str]]:
        """
        Validate that indicator periods don't exceed available data length.
        
        Args:
            indicators: List of parsed indicators
            data_length: Number of available data points
            
        Returns:
            List of valid indicators (may be filtered)
            
        Raises:
            ValueError: If no indicators remain valid
        """
        if data_length <= 0:
            raise ValueError("No data available for indicator calculations")
        
        valid_indicators = []
        
        for indicator_type, period, color in indicators:
            if period <= data_length:
                valid_indicators.append((indicator_type, period, color))
                self.logger.info(f"Indicator {indicator_type}_{period} is valid (period <= {data_length})")
            else:
                self.logger.warning(f"Skipping {indicator_type}_{period}: period {period} > available data {data_length}")
        
        if not valid_indicators:
            raise ValueError(f"No indicators have valid periods for {data_length} data points")
        
        return valid_indicators
