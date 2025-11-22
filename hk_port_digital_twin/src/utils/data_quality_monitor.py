#!/usr/bin/env python3
"""
Comments for context:
This module provides comprehensive data quality monitoring and reporting capabilities
for the Hong Kong Port Digital Twin system. It extends the existing data validation
framework with enhanced metrics, alerting, historical tracking, and quality scoring.

The module focuses on:
1. Enhanced vessel data quality metrics including deduplication analysis
2. Quality score calculation and trending
3. Alerting system for quality threshold violations
4. Historical quality tracking and reporting
5. Integration with the existing validation framework

This builds upon the existing validate_data_quality() function in data_loader.py
and provides additional monitoring capabilities specifically for the enhanced
deduplication strategies implemented in the vessel data pipeline.
"""

import logging
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class QualityLevel(Enum):
    """Quality level enumeration for standardized quality assessment"""
    EXCELLENT = "excellent"
    GOOD = "good" 
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class QualityMetric:
    """Data class for individual quality metrics"""
    name: str
    value: float
    threshold: float
    status: QualityLevel
    timestamp: datetime
    description: str
    category: str

@dataclass
class QualityAlert:
    """Data class for quality alerts"""
    alert_id: str
    metric_name: str
    severity: QualityLevel
    message: str
    timestamp: datetime
    threshold_violated: float
    actual_value: float
    category: str

