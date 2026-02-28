from typing import TypedDict, Callable, Optional
import copy
import random
import argparse
import importlib


random.seed(114514)

# 每百万Token价格
INPUT_TOKEN_PRICE_RMB = 0.8
OUTPUT_TOKEN_PRICE_RMB = 4.8
CACHED_INPUT_PRICE_RMB = 0.8 * 0.1
CACHED_WRITE_PRICE_RMB = 0.8 * 1.25


class Message(TypedDict):
    content: str
    role: str
    savepoint: bool


class ChatCompletionResult(TypedDict):
    cache_write_tokens: int
    cached_input_tokens: int
    input_tokens: int
    output: str


class Billing(TypedDict):
    cache_write_tokens: int
    cached_input_tokens: int
    input_tokens: int
    output_tokens: int


def is_content_equal(a: list[Message], b: list[Message]):
    return len(a) == len(b) and all(
        ax["content"] == bx["content"] and ax["role"] == bx["role"]
        for ax, bx in zip(a, b)
    )


def token_count(history: list[Message]):
    """为了简化算法题，我们简化为一个字符一个token"""
    return sum(len(message["content"]) for message in history)


def random_user_content() -> str:
    c = chr(random.randint(32, 127))
    if random.randint(1, 100) < 95:
        return c * random.randint(20, 100)
    else:
        return c * random.randint(500, 2000)


def calculate_consumption(billing: Billing):
    return (
        INPUT_TOKEN_PRICE_RMB * billing["input_tokens"]
        + OUTPUT_TOKEN_PRICE_RMB * billing["output_tokens"]
        + CACHED_WRITE_PRICE_RMB * billing["cache_write_tokens"]
        + CACHED_INPUT_PRICE_RMB * billing["cached_input_tokens"]
    ) / 1_000_000


class ApiProvider:
    def __init__(self):
        self.caches: list[list[Message]] = []
        self.caches.sort(key=len, reverse=True)
        self.billing = Billing(
            cache_write_tokens=0,
            cached_input_tokens=0,
            input_tokens=0,
            output_tokens=0,
        )

    def chat_completion_raw(self, history: list[Message]) -> ChatCompletionResult:
        if len([m for m in history if m["savepoint"]]) > 4:
            raise RuntimeError("Too many savepoint")
        cache_write_tokens = 0

        for i in range(len(history) - 1, -1, -1):
            if not history[i]["savepoint"]:
                continue

            if not any(
                is_content_equal(cached_history, history[: i + 1])
                for cached_history in self.caches
            ):
                self.caches.append(history[: i + 1])
                self.caches.sort(key=len, reverse=True)
                cache_write_tokens += token_count(history[: i + 1])
                continue

            cached_input_tokens = token_count(history[: i + 1])
            input_tokens = token_count(history[i + 1 :])
            return ChatCompletionResult(
                cache_write_tokens=cache_write_tokens,
                cached_input_tokens=cached_input_tokens,
                input_tokens=input_tokens,
                output="Example output of cache match",
            )

        return ChatCompletionResult(
            cache_write_tokens=cache_write_tokens,
            cached_input_tokens=0,
            input_tokens=token_count(history),
            output="Example output of matching no cache",
        )

    def chat_completion(
        self, history: list[Message]
    ) -> tuple[ChatCompletionResult, Billing]:
        result = self.chat_completion_raw(history)
        self.billing["cache_write_tokens"] += result["cache_write_tokens"]
        self.billing["cached_input_tokens"] += result["cached_input_tokens"]
        self.billing["input_tokens"] += result["input_tokens"]
        self.billing["output_tokens"] += len(result["output"])
        return result, self.billing.copy()


class LlmApplication:
    def __init__(
        self,
        optimizer: Callable[[list[Message]], list[Message]],
        billing_watcher: Callable[[Billing], None],
    ):
        self.history: list[Message] = [
            Message(
                role="system", content="Example System Prompt" * 500, savepoint=False
            )
        ]
        self.billing: Optional[Billing] = None
        self.api = ApiProvider()
        self.optimizer = optimizer
        self.billing_watcher = billing_watcher

    def run_application(self) -> tuple[Billing, float]:
        """一个简单的应用
        
        在上下文过长时清理上下文，这会导致部分savepoint被移动而失效
        
        每次调用optimizer时都deepcopy，这意味着每次都需要重新设置savepoint标志
        """
        for _ in range(3000):
            for _ in range(random.randint(1, 3)):
                self.history.append(
                    Message(role="user", content=random_user_content(), savepoint=False)
                )

            if token_count(self.history) > 128 * 1024:
                self.history = (
                    self.history[0:1]
                    + self.history[
                        int(len(self.history) * random.randint(40, 60) / 100) :
                    ]
                )
            optimized = self.optimizer(copy.deepcopy(self.history))
            assert is_content_equal(optimized, self.history)

            result, self.billing = self.api.chat_completion(optimized)
            self.billing_watcher(self.billing.copy())
            self.history.append(
                Message(role="assistant", content=result["output"], savepoint=False)
            )
        assert self.billing is not None
        return (self.billing.copy(), calculate_consumption(self.billing))


def main():
    parser = argparse.ArgumentParser(description="动态导入solve模块并调用solve函数")
    parser.add_argument("module_name", help="要导入的solve模块名称")

    args = parser.parse_args()

    module = importlib.import_module(args.module_name)

    app = LlmApplication(module.optimizer, module.billing_watcher)

    billing, consumption = app.run_application()

    comsumption_without_cache = calculate_consumption(
        Billing(
            cache_write_tokens=0,
            cached_input_tokens=0,
            input_tokens=billing["cached_input_tokens"] + billing["input_tokens"],
            output_tokens=billing["output_tokens"],
        )
    )

    print(
        f"你本次的测试结果为: 消耗{consumption:.2f}元，"
        f"为未使用缓存的{consumption / comsumption_without_cache * 100:.2f}%"
    )
    print(f"{billing=}")


if __name__ == "__main__":
    main()
