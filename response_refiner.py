def refine_response(response: str, intent: str) -> str:
    """
    Refines the AI's response based on the intent.

    Args:
        response (str): The AI's raw response.
        intent (str): The classified intent of the user's prompt.

    Returns:
        str: The refined response.
    """
    if intent == 'coding':
        # Basic code formatting (e.g., fix indentation)
        # This is a placeholder for a more sophisticated implementation
        lines = response.split('\n')
        refined_lines = []
        indentation_level = 0
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('}'):
                indentation_level -= 1
            
            refined_lines.append('    ' * indentation_level + stripped_line)

            if stripped_line.endswith('{'):
                indentation_level += 1
        
        return '\n'.join(refined_lines)

    return response.strip()