class DataQualityMonitor:
    """
    Comprehensive data quality monitoring system for vessel data and related datasets.
    
    This class provides enhanced monitoring capabilities including:
    - Quality score calculation and trending
    - Threshold-based alerting
    - Historical quality tracking
    - Deduplication metrics analysis
    - Cross-dataset quality validation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the data quality monitor.
        
        Args:
            config_path: Optional path to quality monitoring configuration file
        """
        self.config = self._load_config(config_path)
        self.quality_history = []
        self.active_alerts = []
        self.metrics_cache = {}
        
        # Quality thresholds (can be overridden by config)
        self.thresholds = {
            'data_completeness': {'excellent': 98.0, 'good': 95.0, 'fair': 90.0, 'poor': 80.0},
            'duplicate_rate': {'excellent': 1.0, 'good': 2.0, 'fair': 5.0, 'poor': 10.0},
            'deduplication_efficiency': {'excellent': 95.0, 'good': 90.0, 'fair': 85.0, 'poor': 75.0},
            'vessel_count_consistency': {'excellent': 98.0, 'good': 95.0, 'fair': 90.0, 'poor': 85.0},
            'parsing_success_rate': {'excellent': 99.0, 'good': 97.0, 'fair': 95.0, 'poor': 90.0},
            'data_freshness_hours': {'excellent': 1.0, 'good': 6.0, 'fair': 12.0, 'poor': 24.0}
        }
        
        logger.info("DataQualityMonitor initialized with comprehensive monitoring capabilities")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'enable_alerting': True,
            'alert_cooldown_minutes': 30,
            'history_retention_days': 30,
            'quality_report_frequency': 'hourly',
            'enable_historical_tracking': True
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
                    logger.info(f"Loaded quality monitoring config from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def analyze_vessel_data_quality(self, vessel_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive vessel data quality analysis including deduplication metrics.
        
        Args:
            vessel_data: DataFrame containing vessel data with deduplication metrics
            
        Returns:
            Dict containing detailed quality analysis
        """
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'basic_metrics': {},
                'deduplication_analysis': {},
                'quality_scores': {},
                'alerts': [],
                'recommendations': []
            }
            
            # Basic data quality metrics
            analysis['basic_metrics'] = self._analyze_basic_metrics(vessel_data)
            
            # Enhanced deduplication analysis
            analysis['deduplication_analysis'] = self._analyze_deduplication_metrics(vessel_data)
            
            # Calculate quality scores
            analysis['quality_scores'] = self._calculate_quality_scores(
                analysis['basic_metrics'], 
                analysis['deduplication_analysis']
            )
            
            # Generate alerts if thresholds are violated
            analysis['alerts'] = self._check_quality_thresholds(analysis)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            # Store in history for trending
            if self.config.get('enable_historical_tracking', True):
                self._store_quality_history(analysis)
            
            logger.info(f"Vessel data quality analysis completed. Overall score: {analysis['quality_scores'].get('overall_score', 'N/A')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in vessel data quality analysis: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def _analyze_basic_metrics(self, vessel_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze basic data quality metrics"""
        if vessel_data.empty:
            return {
                'records_count': 0,
                'data_completeness': 0.0,
                'unique_vessels': 0,
                'status': 'no_data'
            }
        
        # Calculate completeness
        total_cells = vessel_data.size
        missing_cells = vessel_data.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
        
        # Analyze key columns
        key_columns = ['vessel_name', 'call_sign', 'arrival_time', 'status']
        key_completeness = {}
        for col in key_columns:
            if col in vessel_data.columns:
                col_completeness = (1 - vessel_data[col].isnull().sum() / len(vessel_data)) * 100
                key_completeness[col] = col_completeness
        
        return {
            'records_count': len(vessel_data),
            'data_completeness': round(completeness, 2),
            'key_column_completeness': key_completeness,
            'unique_vessels': vessel_data['vessel_name'].nunique() if 'vessel_name' in vessel_data.columns else 0,
            'unique_call_signs': vessel_data['call_sign'].nunique() if 'call_sign' in vessel_data.columns else 0,
            'date_range': self._get_date_range(vessel_data),
            'status_distribution': self._get_status_distribution(vessel_data)
        }
    
    def _analyze_deduplication_metrics(self, vessel_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze deduplication-specific metrics from DataFrame attributes"""
        dedup_analysis = {
            'strategy_used': 'unknown',
            'duplicates_removed': 0,
            'duplicate_rate': 0.0,
            'deduplication_efficiency': 0.0,
            'original_count': len(vessel_data),
            'final_count': len(vessel_data),
            'time_window_analysis': {},
            'status_based_analysis': {}
        }
        
        try:
            # Extract deduplication metrics from DataFrame attributes
            if hasattr(vessel_data, 'attrs') and vessel_data.attrs:
                attrs = vessel_data.attrs
                
                # Basic deduplication metrics
                dedup_analysis['strategy_used'] = attrs.get('deduplication_strategy', 'unknown')
                dedup_analysis['duplicates_removed'] = attrs.get('duplicates_removed', 0)
                dedup_analysis['original_count'] = attrs.get('original_count', len(vessel_data))
                dedup_analysis['final_count'] = len(vessel_data)
                
                # Calculate rates
                if dedup_analysis['original_count'] > 0:
                    dedup_analysis['duplicate_rate'] = round(
                        (dedup_analysis['duplicates_removed'] / dedup_analysis['original_count']) * 100, 2
                    )
                    dedup_analysis['deduplication_efficiency'] = round(
                        ((dedup_analysis['original_count'] - dedup_analysis['duplicates_removed']) / dedup_analysis['original_count']) * 100, 2
                    )
                
                # Time window analysis (if available)
                if 'time_window_duplicates' in attrs:
                    dedup_analysis['time_window_analysis'] = attrs['time_window_duplicates']
                
                # Status-based analysis (if available)
                if 'status_conflicts_resolved' in attrs:
                    dedup_analysis['status_based_analysis'] = {
                        'conflicts_resolved': attrs['status_conflicts_resolved'],
                        'priority_assignments': attrs.get('priority_assignments', {})
                    }
            
            # Additional analysis based on actual data
            if not vessel_data.empty and 'call_sign' in vessel_data.columns:
                # Analyze potential duplicates that might remain
                potential_duplicates = self._identify_potential_duplicates(vessel_data)
                dedup_analysis['potential_remaining_duplicates'] = potential_duplicates
                
                # Analyze temporal clustering
                if 'arrival_time' in vessel_data.columns:
                    temporal_analysis = self._analyze_temporal_clustering(vessel_data)
                    dedup_analysis['temporal_clustering'] = temporal_analysis
            
        except Exception as e:
            logger.warning(f"Error analyzing deduplication metrics: {e}")
            dedup_analysis['analysis_error'] = str(e)
        
        return dedup_analysis
    
    def _identify_potential_duplicates(self, vessel_data: pd.DataFrame) -> Dict[str, Any]:
        """Identify potential duplicates that might remain in the data"""
        potential_duplicates = {
            'call_sign_duplicates': 0,
            'vessel_name_duplicates': 0,
            'suspicious_patterns': []
        }
        
        try:
            # Check for call sign duplicates
            if 'call_sign' in vessel_data.columns:
                call_sign_counts = vessel_data['call_sign'].value_counts()
                potential_duplicates['call_sign_duplicates'] = (call_sign_counts > 1).sum()
                
                # Identify suspicious patterns
                if potential_duplicates['call_sign_duplicates'] > 0:
                    suspicious_call_signs = call_sign_counts[call_sign_counts > 1].head(5)
                    for call_sign, count in suspicious_call_signs.items():
                        potential_duplicates['suspicious_patterns'].append({
                            'call_sign': call_sign,
                            'count': count,
                            'type': 'call_sign_duplicate'
                        })
            
            # Check for vessel name duplicates
            if 'vessel_name' in vessel_data.columns:
                vessel_name_counts = vessel_data['vessel_name'].value_counts()
                potential_duplicates['vessel_name_duplicates'] = (vessel_name_counts > 1).sum()
        
        except Exception as e:
            logger.warning(f"Error identifying potential duplicates: {e}")
            potential_duplicates['error'] = str(e)
        
        return potential_duplicates
    
    def _analyze_temporal_clustering(self, vessel_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal clustering patterns in vessel data"""
        temporal_analysis = {
            'time_gaps_analysis': {},
            'clustering_patterns': {},
            'data_distribution': {}
        }
        
        try:
            if 'arrival_time' in vessel_data.columns and not vessel_data.empty:
                # Ensure arrival_time is datetime
                arrival_times = pd.to_datetime(vessel_data['arrival_time'], errors='coerce')
                arrival_times = arrival_times.dropna().sort_values()
                
                if len(arrival_times) > 1:
                    # Calculate time gaps between consecutive arrivals
                    time_gaps = arrival_times.diff().dropna()
                    
                    temporal_analysis['time_gaps_analysis'] = {
                        'mean_gap_hours': round(time_gaps.mean().total_seconds() / 3600, 2),
                        'median_gap_hours': round(time_gaps.median().total_seconds() / 3600, 2),
                        'min_gap_minutes': round(time_gaps.min().total_seconds() / 60, 2),
                        'max_gap_hours': round(time_gaps.max().total_seconds() / 3600, 2)
                    }
                    
                    # Identify clustering patterns (arrivals within 1 hour)
                    short_gaps = time_gaps[time_gaps <= pd.Timedelta(hours=1)]
                    temporal_analysis['clustering_patterns'] = {
                        'arrivals_within_1hour': len(short_gaps),
                        'clustering_rate': round((len(short_gaps) / len(time_gaps)) * 100, 2)
                    }
                    
                    # Data distribution by hour of day
                    hour_distribution = arrival_times.dt.hour.value_counts().sort_index()
                    temporal_analysis['data_distribution'] = {
                        'peak_hour': int(hour_distribution.idxmax()),
                        'peak_hour_count': int(hour_distribution.max()),
                        'hourly_distribution': hour_distribution.to_dict()
                    }
        
        except Exception as e:
            logger.warning(f"Error in temporal clustering analysis: {e}")
            temporal_analysis['error'] = str(e)
        
        return temporal_analysis
    
    def _calculate_quality_scores(self, basic_metrics: Dict[str, Any], dedup_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive quality scores"""
        scores = {
            'data_completeness_score': 0,
            'deduplication_score': 0,
            'consistency_score': 0,
            'overall_score': 0,
            'grade': QualityLevel.POOR.value
        }
        
        try:
            # Data completeness score (0-100)
            completeness = basic_metrics.get('data_completeness', 0)
            scores['data_completeness_score'] = completeness
            
            # Deduplication efficiency score (0-100)
            dedup_efficiency = dedup_metrics.get('deduplication_efficiency', 0)
            duplicate_rate = dedup_metrics.get('duplicate_rate', 100)  # Lower is better
            dedup_score = max(0, dedup_efficiency - (duplicate_rate * 2))  # Penalty for high duplicate rate
            scores['deduplication_score'] = round(dedup_score, 2)
            
            # Consistency score based on data patterns
            consistency_factors = []
            
            # Check key column completeness
            key_completeness = basic_metrics.get('key_column_completeness', {})
            if key_completeness:
                avg_key_completeness = sum(key_completeness.values()) / len(key_completeness)
                consistency_factors.append(avg_key_completeness)
            
            # Check for remaining potential duplicates
            potential_dupes = dedup_metrics.get('potential_remaining_duplicates', {})
            if potential_dupes:
                total_records = basic_metrics.get('records_count', 1)
                remaining_dupe_rate = (potential_dupes.get('call_sign_duplicates', 0) / total_records) * 100
                consistency_score = max(0, 100 - (remaining_dupe_rate * 10))
                consistency_factors.append(consistency_score)
            
            scores['consistency_score'] = round(sum(consistency_factors) / len(consistency_factors) if consistency_factors else 0, 2)
            
            # Overall score (weighted average)
            weights = {'completeness': 0.4, 'deduplication': 0.4, 'consistency': 0.2}
            overall = (
                scores['data_completeness_score'] * weights['completeness'] +
                scores['deduplication_score'] * weights['deduplication'] +
                scores['consistency_score'] * weights['consistency']
            )
            scores['overall_score'] = round(overall, 2)
            
            # Assign grade based on overall score
            if overall >= 95:
                scores['grade'] = QualityLevel.EXCELLENT.value
            elif overall >= 85:
                scores['grade'] = QualityLevel.GOOD.value
            elif overall >= 70:
                scores['grade'] = QualityLevel.FAIR.value
            elif overall >= 50:
                scores['grade'] = QualityLevel.POOR.value
            else:
                scores['grade'] = QualityLevel.CRITICAL.value
        
        except Exception as e:
            logger.error(f"Error calculating quality scores: {e}")
            scores['error'] = str(e)
        
        return scores
    
    def _check_quality_thresholds(self, analysis: Dict[str, Any]) -> List[QualityAlert]:
        """Check quality metrics against thresholds and generate alerts"""
        alerts = []
        
        try:
            basic_metrics = analysis.get('basic_metrics', {})
            dedup_metrics = analysis.get('deduplication_analysis', {})
            quality_scores = analysis.get('quality_scores', {})
            
            # Check data completeness
            completeness = basic_metrics.get('data_completeness', 0)
            if completeness < self.thresholds['data_completeness']['poor']:
                alerts.append(QualityAlert(
                    alert_id=f"completeness_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    metric_name="data_completeness",
                    severity=QualityLevel.CRITICAL if completeness < 50 else QualityLevel.POOR,
                    message=f"Data completeness is {completeness}%, below threshold of {self.thresholds['data_completeness']['poor']}%",
                    timestamp=datetime.now(),
                    threshold_violated=self.thresholds['data_completeness']['poor'],
                    actual_value=completeness,
                    category="data_quality"
                ))
            
            # Check duplicate rate
            duplicate_rate = dedup_metrics.get('duplicate_rate', 0)
            if duplicate_rate > self.thresholds['duplicate_rate']['poor']:
                alerts.append(QualityAlert(
                    alert_id=f"duplicates_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    metric_name="duplicate_rate",
                    severity=QualityLevel.CRITICAL if duplicate_rate > 20 else QualityLevel.POOR,
                    message=f"Duplicate rate is {duplicate_rate}%, above threshold of {self.thresholds['duplicate_rate']['poor']}%",
                    timestamp=datetime.now(),
                    threshold_violated=self.thresholds['duplicate_rate']['poor'],
                    actual_value=duplicate_rate,
                    category="deduplication"
                ))
            
            # Check overall quality score
            overall_score = quality_scores.get('overall_score', 0)
            if overall_score < 70:  # Fair threshold
                alerts.append(QualityAlert(
                    alert_id=f"overall_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    metric_name="overall_quality_score",
                    severity=QualityLevel.CRITICAL if overall_score < 50 else QualityLevel.POOR,
                    message=f"Overall quality score is {overall_score}, below acceptable threshold",
                    timestamp=datetime.now(),
                    threshold_violated=70.0,
                    actual_value=overall_score,
                    category="overall_quality"
                ))
        
        except Exception as e:
            logger.error(f"Error checking quality thresholds: {e}")
        
        return alerts
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on quality analysis"""
        recommendations = []
        
        try:
            basic_metrics = analysis.get('basic_metrics', {})
            dedup_metrics = analysis.get('deduplication_analysis', {})
            quality_scores = analysis.get('quality_scores', {})
            
            # Data completeness recommendations
            completeness = basic_metrics.get('data_completeness', 0)
            if completeness < 95:
                recommendations.append(f"Improve data completeness from {completeness}% by addressing missing values in key fields")
            
            # Deduplication recommendations
            duplicate_rate = dedup_metrics.get('duplicate_rate', 0)
            if duplicate_rate > 5:
                recommendations.append(f"High duplicate rate ({duplicate_rate}%) detected. Consider reviewing deduplication strategy parameters")
            
            potential_dupes = dedup_metrics.get('potential_remaining_duplicates', {})
            if potential_dupes.get('call_sign_duplicates', 0) > 0:
                recommendations.append(f"Found {potential_dupes['call_sign_duplicates']} potential call sign duplicates that may need manual review")
            
            # Temporal clustering recommendations
            temporal_analysis = dedup_metrics.get('temporal_clustering', {})
            clustering_rate = temporal_analysis.get('clustering_patterns', {}).get('clustering_rate', 0)
            if clustering_rate > 20:
                recommendations.append(f"High temporal clustering detected ({clustering_rate}%). Consider adjusting time window parameters")
            
            # Overall quality recommendations
            overall_score = quality_scores.get('overall_score', 0)
            if overall_score < 85:
                recommendations.append("Overall quality score below 85%. Focus on improving data completeness and deduplication efficiency")
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Error generating recommendations. Check system logs for details.")
        
        return recommendations
    
    def _store_quality_history(self, analysis: Dict[str, Any]) -> None:
        """Store quality analysis in history for trending"""
        try:
            # Keep only essential metrics for history
            history_entry = {
                'timestamp': analysis['timestamp'],
                'overall_score': analysis.get('quality_scores', {}).get('overall_score', 0),
                'data_completeness': analysis.get('basic_metrics', {}).get('data_completeness', 0),
                'duplicate_rate': analysis.get('deduplication_analysis', {}).get('duplicate_rate', 0),
                'records_count': analysis.get('basic_metrics', {}).get('records_count', 0),
                'alerts_count': len(analysis.get('alerts', []))
            }
            
            self.quality_history.append(history_entry)
            
            # Maintain history size (keep last 100 entries)
            if len(self.quality_history) > 100:
                self.quality_history = self.quality_history[-100:]
                
        except Exception as e:
            logger.error(f"Error storing quality history: {e}")
    
    def _get_date_range(self, vessel_data: pd.DataFrame) -> str:
        """Get date range from vessel data"""
        try:
            if 'arrival_time' in vessel_data.columns and not vessel_data.empty:
                arrival_times = pd.to_datetime(vessel_data['arrival_time'], errors='coerce')
                arrival_times = arrival_times.dropna()
                if not arrival_times.empty:
                    return f"{arrival_times.min()} to {arrival_times.max()}"
        except Exception:
            pass
        return "unknown"
    
    def _get_status_distribution(self, vessel_data: pd.DataFrame) -> Dict[str, int]:
        """Get distribution of vessel statuses"""
        try:
            if 'status' in vessel_data.columns and not vessel_data.empty:
                return vessel_data['status'].value_counts().to_dict()
        except Exception:
            pass
        return {}
    
    def get_quality_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get quality trends over specified time period"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_history = [
                entry for entry in self.quality_history 
                if datetime.fromisoformat(entry['timestamp']) > cutoff_time
            ]
            
            if not recent_history:
                return {'status': 'no_data', 'message': f'No quality data available for last {hours} hours'}
            
            # Calculate trends
            scores = [entry['overall_score'] for entry in recent_history]
            completeness = [entry['data_completeness'] for entry in recent_history]
            duplicate_rates = [entry['duplicate_rate'] for entry in recent_history]
            
            trends = {
                'period_hours': hours,
                'data_points': len(recent_history),
                'overall_score_trend': {
                    'current': scores[-1] if scores else 0,
                    'average': round(sum(scores) / len(scores), 2) if scores else 0,
                    'min': min(scores) if scores else 0,
                    'max': max(scores) if scores else 0,
                    'trend_direction': self._calculate_trend_direction(scores)
                },
                'completeness_trend': {
                    'current': completeness[-1] if completeness else 0,
                    'average': round(sum(completeness) / len(completeness), 2) if completeness else 0,
                    'trend_direction': self._calculate_trend_direction(completeness)
                },
                'duplicate_rate_trend': {
                    'current': duplicate_rates[-1] if duplicate_rates else 0,
                    'average': round(sum(duplicate_rates) / len(duplicate_rates), 2) if duplicate_rates else 0,
                    'trend_direction': self._calculate_trend_direction(duplicate_rates, lower_is_better=True)
                }
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating quality trends: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_trend_direction(self, values: List[float], lower_is_better: bool = False) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        recent_avg = sum(values[-3:]) / len(values[-3:]) if len(values) >= 3 else values[-1]
        earlier_avg = sum(values[:3]) / len(values[:3]) if len(values) >= 3 else values[0]
        
        diff = recent_avg - earlier_avg
        threshold = 0.5  # Minimum change to consider as trend
        
        if abs(diff) < threshold:
            return "stable"
        elif diff > 0:
            return "declining" if lower_is_better else "improving"
        else:
            return "improving" if lower_is_better else "declining"
    
    def generate_quality_report(self, vessel_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        try:
            # Perform quality analysis
            analysis = self.analyze_vessel_data_quality(vessel_data)
            
            # Get trends
            trends = self.get_quality_trends(hours=24)
            
            # Compile comprehensive report
            report = {
                'report_id': f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'overall_grade': analysis.get('quality_scores', {}).get('grade', 'unknown'),
                    'overall_score': analysis.get('quality_scores', {}).get('overall_score', 0),
                    'total_records': analysis.get('basic_metrics', {}).get('records_count', 0),
                    'active_alerts': len(analysis.get('alerts', [])),
                    'recommendations_count': len(analysis.get('recommendations', []))
                },
                'detailed_analysis': analysis,
                'trends': trends,
                'system_info': {
                    'monitor_version': '1.0.0',
                    'config': self.config
                }
            }
            
            logger.info(f"Quality report generated: {report['report_id']}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return {
                'report_id': f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }

# Global instance for easy access
quality_monitor = DataQualityMonitor()