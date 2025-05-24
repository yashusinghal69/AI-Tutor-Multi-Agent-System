import json
import redis
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
import os
from config.settings import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("state_manager")

class InMemoryStateManager:
    """In-memory fallback when Redis is unavailable"""
    def __init__(self):
        self.sessions = {}
        logger.info("Using in-memory session storage (Redis unavailable)")
    
    async def create_session(self, user_id: str = None) -> str:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id or 'anonymous'}"
        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "conversation_history": [],
            "context": {},
            "active": True,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if session and datetime.fromisoformat(session["expires_at"]) < datetime.now():
            del self.sessions[session_id]
            return None
        return session
    
    async def update_session(self, session_id: str, data: Dict[str, Any]):
        if session_id in self.sessions:
            self.sessions[session_id].update(data)
    
    async def add_to_history(self, session_id: str, role: str, message: str):
        if session_id in self.sessions:
            self.sessions[session_id]["conversation_history"].append({
                "role": role,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
    
    async def clear_session(self, session_id: str) -> bool:
        """Clear session data but keep the session ID"""
        if session_id in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "conversation_history": [],
                "context": {},
                "active": True,
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            return True
        return False


class StateManager:
    def __init__(self):
        # Try to connect to Redis, fall back to in-memory if unavailable
        self.use_redis = True
        self.redis_client = None
        try:
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=2)
            # Test connection
            self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.warning(f"Redis connection failed: {str(e)}. Using in-memory state manager instead.")
            self.use_redis = False
            self.fallback = InMemoryStateManager()
    
    async def create_session(self, user_id: str = None) -> str:
        if not self.use_redis:
            return await self.fallback.create_session(user_id)
            
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id or 'anonymous'}"
        session_data = {
            "created_at": datetime.now().isoformat(),
            "conversation_history": [],
            "context": {},
            "active": True
        }
        
        try:
            self.redis_client.setex(
                f"session:{session_id}",
                timedelta(hours=24),
                json.dumps(session_data)
            )
            return session_id
        except Exception as e:
            logger.error(f"Redis error in create_session: {str(e)}")
            self.use_redis = False
            self.fallback = InMemoryStateManager()
            return await self.fallback.create_session(user_id)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self.use_redis:
            return await self.fallback.get_session(session_id)
            
        try:
            data = self.redis_client.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis error in get_session: {str(e)}")
            self.use_redis = False
            self.fallback = InMemoryStateManager()
            return await self.fallback.get_session(session_id)
    
    async def update_session(self, session_id: str, data: Dict[str, Any]):
        if not self.use_redis:
            return await self.fallback.update_session(session_id, data)
            
        try:
            existing = await self.get_session(session_id)
            if existing:
                existing.update(data)
                self.redis_client.setex(
                    f"session:{session_id}",
                    timedelta(hours=24),
                    json.dumps(existing)
                )
        except Exception as e:
            logger.error(f"Redis error in update_session: {str(e)}")
            self.use_redis = False
            self.fallback = InMemoryStateManager()
            return await self.fallback.update_session(session_id, data)
    
    async def add_to_history(self, session_id: str, role: str, message: str):
        if not self.use_redis:
            return await self.fallback.add_to_history(session_id, role, message)
            
        try:
            session = await self.get_session(session_id)
            if session:
                session["conversation_history"].append({
                    "role": role,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                })
                await self.update_session(session_id, session)
        except Exception as e:
            logger.error(f"Redis error in add_to_history: {str(e)}")
            self.use_redis = False
            self.fallback = InMemoryStateManager()
            return await self.fallback.add_to_history(session_id, role, message)
    
    async def clear_session(self, session_id: str) -> bool:
        """Clear a session's conversation history"""
        if not self.use_redis:
            return await self.fallback.clear_session(session_id)
            
        try:
            existing = await self.get_session(session_id)
            if existing:
                # Create fresh session data but keep the ID
                session_data = {
                    "created_at": datetime.now().isoformat(),
                    "conversation_history": [],
                    "context": {},
                    "active": True
                }
                
                self.redis_client.setex(
                    f"session:{session_id}",
                    timedelta(hours=24),
                    json.dumps(session_data)
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Redis error in clear_session: {str(e)}")
            self.use_redis = False
            self.fallback = InMemoryStateManager()
            return await self.fallback.clear_session(session_id)

state_manager = StateManager()
