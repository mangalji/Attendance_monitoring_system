from django import template
import math

register = template.Library()

@register.filter
def format_duration(value):
    """
    Converts decimal hours (float) to "X hours Y minutes" string.
    Example: 4.5 -> "4 hours 30 minutes"
    Example: 4.83 -> "4 hours 50 minutes"
    """
    try:
        if value is None or value == "":
            return "-"
        
        hours_float = float(value)
        if hours_float == 0:
            return "-" # Or "0 hours"
            
        hours = int(hours_float)
        minutes = int(round((hours_float - hours) * 60))
        
        if minutes == 60:
            hours += 1
            minutes = 0
            
        parts = []
        if hours > 0:
            parts.append(f"{hours} hours") # or "hour" if 1? User said "10hours". I'll stick to plural/singular logic or just hours.
            # User example: "4 hours", "10hours".
        
        if minutes > 0:
            parts.append(f"{minutes} minutes")
            
        if not parts:
            return "0 minutes" 
            
        return " ".join(parts)
        
    except (ValueError, TypeError):
        return value

