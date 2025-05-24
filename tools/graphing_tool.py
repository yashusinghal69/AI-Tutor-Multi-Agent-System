import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
import re
from core.base_tool import BaseTool
from typing import Any, Dict

class GraphingTool(BaseTool):
    def __init__(self):
        super().__init__("graphing", "Creates interactive graphs and visualizations for mathematical functions")
    
    async def execute(self, **kwargs) -> Any:
        function = kwargs.get('function', '')
        plot_type = kwargs.get('plot_type', 'auto')
        
        try:
            # Clean the function string to extract the actual function
            clean_function = self._clean_function(function)
            
            # Create the appropriate graph
            if plot_type == '3d' or 'z' in function.lower() or any(term in function.lower() for term in ['3d', 'surface', 'contour']):
                return self._create_3d_graph(clean_function)
            else:
                return self._create_2d_graph(clean_function)
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"Graphing error: {str(e)}"
    
    def _clean_function(self, func: str) -> str:
        """Extract and clean mathematical function from query text"""
        # Remove "graph", "plot", etc.
        func = re.sub(r'graph of|plot|graph|draw|show', '', func, flags=re.IGNORECASE)
        
        # Handle "f(x) = ..." format
        match = re.search(r'f\s*\(\s*x\s*\)\s*=\s*([^,.;]+)', func)
        if match:
            return match.group(1).strip()
        
        # Handle "y = ..." format
        match = re.search(r'y\s*=\s*([^,.;]+)', func)
        if match:
            return match.group(1).strip()
        
        # Replace x^2 with x**2 for Python
        func = func.replace('^', '**')
        
        return func.strip()
    
    def _create_2d_graph(self, function_str: str) -> str:
        """Create a 2D plot using Plotly"""
        # Generate data points
        x = np.linspace(-10, 10, 200)
        
        try:
            # Replace common math patterns with numpy equivalents
            func_code = function_str.lower()
            func_code = func_code.replace('sin(', 'np.sin(')
            func_code = func_code.replace('cos(', 'np.cos(')
            func_code = func_code.replace('tan(', 'np.tan(')
            func_code = func_code.replace('exp(', 'np.exp(')
            func_code = func_code.replace('log(', 'np.log(')
            func_code = func_code.replace('sqrt(', 'np.sqrt(')
            func_code = func_code.replace('pi', 'np.pi')
            func_code = func_code.replace('e', 'np.e')
            func_code = func_code.replace('^', '**')
            
            # Handle special cases
            if 'x**2' in func_code or 'x^2' in function_str:
                title = 'Quadratic Function'
            elif 'x**3' in func_code or 'x^3' in function_str:
                title = 'Cubic Function'
            elif 'sin' in func_code:
                title = 'Sine Function'
                x = np.linspace(-2*np.pi, 2*np.pi, 200)
            elif 'cos' in func_code:
                title = 'Cosine Function'
                x = np.linspace(-2*np.pi, 2*np.pi, 200)
            else:
                title = f'Graph of {function_str}'
            
            # Evaluate function
            y = eval(func_code, {"x": x, "np": np})
            
            # Create plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=function_str))
            
            # Add layout
            fig.update_layout(
                title=title,
                xaxis_title="x",
                yaxis_title="y",
                height=500,
                plot_bgcolor="white"
            )
            
            # Serialize to JSON
            return f'<plotly-graph>{json.dumps(fig.to_dict())}</plotly-graph>'
            
        except Exception as e:
            return f"Could not plot function: {str(e)}"
    
    def _create_3d_graph(self, function_str: str) -> str:
        """Create a 3D surface plot using Plotly"""
        # Generate grid data
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        
        try:
            # Convert to numpy-compatible code
            func_code = function_str.lower()
            func_code = func_code.replace('sin(', 'np.sin(')
            func_code = func_code.replace('cos(', 'np.cos(')
            func_code = func_code.replace('exp(', 'np.exp(')
            func_code = func_code.replace('log(', 'np.log(')
            func_code = func_code.replace('sqrt(', 'np.sqrt(')
            func_code = func_code.replace('pi', 'np.pi')
            func_code = func_code.replace('^', '**')
            
            # Evaluate Z values
            Z = eval(func_code, {"x": X, "y": Y, "np": np})
            
            # Create 3D surface plot
            fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
            
            # Customize appearance
            fig.update_layout(
                title=f"Surface: z = {function_str}",
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z',
                ),
                height=600
            )
            
            # Serialize to JSON
            return f'<plotly-graph>{json.dumps(fig.to_dict())}</plotly-graph>'
            
        except Exception as e:
            return f"Could not generate 3D plot: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "function": {
                    "type": "string",
                    "description": "Mathematical function to graph (e.g., 'x^2', 'sin(x)', 'x^2 + y^2')"
                },
                "plot_type": {
                    "type": "string",
                    "description": "Type of plot ('2d', '3d', or 'auto')",
                    "enum": ["2d", "3d", "auto"],
                    "default": "auto"
                }
            }
        }
