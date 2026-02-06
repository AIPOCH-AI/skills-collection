#!/usr/bin/env python3
"""
Keyword Velocity Tracker
计算关键词的文献增长速率和加速度，判断领域发展阶段。
"""

import json
import argparse
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum


class DevelopmentStage(Enum):
    """领域发展阶段"""
    EMBRYONIC = "萌芽期"
    GROWTH = "成长期"
    MATURE = "成熟期"
    DECLINE = "衰退期"


class TrendDirection(Enum):
    """趋势方向"""
    GROWTH = "growth"
    STABLE = "stable"
    DECLINE = "decline"


@dataclass
class VelocityPoint:
    """单点速度和加速度数据"""
    year: int
    count: int
    velocity: Optional[float] = None
    acceleration: Optional[float] = None
    smoothed_velocity: Optional[float] = None


@dataclass
class Prediction:
    """预测结果"""
    year: int
    estimated_count: int
    confidence: float


class KeywordVelocityTracker:
    """
    关键词文献增长速率和加速度分析器
    """
    
    def __init__(
        self,
        time_window: int = 3,
        smoothing: bool = True,
        smoothing_factor: float = 0.3,
        min_confidence: float = 0.7
    ):
        """
        初始化分析器
        
        Args:
            time_window: 计算增长率的时间窗口（年）
            smoothing: 是否平滑数据
            smoothing_factor: 平滑系数
            min_confidence: 最小置信度阈值
        """
        self.time_window = time_window
        self.smoothing = smoothing
        self.smoothing_factor = smoothing_factor
        self.min_confidence = min_confidence
    
    def _validate_data(self, data: List[Dict]) -> List[Dict]:
        """验证并排序输入数据"""
        if not data or len(data) < 2:
            raise ValueError("至少需要2个年份的数据")
        
        # 确保数据按年份排序
        sorted_data = sorted(data, key=lambda x: x['year'])
        
        # 验证数据完整性
        for item in sorted_data:
            if 'year' not in item or 'count' not in item:
                raise ValueError("数据项必须包含 'year' 和 'count' 字段")
            if not isinstance(item['count'], (int, float)) or item['count'] < 0:
                raise ValueError("count 必须是非负数")
        
        return sorted_data
    
    def _calculate_velocity(
        self,
        current_count: float,
        previous_count: float
    ) -> Optional[float]:
        """
        计算增长率
        
        Args:
            current_count: 当前年份文献数
            previous_count: 前一年文献数
            
        Returns:
            增长率（可为负值）
        """
        if previous_count == 0:
            return None if current_count == 0 else float('inf')
        return (current_count - previous_count) / previous_count
    
    def _smooth_series(
        self,
        series: List[Optional[float]]
    ) -> List[Optional[float]]:
        """
        使用指数平滑处理序列
        
        Args:
            series: 原始序列（可能包含None）
            
        Returns:
            平滑后的序列
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
        计算完整的时间序列数据
        
        Args:
            data: 原始文献数据
            
        Returns:
            包含速度和加速度的时间序列
        """
        velocity_points = []
        velocities = []
        
        # 第一年的数据点
        velocity_points.append(VelocityPoint(
            year=data[0]['year'],
            count=data[0]['count'],
            velocity=None,
            acceleration=None
        ))
        velocities.append(None)
        
        # 计算每年的增长率
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
        
        # 平滑处理速度
        if self.smoothing:
            smoothed_velocities = self._smooth_series(velocities)
            for i, vp in enumerate(velocity_points):
                vp.smoothed_velocity = smoothed_velocities[i]
        
        # 计算加速度（速度的变化率）
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
        判断领域发展阶段
        
        Args:
            velocity_points: 时间序列数据
            
        Returns:
            (阶段, 置信度, 趋势方向)
        """
        # 获取最近的数据点
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
        
        # 判断阶段
        if avg_velocity < -0.05:
            stage = DevelopmentStage.DECLINE
            confidence = min(1.0, abs(avg_velocity) * 2)
            trend = TrendDirection.DECLINE
        elif avg_velocity < 0.1:
            # 低增长可能是萌芽期或衰退期
            if avg_acceleration > 0:
                stage = DevelopmentStage.EMBRYONIC
                confidence = min(1.0, avg_acceleration * 3 + 0.5)
                trend = TrendDirection.GROWTH
            else:
                stage = DevelopmentStage.DECLINE
                confidence = min(1.0, abs(avg_acceleration) * 3 + 0.5)
                trend = TrendDirection.DECLINE
        elif velocity_std < 0.1 and abs(avg_acceleration) < 0.05:
            # 增长稳定 → 成熟期
            stage = DevelopmentStage.MATURE
            confidence = min(1.0, 1 - velocity_std * 5)
            trend = TrendDirection.STABLE
        elif avg_acceleration > 0:
            # 增长加速 → 成长期
            stage = DevelopmentStage.GROWTH
            confidence = min(1.0, avg_acceleration * 2 + 0.5)
            trend = TrendDirection.GROWTH
        else:
            # 增长但减速 → 可能从成长期进入成熟期
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
        """生成分析洞察"""
        insights = []
        
        # 阶段相关洞察
        if stage == DevelopmentStage.GROWTH:
            insights.append("领域处于成长期，文献数量快速增长")
            if current_acceleration > 0.1:
                insights.append("增长速度正在加快，领域热度上升")
        elif stage == DevelopmentStage.MATURE:
            insights.append("领域已进入成熟期，增长趋于稳定")
            if current_acceleration < -0.05:
                insights.append("近期出现轻微减速，可能进入平台期")
        elif stage == DevelopmentStage.EMBRYONIC:
            insights.append("领域尚处于萌芽期，文献基数较小")
            if current_acceleration > 0:
                insights.append("显示出增长潜力，值得关注")
        elif stage == DevelopmentStage.DECLINE:
            insights.append("领域可能进入衰退期，文献增长放缓或下降")
        
        # 速度相关洞察
        if current_velocity > 0.5:
            insights.append("年增长率超过50%，是非常热门的领域")
        elif current_velocity < 0.05:
            insights.append("年增长率低于5%，增长动力不足")
        
        # 加速度相关洞察
        if current_acceleration > 0.2:
            insights.append("增长加速明显，可能是突破性进展带来的")
        elif current_acceleration < -0.2:
            insights.append("增长减速明显，可能需要新的研究突破")
        
        return insights
    
    def _predict_future(
        self,
        velocity_points: List[VelocityPoint],
        predict_years: int
    ) -> Dict[int, Prediction]:
        """
        预测未来文献数量
        
        Args:
            velocity_points: 历史数据
            predict_years: 预测年数
            
        Returns:
            预测结果字典
        """
        if len(velocity_points) < 2:
            return {}
        
        predictions = {}
        last_point = velocity_points[-1]
        
        # 使用最近的增长率趋势
        recent_velocities = [
            (vp.smoothed_velocity or vp.velocity)
            for vp in velocity_points[-self.time_window:]
            if (vp.smoothed_velocity or vp.velocity) is not None
        ]
        
        if not recent_velocities:
            return {}
        
        avg_velocity = np.mean(recent_velocities)
        velocity_trend = 0
        
        # 计算速度趋势（加速度）
        if len(recent_velocities) >= 2:
            velocity_trend = (
                recent_velocities[-1] - recent_velocities[0]
            ) / (len(recent_velocities) - 1)
        
        current_count = last_point.count
        
        for i in range(1, predict_years + 1):
            year = last_point.year + i
            
            # 随时间递减的增长率（考虑增长放缓）
            projected_velocity = avg_velocity + velocity_trend * i
            # 确保增长率不会变得过于极端
            projected_velocity = max(-0.3, min(1.0, projected_velocity))
            
            # 计算预测数量
            projected_count = int(current_count * (1 + projected_velocity) ** i)
            projected_count = max(0, projected_count)
            
            # 置信度随预测时间递减
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
        执行完整的关键词速度分析
        
        Args:
            keyword: 分析的关键词
            data: 时间序列文献数据
            predict_years: 预测未来年份数
            
        Returns:
            完整的分析结果
        """
        # 验证数据
        validated_data = self._validate_data(data)
        
        # 计算速度序列
        velocity_points = self._calculate_velocity_series(validated_data)
        
        # 获取最新数据
        latest_point = velocity_points[-1]
        current_velocity = (
            latest_point.smoothed_velocity or latest_point.velocity or 0
        )
        current_acceleration = latest_point.acceleration or 0
        
        # 判断阶段
        stage, confidence, trend = self._determine_stage(velocity_points)
        
        # 生成洞察
        insights = self._generate_insights(
            velocity_points,
            stage,
            trend,
            current_velocity,
            current_acceleration
        )
        
        # 预测未来
        predictions = self._predict_future(velocity_points, predict_years)
        
        # 构建返回结果
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
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='关键词文献增长速率和加速度分析工具'
    )
    parser.add_argument(
        '--keyword', '-k',
        required=True,
        help='要分析的关键词'
    )
    parser.add_argument(
        '--data-file', '-f',
        required=True,
        help='JSON数据文件路径，格式: [{"year": 2020, "count": 100}, ...]'
    )
    parser.add_argument(
        '--predict-years', '-p',
        type=int,
        default=3,
        help='预测未来年份数 (默认: 3)'
    )
    parser.add_argument(
        '--time-window', '-w',
        type=int,
        default=3,
        help='时间窗口大小 (默认: 3)'
    )
    parser.add_argument(
        '--no-smoothing',
        action='store_true',
        help='禁用数据平滑处理'
    )
    parser.add_argument(
        '--output', '-o',
        help='输出文件路径 (默认输出到控制台)'
    )
    
    args = parser.parse_args()
    
    # 读取数据
    with open(args.data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建分析器
    tracker = KeywordVelocityTracker(
        time_window=args.time_window,
        smoothing=not args.no_smoothing
    )
    
    # 执行分析
    result = tracker.analyze(
        keyword=args.keyword,
        data=data,
        predict_years=args.predict_years
    )
    
    # 输出结果
    output_json = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"结果已保存到: {args.output}")
    else:
        print(output_json)


if __name__ == '__main__':
    main()
