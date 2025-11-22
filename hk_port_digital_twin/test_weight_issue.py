#!/usr/bin/env python3
"""
Test script to reproduce the weight rebalancing issue described in PRD v2.

This script tests the specific scenario where users input weights that sum to 0.9
and verifies that the rebalancing works correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.optimization import ScenarioWeights

def test_weight_rebalancing_issue():
    """Test the specific weight rebalancing issue from PRD v2."""
    
    print("🧪 Testing Weight Rebalancing Issue from PRD v2")
    print("=" * 50)
    
    # Test case 1: Weights that sum to 0.9 (the specific issue mentioned in PRD)
    print("\n📋 Test Case 1: Weights summing to 0.9")
    raw_weights = {
        'normal': 0.3,
        'peak_season': 0.25,
        'maintenance': 0.2,
        'typhoon_season': 0.15
    }
    
    total = sum(raw_weights.values())
    print(f"Raw weights: {raw_weights}")
    print(f"Raw sum: {total}")
    
    # Test the rebalancing
    try:
        rebalanced = ScenarioWeights.from_raw_weights(**raw_weights)
        print(f"Rebalanced weights:")
        print(f"  Normal: {rebalanced.normal:.6f}")
        print(f"  Peak Season: {rebalanced.peak_season:.6f}")
        print(f"  Maintenance: {rebalanced.maintenance:.6f}")
        print(f"  Typhoon Season: {rebalanced.typhoon_season:.6f}")
        
        rebalanced_sum = (rebalanced.normal + rebalanced.peak_season + 
                         rebalanced.maintenance + rebalanced.typhoon_season)
        print(f"Rebalanced sum: {rebalanced_sum:.6f}")
        
        # Check if rebalancing maintained proportions
        original_proportions = [w/total for w in raw_weights.values()]
        rebalanced_proportions = [rebalanced.normal, rebalanced.peak_season, 
                                rebalanced.maintenance, rebalanced.typhoon_season]
        
        print(f"\nProportion check:")
        scenarios = ['Normal', 'Peak Season', 'Maintenance', 'Typhoon Season']
        for i, scenario in enumerate(scenarios):
            print(f"  {scenario}: {original_proportions[i]:.6f} -> {rebalanced_proportions[i]:.6f}")
        
        # Verify proportions are maintained (within floating point precision)
        proportions_maintained = all(
            abs(orig - rebal) < 1e-10 
            for orig, rebal in zip(original_proportions, rebalanced_proportions)
        )
        
        if proportions_maintained and abs(rebalanced_sum - 1.0) < 1e-10:
            print("✅ Test Case 1 PASSED: Rebalancing works correctly")
        else:
            print("❌ Test Case 1 FAILED: Rebalancing issue detected")
            
    except Exception as e:
        print(f"❌ Test Case 1 FAILED with exception: {e}")
    
    # Test case 2: Edge case with very small weights
    print("\n📋 Test Case 2: Very small weights")
    small_weights = {
        'normal': 0.0001,
        'peak_season': 0.0002,
        'maintenance': 0.0001,
        'typhoon_season': 0.0001
    }
    
    try:
        rebalanced_small = ScenarioWeights.from_raw_weights(**small_weights)
        small_sum = (rebalanced_small.normal + rebalanced_small.peak_season + 
                    rebalanced_small.maintenance + rebalanced_small.typhoon_season)
        print(f"Small weights rebalanced sum: {small_sum:.6f}")
        
        if abs(small_sum - 1.0) < 1e-10:
            print("✅ Test Case 2 PASSED: Small weights handled correctly")
        else:
            print("❌ Test Case 2 FAILED: Small weights not handled correctly")
            
    except Exception as e:
        print(f"❌ Test Case 2 FAILED with exception: {e}")
    
    # Test case 3: Weights that sum to more than 1.0
    print("\n📋 Test Case 3: Weights summing to 1.5")
    large_weights = {
        'normal': 0.5,
        'peak_season': 0.4,
        'maintenance': 0.3,
        'typhoon_season': 0.3
    }
    
    try:
        rebalanced_large = ScenarioWeights.from_raw_weights(**large_weights)
        large_sum = (rebalanced_large.normal + rebalanced_large.peak_season + 
                    rebalanced_large.maintenance + rebalanced_large.typhoon_season)
        print(f"Large weights rebalanced sum: {large_sum:.6f}")
        
        if abs(large_sum - 1.0) < 1e-10:
            print("✅ Test Case 3 PASSED: Large weights handled correctly")
        else:
            print("❌ Test Case 3 FAILED: Large weights not handled correctly")
            
    except Exception as e:
        print(f"❌ Test Case 3 FAILED with exception: {e}")

if __name__ == "__main__":
    test_weight_rebalancing_issue()