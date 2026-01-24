import re
from typing import Union
from decimal import Decimal

class BudgetEstimator:
    """
    A class to estimate travel budgets based on trip details.
    """
    
    def __init__(self):
        self.base_rates = {
            'budget_flight_per_night': 50.0,
            'luxury_flight_per_night': 100.0,
            'budget_accommodation_per_night': 30.0,
            'luxury_accommodation_per_night': 150.0,
            'food_per_day_budget': 20.0,
            'food_per_day_luxury': 50.0,
            'attractions_per_day_budget': 10.0,
            'attractions_per_day_luxury': 30.0,
            'transportation_per_day_budget': 15.0,
            'transportation_per_day_luxury': 40.0
        }

    def extract_budget_from_text(self, text: str) -> Union[float, None]:
        """
        Extract budget amount from text.
        """
        budget_pattern = r'\$?(\d+(?:\.\d{1,2})?)(?:(?:\s*(?:usd|USD|dollars|Dollars))|(?:\s*per\s*(?:day|night|trip|travel)))?'
        matches = re.findall(budget_pattern, text)
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                return None
        return None

    def estimate_budget(self, trip_details: dict) -> dict:
        """
        Estimate budget based on trip details.
        """
        duration = float(trip_details.get('duration', 7))
        budget_type = 'budget'
        if any(word in str(trip_details.get('style', '').lower()) for word in ['luxury', 'premium', 'high-end']):
            budget_type = 'luxury'
        
        flight_per_night = self.base_rates[f'{budget_type}_flight_per_night']
        accommodation_per_night = self.base_rates[f'{budget_type}_accommodation_per_night']
        food_per_day = self.base_rates[f'food_per_day_{budget_type}']
        attractions_per_day = self.base_rates[f'attractions_per_day_{budget_type}']
        transportation_per_day = self.base_rates[f'transportation_per_day_{budget_type}']
        
        total_flight = flight_per_night * duration
        total_accommodation = accommodation_per_night * duration
        total_food = food_per_day * duration
        total_attractions = attractions_per_day * duration
        total_transportation = transportation_per_day * duration
        
        total_budget = total_flight + total_accommodation + total_food + total_attractions + total_transportation
        
        return {
            'total_budget': float(Decimal(str(total_budget)).quantize(Decimal('0.01'))),
            'breakdown': {
                'flights': float(Decimal(str(total_flight)).quantize(Decimal('0.01'))),
                'accommodation': float(Decimal(str(total_accommodation)).quantize(Decimal('0.01'))),
                'food': float(Decimal(str(total_food)).quantize(Decimal('0.01'))),
                'attractions': float(Decimal(str(total_attractions)).quantize(Decimal('0.01'))),
                'transportation': float(Decimal(str(total_transportation)).quantize(Decimal('0.01')))
            },
            'budget_type': budget_type,
            'duration_days': duration
        }