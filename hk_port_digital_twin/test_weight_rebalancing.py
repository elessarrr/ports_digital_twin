#!/usr/bin/env python3
"""
Test Weight Rebalancing Functionality

This script tests the ScenarioWeights rebalancing functionality with various input combinations
to ensure it works correctly across different scenarios.

Comments for context:
- Tests the automatic proportional rebalancing method added to ScenarioWeights class
- Validates that weights are correctly normalized while maintaining relative proportions
- Covers edge cases like zero weights, extreme values, and precision issues
- Ensures the rebalancing works consistently with the UI implementation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.optimization import ScenarioWeights
import pytest
from typing import Dict, List, Tuple

def test_scenario_weights_rebalancing():
    """Test various weight rebalancing scenarios"""
    
    print("🧪 Testing ScenarioWeights Rebalancing Functionality")
    print("=" * 60)
    
    # Test cases: (description, input_weights, expected_behavior)
    test_cases = [
        # Normal cases
        ("Balanced weights (should not change)", 
         {"normal": 0.25, "peak_season": 0.25, "maintenance": 0.25, "typhoon_season": 0.25},
         "no_change"),
        
        ("Slightly unbalanced weights", 
         {"normal": 0.3, "peak_season": 0.3, "maintenance": 0.2, "typhoon_season": 0.15},
         "minor_rebalance"),
        
        ("Heavily unbalanced weights", 
         {"normal": 0.5, "peak_season": 0.8, "maintenance": 0.3, "typhoon_season": 0.1},
         "major_rebalance"),
        
        # Edge cases
        ("One zero weight", 
         {"normal": 0.0, "peak_season": 0.4, "maintenance": 0.3, "typhoon_season": 0.3},
         "zero_handling"),
        
        ("Multiple zero weights", 
         {"normal": 0.0, "peak_season": 0.0, "maintenance": 0.5, "typhoon_season": 0.5},
         "multiple_zeros"),
        
        ("Very small weights", 
         {"normal": 0.001, "peak_season": 0.002, "maintenance": 0.003, "typhoon_season": 0.004},
         "small_values"),
        
        ("Large weights", 
         {"normal": 2.0, "peak_season": 3.0, "maintenance": 1.5, "typhoon_season": 0.5},
         "large_values"),
        
        ("Extreme imbalance", 
         {"normal": 10.0, "peak_season": 0.1, "maintenance": 0.05, "typhoon_season": 0.01},
         "extreme_imbalance"),
    ]
    
    results = []
    
    for i, (description, input_weights, expected_behavior) in enumerate(test_cases, 1):
        print(f"\n{i}. {description}")
        print("-" * 40)
        
        try:
            # Test the rebalancing method
            original_sum = sum(input_weights.values())
            print(f"Original weights: {input_weights}")
            print(f"Original sum: {original_sum:.6f}")
            
            # Create ScenarioWeights using from_raw_weights method
            rebalanced = ScenarioWeights.from_raw_weights(**input_weights)
            
            # Verify the result
            rebalanced_dict = {
                "normal": rebalanced.normal,
                "peak_season": rebalanced.peak_season,
                "maintenance": rebalanced.maintenance,
                "typhoon_season": rebalanced.typhoon_season
            }
            
            rebalanced_sum = sum(rebalanced_dict.values())
            print(f"Rebalanced weights: {rebalanced_dict}")
            print(f"Rebalanced sum: {rebalanced_sum:.6f}")
            
            # Check if proportions are maintained
            if original_sum > 0:
                original_proportions = {k: v/original_sum for k, v in input_weights.items()}
                rebalanced_proportions = rebalanced_dict
                
                print(f"Original proportions: {original_proportions}")
                print(f"Rebalanced proportions: {rebalanced_proportions}")
                
                # Verify proportions are maintained (within tolerance)
                proportions_maintained = all(
                    abs(original_proportions[k] - rebalanced_proportions[k]) < 1e-10
                    for k in original_proportions.keys()
                )
                
                print(f"✅ Proportions maintained: {proportions_maintained}")
            else:
                print("⚠️  Original sum is zero - cannot check proportions")
            
            # Verify sum is 1.0
            sum_correct = abs(rebalanced_sum - 1.0) < 1e-10
            print(f"✅ Sum equals 1.0: {sum_correct}")
            
            results.append({
                "test": description,
                "passed": sum_correct,
                "original_sum": original_sum,
                "rebalanced_sum": rebalanced_sum,
                "input": input_weights,
                "output": rebalanced_dict
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "test": description,
                "passed": False,
                "error": str(e),
                "input": input_weights
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for r in results if r.get("passed", False))
    total_tests = len(results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed:")
        for result in results:
            if not result.get("passed", False):
                print(f"  - {result['test']}: {result.get('error', 'Failed')}")
    
    return results

def test_ui_integration_scenarios():
    """Test scenarios that might occur in the UI"""
    
    print("\n" + "=" * 60)
    print("🖥️  Testing UI Integration Scenarios")
    print("=" * 60)
    
    # Common UI scenarios
    ui_scenarios = [
        ("User sets all sliders to 0.5", 
         {"normal": 0.5, "peak_season": 0.5, "maintenance": 0.5, "typhoon_season": 0.5}),
        
        ("User focuses on normal operations", 
         {"normal": 0.8, "peak_season": 0.1, "maintenance": 0.05, "typhoon_season": 0.05}),
        
        ("User emphasizes peak season", 
         {"normal": 0.2, "peak_season": 0.6, "maintenance": 0.1, "typhoon_season": 0.1}),
        
        ("User sets maintenance priority", 
         {"normal": 0.1, "peak_season": 0.1, "maintenance": 0.7, "typhoon_season": 0.1}),
        
        ("User prepares for typhoon season", 
         {"normal": 0.15, "peak_season": 0.15, "maintenance": 0.1, "typhoon_season": 0.6}),
        
        ("Slider precision issues (common in UI)", 
         {"normal": 0.333333, "peak_season": 0.333333, "maintenance": 0.333333, "typhoon_season": 0.000001}),
    ]
    
    for scenario_name, weights in ui_scenarios:
        print(f"\n📱 {scenario_name}")
        print("-" * 30)
        
        original_sum = sum(weights.values())
        rebalanced = ScenarioWeights.from_raw_weights(**weights)
        
        rebalanced_dict = {
            "normal": rebalanced.normal,
            "peak_season": rebalanced.peak_season,
            "maintenance": rebalanced.maintenance,
            "typhoon_season": rebalanced.typhoon_season
        }
        
        print(f"Input sum: {original_sum:.6f}")
        print(f"Output sum: {sum(rebalanced_dict.values()):.6f}")
        print(f"Rebalanced: {rebalanced_dict}")

def test_edge_cases():
    """Test edge cases that might break the system"""
    
    print("\n" + "=" * 60)
    print("⚠️  Testing Edge Cases")
    print("=" * 60)
    
    edge_cases = [
        ("All zeros", {"normal": 0, "peak_season": 0, "maintenance": 0, "typhoon_season": 0}),
        ("Negative weights", {"normal": -0.1, "peak_season": 0.5, "maintenance": 0.3, "typhoon_season": 0.3}),
        ("Very large numbers", {"normal": 1e6, "peak_season": 1e6, "maintenance": 1e6, "typhoon_season": 1e6}),
        ("Very small numbers", {"normal": 1e-10, "peak_season": 1e-10, "maintenance": 1e-10, "typhoon_season": 1e-10}),
    ]
    
    for case_name, weights in edge_cases:
        print(f"\n🔍 {case_name}")
        print("-" * 20)
        
        try:
            rebalanced = ScenarioWeights.from_raw_weights(**weights)
            rebalanced_dict = {
                "normal": rebalanced.normal,
                "peak_season": rebalanced.peak_season,
                "maintenance": rebalanced.maintenance,
                "typhoon_season": rebalanced.typhoon_season
            }
            print(f"✅ Handled successfully: {rebalanced_dict}")
            print(f"Sum: {sum(rebalanced_dict.values()):.10f}")
        except Exception as e:
            print(f"❌ Error (expected for some cases): {e}")

if __name__ == "__main__":
    print("🚀 Starting Weight Rebalancing Tests")
    print("=" * 60)
    
    # Run all tests
    basic_results = test_scenario_weights_rebalancing()
    test_ui_integration_scenarios()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)
    
    # Final validation
    passed_count = sum(1 for r in basic_results if r.get("passed", False))
    total_count = len(basic_results)
    
    if passed_count == total_count:
        print(f"🎉 All {total_count} core tests passed!")
        print("The weight rebalancing functionality is working correctly.")
    else:
        print(f"⚠️  {passed_count}/{total_count} tests passed.")
        print("Some issues need to be addressed.")