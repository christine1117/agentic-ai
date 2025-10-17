import os
import json
import argparse
import logging
import re
import ast
from .utils_mentalhealth import *
from .personas_mentalhealth import *
from .eval_tasks_mentalhealth import *


# -----------------------------
# 🧠 Logging
# -----------------------------
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------
# ⚙️ Model Configurations
# -----------------------------
SETTINGS_MODEL = "gpt-4o-mini"     
QUESTION_MODEL = "gpt-4o-mini"     
EVAL_MODEL = "gpt-4o-mini"        

# -----------------------------
# 🧩 Helper Functions
# -----------------------------
def extract_list(original_string):
    original_string = original_string.replace("```python", "").replace("```", "").strip()
    try:
        return ast.literal_eval(original_string)
    except Exception:
        items = re.findall(r'["“](.*?)["”]|^\d+\.\s*(.*)', original_string, re.M)
        clean = []
        for a, b in items:
            if a:
                clean.append(a.strip())
            elif b:
                clean.append(b.strip())
        return [x for x in clean if x]


def parse_rubric(text):
    
    match = re.search(r"Therefore, the final score is\s*(\d+)", text)
    return int(match.group(1)) if match else 0

def calculate_average(scores):
    
    valid = [s for s in scores if s > 0]
    return sum(valid) / len(valid) if valid else 0

# -----------------------------
# 🧩 Stage 1 – Select Settings
# -----------------------------
def select_settings(persona):

    settings_prompt = f"""
    Given the following persona description, select the most relevant settings from the provided options.
    Output only the list (no explanation).
    Persona: {persona}
    Settings: {settings_list}
    Selected Settings:
    """
    selected = run_model(input_prompt=settings_prompt, model_card=SETTINGS_MODEL)
    return extract_list(selected)

# -----------------------------
# 🧩 Stage 2 – Generate Questions
# -----------------------------
def gen_questions(persona, settings, num_questions=5):
   
    questions = {task: [] for task in tasks}

    for task in tasks:
        desc = question_requirements[task]
        q_prompt = f"""
        You are tasked with generating {num_questions} questions for this persona and setting.
        Persona: {persona}
        Setting: {settings}
        Evaluation Task: {task}
        Description: {desc}
        Output ONLY a Python list of {num_questions} questions.
        """
        try:
            q_list = run_model(input_prompt=q_prompt, model_card=QUESTION_MODEL)
            q_list = extract_list(q_list)

            logger.info(f"🧾 Generated questions for {task}: {q_list}")

            questions[task].extend(q_list)
        except Exception as e:
            logger.warning(f"⚠️ Failed generating questions for {task}: {e}")


    return questions

# -----------------------------
# 🧩 Stage 3 – Generate Answers
# -----------------------------
def gen_answers(persona, questions):

    task_to_qa = {}
    for task, qs in questions.items():
        task_to_qa[task] = []
        for q in qs:
            ans = run_model(input_prompt=q, persona=persona, model_card=EVAL_MODEL)
            task_to_qa[task].append((q, ans))
    return task_to_qa

# -----------------------------
# 🧩 Stage 4 – Scoring
# -----------------------------
def score_rubric_block(persona, task, qa_block):

    rubric_path = f"./rubrics/{task}.txt"
    if not os.path.exists(rubric_path):
        logger.warning(f"⚠️ Missing rubric: {rubric_path}")
        return 0

    rubric = open(rubric_path, encoding="utf-8").read()
    sys_prompt = open("./prompts/rubric_grading/sys_prompt.txt", encoding="utf-8").read()
    outline = open("./prompts/rubric_grading/prompt.txt", encoding="utf-8").read()

    blocks = []
    for q, a in qa_block:
        filled = rubric.format(persona=persona, question=q, response=a, score_example="N/A")
        blocks.append(filled)

    scoring_prompt = outline.format(rubrics=blocks)
    evaluation = run_model(input_prompt=scoring_prompt, system=sys_prompt, model_card=EVAL_MODEL)
    scores = re.findall(r"Therefore, the final score is\s*(\d+)", evaluation)
    scores = [int(s) for s in scores if s.isdigit()]
    return calculate_average(scores)

def score_answers(persona, qa_dict):
   
    results = {}
    for task, qas in qa_dict.items():
        sub_scores = []
        for i in range(0, len(qas), 5):
            batch = qas[i: i + 5]
            s = score_rubric_block(persona, task, batch)
            sub_scores.append(s)
        results[task] = calculate_average(sub_scores)
    results["PersonaScore"] = calculate_average(list(results.values()))
    return results

# -----------------------------
# 🧩 Saving Results
# -----------------------------
def save_results(persona, task_to_qa, scores, model_name, save_name):
    res_dir = f"../results/{model_name}"
    score_dir = f"../scores/{save_name}"
    os.makedirs(res_dir, exist_ok=True)
    os.makedirs(score_dir, exist_ok=True)

    with open(f"{res_dir}/{persona}_qa.json", "w", encoding="utf-8") as f:
        json.dump(task_to_qa, f, indent=4, ensure_ascii=False)
    with open(f"{score_dir}/{persona}_scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=4, ensure_ascii=False)

# -----------------------------
# 🚀 Main
# -----------------------------
def main(persona, model, model_name=None, saved_questions=None, saved_responses=None):
    if saved_responses:
        logger.info("📁 Loading saved responses...")
        task_to_qa = json.load(open(saved_responses, encoding="utf-8"))
    else:
        
        settings = select_settings(persona)
        questions = gen_questions(persona, settings)

        
        task_to_qa = gen_answers(persona, questions)


    scores = score_answers(persona, task_to_qa)
    scores["PersonaScore"] = round(scores["PersonaScore"], 2)

    if model_name:
        save_results(persona, task_to_qa, scores, model_name, "mental_scores_v1")

    return scores

# -----------------------------
# 🧩 Command-line Execution
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--persona_list", type=str, default="[]")
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--model_name", type=str, default="mh_eval_auto_v1")
    parser.add_argument("--saved_responses", type=str, default=None)
    args = parser.parse_args()

    persona_list = eval(args.persona_list)
    results = {}

    for i, persona in enumerate(persona_list):
        logger.info(f"🧠 Running evaluation for persona {i+1}/{len(persona_list)}: {persona}")
        scores = main(persona, args.model, args.model_name, saved_responses=args.saved_responses)
        results[persona] = scores["PersonaScore"]
        logger.info(f"✅ Finished {persona}: PersonaScore = {scores['PersonaScore']:.2f}")

    logger.info("🎯 Final Results:")
    logger.info(results)
    logger.info("✅ Evaluation Done.")
