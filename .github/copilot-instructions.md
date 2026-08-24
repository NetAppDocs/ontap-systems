# Copilot instructions for ONTAP hardware systems documentation

## Repository overview

This repository contains installation and maintenance documentation for NetApp ONTAP storage hardware, including step-by-step procedures for hardware installation, FRU replacement, and system recovery across all supported platform families.

Products: Multiple NetApp ONTAP hardware platforms across the AFF, ASA, FAS, and AFX storage families. Note that ONTAP systems is the category, not the product name; use the exact storage family and model to specify the product.

Title style: The product name should include the [Family] [Model] — for example, AFF A150, AFF A1K, AFF C80, ASA A400, ASA r2 A1K, FAS9500, AFX 1K. See the Repository structure and Product-specific context sections for the full platform list. Don't refer to related pages for title or style guidance; use the custom repository instructions and/or custom agent instructions only.

Use "an" before product names starting with a vowel sound (AFF, ASA, AFX) and "a" before product names starting with a consonant sound (FAS). Use "the" instead of an indefinite article when the noun following the product name is plural (e.g., "controllers") or uncountable (e.g., "hardware").

**FRU replacement and maintenance pages:**
- Replace/add: `[Verb] the [component] in [a/an] [Product] system [optional purpose]` — the purpose clause is optional and should generally be omitted; for example, "Replace the boot media in an AFF A1K system", "Replace a DIMM in an AFF C30 or AFF C60 system"
- Add an I/O module (exception — uses "to" instead of "in"): `Add an I/O module to [a/an] [Product] system` — for example, "Add an I/O module to an AFF A1K system"
- Replace/add (boot media, BMR-capable platforms): `Replace the boot media in [a/an] [Product] system during the [manual/automated] boot recovery process` — for example, "Replace the boot media in an AFF C30 or AFF C60 system during the automated boot recovery process"
- Hot-swap: `Hot-swap a [component] in [a/an] [Product] system` — for example, "Hot-swap a fan in an AFF A1K system"
- Requirements (before): `Review the requirements for [action] [a/an] [component/system] in [a/an] [Product] system` — for example, "Review the requirements for replacing a controller in an AFF A1K system", "Review the requirements for replacing a controller in an AFF C30 or AFF C60 system"
- Requirements (for): `Review the requirements for [procedure] in [a/an] [Product] system` — for example, "Review the requirements for manual boot media recovery in an AFF A1K system"
- Shutdown (controller-integral component replacement, including the controller itself — DIMM, RTC battery, NVDIMM/NVRAM battery, controller): `Shut down the impaired controller in [a/an] [Product] system [optional procedure]` — the procedure clause is optional and should generally be omitted; for example, "Shut down the impaired controller in an AFF A1K system", "Shut down the impaired controller in an AFF C30 or AFF C60 system"
- Shutdown (removable/modular FRU replacement — e.g., NVRAM module, I/O module, other non-integral FRUs): `Shut down the controller in [a/an] [Product] system before [procedure]` — no "impaired"; the component itself is impaired, not the controller
- Shutdown (boot media recovery): `Shut down the controller in [a/an] [Product] system during the [manual/automated] boot recovery process` — no "impaired"; boot media is a removable component, not part of the controller itself
- Shutdown (chassis replacement, single-controller models): `Shut down [a/an] [Product] controller to replace the chassis` — for example, "Shut down an AFF A1K controller to replace the chassis"
- Shutdown (chassis replacement, HA-pair models): `Shut down the [Product] controllers to replace the chassis` — plural "controllers" takes "the"; for example, "Shut down the AFF A700 controllers to replace the chassis"
- Pre-shutdown check: `Check [topic] on the [component] in [a/an] [Product] system` — for example, "Check encryption support on the boot media in an AFF A1K system"
- Boot image: `Boot the recovery image on [a/an] [Product] system [using the manual/automated boot recovery process]`
- Restore encryption: `Restore encryption on the [component] in [a/an] [Product] system [context]`
- Restore and verify: `Restore and verify the [component] configuration in [a/an] [Product] system`
- Completion: `Complete the [procedure] for [a/an] [Product] system` — for example, "Complete the controller replacement for an AFF A1K system"
- RMA return: `Return the failed [Product] [component] to NetApp [after the manual/automated boot recovery process]`

**Workflow pages:**
- `[Product] [procedure] workflow` — for example, "AFF A1K controller replacement workflow", "AFF A1K chassis replacement workflow"
- Boot media workflow: `[Procedure] workflow for [a/an] [Product] system using the [manual/automated] boot recovery process` — for example, "Boot media replacement workflow for an AFF C30 or AFF C60 system using the automated boot recovery process"

