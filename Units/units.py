class UnitRegistry:
    def __init__(self, autoload=True):
        self._units = {}
        self._base_units = {}
        if autoload:
            self.load_defaults()

    def load_defaults(self):
        # Length
        self.define('m')
        self.define('mm', 'm', 0.001)
        self.define('cm', 'm', 0.01)
        self.define('km', 'm', 1000)
        self.define('inch', 'm', 0.0254)
        self.define('ft', 'inch', 12)
        self.define('yd', 'ft', 3)
        self.define('mile', 'yd', 1760)

        # Mass
        self.define('kg')
        self.define('g', 'kg', 0.001)
        self.define('mg', 'g', 0.001)
        self.define('lb', 'kg', 0.45359237)
        self.define('oz', 'lb', 1/16)

        # Time
        self.define('s')
        self.define('ms', 's', 0.001)
        self.define('min', 's', 60)
        self.define('hr', 'min', 60)
        self.define('day', 'hr', 24)
        
        # Temperature
        self.define('K') # Kelvin base
        self.define('degC', 'K', 1.0, 273.15)
        self.define('degR', 'K', 5/9, 0)
        self.define('degF', 'K', 5/9, 255.37222222222222)

    def define(self, unit_name, base_unit=None, factor=1.0, offset=0.0):
        if base_unit is None:
            self._units[unit_name] = {'base': unit_name, 'factor': 1.0, 'offset': 0.0}
            self._base_units[unit_name] = unit_name
        else:
            if base_unit not in self._units:
                raise ValueError(f"Unknown base unit: {base_unit}")
            
            # Resolve to the true base unit
            parent_info = self._units[base_unit]
            self._units[unit_name] = {
                'base': parent_info['base'],
                'factor': factor * parent_info['factor'],
                'offset': offset * parent_info['factor'] + parent_info['offset'] 
            }
            # Note on offset composition:
            # v_base = v_parent * f_parent + o_parent
            # v_parent = v_new * f_new + o_new
            # v_base = (v_new * f_new + o_new) * f_parent + o_parent
            #        = v_new * (f_new * f_parent) + (o_new * f_parent + o_parent)
    
    def __getattr__(self, name):
        if name in self._units:
            return self.Quantity(1, name)
        raise AttributeError(f"'UnitRegistry' object has no attribute '{name}'")
    
    def get_base_unit(self, unit_name):
        return self._units.get(unit_name, {}).get('base')

    def get_factor(self, unit_name):
        return self._units.get(unit_name, {}).get('factor', 1.0)
    
    def get_offset(self, unit_name):
        return self._units.get(unit_name, {}).get('offset', 0.0)
        
    def Quantity(self, value, unit):
        return Quantity(value, unit, self)

