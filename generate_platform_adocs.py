import os
import glob
import xml.etree.ElementTree as ET
import re

def postprocess_adoc_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove b_start and b_end (and any text like b_start...b_end)
    content = re.sub(r'b_start(.*?)b_end', lambda m: m.group(1), content)
    # Remove any remaining b_start or b_end
    content = content.replace('b_start', '').replace('b_end', '')
    # Replace <br/> and <br> with newlines
    content = re.sub(r'<br\s*/?>', '\n', content)
    # Remove semicolons at end of lines
    content = re.sub(r';\s*$', '', content, flags=re.MULTILINE)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

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
    # All ASA R2 A1K, A70, A90, A20, A30, and A50 map to the same 'asa-r2-key-specifications' folder
    'asaa1k': 'asa-r2-key-specifications',
    'asaa70': 'asa-r2-key-specifications',
    'asaa90': 'asa-r2-key-specifications',
    'asaa20': 'asa-r2-key-specifications',
    'asaa30': 'asa-r2-key-specifications',
    'asaa50': 'asa-r2-key-specifications',
    #ASA C-Series models map to their respective folders
    # All other ASA models keep their current mapping
    'asaa900': 'asa900',
    'asaa800': 'asa800',
    'asaa400': 'asa400',
    'asa250': 'asa250',
    'asaa250': 'asa250',
    'asaa150': 'asa150',
}

def get_text(elem, tag, default=None):
    v = elem.findtext(tag)
    return v if v is not None and v.strip() != '' else default

def get_related(elems, key, value):
    return [e for e in elems if e.findtext(key) == value]

def sentence_case(s):
    if not s:
        return s
    s = s.strip()
    # Capitalize first letter, lowercase the rest, but preserve proper nouns and acronyms
    if len(s) > 1:
        return s[0].upper() + s[1:]
    return s.upper()

def clean_br(val):
    if not val:
        return ''
    return re.sub(r'<br\s*/?>', '\n', val, flags=re.IGNORECASE)

def adoc_bulleted_list(headers, rows):
    out = ''
    for row in rows:
        # Each row is a list of values, zipped with headers
        items = [f"{headers[i]}: {row[i]}" for i in range(len(headers)) if row[i]]
        if items:
            out += f"* {'; '.join(items)}\n"
    return out if out else 'No data available.\n'

# Add explicit FAS model to folder mapping for special cases
FAS_MODEL_TO_FOLDER = {
    'fas70': 'fas-70-90',
    'fas90': 'fas-70-90',
    'fas2750': 'fas2700',
    'fas2820': 'fas2800',
    'fas8300': 'fas8300',
    'fas8700': 'fas8300',
}

# Find all techspec XML files
folder_to_platformconfigs = {}
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
        # Explicit FAS model-to-folder mapping
        if model_key in FAS_MODEL_TO_FOLDER:
            folder = FAS_MODEL_TO_FOLDER[model_key]
        # Special handling for AFF C-Series, A-Series, and ASA A-Series
        elif prefix == 'aff-c-series' and model_key in C_SERIES_MODELS:
            folder = C_SERIES_MODELS[model_key]
        elif prefix == 'aff-a-series' and model_key in A_SERIES_MODELS:
            folder = A_SERIES_MODELS[model_key]
        elif prefix == 'asa-a-series' and model_key in ASA_SERIES_MODELS:
            folder = ASA_SERIES_MODELS[model_key]
        else:
            folder = NORMALIZED_FOLDER_MAP.get(model_key)
            if (not folder or not os.path.isdir(folder)) and (prefix in PLATFORM_FOLDER_MAP.values() and os.path.isdir(prefix)):
                folder = prefix
        if not folder or not os.path.isdir(folder):
            print(f"Skipping model '{model}' (normalized: '{model_key}') - no folder match for model or prefix '{prefix}'.")
            continue
        if folder not in folder_to_platformconfigs:
            folder_to_platformconfigs[folder] = []
        folder_to_platformconfigs[folder].append((pc, all_onboard, all_totalio, all_mgmt, all_env, all_compliance))

