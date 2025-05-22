import os
import glob
import xml.etree.ElementTree as ET
import re

# Map platform model to folder (add more as needed)
PLATFORM_FOLDER_MAP = {
    'A150': 'a150',
    'A1K': 'a1k',
    'A20-30-50': 'a20-30-50',
    'A200': 'a200',
    'A220': 'a220',
    'A250': 'a250',
    'A300': 'a300',
    'A320': 'a320',
    'A400': 'a400',
    'A70-90': 'a70-90',
    'A700': 'a700',
    'A700S': 'a700s',
    'A800': 'a800',
    'A900': 'a900',
    'AFF-ASERIES': 'aff-aseries',
    'AFF-CSERIES': 'aff-cseries',
    'AFF-LANDING': 'aff-landing',
    'ALLSAN-A-SERIES': 'allsan-a-series',
    'ALLSAN-C-SERIES': 'allsan-c-series',
    'ALLSAN-LANDING': 'allsan-landing',
    'ASA-C250': 'asa-c250',
    'ASA-C400': 'asa-c400',
    'ASA-C800': 'asa-c800',
    'ASA-R2': 'asa-r2',
    'ASA-R2-70-90': 'asa-r2-70-90',
    'ASA-R2-A1K': 'asa-r2-a1k',
    'ASA-R2-A20-30-50': 'asa-r2-a20-30-50',
    'ASA-R2-LANDING-MAINTAIN': 'asa-r2-landing-maintain',
    'ASA150': 'asa150',
    'ASA250': 'asa250',
    'ASA400': 'asa400',
    'ASA800': 'asa800',
    'ASA900': 'asa900',
    'C190': 'c190',
    'C250': 'c250',
    'C30-60': 'c30-60',
    'C400': 'c400',
    'C80': 'c80',
    'C800': 'c800',
    'DRIVE-SHELVES': 'drive-shelves',
    'ENDOFAVAIL': 'endofavail',
    'FAS': 'fas',
    'FAS-70-90': 'fas-70-90',
    'FAS2600': 'fas2600',
    'FAS2700': 'fas2700',
    'FAS2800': 'fas2800',
    'FAS50': 'fas50',
    'FAS500F': 'fas500f',
    'FAS8200': 'fas8200',
    'FAS8300': 'fas8300',
    'FAS9000': 'fas9000',
    'FAS9500': 'fas9500',
    'MEDIA': 'media',
    'NS224': 'ns224',
    'OTHER': 'other',
    'PLATFORM-SUPPLEMENTAL': 'platform-supplemental',
    'SAS3': 'sas3',
    'STORE-REDIRECTS': 'store-redirects',
}

# Normalize keys for better matching
NORMALIZED_FOLDER_MAP = {k.lower().replace('-', '').replace('_', ''): v for k, v in PLATFORM_FOLDER_MAP.items()}

# Map platform type id to prefix for adoc file naming
PLATFORM_TYPE_PREFIX = {
    '2032': 'fas',
    '5265148': 'aff-a-series',
    '13684325': 'asa-aff-a-series',
    '30310846': 'aff-c-series',
    '31745792': 'asa-a-series',
    '32834061': 'asa-c-series',
}

# Add special handling for AFF C-Series and A-Series folder mapping
C_SERIES_MODELS = {
    'affc30': 'c30-60',
    'affc60': 'c30-60',
    'affc250': 'c250',
    'affc400': 'c400',
    'affc800': 'c800',
    'affc80': 'c80',
}
A_SERIES_MODELS = {
    'affa50': 'a20-30-50',
    'affa20': 'a20-30-50',
    'affa30': 'a20-30-50',
    'affa1k': 'a1k',
    'affa90': 'a70-90',
    'affa70': 'a70-90',
    'affa900': 'a900',
    'affa400': 'a400',
    'affa800': 'a800',
    'affa150': 'a150',
    'affa200': 'a200',
    'affa220': 'a220',
    'affa250': 'a250',
    'affa300': 'a300',
    'affa320': 'a320',
    # Add more as needed for all AFF A models
}
ASA_SERIES_MODELS = {
    'asaa50': 'asa-r2-a20-30-50',
    'asaa30': 'asa-r2-a20-30-50',
    'asaa900': 'asa900',
    'asaa800': 'asa800',
    'asaa400': 'asa400',
    'asa250': 'asa250',
    'asaa250': 'asa250',
    'asaa1k': 'asa-r2-a1k',
    'asaa90': 'asa-r2-70-90',
    'asaa70': 'asa-r2-70-90',
    'asaa150': 'asa150',
    'asaa20': 'asa-r2-a20-30-50',
}

