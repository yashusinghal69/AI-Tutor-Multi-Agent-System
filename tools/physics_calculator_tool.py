import math
import re
from core.base_tool import BaseTool
from typing import Any, Dict

class PhysicsCalculatorTool(BaseTool):
    def __init__(self):
        super().__init__("physics_calculator", "Calculates physics problems using common formulas")
        
        # Physics formulas database
        self.formulas = {
            # Mechanics
            "force": lambda m, a: m * a,  # F = ma
            "velocity": lambda d, t: d / t,  # v = d/t
            "acceleration": lambda v, t: v / t,  # a = v/t
            "kinetic_energy": lambda m, v: 0.5 * m * v**2,  # KE = 1/2 mv²
            "potential_energy": lambda m, g, h: m * g * h,  # PE = mgh
            "momentum": lambda m, v: m * v,  # p = mv
            "work": lambda f, d: f * d,  # W = Fd
            "power": lambda w, t: w / t,  # P = W/t
            
            # Waves and Optics
            "wave_speed": lambda f, l: f * l,  # v = fλ
            "frequency": lambda v, l: v / l,  # f = v/λ
            "wavelength": lambda v, f: v / f,  # λ = v/f
            
            # Electricity
            "ohms_law_voltage": lambda i, r: i * r,  # V = IR
            "ohms_law_current": lambda v, r: v / r,  # I = V/R
            "ohms_law_resistance": lambda v, i: v / i,  # R = V/I
            "electrical_power": lambda v, i: v * i,  # P = VI
            
            # Thermodynamics
            "heat_capacity": lambda m, c, dt: m * c * dt,  # Q = mcΔT
        }
        
        # Constants
        self.constants = {
            "g": 9.81,  # gravitational acceleration
            "c": 299792458,  # speed of light
            "h": 6.62607015e-34,  # Planck constant
            "k": 1.380649e-23,  # Boltzmann constant
        }
    
    async def execute(self, **kwargs) -> Any:
        problem = kwargs.get('problem', '')
        
        try:
            result = self._solve_physics_problem(problem)
            return result
            
        except Exception as e:
            # Return user-friendly error instead of technical details
            return "I couldn't calculate that. Please check if all needed values are provided."
    
    def _solve_physics_problem(self, problem: str) -> str:
        problem_lower = problem.lower()
        
        # Pattern matching for different physics problems
        if "force" in problem_lower and ("mass" in problem_lower or "acceleration" in problem_lower):
            return self._solve_force_problem(problem)
        elif "velocity" in problem_lower or "speed" in problem_lower:
            return self._solve_velocity_problem(problem)
        elif "energy" in problem_lower:
            return self._solve_energy_problem(problem)
        elif "ohm" in problem_lower or "voltage" in problem_lower or "current" in problem_lower:
            return self._solve_electrical_problem(problem)
        elif "wave" in problem_lower or "frequency" in problem_lower:
            return self._solve_wave_problem(problem)
        else:
            return self._general_physics_calculation(problem)
    
    def _solve_force_problem(self, problem: str) -> str:
        # Extract mass and acceleration from problem
        mass_match = re.search(r'mass[:\s]*(\d*\.?\d+)', problem)
        accel_match = re.search(r'acceleration[:\s]*(\d*\.?\d+)', problem)
        
        if mass_match and accel_match:
            mass = float(mass_match.group(1))
            acceleration = float(accel_match.group(1))
            force = self.formulas["force"](mass, acceleration)
            return f"Force = mass × acceleration = {mass} kg × {acceleration} m/s² = {force} N"
        
        return "Could not extract mass and acceleration values"
    
    def _solve_velocity_problem(self, problem: str) -> str:
        # Extract distance and time
        distance_match = re.search(r'distance[:\s]*(\d*\.?\d+)', problem)
        time_match = re.search(r'time[:\s]*(\d*\.?\d+)', problem)
        
        if distance_match and time_match:
            distance = float(distance_match.group(1))
            time = float(time_match.group(1))
            velocity = self.formulas["velocity"](distance, time)
            return f"Velocity = distance / time = {distance} m / {time} s = {velocity} m/s"
        
        return "Could not extract distance and time values"
    
    def _solve_energy_problem(self, problem: str) -> str:
        if "kinetic" in problem.lower():
            mass_match = re.search(r'mass[:\s]*(\d*\.?\d+)', problem)
            velocity_match = re.search(r'velocity[:\s]*(\d*\.?\d+)', problem)
            
            if mass_match and velocity_match:
                mass = float(mass_match.group(1))
                velocity = float(velocity_match.group(1))
                ke = self.formulas["kinetic_energy"](mass, velocity)
                return f"Kinetic Energy = ½mv² = ½ × {mass} kg × ({velocity} m/s)² = {ke} J"
        
        elif "potential" in problem.lower():
            mass_match = re.search(r'mass[:\s]*(\d*\.?\d+)', problem)
            height_match = re.search(r'height[:\s]*(\d*\.?\d+)', problem)
            
            if mass_match and height_match:
                mass = float(mass_match.group(1))
                height = float(height_match.group(1))
                pe = self.formulas["potential_energy"](mass, self.constants["g"], height)
                return f"Potential Energy = mgh = {mass} kg × {self.constants['g']} m/s² × {height} m = {pe} J"
        
        return "Could not solve energy problem"
    
    def _solve_electrical_problem(self, problem: str) -> str:
        voltage_match = re.search(r'voltage[:\s]*(\d*\.?\d+)', problem)
        current_match = re.search(r'current[:\s]*(\d*\.?\d+)', problem)
        resistance_match = re.search(r'resistance[:\s]*(\d*\.?\d+)', problem)
        
        if voltage_match and current_match:
            voltage = float(voltage_match.group(1))
            current = float(current_match.group(1))
            resistance = self.formulas["ohms_law_resistance"](voltage, current)
            power = self.formulas["electrical_power"](voltage, current)
            return f"Resistance = V/I = {voltage} V / {current} A = {resistance} Ω\nPower = VI = {voltage} V × {current} A = {power} W"
        
        elif voltage_match and resistance_match:
            voltage = float(voltage_match.group(1))
            resistance = float(resistance_match.group(1))
            current = self.formulas["ohms_law_current"](voltage, resistance)
            return f"Current = V/R = {voltage} V / {resistance} Ω = {current} A"
        
        elif current_match and resistance_match:
            current = float(current_match.group(1))
            resistance = float(resistance_match.group(1))
            voltage = self.formulas["ohms_law_voltage"](current, resistance)
            return f"Voltage = IR = {current} A × {resistance} Ω = {voltage} V"
        
        return "Could not solve electrical problem"
    
    def _solve_wave_problem(self, problem: str) -> str:
        frequency_match = re.search(r'frequency[:\s]*(\d*\.?\d+)', problem)
        wavelength_match = re.search(r'wavelength[:\s]*(\d*\.?\d+)', problem)
        
        if frequency_match and wavelength_match:
            frequency = float(frequency_match.group(1))
            wavelength = float(wavelength_match.group(1))
            speed = self.formulas["wave_speed"](frequency, wavelength)
            return f"Wave Speed = frequency × wavelength = {frequency} Hz × {wavelength} m = {speed} m/s"
        
        return "Could not solve wave problem"
    
    def _general_physics_calculation(self, problem: str) -> str:
        # Extract numbers and try basic calculations
        numbers = re.findall(r'\d*\.?\d+', problem)
        
        if len(numbers) >= 2:
            return f"Found values: {numbers}. Please specify the physics formula or relationship you want to calculate."
        
        return "Please provide more specific information about the physics problem you want to solve."
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "problem": {
                    "type": "string",
                    "description": "Physics problem description with values (e.g., 'Calculate force with mass 5 kg and acceleration 10 m/s²')"
                }
            }
        }
