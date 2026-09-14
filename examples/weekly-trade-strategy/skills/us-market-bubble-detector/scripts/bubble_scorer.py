#!/usr/bin/env python3
"""
Bubble-O-Meter: 多维度评估美国股市泡沫程度的脚本

8个指标按0-2分评估，总分(0-16分)判定泡沫程度:
- 0-4: 正常区间
- 5-8: 警戒区间
- 9-12: 狂热区间
- 13-16: 临界区间

使用方法:
    python bubble_scorer.py --ticker SPY --period 1y
"""

import argparse
import json
from datetime import datetime


class BubbleScorer:
    """泡沫评分系统"""

    def __init__(self):
        self.indicators = {
            "mass_penetration": {
                "name": "大众渗透度",
                "weight": 2,
                "description": "非投资者群体的推荐和提及",
            },
            "media_saturation": {
                "name": "媒体饱和度",
                "weight": 2,
                "description": "搜索、社交媒体、媒体曝光急剧上升",
            },
            "new_accounts": {
                "name": "新参与者涌入",
                "weight": 2,
                "description": "开户和资金流入加速",
            },
            "new_issuance": {
                "name": "新发行泛滥",
                "weight": 2,
                "description": "IPO/SPAC/相关产品泛滥",
            },
            "leverage": {
                "name": "杠杆",
                "weight": 2,
                "description": "保证金、信用、融资利率偏离",
            },
            "price_acceleration": {
                "name": "价格加速度",
                "weight": 2,
                "description": "收益率达到历史分布上端",
            },
            "valuation_disconnect": {
                "name": "估值偏离",
                "weight": 2,
                "description": "基本面解释完全依赖叙事",
            },
            "breadth_expansion": {
                "name": "相关性与广度",
                "weight": 2,
                "description": "低质量股票也全面上涨",
            },
        }

    def calculate_score(self, scores: dict[str, int]) -> dict:
        """
        根据各指标评分计算综合评估

        Args:
            scores: 各指标的评分字典 (0-2分)

        Returns:
            评估结果字典
        """
        total_score = sum(scores.values())
        max_score = len(self.indicators) * 2

        # 泡沫阶段判定
        if total_score <= 4:
            phase = "正常区间"
            risk_level = "低"
            action = "继续正常投资策略"
        elif total_score <= 8:
            phase = "警戒区间"
            risk_level = "中"
            action = "开始部分止盈，缩小新仓位规模"
        elif total_score <= 12:
            phase = "狂热区间"
            risk_level = "高"
            action = "加速阶梯式止盈，严格ATR跟踪止损，总风险预算削减30-50%"
        else:
            phase = "临界区间"
            risk_level = "极高"
            action = "大幅止盈或全面对冲，停止新建仓位，确认反转后考虑做空"

        # Minsky阶段推定
        minsky_phase = self._estimate_minsky_phase(scores, total_score)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_score": total_score,
            "max_score": max_score,
            "percentage": round(total_score / max_score * 100, 1),
            "phase": phase,
            "risk_level": risk_level,
            "minsky_phase": minsky_phase,
            "recommended_action": action,
            "indicator_scores": scores,
            "detailed_indicators": self._format_indicator_details(scores),
        }

    def _estimate_minsky_phase(self, scores: dict[str, int], total: int) -> str:
        """Minsky/Kindleberger阶段推定"""
        mass_pen = scores.get("mass_penetration", 0)
        media = scores.get("media_saturation", 0)
        price_acc = scores.get("price_acceleration", 0)

        if total <= 4:
            return "Displacement/Early Boom (触发与早期扩张)"
        elif total <= 8:
            if media >= 1 and price_acc >= 1:
                return "Boom (扩张期)"
            else:
                return "Displacement/Early Boom (触发与早期扩张)"
        elif total <= 12:
            if mass_pen >= 2 and media >= 2:
                return "Euphoria (狂热期) - FOMO已制度化"
            else:
                return "Late Boom/Early Euphoria (扩张后期与狂热初期)"
        else:
            if mass_pen >= 2:
                return "Peak Euphoria/Profit Taking (狂热顶峰与止盈开始) - 反转临近"
            else:
                return "Euphoria (狂热期)"

    def _format_indicator_details(self, scores: dict[str, int]) -> list[dict]:
        """格式化指标详细信息"""
        details = []
        for key, value in scores.items():
            indicator = self.indicators.get(key, {})
            status = "🔴高" if value == 2 else "🟡中" if value == 1 else "🟢低"
            details.append(
                {
                    "indicator": indicator.get("name", key),
                    "score": value,
                    "status": status,
                    "description": indicator.get("description", ""),
                }
            )
        return details

    def get_scoring_guidelines(self) -> str:
        """返回各指标的评分指南"""
        guidelines = """
## 泡沫评分指南

### 1. 大众渗透度 (Mass Penetration)
- 0分: 仅限专家和投资者群体讨论
- 1分: 普通大众也有认知，但作为投资对象仍有限
- 2分: 非投资者（出租车司机、理发师、家人）积极推荐和提及

### 2. 媒体饱和度 (Media Saturation)
- 0分: 正常水平的报道和搜索趋势
- 1分: 搜索趋势、社交媒体提及量为平时的2-3倍
- 2分: 电视专题、杂志封面、搜索趋势暴涨（平时的5倍以上）

### 3. 新参与者涌入 (New Accounts & Inflows)
- 0分: 正常水平的开户和入金
- 1分: 开户量同比增长50-100%
- 2分: 开户量同比增长200%以上，"首次投资"群体大量涌入

### 4. 新发行泛滥 (New Issuance Flood)
- 0分: 正常水平的IPO/产品发行
- 1分: IPO/SPAC/相关ETF同比增长50%以上
- 2分: 低质量IPO泛滥，"XX概念"基金和ETF滥造

### 5. 杠杆 (Leverage Indicators)
- 0分: 保证金余额和信用评估在正常范围
- 1分: 保证金余额为历史平均的1.5倍，期货仓位偏离
- 2分: 保证金余额创历史新高，融资利率居高不下，极端仓位偏离

### 6. 价格加速度 (Price Acceleration)
- 0分: 年化收益率接近历史分布中位数
- 1分: 年化收益率超过历史90百分位
- 2分: 年化收益率达到历史95-99百分位，或加速度（二阶导数）为正且增加

### 7. 估值偏离 (Valuation Disconnect)
- 0分: 可用基本面合理解释
- 1分: 高估值但"增长预期"尚可解释
- 2分: 解释完全依赖"叙事"、"革命"、"范式转换"，"这次不一样"

### 8. 相关性与广度 (Breadth & Correlation)
- 0分: 仅部分龙头股上涨
- 1分: 波及整个板块，mid-cap也上涨
- 2分: 低质量、low-cap股票全面上涨，"僵尸企业"也上涨（最后的买家入场）
"""
        return guidelines

    def format_output(self, result: dict) -> str:
        """将结果格式化为可读输出"""
        output = f"""
{"=" * 60}
🔍 美国市场泡沫度评估 - Bubble-O-Meter
{"=" * 60}

评估时间: {result["timestamp"]}

【综合评分】
{result["total_score"]}/{result["max_score"]}分 ({result["percentage"]}%)

【市场阶段】
当前: {result["phase"]} (风险: {result["risk_level"]})
Minsky阶段: {result["minsky_phase"]}

【建议操作】
{result["recommended_action"]}

{"=" * 60}
【各指标评分】
{"=" * 60}
"""
        for detail in result["detailed_indicators"]:
            output += f"\n{detail['status']} {detail['indicator']}: {detail['score']}/2分\n"
            output += f"   └─ {detail['description']}\n"

        output += f"\n{'=' * 60}\n"

        return output


