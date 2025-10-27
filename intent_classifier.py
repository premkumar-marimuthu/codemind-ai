import re

def classify_intent(user_prompt):
    """
    Classifies the user's intent based on keywords in the prompt.

    Args:
        user_prompt (str): The user's input prompt.

    Returns:
        str: The classified intent (e.g., 'coding', 'writing', 'design').
    """
    prompt = user_prompt.lower()

    # Define keywords for each category
    coding_keywords = ['code', 'python', 'javascript', 'java', 'c++', 'debug', 'error', 'algorithm', 'function', 'class', 'method', 'variable', 'array', 'list', 'dict', 'map', 'object', 'instance', 'module', 'library', 'import', 'export', 'exception', 'bug', 'fix', 'test', 'refactor', 'optimize', 'performance']
    writing_keywords = ['write', 'edit', 'proofread', 'grammar', 'style', 'tone', 'document', 'explain', 'summarize', 'rephrase', 'paraphrase', 'translate', 'essay', 'report', 'article', 'blog', 'post', 'email', 'letter', 'resume', 'cv', 'cover letter', 'sentence', 'phrase']
    design_keywords = ['design', 'ui', 'ux', 'user interface', 'user experience', 'layout', 'color', 'font', 'wireframe', 'mockup', 'prototype', 'logo', 'icon', 'brand', 'style guide', 'mood board', 'user flow', 'journey map', 'persona', 'usability', 'accessibility']
    research_keywords = ['research', 'find', 'what is', 'who is', 'when is', 'where is', 'why is', 'how does', 'data', 'statistics', 'information', 'fact', 'source', 'citation', 'reference', 'study', 'paper', 'journal', 'article', 'book', 'author', 'expert', 'who was', 'what was', 'what are']
    strategy_keywords = ['plan', 'strategy', 'goal', 'risk', 'business', 'market', 'product', 'roadmap', 'vision', 'mission', 'values', 'objective', 'key result', 'okr', 'kpi', 'swot', 'pestle', 'porter', 'five forces', 'competitive analysis', 'market research', 'customer segmentation', 'value proposition', 'investment']
    empathy_keywords = ['feel', 'anxious', 'sad', 'stressed', 'relationship', 'friend', 'family', 'advice', 'listen', 'listener', 'understand', 'support', 'help', 'cope', 'deal with', 'manage', 'overcome', 'navigate', 'challenge', 'difficulty', 'problem', 'issue', 'concern', 'worry']

    # Check for keywords in the prompt
    if any(re.search(r'\b' + keyword + r'\b', prompt) for keyword in coding_keywords):
        return 'coding'
    if any(re.search(r'\b' + keyword + r'\b', prompt) for keyword in writing_keywords):
        return 'writing'
    if any(re.search(r'\b' + keyword + r'\b', prompt) for keyword in design_keywords):
        return 'design'
    if any(re.search(r'\b' + keyword + r'\b', prompt) for keyword in strategy_keywords):
        return 'strategy'
    if any(re.search(r'\b' + keyword + r'\b', prompt) for keyword in research_keywords):
        return 'research'
    if any(re.search(r'\b' + keyword + r'\b', prompt) for keyword in empathy_keywords):
        return 'empathy'

    return 'default'
