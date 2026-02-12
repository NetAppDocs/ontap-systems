# ONTAP Hardware Systems - Copilot Instructions

## Repository Overview
**Product:** ONTAP hardware systems

**Repository Type:** NetApp documentation site (AsciiDoc-based)

**URL:** https://docs.netapp.com/us-en/ontap-systems/
Documentation for installing and maintaining ONTAP storage systems and drive shelves.

## Repository Structure

### Key Configuration Files
- `project.yml` - Site config and sidebar
- `_index.yml` - Landing page

### Content Organization

#### Release notes
- `root-level/` - What's new, compatibility, end of support 
#### Installation and maintenance:
- `aff-aseries/` - AFF A-Series
- `aff-cseries/` - AFF C-Series
- `afx/`, `afx-1k/` - AFX systems
- `asa*/` - ASA systems
- `asa-r2*/` - ASA r2 next-gen
- `fas*/` - FAS hybrid storage
- `endofavail/` - End-of-availability
- `drive-shelves/`, `ns224/`, `nx224/`, `sas3/` - Shelves
- `platform-supplemental/` - Cabinets/rail kits
#### Includes:
- `_include/` - Shared procedures

## Product-Specific Context

### Key Concepts

- **HA pair:** Two controllers (impaired/healthy) with takeover/giveback operations for zero-downtime maintenance
- **System ID:** Unique controller id that must be reassigned during controller/NVRAM replacement; automatic in HA pairs, manual in 2-node MetroCluster
- **LOADER/Maintenance mode:** LOADER is firmware-level prompt before ONTAP loads; Maintenance mode is diagnostic/recovery environment for low-level operations
- **MetroCluster:** Disaster recovery configuration linking two sites with synchronous mirroring; uses `_include/2n_mcc_*.adoc` files for specialized switchover/switchback procedures
- **ASA r2:** Next-generation SAN-only systems (A1K, A70, A90, C30) with symmetric active-active architecture; separate procedures from traditional ASA
- **Boot media recovery methods:** Automated BMR (9.17.1+, retrieves image from partner node) vs manual (pre-9.17.1, requires USB drive with recovery image)
- **I/O module hot-swap:** New in 9.17.1+; slot 4 limited scenarios in 9.17.1/9.18.1RC, any slot with 9.18.1 GA+; cannot hot-swap modules with storage/MetroCluster port assignments
- **Encryption:** OKM (Onboard Key Manager) vs external key management, NSE (NetApp Storage Encryption); encryption checks required during boot media recovery

### Common Terminology
- Boot media recovery
- Impaired controller/Healthy controller
- HA partner
- Giveback
- Field Replaceable Unit

### Typical User Workflows
- **Install:** Requirements → prepare → install → cable → power on → configure cluster
- **Maintenance:** Requirements → shutdown → replace → restore → verify → RMA (boot media adds encryption checks/BMR)

## Documentation Conventions
**Include files:** `{model}_{component}_{action}.adoc` 

**Platform files:** `{component}-replace-workflow.adoc`, `{component}-requirements.adoc`, `{component}-shutdown.adoc`, `{component}-replace.adoc`, `{component}-complete-rma.adoc`

## Common Writer Tasks
- Add new platforms: Create directory (lowercase-hyphenated), create/reuse `_include/` files, update `project.yml` and `_index.yml`
- Create FRU procedures: Create `_include/{prefix}_{component}_replace.adoc` if shared, create platform wrappers, follow workflow pattern (reqs → shutdown → replace → recovery → complete)
- Edit `_include/` for multi-platform changes.