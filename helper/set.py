from typing import List

def escape_invalid_curly_brackets(text: str, valids: List[str]) -> str:
    """
    Escapes invalid curly brackets in the input text.

    Args:
        text (str): The input string containing curly brackets.
        valids (List[str]): A list of valid placeholders (without braces).

    Returns:
        str: The processed string with invalid curly brackets escaped.
    """
    new_text = []
    idx = 0
    valid_set = set(valids)  # Convert list to set for faster lookup
    
    while idx < len(text):
        if text[idx] == "{":
            # Handle double curly brackets "{{"
            if idx + 1 < len(text) and text[idx + 1] == "{":
                new_text.append("{{")
                idx += 2
                continue
            
            # Check for valid placeholders
            success = False
            for v in valid_set:
                placeholder = f"{{{v}}}"
                if text[idx:].startswith(placeholder):
                    new_text.append(placeholder)
                    idx += len(placeholder)
                    success = True
                    break
            
            # Escape invalid opening brace
            if not success:
                new_text.append("{{")
                idx += 1

        elif text[idx] == "}":
            # Handle double curly brackets "}}"
            if idx + 1 < len(text) and text[idx + 1] == "}":
                new_text.append("}}")
                idx += 2
                continue
            
            # Escape invalid closing brace
            new_text.append("}}")
            idx += 1

        else:
            # Add regular characters to the result
            new_text.append(text[idx])
            idx += 1

    return ''.join(new_text)

# Example usage
text = "Hello {user}, your balance is {{balance}}."
valids = ["user", "balance"]

result = escape_invalid_curly_brackets(text, valids)
print(result)  # Output: "Hello {user}, your balance is {{balance}}."
