"""
Metrics Tracking System
Tracks and analyzes conversation metrics for performance monitoring
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class MetricsTracker:
    """Tracks and stores conversation metrics"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize metrics tracker
        
        Args:
            log_dir: Directory to store metrics logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.metrics_file = self.log_dir / "metrics.jsonl"
        self.daily_stats_file = self.log_dir / "daily_stats.json"
    
    def log_conversation_metrics(self, session_id: str, metrics: Dict):
        """
        Log metrics for a conversation
        
        Args:
            session_id: Unique session identifier
            metrics: Dictionary of metrics
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'metrics': metrics
        }
        
        # Append to JSONL file
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_interaction(self, session_id: str, event_type: str, data: Dict):
        """
        Log individual interaction event
        
        Args:
            session_id: Session identifier
            event_type: Type of event (e.g., 'message_sent', 'intent_recognized')
            data: Event data
        """
        event_log = self.log_dir / f"session_{session_id}.jsonl"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        
        with open(event_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_daily_statistics(self) -> Dict:
        """
        Calculate daily statistics from logged metrics
        
        Returns:
            Dictionary with aggregated statistics
        """
        if not self.metrics_file.exists():
            return self._empty_stats()
        
        today = datetime.now().date()
        
        conversations = []
        total_turns = 0
        intent_recognized_count = 0
        entity_extraction_counts = []
        completion_rates = []
        avg_duration = []
        error_counts = []
        
        with open(self.metrics_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_date = datetime.fromisoformat(entry['timestamp']).date()
                    
                    if entry_date == today:
                        conversations.append(entry)
                        metrics = entry['metrics']
                        
                        total_turns += metrics.get('turn_count', 0)
                        if metrics.get('intent_recognized'):
                            intent_recognized_count += 1
                        entity_extraction_counts.append(metrics.get('entity_extraction_count', 0))
                        completion_rates.append(metrics.get('data_completeness', 0))
                        avg_duration.append(metrics.get('conversation_duration_seconds', 0))
                        error_counts.append(metrics.get('error_count', 0))
                except Exception as e:
                    print(f"Error parsing log entry: {e}")
                    continue
        
        if not conversations:
            return self._empty_stats()
        
        stats = {
            'date': today.isoformat(),
            'total_conversations': len(conversations),
            'total_turns': total_turns,
            'avg_turns_per_conversation': round(total_turns / len(conversations), 2),
            'intent_recognition_rate': round(intent_recognized_count / len(conversations) * 100, 2),
            'avg_entities_extracted': round(sum(entity_extraction_counts) / len(entity_extraction_counts), 2),
            'avg_completion_rate': round(sum(completion_rates) / len(completion_rates), 2),
            'avg_conversation_duration_seconds': round(sum(avg_duration) / len(avg_duration), 2),
            'total_errors': sum(error_counts),
            'error_rate': round(sum(error_counts) / len(conversations), 2),
            'generated_at': datetime.now().isoformat()
        }
        
        # Save daily stats
        self._save_daily_stats(stats)
        
        return stats
    
    def _empty_stats(self) -> Dict:
        """Return empty statistics structure"""
        return {
            'date': datetime.now().date().isoformat(),
            'total_conversations': 0,
            'total_turns': 0,
            'avg_turns_per_conversation': 0,
            'intent_recognition_rate': 0,
            'avg_entities_extracted': 0,
            'avg_completion_rate': 0,
            'avg_conversation_duration_seconds': 0,
            'total_errors': 0,
            'error_rate': 0,
            'generated_at': datetime.now().isoformat()
        }
    
    def _save_daily_stats(self, stats: Dict):
        """Save daily statistics to file"""
        if self.daily_stats_file.exists():
            with open(self.daily_stats_file, 'r') as f:
                all_stats = json.load(f)
        else:
            all_stats = []
        
        # Update or append today's stats
        today = stats['date']
        found = False
        for i, stat in enumerate(all_stats):
            if stat['date'] == today:
                all_stats[i] = stats
                found = True
                break
        
        if not found:
            all_stats.append(stats)
        
        with open(self.daily_stats_file, 'w') as f:
            json.dump(all_stats, f, indent=2)
    
    def get_historical_stats(self, days: int = 7) -> List[Dict]:
        """
        Get historical statistics for specified number of days
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of daily statistics
        """
        if not self.daily_stats_file.exists():
            return []
        
        with open(self.daily_stats_file, 'r') as f:
            all_stats = json.load(f)
        
        # Return last N days
        return all_stats[-days:] if len(all_stats) > days else all_stats
    
    def generate_report(self) -> str:
        """
        Generate a text report of current metrics
        
        Returns:
            Formatted text report
        """
        stats = self.get_daily_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           LOAN APPROVAL CHATBOT - DAILY METRICS             ║
╚══════════════════════════════════════════════════════════════╝

Date: {stats['date']}
Generated: {stats['generated_at']}

CONVERSATION METRICS
─────────────────────────────────────────────────────────────
Total Conversations:        {stats['total_conversations']}
Total Turns:                {stats['total_turns']}
Avg Turns per Session:      {stats['avg_turns_per_conversation']}
Avg Duration:               {stats['avg_conversation_duration_seconds']:.1f}s

PERFORMANCE METRICS
─────────────────────────────────────────────────────────────
Intent Recognition Rate:    {stats['intent_recognition_rate']}%
Avg Entities Extracted:     {stats['avg_entities_extracted']}
Avg Completion Rate:        {stats['avg_completion_rate']}%

ERROR METRICS
─────────────────────────────────────────────────────────────
Total Errors:               {stats['total_errors']}
Error Rate:                 {stats['error_rate']} errors/conversation

"""
        return report


# Test the metrics tracker
if __name__ == "__main__":
    tracker = MetricsTracker()
    
    # Simulate logging some metrics
    test_metrics = {
        'conversation_duration_seconds': 180,
        'turn_count': 8,
        'intent_recognized': True,
        'entities_extracted': ['income', 'debt', 'loan_amount'],
        'entity_extraction_count': 3,
        'data_completeness': 60.0,
        'error_count': 0
    }
    
    tracker.log_conversation_metrics('test-session-123', test_metrics)
    
    # Generate report
    print(tracker.generate_report())
    
    # Get historical stats
    historical = tracker.get_historical_stats(7)
    print(f"\nHistorical data points: {len(historical)}")
