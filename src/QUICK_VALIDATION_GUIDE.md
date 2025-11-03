# AI Battle Mode - 快速验收指南

## 🚀 快速开始

### 1. 运行游戏
```bash
cd src
python3 main.py
```

### 2. 选择AI模式
1. 弹出 "Play against AI?" 窗口时，选择 **"Yes"**
2. 选择 **"Single AI"** 模式
3. 选择AI难度：
   - **Easy** - 快速随机移动 (< 1秒)
   - **Medium** - 平衡的角落策略 (< 3秒)
   - **Hard** - 高级战略思考 (< 6秒)
4. 点击 **"Start Game"**

### 3. 验证游戏流程
✅ **检查清单**:
- [ ] Human玩家（Player 1）可以正常选择和放置棋子
- [ ] AI玩家显示为 "AI (EASY/MEDIUM/HARD)"
- [ ] 轮到AI时显示 **"AI thinking..."** 指示器
- [ ] AI自动放置棋子或跳过回合
- [ ] 回合自动传递给下一个玩家
- [ ] 游戏可以完整进行10轮以上
- [ ] 没有错误或卡死现象

## 🧪 自动化测试

### 运行所有AI相关测试
```bash
cd src
python3 -m pytest ../tests/unit/test_ai_strategy.py -v
python3 -m pytest ../tests/unit/test_ai_player.py -v
python3 -m pytest ../tests/unit/test_game_mode.py -v
python3 -m pytest ../tests/unit/test_ai_performance.py -v
python3 -m pytest ../tests/integration/test_single_ai.py -v
```

### 预期结果
- ✅ 所有测试通过
- ✅ 没有错误或失败

## 📊 性能检查

### Easy AI (RandomStrategy)
- 平均计算时间: **< 0.5秒**
- 超时限制: **3秒**

### Medium AI (CornerStrategy)
- 平均计算时间: **< 2秒**
- 超时限制: **5秒**

### Hard AI (StrategicStrategy)
- 平均计算时间: **< 5秒**
- 超时限制: **8秒**

## 🔍 常见问题

### Q: AI不移动怎么办？
**A**: 检查是否有有效的移动位置。如果没有，AI应该跳过回合。

### Q: 游戏卡在AI回合？
**A**: 检查 "AI thinking..." 指示器。如果超过8秒，可能是超时问题。

### Q: AI放置无效棋子？
**A**: 这不应该发生。如果发生，说明Blokus规则验证器有问题。

### Q: 如何测试不同难度？
**A**: 重新启动游戏，每次选择不同的难度级别。

## ✅ 验收标准

### 必须满足 (100%)
1. **T033**: AI始终做出有效移动
2. **T034**: AI计算在超时内完成
3. **T035**: 完整游戏流程正常工作

### 理想表现
- AI计算时间在平均范围内
- UI响应流畅
- 没有内存泄漏

## 📁 重要文件

### 核心实现
- `src/services/ai_strategy.py` - AI策略
- `src/models/ai_player.py` - AI玩家
- `src/models/game_mode.py` - 游戏模式
- `src/main.py` - 游戏初始化

### 测试文件
- `tests/unit/test_ai_strategy.py` - AI策略测试
- `tests/unit/test_ai_player.py` - AI玩家测试
- `tests/unit/test_ai_performance.py` - 性能测试
- `tests/integration/test_single_ai.py` - 集成测试

### 文档
- `docs/AI_BATTLE_MODE验收指南.md` - 完整验收指南
- `PHASE_3_COMPLETION_SUMMARY.md` - 完成总结

## 🎯 成功指标

### 手动验收
- [ ] 成功启动游戏
- [ ] 成功选择AI模式
- [ ] 成功完成一局游戏
- [ ] 所有AI移动有效
- [ ] AI计算在超时内完成

### 自动化测试
- [ ] 所有单元测试通过 (100%)
- [ ] 所有集成测试通过 (100%)
- [ ] 性能测试在限制内 (100%)

## 🔄 后续阶段

完成Phase 3后，可以继续：
- **Phase 4**: Three AI Mode (1 Human + 3 AI)
- **Phase 5**: Difficulty Settings (动态难度)
- **Phase 6**: Spectate Mode (观战模式)
- **Phase 7**: Polish & Testing

---

**Phase 3 - User Story 1 (Single AI Mode) 已完成！** ✅

所有35个任务已实现和测试。
项目现在具备完整的AI对战功能！