def get_text(elem, tag, default=None):
    v = elem.findtext(tag)
    return v if v is not None and v.strip() != '' else default

def get_related(elems, key, value):
    return [e for e in elems if e.findtext(key) == value]

def clean_br(val):
    if not val:
        return ''
    return re.sub(r'<br\s*/?>', '\n', val, flags=re.IGNORECASE)

def adoc_table(headers, rows):
    out = f"|===\n| {' | '.join(headers)}\n"
    for row in rows:
        out += '| ' + ' | '.join(row) + '\n'
    out += '|===\n'
    return out

# Find all techspec XML files
for xml_file in glob.glob('techspec_*.xml'):
    # Extract platform type id from filename
    platform_type_id = xml_file.split('_')[1].split('.')[0]
    prefix = PLATFORM_TYPE_PREFIX.get(platform_type_id, 'platform')
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # Collect all related sections for cross-referencing
    all_onboard = root.findall('.//OnboardPortsIO')
    all_totalio = root.findall('.//TotalIOPorts')
    all_mgmt = root.findall('.//ManagementPorts')
    all_env = root.findall('.//EnvironmentSpec')
    all_compliance = root.findall('.//Compliance')
    # Find all PlatformConfig elements
    for pc in root.findall('.//PlatformConfig'):
        model = get_text(pc, 'PlatformModel')
        if not model:
            continue
        # Normalize model key for matching
        model_key = model.lower().replace(' ', '').replace('-', '').replace('_', '')
        # Special handling for AFF C-Series, A-Series, and ASA A-Series
        if prefix == 'aff-c-series' and model_key in C_SERIES_MODELS:
            folder = C_SERIES_MODELS[model_key]
        elif prefix == 'aff-a-series' and model_key in A_SERIES_MODELS:
            folder = A_SERIES_MODELS[model_key]
        elif prefix == 'asa-a-series' and model_key in ASA_SERIES_MODELS:
            folder = ASA_SERIES_MODELS[model_key]
        else:
            folder = NORMALIZED_FOLDER_MAP.get(model_key)
            # If not found, try prefix folder (e.g., aff-aseries, fas, etc.)
            if (not folder or not os.path.isdir(folder)) and (prefix in PLATFORM_FOLDER_MAP.values() and os.path.isdir(prefix)):
                folder = prefix
        if not folder or not os.path.isdir(folder):
            print(f"Skipping model '{model}' (normalized: '{model_key}') - no folder match for model or prefix '{prefix}'.")
            continue
        adoc_name = f"{prefix}-{model_key}-overview.adoc"
        adoc_path = os.path.join(folder, adoc_name)
        # Extract main fields
        config = get_text(pc, 'PlatformConfig', '')
        max_capacity = get_text(pc, 'MaxRawCapacity_PB', '')
        memory = get_text(pc, 'PlatformMemory_GB', '')
        form_factor = get_text(pc, 'ControllerChassisFormFactor', '')
        os_version = get_text(pc, 'OSVersion', '')
        pci_slots = get_text(pc, 'PCIExpansionSlots', '')
        min_os = get_text(pc, 'MinOSVersion', '')
        ha = clean_br(get_text(pc, 'HighAvailability', ''))
        storage_networking = clean_br(get_text(pc, 'StorageNetworkingSupported', ''))
        # Scaleout
        scaleout = {
            'NAS HAPairs': get_text(pc, 'NASScaleOut_HAPairs', ''),
            'NAS RawCapacity': get_text(pc, 'NASScaleOut_RawCapacity', ''),
            'NAS MaxMemory': get_text(pc, 'NASScaleOut_MaxMemory', ''),
            'SAN HAPairs': get_text(pc, 'SANScaleOut_HAPAirs', ''),
            'SAN RawCapacity': get_text(pc, 'SANScaleOut_RawCapacity', ''),
            'SAN MaxMemory': get_text(pc, 'SANScaleOut_MaxMemory', ''),
            'HA Pair RawCapacity': get_text(pc, 'HAPair_RawCapacity', ''),
            'HA Pair MaxMemory': memory,
        }
        # IO tables
        pcid = get_text(pc, 'PlatformConfigId', '')
        onboard = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_onboard if get_text(e, 'PlatformConfigId', '') == pcid]
        totalio = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_totalio if get_text(e, 'PlatformConfigId', '') == pcid]
        mgmt = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_mgmt if get_text(e, 'PlatformConfigId', '') == pcid]
        # System environment
        envs = [e for e in all_env if get_text(e, 'PlatformConfigId', '') == pcid]
        env = envs[0] if envs else None
        # Compliance
        pmid = get_text(pc, 'PlatformModelId', '')
        compliance = [e for e in all_compliance if get_text(e, 'PlatformModelId', '') == pmid]
        # Build adoc content with general header
        permalink = f"{folder}/specifications.html"
        keywords = f"{model} specifications, {model} specs, NetApp {model}, {model} hardware"
        summary = f"Key specifications for the {model} storage system"
        adoc_title = f"Key specifications for {model}"
        lead = f"The following are select specifications for the {model}. Visit https://hwu.netapp.com[NetApp Hardware Universe^] (HWU) for a complete list of {model} specifications. This page is reflective of a single high availability pair. "
        content = f"---\npermalink: {permalink}\nsidebar: sidebar\nkeywords: {keywords}\nsummary: {summary}\n---\n"
        content += f"= {adoc_title}\n:icons: font\n:imagesdir: ../media/\n\n[.lead]\n{lead}\n\n=== Key specifications for {model}\n\n"
        content += f"Platform Configuration: {config}\n\n"
        content += f"Max Raw Capacity: {max_capacity} PB\n\n"
        content += f"Memory: {memory} GB\n\n"
        content += f"Form Factor: {form_factor}\n\n"
        content += f"ONTAP Version: {os_version}\n\n"
        content += f"PCIe Expansion Slots: {pci_slots}\n\n"
        content += f"Minimum ONTAP Version: {min_os}\n\n"
        content += f"=== Scaleout Maximums\n" + adoc_table([
            'Type', 'HA Pairs', 'Raw Capacity', 'Max Memory'], [
            ['NAS', scaleout['NAS HAPairs'], scaleout['NAS RawCapacity'], scaleout['NAS MaxMemory']],
            ['SAN', scaleout['SAN HAPairs'], scaleout['SAN RawCapacity'], scaleout['SAN MaxMemory']],
            ['HA Pair', '', scaleout['HA Pair RawCapacity'], scaleout['HA Pair MaxMemory']],
        ]) + '\n'
        content += f"=== IO\n\n==== Onboard IO\n" + (adoc_table(['Protocol', 'Ports'], onboard) if onboard else 'No onboard IO data.\n')
        content += f"\n==== Total IO\n" + (adoc_table(['Protocol', 'Ports'], totalio) if totalio else 'No total IO data.\n')
        content += f"\n==== Management Ports\n" + (adoc_table(['Protocol', 'Ports'], mgmt) if mgmt else 'No management port data.\n')
        content += f"\n=== Storage Networking Supported\n{storage_networking}\n\n"
        content += f"=== System Environment Specifications\n"
        if env:
            content += f"* Typical Power: {get_text(env, 'BtusPerHourTypical', '')}\n"
            content += f"* Worst-case Power: {get_text(env, 'BtusPerHourWorst', '')}\n"
            content += f"* Weight: {get_text(env, 'Weight', '')}\n"
            content += f"* Height: {get_text(env, 'Height', '')}\n"
            content += f"* Width: {get_text(env, 'Width', '')}\n"
            content += f"* Depth: {get_text(env, 'Depth', '')}\n"
            content += f"* Operating Temp/Altitude/Humidity: {get_text(env, 'Operating_Temp_Alt_Rel_Humidity', '')}\n"
            content += f"* Non-operating Temp/Humidity: {get_text(env, 'Nonoperating_Temp_Rel_Humidity', '')}\n"
            content += f"* Acoustic Noise: {get_text(env, 'Operating_Acoustic_Noise', '')}\n"
        else:
            content += "No environment data available.\n"
        content += f"\n=== Compliance\n"
        if compliance:
            for c in compliance:
                std = get_text(c, 'StandardType', '')
                val = clean_br(get_text(c, 'storageNetworkingSupported', ''))
                content += f"* {std}: {val}\n"
        else:
            content += "No compliance data available.\n"
        content += f"\n=== High Availability\n{ha}\n"
        # Write .adoc file
        with open(adoc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created {adoc_path}")
