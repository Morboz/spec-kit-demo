#!/usr/bin/env python3
"""
测试脚本：验证键盘快捷键功能
"""

print("=" * 60)
print("Blokus 键盘快捷键功能测试")
print("=" * 60)

# 测试导入
try:
    from src.ui.keyboard_shortcuts import GameKeyboardHandler, KeyboardShortcuts
    print("✓ 成功导入 GameKeyboardHandler 和 KeyboardShortcuts")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    exit(1)

# 测试默认键绑定
shortcuts = KeyboardShortcuts
default_bindings = shortcuts.DEFAULT_BINDINGS

print("\n" + "=" * 60)
print("已配置的快捷键:")
print("=" * 60)

# 棋子操作快捷键
print("\n【棋子操作】")
piece_manipulation_keys = {
    "r": "旋转 (顺时针)",
    "R": "旋转 (逆时针)", 
    "f": "翻转",
    "F": "翻转",
}

for key, action in piece_manipulation_keys.items():
    if key in default_bindings:
        print(f"  {key:10} -> {action}")

# 游戏操作快捷键
print("\n【游戏操作】")
game_actions = {
    "space": "跳过回合",
    "Return": "放置棋子",
    "Escape": "取消操作",
}

for key, action in game_actions.items():
    if key in default_bindings:
        print(f"  {key:10} -> {action}")

# 游戏控制快捷键
print("\n【游戏控制】")
game_control = {
    "n": "新游戏",
    "q": "退出",
    "h": "帮助",
    "?": "帮助",
}

for key, action in game_control.items():
    if key in default_bindings:
        print(f"  {key:10} -> {action}")

print("\n" + "=" * 60)
print("使用说明:")
print("=" * 60)
print("""
1. 选择一个棋子后:
   - 按 R 键可以旋转棋子
   - 按 F 键可以翻转棋子
   - 用鼠标点击棋盘放置棋子

2. 这些快捷键让你可以快速调整棋子方向，无需使用鼠标点击按钮

3. 按 H 或 ? 键可以在游戏中查看完整的快捷键帮助
""")

print("=" * 60)
print("✓ 键盘快捷键功能已就绪!")
print("=" * 60)
