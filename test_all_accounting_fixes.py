#!/usr/bin/env python3
"""
Comprehensive test runner for all accounting fixes
Tests Phases 1-4 in sequence to validate the complete accounting flow
"""

import sys
import os
import subprocess

def run_test_script(script_name, phase_name):
    """Run a test script and return success status"""
    try:
        print(f"\n{'='*70}")
        print(f"🧪 Running {phase_name} Test")
        print(f"📄 Script: {script_name}")
        print(f"{'='*70}")
        
        # Run the test script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {phase_name} Test: PASSED")
            return True
        else:
            print(f"❌ {phase_name} Test: FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running {phase_name} test: {str(e)}")
        return False

def main():
    """Run all accounting fix tests"""
    
    print("🎯 RENTAL MANAGEMENT ACCOUNTING FIXES - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("Testing all phases of the 3-stage booking accounting system")
    print("="*80)
    
    # Test phases in order
    test_phases = [
        ("test_phase1_advance_payment.py", "Phase 1: Advance Payment Allocation"),
        ("test_phase2_commission_timing.py", "Phase 2: Commission Timing Fix"),
        ("test_phase3_third_party_owner.py", "Phase 3: Third Party Owner System"),
        ("test_phase4_delivery_accounting.py", "Phase 4: Delivery Stage Accounting")
    ]
    
    results = {}
    
    for script, phase in test_phases:
        if os.path.exists(script):
            results[phase] = run_test_script(script, phase)
        else:
            print(f"⚠️  Test script not found: {script}")
            results[phase] = False
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = 0
    total = len(results)
    
    for phase, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {phase}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} phases passed")
    
    if passed == total:
        print("🎉 ALL ACCOUNTING FIXES VALIDATED SUCCESSFULLY!")
        print("\n📋 What's Working:")
        print("   ✅ Advance payment allocation reduces AR correctly")
        print("   ✅ Owner commission timing moved to delivery stage")  
        print("   ✅ Third Party Owner system with dedicated accounts")
        print("   ✅ Delivery stage accounting with proper AR/Cash handling")
        print("   ✅ Caution deposit liability management")
        print("   ✅ Complete 3-stage accounting flow")
        
        print("\n🚀 SYSTEM READY FOR PRODUCTION!")
        
    else:
        print(f"❌ {total - passed} phase(s) failed validation")
        print("   Please review failed tests before proceeding")
    
    print(f"\n{'='*80}")

if __name__ == "__main__":
    main()
