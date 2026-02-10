# ESD precaution statement implementation

**Date:** February 10, 2026  
**Jira Story:** IEOPS-2711 / AFFFASDOC-455  
**Requirement:** NEBS GR-1089 Compliance  
**Status:** ✅ IMPLEMENTED

## Overview

Added ESD (electrostatic discharge) precaution statements to installation and maintenance procedures for ONTAP systems, initially requested for AFF A90 & AFF A50, now applied to all new products moving forward.

## ESD CAUTION statement

The following CAUTION block has been added to all relevant procedures:

```asciidoc
CAUTION: Always wear a grounded wrist strap connected to a verified ground point during installation and maintenance procedures. Failure to follow proper ESD precautions can cause permanent damage to controller nodes, storage shelves, and network switches.
```

## Placement strategy

### Installation procedures
The ESD CAUTION is placed after the lead paragraph and before the main content/include statements.

### Maintenance Procedures
The ESD CAUTION replaces the previous step "If you are not already grounded, properly ground yourself" at the beginning of the procedure steps.

## Files modified

### Installation hardware files (7 files)

| File Path | Products Covered |
|-----------|------------------|
| `a70-90/install-hardware.adoc` | AFF A70, AFF A90 |
| `a20-30-50/install-hardware.adoc` | AFF A20, AFF A30, AFF A50 |
| `a1k/install-hardware.adoc` | AFF A1K |
| `fas-70-90/install-hardware.adoc` | FAS70, FAS90 |
| `fas50/install-hardware.adoc` | FAS50 |
| `c80/install-hardware.adoc` | AFF C80 |
| `c30-60/install-hardware.adoc` | AFF C30, AFF C60 |

### Maintenance procedure include fragments (24 files)

#### Generic platform fragments (g_)
These fragments are used across multiple platforms:

- `_include/g_dimm_replace.adoc` - DIMM replacement
- `_include/g_power_supply_replace.adoc` - Power supply replacement
- `_include/g_bootmedia_replace.adoc` - Boot media replacement
- `_include/g_bootmedia_replace-bmr.adoc` - Boot media replacement (BMR)
- `_include/g_rtc_battery_replace.adoc` - RTC battery replacement
- `_include/g_controller_remove.adoc` - Controller removal
- `_include/g_io_module_replace.adoc` - I/O module replacement
- `_include/g_nvdimm_battery_replace.adoc` - NVDIMM battery replacement
- `_include/g_fan_replace.adoc` - Fan replacement

#### AFF A70/A90 platform fragments
- `_include/a70-90_dimm_replace.adoc` - DIMM replacement
- `_include/a70-90_power_supply_replace.adoc` - Power supply replacement
- `_include/a70-90_bootmedia_replace.adoc` - Boot media replacement
- `_include/a70-90_rtc_battery_replace.adoc` - RTC battery replacement
- `_include/a70-90_nvram_replace.adoc` - NVRAM replacement
- `_include/a70-90_controller_remove_physical.adoc` - Controller removal
- `_include/a70-90_io_module_replace.adoc` - I/O module replacement
- `_include/a70-90_fan_swap_out.adoc` - Fan replacement

#### AFF A1K platform fragments
- `_include/a1k_dimm_replace.adoc` - DIMM replacement
- `_include/a1k_fan_replace.adoc` - Fan replacement
- `_include/a1k_controller_remove_physical.adoc` - Controller removal
- `_include/a1k_io_module_replace.adoc` - I/O module replacement
- `_include/a1k_io_module_hotswap_replace.adoc` - I/O module hot-swap
- `_include/a1k_power_supply_replace.adoc` - Power supply replacement

#### AFX platform fragments
- `_include/afx_dimm_replace.adoc` - DIMM replacement
- `_include/afx_io_module_replace.adoc` - I/O module replacement
- `_include/afx_power_supply_replace.adoc` - Power supply replacement

## Scope and coverage

### Products covered
- **AFF A-Series:** A20, A30, A50, A70, A90, A1K
- **AFF C-Series:** C30, C60, C80
- **FAS Series:** FAS50, FAS70, FAS90

### Procedure types
1. **Installation Procedures** - Hardware installation and rack mounting
2. **Maintenance/FRU Procedures** - Field replaceable unit replacement procedures including:
   - DIMM replacement
   - Power supply replacement
   - Boot media replacement
   - RTC battery replacement
   - NVRAM/NVMEM replacement
   - Controller removal/replacement
   - I/O module replacement
   - Fan replacement
   - NVDIMM battery replacement

## Implementation notes

### Design decisions

1. **Consistent Wording:** Used the exact CAUTION text proposed by Jackie Snyder on February 10, 2026, for consistency across all documentation.

2. **Fragment-Based Approach:** Updated shared include fragments (`_include/` directory) to propagate changes across multiple product lines efficiently.

3. **Replacement vs. Addition:** 
   - In installation procedures: Added as a new CAUTION block
   - In maintenance procedures: Replaced the existing grounding step for stronger emphasis

4. **Scope Limitation:** Focused on new products as specified in the Jira requirement. Legacy platform-specific fragments (150_, 220_2700_, 250_, etc.) were not updated as they apply to systems not subject to the new NEBS GR-1089 requirement.

5. **Platform Coverage:** Prioritized generic (g_) fragments and newer platform-specific fragments (A70/A90, A1K, AFX) that apply to current and future products.

### Validation

All modified files have been validated:
- No AsciiDoc syntax errors introduced
- Proper placement of CAUTION blocks
- Correct formatting and indentation maintained
- Include statements remain functional

## Related documentation

- **Original Jira:** IEOPS-2711
- **Related Jira:** AFFFASDOC-455
- **Compliance Standard:** NEBS GR-1089
- **Requester:** Husnain Shafqat
- **Assignee:** Martin Houser
- **Wording Finalized By:** Jackie Snyder

## Future considerations

1. **New Products:** All future ONTAP system products should include this ESD CAUTION in their installation and maintenance procedures.

2. **Template Updates:** Consider updating documentation templates to include the ESD CAUTION by default.

3. **Legacy Products:** Evaluate whether legacy products (A150, A220, A250, A300, etc.) should be updated for consistency, though not required by NEBS GR-1089.

4. **Drive Shelf Documentation:** Consider whether drive shelf installation and maintenance procedures also require ESD precautions.

## Verification checklist

- ✅ ESD CAUTION text matches approved wording
- ✅ Installation procedures updated for all new products
- ✅ Generic maintenance fragments updated
- ✅ Platform-specific maintenance fragments updated for A70/A90, A1K, AFX
- ✅ No syntax errors in modified files
- ✅ Proper AsciiDoc formatting maintained
- ✅ Changes follow existing documentation patterns
