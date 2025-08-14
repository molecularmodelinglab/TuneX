"""
Data manager for handling runs data and persistence.
"""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import uuid4

from app.models.campaign import Campaign
from app.shared.constants import WorkspaceConstants

class RunsDataManager:
    """Manages runs data storage and retrieval."""

    RUNS_FOLDERNAME = "runs"
    
    def __init__(self, workspace_path: str, campaign_id: str):
        self.workspace_path = Path(workspace_path)
        self.campaign_id = campaign_id
        self.campaign_folder = self.workspace_path / WorkspaceConstants.CAMPAIGNS_DIRNAME / f"{self.campaign_id}"
        self.runs_file = self.campaign_folder / self.RUNS_FOLDERNAME / f"runs_{campaign_id}.json"

        self.runs_file.parent.mkdir(exist_ok=True)
    
    def load_runs(self) -> List[Dict[str, Any]]:
        """Load all runs for the campaign."""
        if not self.runs_file.exists():
            return []
        
        try:
            with open(self.runs_file, 'r', encoding='utf-8') as f:
                runs_data = json.load(f)
                
            # Convert date strings back to datetime objects
            for run in runs_data:
                if 'created_at' in run:
                    run['created_at'] = datetime.fromisoformat(run['created_at'])
                if 'updated_at' in run:
                    run['updated_at'] = datetime.fromisoformat(run['updated_at'])
                    
            return runs_data
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading runs data: {e}")
            return []
    
    def save_runs(self, runs_data: List[Dict[str, Any]]):
        """Save all runs data."""
        # Convert datetime objects to strings for JSON serialization
        serializable_runs = []
        for run in runs_data:
            run_copy = run.copy()
            if 'created_at' in run_copy and isinstance(run_copy['created_at'], datetime):
                run_copy['created_at'] = run_copy['created_at'].isoformat()
            if 'updated_at' in run_copy and isinstance(run_copy['updated_at'], datetime):
                run_copy['updated_at'] = run_copy['updated_at'].isoformat()
            serializable_runs.append(run_copy)
        
        try:
            with open(self.runs_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_runs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving runs data: {e}")
    
    def add_run(self, experiments: List[Dict[str, Any]], campaign: Campaign) -> int:
        """Add a new run and return its run number."""
        runs_data = self.load_runs()
        
        # Create new run
        run_number = len(runs_data) + 1
        new_run = {
            'run_id': str(uuid4()),
            'run_number': run_number,
            'campaign_id': self.campaign_id,
            'status': 'completed',
            'experiments': experiments,
            'targets': [{'name': target.name, 'mode': target.mode} for target in campaign.targets],
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'experiment_count': len(experiments),
            'completed_count': 0
        }
        
        runs_data.append(new_run)
        self.save_runs(runs_data)
        
        return run_number
    
    def update_run_experiments(self, run_number: int, experiments: List[Dict[str, Any]]):
        """Update experiments data for a specific run."""
        runs_data = self.load_runs()
        
        for run in runs_data:
            if run.get('run_number') == run_number:
                run['experiments'] = experiments
                run['updated_at'] = datetime.now()
                
                target_names = [t['name'] for t in run.get('targets', [])]
                completed_count = sum(1 for exp in experiments 
                                    if any(exp.get(target_name) is not None 
                                          for target_name in target_names))
                run['completed_count'] = completed_count
                
                break
        
        self.save_runs(runs_data)
    
    def get_run(self, run_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific run by number."""
        runs_data = self.load_runs()
        
        for run in runs_data:
            if run.get('run_number') == run_number:
                return run
        
        return None
    
    def delete_run(self, run_number: int):
        """Delete a specific run."""
        runs_data = self.load_runs()
        runs_data = [run for run in runs_data if run.get('run_number') != run_number]
        
        for i, run in enumerate(runs_data, 1):
            run['run_number'] = i
        
        self.save_runs(runs_data)
    
    def get_run_count(self) -> int:
        """Get the total number of runs."""
        return len(self.load_runs())
    
    def has_previous_data(self) -> bool:
        """Check if there are any completed runs with target data."""
        runs_data = self.load_runs()
        
        for run in runs_data:
            if run.get('completed_count', 0) > 0:
                return True
        
        return False
