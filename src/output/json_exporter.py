"""
JSON output module for exporting stock data.

This module handles converting stock data to JSON format for external use.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import configparser

from ..data.data_models import StockDataset, OHLCVData


class JSONExporter:
    """
    Exports stock data to JSON format with metadata.
    
    Provides structured JSON output with data points, metadata,
    and configuration information.
    """
    
    def __init__(self, config_path: str = "settings.ini"):
        """
        Initialize the JSON exporter with configuration.
        
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
    
    def export_to_json(self, dataset: StockDataset, 
                      output_path: str,
                      exchange_code: str = "",
                      days: int = 1,
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Export stock dataset to JSON file.
        
        Args:
            dataset: StockDataset containing OHLCV data
            output_path: Path where JSON file should be saved
            exchange_code: Exchange code for metadata
            days: Number of days included in the data
            metadata: Additional metadata to include
        """
        if not dataset:
            raise ValueError("Dataset is empty, cannot export to JSON")
        
        # Prepare the JSON structure
        json_data = self._create_json_structure(dataset, exchange_code, days, metadata)
        
        # Write to file
        output_file = Path(output_path)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, default=self._json_serializer)
            
            self.logger.info(f"Successfully exported {len(dataset)} data points to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to write JSON file {output_path}: {e}")
            raise
    
    def _create_json_structure(self, dataset: StockDataset, 
                              exchange_code: str,
                              days: int,
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create the JSON data structure.
        
        Args:
            dataset: StockDataset containing OHLCV data
            exchange_code: Exchange code for metadata
            days: Number of days included in the data
            metadata: Additional metadata to include
            
        Returns:
            Dictionary representing the JSON structure
        """
        # Get time range information
        first_timestamp = dataset.data[0].timestamp if dataset.data else None
        last_timestamp = dataset.data[-1].timestamp if dataset.data else None
        
        # Create metadata section
        export_metadata = {
            "export_timestamp": datetime.now().replace(microsecond=0).isoformat(),
            "exchange_code": exchange_code,
            "days_requested": days,
            "data_points_count": len(dataset),
            "time_range": {
                "start": (first_timestamp.replace(tzinfo=None) if first_timestamp.tzinfo else first_timestamp).isoformat() if first_timestamp else None,
                "end": (last_timestamp.replace(tzinfo=None) if last_timestamp.tzinfo else last_timestamp).isoformat() if last_timestamp else None
            },
            "data_format": "OHLCV",
            "timezone_info": "Local time (timezone information removed for cleaner output)"
        }
        
        # Add any additional metadata
        if metadata:
            export_metadata.update(metadata)
        
        # Convert data points to JSON format
        data_points = []
        for point in dataset.data:
            # Remove timezone info from timestamp for cleaner JSON output
            naive_timestamp = point.timestamp.replace(tzinfo=None) if point.timestamp.tzinfo else point.timestamp
            data_points.append({
                "timestamp": naive_timestamp.isoformat(),
                "open": point.open,
                "high": point.high,
                "low": point.low,
                "close": point.close,
                "volume": point.volume
            })
        
        # Create the complete JSON structure
        json_structure = {
            "metadata": export_metadata,
            "data": data_points
        }
        
        return json_structure
    
    def _json_serializer(self, obj: Any) -> str:
        """
        Custom JSON serializer for datetime objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serialized string representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def get_json_string(self, dataset: StockDataset,
                       exchange_code: str = "",
                       days: int = 1,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Get JSON representation as string without writing to file.
        
        Args:
            dataset: StockDataset containing OHLCV data
            exchange_code: Exchange code for metadata
            days: Number of days included in the data
            metadata: Additional metadata to include
            
        Returns:
            JSON string representation of the data
        """
        if not dataset:
            raise ValueError("Dataset is empty, cannot convert to JSON")
        
        json_data = self._create_json_structure(dataset, exchange_code, days, metadata)
        return json.dumps(json_data, indent=2, default=self._json_serializer)
    
    def validate_output_path(self, output_path: str) -> bool:
        """
        Validate that the output path is suitable for JSON export.
        
        Args:
            output_path: Path to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        try:
            output_file = Path(output_path)
            
            # Check if directory exists or can be created
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if we can write to the location
            if output_file.exists():
                if not output_file.is_file():
                    self.logger.error(f"Output path exists but is not a file: {output_path}")
                    return False
                
                # Check if file is writable
                if not output_file.stat().st_mode & 0o200:  # Check write permission
                    self.logger.error(f"Output file is not writable: {output_path}")
                    return False
            
            # Suggest .json extension if not present
            if not output_path.lower().endswith('.json'):
                self.logger.warning(f"Output file does not have .json extension: {output_path}")
                self.logger.info("Consider using .json extension for clarity")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Invalid output path {output_path}: {e}")
            return False
