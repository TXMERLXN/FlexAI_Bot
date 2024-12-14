import json
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger
import kaggle
from typing import Dict, Optional

class KaggleManager:
    def __init__(self, accounts_file: str = "kaggle_accounts.json"):
        self.accounts_file = Path(accounts_file)
        self.accounts = self._load_accounts()
        self.current_account = None
        self.last_switch_time = None

    def _load_accounts(self) -> Dict:
        """Load Kaggle accounts from JSON file"""
        if not self.accounts_file.exists():
            logger.warning(f"Accounts file {self.accounts_file} not found. Creating empty file.")
            self._save_accounts({})
            return {}
        
        try:
            with open(self.accounts_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error reading {self.accounts_file}. Creating new empty file.")
            self._save_accounts({})
            return {}

    def _save_accounts(self, accounts: Dict):
        """Save accounts to JSON file"""
        with open(self.accounts_file, 'w') as f:
            json.dump(accounts, f, indent=4)

    def add_account(self, username: str, api_key: str):
        """Add a new Kaggle account"""
        self.accounts[username] = {
            "api_key": api_key,
            "last_used": None,
            "usage_count": 0
        }
        self._save_accounts(self.accounts)
        logger.info(f"Added new account: {username}")

    def get_next_available_account(self) -> Optional[str]:
        """Get the next available account based on usage time"""
        current_time = datetime.now()
        
        # Find account with oldest last_used time or None
        available_account = None
        oldest_time = current_time
        
        for username, data in self.accounts.items():
            last_used = data.get("last_used")
            if last_used is None:
                return username
            
            last_used_time = datetime.fromisoformat(last_used)
            if last_used_time + timedelta(hours=12) < current_time:
                if last_used_time < oldest_time:
                    oldest_time = last_used_time
                    available_account = username
        
        return available_account

    def switch_account(self) -> bool:
        """Switch to the next available Kaggle account"""
        next_account = self.get_next_available_account()
        if not next_account:
            logger.error("No available Kaggle accounts!")
            return False

        try:
            # Update Kaggle API credentials
            kaggle.api.authenticate()
            
            # Update account usage information
            self.accounts[next_account]["last_used"] = datetime.now().isoformat()
            self.accounts[next_account]["usage_count"] += 1
            self._save_accounts(self.accounts)
            
            self.current_account = next_account
            self.last_switch_time = datetime.now()
            
            logger.info(f"Switched to account: {next_account}")
            return True
            
        except Exception as e:
            logger.error(f"Error switching to account {next_account}: {e}")
            return False

    def check_current_account(self) -> bool:
        """Check if current account needs to be switched"""
        if not self.current_account or not self.last_switch_time:
            return False
            
        time_since_switch = datetime.now() - self.last_switch_time
        return time_since_switch.total_seconds() < 12 * 3600  # 12 hours in seconds

    def get_account_status(self) -> Dict:
        """Get status of all accounts"""
        return {
            "total_accounts": len(self.accounts),
            "current_account": self.current_account,
            "accounts_status": self.accounts
        }
