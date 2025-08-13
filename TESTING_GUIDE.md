# Rental Management System - Testing Guide

## 🚀 Quick Start Testing

### Pre-requisites
- ERPNext development environment set up
- Rental management app installed in ERPNext
- Access to ERPNext bench/site

### 1. Quick Validation (2 minutes)
Basic system health check to ensure everything is set up correctly:

```bash
# Navigate to the rental management directory
cd /path/to/your/erpnext/apps/rental_management

# Run quick validation
frappe --site your-site-name execute rental_management.quick_validation.run_quick_validation
```

**Expected Output:** ✅ All basic components should be installed and working

### 2. Full Integration Tests (10-15 minutes)
Comprehensive test suite covering all implemented phases:

```bash
# Run complete test suite
frappe --site your-site-name execute rental_management.tests.test_integration.run_integration_tests
```

**Expected Output:** ✅ All test phases should pass with detailed results

### 3. Manual Testing Checklist

#### Phase 1: Basic Setup ✅
- [x] Custom fields added to Item, Customer, Sales Invoice
- [x] Item groups created (Women's Wear, Men's Wear, etc.)
- [x] App hooks configured correctly

#### Phase 2: Item Management ✅
- [x] Create rental item → Auto-sets item group, status, creates service item
- [x] Create third-party item → Auto-sets commission tracking
- [x] Item validation → Prevents invalid combinations

#### Phase 3: Customer Enhancement ✅
- [x] Create customer → Auto-generates unique ID
- [x] Mobile validation → Formats and validates mobile numbers
- [x] Duplicate prevention → Prevents duplicate mobile numbers

#### Phase 4: Booking System ✅
- [x] Create rental booking → Calculates dates, validates availability
- [x] Commission calculation → Auto-calculates owner commission
- [x] Caution deposit → Creates proper journal entries
- [x] Exchange booking → Links to original bookings

### 4. Common Issues & Solutions

#### Issue: "Party Type and Party is required"
**Status:** ✅ FIXED - Updated journal entry creation to include party information

#### Issue: Custom fields not showing
**Solution:** Run installation script:
```bash
frappe --site your-site-name execute rental_management.setup.install.setup_custom_fields
```

#### Issue: Item groups not created  
**Solution:** Run setup:
```bash
frappe --site your-site-name execute rental_management.setup.install.setup_item_groups
```

### 5. Test Data Cleanup
After testing, clean up test data:

```bash
frappe --site your-site-name execute rental_management.utils.cleanup_test_data
```

### 6. Production Deployment Checklist

#### Pre-deployment:
- [ ] All integration tests pass
- [ ] Manual testing completed for all phases
- [ ] Data migration plan prepared (if needed)
- [ ] Backup of current system taken

#### Deployment:
- [ ] Install rental_management app
- [ ] Run `bench migrate`
- [ ] Execute setup scripts for custom fields and item groups
- [ ] Verify installation with quick validation script

#### Post-deployment:
- [ ] Run quick validation on production
- [ ] Test create sample rental items
- [ ] Test create sample customers
- [ ] Test create sample bookings
- [ ] Verify journal entries are created correctly

## 🏁 Success Criteria

### System is Ready for Production When:
1. ✅ Quick validation shows all green checkmarks
2. ✅ Integration tests pass with 95%+ success rate
3. ✅ Manual testing checklist completed
4. ✅ Sample end-to-end workflow works correctly:
   - Create rental item
   - Create customer  
   - Create booking
   - Update booking status
   - Process refund

### Next Phases (Future Development):
- **Phase 5:** Financial Integration (Advanced accounting)
- **Phase 6:** Reports & Dashboard (Analytics, calendars)
- **Phase 7:** End-to-End Workflows (Complete business processes)

## 📞 Support

For issues or questions:
1. Check the IMPLEMENTATION_PROGRESS.md file
2. Review test results for specific errors
3. Check ERPNext error logs
4. Verify custom field installation

---

**System Status:** ✅ READY FOR INTEGRATION TESTING
**Last Updated:** December 2024
**Current Phase:** Phase 4 Complete - Booking System Fully Functional
