#!/usr/bin/env python3
"""
Enhanced Weight Validation Tests

This script comprehensively tests the improved ScenarioWeights validation functionality,
including edge cases, error messages, and rebalancing behavior.

Comments for context:
- Tests the enhanced __post_init__ validation with detailed error messages
- Validates handling of NaN, infinity, None, and negative values
- Ensures proper error messages guide users toward solutions
- Tests the improved rebalance_proportionally method with edge cases
- Synthetic test data is used to verify all validation scenarios
"""

import sys
import os
import math
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.optimization import ScenarioWeights
import pytest
from typing import Dict, List, Tuple

def test_enhanced_validation():
    """Test enhanced weight validation with comprehensive error checking"""
    
    print("🧪 Testing Enhanced Weight Validation")
    print("=" * 60)
    
    test_results = []
    
    # Test Case 1: Valid weights (should pass)
    print("\n📋 Test Case 1: Valid weights")
    try:
        valid_weights = ScenarioWeights(0.25, 0.25, 0.25, 0.25)
        print("✅ Valid weights accepted correctly")
        test_results.append({"test": "valid_weights", "passed": True})
    except Exception as e:
        print(f"❌ Valid weights rejected: {e}")
        test_results.append({"test": "valid_weights", "passed": False, "error": str(e)})
    
    # Test Case 2: None values
    print("\n📋 Test Case 2: None values")
    try:
        ScenarioWeights(None, 0.3, 0.3, 0.4)
        print("❌ None values should be rejected")
        test_results.append({"test": "none_values", "passed": False})
    except ValueError as e:
        if "cannot be None" in str(e) and "numeric value between 0.0 and 1.0" in str(e):
            print("✅ None values properly rejected with helpful message")
            test_results.append({"test": "none_values", "passed": True})
        else:
            print(f"❌ Wrong error message for None: {e}")
            test_results.append({"test": "none_values", "passed": False, "error": str(e)})
    
    # Test Case 3: Non-numeric values
    print("\n📋 Test Case 3: Non-numeric values")
    try:
        ScenarioWeights("invalid", 0.3, 0.3, 0.4)
        print("❌ Non-numeric values should be rejected")
        test_results.append({"test": "non_numeric", "passed": False})
    except ValueError as e:
        if "must be a number" in str(e) and "str" in str(e):
            print("✅ Non-numeric values properly rejected with type information")
            test_results.append({"test": "non_numeric", "passed": True})
        else:
            print(f"❌ Wrong error message for non-numeric: {e}")
            test_results.append({"test": "non_numeric", "passed": False, "error": str(e)})
    
    # Test Case 4: NaN values
    print("\n📋 Test Case 4: NaN values")
    try:
        ScenarioWeights(float('nan'), 0.3, 0.3, 0.4)
        print("❌ NaN values should be rejected")
        test_results.append({"test": "nan_values", "passed": False})
    except ValueError as e:
        if "cannot be NaN" in str(e):
            print("✅ NaN values properly rejected")
            test_results.append({"test": "nan_values", "passed": True})
        else:
            print(f"❌ Wrong error message for NaN: {e}")
            test_results.append({"test": "nan_values", "passed": False, "error": str(e)})
    
    # Test Case 5: Infinity values
    print("\n📋 Test Case 5: Infinity values")
    try:
        ScenarioWeights(float('inf'), 0.3, 0.3, 0.4)
        print("❌ Infinity values should be rejected")
        test_results.append({"test": "infinity_values", "passed": False})
    except ValueError as e:
        if "cannot be infinite" in str(e):
            print("✅ Infinity values properly rejected")
            test_results.append({"test": "infinity_values", "passed": True})
        else:
            print(f"❌ Wrong error message for infinity: {e}")
            test_results.append({"test": "infinity_values", "passed": False, "error": str(e)})
    
    # Test Case 6: Negative values with helpful message
    print("\n📋 Test Case 6: Negative values")
    try:
        ScenarioWeights(-0.1, 0.4, 0.4, 0.3)
        print("❌ Negative values should be rejected")
        test_results.append({"test": "negative_values", "passed": False})
    except ValueError as e:
        if "Negative weights are not allowed" in str(e) and "from_raw_weights" in str(e):
            print("✅ Negative values properly rejected with rebalancing suggestion")
            test_results.append({"test": "negative_values", "passed": True})
        else:
            print(f"❌ Wrong error message for negative: {e}")
            test_results.append({"test": "negative_values", "passed": False, "error": str(e)})
    
    # Test Case 7: Extremely large values
    print("\n📋 Test Case 7: Extremely large values")
    try:
        ScenarioWeights(5.0, 0.3, 0.3, 0.4)
        print("❌ Extremely large values should be rejected")
        test_results.append({"test": "large_values", "passed": False})
    except ValueError as e:
        if "Unusually large weights detected" in str(e) and "from_raw_weights" in str(e):
            print("✅ Large values properly rejected with rebalancing suggestion")
            test_results.append({"test": "large_values", "passed": True})
        else:
            print(f"❌ Wrong error message for large values: {e}")
            test_results.append({"test": "large_values", "passed": False, "error": str(e)})
    
    # Test Case 8: Sum too low with suggestions
    print("\n📋 Test Case 8: Sum too low")
    try:
        ScenarioWeights(0.1, 0.1, 0.1, 0.1)  # Sum = 0.4
        print("❌ Low sum should be rejected")
        test_results.append({"test": "low_sum", "passed": False})
    except ValueError as e:
        if "must sum to 1.0" in str(e) and "very small" in str(e) and "Suggested balanced weights" in str(e):
            print("✅ Low sum properly rejected with suggestions")
            test_results.append({"test": "low_sum", "passed": True})
        else:
            print(f"❌ Wrong error message for low sum: {e}")
            test_results.append({"test": "low_sum", "passed": False, "error": str(e)})
    
    # Test Case 9: Sum too high with suggestions
    print("\n📋 Test Case 9: Sum too high")
    try:
        ScenarioWeights(0.4, 0.4, 0.4, 0.4)  # Sum = 1.6
        print("❌ High sum should be rejected")
        test_results.append({"test": "high_sum", "passed": False})
    except ValueError as e:
        if "sum to more than 1.0" in str(e) and "Suggested balanced weights" in str(e):
            print("✅ High sum properly rejected with suggestions")
            test_results.append({"test": "high_sum", "passed": True})
        else:
            print(f"❌ Wrong error message for high sum: {e}")
            test_results.append({"test": "high_sum", "passed": False, "error": str(e)})
    
    # Test Case 10: All zero weights
    print("\n📋 Test Case 10: All zero weights")
    try:
        ScenarioWeights(0.0, 0.0, 0.0, 0.0)
        print("❌ All zero weights should be rejected")
        test_results.append({"test": "all_zero", "passed": False})
    except ValueError as e:
        if "must sum to 1.0" in str(e) and "very small" in str(e) and "Suggested balanced weights" in str(e):
            print("✅ All zero weights properly rejected")
            test_results.append({"test": "all_zero", "passed": True})
        else:
            print(f"❌ Wrong error message for all zero: {e}")
            test_results.append({"test": "all_zero", "passed": False, "error": str(e)})
    
    return test_results

