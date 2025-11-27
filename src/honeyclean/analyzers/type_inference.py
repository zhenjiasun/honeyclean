"""
Advanced data type inference with pattern recognition.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any

class DataTypeInference:
    """Advanced data type inference with pattern recognition."""
    
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$',
        'url': r'^https?://[^\s]+$',
        'ip_address': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
        'postal_code': r'^\d{5}(-\d{4})?$',
        'credit_card': r'^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$',
        'date_iso': r'^\d{4}-\d{2}-\d{2}$',
        'datetime_iso': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        'currency': r'^\$?[\d,]+\.?\d*$',
        'datetime_global': (
            r'^(?:'
                # YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
                r'(?:\d{4}[-/.]\d{2}[-/.]\d{2})'
                # DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
                r'|(?:\d{2}[-/.]\d{2}[-/.]\d{4})'
                # MM-DD-YYYY, MM/DD/YYYY, MM.DD.YYYY
                r'|(?:\d{2}[-/.]\d{2}[-/.]\d{4})'
            r')'
            # Optional time part
            r'(?:[T\s]\d{1,2}:\d{2}'
                r'(?:\:\d{2}(?:\.\d{1,6})?)?'   # Optional seconds + fractional
                r'(?:\s?(?:AM|PM|am|pm))?'      # Optional AM/PM
                r'(?:Z|[+-]\d{2}:?\d{2})?'      # Optional timezone
            r')?$'
        )
    }
    
    @classmethod
    def infer_column_type(cls, series: pd.Series) -> Dict[str, Any]:
        """Infer detailed column type with confidence scores."""
        sample_size = min(1000, len(series.dropna()))
        sample = series.dropna().head(sample_size).astype(str)
        
        # Basic pandas inference
        pandas_type = pd.api.types.infer_dtype(series, skipna=True)
        
        # Pattern matching
        pattern_scores = {}
        for pattern_name, pattern in cls.PATTERNS.items():
            matches = sample.str.match(pattern, na=False).sum()
            pattern_scores[pattern_name] = matches / len(sample) if len(sample) > 0 else 0
        
        # Best pattern match
        best_pattern = max(pattern_scores, key=pattern_scores.get)
        best_pattern_score = pattern_scores[best_pattern]
        
        # Determine suggested type
        suggested_type = cls._determine_suggested_type(pandas_type, best_pattern, best_pattern_score)
        
        return {
            'pandas_inferred': pandas_type,
            'best_pattern': best_pattern,
            'pattern_confidence': best_pattern_score,
            'suggested_type': suggested_type,
            'pattern_scores': pattern_scores,
            'sample_values': sample.head(5).tolist()
        }
    
    @classmethod
    def _determine_suggested_type(cls, pandas_type: str, best_pattern: str, confidence: float) -> str:
        """Determine the suggested data type based on inference results."""
        if confidence > 0.8:
            return best_pattern
        elif pandas_type in ['integer', 'floating']:
            return 'numeric'
        elif pandas_type == 'datetime64':
            return 'datetime'
        elif pandas_type == 'boolean':
            return 'boolean'
        elif pandas_type == 'categorical':
            return 'categorical'
        else:
            return 'text'