def manual_assessment() -> dict[str, int]:
    """交互式手动评估"""
    scorer = BubbleScorer()
    print("\n" + "=" * 60)
    print("🔍 美国市场泡沫度评估 - Manual Assessment")
    print("=" * 60)
    print("\n请对各指标进行0-2分评估:")
    print(scorer.get_scoring_guidelines())

    scores = {}
    for key, indicator in scorer.indicators.items():
        while True:
            try:
                score = int(input(f"\n{indicator['name']} (0-2): "))
                if 0 <= score <= 2:
                    scores[key] = score
                    break
                else:
                    print("请输入0、1或2")
            except ValueError:
                print("请输入数字")

    return scores


def main():
    parser = argparse.ArgumentParser(description="评估美国市场泡沫程度的Bubble-O-Meter")
    parser.add_argument("--manual", action="store_true", help="交互式手动评估模式")
    parser.add_argument(
        "--scores",
        type=str,
        help='JSON格式的评分字符串 (例: \'{"mass_penetration":2,"media_saturation":1,...}\')',
    )
    parser.add_argument("--output", choices=["text", "json"], default="text", help="输出格式")

    args = parser.parse_args()
    scorer = BubbleScorer()

    # 获取评分
    if args.manual:
        scores = manual_assessment()
    elif args.scores:
        try:
            scores = json.loads(args.scores)
        except json.JSONDecodeError:
            print("错误: 无效的JSON格式")
            return 1
    else:
        print("错误: 请指定 --manual 或 --scores")
        print("\n显示评分指南:")
        print(scorer.get_scoring_guidelines())
        return 1

    # 执行评估
    result = scorer.calculate_score(scores)

    # 输出
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(scorer.format_output(result))

    return 0


if __name__ == "__main__":
    exit(main())
