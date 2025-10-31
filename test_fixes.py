#!/usr/bin/env python3
"""
测试脚本：验证游戏状态和 UI 更新修复
"""

print("=" * 60)
print("Blokus 游戏状态和 UI 修复测试")
print("=" * 60)

# 测试 1: 游戏状态初始化
print("\n【测试 1: 游戏状态初始化】")
try:
    from src.game.game_setup import GameSetup
    from src.models.game_state import GamePhase
    
    setup = GameSetup()
    game_state = setup.setup_game(
        num_players=4,
        player_names=["Alice", "Bob", "Charlie", "Diana"]
    )
    
    print(f"✓ 游戏创建成功")
    print(f"  - 玩家数量: {game_state.get_player_count()}")
    print(f"  - 游戏阶段: {game_state.phase.name}")
    
    if game_state.phase == GamePhase.PLAYING:
        print(f"  ✓ 游戏已正确启动 (阶段: PLAYING)")
    else:
        print(f"  ✗ 游戏未启动 (阶段: {game_state.phase.name})")
        
    current_player = game_state.get_current_player()
    if current_player:
        print(f"  - 当前玩家: {current_player.name} (ID: {current_player.player_id})")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")

# 测试 2: PieceSelector 标题更新
print("\n【测试 2: PieceSelector 标题更新功能】")
try:
    from src.models.player import Player
    
    player1 = Player(player_id=1, name="Alice")
    player2 = Player(player_id=2, name="Bob")
    
    print(f"✓ 创建测试玩家:")
    print(f"  - {player1.name} (ID: {player1.player_id})")
    print(f"  - {player2.name} (ID: {player2.player_id})")
    
    # 检查 PieceSelector 是否有 title_var 属性
    import inspect
    from src.ui.piece_selector import PieceSelector
    
    # 检查 _create_widgets 方法
    source = inspect.getsource(PieceSelector._create_widgets)
    if "title_var" in source:
        print(f"  ✓ PieceSelector 已更新为使用 title_var")
    else:
        print(f"  ✗ PieceSelector 未使用 title_var")
    
    # 检查 set_player 方法
    source = inspect.getsource(PieceSelector.set_player)
    if "title_var.set" in source:
        print(f"  ✓ set_player 方法会更新标题")
    else:
        print(f"  ✗ set_player 方法未更新标题")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")

# 测试 3: CurrentPlayerIndicator 阶段检测
print("\n【测试 3: CurrentPlayerIndicator 阶段检测】")
try:
    from src.ui.current_player_indicator import CurrentPlayerIndicator
    import inspect
    
    source = inspect.getsource(CurrentPlayerIndicator.update_from_game_state)
    
    if "phase.value >= 2" in source or "PLAYING" in source:
        print(f"  ✓ CurrentPlayerIndicator 正确检查游戏阶段")
    else:
        print(f"  ✗ CurrentPlayerIndicator 未检查游戏阶段")
        
except Exception as e:
    print(f"✗ 测试失败: {e}")

print("\n" + "=" * 60)
print("修复内容总结:")
print("=" * 60)
print("""
修复 1: 游戏状态自动启动
--------------------------
- 在 game_setup.py 中，创建游戏后自动调用 start_game()
- 这会将游戏阶段从 SETUP 转换为 PLAYING
- 修复了 "Game not started" 的显示问题

修复 2: PieceSelector 标题动态更新
----------------------------------
- 将标题从静态 Label 改为使用 StringVar
- 在 set_player() 方法中更新标题文本
- 修复了玩家切换时标题不更新的问题

测试方法:
---------
1. 启动游戏
2. 选择 4 人游戏模式
3. 确认右上角显示的是当前玩家而不是 "Game not started"
4. 放置棋子后，确认左侧标题更新为下一个玩家的名字
""")

print("=" * 60)
print("✓ 测试完成!")
print("=" * 60)
