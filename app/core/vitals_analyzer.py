from typing import List, Tuple
from datetime import datetime, timedelta

def analyze_vitals(history: List[Tuple], vitals_type: str) -> str:
    if not history:
        return "No data available yet to provide suggestions."

    # Sort by time
    history = sorted(history, key=lambda x: x[3])
    
    recent_entries = history[-5:] # look at last 5 entries
    
    if vitals_type == "blood_pressure":
        systolic_avg = sum(e[0] for e in recent_entries) / len(recent_entries)
        diastolic_avg = sum(e[1] for e in recent_entries) / len(recent_entries)
        
        if systolic_avg > 140 or diastolic_avg > 90:
            return (f"Your recent average ({int(systolic_avg)}/{int(diastolic_avg)}) is high. "
                    "Try reducing salt intake, staying hydrated, and consulting a doctor if this persists.")
        elif systolic_avg < 90 or diastolic_avg < 60:
            return "Your recent average is on the lower side. Ensure you are well-hydrated and nourished."
        else:
            return "Your blood pressure trends look stable and within a healthy range. Keep up the good work!"

    elif vitals_type == "sugar":
        sugar_avg = sum(e[0] for e in recent_entries) / len(recent_entries)
        
        if sugar_avg > 180:
            return (f"Your recent average sugar level ({int(sugar_avg)} mg/dL) is elevated. "
                    "Consider monitoring your carb intake and staying active. Please speak with your doctor about these readings.")
        elif sugar_avg < 70:
            return "Your recent sugar levels are low (hypoglycemia). Ensure you're eating consistent meals."
        else:
            return "Your blood sugar levels are currently within target ranges."
            
    return "Trend analysis complete. Keep monitoring regularly."
