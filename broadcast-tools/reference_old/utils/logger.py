import logging

def setup_logger(level=logging.INFO):
    """Set up the logger for the application"""
    logger = logging.getLogger('AutoCADExcelTool')
    
    # If logger already has handlers, don't add more
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handler
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger
