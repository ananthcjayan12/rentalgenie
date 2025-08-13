#!/usr/bin/env python3
"""
ERPNext Rental Management System - Test Runner
Run comprehensive integration tests for all phases
"""

import frappe
import sys
import os
from frappe.test_runner import main as run_frappe_tests

def setup_test_environment():
    """Setup test environment for rental management"""
    print("Setting up test environment...")
    
    # Initialize frappe if needed
    try:
        frappe.init(site="localhost")
        frappe.connect()
    except Exception as e:
        print(f"Error initializing frappe: {e}")
        return False
    
    # Set test flags
    frappe.flags.in_test = True
    
    return True

def run_rental_management_tests():
    """Run all rental management tests"""
    print("\n" + "="*80)
    print("STARTING RENTAL MANAGEMENT SYSTEM INTEGRATION TESTS")
    print("="*80)
    
    # Setup test environment
    if not setup_test_environment():
        print("Failed to setup test environment")
        return False
    
    try:
        # Import and run integration tests
        from rental_management.tests.test_integration import run_integration_tests
        
        print("\nRunning comprehensive integration tests...")
        test_results = run_integration_tests()
        
        # Check if all tests passed
        all_passed = all(result["success"] for result in test_results.values())
        
        if all_passed:
            print("\n✅ ALL TESTS PASSED!")
            print("Rental Management System is ready for deployment.")
        else:
            print("\n❌ SOME TESTS FAILED!")
            print("Please check the test results above and fix issues before deployment.")
        
        return all_passed
        
    except ImportError as e:
        print(f"Error importing test modules: {e}")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def run_specific_phase_tests(phase):
    """Run tests for a specific phase"""
    print(f"\nRunning Phase {phase} tests...")
    
    phase_test_map = {
        1: "TestPhase1BasicSetup",
        2: "TestPhase2ItemManagement", 
        3: "TestPhase3CustomerManagement",
        4: "TestPhase4BookingSystem",
        5: "TestPhase5FinancialIntegration",
        6: "TestPhase6Reports",
        7: "TestPhase7EndToEnd"
    }
    
    if phase not in phase_test_map:
        print(f"Invalid phase: {phase}. Valid phases are 1-7.")
        return False
    
    try:
        from rental_management.tests.test_integration import *
        import unittest
        
        test_class_name = phase_test_map[phase]
        test_class = globals().get(test_class_name)
        
        if not test_class:
            print(f"Test class {test_class_name} not found")
            return False
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Error running phase {phase} tests: {e}")
        return False

def validate_system_health():
    """Basic system health checks"""
    print("\nRunning system health checks...")
    
    health_checks = []
    
    try:
        # Check if rental_management app is installed
        if frappe.get_installed_apps().count('rental_management') > 0:
            health_checks.append(("✅", "rental_management app installed"))
        else:
            health_checks.append(("❌", "rental_management app NOT installed"))
        
        # Check for custom fields
        item_fields = frappe.db.count("Custom Field", {"dt": "Item", "fieldname": ["like", "%rental%"]})
        health_checks.append((
            "✅" if item_fields > 0 else "❌", 
            f"Item rental custom fields: {item_fields} found"
        ))
        
        customer_fields = frappe.db.count("Custom Field", {"dt": "Customer", "fieldname": ["like", "%rental%"]})
        health_checks.append((
            "✅" if customer_fields > 0 else "❌", 
            f"Customer rental custom fields: {customer_fields} found"
        ))
        
        invoice_fields = frappe.db.count("Custom Field", {"dt": "Sales Invoice", "fieldname": ["like", "%rental%"]})
        health_checks.append((
            "✅" if invoice_fields > 0 else "❌", 
            f"Sales Invoice rental custom fields: {invoice_fields} found"
        ))
        
        # Check for test data
        test_items = frappe.db.count("Item", {"is_rental_item": 1})
        health_checks.append((
            "ℹ️", 
            f"Rental items in system: {test_items}"
        ))
        
        print("\nSYSTEM HEALTH CHECK RESULTS:")
        print("-" * 50)
        for status, message in health_checks:
            print(f"{status} {message}")
        
        return True
        
    except Exception as e:
        print(f"Error during health check: {e}")
        return False

def show_help():
    """Show help information"""
    print("""
ERPNext Rental Management System - Test Runner

Usage:
    python test_runner.py [command] [options]

Commands:
    test            Run all integration tests (default)
    health          Run system health checks only
    phase <1-7>     Run tests for specific phase
    help            Show this help message

Examples:
    python test_runner.py                    # Run all tests
    python test_runner.py health             # Health check only
    python test_runner.py phase 4           # Run Phase 4 tests only
    python test_runner.py test               # Run all tests

Phases:
    Phase 1: Basic Setup
    Phase 2: Item Management
    Phase 3: Customer Enhancement
    Phase 4: Sales Invoice Enhancement (Booking System)
    Phase 5: Financial Integration
    Phase 6: Reports & Dashboard
    Phase 7: End-to-End Testing & Workflows
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help":
            show_help()
        elif command == "health":
            setup_test_environment()
            validate_system_health()
        elif command == "phase" and len(sys.argv) > 2:
            try:
                phase_num = int(sys.argv[2])
                setup_test_environment()
                run_specific_phase_tests(phase_num)
            except ValueError:
                print("Invalid phase number. Use 1-7.")
        elif command == "test":
            run_rental_management_tests()
        else:
            print(f"Unknown command: {command}")
            show_help()
    else:
        # Default: run all tests
        success = run_rental_management_tests()
        sys.exit(0 if success else 1)
