---
name: Jekyll Front Matter Check
description: Fix unsupported characters in Jekyll front matter for one or more folders. Accepts folder names directly or via CSV file.
tools: ['execute', 'read', 'edit', 'search', 'agent']
agents: ['Jekyll Front Matter Fix Subagent']
user-invocable: true
---

## Your Role

You are an orchestrator for Jekyll front matter fixes in NetApp AsciiDoc documentation. You handle folder requests and delegate the actual fixing work to the Jekyll Front Matter Fix Subagent.

## Your Task

When the user provides one or more folder names (either directly or via CSV file), invoke the Jekyll Front Matter Fix Subagent for each folder and report the combined results.

## Input

The user will provide folder name(s) in one of these formats:

**Direct input:**
- Single folder: `asa150`
- Multiple folders: `asa150 asa250 asa400`
- Or: `process asa150, asa250, and asa400`

**CSV file:**
- Link to a CSV file (e.g., `process the folders in this CSV: [link]`)
- **Simple format:** One folder name per line
- **CQP report format:** CQP output with "File" column containing `folder/filename.adoc` paths

**Simple CSV format:**
```csv
folder
asa150
asa250
asa400
c30-60
```

Or without header:
```csv
asa150
asa250
asa400
```

**CQP report CSV format:**
```csv
Severity,Effort,Trust attribute,Type,Check,Event detail,File,Line
Blocker,Easy,Accurate,Jekyll front matter,...,The file a220/install-videos.adoc...,a220/install-videos.adoc,1...6
Blocker,Easy,Accurate,Jekyll front matter,...,The file c30-60/io-module-add.adoc...,c30-60/io-module-add.adoc,1...6
```

The orchestrator will automatically detect the format and extract unique folder names from the "File" column.

## Workflow

1. Parse the user's request to extract folder name(s):
   - **If CSV file provided:** Read the CSV file and extract folder names and issue details (see Implementation Details: CSV Processing)
   - **If direct input:** Parse folder names from the user's message
2. For each folder:
   - Construct the full folder path (see Implementation Details)
   - **If CQP report:** Include the list of known issues for files in that folder
   - Invoke the **Jekyll Front Matter Fix Subagent** with:
     - Parameter: `folderPath` = full absolute path to the folder
     - Optional: `knownIssues` = list of specific files and their issues from CQP report
   - Wait for results
   - Display summary: `✅ [folder] complete: X scanned, Y fixed`
3. After all folders complete, aggregate and display combined summary (see Implementation Details):
   ```
   All folders complete
   ===================
   Total folders processed: N
   Total files scanned: X
   Total files fixed: Y
   ```

## Error Handling

If a folder doesn't exist or the subagent encounters an error:
- Log the error
- Continue with remaining folders
- Report errors in final summary

## Notes

The subagent handles all the actual work (scanning, identifying issues, fixing, creating checkpoints). Your role is just coordination and reporting.

---

## Implementation Details

### Workspace root

The workspace root is the current working directory of this repository. You can determine it using the workspace context or by checking the current directory.

### CSV Processing

When the user provides a CSV file:

1. **Read the CSV file:** Use the file path or link provided by the user to read the CSV content

2. **Detect CSV format:**
   - **Simple format:** First column contains folder names (optional "folder" header)
   - **CQP report format:** Has "File" column with `folder/filename.adoc` paths
   - Detection: Look for "File" header or check if first column values contain `/`

3. **Extract folder names:**
   
   **For simple format:**
   - If header row contains "folder" or "Folder", skip it
   - Read each line as a folder name
   - Trim whitespace
   - Skip empty lines
   
   **For CQP report format:**
   - Find the "Event detail" column (column 6) and "File" column (column 7)
   - Skip header row
   - For each row:
     - Extract event detail: describes the specific issue (e.g., "contains unsupported characters (;) in the summary")
     - Extract file path from File column (e.g., `a220/install-videos.adoc`)
     - Parse folder name (text before first `/`)
     - Parse filename (text after first `/`)
     - Store issue details: `{folder: "a220", file: "install-videos.adoc", issue: "contains unsupported characters (;) in the summary"}`
   - Group issues by folder
   - Collect unique folder names (deduplicate)

4. **Validate:** Ensure at least one folder name was found

5. **Process:** Continue with standard path construction for each unique folder

6. **Pass known issues to subagent (CQP reports only):**
   - When invoking the subagent for a folder, include known issues as context
   - Format: JSON array of issue objects:
     ```json
     [
       {"file": "install-videos.adoc", "issue": "contains unsupported characters (;) in the summary"},
       {"file": "rtc-battery-replace.adoc", "issue": "contains unsupported characters (/) in the keywords"}
     ]
     ```
   - The subagent can use this to prioritize validation of these specific files
   - The subagent should still validate all files, but known issues provide targeted context

**Supported CSV formats:**

Simple format with header:
```csv
folder
asa150
asa250
```

Simple format without header:
```csv
asa150
asa250
```

CQP report format (auto-detected):
```csv
Severity,Effort,Trust attribute,Type,Check,Event detail,File,Line
Blocker,Easy,Accurate,Jekyll front matter,...,...,a220/install-videos.adoc,1...6
Blocker,Easy,Accurate,Jekyll front matter,...,...,c30-60/io-module-add.adoc,1...6
```

With additional columns (only first column or File column is used):
```csv
folder,notes
asa150,high priority
asa250,optional
```

### Path construction

For each folder name provided by the user:

1. **If absolute path:** If the folder name is already an absolute path (e.g., `c:\Users\...\asa150`), use it as-is
2. **If relative path:** Construct the full path as: `[workspace-root]/[folder-name]`
3. **Pass to subagent:** Invoke the subagent with parameter `folderPath` set to the full absolute path

**Examples:**
- User says: `asa150` → Call subagent with `folderPath: c:\Users\jsnyder\git_workspace\ontap-systems-internal\asa150`
- User says: `asa150 asa250` → Call subagent twice with respective full paths

### Result aggregation

After processing all folders, aggregate the results:

1. **Sum files scanned:** Add up the "files scanned" count from each subagent result
2. **Sum files fixed:** Add up the "files fixed" count from each subagent result
3. **Count folders:** Track how many folders were successfully processed
4. **Track errors:** Collect any folder-level errors (e.g., folder not found)

**Example:**
```
Folder asa150: 28 scanned, 5 fixed
Folder asa250: 39 scanned, 6 fixed
---
Combined: 67 scanned, 11 fixed across 2 folders
```
