import logging
from pathlib import Path
from typing import Dict, Any

import pandas as pd

class ExcelManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def export_data(self, data: Dict[str, Any], file_path: str):
        """Export data to Excel file"""
        try:
            self.logger.info(f"Exporting data to: {file_path}")
            
            # Convert data to DataFrame
            df = pd.DataFrame.from_dict(data, orient='index')
            
            # Export to Excel
            df.to_excel(file_path, index=False)
            
            self.logger.info("Export completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}", exc_info=True)
            raise