**Installation pages:**
- Overview: `[Product] installation and configuration workflow`
- Prepare: `Prepare to install [a/an] [Product] storage system`
- Requirements: `Review the requirements for installing [a/an] [Product] storage system`
- Install hardware: `Install the [Product] hardware in [location]` — for example, "Install the AFF A1K hardware in a cabinet or rack"
- Cable: `Cable the [Product] hardware for [purpose]` — for example, "Cable the AFF A1K hardware for network and storage connectivity"
- Power on: `Power on [a/an] [Product] storage system`

**Concept pages:**
- General concept: `Learn about [topic] in [a/an] [Product] system` — for example, "Learn about adding and replacing I/O modules in an AFF A1K system"
- Maintain overview: `Learn about maintaining [a/an] [Product] storage system`
- Key specifications: `Key specifications for [a/an] [Product] system` — for example, "Key specifications for an AFF C30 system"

**BMR context suffix:** On platforms that support both manual and automated (ONTAP 9.17.1+) boot media recovery, append "during the manual boot recovery process" or "during the automated boot recovery process" to boot media replace/shutdown page titles, and "using the manual boot recovery process" to other boot media page titles (boot image, workflow, RMA return), to disambiguate them. Pages for platforms that support only manual recovery (older platforms) do not need this suffix.

## Repository structure

- `_include/` – Reusable AsciiDoc content fragments shared across platform directories; files are prefixed with the platform model (e.g., `a1k_`, `a70-90_`, `800_`) or are generic (e.g., `g_`, `afx_`)
- `a1k/`, `a20-30-50/`, `a70-90/`, `a200/`–`a900/` – AFF A-Series platform-specific content (install and maintain)
- `c250/`, `c400/`, `c800/`, `c80/`, `c30-60/` – AFF C-Series platform-specific content (install and maintain)
- `asa150/`–`asa900/`, `asa-c250/`–`asa-c800/` – ASA (All SAN Array) platform content (install and maintain)
- `asa-r2/`, `asa-r2-a1k/`, `asa-r2-a20-30-50/`, `asa-r2-70-90/`, `asa-r2-c30/` – ASA r2 generation content (install and maintain); some procedures differ from earlier ASA and AFF
- `fas2600/`–`fas9500/`, `fas50/`, `fas70-90/` – FAS hybrid storage platform content (install and maintain)
- `afx/`, `afx-1k/` – AFX all-flash platform content (install and maintain)
- `aff-landing/`, `aff-aseries/`, `aff-cseries/` – AFF product family index and landing pages
- `allsan-landing/`, `allsan-a-series/`, `allsan-c-series/` – ASA product family landing pages
- `asa-r2-landing-maintain/`, `afx-landing-maintain/` – r2 and AFX maintenance landing pages
- `drive-shelves/` – NS224, NX224, and SAS shelf documentation
- `ns224/`, `nx224/`, `sas3/` – Shelf-specific installation and maintenance content
- `platform-supplemental/` – Supplemental rack/cabinet content (42U cabinet install, superrail, telco rack)
- `fru-reference/` – Cross-platform FRU cross-reference link pages, one file per FRU type
- `endofavail/` – Hardware end-of-availability and end-of-support content
- `store-redirects/` – Stub files that redirect legacy URLs

## Product-specific context

