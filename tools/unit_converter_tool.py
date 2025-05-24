import re
from core.base_tool import BaseTool
from typing import Any, Dict

class UnitConverterTool(BaseTool):
    def __init__(self):
        super().__init__("unit_converter", "Converts between different units of measurement")
        
        # Unit conversion factors (to base SI units)
        self.conversions = {
            # Length
            "meter": 1.0, "m": 1.0,
            "kilometer": 1000.0, "km": 1000.0,
            "centimeter": 0.01, "cm": 0.01,
            "millimeter": 0.001, "mm": 0.001,
            "inch": 0.0254, "in": 0.0254,
            "foot": 0.3048, "ft": 0.3048,
            "yard": 0.9144, "yd": 0.9144,
            "mile": 1609.344,
            
            # Mass
            "kilogram": 1.0, "kg": 1.0,
            "gram": 0.001, "g": 0.001,
            "pound": 0.453592, "lb": 0.453592,
            "ounce": 0.0283495, "oz": 0.0283495,
            "ton": 1000.0,
            
            # Time
            "second": 1.0, "s": 1.0,
            "minute": 60.0, "min": 60.0,
            "hour": 3600.0, "hr": 3600.0, "h": 3600.0,
            "day": 86400.0,
            "year": 31557600.0,
            
            # Energy
            "joule": 1.0, "j": 1.0,
            "kilojoule": 1000.0, "kj": 1000.0,
            "calorie": 4.184, "cal": 4.184,
            "kilocalorie": 4184.0, "kcal": 4184.0,
            "watt_hour": 3600.0, "wh": 3600.0,
            "kilowatt_hour": 3600000.0, "kwh": 3600000.0,
            
            # Power
            "watt": 1.0, "w": 1.0,
            "kilowatt": 1000.0, "kw": 1000.0,
            "horsepower": 745.7, "hp": 745.7,
            
            # Temperature (special handling required)
            "celsius": "celsius", "c": "celsius",
            "fahrenheit": "fahrenheit", "f": "fahrenheit",
            "kelvin": "kelvin", "k": "kelvin",
        }
    
    async def execute(self, **kwargs) -> Any:
        query = kwargs.get('query', '')
        
        try:
            conversion_result = self._parse_and_convert(query)
            return conversion_result
            
        except Exception as e:
            return f"Unit conversion error: {str(e)}"
    
    def _parse_and_convert(self, query: str) -> str:
        # Pattern: "convert X unit1 to unit2" or "X unit1 to unit2"
        patterns = [
            r'convert\s+(\d*\.?\d+)\s+(\w+)\s+to\s+(\w+)',
            r'(\d*\.?\d+)\s+(\w+)\s+to\s+(\w+)',
            r'(\d*\.?\d+)\s*(\w+)\s*=\s*\?\s*(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                value = float(match.group(1))
                from_unit = match.group(2).lower()
                to_unit = match.group(3).lower()
                
                return self._convert_units(value, from_unit, to_unit)
        
        return "Could not parse conversion request. Use format: 'convert 5 meters to feet'"
    
    def _convert_units(self, value: float, from_unit: str, to_unit: str) -> str:
        # Handle temperature conversions separately
        if from_unit in ["celsius", "c", "fahrenheit", "f", "kelvin", "k"]:
            return self._convert_temperature(value, from_unit, to_unit)
        
        # Get conversion factors
        from_factor = self.conversions.get(from_unit)
        to_factor = self.conversions.get(to_unit)
        
        if from_factor is None:
            return f"Unknown unit: {from_unit}"
        if to_factor is None:
            return f"Unknown unit: {to_unit}"
        
        # Convert to base unit, then to target unit
        base_value = value * from_factor
        result = base_value / to_factor
        
        return f"{value} {from_unit} = {result:.6g} {to_unit}"
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> str:
        # Normalize unit names
        from_unit = "celsius" if from_unit in ["celsius", "c"] else from_unit
        from_unit = "fahrenheit" if from_unit in ["fahrenheit", "f"] else from_unit
        from_unit = "kelvin" if from_unit in ["kelvin", "k"] else from_unit
        
        to_unit = "celsius" if to_unit in ["celsius", "c"] else to_unit
        to_unit = "fahrenheit" if to_unit in ["fahrenheit", "f"] else to_unit
        to_unit = "kelvin" if to_unit in ["kelvin", "k"] else to_unit
        
        # Convert to Celsius first
        if from_unit == "fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "kelvin":
            celsius = value - 273.15
        else:  # celsius
            celsius = value
        
        # Convert from Celsius to target
        if to_unit == "fahrenheit":
            result = celsius * 9/5 + 32
        elif to_unit == "kelvin":
            result = celsius + 273.15
        else:  # celsius
            result = celsius
        
        return f"{value}°{from_unit.title()} = {result:.2f}°{to_unit.title()}"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "query": {
                    "type": "string",
                    "description": "Conversion request (e.g., 'convert 5 meters to feet', '100 celsius to fahrenheit')"
                }
            }
        }
