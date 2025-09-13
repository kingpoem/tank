# TankGame

## Env Create

在 Win11 MacOS Archlinux 平台均可通过如下命令启动（在已经安装 poetry 的情况下）

win11 平台前置安装：
```shell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
scoop install poetry
```

```shell
git clone --depth=1 https://github.com/kingpoem/tank.git
cd tank
poetry env use 3.12
poetry install
poetry run tank
```
## Refactor

- poetry run black .
- poetry run isort .
- poetry run autoflake-clean
- poetry run tank

## 📄介绍

python = 3.12.7


使用`Python`库
- `pygame`
- `pymunk`
- `loguru`

## 操作说明

**主玩家**

- `WASD` 移动

- `G` 射击

**副玩家**

- `方向键` 移动

- `[0]` 射击

## 游戏道具类型

- ### 幽灵武器道具

    幽灵武器，子弹穿墙并在飞行过程中加速

