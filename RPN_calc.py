#!/bin/python3.10
# REQUIRES 3.10 (I can rewrite it for lower versions, but it's uglier) ({and a hard cap of 3.7.x enforced by __future__})
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass


class Operator(Enum):
    Add = "+"
    Sub = "-"
    Mul = "*"
    Div = "/"
    Mod = "%"
    Pow = "^"

    def evaluate(self, operand1: float, operand2: float) -> float:
        match self:
            case self.Add:
                return operand1 + operand2
            case self.Sub:
                return operand1 - operand2
            case self.Mul:
                return operand1 * operand2
            case self.Div:
                return operand1 / operand2
            case self.Mod:
                return operand1 % operand2
            case self.Pow:
                return pow(operand1, operand2)
            case _:
                raise ValueError("Invalid operation")

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


@dataclass
class Variable:
    char: str
    id: int


class Function:
    name: str
    vars: list[Variable]
    tokens: list[Operator | float | Function | Variable]

    def __init__(self, name, vars, tokens):
        self.name = name
        self.vars = vars
        self.tokens = tokens

    def evaluate(self, var_bindings: list[float]) -> float:
        if len(var_bindings) != len(self.vars):
            raise ValueError("Not all variables bound")

        stack = []
        for t in self.tokens:
            if isinstance(t, Variable):
                stack.append(var_bindings[t.id])
            elif isinstance(t, float):
                stack.append(t)
            elif isinstance(t, Function):
                num_args = len(self.func_map[t.name].vars)
                if len(stack) < num_args:
                    raise ValueError(f"Too few arguments for function {t.name}, \
                            expected {num_args} found {len(stack)}")
                stack.append(t(stack[-num_args:]))
            elif isinstance(t, Operator):
                if len(stack) < 2:
                    raise ValueError("Insufficient operands for operator")
                stack.append(t.evaluate(stack.pop(-2), stack.pop()))
            else:
                raise ValueError(f"Unrecognised token {t}")
        if len(stack) > 1:
            raise ValueError("Untreated operands, maybe missing an operator?")
        elif len(stack) == 0:
            raise ValueError("No return value")
        return stack.pop()

    # QoL func
    def __call__(self, *args):
        return self.evaluate(*args)

    def parse(expr: str, func_map: dict[str, Function]) -> Function | None:
        def tokenise_func_expr(expr: str, vars: list[str], func_map: dict[str, Function]) -> list[Operator | float | Function | Variable]:
            tokens = []
            for t in expr.split():
                if t in func_map.keys():
                    tokens.append(func_map[t])
                elif t in vars:
                    idx = vars.index(t)
                    tokens.append(Variable(t, idx))
                else:
                    try:
                        tokens.append(Operator(t))
                        continue
                    except ValueError:
                        pass
                    try:
                        tokens.append(float(t))
                    except ValueError:
                        raise ValueError(f"Could not parse symbol {t}")
            return tokens

        spl = expr.split(':')
        if len(spl) == 1:
            return None
        if len(spl) != 2:
            return ValueError(f"Expected one function definition at a time, found {len(spl)}")
        func_def = spl[0]
        func_expr = spl[1]
        (name, *args) = func_def.split()
        func_tokens = tokenise_func_expr(func_expr.strip(), args, func_map)
        return Function(name, args, func_tokens)


class Calculator:
    func_map: dict[str, Function]

    def __init__(self):
        self.func_map = {}

    def tokenise_expr(self, expr: str) -> list[Operator | float | Function]:
        tokens = []
        for t in expr.split():
            if t in self.func_map.keys():
                tokens.append(self.func_map[t])
            else:
                try:
                    tokens.append(Operator(t))
                    continue
                except ValueError:
                    pass
                try:
                    tokens.append(float(t))
                except ValueError:
                    raise ValueError(f"Could not parse symbol {t}")
        return tokens

    def eval_tokens(self, tokens: list[Operator | float | Function]) -> float:
        stack = []
        for t in tokens:
            if isinstance(t, float):
                stack.append(t)
            elif isinstance(t, Function):
                num_args = len(self.func_map[t.name].vars)
                if len(stack) < num_args:
                    raise ValueError(f"Too few arguments for function {t.name}, \
                            expected {num_args} found {len(stack)}")
                stack.append(t([stack.pop() for _ in range(num_args)]))
            elif isinstance(t, Operator):
                if len(stack) < 2:
                    raise ValueError("Insufficient operands for operator")
                stack.append(t.evaluate(stack.pop(-2), stack.pop()))
            else:
                raise ValueError(f"Unrecognised token {t}")
        if len(stack) > 1:
            raise ValueError("Untreated operands, maybe missing an operator?")
        elif len(stack) == 0:
            raise ValueError("No return value")
        return stack.pop()

    def eval_expr(self, expr: str) -> str:
        function = Function.parse(expr, self.func_map)
        if function is not None:
            self.func_map[function.name] = function
            return f"Registered function: {function.name}"
        else:
            tokens = self.tokenise_expr(expr)
            return str(self.eval_tokens(tokens))


if __name__ == '__main__':
    c = Calculator()
    while True:
        try:
            i = input(">>> ")
            if "\x04" in i:
                break
            print(c.eval_expr(i))
        except ValueError as e:
            print("ERROR:", e.args[0])
