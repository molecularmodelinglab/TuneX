"""
BayBe integration service for experiment generation and optimization.
"""

import csv
import logging
import os
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.models.campaign import Campaign
from app.models.parameters.base import BaseParameter
from app.shared.constants import WorkspaceConstants


class BayBeIntegrationService:
    """Service for integrating with BayBe optimization library."""
    
    LOG_FOLDERNAME = "logs"
    RUNS_FOLDERNAME = "runs"
    LOG_FILENAME = "bayesian_generation.log"
    
    def __init__(self, campaign: Campaign, workspace_path: str):
        self.campaign = campaign
        self.workspace_path = workspace_path
        self.campaign_folder = Path(workspace_path) / WorkspaceConstants.CAMPAIGNS_DIRNAME / f"{self.campaign.id}"
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for BayBe operations."""
        logger = logging.getLogger("baybe_integration")
        logger.setLevel(logging.INFO)

        logs_dir = self.campaign_folder / self.LOG_FOLDERNAME
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / self.LOG_FILENAME
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def generate_experiments(self, num_experiments: int, 
                           has_previous_data: bool = False) -> List[Dict[str, Any]]:
        """
        Generate experiments using BayBe.
        
        For now, this is a mock implementation that generates random experiments.
        This should be replaced with actual BayBe integration.
        """
        self.logger.info(f"Starting generation of {num_experiments} experiments")
        self.logger.info(f"Campaign: {self.campaign.name}")
        self.logger.info(f"Parameters: {len(self.campaign.parameters)}")
        self.logger.info(f"Has previous data: {has_previous_data}")
        
        experiments = []
        
        try:
            for i in range(num_experiments):
                experiment = {}
                
                # Generate values for each parameter
                for param in self.campaign.parameters:
                    experiment[param.name] = self._generate_parameter_value(param)
                
                experiments.append(experiment)
                
                # Log progress
                if (i + 1) % 10 == 0 or i == 0:
                    self.logger.info(f"Generated {i + 1}/{num_experiments} experiments")
            
            self.logger.info(f"Successfully generated {len(experiments)} experiments")
            
            # Save experiments to CSV
            self._save_experiments_csv(experiments)
            
            return experiments
            
        except Exception as e:
            self.logger.error(f"Error generating experiments: {str(e)}")
            raise
    
    def _generate_parameter_value(self, parameter: BaseParameter) -> Any:
        """
        Generate a random value for a parameter.
        This is a mock implementation - replace with BayBe logic.
        """
        param_type = getattr(parameter, 'type', 'numerical')
        
        if param_type == 'numerical':
            min_val = getattr(parameter, 'min_value', 0.0)
            max_val = getattr(parameter, 'max_value', 100.0)
            return round(random.uniform(min_val, max_val), 3)
            
        elif param_type == 'categorical':
            categories = getattr(parameter, 'categories', ['A', 'B', 'C'])
            return random.choice(categories)
            
        elif param_type == 'integer':
            min_val = int(getattr(parameter, 'min_value', 1))
            max_val = int(getattr(parameter, 'max_value', 100))
            return random.randint(min_val, max_val)
        
        else:
            return random.uniform(0, 100)
    
    def _save_experiments_csv(self, experiments: List[Dict[str, Any]]):
        """Save experiments to a CSV file."""
        if not experiments:
            return

        runs_dir = self.campaign_folder / self.RUNS_FOLDERNAME
        runs_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = runs_dir / f"experiments_{timestamp}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if experiments:
                writer = csv.DictWriter(f, fieldnames=experiments[0].keys())
                writer.writeheader()
                writer.writerows(experiments)
        
        self.logger.info(f"Experiments saved to: {csv_file}")
    
    def get_log_file_path(self) -> Path:
        """Get the path to the BayBe log file."""
        return self.campaign_folder / self.LOG_FOLDERNAME / self.LOG_FILENAME

    def get_last_log_update_time(self) -> Optional[datetime]:
        """Get the last modification time of the log file."""
        log_file = self.get_log_file_path()
        if log_file.exists():
            timestamp = log_file.stat().st_mtime
            return datetime.fromtimestamp(timestamp)
        return None


class MockBayBeService(BayBeIntegrationService):
    """
    Mock BayBe service for development and testing.
    Simulates the behavior of BayBe with realistic delays.
    """

    def generate_experiments(self, num_experiments: int,
                              has_previous_data: bool = False) -> List[Dict[str, Any]]:
        """
        Generate mock experiments with simulated processing time.
        """
        import time
        
        self.logger.info("Using Mock BayBe Service for development")
        
        # Simulate processing time (faster for first run, slower for subsequent)
        if not has_previous_data:
            # First run is quick (random generation)
            time.sleep(1)
        else:
            # Subsequent runs take longer (optimization)
            time.sleep(2 + (num_experiments * 0.1))  # Scale with number of experiments
        
        return super().generate_experiments(num_experiments, has_previous_data)
