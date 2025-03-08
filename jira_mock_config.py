import json
import os
import logging

class Config:
    def __init__(self, config_file=None):
        self.config = {}
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration for mock testing
            self.config = {
                "Jira.User": "test_user",
                "Jira.Token": "test_token",
                "Jira.Server": "http://localhost:5000",
                "Jira.URL": "http://localhost:5000/rest/api/2/search",
                "Jira.Project": "MOCK",
                "Jira.Team": "Toasted Snow",
                "Jira.Chunk": 50
            }
    
    def getParm(self, key):
        """Get a parameter from the configuration"""
        if key in self.config:
            return self.config[key]
        raise KeyError(f"Configuration parameter '{key}' not found")
    
    def getParmDefault(self, key, default):
        """Get a parameter with a default value if not found"""
        return self.config.get(key, default)
    
    def setParm(self, key, value):
        """Set a parameter in the configuration"""
        self.config[key] = value
        
    def save(self, filename):
        """Save the configuration to a file"""
        with open(filename, 'w') as f:
            json.dump(self.config, f, indent=4)

# Setup logging
def setup_logger():
    logger = logging.getLogger("JiraMockTest")
    logger.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(ch)
    
    return logger