- **AFF (All Flash FAS):** NetApp's all-flash NAS/unified storage arrays; A-Series and C-Series variants; always referred to as "AFF A-Series" or "AFF C-Series", not just "AFF".
- **ASA (All SAN Array):** SAN-optimized all-flash storage; "ASA r2" is the current generation with distinct procedures from earlier ASA models.
- **FAS:** Hybrid flash/disk storage arrays; procedures are often similar to AFF but must be kept separate.
- **AFX / AFX 1K:** Newer all-flash platforms; use `afx_` prefixed include fragments.
- **FRU (field-replaceable unit):** Any hardware component that a customer can replace on-site (boot media, controller, DIMM, fan, NVDIMM, NVRAM, power supply, RTC battery, I/O module, system management module).
- **HA pair:** Two controllers operating in a high-availability configuration; most maintenance procedures require gracefully failing over to the partner before starting.
- **Impaired component terminology:** Reserve "impaired controller" for failures of components integral to the controller itself (DIMM, RTC battery, NVDIMM/NVRAM battery). For removable/modular FRUs (boot media, NVRAM module, I/O card), describe the component itself as impaired, not the controller.
- **BMR (boot media recovery):** Automated boot recovery introduced in ONTAP 9.17.1; platforms running earlier versions must use the manual USB-based recovery procedure. Both workflows exist for most modern platforms.
- **MetroCluster (MCC):** Two-site disaster recovery configuration; shutdown and recovery procedures differ from standard HA pair procedures and often use separate include files with the `_mcc` suffix (e.g., `shutdown_2n_mcc.adoc`).
- **NVDIMM / NVRAM:** Non-volatile memory used for write caching; replacing these components requires specific shutdown and recovery steps to avoid data loss.
- **Shared includes pattern:** Content in `_include/` is included by platform files using AsciiDoc `include::` directives. Generic fragments prefixed `g_` are reused by multiple modern platforms; platform-prefixed fragments (e.g., `a1k_`, `a70-90_`) are platform-specific.
- **Platform families share hardware:** The a70 and a90 share the same include fragments (prefixed `a70-90_`); similarly, a20, a30, and a50 share `a20-30-50` content.
- **NS224 shelf:** NVMe-attached drive shelf using NSM100 shelf modules; connected to controllers over 100GbE RoCE ports; content lives in `ns224/` and shared include fragments prefixed `ns224_`; supports hot-add (to AFF, ASA, and end-of-availability systems), hot-remove, cold shelf replacement, and individual FRU replacement (drive, NSM module, boot media, DIMM, fan, I/O module, power supply, RTC battery).
- **NX224 shelf:** Next-generation NVMe-attached drive shelf using NSM140 shelf modules; content lives in `nx224/`; currently supports hot-add drives and FRU replacement (drive, NSM module, boot media, DIMM, fan, I/O module, power supply, RTC battery); fewer procedures than NS224 due to newer platform lifecycle.
- **SAS shelves (DS212C, DS224C, DS460C):** SAS-attached shelves using IOM12, IOM12B, or IOM12C modules; content lives in `sas3/`; cabled in multipath HA, quad-path HA, or (for FAS2820) tri-path HA configurations; supports hot-add shelves and drives, cold shelf replacement, hot-remove, IOM hot-swap, and FRU replacement (drive, drawer for DS460C, fan for DS460C, power supply); cabling rules are a significant part of the documentation due to the complexity of SAS stack topologies.
- **Hot-add vs. cold-replace:** Hot-add procedures add a shelf to a running system without downtime; cold-replace procedures require the system to be shut down; hot-remove removes a shelf from a running system. NS224 and SAS shelves support all three; NX224 currently does not document hot-remove or cold-replace.
- **Shelf ID:** Each shelf in a stack must have a unique ID; procedures for changing the shelf ID exist for NS224 (`ns224/change-shelf-id.adoc`), NX224 (`nx224/change-shelf-id.adoc`), and SAS shelves (`sas3/install-change-shelf-id.adoc`).
- **NSM module (NS224/NX224):** The shelf I/O module for NVMe shelves; NSM100 is used in NS224 shelves, NSM140 is used in NX224 shelves; replacing an NSM module is a hot-swap procedure that does not require system shutdown.

## Typical user workflows

- **Hardware installation:** review requirements → prepare site → install hardware → cable controllers and shelves → power on → set up ONTAP cluster
- **FRU replacement (controller-integral components — DIMM, RTC battery, NVDIMM/NVRAM battery):** review requirements → shut down impaired controller → replace FRU → restore system configuration → complete RMA
- **FRU replacement (removable/modular components — e.g., NVRAM module, I/O module):** review requirements → shut down controller → replace FRU → restore system configuration → complete RMA
- **Boot media replacement (manual):** check encryption → shut down controller → replace boot media → boot from USB recovery image → restore encryption → complete RMA
- **Boot media replacement (automated, ONTAP 9.17.1+):** check encryption → shut down controller → replace boot media → run automated boot recovery → restore encryption → complete RMA
- **Controller replacement:** review requirements → shut down impaired controller → move hardware to replacement controller → recable and reassign disks → restore system config → complete RMA
- **NS224/NX224 shelf hot-add:** review requirements and best practices → prepare system (verify ONTAP version, firmware, cabling capacity) → install shelf in rack → cable shelf to controllers (platform-specific cabling file) → complete hot-add (verify shelf detection, update firmware if needed)
- **SAS shelf hot-add:** review cabling rules and worksheets → prepare cabling worksheet for the stack topology → install shelf → cable shelf-to-shelf and controller-to-stack connections per multipath HA or quad-path HA rules → verify stack
- **Shelf FRU replacement (NS224/NX224):** identify failed component via LEDs → hot-swap the FRU (drive, NSM module, power supply, fan, DIMM, boot media, I/O module, or RTC battery) → verify operation; most NS224/NX224 FRUs are hot-swappable without system downtime
- **SAS shelf FRU replacement:** identify failed component → hot-swap IOM, drive, or power supply (no downtime); DS460C-specific procedures cover drawer and fan replacement
- **Cold shelf replacement:** gracefully shut down the system → replace the shelf chassis → recable → power on → verify
