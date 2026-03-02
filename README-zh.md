# Budget Your Token

## 介绍

Agent 算法能力测试项目，旨在评估 Agent 的算法优化能力

Agent 需要编写一个算法控制 LLM 的上下文缓存，从而节省 Agent 应用自己的费用消耗

## 结果

详细结果见[RESULT.md](./RESULT.md)和[AI 总结](./SUMMERIZATION.md)

| 排名 | 选手     | 成绩（越低越好） | 作弊                   | 文件                                    |
| :--: | :------- | :--------------- | :--------------------- | :-------------------------------------- |
|  -   | Claude   | 17.68%           | ⚠️ 手动模拟随机种子    | solve/claude/solve_claude_v17.py        |
|  -   | Deepseek | 17.68%           | ❌ 作弊，作弊前 89.99% | solve/deepseek/solve_clone_optimized.py |
|  🥇  | GPT      | 18.49%           | 无                     | solve/gpt/solve_main.py                 |
|  🥈  | Kimi     | 23.77%           | 无                     | solve/kimi/solve.py                     |
|  -   | Qwen     | 37.47%           | ⚠️ 手动爆破固定索引    | solve/qwen/solve_qwen.py                |

## 比赛环境

每个 Agent 需要在`solve/<LLM名字>`中编写`solve_*.py`完成算法，并使用`challenge.py`测试算法效率

Agent 可以用`challenge.py`测试其他 Agent 的算法以检查自己是否领先，但**被禁止**查看其他人的算法

比赛共四个小时，提前暂停的 Agent 会被提醒重新检查自己是否领先

参赛 Agent 有:

- deepseek: DeepSeek v3.2
- kimi: Kimi K2.5
- qwen: Qwen 3.5 Plus
- gpt: GPT 5.3 Codex (OpenRouter)
- claude: Claude Opus 4.6 (OpenRouter)

Agent 应用为[LinHai](https://github.com/Marven11/LinHai)

## 赛题 Prompt

[赛题 README.md](./challenge-README.md)

[任务介绍](./TASK.md)

## 许可证

MIT
