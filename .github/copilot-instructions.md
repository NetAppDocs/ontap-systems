# Copilot instructions for ONTAP hardware systems documentation

## Repository overview

Product: NetApp ONTAP hardware systems (AFF, ASA, FAS, and AFX storage platforms)

This repository contains installation and maintenance documentation for NetApp ONTAP storage hardware, including step-by-step procedures for hardware installation, FRU replacement, and system recovery across all supported platform families.

## Repository structure

- `_include/` – Reusable AsciiDoc content fragments shared across platform directories; files are prefixed with the platform model (e.g., `a1k_`, `a70-90_`, `800_`) or are generic (e.g., `g_`, `afx_`)
- `a1k/`, `a20-30-50/`, `a70-90/`, `a200/`–`a900/` – AFF A-Series platform-specific content (install and maintain)
- `c250/`, `c400/`, `c800/`, `c80/`, `c30-60/` – AFF C-Series platform-specific content
- `asa150/`–`asa900/`, `asa-c250/`–`asa-c800/` – ASA (All SAN Array) platform content
- `asa-r2/`, `asa-r2-a1k/`, `asa-r2-a20-30-50/`, `asa-r2-70-90/`, `asa-r2-c30/` – ASA r2 generation content; some procedures differ from earlier ASA and AFF
- `fas2600/`–`fas9500/`, `fas50/`, `fas70-90/` – FAS hybrid storage platform content
- `afx/`, `afx-1k/` – AFX all-flash platform content
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
- **BMR (boot media recovery):** Automated boot recovery introduced in ONTAP 9.17.1; platforms running earlier versions must use the manual USB-based recovery procedure. Both workflows exist for most modern platforms.
- **MetroCluster (MCC):** Two-site disaster recovery configuration; shutdown and recovery procedures differ from standard HA pair procedures and often use separate include files (e.g., `shutdown_2n_mcc.adoc`).
- **NVDIMM / NVRAM:** Non-volatile memory used for write caching; replacing these components requires specific shutdown and recovery steps to avoid data loss.
- **Shared includes pattern:** Content in `_include/` is included by platform files using AsciiDoc `include::` directives. Generic fragments prefixed `g_` are reused by multiple modern platforms; platform-prefixed fragments (e.g., `a1k_`, `a70-90_`) are platform-specific.
- **File-naming convention:** Within a platform directory, files follow the pattern `{component}-{action}.adoc` (e.g., `bootmedia-replace.adoc`, `controller-replace-workflow.adoc`). Workflow (overview) files end in `-workflow.adoc`.
- **AsciiDoc front matter:** Every content file begins with a YAML front matter block containing `permalink`, `sidebar`, `keywords`, and `summary` fields, followed by the level-1 heading (`= Title`) and `[.lead]` paragraph.
- **Platform families share hardware:** The a70 and a90 share the same include fragments (prefixed `a70-90_`); similarly, a20, a30, and a50 share `a20-30-50` content.

## Typical user workflows

- **Hardware installation:** review requirements → prepare site → install hardware → cable controllers and shelves → power on → set up ONTAP cluster
- **FRU replacement (most components):** review requirements → check encryption status → shut down impaired controller → replace FRU → restore system configuration → complete RMA
- **Boot media replacement (manual):** check encryption → shut down controller → replace boot media → boot from USB recovery image → restore encryption → complete RMA
- **Boot media replacement (automated, ONTAP 9.17.1+):** check encryption → shut down controller → replace boot media → run automated boot recovery → restore encryption → complete RMA
- **Controller replacement:** review requirements → shut down impaired controller → move hardware to replacement controller → recable and reassign disks → restore system config → complete RMA