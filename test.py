import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from jira_mock_config import Config, setup_logger

# Import the BAJiraHelper class from your original script
# You may need to adjust the import path based on your file structure
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from BAJiraHelper import BAJiraHelper

def main():
    # Setup logger and config
    logger = setup_logger()
    config = Config()
    
    logger.info("Starting Jira Mock API Test")
    
    # Create an instance of BAJiraHelper
    jira_helper = BAJiraHelper(config, logger)
    
    # Test getting issues created after a date (90 days ago)
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    logger.info(f"Getting issues created after {start_date}")
    
    try:
        issues_df = jira_helper.getIssuesCreatedAfterDF(start_date)
        logger.info(f"Retrieved {len(issues_df)} issues")
        logger.info(f"Sample issues:\n{issues_df.head()}")
        
        # Test getting watchers
        if not issues_df.empty:
            logger.info("Getting watchers for the first 5 issues")
            watchers_df = jira_helper.getWatchersDF(issues_df.head(5))
            logger.info(f"Retrieved {len(watchers_df)} watchers")
            logger.info(f"Sample watchers:\n{watchers_df.head()}")
        
        # Test getting issue history
        logger.info("Getting issue history")
        history_df = jira_helper.getAllIssueHistoryDF(start_date)
        logger.info(f"Retrieved {len(history_df)} history records")
        logger.info(f"Sample history:\n{history_df.head()}")
        
        logger.info("All tests completed successfully")
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()