import google.generativeai as genai
import json
import re  # Make sure re is imported
from core.base_agent import BaseAgent, AgentType, AgentMessage, AgentContext
from tools.calculator_tool import CalculatorTool
from tools.graphing_tool import GraphingTool
from tools.equation_solver_tool import EquationSolverTool
from config.settings import settings

class MathAgent(BaseAgent):
    def __init__(self):
        super().__init__("math_001", AgentType.SPECIALIST, "Mathematics Expert")
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Add mathematical tools
        self.add_tool(CalculatorTool())
        self.add_tool(GraphingTool())
        self.add_tool(EquationSolverTool())
        
        self.capabilities = [
            "algebra", "calculus", "geometry", "statistics", 
            "equations", "graphing", "calculations"
        ]
    
    def can_handle(self, query: str) -> float:
        math_indicators = [
            "solve", "calculate", "equation", "derivative", "integral",
            "graph", "plot", "algebra", "geometry", "trigonometry"
        ]
        
        query_lower = query.lower()
        matches = sum(1 for indicator in math_indicators if indicator in query_lower)
        return min(matches * 0.3, 1.0)
    
    async def process(self, message: AgentMessage, context: AgentContext) -> str:
        query = message.content
        
        # Special handling for equation solving
        is_equation_solving = any(phrase in query.lower() for phrase in [
            'solve', 'equation', 'find x', 'find the value'
        ])
        
        if is_equation_solving:
            try:
                # Use equation solver tool directly
                solution = await self.use_tool("equation_solver", equation=query)
                
                # Return a clear, concise response for equation solving
                if "x =" in solution:
                    # Extract just the solution part for a cleaner response
                    if "\n\nSteps:" in solution:
                        solution_part, steps_part = solution.split("\n\nSteps:", 1)
                        return f"{solution_part}\n\nSteps:{steps_part}"
                    return solution
            except Exception as e:
                # Continue with regular processing if direct solving fails
                pass
        
        # Check if this is a graphing request
        is_graphing_request = any(phrase in query.lower() for phrase in [
            'graph', 'plot', 'visualize', 'draw', 'show the function', 
            'display function', 'show f(x)', 'plot f(x)'
        ])
        
        # For graphing requests, simplify the response and prioritize the graph
        if is_graphing_request:
            try:
                # Extract the function to graph
                function_str = query
                
                # Generate the graph directly
                graph_result = await self.use_tool("graphing", function=function_str)
                
                # For graphing requests, return a simple response with the graph
                if '<plotly-graph>' in graph_result:
                    # Extract the function expression
                    match = re.search(r'f\s*\(\s*x\s*\)\s*=\s*([^,.;]+)', query)
                    function_expr = match.group(0) if match else query
                    
                    return f"Here's the graph of {function_expr}:\n\n{graph_result}"
                else:
                    # If there was an error, fall back to regular processing
                    pass
            except Exception as e:
                # If graphing fails, continue with regular processing
                pass
        
        # Check if this is specifically a graphing request
        is_primarily_graphing = any(phrase in query.lower() for phrase in [
            'graph', 'plot', 'visualize', 'draw', 'show the function', 
            'display function', 'show f(x)', 'plot f(x)'
        ])
        
        # Extract other needs
        needs_calculation = any(op in query for op in ['+', '-', '*', '/', '=', 'calculate'])
        needs_solving = any(word in query.lower() for word in ['solve', 'equation', 'find x'])
        
        tool_results = []
        graph_result = None
        
        # For graph requests, prioritize visualization over explanation
        if is_primarily_graphing:
            try:
                # Determine if it's a 2D or 3D graph request
                plot_type = "auto"
                if any(term in query.lower() for term in ['3d', 'surface', 'three dimensional']):
                    plot_type = "3d"
                elif any(term in query.lower() for term in ['2d', 'plane', 'two dimensional']):
                    plot_type = "2d"
                    
                graph_result = await self.use_tool("graphing", function=query, plot_type=plot_type)
                
                # For primarily graphing requests, return just the graph with minimal text
                if isinstance(graph_result, dict) and "type" in graph_result:
                    function_expression = self._extract_function(query)
                    graph_json = json.dumps(graph_result)
                    
                    # If this is primarily a graphing request, return a concise response
                    brief_response = f"Here's the graph of {function_expression}:\n\n{graph_json}"
                    
                    # Only if another tool is needed, add more explanation
                    if needs_calculation or needs_solving:
                        return await self._generate_full_response(query, [brief_response])
                    
                    return brief_response
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                tool_results.append(f"Graphing error: {str(e)}")
        
        # Handle other tools if needed
        if needs_calculation:
            try:
                calc_result = await self.use_tool("calculator", expression=query)
                tool_results.append(f"Calculation result: {calc_result}")
            except Exception as e:
                tool_results.append(f"Calculation error: {str(e)}")
        
        if needs_solving:
            try:
                solve_result = await self.use_tool("equation_solver", equation=query)
                tool_results.append(f"Solution: {solve_result}")
            except Exception as e:
                tool_results.append(f"Equation solving error: {str(e)}")
        
        # If we're here and have a graph result but not a primarily graphing request
        if graph_result and not is_primarily_graphing:
            if isinstance(graph_result, dict) and "type" in graph_result:
                tool_results.append(json.dumps(graph_result))
            else:
                tool_results.append(f"Graph generated: {graph_result}")
        
        # Generate response with Gemini for non-graph focused requests
        return await self._generate_full_response(query, tool_results)
    
    def _extract_function(self, query: str) -> str:
        """Extract the function expression from the query"""
        # Look for function expressions like f(x) = ...
        function_match = re.search(r'f\s*\(\s*x\s*\)\s*=\s*([^,.;]+)', query)
        if function_match:
            return f"f(x) = {function_match.group(1).strip()}"
        
        # Look for expressions like y = ...
        y_match = re.search(r'y\s*=\s*([^,.;]+)', query)
        if y_match:
            return f"y = {y_match.group(1).strip()}"
            
        # Look for expressions after common verbs
        verb_match = re.search(r'(graph|plot|visualize|draw|show)\s+([^,.;]+)', query, re.IGNORECASE)
        if verb_match:
            return verb_match.group(2).strip()
            
        # Default
        return query.strip()
    
    async def _generate_full_response(self, query: str, tool_results: list) -> str:
        # Create a prompt that requests a concise response
        tool_context = "\n".join(tool_results) if tool_results else "No tools were used."
        
        math_prompt = f"""
        You are a mathematics expert. Answer this math question concisely.
        
        Question: {query}
        Tool Results: {tool_context}
        
        Provide a brief, educational explanation. Focus on the main concepts without unnecessary details.
        Keep explanations short and to the point. If there's a graph or calculation result, highlight that.
        """
        
        try:
            response = self.model.generate_content(math_prompt)
            
            final_response = response.text
            if tool_results:
                # If the response already includes the tool results, don't append them again
                if not any(result in final_response for result in tool_results):
                    final_response += f"\n\n{chr(10).join(tool_results)}"
            
            return final_response
        except Exception as e:
            return f"I apologize, but I encountered an error solving this math problem: {str(e)}"
