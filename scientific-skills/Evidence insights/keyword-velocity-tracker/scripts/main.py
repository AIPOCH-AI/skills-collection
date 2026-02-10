#!/usr/bin/env python3
"""
Keyword Velocity Tracker
Calculate keyword publication growth rate and acceleration to determine field development stage.
"""

import json
import argparse
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum


class DevelopmentStage(Enum):
    """Field development stage"""
    EMBRYONIC = "embryonic"
    GROWTH = "growth"
    MATURE = "mature"
    DECLINE = "decline"


class TrendDirection(Enum):
    """Trend direction"""
    GROWTH = "growth"
    STABLE = "stable"
    DECLINE = "decline"


@dataclass
class VelocityPoint:
    """Single point velocity and acceleration data"""
    year: int
    count: int
    velocity: Optional[float] = None
    acceleration: Optional[float] = None
    smoothed_velocity: Optional[float] = None


@dataclass
class Prediction:
    """Prediction result"""
    year: int
    estimated_count: int
    confidence: float


class KeywordVelocityTracker:
    """
    Keyword publication growth rate and acceleration analyzer
    """
    
    def __init__(
        self,
        time_window: int = 3,
        smoothing: bool = True,
        smoothing_factor: float = 0.3,
        min_confidence: float = 0.7
    ):
        """
        Initialize analyzer
        
        Args:
            time_window: Time window for calculating growth rate (years)
            smoothing: Whether to smooth data
            smoothing_factor: Smoothing coefficient
            min_confidence: Minimum confidence threshold
        """
        self.time_window = time_window
        self.smoothing = smoothing
        self.smoothing_factor = smoothing_factor
        self.min_confidence = min_confidence
    
    def _validate_data(self, data: List[Dict]) -> List[Dict]:
        """Validate and sort input data"""
        if not data or len(data) < 2:
            raise ValueError("At least 2 years of data required")
        
        # Ensure data is sorted by year
        sorted_data = sorted(data, key=lambda x: x['year'])
        
        # Validate data integrity
        for item in sorted_data:
            if 'year' not in item or 'count' not in item:
                raise ValueError("Data items must contain 'year' and 'count' fields")
            if not isinstance(item['count'], (int, float)) or item['count'] < 0:
                raise ValueError("count must be non-negative")
        
        return sorted_data
    
    def _calculate_velocity(
        self,
        current_count: float,
        previous_count: float
    ) -> Optional[float]:
        """
        Calculate growth rate
        
        Args:
            current_count: Current year publication count
            previous_count: Previous year publication count
            
        Returns:
            Growth rate (can be negative)
        """
        if previous_count == 0:
            return None if current_count == 0 else float('inf')
        return (current_count - previous_count) / previous_count
    
    def _smooth_series(
        self,
        series: List[Optional[float]]
    ) -> List[Optional[float]]:
        """
        Smooth series using exponential smoothing
        
        Args:
            series: Raw series (may contain None)
            
        Returns:
            Smoothed series
        """
        if not self.smoothing:
            return series
        
        smoothed = []
        last_valid = None
        
        for value in series:
            if value is None:
                smoothed.append(None)
            elif last_valid is None:
                smoothed.append(value)
                last_valid = value
            else:
                smoothed_value = (
                    self.smoothing_factor * value +
                    (1 - self.smoothing_factor) * last_valid
                )
                smoothed.append(smoothed_value)
                last_valid = smoothed_value
        
        return smoothed
    
    def _calculate_velocity_series(
        self,
        data: List[Dict]
    ) -> List[VelocityPoint]:
        """
        Calculate complete time series data
        
        Args:
            data: Raw publication data
            
        Returns:
            Time series with velocity and acceleration
        """
        velocity_points = []
        velocities = []
        
        # First year data point
        velocity_points.append(VelocityPoint(
            year=data[0]['year'],
            count=data[0]['count'],
            velocity=None,
            acceleration=None
        ))
        velocities.append(None)
        
        # Calculate growth rate for each year
        for i in range(1, len(data)):
            current = data[i]
            previous = data[i - 1]
            
            velocity = self._calculate_velocity(
                current['count'],
                previous['count']
            )
            velocities.append(velocity)
            
            velocity_points.append(VelocityPoint(
                year=current['year'],
                count=current['count'],
                velocity=velocity
            ))
        
        # Smooth velocity
        if self.smoothing:
            smoothed_velocities = self._smooth_series(velocities)
            for i, vp in enumerate(velocity_points):
                vp.smoothed_velocity = smoothed_velocities[i]
        
        # Calculate acceleration (rate of change of velocity)
        for i in range(2, len(velocity_points)):
            current_vp = velocity_points[i]
            prev_vp = velocity_points[i - 1]
            
            v_curr = current_vp.smoothed_velocity or current_vp.velocity
            v_prev = prev_vp.smoothed_velocity or prev_vp.velocity
            
            if v_curr is not None and v_prev is not None:
                current_vp.acceleration = v_curr - v_prev
        
        return velocity_points
    
    def _determine_stage(
        self,
        velocity_points: List[VelocityPoint]
    ) -> Tuple[DevelopmentStage, float, TrendDirection]:
        """
        Determine field development stage
        
        Args:
            velocity_points: Time series data
            
        Returns:
            (stage, confidence, trend direction)
        """
        # Get recent data points
        recent_points = velocity_points[-self.time_window:]
        
        valid_velocities = [
            (vp.smoothed_velocity or vp.velocity)
            for vp in recent_points
            if (vp.smoothed_velocity or vp.velocity) is not None
        ]
        
        valid_accelerations = [
            vp.acceleration for vp in recent_points
            if vp.acceleration is not None
        ]
        
        if not valid_velocities:
            return DevelopmentStage.EMBRYONIC, 0.0, TrendDirection.STABLE
        
        avg_velocity = np.mean(valid_velocities)
        velocity_std = np.std(valid_velocities) if len(valid_velocities) > 1 else 0
        
        avg_acceleration = (
            np.mean(valid_accelerations) if valid_accelerations else 0
        )
        
        # Determine stage
        if avg_velocity < -0.05:
            stage = DevelopmentStage.DECLINE
            confidence = min(1.0, abs(avg_velocity) * 2)
            trend = TrendDirection.DECLINE
        elif avg_velocity < 0.1:
            # Low growth could be embryonic or decline
            if avg_acceleration > 0:
                stage = DevelopmentStage.EMBRYONIC
                confidence = min(1.0, avg_acceleration * 3 + 0.5)
                trend = TrendDirection.GROWTH
            else:
                stage = DevelopmentStage.DECLINE
                confidence = min(1.0, abs(avg_acceleration) * 3 + 0.5)
                trend = TrendDirection.DECLINE
        elif velocity_std < 0.1 and abs(avg_acceleration) < 0.05:
            # Stable growth → mature stage
            stage = DevelopmentStage.MATURE
            confidence = min(1.0, 1 - velocity_std * 5)
            trend = TrendDirection.STABLE
        elif avg_acceleration > 0:
            # Accelerating growth → growth stage
            stage = DevelopmentStage.GROWTH
            confidence = min(1.0, avg_acceleration * 2 + 0.5)
            trend = TrendDirection.GROWTH
        else:
            # Growing but decelerating → may be transitioning from growth to mature
            stage = DevelopmentStage.MATURE
            confidence = min(1.0, 0.6 + abs(avg_acceleration))
            trend = TrendDirection.STABLE
        
        return stage, max(self.min_confidence, confidence), trend
    
    def _generate_insights(
        self,
        velocity_points: List[VelocityPoint],
        stage: DevelopmentStage,
        trend: TrendDirection,
        current_velocity: float,
        current_acceleration: float
    ) -> List[str]:
        """Generate analysis insights"""
        insights = []
        
        # Stage-related insights
        if stage == DevelopmentStage.GROWTH:
            insights.append("Field is in growth stage with rapidly increasing publications")
            if current_acceleration > 0.1:
                insights.append("Growth rate is accelerating, field popularity is rising")
        elif stage == DevelopmentStage.MATURE:
            insights.append("Field has entered mature stage with stable growth")
            if current_acceleration < -0.05:
                insights.append("Recent slight deceleration detected, may be entering plateau")
        elif stage == DevelopmentStage.EMBRYONIC:
            insights.append("Field is still in embryonic stage with small publication base")
            if current_acceleration > 0:
                insights.append("Showing growth potential, worth monitoring")
        elif stage == DevelopmentStage.DECLINE:
            insights.append("Field may be entering decline stage, publication growth slowing or decreasing")
        
        # Velocity-related insights
        if current_velocity > 0.5:
            insights.append("Annual growth rate exceeds 50%, very hot field")
        elif current_velocity < 0.05:
            insights.append("Annual growth rate below 5%, insufficient growth momentum")
        
        # Acceleration-related insights
        if current_acceleration > 0.2:
            insights.append("Significant growth acceleration detected, possibly due to breakthrough advances")
        elif current_acceleration < -0.2:
            insights.append("Significant growth deceleration detected, may need new research breakthroughs")
        
        return insights
    
    def _predict_future(
        self,
        velocity_points: List[VelocityPoint],
        predict_years: int
    ) -> Dict[int, Prediction]:
        """
        Predict future publication counts
        
        Args:
            velocity_points: Historical data
            predict_years: Years to predict
            
        Returns:
            Prediction results dictionary
        """
        if len(velocity_points) < 2:
            return {}
        
        predictions = {}
        last_point = velocity_points[-1]
        
        # Use recent growth rate trend
        recent_velocities = [
            (vp.smoothed_velocity or vp.velocity)
            for vp in velocity_points[-self.time_window:]
            if (vp.smoothed_velocity or vp.velocity) is not None
        ]
        
        if not recent_velocities:
            return {}
        
        avg_velocity = np.mean(recent_velocities)
        velocity_trend = 0
        
        # Calculate velocity trend (acceleration)
        if len(recent_velocities) >= 2:
            velocity_trend = (
                recent_velocities[-1] - recent_velocities[0]
            ) / (len(recent_velocities) - 1)
        
        current_count = last_point.count
        
        for i in range(1, predict_years + 1):
            year = last_point.year + i
            
            # Growth rate that decreases over time (considering growth slowdown)
            projected_velocity = avg_velocity + velocity_trend * i
            # Ensure growth rate doesn't become too extreme
            projected_velocity = max(-0.3, min(1.0, projected_velocity))
            
            # Calculate predicted count
            projected_count = int(current_count * (1 + projected_velocity) ** i)
            projected_count = max(0, projected_count)
            
            # Confidence decreases with prediction time
            confidence = max(0.3, 0.9 - i * 0.15)
            
            predictions[year] = Prediction(
                year=year,
                estimated_count=projected_count,
                confidence=round(confidence, 2)
            )
        
        return predictions
    
    def analyze(
        self,
        keyword: str,
        data: List[Dict],
        predict_years: int = 3
    ) -> Dict:
        """
        Perform complete keyword velocity analysis
        
        Args:
            keyword: Keyword to analyze
            data: Time series publication data
            predict_years: Years to predict into future
            
        Returns:
            Complete analysis results
        """
        # Validate data
        validated_data = self._validate_data(data)
        
        # Calculate velocity series
        velocity_points = self._calculate_velocity_series(validated_data)
        
        # Get latest data
        latest_point = velocity_points[-1]
        current_velocity = (
            latest_point.smoothed_velocity or latest_point.velocity or 0
        )
        current_acceleration = latest_point.acceleration or 0
        
        # Determine stage
        stage, confidence, trend = self._determine_stage(velocity_points)
        
        # Generate insights
        insights = self._generate_insights(
            velocity_points,
            stage,
            trend,
            current_velocity,
            current_acceleration
        )
        
        # Predict future
        predictions = self._predict_future(velocity_points, predict_years)
        
        # Build return result
        result = {
            "keyword": keyword,
            "analysis_period": {
                "start": validated_data[0]['year'],
                "end": validated_data[-1]['year']
            },
            "current_velocity": round(current_velocity, 4),
            "current_acceleration": round(current_acceleration, 4),
            "stage": stage.value,
            "stage_confidence": round(confidence, 2),
            "trend": trend.value,
            "velocity_series": [
                {
                    "year": vp.year,
                    "count": vp.count,
                    "velocity": round(vp.velocity, 4) if vp.velocity else None,
                    "acceleration": round(vp.acceleration, 4) if vp.acceleration else None,
                    "smoothed_velocity": (
                        round(vp.smoothed_velocity, 4)
                        if vp.smoothed_velocity else None
                    )
                }
                for vp in velocity_points
            ],
            "prediction": {
                str(year): {
                    "estimated_count": pred.estimated_count,
                    "confidence": pred.confidence
                }
                for year, pred in predictions.items()
            },
            "insights": insights
        }
        
        return result


