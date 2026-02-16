"""
Sustainability Simulator for Halal Businesses

Uses Monte Carlo simulation to model different sustainability scenarios
and predict the impact of various interventions over time.

This helps businesses understand the uncertainty and variability in 
sustainability outcomes and make data-driven decisions.
"""

import numpy as np
from typing import Dict, List
import pandas as pd


class SustainabilitySimulator:
    """
    Simulates sustainability improvements using Monte Carlo methods.
    
    This accounts for:
    - Variability in implementation effectiveness
    - Seasonal variations in energy use
    - Economic fluctuations
    - Uncertainty in cost savings
    """
    
    def __init__(self, baseline_footprint: Dict):
        """
        Initialize simulator with baseline carbon footprint.
        
        Parameters:
        -----------
        baseline_footprint : dict
            Current carbon footprint data from environmental_data_processor
        """
        self.baseline = baseline_footprint
        self.results = {}
        
    def simulate_intervention(self, 
                            intervention_params: Dict,
                            months: int = 24,
                            num_simulations: int = 10000) -> Dict:
        """
        Simulate the impact of sustainability interventions over time.
        
        Parameters:
        -----------
        intervention_params : dict
            Dictionary containing:
            - electricity_reduction: % reduction target (e.g., 0.30 for 30%)
            - transport_reduction: % reduction target
            - waste_reduction: % reduction target
            - implementation_months: Months to fully implement
            - upfront_cost: Initial investment (optional)
            
        months : int
            Number of months to simulate
            
        num_simulations : int
            Number of Monte Carlo runs
            
        Returns:
        --------
        dict : Simulation results including emissions over time and cost savings
        """
        # Extract baseline values
        baseline_total = self.baseline['total_emissions_kg_month']
        breakdown = self.baseline['breakdown']
        
        # Intervention targets
        elec_reduction = intervention_params.get('electricity_reduction', 0)
        transport_reduction = intervention_params.get('transport_reduction', 0)
        waste_reduction = intervention_params.get('waste_reduction', 0)
        heating_reduction = intervention_params.get('heating_reduction', 0)
        water_reduction = intervention_params.get('water_reduction', 0)
        
        implementation_months = intervention_params.get('implementation_months', 6)
        
        # Storage for all simulations
        all_emissions = np.zeros((num_simulations, months))
        all_costs = np.zeros((num_simulations, months))
        all_savings = np.zeros((num_simulations, months))
        
        # Run Monte Carlo simulations
        for sim in range(num_simulations):
            monthly_emissions = []
            monthly_costs = []
            monthly_savings = []
            
            for month in range(months):
                # Calculate implementation progress (S-curve adoption)
                if month < implementation_months:
                    progress = self._implementation_curve(month, implementation_months)
                else:
                    progress = 1.0
                
                # Add variability to effectiveness (normal distribution)
                effectiveness_variance = np.random.normal(1.0, 0.1)
                actual_progress = progress * effectiveness_variance
                actual_progress = max(0, min(1.2, actual_progress))  # Clamp between 0 and 120%
                
                # Calculate reductions for each category
                elec_saving = breakdown['electricity'] * elec_reduction * actual_progress
                transport_saving = breakdown['transport'] * transport_reduction * actual_progress
                waste_saving = breakdown['waste'] * waste_reduction * actual_progress
                heating_saving = breakdown['heating'] * heating_reduction * actual_progress
                water_saving = breakdown['water'] * water_reduction * actual_progress
                
                total_saving = elec_saving + transport_saving + waste_saving + heating_saving + water_saving
                
                # Add seasonal variation (higher energy in summer/winter)
                seasonal_factor = 1 + 0.15 * np.sin(2 * np.pi * month / 12)
                
                # Calculate emissions for this month
                emissions = (baseline_total - total_saving) * seasonal_factor
                
                # Add random events (small probability of setbacks or extra gains)
                random_event = np.random.choice([0.95, 1.0, 1.05], p=[0.1, 0.8, 0.1])
                emissions *= random_event
                
                monthly_emissions.append(emissions)
                
                # Calculate cost savings (energy costs)
                # Average UK electricity: £0.28/kWh, gas: £0.07/kWh
                elec_kwh_saved = elec_saving / (self.baseline['carbon_intensity'] / 1000)
                heating_kwh_saved = heating_saving / 0.185
                
                cost_saving = (elec_kwh_saved * 0.28) + (heating_kwh_saved * 0.07)
                monthly_savings.append(cost_saving)
                
                # Calculate cumulative investment cost (spread over implementation)
                if month < implementation_months:
                    upfront_cost = intervention_params.get('upfront_cost', 0)
                    monthly_cost = upfront_cost / implementation_months
                else:
                    monthly_cost = 0
                
                # Add maintenance costs (small ongoing cost)
                maintenance = cost_saving * 0.05  # 5% of savings
                monthly_costs.append(monthly_cost + maintenance)
            
            all_emissions[sim] = monthly_emissions
            all_costs[sim] = monthly_costs
            all_savings[sim] = monthly_savings
        
        # Calculate statistics across all simulations
        mean_emissions = np.mean(all_emissions, axis=0)
        p10_emissions = np.percentile(all_emissions, 10, axis=0)
        p90_emissions = np.percentile(all_emissions, 90, axis=0)
        
        mean_savings = np.mean(all_savings, axis=0)
        mean_costs = np.mean(all_costs, axis=0)
        
        # Calculate cumulative metrics
        cumulative_savings = np.cumsum(mean_savings)
        cumulative_costs = np.cumsum(mean_costs)
        net_benefit = cumulative_savings - cumulative_costs
        
        # Calculate total carbon saved
        baseline_trajectory = np.full(months, baseline_total)
        total_carbon_saved = np.sum(baseline_trajectory - mean_emissions)
        
        # Calculate ROI metrics
        total_investment = intervention_params.get('upfront_cost', 0)
        total_savings = np.sum(mean_savings)
        
        if total_investment > 0:
            roi_percent = ((total_savings - total_investment) / total_investment) * 100
            # Find payback period (month where cumulative savings > cumulative costs)
            payback_month = None
            for i, benefit in enumerate(net_benefit):
                if benefit > 0:
                    payback_month = i + 1
                    break
        else:
            roi_percent = float('inf')
            payback_month = 0
        
        return {
            'monthly_emissions_mean': mean_emissions.tolist(),
            'monthly_emissions_p10': p10_emissions.tolist(),
            'monthly_emissions_p90': p90_emissions.tolist(),
            'monthly_savings': mean_savings.tolist(),
            'cumulative_savings': cumulative_savings.tolist(),
            'cumulative_costs': cumulative_costs.tolist(),
            'net_benefit': net_benefit.tolist(),
            'total_carbon_saved_kg': total_carbon_saved,
            'total_carbon_saved_tonnes': total_carbon_saved / 1000,
            'percentage_reduction': ((baseline_total - mean_emissions[-1]) / baseline_total) * 100,
            'total_cost_savings': total_savings,
            'roi_percent': roi_percent,
            'payback_months': payback_month,
            'baseline_monthly': baseline_total,
            'trees_equivalent': total_carbon_saved / 21  # Trees for 1 year
        }
    
    def _implementation_curve(self, current_month: int, total_months: int) -> float:
        """
        Calculate implementation progress using S-curve.
        
        Real-world implementations start slow, accelerate, then plateau.
        This is more realistic than linear progress.
        """
        # Logistic function for S-curve
        x = (current_month / total_months) * 12 - 6  # Scale and shift
        return 1 / (1 + np.exp(-x))
    
    def compare_scenarios(self, scenarios: List[Dict], months: int = 24) -> Dict:
        """
        Compare multiple intervention scenarios side-by-side.
        
        Parameters:
        -----------
        scenarios : list of dict
            List of intervention parameter dictionaries, each with 'name' key
            
        months : int
            Simulation duration
            
        Returns:
        --------
        dict : Comparison results for all scenarios
        """
        results = {}
        
        for scenario in scenarios:
            name = scenario.pop('name', 'Unnamed Scenario')
            simulation_result = self.simulate_intervention(scenario, months=months)
            results[name] = simulation_result
        
        # Calculate comparative metrics
        comparison = {
            'scenarios': results,
            'best_carbon_reduction': max(results.items(), 
                                        key=lambda x: x[1]['percentage_reduction'])[0],
            'best_roi': max(results.items(), 
                           key=lambda x: x[1]['roi_percent'] if x[1]['roi_percent'] != float('inf') else -999)[0],
            'fastest_payback': min(results.items(),
                                  key=lambda x: x[1]['payback_months'] if x[1]['payback_months'] else 999)[0]
        }
        
        return comparison
    
    def calculate_certification_benefits(self, 
                                        footprint_reduction: float,
                                        certification_cost: float = 2000) -> Dict:
        """
        Calculate benefits of obtaining sustainability certifications.
        
        Many certifications (ISO 14001, B Corp, etc.) can help halal businesses
        attract environmentally conscious customers and improve operations.
        
        Parameters:
        -----------
        footprint_reduction : float
            Expected reduction in carbon footprint (e.g., 0.25 for 25%)
            
        certification_cost : float
            Cost of obtaining and maintaining certification (annual)
            
        Returns:
        --------
        dict : Analysis of certification benefits
        """
        baseline = self.baseline['total_emissions_kg_month']
        
        # Estimated benefits
        # 1. Customer preference (5-15% revenue increase for certified businesses)
        revenue_boost_low = 0.05
        revenue_boost_high = 0.15
        revenue_boost = np.random.uniform(revenue_boost_low, revenue_boost_high)
        
        # 2. Operational efficiency (certifications require process improvements)
        efficiency_saving = footprint_reduction * baseline * 12  # Annual kg CO2
        
        # 3. Brand value and customer trust
        brand_value_score = min(10, footprint_reduction * 40)  # Score out of 10
        
        return {
            'certification_type': 'Sustainability + Halal Certification',
            'annual_cost': certification_cost,
            'carbon_reduction_kg_year': efficiency_saving,
            'estimated_revenue_increase': f"{revenue_boost*100:.1f}%",
            'brand_value_score': brand_value_score,
            'customer_trust_benefit': 'HIGH' if brand_value_score > 7 else 'MEDIUM',
            'recommended': brand_value_score > 5,
            'islamic_alignment': 'Demonstrates commitment to stewardship (khalifah) and attracts conscious Muslim consumers'
        }
