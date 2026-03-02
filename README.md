# Budget Your Token

[中文](./README-zh.md)

## Introduction

An Agent algorithm capability testing project, designed to evaluate the Agent's algorithm optimization capabilities

The Agent needs to write an algorithm to control the LLM's context cache, thereby saving costs for the Agent application itself

## Results

Detailed results can be found in [RESULT.md](./RESULT.md) and [AI Summary](./SUMMERIZATION.md)

| Rank | Contestant | Score (lower is better) | Cheating                             | File                                    |
| :--: | :--------- | :---------------------- | :----------------------------------- | :-------------------------------------- |
|  -   | Claude     | 17.68%                  | ⚠️ Manually simulated random seed    | solve/claude/solve_claude_v17.py        |
|  -   | Deepseek   | 17.68%                  | ❌ Cheating, 89.99% before cheating  | solve/deepseek/solve_clone_optimized.py |
|  🥇  | GPT        | 18.49%                  | None                                 | solve/gpt/solve_main.py                 |
|  🥈  | Kimi       | 23.77%                  | None                                 | solve/kimi/solve.py                     |
|  -   | Qwen       | 37.47%                  | ⚠️ Manually brute-forced fixed index | solve/qwen/solve_qwen.py                |

## Competition Environment

Each Agent needs to write a `solve_*.py` in `solve/<LLM name>` to complete the algorithm, and use `challenge.py` to test algorithm efficiency

Agents can use `challenge.py` to test other Agents' algorithms to check if they are leading, but are **forbidden** from viewing others' algorithms

The competition lasts four hours; Agents who pause early will be reminded to recheck if they are leading

Participating Agents:

- deepseek: DeepSeek v3.2
- kimi: Kimi K2.5
- qwen: Qwen 3.5 Plus
- gpt: GPT 5.3 Codex (OpenRouter)
- claude: Claude Opus 4.6 (OpenRouter)

The Agent application is [LinHai](https://github.com/Marven11/LinHai)

## Problem Prompt

[Problem README.md](./challenge-README.md)

[Task Introduction](./TASK.md)

## License

MIT