# Now, for each folder, generate a single overview.adoc with all models in that group
ASA_R2_KEY_SPECS_FOLDER = 'asa-r2-key-specifications'
ASA_R2_FOLDERS = ['asa-r2-a1k', 'asa-r2-70-90', 'asa-r2-a20-30-50']
ASA_R2_MODEL_TO_FILENAME = {
    'asa-r2-a1k': 'asa-r2-a1k-key-specifications.html',
    'asa-r2-70-90': {
        'ASA r2 A70': 'asa-r2-70-90/asa-a-series-asaa70-overview.html',
        'ASA r2 A90': 'asa-r2-70-90/asa-a-series-asaa90-overview.html',
    },
    'asa-r2-a20-30-50': {
        'ASA r2 A20': 'asa-r2-a20-30-50/asa-a-series-asaa20-overview.html',
        'ASA r2 A30': 'asa-r2-a20-30-50/asa-a-series-asaa30-overview.html',
        'ASA r2 A50': 'asa-r2-a20-30-50/asa-a-series-asaa50-overview.html',
    },
}
for folder, configs in folder_to_platformconfigs.items():
    # Special handling for ASA r2 key specifications (flat structure)
    if folder == 'asa-r2-key-specifications':
        for pc, all_onboard, all_totalio, all_mgmt, all_env, all_compliance in configs:
            model = get_text(pc, 'PlatformModel')
            # Generate a safe filename for each model
            model_key = model.lower().replace(' ', '-').replace('/', '-').replace('_', '-')
            adoc_path = os.path.join(folder, f'{model_key}-key-specifications.adoc')
            content = ''
            content += f"---\npermalink: {folder}/{model_key}-key-specifications.html\nsidebar: sidebar\nsummary: Key specifications for {model}\n---\n"
            content += f"= Key specifications for {model}\n:icons: font\n:imagesdir: ../media/\n\n[.lead]\nThe following are a selection of key specifications for {model} in a single high availability pair. Visit https://hwu.netapp.com[NetApp Hardware Universe^] (HWU) for a complete list of {model} specifications.\n\n"
            config = get_text(pc, 'PlatformConfig', '')
            max_capacity = get_text(pc, 'MaxRawCapacity_PB', '')
            memory = get_text(pc, 'PlatformMemory_GB', '')
            form_factor = get_text(pc, 'ControllerChassisFormFactor', '')
            os_version = get_text(pc, 'OSVersion', '')
            pci_slots = get_text(pc, 'PCIExpansionSlots', '')
            min_os = get_text(pc, 'MinOSVersion', '')
            ha = clean_br(get_text(pc, 'HighAvailability', ''))
            storage_networking = clean_br(get_text(pc, 'StorageNetworkingSupported', ''))
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
            pcid = get_text(pc, 'PlatformConfigId', '')
            onboard = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_onboard if get_text(e, 'PlatformConfigId', '') == pcid]
            totalio = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_totalio if get_text(e, 'PlatformConfigId', '') == pcid]
            mgmt = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_mgmt if get_text(e, 'PlatformConfigId', '') == pcid]
            envs = [e for e in all_env if get_text(e, 'PlatformConfigId', '') == pcid]
            env = envs[0] if envs else None
            pmid = get_text(pc, 'PlatformModelId', '')
            compliance = [e for e in all_compliance if get_text(e, 'PlatformModelId', '') == pmid]
            content += f"=== Key specifications for {model}\n\n"
            content += f"Platform Configuration: {config}\n\n"
            content += f"Max Raw Capacity: {max_capacity} PB\n\n"
            content += f"Memory: {memory} GB\n\n"
            content += f"Form Factor: {form_factor}\n\n"
            content += f"ONTAP Version: {os_version}\n\n"
            content += f"PCIe Expansion Slots: {pci_slots}\n\n"
            content += f"Minimum ONTAP Version: {min_os}\n\n"
            content += f"=== Scaleout Maximums\n" + adoc_bulleted_list([
                'Type', 'HA Pairs', 'Raw Capacity', 'Max Memory'], [
                ['NAS', scaleout['NAS HAPairs'], scaleout['NAS RawCapacity'], scaleout['NAS MaxMemory']],
                ['SAN', scaleout['SAN HAPairs'], scaleout['SAN RawCapacity'], scaleout['SAN MaxMemory']],
                ['HA Pair', '', scaleout['HA Pair RawCapacity'], scaleout['HA Pair MaxMemory']],
            ]) + '\n'
            content += f"=== IO\n\n==== Onboard IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], onboard) if onboard else 'No onboard IO data.\n')
            content += f"\n==== Total IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], totalio) if totalio else 'No total IO data.\n')
            content += f"\n==== Management Ports\n" + (adoc_bulleted_list(['Protocol', 'Ports'], mgmt) if mgmt else 'No management port data.\n')
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
            content += f"\n=== High Availability\n{ha}\n\n"
            os.makedirs(os.path.dirname(adoc_path), exist_ok=True)
            with open(adoc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            postprocess_adoc_file(adoc_path)
            print(f"Created {adoc_path}")
        continue  # Skip normal group output for this folder

    # Special handling for a70-90: generate separate files for A70 and A90
    if folder == 'a70-90':
        for pc, all_onboard, all_totalio, all_mgmt, all_env, all_compliance in configs:
            model = get_text(pc, 'PlatformModel')
            model_key = model.lower().replace(' ', '').replace('-', '').replace('_', '')
            if model_key == 'affa70':
                adoc_path = os.path.join(folder, 'a70-key-specifications.adoc')
                permalink = 'a70-key-specifications.html'
            elif model_key == 'affa90':
                adoc_path = os.path.join(folder, 'a90-key-specifications.adoc')
                permalink = 'a90-key-specifications.html'
            else:
                # For any other models, skip or handle as needed
                continue
            content = ''
            content += f"---\npermalink: {permalink}\nsidebar: sidebar\nsummary: Key specifications for {model}\n---\n"
            content += f"= Key specifications for {model}\n:icons: font\n:imagesdir: ../media/\n\n[.lead]\nThe following are a selection of key specifications for {model} in a single high availability pair. Visit https://hwu.netapp.com[NetApp Hardware Universe^] (HWU) for a complete list of {model} specifications.\n\n"
            config = get_text(pc, 'PlatformConfig', '')
            max_capacity = get_text(pc, 'MaxRawCapacity_PB', '')
            memory = get_text(pc, 'PlatformMemory_GB', '')
            form_factor = get_text(pc, 'ControllerChassisFormFactor', '')
            os_version = get_text(pc, 'OSVersion', '')
            pci_slots = get_text(pc, 'PCIExpansionSlots', '')
            min_os = get_text(pc, 'MinOSVersion', '')
            ha = clean_br(get_text(pc, 'HighAvailability', ''))
            storage_networking = clean_br(get_text(pc, 'StorageNetworkingSupported', ''))
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
            pcid = get_text(pc, 'PlatformConfigId', '')
            onboard = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_onboard if get_text(e, 'PlatformConfigId', '') == pcid]
            totalio = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_totalio if get_text(e, 'PlatformConfigId', '') == pcid]
            mgmt = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_mgmt if get_text(e, 'PlatformConfigId', '') == pcid]
            envs = [e for e in all_env if get_text(e, 'PlatformConfigId', '') == pcid]
            env = envs[0] if envs else None
            pmid = get_text(pc, 'PlatformModelId', '')
            compliance = [e for e in all_compliance if get_text(e, 'PlatformModelId', '') == pmid]
            content += f"=== Key specifications for {model}\n\n"
            content += f"Platform Configuration: {config}\n\n"
            content += f"Max Raw Capacity: {max_capacity} PB\n\n"
            content += f"Memory: {memory} GB\n\n"
            content += f"Form Factor: {form_factor}\n\n"
            content += f"ONTAP Version: {os_version}\n\n"
            content += f"PCIe Expansion Slots: {pci_slots}\n\n"
            content += f"Minimum ONTAP Version: {min_os}\n\n"
            content += f"=== Scaleout Maximums\n" + adoc_bulleted_list([
                'Type', 'HA Pairs', 'Raw Capacity', 'Max Memory'], [
                ['NAS', scaleout['NAS HAPairs'], scaleout['NAS RawCapacity'], scaleout['NAS MaxMemory']],
                ['SAN', scaleout['SAN HAPairs'], scaleout['SAN RawCapacity'], scaleout['SAN MaxMemory']],
                ['HA Pair', '', scaleout['HA Pair RawCapacity'], scaleout['HA Pair MaxMemory']],
            ]) + '\n'
            content += f"=== IO\n\n==== Onboard IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], onboard) if onboard else 'No onboard IO data.\n')
            content += f"\n==== Total IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], totalio) if totalio else 'No total IO data.\n')
            content += f"\n==== Management Ports\n" + (adoc_bulleted_list(['Protocol', 'Ports'], mgmt) if mgmt else 'No management port data.\n')
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
            content += f"\n=== High Availability\n{ha}\n\n"
            os.makedirs(os.path.dirname(adoc_path), exist_ok=True)
            with open(adoc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            postprocess_adoc_file(adoc_path)
            print(f"Created {adoc_path}")
        continue  # Skip normal group output for this folder

    # Special handling for a20-30-50: generate separate files for A20, A30, and A50
    if folder == 'a20-30-50':
        for pc, all_onboard, all_totalio, all_mgmt, all_env, all_compliance in configs:
            model = get_text(pc, 'PlatformModel')
            model_key = model.lower().replace(' ', '').replace('-', '').replace('_', '')
            if model_key == 'affa20':
                adoc_path = os.path.join(folder, 'a20-key-specifications.adoc')
                permalink = 'a20-key-specifications.html'
            elif model_key == 'affa30':
                adoc_path = os.path.join(folder, 'a30-key-specifications.adoc')
                permalink = 'a30-key-specifications.html'
            elif model_key == 'affa50':
                adoc_path = os.path.join(folder, 'a50-key-specifications.adoc')
                permalink = 'a50-key-specifications.html'
            else:
                continue
            content = ''
            content += f"---\npermalink: {permalink}\nsidebar: sidebar\nsummary: Key specifications for {model}\n---\n"
            content += f"= Key specifications for {model}\n:icons: font\n:imagesdir: ../media/\n\n[.lead]\nThe following are a selection of key specifications for {model} in a single high availability pair. Visit https://hwu.netapp.com[NetApp Hardware Universe^] (HWU) for a complete list of {model} specifications.\n\n"
            config = get_text(pc, 'PlatformConfig', '')
            max_capacity = get_text(pc, 'MaxRawCapacity_PB', '')
            memory = get_text(pc, 'PlatformMemory_GB', '')
            form_factor = get_text(pc, 'ControllerChassisFormFactor', '')
            os_version = get_text(pc, 'OSVersion', '')
            pci_slots = get_text(pc, 'PCIExpansionSlots', '')
            min_os = get_text(pc, 'MinOSVersion', '')
            ha = clean_br(get_text(pc, 'HighAvailability', ''))
            storage_networking = clean_br(get_text(pc, 'StorageNetworkingSupported', ''))
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
            pcid = get_text(pc, 'PlatformConfigId', '')
            onboard = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_onboard if get_text(e, 'PlatformConfigId', '') == pcid]
            totalio = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_totalio if get_text(e, 'PlatformConfigId', '') == pcid]
            mgmt = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_mgmt if get_text(e, 'PlatformConfigId', '') == pcid]
            envs = [e for e in all_env if get_text(e, 'PlatformConfigId', '') == pcid]
            env = envs[0] if envs else None
            pmid = get_text(pc, 'PlatformModelId', '')
            compliance = [e for e in all_compliance if get_text(e, 'PlatformModelId', '') == pmid]
            content += f"=== Key specifications for {model}\n\n"
            content += f"Platform Configuration: {config}\n\n"
            content += f"Max Raw Capacity: {max_capacity} PB\n\n"
            content += f"Memory: {memory} GB\n\n"
            content += f"Form Factor: {form_factor}\n\n"
            content += f"ONTAP Version: {os_version}\n\n"
            content += f"PCIe Expansion Slots: {pci_slots}\n\n"
            content += f"Minimum ONTAP Version: {min_os}\n\n"
            content += f"=== Scaleout Maximums\n" + adoc_bulleted_list([
                'Type', 'HA Pairs', 'Raw Capacity', 'Max Memory'], [
                ['NAS', scaleout['NAS HAPairs'], scaleout['NAS RawCapacity'], scaleout['NAS MaxMemory']],
                ['SAN', scaleout['SAN HAPairs'], scaleout['SAN RawCapacity'], scaleout['SAN MaxMemory']],
                ['HA Pair', '', scaleout['HA Pair RawCapacity'], scaleout['HA Pair MaxMemory']],
            ]) + '\n'
            content += f"=== IO\n\n==== Onboard IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], onboard) if onboard else 'No onboard IO data.\n')
            content += f"\n==== Total IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], totalio) if totalio else 'No total IO data.\n')
            content += f"\n==== Management Ports\n" + (adoc_bulleted_list(['Protocol', 'Ports'], mgmt) if mgmt else 'No management port data.\n')
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
            content += f"\n=== High Availability\n{ha}\n\n"
            os.makedirs(os.path.dirname(adoc_path), exist_ok=True)
            with open(adoc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            postprocess_adoc_file(adoc_path)
            print(f"Created {adoc_path}")
        continue  # Skip normal group output for this folder

    # Special handling for c30-60: generate separate files for C30 and C60
    if folder == 'c30-60':
        for pc, all_onboard, all_totalio, all_mgmt, all_env, all_compliance in configs:
            model = get_text(pc, 'PlatformModel')
            model_key = model.lower().replace(' ', '').replace('-', '').replace('_', '')
            if model_key == 'affc30':
                adoc_path = os.path.join(folder, 'c30-key-specifications.adoc')
                permalink = 'c30-key-specifications.html'
            elif model_key == 'affc60':
                adoc_path = os.path.join(folder, 'c60-key-specifications.adoc')
                permalink = 'c60-key-specifications.html'
            else:
                continue
            content = ''
            content += f"---\npermalink: {permalink}\nsidebar: sidebar\nsummary: Key specifications for {model}\n---\n"
            content += f"= Key specifications for {model}\n:icons: font\n:imagesdir: ../media/\n\n[.lead]\nThe following are a selection of key specifications for {model} in a single high availability pair. Visit https://hwu.netapp.com[NetApp Hardware Universe^] (HWU) for a complete list of {model} specifications.\n\n"
            config = get_text(pc, 'PlatformConfig', '')
            max_capacity = get_text(pc, 'MaxRawCapacity_PB', '')
            memory = get_text(pc, 'PlatformMemory_GB', '')
            form_factor = get_text(pc, 'ControllerChassisFormFactor', '')
            os_version = get_text(pc, 'OSVersion', '')
            pci_slots = get_text(pc, 'PCIExpansionSlots', '')
            min_os = get_text(pc, 'MinOSVersion', '')
            ha = clean_br(get_text(pc, 'HighAvailability', ''))
            storage_networking = clean_br(get_text(pc, 'StorageNetworkingSupported', ''))
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
            pcid = get_text(pc, 'PlatformConfigId', '')
            onboard = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_onboard if get_text(e, 'PlatformConfigId', '') == pcid]
            totalio = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_totalio if get_text(e, 'PlatformConfigId', '') == pcid]
            mgmt = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_mgmt if get_text(e, 'PlatformConfigId', '') == pcid]
            envs = [e for e in all_env if get_text(e, 'PlatformConfigId', '') == pcid]
            env = envs[0] if envs else None
            pmid = get_text(pc, 'PlatformModelId', '')
            compliance = [e for e in all_compliance if get_text(e, 'PlatformModelId', '') == pmid]
            content += f"=== Key specifications for {model}\n\n"
            content += f"Platform Configuration: {config}\n\n"
            content += f"Max Raw Capacity: {max_capacity} PB\n\n"
            content += f"Memory: {memory} GB\n\n"
            content += f"Form Factor: {form_factor}\n\n"
            content += f"ONTAP Version: {os_version}\n\n"
            content += f"PCIe Expansion Slots: {pci_slots}\n\n"
            content += f"Minimum ONTAP Version: {min_os}\n\n"
            content += f"=== Scaleout Maximums\n" + adoc_bulleted_list([
                'Type', 'HA Pairs', 'Raw Capacity', 'Max Memory'], [
                ['NAS', scaleout['NAS HAPairs'], scaleout['NAS RawCapacity'], scaleout['NAS MaxMemory']],
                ['SAN', scaleout['SAN HAPairs'], scaleout['SAN RawCapacity'], scaleout['SAN MaxMemory']],
                ['HA Pair', '', scaleout['HA Pair RawCapacity'], scaleout['HA Pair MaxMemory']],
            ]) + '\n'
            content += f"=== IO\n\n==== Onboard IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], onboard) if onboard else 'No onboard IO data.\n')
            content += f"\n==== Total IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], totalio) if totalio else 'No total IO data.\n')
            content += f"\n==== Management Ports\n" + (adoc_bulleted_list(['Protocol', 'Ports'], mgmt) if mgmt else 'No management port data.\n')
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
            content += f"\n=== High Availability\n{ha}\n\n"
            os.makedirs(os.path.dirname(adoc_path), exist_ok=True)
            with open(adoc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            postprocess_adoc_file(adoc_path)
            print(f"Created {adoc_path}")
        continue  # Skip normal group output for this folder

    # Special handling for fas-70-90: generate separate files for FAS 70 and FAS 90
    if folder == 'fas-70-90':
        for pc, all_onboard, all_totalio, all_mgmt, all_env, all_compliance in configs:
            model = get_text(pc, 'PlatformModel')
            model_key = model.lower().replace(' ', '').replace('-', '').replace('_', '')
            if model_key == 'fas70':
                adoc_path = os.path.join(folder, 'fas70-key-specifications.adoc')
                permalink = 'fas70-key-specifications.html'
            elif model_key == 'fas90':
                adoc_path = os.path.join(folder, 'fas90-key-specifications.adoc')
                permalink = 'fas90-key-specifications.html'
            else:
                continue
            content = ''
            content += f"---\npermalink: {permalink}\nsidebar: sidebar\nsummary: Key specifications for {model}\n---\n"
            content += f"= Key specifications for {model}\n:icons: font\n:imagesdir: ../media/\n\n[.lead]\nThe following are a selection of key specifications for {model} in a single high availability pair. Visit https://hwu.netapp.com[NetApp Hardware Universe^] (HWU) for a complete list of {model} specifications.\n\n"
            config = get_text(pc, 'PlatformConfig', '')
            max_capacity = get_text(pc, 'MaxRawCapacity_PB', '')
            memory = get_text(pc, 'PlatformMemory_GB', '')
            form_factor = get_text(pc, 'ControllerChassisFormFactor', '')
            os_version = get_text(pc, 'OSVersion', '')
            pci_slots = get_text(pc, 'PCIExpansionSlots', '')
            min_os = get_text(pc, 'MinOSVersion', '')
            ha = clean_br(get_text(pc, 'HighAvailability', ''))
            storage_networking = clean_br(get_text(pc, 'StorageNetworkingSupported', ''))
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
            pcid = get_text(pc, 'PlatformConfigId', '')
            onboard = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_onboard if get_text(e, 'PlatformConfigId', '') == pcid]
            totalio = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_totalio if get_text(e, 'PlatformConfigId', '') == pcid]
            mgmt = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_mgmt if get_text(e, 'PlatformConfigId', '') == pcid]
            envs = [e for e in all_env if get_text(e, 'PlatformConfigId', '') == pcid]
            env = envs[0] if envs else None
            pmid = get_text(pc, 'PlatformModelId', '')
            compliance = [e for e in all_compliance if get_text(e, 'PlatformModelId', '') == pmid]
            content += f"=== Key specifications for {model}\n\n"
            content += f"Platform Configuration: {config}\n\n"
            content += f"Max Raw Capacity: {max_capacity} PB\n\n"
            content += f"Memory: {memory} GB\n\n"
            content += f"Form Factor: {form_factor}\n\n"
            content += f"ONTAP Version: {os_version}\n\n"
            content += f"PCIe Expansion Slots: {pci_slots}\n\n"
            content += f"Minimum ONTAP Version: {min_os}\n\n"
            content += f"=== Scaleout Maximums\n" + adoc_bulleted_list([
                'Type', 'HA Pairs', 'Raw Capacity', 'Max Memory'], [
                ['NAS', scaleout['NAS HAPairs'], scaleout['NAS RawCapacity'], scaleout['NAS MaxMemory']],
                ['SAN', scaleout['SAN HAPairs'], scaleout['SAN RawCapacity'], scaleout['SAN MaxMemory']],
                ['HA Pair', '', scaleout['HA Pair RawCapacity'], scaleout['HA Pair MaxMemory']],
            ]) + '\n'
            content += f"=== IO\n\n==== Onboard IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], onboard) if onboard else 'No onboard IO data.\n')
            content += f"\n==== Total IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], totalio) if totalio else 'No total IO data.\n')
            content += f"\n==== Management Ports\n" + (adoc_bulleted_list(['Protocol', 'Ports'], mgmt) if mgmt else 'No management port data.\n')
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
            content += f"\n=== High Availability\n{ha}\n\n"
            os.makedirs(os.path.dirname(adoc_path), exist_ok=True)
            with open(adoc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            postprocess_adoc_file(adoc_path)
            print(f"Created {adoc_path}")
        continue  # Skip normal group output for this folder

    # Special handling for fas8300: generate separate files for FAS8300 and FAS8700
    if folder == 'fas8300':
        for pc, all_onboard, all_totalio, all_mgmt, all_env, all_compliance in configs:
            model = get_text(pc, 'PlatformModel')
            model_key = model.lower().replace(' ', '').replace('-', '').replace('_', '')
            if model_key == 'fas8300':
                adoc_path = os.path.join(folder, 'fas8300-key-specifications.adoc')
                permalink = 'fas8300-key-specifications.html'
            elif model_key == 'fas8700':
                adoc_path = os.path.join(folder, 'fas8700-key-specifications.adoc')
                permalink = 'fas8700-key-specifications.html'
            else:
                continue
            content = ''
            content += f"---\npermalink: {permalink}\nsidebar: sidebar\nsummary: Key specifications for {model}\n---\n"
            content += f"= Key specifications for {model}\n:icons: font\n:imagesdir: ../media/\n\n[.lead]\nThe following are a selection of key specifications for {model} in a single high availability pair. Visit https://hwu.netapp.com[NetApp Hardware Universe^] (HWU) for a complete list of {model} specifications.\n\n"
            config = get_text(pc, 'PlatformConfig', '')
            max_capacity = get_text(pc, 'MaxRawCapacity_PB', '')
            memory = get_text(pc, 'PlatformMemory_GB', '')
            form_factor = get_text(pc, 'ControllerChassisFormFactor', '')
            os_version = get_text(pc, 'OSVersion', '')
            pci_slots = get_text(pc, 'PCIExpansionSlots', '')
            min_os = get_text(pc, 'MinOSVersion', '')
            ha = clean_br(get_text(pc, 'HighAvailability', ''))
            storage_networking = clean_br(get_text(pc, 'StorageNetworkingSupported', ''))
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
            pcid = get_text(pc, 'PlatformConfigId', '')
            onboard = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_onboard if get_text(e, 'PlatformConfigId', '') == pcid]
            totalio = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_totalio if get_text(e, 'PlatformConfigId', '') == pcid]
            mgmt = [(get_text(e, 'ProtocolStack', ''), get_text(e, 'PortsCount', '')) for e in all_mgmt if get_text(e, 'PlatformConfigId', '') == pcid]
            envs = [e for e in all_env if get_text(e, 'PlatformConfigId', '') == pcid]
            env = envs[0] if envs else None
            pmid = get_text(pc, 'PlatformModelId', '')
            compliance = [e for e in all_compliance if get_text(e, 'PlatformModelId', '') == pmid]
            content += f"=== Key specifications for {model}\n\n"
            content += f"Platform Configuration: {config}\n\n"
            content += f"Max Raw Capacity: {max_capacity} PB\n\n"
            content += f"Memory: {memory} GB\n\n"
            content += f"Form Factor: {form_factor}\n\n"
            content += f"ONTAP Version: {os_version}\n\n"
            content += f"PCIe Expansion Slots: {pci_slots}\n\n"
            content += f"Minimum ONTAP Version: {min_os}\n\n"
            content += f"=== Scaleout Maximums\n" + adoc_bulleted_list([
                'Type', 'HA Pairs', 'Raw Capacity', 'Max Memory'], [
                ['NAS', scaleout['NAS HAPairs'], scaleout['NAS RawCapacity'], scaleout['NAS MaxMemory']],
                ['SAN', scaleout['SAN HAPairs'], scaleout['SAN RawCapacity'], scaleout['SAN MaxMemory']],
                ['HA Pair', '', scaleout['HA Pair RawCapacity'], scaleout['HA Pair MaxMemory']],
            ]) + '\n'
            content += f"=== IO\n\n==== Onboard IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], onboard) if onboard else 'No onboard IO data.\n')
            content += f"\n==== Total IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], totalio) if totalio else 'No total IO data.\n')
            content += f"\n==== Management Ports\n" + (adoc_bulleted_list(['Protocol', 'Ports'], mgmt) if mgmt else 'No management port data.\n')
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
            content += f"\n=== High Availability\n{ha}\n\n"
            os.makedirs(os.path.dirname(adoc_path), exist_ok=True)
            with open(adoc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            postprocess_adoc_file(adoc_path)
            print(f"Created {adoc_path}")
        continue  # Skip normal group output for this folder

    # Default: group output for all other folders
    adoc_path = os.path.join(folder, 'overview.adoc')
    content = ''
    # Compose a general header for the group
    content += f"---\npermalink: {folder}/overview.html\nsidebar: sidebar\nsummary: Key specifications for the {folder.upper()} platform group\n---\n"
    content += f"= Key specifications for {model}\n:icons: font\n:imagesdir: ../media/\n\n[.lead]\nThe following are a selection of key specifications for {model} in a single high availability pair. Visit https://hwu.netapp.com[NetApp Hardware Universe^] (HWU) for a complete list of {model} specifications.\n\n"
    for pc, all_onboard, all_totalio, all_mgmt, all_env, all_compliance in configs:
        model = get_text(pc, 'PlatformModel')
        # Fix heading hierarchy: '===' -> '==', '====' -> '===', '=====' -> '===='
        content += f"== {sentence_case(f'Key specifications for {model}')}\n\n"
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
        content += f"== {sentence_case(f'Key specifications for {model}')}\n\n"
        content += f"Platform Configuration: {config}\n\n"
        content += f"Max Raw Capacity: {max_capacity} PB\n\n"
        content += f"Memory: {memory} GB\n\n"
        content += f"Form Factor: {form_factor}\n\n"
        content += f"ONTAP Version: {os_version}\n\n"
        content += f"PCIe Expansion Slots: {pci_slots}\n\n"
        content += f"Minimum ONTAP Version: {min_os}\n\n"
        content += f"== {sentence_case('Scaleout maximums')}\n" + adoc_bulleted_list([
            'Type', 'HA Pairs', 'Raw Capacity', 'Max Memory'], [
            ['NAS', scaleout['NAS HAPairs'], scaleout['NAS RawCapacity'], scaleout['NAS MaxMemory']],
            ['SAN', scaleout['SAN HAPairs'], scaleout['SAN RawCapacity'], scaleout['SAN MaxMemory']],
            ['HA Pair', '', scaleout['HA Pair RawCapacity'], scaleout['HA Pair MaxMemory']],
        ]) + '\n'
        content += f"== {sentence_case('IO')}\n\n=== {sentence_case('Onboard IO')}\n" + (adoc_bulleted_list(['Protocol', 'Ports'], onboard) if onboard else 'No onboard IO data.\n')
        content += f"\n=== Total IO\n" + (adoc_bulleted_list(['Protocol', 'Ports'], totalio) if totalio else 'No total IO data.\n')
        content += f"\n=== Management Ports\n" + (adoc_bulleted_list(['Protocol', 'Ports'], mgmt) if mgmt else 'No management port data.\n')
        content += f"\n== Storage Networking Supported\n{storage_networking}\n\n"
        content += f"== {sentence_case('System environment specifications')}\n"
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
        content += f"\n== Compliance\n"
        if compliance:
            for c in compliance:
                std = get_text(c, 'StandardType', '')
                val = clean_br(get_text(c, 'storageNetworkingSupported', ''))