class Quantity:
    def __init__(self, value, unit, registry):
        self.value = value
        self.registry = registry
        
        if isinstance(unit, str):
            self._units = self._parse_unit_string(unit)
        elif isinstance(unit, dict):
            self._units = unit.copy()
        else:
             raise TypeError("Unit must be a string or dictionary")

        for u in self._units:
            if u not in registry._units:
                 raise ValueError(f"Unknown unit: {u}")
    
    def _parse_unit_string(self, unit_str):
        return {unit_str: 1}
    
    def is_single_unit(self):
        return len(self._units) == 1 and list(self._units.values())[0] == 1

    def to(self, target_unit_str):
        # 1. Simple Case: Affine conversion for single units (Temperature)
        # Only allowed if both self and target are single atomic units AND bases match
        # AND we do NOT treat this as a delta (which standard physics libs usually distinguish, 
        # but here the user implies absolute temp conversion usually).
        
        # Check if self is single unit
        if self.is_single_unit():
             source_unit = list(self._units.keys())[0]
             
             # Check if target is known atomic unit
             if target_unit_str in self.registry._units:
                 base_src = self.registry.get_base_unit(source_unit)
                 base_dst = self.registry.get_base_unit(target_unit_str)
                 
                 if base_src == base_dst:
                     # Calculate with offsets
                     # base = val * factor + offset
                     # val_dst = (base - offset_dst) / factor_dst
                     
                     f_src = self.registry.get_factor(source_unit)
                     o_src = self.registry.get_offset(source_unit)
                     f_dst = self.registry.get_factor(target_unit_str)
                     o_dst = self.registry.get_offset(target_unit_str)
                     
                     base_val = self.value * f_src + o_src
                     new_val = (base_val - o_dst) / f_dst
                     
                     return Quantity(new_val, target_unit_str, self.registry)

        # 2. General Case: Dimensional Analysis (ignoring offsets, treating as deltas)
        
        # Calculate base value (factors only)
        base_value = self.value
        base_units = {}
        
        for u, exp in self._units.items():
            factor = self.registry.get_factor(u)
            base = self.registry.get_base_unit(u)
            
            base_value *= (factor ** exp)
            base_units[base] = base_units.get(base, 0) + exp

        # Check homogeneity
        unique_bases = set(base_units.keys())
        if len(unique_bases) != 1:
             raise NotImplementedError("Converting complex compound units via string not fully supported yet.")

        current_base = list(unique_bases)[0]
        target_base = self.registry.get_base_unit(target_unit_str)
        if target_base != current_base:
             # Try assuming target_unit_str is a complex string? No, keeping it simple.
             raise ValueError(f"Incompatible dimensions: {current_base} vs {target_base}")
        
        total_exp = base_units[current_base]
        factor_target = self.registry.get_factor(target_unit_str)
        
        # For general conversion, we ignore offsets (assume quantity is a delta or offset-less unit)
        new_value = base_value / (factor_target ** total_exp)
        
        return Quantity(new_value, {target_unit_str: total_exp}, self.registry)

    def __str__(self):
        # Pretty Printing: unit / unit
        numerator = []
        denominator = []
        
        # Sort units for consistent output?
        for u, exp in sorted(self._units.items()):
            if exp > 0:
                if exp == 1:
                    numerator.append(u)
                else:
                    numerator.append(f"{u}^{exp}")
            else:
                if abs(exp) == 1:
                    denominator.append(u)
                else:
                    denominator.append(f"{u}^{abs(exp)}")
        
        if not numerator:
            num_str = "1"
        else:
            num_str = " ".join(numerator) # simple space joint
            
        if not denominator:
            return f"{self.value} {num_str}" if numerator else f"{self.value}"
        
        den_str = " ".join(denominator)
        if len(denominator) > 1:
            den_str = f"({den_str})" # encapsulate if multiple
            
        return f"{self.value} {num_str}/{den_str}"

    def __repr__(self):
        return f"<Quantity({self.value}, {self._units})>"
    
    def _add_sub(self, other, op_sign):
        if not isinstance(other, Quantity):
            raise TypeError("Operands must be Quantity instances")

        # 1. Check direct unit match
        if self._units == other._units:
             val = self.value + other.value if op_sign == 1 else self.value - other.value
             return Quantity(val, self._units, self.registry)
        
        # 2. Check compatibility (using factors)
        # Convert 'other' to 'self' units (treating as Delta, ignore offsets for arithmetic usually)
        # BUT: For temperature, T1 + T2 is usually meaningless if absolute.
        # DeltaT + DeltaT is fine. AbsT - AbsT = DeltaT. AbsT + DeltaT = AbsT.
        # This library is simple: it treats everything as Quantities.
        # If we subtract 10 degC - 5 degC, we usually mean 5 degC (difference)? Or 5 degC absolute?
        # Let's assume standard behavior: Convert to self units using factors only (Delta).
        # EXCEPT if we are converting for display?
        # A simple approach for this MVP: Always convert using factors (Delta logic) for arithmetic.
        # Users should be careful adding absolute temperatures.
        
        other_converted_val = other.value
        # Convert other to base (factors only)
        for u, exp in other._units.items():
             other_converted_val *= (self.registry.get_factor(u) ** exp)
        # Convert base to self (factors only)
        for u, exp in self._units.items():
             other_converted_val /= (self.registry.get_factor(u) ** exp)
             
        # Check dimensionality match
        self_base = {}
        for u, exp in self._units.items():
            b = self.registry.get_base_unit(u)
            self_base[b] = self_base.get(b, 0) + exp
            
        other_base = {}
        for u, exp in other._units.items():
             b = self.registry.get_base_unit(u)
             other_base[b] = other_base.get(b, 0) + exp
             
        if self_base != other_base:
             # try to see if other_base is empty (dimensionless)? No.
             raise ValueError(f"Incompatible units for arithmetic")

        new_val = self.value + other_converted_val if op_sign == 1 else self.value - other_converted_val
        return Quantity(new_val, self._units, self.registry)

    def __add__(self, other):
        return self._add_sub(other, 1)

    def __sub__(self, other):
        return self._add_sub(other, -1)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
             return Quantity(self.value * other, self._units, self.registry)
        
        if isinstance(other, Quantity):
            new_val = self.value * other.value
            new_units = self._units.copy()
            for u, exp in other._units.items():
                new_units[u] = new_units.get(u, 0) + exp
                if new_units[u] == 0:
                    del new_units[u]
            return Quantity(new_val, new_units, self.registry)
            
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
             return Quantity(self.value / other, self._units, self.registry)
        
        if isinstance(other, Quantity):
            new_val = self.value / other.value
            new_units = self._units.copy()
            for u, exp in other._units.items():
                new_units[u] = new_units.get(u, 0) - exp
                if new_units[u] == 0:
                    del new_units[u]
            return Quantity(new_val, new_units, self.registry)

        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
             new_val = other / self.value
             new_units = {}
             for u, exp in self._units.items():
                 new_units[u] = -exp
             return Quantity(new_val, new_units, self.registry)
        return NotImplemented

    def __pow__(self, power):
        if not isinstance(power, (int, float)):
             raise TypeError("Power must be a number")
        
        new_val = self.value ** power
        new_units = {}
        for u, exp in self._units.items():
            new_units[u] = exp * power
        return Quantity(new_val, new_units, self.registry)
