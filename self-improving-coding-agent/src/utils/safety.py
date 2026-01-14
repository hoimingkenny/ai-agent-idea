import ast
from typing import Tuple, Set

class Safety:
    """
    Static analysis to prevent dangerous code execution before it reaches the sandbox.
    """
    BLACKLIST_IMPORTS: Set[str] = {"os", "subprocess", "sys", "shutil", "builtins", "importlib"}
    BLACKLIST_CALLS: Set[str] = {"exec", "eval", "open", "compile"}

    @staticmethod
    def check(code: str) -> Tuple[bool, str]:
        """
        Analyzes the code for banned imports and function calls.
        Returns (True, "Safe") if checks pass, otherwise (False, reason).
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"

        for node in ast.walk(tree):
            # Check for imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Check if the root module is blacklisted
                    root_module = alias.name.split('.')[0]
                    if root_module in Safety.BLACKLIST_IMPORTS:
                        return False, f"Importing '{alias.name}' is not allowed."
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_module = node.module.split('.')[0]
                    if root_module in Safety.BLACKLIST_IMPORTS:
                        return False, f"Importing from '{node.module}' is not allowed."
            
            # Check for calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in Safety.BLACKLIST_CALLS:
                        return False, f"Calling '{node.func.id}' is not allowed."
                # Check for calls like os.system() (Attribute)
                elif isinstance(node.func, ast.Attribute):
                    # This is harder to track perfectly without type inference, 
                    # but we can block known dangerous methods if we wanted.
                    # For now, we rely on blocking the import of the module.
                    pass

        return True, "Safe"
