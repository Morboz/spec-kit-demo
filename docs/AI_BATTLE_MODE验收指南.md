# AI Battle Mode 验收指南

## 概述

本文档提供AI对战模式的完整验收测试指南，用于验证Phase 3 (User Story 1 - Single AI Mode)的实现是否满足要求。

## 验收标准

### T033: AI makes valid moves 100% of the time
**目标**: 验证AI玩家100%的时间都做出有效移动，不违反规则

**测试方法**:
1. 启动游戏，选择"Single AI"模式
2. 观察AI移动，验证：
   - AI移动位置在棋盘范围内
   - AI不会将棋子放在已有棋子的位置
   - AI遵循角落连接规则（首次移动必须在角落）
   - AI不与同色棋子边缘相邻
3. 进行至少10轮完整游戏
4. 验证0次规则违规

**通过标准**: AI在整个游戏过程中从未做出无效移动

### T034: AI move calculation completes within timeout limits
**目标**: 验证AI移动计算在超时限制内完成

**测试方法**:
1. 启动游戏，观察AI思考状态
2. 测量AI计算时间：
   - Easy (RandomStrategy): 应在3秒内完成
   - Medium (CornerStrategy): 应在5秒内完成
   - Hard (StrategicStrategy): 应在8秒内完成
3. 多次测试不同难度级别
4. 验证超时情况下AI不会卡死

**通过标准**:
- Easy: 平均 < 0.5秒，最大 3秒
- Medium: 平均 < 2秒，最大 5秒
- Hard: 平均 < 5秒，最大 8秒

### T035: Complete game flow from start to finish in Single AI mode
**目标**: 验证Single AI模式可以完整进行从开始到结束的游戏

**测试步骤**:

#### 步骤1: 启动游戏
```bash
cd src
python3 main.py
```

#### 步骤2: 选择AI模式
1. 点击"Yes"选择AI对战模式
2. 选择"Single AI"模式
3. 选择AI难度级别（Easy/Medium/Hard）
4. 点击"Start Game"

#### 步骤3: 验证游戏设置
**检查列表**:
- [ ] 游戏显示2个玩家：Human 和 AI (难度)
- [ ] Human玩家位置：Player 1
- [ ] AI玩家位置：Player 3
- [ ] Human玩家可以正常选择和放置棋子
- [ ] AI玩家名称显示为"AI (EASY)"、"AI (MEDIUM)"或"AI (HARD)"

#### 步骤4: 验证人类玩家回合
1. 选择一个棋子
2. 点击棋盘放置
3. 验证：
   - [ ] 棋子正确放置
   - [ ] 得分更新
   - [ ] 棋子从库存中移除
   - [ ] 回合自动传递给AI

#### 步骤5: 验证AI玩家回合
1. 观察"AI thinking..."指示器出现
2. 等待AI计算完成（使用秒表计时）
3. 验证：
   - [ ] "AI thinking..."指示器消失
   - [ ] AI自动放置棋子或选择跳过
   - [ ] 棋盘正确更新
   - [ ] 得分正确更新
   - [ ] 回合传递给下一个玩家

#### 步骤6: 重复回合循环
1. 重复步骤4-5至少10轮
2. 验证：
   - [ ] 每次AI回合都能完成
   - [ ] 没有错误或卡死
   - [ ] 游戏流程顺畅

#### 步骤7: 验证AI行为差异（不同难度）
**测试Easy难度**:
- [ ] AI移动相对随机
- [ ] 计算时间 < 1秒

**测试Medium难度**:
- [ ] AI优先角落连接
- [ ] 计算时间 < 3秒

**测试Hard难度**:
- [ ] AI显示战略思考
- [ ] 计算时间 < 6秒

#### 步骤8: 游戏结束验证
游戏可能因以下情况结束：
1. 所有玩家都跳过回合
2. 所有玩家都放置完所有棋子

验证：
- [ ] 游戏正确检测结束条件
- [ ] 显示最终得分
- [ ] 正确宣布获胜者（最高分）

#### 步骤9: 错误处理
**测试场景**:
1. AI无法找到有效移动时应该跳过
2. 连续多次运行游戏不应有内存泄漏
3. 取消游戏选择应正确返回主菜单

## 自动化测试

### 运行单元测试
```bash
cd src
python3 -m pytest ../tests/unit/test_ai_strategy.py -v
python3 -m pytest ../tests/unit/test_ai_player.py -v
python3 -m pytest ../tests/unit/test_game_mode.py -v
python3 -m pytest ../tests/unit/test_ai_performance.py -v
```

### 运行集成测试
```bash
cd src
python3 -m pytest ../tests/integration/test_single_ai.py -v
python3 -m pytest ../tests/integration/test_ai_basic.py -v
```

### 预期测试结果
- 所有单元测试通过
- 所有集成测试通过
- 性能测试在超时限制内

## 性能基准

| 指标 | Easy | Medium | Hard |
|------|------|--------|------|
| 平均计算时间 | < 0.5秒 | < 2秒 | < 5秒 |
| 最大超时 | 3秒 | 5秒 | 8秒 |
| 内存使用 | 稳定 | 稳定 | 稳定 |
| CPU使用 | < 50% | < 70% | < 90% |

## 已知限制

1. AI策略可能不是最优的，但应该有效
2. 在复杂位置，Hard AI可能需要更长时间
3. 某些边缘情况下AI可能选择跳过

## 故障排除

### 问题1: AI不移动
**症状**: "AI thinking..."显示但不放置棋子
**解决**: 检查AI是否因无可用移动而正确跳过

### 问题2: AI移动无效
**症状**: AI放置违反规则的棋子
**解决**: 检查Blokus规则验证器是否正确工作

### 问题3: 游戏卡死
**症状**: AI计算超过超时限制
**解决**: AI策略可能需要优化，检查超时处理机制

### 问题4: UI不更新
**症状**: AI放置后棋盘不刷新
**解决**: 检查UI更新回调是否正确触发

## 验收检查清单

### 功能性
- [ ] 可以选择Single AI模式
- [ ] 可以选择AI难度
- [ ] AI玩家正确显示
- [ ] 人类玩家可以正常游戏
- [ ] AI自动回合工作
- [ ] AI思考指示器显示
- [ ] 游戏可以完整进行
- [ ] 游戏正确结束
- [ ] 最终得分正确

### 质量
- [ ] AI移动100%有效
- [ ] AI计算在超时内完成
- [ ] 没有内存泄漏
- [ ] UI响应流畅
- [ ] 错误处理正确

### 性能
- [ ] Easy AI: < 0.5秒平均
- [ ] Medium AI: < 2秒平均
- [ ] Hard AI: < 5秒平均
- [ ] 无超时错误

### 测试
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 性能测试通过
- [ ] 手动验收测试通过

## 总结

完成Phase 3后，应该有一个功能完整的Single AI模式，允许玩家与AI进行完整的Blokus游戏。AI应该能够：
1. 自动进行回合
2. 在合理时间内计算移动
3. 做出有效的移动
4. 遵循所有游戏规则

验收标准应满足：
- T033: ✓ AI移动100%有效
- T034: ✓ AI计算在超时内完成
- T035: ✓ 完整游戏流程工作

## 下一步

完成Phase 3后，可以继续：
- Phase 4: User Story 2 (Three AI Mode)
- Phase 5: User Story 3 (Difficulty Settings)
- Phase 6: User Story 4 (Spectate Mode)
- Phase 7: Polish & Cross-Cutting Concerns
