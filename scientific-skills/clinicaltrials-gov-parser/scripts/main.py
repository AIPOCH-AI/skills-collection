#!/usr/bin/env python3
"""
ClinicalTrials.gov Parser
Monitor and summarize competitor clinical trial status changes.

Technical: ClinicalTrials.gov API v2 integration, trial monitoring, status tracking
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import requests
import time


@dataclass
class TrialStatus:
    """Represents a trial's status information."""
    nct_id: str
    title: str
    status: str
    phase: Optional[str]
    sponsor: Optional[str]
    condition: Optional[str]
    last_update: Optional[str]
    enrollment_count: Optional[int]
    start_date: Optional[str]
    completion_date: Optional[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ClinicalTrialsMonitor:
    """
    Monitor and track clinical trial status changes from ClinicalTrials.gov.
    
    API: ClinicalTrials.gov API v2
    Rate Limit: 10 requests/second
    """
    
    BASE_URL = "https://clinicaltrials.gov/api/v2"
    RATE_LIMIT_DELAY = 0.15  # seconds between requests (10 req/sec max)
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "ClinicalTrials-Parser/1.0"
        })
        self._last_request_time = 0
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make rate-limited API request."""
        # Rate limiting
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        self._last_request_time = time.time()
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            raise Exception("API rate limit exceeded. Please wait and try again.")
        else:
            raise Exception(f"API error {response.status_code}: {response.text}")
    
    def search_trials(
        self,
        sponsor: Optional[str] = None,
        condition: Optional[str] = None,
        status: Optional[str] = None,
        phase: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 100
    ) -> List[TrialStatus]:
        """
        Search for clinical trials with filters.
        
        Args:
            sponsor: Sponsor/Collaborator name
            condition: Medical condition
            status: Trial status (RECRUITING, ACTIVE_NOT_RECRUITING, etc.)
            phase: Trial phase (EARLY_PHASE1, PHASE1, PHASE2, etc.)
            keyword: Search keyword
            limit: Maximum results (1-1000)
        
        Returns:
            List of TrialStatus objects
        """
        params = {"pageSize": min(limit, 1000)}
        
        # Build query.term for combined search
        query_parts = []
        if sponsor:
            query_parts.append(f'"{sponsor}"')
        if condition:
            query_parts.append(condition)
        if keyword:
            query_parts.append(keyword)
        
        if query_parts:
            params["query.term"] = " ".join(query_parts)
        
        # Use filter.advanced for status and phase
        filters = []
        if status:
            filters.append(f"area:STATUS status:{status}")
        if phase:
            filters.append(f"area:PHASE phase:{phase}")
        
        if filters:
            params["filter.advanced"] = " AND ".join(filters)
        
        data = self._make_request("studies", params)
        
        trials = []
        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            design_module = protocol.get("designModule", {})
            
            trial = TrialStatus(
                nct_id=identification.get("nctId", ""),
                title=identification.get("briefTitle", ""),
                status=status_module.get("overallStatus", "UNKNOWN"),
                phase=self._get_phase(protocol),
                sponsor=sponsor_module.get("leadSponsor", {}).get("name"),
                condition=self._get_first_condition(conditions_module),
                last_update=status_module.get("statusVerifiedDate"),
                enrollment_count=design_module.get("enrollmentInfo", {}).get("count"),
                start_date=status_module.get("startDateStruct", {}).get("date"),
                completion_date=status_module.get("completionDateStruct", {}).get("date")
            )
            trials.append(trial)
        
        return trials
    
    def get_trial(self, nct_id: str) -> Optional[TrialStatus]:
        """
        Get detailed information for a specific trial.
        
        Args:
            nct_id: ClinicalTrials.gov identifier (e.g., NCT05108922)
        
        Returns:
            TrialStatus object or None if not found
        """
        try:
            data = self._make_request(f"studies/{nct_id}")
            protocol = data.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            design_module = protocol.get("designModule", {})
            
            return TrialStatus(
                nct_id=identification.get("nctId", nct_id),
                title=identification.get("briefTitle", ""),
                status=status_module.get("overallStatus", "UNKNOWN"),
                phase=self._get_phase(protocol),
                sponsor=sponsor_module.get("leadSponsor", {}).get("name"),
                condition=self._get_first_condition(conditions_module),
                last_update=status_module.get("statusVerifiedDate"),
                enrollment_count=design_module.get("enrollmentInfo", {}).get("count"),
                start_date=status_module.get("startDateStruct", {}).get("date"),
                completion_date=status_module.get("completionDateStruct", {}).get("date")
            )
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                return None
            raise
    
    def check_status_changes(
        self,
        trial_ids: List[str],
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Check for status changes in monitored trials.
        
        Args:
            trial_ids: List of NCT IDs to check
            since: Check for changes since this date (default: 30 days ago)
        
        Returns:
            List of trials with their current status
        """
        if since is None:
            since = datetime.now() - timedelta(days=30)
        
        changes = []
        for nct_id in trial_ids:
            trial = self.get_trial(nct_id)
            if trial:
                trial_dict = trial.to_dict()
                trial_dict["monitored_since"] = since.isoformat()
                changes.append(trial_dict)
            time.sleep(self.RATE_LIMIT_DELAY)
        
        return changes
    
    def get_recruitment_status(self, nct_id: str) -> Optional[Dict]:
        """
        Get detailed recruitment/enrollment status.
        
        Args:
            nct_id: ClinicalTrials.gov identifier
        
        Returns:
            Dictionary with recruitment details
        """
        trial = self.get_trial(nct_id)
        if not trial:
            return None
        
        return {
            "nct_id": trial.nct_id,
            "title": trial.title,
            "status": trial.status,
            "enrollment_count": trial.enrollment_count,
            "last_update": trial.last_update
        }
    
    def generate_summary(
        self,
        sponsor: Optional[str] = None,
        condition: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Generate a summary report of trial activities.
        
        Args:
            sponsor: Filter by sponsor
            condition: Filter by condition
            days: Number of days to look back
        
        Returns:
            Summary dictionary with statistics
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        trials = self.search_trials(
            sponsor=sponsor,
            condition=condition,
            limit=1000
        )
        
        status_counts = {}
        phase_counts = {}
        recent_updates = []
        
        for trial in trials:
            # Count by status
            status_counts[trial.status] = status_counts.get(trial.status, 0) + 1
            
            # Count by phase
            if trial.phase:
                phase_counts[trial.phase] = phase_counts.get(trial.phase, 0) + 1
            
            # Check for recent updates
            if trial.last_update and trial.last_update >= since_date:
                recent_updates.append(trial.to_dict())
        
        return {
            "report_date": datetime.now().isoformat(),
            "period_days": days,
            "filters": {"sponsor": sponsor, "condition": condition},
            "total_trials": len(trials),
            "status_breakdown": status_counts,
            "phase_breakdown": phase_counts,
            "recent_updates": recent_updates,
            "recent_update_count": len(recent_updates)
        }
    
    def _get_phase(self, protocol: Dict) -> Optional[str]:
        """Extract phase information from protocol."""
        design = protocol.get("designModule", {})
        phases = design.get("phases", [])
        return phases[0] if phases else None
    
    def _get_first_condition(self, conditions_module: Dict) -> Optional[str]:
        """Get first condition from conditions module."""
        conditions = conditions_module.get("conditions", [])
        return conditions[0] if conditions else None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ClinicalTrials.gov Parser - Monitor trial status changes"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for trials")
    search_parser.add_argument("--sponsor", help="Sponsor name")
    search_parser.add_argument("--condition", help="Medical condition")
    search_parser.add_argument("--status", help="Trial status")
    search_parser.add_argument("--phase", help="Trial phase")
    search_parser.add_argument("--keyword", help="Search keyword")
    search_parser.add_argument("--limit", type=int, default=100, help="Result limit")
    search_parser.add_argument("--output", choices=["json", "table"], default="table")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get trial details")
    get_parser.add_argument("nct_id", help="ClinicalTrials.gov ID")
    get_parser.add_argument("--output", choices=["json", "table"], default="table")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor status changes")
    monitor_parser.add_argument(
        "--trials", 
        required=True, 
        help="Comma-separated NCT IDs"
    )
    monitor_parser.add_argument("--days", type=int, default=30, help="Days to look back")
    monitor_parser.add_argument("--output", choices=["json", "table"], default="table")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate summary report")
    report_parser.add_argument("--sponsor", help="Filter by sponsor")
    report_parser.add_argument("--condition", help="Filter by condition")
    report_parser.add_argument("--days", type=int, default=30, help="Report period")
    report_parser.add_argument("--output", choices=["json", "text"], default="text")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    monitor = ClinicalTrialsMonitor()
    
    try:
        if args.command == "search":
            trials = monitor.search_trials(
                sponsor=args.sponsor,
                condition=args.condition,
                status=args.status,
                phase=args.phase,
                keyword=args.keyword,
                limit=args.limit
            )
            if args.output == "json":
                print(json.dumps([t.to_dict() for t in trials], indent=2))
            else:
                print(f"\n{'NCT ID':<15} {'Status':<20} {'Phase':<12} {'Title'}")
                print("-" * 100)
                for trial in trials:
                    phase = trial.phase or "N/A"
                    print(f"{trial.nct_id:<15} {trial.status:<20} {phase:<12} {trial.title[:50]}...")
                print(f"\nTotal: {len(trials)} trials found")
        
        elif args.command == "get":
            trial = monitor.get_trial(args.nct_id)
            if trial:
                if args.output == "json":
                    print(json.dumps(trial.to_dict(), indent=2))
                else:
                    print(f"\n{'Field':<20} {'Value'}")
                    print("-" * 60)
                    for key, value in trial.to_dict().items():
                        print(f"{key:<20} {value or 'N/A'}")
            else:
                print(f"Trial {args.nct_id} not found")
                sys.exit(1)
        
        elif args.command == "monitor":
            trial_ids = [t.strip() for t in args.trials.split(",")]
            changes = monitor.check_status_changes(trial_ids)
            if args.output == "json":
                print(json.dumps(changes, indent=2))
            else:
                print(f"\n{'NCT ID':<15} {'Status':<20} {'Last Update':<15} {'Title'}")
                print("-" * 100)
                for change in changes:
                    print(f"{change['nct_id']:<15} {change['status']:<20} "
                          f"{change['last_update'] or 'N/A':<15} {change['title'][:40]}...")
                print(f"\nMonitored: {len(changes)} trials")
        
        elif args.command == "report":
            summary = monitor.generate_summary(
                sponsor=args.sponsor,
                condition=args.condition,
                days=args.days
            )
            if args.output == "json":
                print(json.dumps(summary, indent=2))
            else:
                print("\n" + "=" * 60)
                print("CLINICAL TRIALS SUMMARY REPORT")
                print("=" * 60)
                print(f"Report Date: {summary['report_date']}")
                print(f"Period: Last {summary['period_days']} days")
                if summary['filters']['sponsor']:
                    print(f"Sponsor: {summary['filters']['sponsor']}")
                if summary['filters']['condition']:
                    print(f"Condition: {summary['filters']['condition']}")
                print(f"\nTotal Trials: {summary['total_trials']}")
                print("\nStatus Breakdown:")
                for status, count in sorted(summary['status_breakdown'].items()):
                    print(f"  {status}: {count}")
                if summary['phase_breakdown']:
                    print("\nPhase Breakdown:")
                    for phase, count in sorted(summary['phase_breakdown'].items()):
                        print(f"  {phase}: {count}")
                print(f"\nRecent Updates ({summary['recent_update_count']} trials)")
                print("=" * 60)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
