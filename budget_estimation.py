# Budget Estimation Module for Travel Planner
# Provides cost estimation utilities for various travel components

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

class BudgetEstimator:
    """
    Estimates travel budget based on destination, duration, and travel style.
    """
    
    def __init__(self):
        self.base_costs = {
            'accommodation': {
                'budget': 30,
                'mid-range': 80,
                'luxury': 200
            },
            'meals': {
                'budget': 20,
                'mid-range': 50,
                'luxury': 120
            },
            'transportation': {
                'budget': 15,
                'mid-range': 40,
                'luxury': 100
            }
        }
        
        self.destination_multipliers = {
            'expensive': 1.5,
            'moderate': 1.0,
            'affordable': 0.7
        }
    
    def estimate_daily_budget(self, travel_style: str, destination_tier: str) -> float:
        """Calculate estimated daily budget."""
        daily_base = sum([
            self.base_costs['accommodation'][travel_style],
            self.base_costs['meals'][travel_style],
            self.base_costs['transportation'][travel_style]
        ])
        multiplier = self.destination_multipliers.get(destination_tier, 1.0)
        return daily_base * multiplier
    
    def estimate_total_budget(self, days: int, travel_style: str, 
                             destination_tier: str, num_travelers: int = 1) -> Dict:
        """Calculate total trip budget."""
        daily = self.estimate_daily_budget(travel_style, destination_tier)
        base_total = daily * days * num_travelers
        
        activities = base_total * 0.15  # 15% for activities
        contingency = base_total * 0.10  # 10% contingency
        
        return {
            'daily_budget': round(daily, 2),
            'accommodation_total': round(self.base_costs['accommodation'][travel_style] * days * num_travelers, 2),
            'meals_total': round(self.base_costs['meals'][travel_style] * days * num_travelers, 2),
            'transportation_total': round(self.base_costs['transportation'][travel_style] * days * num_travelers, 2),
            'activities_estimate': round(activities, 2),
            'contingency': round(contingency, 2),
            'total_estimate': round(base_total + activities + contingency, 2),
            'currency': 'USD'
        }
