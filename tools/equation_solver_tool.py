import sympy as sp
import re
from core.base_tool import BaseTool
from typing import Any, Dict

class EquationSolverTool(BaseTool):
    def __init__(self):
        super().__init__("equation_solver", "Solves mathematical equations symbolically")
    
    async def execute(self, **kwargs) -> Any:
        equation = kwargs.get('equation', '')
        
        try:
            # Clean and parse equation
            cleaned_equation = self._clean_equation(equation)
            
            # Direct solve for simple linear equations like "2x + 5 = 11"
            if self._is_simple_linear(cleaned_equation):
                return self._solve_simple_linear(cleaned_equation)
                
            # Use sympy for more complex equations
            solution = self._solve_equation(cleaned_equation)
            return solution
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"Equation solving error: {str(e)}"
    
    def _clean_equation(self, equation: str) -> str:
        """Extract and clean the equation from the input text"""
        # Remove common prefixes
        equation = re.sub(r'(?i)solve\s*:?\s*', '', equation)
        equation = re.sub(r'(?i)equation\s*:?\s*', '', equation)
        equation = re.sub(r'(?i)find\s+x\s+in\s+', '', equation)
        
        # Look for equation patterns
        equation_pattern = r'([^=]+=[^=]+)'
        match = re.search(equation_pattern, equation)
        if match:
            return match.group(1).strip()
            
        return equation.strip()
    
    def _is_simple_linear(self, equation: str) -> bool:
        """Check if this is a simple linear equation we can solve directly"""
        # Check for equations like "ax + b = c" or "ax - b = c" or "ax = c"
        simple_patterns = [
            r'^\s*(\d+)\s*x\s*\+\s*(\d+)\s*=\s*(\d+)\s*$',  # ax + b = c
            r'^\s*(\d+)\s*x\s*-\s*(\d+)\s*=\s*(\d+)\s*$',   # ax - b = c
            r'^\s*(\d+)\s*x\s*=\s*(\d+)\s*$',               # ax = c
        ]
        
        return any(re.match(pattern, equation) for pattern in simple_patterns)
    
    def _solve_simple_linear(self, equation: str) -> str:
        """Solve simple linear equations directly for better reliability"""
        # For equations like "ax + b = c"
        match = re.match(r'^\s*(\d+)\s*x\s*\+\s*(\d+)\s*=\s*(\d+)\s*$', equation)
        if match:
            a, b, c = map(int, match.groups())
            x = (c - b) / a
            steps = [
                f"Starting with the equation: {a}x + {b} = {c}",
                f"Subtract {b} from both sides: {a}x = {c} - {b} = {c-b}",
                f"Divide both sides by {a}: x = {c-b}/{a} = {x}"
            ]
            return f"x = {x}\n\nSteps:\n" + "\n".join(steps)
        
        # For equations like "ax - b = c"
        match = re.match(r'^\s*(\d+)\s*x\s*-\s*(\d+)\s*=\s*(\d+)\s*$', equation)
        if match:
            a, b, c = map(int, match.groups())
            x = (c + b) / a
            steps = [
                f"Starting with the equation: {a}x - {b} = {c}",
                f"Add {b} to both sides: {a}x = {c} + {b} = {c+b}",
                f"Divide both sides by {a}: x = {c+b}/{a} = {x}"
            ]
            return f"x = {x}\n\nSteps:\n" + "\n".join(steps)
        
        # For equations like "ax = c"
        match = re.match(r'^\s*(\d+)\s*x\s*=\s*(\d+)\s*$', equation)
        if match:
            a, c = map(int, match.groups())
            x = c / a
            steps = [
                f"Starting with the equation: {a}x = {c}",
                f"Divide both sides by {a}: x = {c}/{a} = {x}"
            ]
            return f"x = {x}\n\nSteps:\n" + "\n".join(steps)
        
        return "Could not solve equation directly. Attempting advanced solution..."
    
    def _solve_equation(self, equation: str) -> str:
        """Solve equation using SymPy"""
        try:
            # Define symbol
            x = sp.Symbol('x')
            
            # Split equation by =
            if '=' in equation:
                left, right = equation.split('=', 1)
                # Create equation: left - right = 0
                eq = sp.sympify(left.strip()) - sp.sympify(right.strip())
            else:
                # Assume equation = 0
                eq = sp.sympify(equation)
            
            # Solve equation
            solutions = sp.solve(eq, x)
            
            if solutions:
                if len(solutions) == 1:
                    return f"x = {solutions[0]}"
                else:
                    solution_text = ", ".join([f"x_{i+1} = {sol}" for i, sol in enumerate(solutions)])
                    return f"Multiple solutions: {solution_text}"
            else:
                return "No solution found"
                
        except Exception as e:
            # Fallback for parsing errors
            return f"Could not solve with SymPy: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "equation": {
                    "type": "string",
                    "description": "Mathematical equation to solve (e.g., '2x + 5 = 11')"
                }
            }
        }