def test_enhanced_rebalancing():
    """Test enhanced rebalancing with edge cases"""
    
    print("\n\n🔄 Testing Enhanced Rebalancing")
    print("=" * 60)
    
    test_results = []
    
    # Test Case 1: Normal rebalancing
    print("\n📋 Test Case 1: Normal rebalancing")
    try:
        weights = ScenarioWeights.from_raw_weights(0.3, 0.25, 0.2, 0.15)  # Sum = 0.9
        total = weights.normal + weights.peak_season + weights.maintenance + weights.typhoon_season
        if abs(total - 1.0) < 1e-10:
            print("✅ Normal rebalancing works correctly")
            test_results.append({"test": "normal_rebalancing", "passed": True})
        else:
            print(f"❌ Rebalancing failed, sum = {total}")
            test_results.append({"test": "normal_rebalancing", "passed": False})
    except Exception as e:
        print(f"❌ Normal rebalancing failed: {e}")
        test_results.append({"test": "normal_rebalancing", "passed": False, "error": str(e)})
    
    # Test Case 2: All zero weights (should return equal weights)
    print("\n📋 Test Case 2: All zero weights rebalancing")
    try:
        weights = ScenarioWeights.from_raw_weights(0.0, 0.0, 0.0, 0.0)
        expected = [0.25, 0.25, 0.25, 0.25]
        actual = [weights.normal, weights.peak_season, weights.maintenance, weights.typhoon_season]
        if all(abs(a - e) < 1e-10 for a, e in zip(actual, expected)):
            print("✅ All zero weights properly handled with equal distribution")
            test_results.append({"test": "zero_rebalancing", "passed": True})
        else:
            print(f"❌ Zero weights not handled correctly: {actual}")
            test_results.append({"test": "zero_rebalancing", "passed": False})
    except Exception as e:
        print(f"❌ Zero weights rebalancing failed: {e}")
        test_results.append({"test": "zero_rebalancing", "passed": False, "error": str(e)})
    
    # Test Case 3: Mixed valid and invalid weights
    print("\n📋 Test Case 3: Mixed valid and invalid weights")
    try:
        # Create temporary instance with invalid values for testing
        temp_weights = ScenarioWeights.__new__(ScenarioWeights)
        temp_weights.normal = 0.5
        temp_weights.peak_season = float('nan')  # Invalid
        temp_weights.maintenance = -0.1  # Invalid
        temp_weights.typhoon_season = 0.3
        
        rebalanced = temp_weights.rebalance_proportionally()
        total = rebalanced.normal + rebalanced.peak_season + rebalanced.maintenance + rebalanced.typhoon_season
        
        # Should only use valid weights (0.5 + 0.3 = 0.8) and scale them
        expected_normal = 0.5 / 0.8  # 0.625
        expected_typhoon = 0.3 / 0.8  # 0.375
        
        if (abs(total - 1.0) < 1e-10 and 
            abs(rebalanced.normal - expected_normal) < 1e-10 and
            abs(rebalanced.peak_season - 0.0) < 1e-10 and
            abs(rebalanced.maintenance - 0.0) < 1e-10 and
            abs(rebalanced.typhoon_season - expected_typhoon) < 1e-10):
            print("✅ Mixed valid/invalid weights handled correctly")
            test_results.append({"test": "mixed_rebalancing", "passed": True})
        else:
            print(f"❌ Mixed weights not handled correctly")
            print(f"   Total: {total}, Normal: {rebalanced.normal}, Typhoon: {rebalanced.typhoon_season}")
            test_results.append({"test": "mixed_rebalancing", "passed": False})
    except Exception as e:
        print(f"❌ Mixed weights rebalancing failed: {e}")
        test_results.append({"test": "mixed_rebalancing", "passed": False, "error": str(e)})
    
    return test_results

