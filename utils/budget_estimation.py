from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re
import json
import os
from datetime import datetime
import numpy as np
from numpy.random import choice
from task.task_processor import TaskProcessor
from envs.tripdays import TripDays
import util.utils as utils

@dataclass
class CostOptions:
    rental_car: str = "medium_car"
    hotel: str = "medium"
    restaurant: str = "medium"
    attraction: str = "medium"
    attraction_details: Optional[Dict[str, Any]] = None
    show_budget: bool = True

@dataclass
class DailyBudgetResult:
    cost: str
    updated_budget: float
    update_reason: str
    updated_plan: List[str]

class BudgetEstimation(TaskProcessor):
    def __init__(self,
                 cost_options: CostOptions = CostOptions()) -> None:
        super().__init__()
        self.cost_options = cost_options
        self.att_action_cost = {'free':0,
                               'low': 500,
                               'medium': 1000,
                               'high': 1500,
                               'random': [0, 500, 1000, 1500]}
        self.trans_action_cost = {'medium_car': 'rental_car',
                                   'economy_car': 'rental_car',
                                   'full_size_car': 'rental_car',
                                   'standard_suv': 'rental_car',
                                   'large_suv': 'rental_car',
                                   'airplane': 'flight',
                                   'flight': 'flight',
                                   'train': 'train',
                                   'bus': 'bus',
                                   'train_or_bus': 'train_or_bus',
                                   'taxi': 'bus',
                                   'subway': 'bus',
                                   'boat': 'bus',
                                   'random': ['rental_car', 'flight', 'train_or_bus', 'bus']}
        self.discount_locations = ['Toronto', 'New York', 'San Francisco', 'Las Vegas', 'Los Angeles', 'Paris', 'London', 'Tokyo', 'Seoul', 'Singapore']

        self.rental_car_prices = {
            "economy_car": 25,
            "medium_car":35,
            "standard_suv": 60,
            "large_suv": 90,
            "full_size_car": 40
        }
        self.train_costs = 100
        self.bus_costs = 30
        self.flight_costs = 150
        self.hotel_costs = {
            "low": 80,
            "medium": 150,
            "high": 300
        }
        self.restaurant_costs = {
            "low": 10,
            "medium": 30,
            "high": 60
        }
    
    
    def process(self, state: Dict[str, Any], raw_vha: Dict[str, Any], step:int, action: str, **kwargs) -> Tuple[Dict[str, Any], float]:
        raise NotImplementedError

    def calculate_budget(self, locations_data: List[str], total_days: int, budget: float) -> Tuple[float, str]:
        
        def format_cost(cost):
            return f"app{cost:.2f}"
        
        visited_attractions = {"spend": 0, "attractions": []}
        visited_restaurants = {"spend": 0, "restaurants": []}
        
        discount_day = total_days // 4
        vacation_day = total_days // 3
        
        for location in locations_data:
            person_count = location['persons']
            
            for day in range(total_days):
                
                for day_plan in location['detailed_plan'][day]:
                    if day_plan['already_slot']: continue
                    
                    if day_plan['content_category_name'] == 'accommodation':
                        hotel = day_plan['content']
                        hotel_cost = self.hotel_costs[self.cost_options.hotel] * person_count
                        budget -= hotel_cost
                        
                    elif day_plan['content_category_name'] == 'transport' and day_plan['content'] == 'rental picks up':
                        car = day_plan['content']
                        rental_duration = day_plan['duration']
                        rental_car_choice = self.cost_options.rental_car if self.cost_options.rental_car != 'random' else choice(['economy_car', 'medium_car', 'standard_suv', 'large_suv', 'full_size_car'])
                        car_price = self.rental_car_prices[rental_car_choice]
                        rental_cost = car_price * rental_duration
                        budget -= rental_cost
                        
                    elif day_plan['content_category_name'] == 'transport' and day_plan['content'] == 'flight':
                        flight_cost_per_person = self.flight_costs
                        flight_cost = flight_cost_per_person * person_count
                        budget -= flight_cost
            
                    elif day_plan['content_category_name'] == 'transport' and day_plan['content'] == 'train':
                        train_cost_per_person = self.train_costs
                        train_cost = train_cost_per_person * person_count
                        budget -= train_cost
                        
                    elif day_plan['content_category_name'] == 'transport' and day_plan['content'] == 'bus':
                        bus_cost_per_person = self.bus_costs
                        bus_cost = bus_cost_per_person * person_count
                        budget -= bus_cost
                        
                    elif day_plan['content_category_name'] == 'food':
                        restaurant = day_plan['content']
                        restaurant_cost = self.restaurant_costs[self.cost_options.restaurant] * person_count
                        budget -= restaurant_cost
                        
                        visited_restaurants["spend"] += restaurant_cost
                        visited_restaurants["restaurants"].append({"name": restaurant})
    
                    elif day_plan['content_category_name'] == 'attraction':
                        attraction = day_plan['content']
                        attraction_cost_detail = self.att_action_cost[self.cost_options.attraction] 
                        if isinstance(attraction_cost_detail, list):
                            attraction_cost_detail = choice(attraction_cost_detail)
                        attraction_cost = attraction_cost_detail * person_count
                        budget -= attraction_cost
                        
                        visited_attractions["spend"] += attraction_cost
                        visited_attractions["attractions"].append({"name": attraction})
    
                is_discount_day = day == discount_day
                is_vacation_day = day == vacation_day
                
                if is_discount_day or is_vacation_day:
                    discount_factor = 0.1 if (location['city'] in self.discount_locations) else 0.05
                    discount_amount = budget * discount_factor
                    budget += discount_amount
                
                remaining_budget = max(budget, 0)
                remaining_budget_per_day = remaining_budget / (total_days - day)
                
                if remaining_budget_per_day < 100:
                    adjustment_needed = 100 - remaining_budget_per_day
                    budget += adjustment_needed * person_count
                
                return format_cost(budget)
        
        return format_cost(budget)