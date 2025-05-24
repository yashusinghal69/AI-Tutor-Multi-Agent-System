import json
from core.base_tool import BaseTool
from typing import Any, Dict

class PhysicsConstantsTool(BaseTool):
    def __init__(self):
        super().__init__("physics_constants", "Looks up physical constants and their values")
        
        # Physics constants database
        self.constants = {
            "speed_of_light": {
                "symbol": "c",
                "value": 299792458,
                "unit": "m/s",
                "description": "Speed of light in vacuum"
            },
            "planck_constant": {
                "symbol": "h",
                "value": 6.62607015e-34,
                "unit": "J⋅s",
                "description": "Planck constant"
            },
            "reduced_planck": {
                "symbol": "ℏ",
                "value": 1.054571817e-34,
                "unit": "J⋅s",
                "description": "Reduced Planck constant (h/2π)"
            },
            "gravitational_constant": {
                "symbol": "G",
                "value": 6.67430e-11,
                "unit": "m³⋅kg⁻¹⋅s⁻²",
                "description": "Gravitational constant"
            },
            "elementary_charge": {
                "symbol": "e",
                "value": 1.602176634e-19,
                "unit": "C",
                "description": "Elementary electric charge"
            },
            "electron_mass": {
                "symbol": "mₑ",
                "value": 9.1093837015e-31,
                "unit": "kg",
                "description": "Electron rest mass"
            },
            "proton_mass": {
                "symbol": "mₚ",
                "value": 1.67262192369e-27,
                "unit": "kg",
                "description": "Proton rest mass"
            },
            "neutron_mass": {
                "symbol": "mₙ",
                "value": 1.67492749804e-27,
                "unit": "kg",
                "description": "Neutron rest mass"
            },
            "avogadro_number": {
                "symbol": "Nₐ",
                "value": 6.02214076e23,
                "unit": "mol⁻¹",
                "description": "Avogadro number"
            },
            "boltzmann_constant": {
                "symbol": "k",
                "value": 1.380649e-23,
                "unit": "J⋅K⁻¹",
                "description": "Boltzmann constant"
            },
            "gas_constant": {
                "symbol": "R",
                "value": 8.314462618,
                "unit": "J⋅mol⁻¹⋅K⁻¹",
                "description": "Universal gas constant"
            },
            "permittivity_vacuum": {
                "symbol": "ε₀",
                "value": 8.8541878128e-12,
                "unit": "F⋅m⁻¹",
                "description": "Electric permittivity of vacuum"
            },
            "permeability_vacuum": {
                "symbol": "μ₀",
                "value": 1.25663706212e-6,
                "unit": "H⋅m⁻¹",
                "description": "Magnetic permeability of vacuum"
            },
            "fine_structure": {
                "symbol": "α",
                "value": 7.2973525693e-3,
                "unit": "dimensionless",
                "description": "Fine structure constant"
            }
        }
    
    async def execute(self, **kwargs) -> Any:
        query = kwargs.get('query', '').lower()
        
        try:
            # Search for constants by name or symbol
            found_constants = []
            
            for key, constant in self.constants.items():
                if (query in key.lower() or 
                    query in constant['description'].lower() or
                    query in constant['symbol'].lower()):
                    found_constants.append({
                        'name': key.replace('_', ' ').title(),
                        'symbol': constant['symbol'],
                        'value': constant['value'],
                        'unit': constant['unit'],
                        'description': constant['description']
                    })
            
            if found_constants:
                result = "**Physics Constants Found:**\n\n"
                for const in found_constants:
                    result += f"**{const['name']}** ({const['symbol']})\n"
                    result += f"Value: {const['value']}\n"
                    result += f"Unit: {const['unit']}\n"
                    result += f"Description: {const['description']}\n\n"
                return result
            else:
                return f"No physics constants found for query: {query}"
                
        except Exception as e:
            return f"Constants lookup error: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "query": {
                    "type": "string",
                    "description": "Search term for physics constants (e.g., 'speed of light', 'planck')"
                }
            }
        }
