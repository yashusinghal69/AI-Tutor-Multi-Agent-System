import re
import math
from core.base_tool import BaseTool
from typing import Any, Dict

class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__("calculator", "Performs mathematical calculations and evaluates expressions")
    
    async def execute(self, **kwargs) -> Any:
        expression = kwargs.get('expression', '')
        
        if not expression or expression.isspace():
            return "No expression provided"
            
        try:
            # Clean and prepare expression
            clean_expr = self._clean_expression(expression)
            
            if not clean_expr or clean_expr.isspace():
                return "Could not extract a valid mathematical expression"
                
            # Safe evaluation with limited scope
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "sqrt": math.sqrt, "log": math.log, "exp": math.exp,
                "pi": math.pi, "e": math.e, "pow": pow
            }
            
            # Replace ^ with ** for exponentiation
            clean_expr = clean_expr.replace('^', '**')
            
            # Try to evaluate
            result = eval(clean_expr, {"__builtins__": {}}, allowed_names)
            return f"{clean_expr} = {result}"
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"Calculation error: {str(e)}"
    
    def _clean_expression(self, expr: str) -> str:
        # Extract mathematical expressions from natural language
        # Specific handling for common patterns
        if "f(x)" in expr and "=" in expr:
            # Extract function definition
            match = re.search(r'f\(x\)\s*=\s*(.+)', expr)
            if match:
                expr = match.group(1)
        
        # Replace word operators with symbols
        expr = expr.replace('plus', '+').replace('minus', '-')
        expr = expr.replace('times', '*').replace('divided by', '/')
        expr = expr.replace('x', '*').replace('X', '*')  # Common mistake: x as multiplication
        
        # Handle implicit multiplication
        expr = re.sub(r'(\d)\s*\(\s*(\d)', r'\1*(\2', expr)  # 2(3) -> 2*(3)
        expr = re.sub(r'\)\s*(\d)', r')*\1', expr)  # (3)2 -> (3)*2
        
        # Find mathematical expressions
        math_pattern = r'[\d+\-*/().\s]+'
        matches = re.findall(math_pattern, expr)
        
        if matches:
            return matches[0].strip()
        
        # If no matches found, try to return the raw input as a last resort
        return expr.strip()
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            }
        }
