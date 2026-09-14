# Edge制度化流程

将日常"灵感"不停留在个人备忘层面，而是提升为可复现的策略资产的标准流程。

## 目的

- 将观察 -> 抽象化 -> 策略化 -> 管道验证进行分工
- 在各阶段定义"晋级门控"，确保质量统一
- 将Edge的生成和劣化监控放在同一运营体系中

## 1. 3技能构成 + 管道连接

### 1-1. 主线

```mermaid
flowchart TD
    A[edge-hint-collector<br/>观察的结构化<br/>output: hints.yaml]
    B[edge-concept-synth<br/>假设的抽象化<br/>output: edge_concepts.yaml]
    C[edge-strategy-export<br/>策略化/导出<br/>output: strategy.yaml + metadata.json]
    D[trade-strategy-pipeline<br/>Phase I -> IS Gate -> Walk-Forward<br/>-> OOS Gate -> Robustness -> Paper -> Live]

    A --> B --> C --> D
```

### 1-2. 退回循环（门控运营）

```mermaid
flowchart TD
    H0[edge-hint-collector]
    C0[edge-concept-synth]
    S0[edge-strategy-export]
    P0[trade-strategy-pipeline]

    G1{"Concept Gate<br/>机制假设 + 成立条件 + FMEA<br/>事前登记(评估标准/成功阈值)"}
    G2{"Spec Gate<br/>StrategySpec适配检查"}
    G3{"Coverage Gate<br/>不支持的作为research-only保留"}
    G4{"Pipeline Gate<br/>IS/OOS/Robustness通过"}

    H0 --> C0
    C0 --> G1
    G1 -->|Fail| H0
    G1 -->|Pass| S0
    S0 --> G2
    G2 -->|Fail| C0
    G2 -->|Pass| G3
    G3 -->|保留| C0
    G3 -->|export对象| P0
    P0 --> G4
    G4 -->|Fail| C0
    G4 -->|Pass| L0[晋升至Paper/Live]
```

### 1-3. 实现映射（当前仓库）

| 逻辑技能名 | 当前实现 |
|---|---|
| edge-hint-collector | `skills/edge-hint-extractor` |
| edge-concept-synth | `skills/edge-concept-synthesizer` |
| edge-strategy-export | `skills/edge-strategy-designer` + `skills/edge-candidate-agent` (`export_candidate.py` / `validate_candidate.py`) |

## 2. Edge的晋级状态（升学模型）

```mermaid
stateDiagram-v2
    [*] --> Hint
    Hint --> Ticket: 有观察依据
    Ticket --> Concept: 多个证据抽象化
    Concept --> Draft: 可规则化
    Draft --> Candidate: 可映射到v1 I/F
    Candidate --> Phase1Pass: validate + dry-run pass
    Phase1Pass --> BacktestPass: 期望值/稳定性 pass
    BacktestPass --> Paper: 纸面运营复现
    Paper --> LiveSmall: 小仓位实盘运营
    LiveSmall --> Live: 持续复现
    Live --> Monitor
    Monitor --> Concept: 劣化检测后重新设计
    Monitor --> Retired: 持续有显著劣化
```

## 3. 日/周运营节奏

```mermaid
flowchart TD
    subgraph Daily[Daily Loop]
        D1[更新观察数据] --> D2[生成hints]
        D2 --> D3[自动检测生成ticket]
        D3 --> D4[概念抽象化]
        D4 --> D5[更新策略草案]
    end

    subgraph Weekly[Weekly Review]
        W1[Concept Review<br/>采纳/保留/拒绝] --> W2[更新验证队列优先级]
        W2 --> W3[管道投入计划]
    end

    subgraph Monthly[Monthly Governance]
        M1[劣化监控审查] --> M2[现役Edge的继续/缩减/退役]
        M2 --> M3[更新假设库]
    end

    D5 --> W1
    W3 --> M1
```

## 4. 晋级门控的最低要求

| 门控 | 最低要求 | 不合格条件 |
|---|---|---|
| Concept Gate | thesis + invalidation_signals 已明确 | 假设仅为观察的改述 |
| Draft Gate | entry/exit/risk/cost 已定义 | 未考虑成本、不可实现条件 |
| Pipeline Gate | 满足 `edge-finder-candidate/v1` 契约 | schema违规、dry-run失败 |
| Promotion Gate | OOS中复现且可进行劣化监控 | 仅特定期间有效、容量不足 |

## 5. 首先关注的要点

1. `edge_concepts.yaml` 的 `abstraction.thesis` 和 `invalidation_signals`
2. `strategy_drafts/*.yaml` 的 `risk` 和 `validation_plan`
3. `validate_candidate.py` 结果（I/F适配）
4. 管道结果的可复现性（期间分割/regime分割）
