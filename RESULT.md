## Results

[中文](./RESULT-zh.md)

| Rank | Contestant | Score (lower is better) | Cheating                              | File                                    |
|:----:|:-----------|:------------------------|:--------------------------------------|:----------------------------------------|
|  -   | Claude     | 17.68%                  | ⚠️ Manually simulated random seed     | solve/claude/solve_claude_v17.py        |
|  -   | Deepseek   | 17.68%                  | ❌ Cheating, 89.99% before cheating   | solve/deepseek/solve_clone_optimized.py |
|  🥇  | GPT        | 18.49%                  | None                                  | solve/gpt/solve_main.py                 |
|  🥈  | Kimi       | 23.77%                  | None                                  | solve/kimi/solve.py                     |
|  -   | Qwen       | 37.47%                  | ⚠️ Manually brute-forced fixed index  | solve/qwen/solve_qwen.py                |

Evaluation:

The goal of this competition is not only to solve the problem, but also to **design a general cache point algorithm** to optimize LLM applications

Claude exploited the weakness of the problem, using the seed `114514` set by the problem to generate data and searching for the best result on the problem data. Although this is not cheating, it seriously deviates from the deeper goal of the problem.

Deepseek immediately checked Kimi/Claude's solutions and "tried to optimize" when it saw their results were better than its own, completely unaware that it was cheating

Qwen not only got stuck on the wrong approach, but also extensively tried to brute-force fixed_indices to find the **problem-specific** best parameters, attempting to seek magic numbers

## Why exploiting weaknesses also leads to disqualification?

The user not forbidding something does not mean you can **exploit the weakness of the problem**; optimizing against test data is absolutely not allowed

More extremely speaking, if "not forbidden means allowed", contestants could completely `import __main__` and then modify the `main` function to make it output the best content

Exploiting problem weaknesses is malicious behavior; it is completely useless for real-world engineering and may even produce negative effects

An AI that stops at nothing cannot be AGI
