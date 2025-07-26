"""
Horizontal lines argument parser for command line interface.

This module handles parsing and validation of the --lines parameter.
"""

import re
import random
import logging
from typing import List, Tuple, Set, Optional


class LineParser:
    """
    Parses and validates horizontal line specifications from command line arguments.
    
    Supports format: "label|value|color|width" with smart random color assignment.
    """
    
    def __init__(self):
        """Initialize the line parser."""
        self.logger = logging.getLogger(__name__)
        
        # Default color pool for random assignment
        self.default_colors = [
            '#FF0000',  # red
            '#00FF00',  # green  
            '#0000FF',  # blue
            '#FFA500',  # orange
            '#800080',  # purple
            '#00FFFF',  # cyan
            '#FF00FF',  # magenta
            '#FFFF00',  # yellow
            '#FF6B35',  # coral
            '#004E89',  # navy
            '#32CD32',  # lime green
            '#DC143C',  # crimson
        ]
        
        # Named color mappings (reuse from indicators)
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
    
    def parse_lines(self, lines_str: str) -> List[Tuple[str, float, str, int]]:
        """
        Parse lines string into structured data with smart color assignment.
        
        Args:
            lines_str: String like "Support|28.2|blue|2,Resistance|30.5"
            
        Returns:
            List of tuples: [(label, value, color, width), ...]
            
        Raises:
            ValueError: If parsing fails or validation errors occur
        """
        if not lines_str or not lines_str.strip():
            return []
        
        # First pass: parse all line specs and collect explicit colors
        raw_lines = []
        used_colors = set()
        
        for line_spec in lines_str.split(','):
            line_spec = line_spec.strip()
            if not line_spec:
                continue
                
            try:
                parsed_line = self._parse_single_line(line_spec)
                raw_lines.append(parsed_line)
                
                # If color was explicitly specified, track it
                if len(parsed_line) >= 3 and parsed_line[2] is not None:
                    normalized_color = self._validate_and_normalize_color(parsed_line[2])
                    used_colors.add(normalized_color)
                    
            except ValueError as e:
                self.logger.error(f"Failed to parse line '{line_spec}': {e}")
                raise ValueError(f"Invalid line specification '{line_spec}': {e}")
        
        if not raw_lines:
            raise ValueError("No valid lines found in specification")
        
        # Second pass: assign colors and finalize specifications
        final_lines = []
        
        for parsed_line in raw_lines:
            label, value, color, width = parsed_line
            
            # Assign random color if not specified
            if color is None:
                color = self._assign_random_color(used_colors)
                used_colors.add(color)
            else:
                color = self._validate_and_normalize_color(color)
            
            # Set default width if not specified
            if width is None:
                width = 1
            
            final_lines.append((label, value, color, width))
        
        self.logger.info(f"Parsed {len(final_lines)} horizontal lines: {final_lines}")
        return final_lines
    
    def _parse_single_line(self, spec: str) -> Tuple[str, float, Optional[str], Optional[int]]:
        """
        Parse a single line specification.
        
        Args:
            spec: String like "Support|28.2|blue|2" or "Support|28.2"
            
        Returns:
            Tuple of (label, value, color, width) with None for missing optional values
            
        Raises:
            ValueError: If parsing or validation fails
        """
        parts = spec.split('|')
        
        if len(parts) < 2:
            raise ValueError("Missing required fields (need at least: label|value)")
        
        if len(parts) > 4:
            raise ValueError("Too many fields (maximum: label|value|color|width)")
        
        # Parse required fields
        label = parts[0].strip()
        if not label:
            raise ValueError("Label cannot be empty")
        
        try:
            value = float(parts[1].strip())
        except ValueError:
            raise ValueError(f"Invalid value '{parts[1]}'. Value must be a number.")
        
        # Parse optional fields
        color = None
        width = None
        
        if len(parts) >= 3 and parts[2].strip():
            color = parts[2].strip()
        
        if len(parts) >= 4 and parts[3].strip():
            try:
                width = int(parts[3].strip())
                if width <= 0:
                    raise ValueError(f"Width must be positive, got {width}")
            except ValueError as e:
                if "invalid literal" in str(e).lower():
                    raise ValueError(f"Invalid width '{parts[3]}'. Width must be a positive integer.")
                raise
        
        return label, value, color, width
    
    def _assign_random_color(self, used_colors: Set[str]) -> str:
        """
        Assign a random color, preferring unused colors.
        
        Args:
            used_colors: Set of already used color codes
            
        Returns:
            Hex color code
        """
        # Get unused colors from the pool
        unused_colors = [c for c in self.default_colors if c not in used_colors]
        
        # If unused colors available, pick random from unused
        if unused_colors:
            return random.choice(unused_colors)
        
        # If all colors used, pick any random color from full pool
        return random.choice(self.default_colors)
    
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