def main():
    """Command line entry"""
    parser = argparse.ArgumentParser(
        description='Keyword publication growth rate and acceleration analysis tool'
    )
    parser.add_argument(
        '--keyword', '-k',
        required=True,
        help='Keyword to analyze'
    )
    parser.add_argument(
        '--data-file', '-f',
        required=True,
        help='JSON data file path, format: [{"year": 2020, "count": 100}, ...]'
    )
    parser.add_argument(
        '--predict-years', '-p',
        type=int,
        default=3,
        help='Years to predict into future (default: 3)'
    )
    parser.add_argument(
        '--time-window', '-w',
        type=int,
        default=3,
        help='Time window size (default: 3)'
    )
    parser.add_argument(
        '--no-smoothing',
        action='store_true',
        help='Disable data smoothing'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: console output)'
    )
    
    args = parser.parse_args()
    
    # Read data
    with open(args.data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create analyzer
    tracker = KeywordVelocityTracker(
        time_window=args.time_window,
        smoothing=not args.no_smoothing
    )
    
    # Perform analysis
    result = tracker.analyze(
        keyword=args.keyword,
        data=data,
        predict_years=args.predict_years
    )
    
    # Output results
    output_json = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Results saved to: {args.output}")
    else:
        print(output_json)


if __name__ == '__main__':
    main()
