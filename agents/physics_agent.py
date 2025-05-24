import google.generativeai as genai
import re  # Add missing import
from core.base_agent import BaseAgent, AgentType, AgentMessage, AgentContext
from tools.physics_constants_tool import PhysicsConstantsTool
from tools.unit_converter_tool import UnitConverterTool
from tools.physics_calculator_tool import PhysicsCalculatorTool
from config.settings import settings

class PhysicsAgent(BaseAgent):
    def __init__(self):
        super().__init__("physics_001", AgentType.SPECIALIST, "Physics Expert")
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Add physics tools
        self.add_tool(PhysicsConstantsTool())
        self.add_tool(UnitConverterTool())
        self.add_tool(PhysicsCalculatorTool())
        
        self.capabilities = [
            "mechanics", "thermodynamics", "electromagnetism", 
            "quantum", "constants", "unit_conversion"
        ]
    
    def can_handle(self, query: str) -> float:
        physics_indicators = [
            "force", "velocity", "acceleration", "energy", "momentum",
            "newton", "einstein", "quantum", "electromagnetic", "gravity"
        ]
        
        query_lower = query.lower()
        matches = sum(1 for indicator in physics_indicators if indicator in query_lower)
        return min(matches * 0.4, 1.0)
    
    async def process(self, message: AgentMessage, context: AgentContext) -> str:
        query = message.content
        
        try:
            tool_results = []
            
            # Check for constants lookup
            if any(word in query.lower() for word in ['constant', 'speed of light', 'planck', 'gravity']):
                try:
                    constants_result = await self.use_tool("physics_constants", query=query)
                    tool_results.append(f"Constants: {constants_result}")
                except:
                    pass
            
            # Check for unit conversion
            if any(word in query.lower() for word in ['convert', 'unit', 'meter', 'kilogram']):
                try:
                    conversion_result = await self.use_tool("unit_converter", query=query)
                    tool_results.append(f"Conversion: {conversion_result}")
                except:
                    pass
            
            # Check for physics calculations
            if any(word in query.lower() for word in ['calculate', 'find', 'formula']):
                try:
                    calc_result = await self.use_tool("physics_calculator", problem=query)
                    tool_results.append(f"Calculation: {calc_result}")
                except:
                    pass
            
            tool_context = "\n".join(tool_results) if tool_results else "No tools were used."
            
            # Modified prompt for brief, focused explanations
            physics_prompt = f"""
            You are a physics expert. Answer this physics question concisely.
            
            Question: {query}
            Tool Results: {tool_context}
            
            Keep your explanation brief and to the point. Focus on:
            1. The core answer/solution first
            2. Only the most essential concepts
            3. Skip unnecessary background information
            
            Limit your answer to 3-4 sentences maximum unless absolutely necessary.
            Use formulas where appropriate but keep explanations minimal.
            """
            
            try:
                response = self.model.generate_content(physics_prompt)
                
                # Process the response to be more concise
                final_response = self._format_concise_response(response.text, tool_results)
                
                return final_response
            except Exception as e:
                # Return user-friendly error instead of technical details
                return "I couldn't answer that physics question properly. Can you try rephrasing it?"
                
        except Exception as e:
            # Catch-all error handling to prevent technical errors in frontend
            return "I had trouble processing your physics question. Please try asking in a different way."

    def _format_concise_response(self, text: str, tool_results: list) -> str:
        """Format the response to be more concise by limiting paragraphs and adding tool results."""
        try:
            # Remove excessive newlines and spaces
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'\s{2,}', ' ', text)
            
            # If tool results exist and aren't already included in the response
            filtered_results = []
            for result in tool_results:
                # Filter out error messages from tools
                if "error" not in result.lower():
                    filtered_results.append(result)
            
            if filtered_results:
                text += "\n\n**Results:**\n" + "\n".join(filtered_results)
            
            return text
        except Exception:
            # If formatting fails, just return the original text
            return text if text else "I can answer physics questions about forces, energy, and more."
