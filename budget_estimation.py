import random
import json
from typing import Dict, List, Any, Tuple, Optional, Union
from copy import deepcopy
from collections import defaultdict

class BudgetEstimator:
    """
    Budget estimation module for travel planning.
    Estimates costs for transportation, accommodation, dining, and activities.
    """
    
    # Default budget categories
    DEFAULT_CATEGORIES = [
        "transportation", "accommodation", "dining", 
        "activities", "shopping", "miscellaneous"
    ]
    
    # Budget constraints for different travel styles
    BUDGET_CONSTRAINTS = {
        "budget": {"min": 50, "max": 150},      # Per day per person
        "moderate": {"min": 150, "max": 300},    # Per day per person
        "luxury": {"min": 300, "max": 1000},     # Per day per person
    }
    
    # City cost multipliers (relative to baseline)
    CITY_COST_MULTIPLIERS = {
        "New York": 1.8, "London": 1.7, "Tokyo": 1.6,
        "Paris": 1.5, "Sydney": 1.4, "Singapore": 1.3,
        "Bangkok": 0.4, "Hanoi": 0.3, "Mumbai": 0.25,
        # Add more cities as needed
    }
    
    def __init__(self, travel_style: str = "moderate", currency: str = "USD"):
        """
        Initialize the budget estimator.
        
        Args:
            travel_style: One of 'budget', 'moderate', 'luxury'
            currency: Currency code (e.g., 'USD', 'EUR', 'GBP')
        """
        self.travel_style = travel_style
        self.currency = currency
        self.daily_estimates = {}
        
    def estimate_daily_budget(self, city: str, num_people: int = 1) -> Dict[str, float]:
        """
        Estimate daily budget for a city.
        
        Args:
            city: Name of the destination city
            num_people: Number of travelers
            
        Returns:
            Dictionary with budget breakdown by category
        """
        # Get base constraints
        constraints = self.BUDGET_CONSTRAINTS.get(
            self.travel_style, 
            self.BUDGET_CONSTRAINTS["moderate"]
        )
        
        # Apply city cost multiplier
        multiplier = self.CITY_COST_MULTIPLIERS.get(city, 1.0)
        
        base_budget = (constraints["min"] + constraints["max"]) / 2
        adjusted_budget = base_budget * multiplier * num_people
        
        # Distribute across categories
        category_weights = {
            "transportation": 0.20,
            "accommodation": 0.35,
            "dining": 0.25,
            "activities": 0.15,
            "shopping": 0.03,
            "miscellaneous": 0.02
        }
        
        budget_breakdown = {}
        for category, weight in category_weights.items():
            budget_breakdown[category] = round(adjusted_budget * weight, 2)
        
        budget_breakdown["total"] = round(adjusted_budget, 2)
        budget_breakdown["per_person"] = round(adjusted_budget / num_people, 2)
        
        return budget_breakdown
    
    def estimate_total_budget(self, itinerary: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Estimate total budget for a complete itinerary.
        
        Args:
            itinerary: List of daily itinerary entries with city info
            
        Returns:
            Total budget estimate with breakdowns
        """
        total_budget = 0
        daily_breakdowns = []
        city_totals = defaultdict(float)
        
        for day_plan in itinerary:
            city = day_plan.get("city", "Unknown")
            num_days = day_plan.get("duration", 1)
            num_people = day_plan.get("num_people", 1)
            
            daily_estimate = self.estimate_daily_budget(city, num_people)
            day_total = daily_estimate["total"] * num_days
            
            daily_breakdowns.append({
                "city": city,
                "days": num_days,
                "daily_budget": daily_estimate["total"],
                "total_for_stay": day_total
            })
            
            city_totals[city] += day_total
            total_budget += day_total
        
        return {
            "total_budget": round(total_budget, 2),
            "currency": self.currency,
            "daily_breakdowns": daily_breakdowns,
            "city_totals": dict(city_totals),
            "travel_style": self.travel_style
        }
    
    def suggest_budget_adjustments(self, current_budget: float, 
                                   target_range: Tuple[float, float]) -> Dict[str, Any]:
        """
        Suggest adjustments if budget is outside target range.
        
        Args:
            current_budget: Current estimated budget
            target_range: Tuple of (min, max) acceptable budget
            
        Returns:
            Suggestions for budget adjustments
        """
        min_target, max_target = target_range
        suggestions = []
        
        if current_budget < min_target:
            difference = min_target - current_budget
            percentage = (difference / current_budget) * 100
            suggestions.append({
                "type": "increase",
                "amount": round(difference, 2),
                "percentage": round(percentage, 2),
                "message": "Consider adding more activities or dining at higher-end restaurants"
            })
        elif current_budget > max_target:
            difference = current_budget - max_target
            percentage = (difference / current_budget) * 100
            suggestions.append({
                "type": "decrease",
                "amount": round(difference, 2),
                "percentage": round(percentage, 2),
                "message": "Consider budget accommodations, free attractions, or local dining options"
            })
        else:
            suggestions.append({
                "type": "optimal",
                "message": "Budget is within the target range"
            })
        
        return {
            "current_budget": current_budget,
            "target_range": list(target_range),
            "suggestions": suggestions
        }
    
    def generate_budget_report(self, itinerary: List[Dict[str, Any]]) -> str:
        """
        Generate a formatted budget report.
        
        Args:
            itinerary: List of daily itinerary entries
            
        Returns:
            Formatted budget report string
        """
        budget_data = self.estimate_total_budget(itinerary)
        
        report = []
        report.append(f"=" * 50)
        report.append(f"TRAVEL BUDGET ESTIMATION REPORT")
        report.append(f"Travel Style: {self.travel_style.capitalize()}")
        report.append(f"Currency: {self.currency}")
        report.append("=" * 50)
        report.append("")
        
        report.append(f"TOTAL ESTIMATED BUDGET: {self.currency} {budget_data['total_budget']}")
        report.append("")
        
        report.append("CITY BREAKDOWN:")
        report.append("-" * 40)
        for city, total in budget_data["city_totals"].items():
            report.append(f"  {city}: {self.currency} {total}")
        report.append("")
        
        report.append("DAILY BREAKDOWN:")
        report.append("-" * 40)
        for day in budget_data["daily_breakdowns"]:
            report.append(f"  {day['city']} ({day['days']} days): {self.currency} {day['total_for_stay']}")
        report.append("")
        
        report.append("=" * 50)
        report.append(f"Report generated using {self.__class__.__name__}")
        
        return "\n".join(report)


# Example usage and testing
if __name__ == "__main__":
    # Initialize estimator
    estimator = BudgetEstimator(travel_style="moderate", currency="USD")
    
    # Sample itinerary
    sample_itinerary = [
        {"city": "Tokyo", "duration": 3, "num_people": 2},
        {"city": "Kyoto", "duration": 2, "num_people": 2},
        {"city": "Osaka", "duration": 2, "num_people": 2},
    ]
    
    # Generate report
    report = estimator.generate_budget_report(sample_itinerary)
    print(report)
    
    # Test budget adjustments
    total = estimator.estimate_total_budget(sample_itinerary)["total_budget"]
    adjustments = estimator.suggest_budget_adjustments(total, (2000, 3000))
    print("\nBudget Adjustment Suggestions:")
    print(json.dumps(adjustments, indent=2))