import json
import ast
import operator
from difflib import get_close_matches


# --------------------------- Math Solver ---------------------------

# Allowed operators for safety
allowed_ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg
}


def safe_eval(node):
    """Safely evaluate math expression AST."""
    if isinstance(node, ast.Num):  # Numbers like 1, 2.5, etc
        return node.n

    if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
        return allowed_ops[type(node.op)](safe_eval(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
        return allowed_ops[type(node.op)](safe_eval(node.left), safe_eval(node.right))

    raise ValueError("Unsupported expression")

def solve_math_expression(expr: str):
    """Check if input is a math expression & solve it."""
    try:
        # Convert ^ (user exponent) into ** (python exponent)
        expr = expr.replace("^", "**")

        parsed = ast.parse(expr, mode='eval')
        return safe_eval(parsed.body)
    except Exception:
        return None


# --------------------------- KB Functions ---------------------------

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)


def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def find_best_match(user_question: str, questions: list) -> str | None:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None


def get_answer_for_question(question: str, knowledge_base: dict) -> str:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]


# --------------------------- Chat Bot ---------------------------

def chat_bot():
    knowledge_base = load_knowledge_base('knowledge_base.json')

    while True:
        user_input = input('You: ').strip()

        if user_input.lower() == 'quit':
            break

        # 1. Try solving math first
        math_result = solve_math_expression(user_input)
        if math_result is not None:
            print("Bot:", math_result)
            continue

        # 2. Try the knowledge base
        best_match = find_best_match(
            user_input,
            [q["question"] for q in knowledge_base["questions"]]
        )

        if best_match:
            answer = get_answer_for_question(best_match, knowledge_base)
            print("Bot:", answer)
            continue

        # 3. Ask to learn new answer if not known
        print("Bot: I don't know the answer. Can you teach me?")
        new_answer = input('Type the answer or "skip" to skip: ').strip()

        if new_answer.lower() == 'skip':
            print("Bot: Okay, maybe next time.")
            continue

        knowledge_base['questions'].append({
            "question": user_input,
            "answer": new_answer
        })

        save_knowledge_base('knowledge_base.json', knowledge_base)
        print('Bot: Thank you! I learned a new response!')


if __name__ == '__main__':
    chat_bot()