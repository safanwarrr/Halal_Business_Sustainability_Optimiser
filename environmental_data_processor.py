"""
Environmental Data Processor for Halal Business Sustainability Optimizer

This module fetches real-world environmental data from various APIs to help
halal businesses understand and reduce their environmental impact.

Islamic Perspective:
"And cause not corruption upon the earth after its reformation" (Quran 7:56)
We are stewards (khalifah) of the Earth and must protect it for future generations.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class EnvironmentalDataProcessor:
    """
    Processes environmental data from multiple sources to calculate
    carbon footprint and sustainability metrics for halal businesses.
    """
    
    def __init__(self):
        """Initialize the environmental data processor."""
        self.carbon_intensity_cache = {}
        self.weather_cache = {}
        
    def get_carbon_intensity(self, country: str = "GB") -> Dict:
        """
        Get real-time carbon intensity data for electricity generation.
        
        Uses Carbon Intensity API (UK) which provides real-time data on how clean
        the electricity grid is. Lower carbon intensity means cleaner energy.
        
        Parameters:
        -----------
        country : str
            Country code (currently supports GB for UK, can be extended)
            
        Returns:
        --------
        dict : Carbon intensity data including:
            - current_intensity: CO2g per kWh
            - forecast: Future predictions
            - generation_mix: Sources of electricity (wind, solar, gas, etc.)
        """
        try:
            if country == "GB":
                # UK Carbon Intensity API (free, no auth required)
                url = "https://api.carbonintensity.org.uk/intensity"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    current = data['data'][0]
                    
                    return {
                        'intensity': current['intensity']['actual'] or current['intensity']['forecast'],
                        'index': current['intensity']['index'],
                        'timestamp': current['from'],
                        'country': country
                    }
            
            # Fallback to average values if API fails
            return self._get_fallback_carbon_intensity(country)
            
        except Exception as e:
            print(f"⚠️ Could not fetch live carbon intensity data: {e}")
            return self._get_fallback_carbon_intensity(country)
    
    def _get_fallback_carbon_intensity(self, country: str) -> Dict:
        """
        Fallback carbon intensity values based on global averages.
        
        These are realistic estimates based on 2024 data from various countries.
        """
        intensities = {
            'GB': 220,  # UK average
            'US': 380,  # USA average
            'FR': 70,   # France (high nuclear)
            'DE': 350,  # Germany
            'SA': 580,  # Saudi Arabia
            'AE': 480,  # UAE
            'MY': 520,  # Malaysia
            'ID': 650,  # Indonesia
            'PK': 450,  # Pakistan
        }
        
        intensity = intensities.get(country, 400)  # Global average
        
        return {
            'intensity': intensity,
            'index': 'moderate',
            'timestamp': datetime.now().isoformat(),
            'country': country,
            'source': 'estimated'
        }
    
    def get_electricity_generation_mix(self, country: str = "GB") -> Dict:
        """
        Get the mix of electricity generation sources (renewable vs fossil fuels).
        
        Understanding the generation mix helps businesses see which hours
        have cleaner electricity, enabling smart scheduling of energy-intensive tasks.
        """
        try:
            if country == "GB":
                url = "https://api.carbonintensity.org.uk/generation"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    mix = data['data']['generationmix']
                    
                    result = {}
                    renewable_percent = 0
                    
                    for source in mix:
                        fuel = source['fuel']
                        percent = source['perc']
                        result[fuel] = percent
                        
                        # Calculate renewable percentage
                        if fuel in ['wind', 'solar', 'hydro', 'biomass']:
                            renewable_percent += percent
                    
                    result['renewable_percent'] = renewable_percent
                    result['fossil_percent'] = 100 - renewable_percent
                    
                    return result
            
            return self._get_fallback_generation_mix(country)
            
        except Exception as e:
            print(f"⚠️ Could not fetch generation mix: {e}")
            return self._get_fallback_generation_mix(country)
    
    def _get_fallback_generation_mix(self, country: str) -> Dict:
        """Fallback generation mix data based on country averages."""
        mixes = {
            'GB': {'renewable_percent': 42, 'fossil_percent': 58},
            'US': {'renewable_percent': 22, 'fossil_percent': 78},
            'FR': {'renewable_percent': 25, 'fossil_percent': 15, 'nuclear': 60},
            'DE': {'renewable_percent': 48, 'fossil_percent': 52},
            'SA': {'renewable_percent': 1, 'fossil_percent': 99},
            'AE': {'renewable_percent': 5, 'fossil_percent': 95},
        }
        
        return mixes.get(country, {'renewable_percent': 25, 'fossil_percent': 75})
    
    def calculate_transport_emissions(self, 
                                     distance_km: float,
                                     transport_mode: str,
                                     is_halal_certified: bool = True) -> Dict:
        """
        Calculate carbon emissions from transportation.
        
        Transport is a major source of emissions for halal businesses, especially
        in food supply chains where products must be certified halal.
        
        Parameters:
        -----------
        distance_km : float
            Distance traveled in kilometers
        transport_mode : str
            Mode of transport: 'car', 'van', 'truck', 'ship', 'plane', 'train'
        is_halal_certified : bool
            If True, adds overhead for halal certification logistics
            
        Returns:
        --------
        dict : Emissions data and recommendations
        """
        # Emission factors in kg CO2 per km (per tonne for freight)
        emission_factors = {
            'car': 0.17,          # kg CO2/km
            'van': 0.25,          # kg CO2/km
            'truck': 0.10,        # kg CO2/km per tonne
            'ship': 0.01,         # kg CO2/km per tonne
            'train': 0.03,        # kg CO2/km per tonne
            'plane': 0.50,        # kg CO2/km per tonne
        }
        
        base_emission = distance_km * emission_factors.get(transport_mode, 0.17)
        
        # Halal certification often requires separate logistics
        if is_halal_certified:
            # Separate halal logistics can add 5-15% to emissions
            certification_overhead = 1.10
            base_emission *= certification_overhead
        
        # Calculate equivalent trees needed to offset
        # 1 tree absorbs ~21 kg CO2/year
        trees_per_year = base_emission / 21
        
        return {
            'total_co2_kg': base_emission,
            'transport_mode': transport_mode,
            'distance_km': distance_km,
            'trees_to_offset': trees_per_year,
            'recommendation': self._get_transport_recommendation(transport_mode)
        }
    
    def _get_transport_recommendation(self, mode: str) -> str:
        """Get Islamic-inspired recommendation for reducing transport emissions."""
        recommendations = {
            'car': "Consider carpooling or switching to hybrid/electric vehicles. The Prophet ﷺ encouraged cooperation.",
            'van': "Optimize delivery routes to reduce unnecessary travel. Avoid waste (israf) of resources.",
            'truck': "Consolidate shipments and use modern, fuel-efficient trucks.",
            'ship': "Sea freight is most efficient for long distances. Plan ahead to avoid air freight.",
            'plane': "Reserve for urgent/perishable items only. Air freight has the highest impact.",
            'train': "Excellent choice! Rail is efficient for long distances."
        }
        return recommendations.get(mode, "Optimize your logistics for efficiency.")
    
    def calculate_business_carbon_footprint(self, business_params: Dict) -> Dict:
        """
        Calculate total carbon footprint for a halal business.
        
        This comprehensive calculation considers:
        - Electricity usage
        - Transportation/logistics
        - Heating/cooling
        - Waste generation
        - Water usage
        
        Parameters:
        -----------
        business_params : dict
            Dictionary containing:
            - electricity_kwh_month: Monthly electricity usage
            - heating_kwh_month: Monthly heating energy
            - water_m3_month: Monthly water consumption in cubic meters
            - waste_kg_month: Monthly waste in kg
            - transport_km_month: Monthly transport distance
            - transport_mode: Primary transport mode
            - country: Country code
            - employees: Number of employees
            
        Returns:
        --------
        dict : Comprehensive carbon footprint analysis
        """
        country = business_params.get('country', 'GB')
        
        # Get carbon intensity for electricity
        carbon_data = self.get_carbon_intensity(country)
        electricity_intensity = carbon_data['intensity']  # g CO2/kWh
        
        # Calculate electricity emissions
        electricity_kwh = business_params.get('electricity_kwh_month', 0)
        electricity_emissions = (electricity_kwh * electricity_intensity) / 1000  # kg CO2
        
        # Calculate heating emissions (typically natural gas)
        # Natural gas: 0.185 kg CO2 per kWh
        heating_kwh = business_params.get('heating_kwh_month', 0)
        heating_emissions = heating_kwh * 0.185  # kg CO2
        
        # Calculate water emissions
        # Water treatment: 0.34 kg CO2 per m³
        water_m3 = business_params.get('water_m3_month', 0)
        water_emissions = water_m3 * 0.34  # kg CO2
        
        # Calculate waste emissions
        # Landfill waste: 0.5 kg CO2 per kg waste
        waste_kg = business_params.get('waste_kg_month', 0)
        waste_emissions = waste_kg * 0.5  # kg CO2
        
        # Calculate transport emissions
        transport_km = business_params.get('transport_km_month', 0)
        transport_mode = business_params.get('transport_mode', 'van')
        transport_data = self.calculate_transport_emissions(
            transport_km, transport_mode, is_halal_certified=True
        )
        transport_emissions = transport_data['total_co2_kg']
        
        # Total carbon footprint
        total_emissions = (
            electricity_emissions + 
            heating_emissions + 
            water_emissions + 
            waste_emissions + 
            transport_emissions
        )
        
        # Calculate per employee
        employees = business_params.get('employees', 1)
        per_employee = total_emissions / employees if employees > 0 else total_emissions
        
        # Calculate tree equivalents
        trees_needed = total_emissions / 21  # Trees needed for 1 year offset
        
        return {
            'total_emissions_kg_month': total_emissions,
            'total_emissions_tonnes_year': (total_emissions * 12) / 1000,
            'per_employee_kg_month': per_employee,
            'breakdown': {
                'electricity': electricity_emissions,
                'heating': heating_emissions,
                'water': water_emissions,
                'waste': waste_emissions,
                'transport': transport_emissions
            },
            'percentages': {
                'electricity': (electricity_emissions / total_emissions * 100) if total_emissions > 0 else 0,
                'heating': (heating_emissions / total_emissions * 100) if total_emissions > 0 else 0,
                'water': (water_emissions / total_emissions * 100) if total_emissions > 0 else 0,
                'waste': (waste_emissions / total_emissions * 100) if total_emissions > 0 else 0,
                'transport': (transport_emissions / total_emissions * 100) if total_emissions > 0 else 0,
            },
            'trees_to_offset_annual': trees_needed * 12,
            'carbon_intensity': electricity_intensity
        }
    
    def generate_reduction_recommendations(self, footprint_data: Dict) -> List[Dict]:
        """
        Generate Islamic-value-based recommendations for reducing carbon footprint.
        
        These recommendations are grounded in Islamic principles of:
        - Stewardship (Khalifah)
        - Avoiding waste (Israf)
        - Balance and moderation (Wasatiyyah)
        - Responsibility to future generations
        """
        recommendations = []
        breakdown = footprint_data['breakdown']
        percentages = footprint_data['percentages']
        
        # Electricity recommendations
        if percentages['electricity'] > 30:
            recommendations.append({
                'category': 'Electricity',
                'priority': 'HIGH',
                'impact_potential': 'Large',
                'actions': [
                    'Switch to LED lighting (60-80% energy reduction)',
                    'Install solar panels - sustainable and aligns with Islamic values of using natural resources',
                    'Schedule energy-intensive tasks during low carbon intensity hours',
                    'Improve insulation to reduce heating/cooling needs'
                ],
                'islamic_principle': 'Avoiding Waste (Israf) - "And eat and drink, but be not excessive" (Quran 7:31)',
                'estimated_reduction': '30-50% of electricity emissions'
            })
        
        # Transport recommendations
        if percentages['transport'] > 25:
            recommendations.append({
                'category': 'Transportation',
                'priority': 'HIGH',
                'impact_potential': 'Large',
                'actions': [
                    'Consolidate halal deliveries with other certified businesses',
                    'Optimize delivery routes using route planning software',
                    'Consider electric vehicles for local deliveries',
                    'Partner with suppliers who use sustainable transport'
                ],
                'islamic_principle': 'Cooperation (Ta\'awun) - "Help one another in righteousness" (Quran 5:2)',
                'estimated_reduction': '20-40% of transport emissions'
            })
        
        # Waste recommendations
        if percentages['waste'] > 15:
            recommendations.append({
                'category': 'Waste Management',
                'priority': 'MEDIUM',
                'impact_potential': 'Medium',
                'actions': [
                    'Implement composting for organic waste',
                    'Donate excess halal food to those in need',
                    'Use biodegradable packaging where possible',
                    'Partner with recycling programs'
                ],
                'islamic_principle': 'No Waste - The Prophet ﷺ said: "Do not waste, even if you are at a running stream"',
                'estimated_reduction': '40-60% of waste emissions'
            })
        
        # Water recommendations
        if percentages['water'] > 10:
            recommendations.append({
                'category': 'Water Conservation',
                'priority': 'MEDIUM',
                'impact_potential': 'Small-Medium',
                'actions': [
                    'Install water-efficient fixtures',
                    'Collect rainwater for non-drinking purposes',
                    'Fix leaks promptly',
                    'Train staff on water conservation'
                ],
                'islamic_principle': 'Water Conservation - The Prophet ﷺ used minimal water for wudu',
                'estimated_reduction': '30-40% of water emissions'
            })
        
        # General recommendations
        recommendations.append({
            'category': 'Overall Sustainability',
            'priority': 'ONGOING',
            'impact_potential': 'Large',
            'actions': [
                'Get halal and sustainability certifications together',
                'Educate customers about your environmental efforts',
                'Join halal business sustainability networks',
                'Set measurable monthly reduction targets'
            ],
            'islamic_principle': 'Stewardship (Khalifah) - Humans are caretakers of Earth for Allah',
            'estimated_reduction': 'Cumulative: 40-60% over 2 years'
        })
        
        return recommendations
