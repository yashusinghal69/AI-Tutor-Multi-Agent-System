import google.generativeai as genai
from core.base_agent import BaseAgent, AgentType, AgentMessage, AgentContext
from typing import Dict, List
import re
from config.settings import settings

genai.configure(api_key=settings.gemini_api_key)

class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__("tutor_001", AgentType.ORCHESTRATOR, "AI Tutor")
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.specialist_agents: Dict[str, BaseAgent] = {}
        
        # Subject classification keywords
        self.subject_keywords = {
            "math": ["math", "algebra", "calculus", "geometry", "equation", "solve", "calculate", "derivative", "integral"],
            "physics": ["physics", "force", "velocity", "acceleration", "energy", "momentum", "newton", "electromagnetic"],
            "chemistry": ["chemistry", "molecule", "atom", "reaction", "compound", "element", "periodic", "bond"],
            "biology": ["biology", "cell", "dna", "organism", "evolution", "genetics", "anatomy", "ecosystem"],
            "computer_science": ["programming", "algorithm", "code", "python", "javascript", "data structure", "software"],
            "language_arts": ["grammar", "literature", "writing", "essay", "poetry", "shakespeare", "analysis"],
            "history": ["history", "war", "civilization", "empire", "revolution", "century", "ancient", "medieval"],
            "geography": ["geography", "continent", "country", "climate", "mountain", "river", "population"]
        }
    
    def register_specialist(self, subject: str, agent: BaseAgent):
        self.specialist_agents[subject] = agent
    
    async def classify_query(self, query: str) -> str:
        # First try keyword matching
        query_lower = query.lower()
        subject_scores = {}
        
        for subject, keywords in self.subject_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                subject_scores[subject] = score
        
        if subject_scores:
            return max(subject_scores, key=subject_scores.get)
        
        # Fallback to Gemini classification
        classification_prompt = f"""
        Classify this educational query into one of these subjects: math, physics, chemistry, biology, computer_science, language_arts, history, geography.
        
        Query: "{query}"
        
        Respond with only the subject name.
        """
        
        try:
            response = self.model.generate_content(classification_prompt)
            return response.text.strip().lower()
        except:
            return "general"
    
    async def process(self, message: AgentMessage, context: AgentContext) -> str:
        query = message.content
        
        # Classify the query
        subject = await self.classify_query(query)
        
        # Check if this is a graphing request to prioritize visualization
        is_graphing_request = any(term in query.lower() for term in [
            'graph', 'plot', 'visualize', 'draw', 'show the function', 'display'
        ])
        
        # Route to appropriate specialist
        if subject in self.specialist_agents:
            specialist = self.specialist_agents[subject]
            specialist_message = AgentMessage(
                id=f"msg_{context.session_id}_{context.current_step}",
                sender_id=self.agent_id,
                receiver_id=specialist.agent_id,
                content=query,
                message_type="query",
                timestamp=message.timestamp
            )
            
            response = await specialist.process(specialist_message, context)
            
            # For graphing requests, just return the specialist response without additional text
            if is_graphing_request and subject == "math":
                return response
                
            return f"🎓 **{specialist.name}**:\n\n{response}"
        else:
            # General response using Gemini
            general_prompt = f"""
            You are an AI tutor. Answer this educational question clearly and concisely:
            
            Question: {query}
            
            Provide a brief, focused explanation without unnecessary details.
            Get straight to the point and focus on the key concepts.
            """
            
            try:
                response = self.model.generate_content(general_prompt)
                return f"🤖 **General Tutor**:\n\n{response.text}"
            except Exception as e:
                return f"I apologize, but I encountered an error processing your question: {str(e)}"