def test_error_message_quality():
    """Test that error messages are helpful and actionable"""
    
    print("\n\n💬 Testing Error Message Quality")
    print("=" * 60)
    
    # Test that error messages contain helpful suggestions
    test_cases = [
        ({"normal": -0.1, "peak_season": 0.4, "maintenance": 0.4, "typhoon_season": 0.3}, 
         ["from_raw_weights", "automatic rebalancing"]),
        ({"normal": 0.1, "peak_season": 0.1, "maintenance": 0.1, "typhoon_season": 0.1}, 
         ["Suggested balanced weights", "from_raw_weights"]),
        ({"normal": 0.4, "peak_season": 0.4, "maintenance": 0.4, "typhoon_season": 0.4}, 
         ["reducing them proportionally", "from_raw_weights"]),
    ]
    
    for i, (weights, expected_phrases) in enumerate(test_cases, 1):
        print(f"\n📋 Error Message Test {i}")
        try:
            ScenarioWeights(**weights)
            print("❌ Should have raised an error")
        except ValueError as e:
            error_msg = str(e)
            missing_phrases = [phrase for phrase in expected_phrases if phrase not in error_msg]
            if not missing_phrases:
                print("✅ Error message contains all expected helpful phrases")
            else:
                print(f"❌ Error message missing phrases: {missing_phrases}")
                print(f"   Actual message: {error_msg}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Weight Validation Tests")
    print("=" * 80)
    
    # Run all test suites
    validation_results = test_enhanced_validation()
    rebalancing_results = test_enhanced_rebalancing()
    test_error_message_quality()
    
    # Summary
    print("\n\n📊 Test Summary")
    print("=" * 80)
    
    all_results = validation_results + rebalancing_results
    passed_count = sum(1 for r in all_results if r.get("passed", False))
    total_count = len(all_results)
    
    print(f"Validation Tests: {sum(1 for r in validation_results if r.get('passed', False))}/{len(validation_results)} passed")
    print(f"Rebalancing Tests: {sum(1 for r in rebalancing_results if r.get('passed', False))}/{len(rebalancing_results)} passed")
    print(f"Overall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed! Enhanced weight validation is working correctly.")
    else:
        print("⚠️  Some tests failed. Review the output above for details.")
        
        # Show failed tests
        failed_tests = [r for r in all_results if not r.get("passed", False)]
        if failed_tests:
            print("\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test.get('error', 'Unknown error')}")