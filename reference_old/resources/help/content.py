from pathlib import Path
import base64
import logging

# Add debug logging
logger = logging.getLogger('AutoCADExcelTool.HelpContent')

def get_image_data(image_name):
    """Load image from resources and convert to base64"""
    image_path = Path(__file__).parent / "images" / image_name
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

HELP_CONTENT = {
    "Getting Started": {  # Main category
        "title": "Getting Started",
        "content": """<h2>Getting Started</h2>
            <p>Welcome to the AutoCAD Excel Tool. Choose a topic below to begin:</p>
            <ul>
                <li><a href="#quick-start-guide">Quick Start Guide</a></li>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#system-requirements">System Requirements</a></li>
            </ul>
        """
    },
    "Quick Start Guide": {  # This should match exactly with the tree item ID
        "title": "Quick Start Guide",
        "content": """
            <h2>Quick Start Guide</h2>
            
            <div class="section">
                <h3>Getting Started in 5 Minutes</h3>
                <ol>
                    <li><strong>Load Your Drawing</strong>
                        <ul>
                            <li>Click 'Open Drawing' or drag and drop a DWG/DXF file</li>
                            <li>The drawing preview will appear in the main window</li>
                            <li>Layers will be automatically loaded into the layer panel</li>
                        </ul>
                    </li>
                    <li><strong>Configure Basic Field Mapping</strong>
                        <ul>
                            <li>Click 'Field Mapping' in the toolbar</li>
                            <li>Add essential fields (NUMBER, SOURCE, DESTINATION)</li>
                            <li>Set basic patterns (e.g., "W*" for cable numbers)</li>
                        </ul>
                    </li>
                    <li><strong>Select Relevant Layers</strong>
                        <ul>
                            <li>Enable layers containing cable information</li>
                            <li>Common layers: CABLE_NUM, EQUIPMENT, TEXT</li>
                            <li>Use the layer filter to find specific layers</li>
                        </ul>
                    </li>
                    <li><strong>Test Extraction</strong>
                        <ul>
                            <li>Click 'Preview' to test your settings</li>
                            <li>Verify extracted data in the preview grid</li>
                            <li>Adjust patterns if needed</li>
                        </ul>
                    </li>
                    <li><strong>Export to Excel</strong>
                        <ul>
                            <li>Click 'Export' when satisfied with the preview</li>
                            <li>Choose export location and format</li>
                            <li>Open the exported file to verify results</li>
                        </ul>
                    </li>
                </ol>

                <h3>Video Tutorials</h3>
                <p>Quick start video guides:</p>
                <ul>
                    <li><a href="#basic-extraction">Basic Cable Extraction (5 min)</a></li>
                    <li><a href="#field-mapping">Field Mapping Tutorial (7 min)</a></li>
                    <li><a href="#advanced-features">Advanced Features (10 min)</a></li>
                </ul>
            </div>
        """
    },
    "Overview": {
        "title": "Overview",
        "content": """
            <h2>AutoCAD Excel Tool Overview</h2>
            
            <div class="section">
                <h3>Purpose</h3>
                <p>This tool streamlines the process of extracting cable information from AutoCAD drawings into organized Excel spreadsheets.</p>
                
                <h3>Key Features</h3>
                <ul>
                    <li>Extract cable numbers, sources, and destinations automatically</li>
                    <li>Configurable pattern matching for text recognition</li>
                    <li>Layer-based filtering and organization</li>
                    <li>Customizable Excel export formats</li>
                    <li>Save and load configurations for different projects</li>
                </ul>
            </div>
        """
    },
    "System Requirements": {
        "title": "System Requirements",
        "content": """
            <h2>System Requirements</h2>
            
            <div class="section">
                <h3>Minimum Requirements</h3>
                <table>
                    <tr>
                        <th>Component</th>
                        <th>Minimum</th>
                        <th>Recommended</th>
                    </tr>
                    <tr>
                        <td>Operating System</td>
                        <td>Windows 10 (64-bit)</td>
                        <td>Windows 10/11 (64-bit)</td>
                    </tr>
                    <tr>
                        <td>Processor</td>
                        <td>Intel Core i3 or equivalent</td>
                        <td>Intel Core i5/i7 or equivalent</td>
                    </tr>
                    <tr>
                        <td>Memory</td>
                        <td>4GB RAM</td>
                        <td>8GB+ RAM</td>
                    </tr>
                    <tr>
                        <td>Storage</td>
                        <td>500MB free space</td>
                        <td>1GB+ free space</td>
                    </tr>
                    <tr>
                        <td>Display</td>
                        <td>1366x768</td>
                        <td>1920x1080 or higher</td>
                    </tr>
                </table>

                <h3>Software Dependencies</h3>
                <ul>
                    <li><strong>Required:</strong>
                        <ul>
                            <li>Python 3.8 or higher</li>
                            <li>PyQt6</li>
                            <li>OpenPyXL for Excel operations</li>
                            <li>ezdxf for DWG/DXF processing</li>
                        </ul>
                    </li>
                    <li><strong>Optional:</strong>
                        <ul>
                            <li>AutoCAD Object Enabler (for advanced DWG support)</li>
                            <li>PDF export capability (requires reportlab)</li>
                            <li>Network license manager (for enterprise deployments)</li>
                        </ul>
                    </li>
                </ul>

                <h3>File Format Support</h3>
                <table>
                    <tr>
                        <th>Format</th>
                        <th>Versions</th>
                        <th>Notes</th>
                    </tr>
                    <tr>
                        <td>DWG</td>
                        <td>R14 through 2024</td>
                        <td>Full support for all entities</td>
                    </tr>
                    <tr>
                        <td>DXF</td>
                        <td>R14 through 2024</td>
                        <td>ASCII and Binary</td>
                    </tr>
                    <tr>
                        <td>Excel</td>
                        <td>2007-2021 (.xlsx)</td>
                        <td>Full formatting support</td>
                    </tr>
                </table>
            </div>
        """
    },

    # Field Mapping
    "Understanding Field Mapping": {
        "title": "Understanding Field Mapping",
        "content": """
            <h2>Understanding Field Mapping</h2>
            
            <div class="section">
                <h3>Field Mapping Basics</h3>
                <p>Field mapping defines how information is extracted from your drawing into Excel columns:</p>
                
                <h4>Key Concepts</h4>
                <ul>
                    <li>Source Fields: Text elements in your drawing</li>
                    <li>Target Fields: Columns in your Excel export</li>
                    <li>Pattern Matching: Rules for identifying text</li>
                    <li>Text Association: How related text is grouped</li>
                </ul>

                <h4>Common Field Types</h4>
                <table>
                    <tr>
                        <th>Field</th>
                        <th>Typical Content</th>
                        <th>Example</th>
                    </tr>
                    <tr>
                        <td>Cable Number</td>
                        <td>Unique identifier</td>
                        <td>W001, CBL-001</td>
                    </tr>
                    <tr>
                        <td>Source</td>
                        <td>Origin point</td>
                        <td>PNL-A, MCC-1</td>
                    </tr>
                    <tr>
                        <td>Destination</td>
                        <td>End point</td>
                        <td>MTR-1, DB-2</td>
                    </tr>
                </table>
            </div>
        """
    },
    "Creating Field Maps": {
        "title": "Creating Field Maps",
        "content": """
            <h2>Creating Field Maps</h2>
            
            <div class="section">
                <h3>Step-by-Step Guide</h3>
                <ol>
                    <li><strong>Define Target Fields</strong>
                        <ul>
                            <li>Click 'Add Field' to create a new mapping</li>
                            <li>Enter the Excel column name</li>
                            <li>Choose the data type (Text, Number, etc.)</li>
                        </ul>
                    </li>
                    <li><strong>Configure Pattern Matching</strong>
                        <ul>
                            <li>Enter the pattern to match drawing text</li>
                            <li>Test pattern with sample text</li>
                            <li>Adjust pattern for accuracy</li>
                        </ul>
                    </li>
                    <li><strong>Set Layer Filters</strong>
                        <ul>
                            <li>Select layers containing relevant text</li>
                            <li>Set layer processing priority</li>
                            <li>Configure text search areas</li>
                        </ul>
                    </li>
                </ol>
            </div>
        """
    },
    "Pattern Matching": {
        "title": "Pattern Matching",
        "content": """
            <h2>Pattern Matching</h2>
            <div class="section">
                <h3>Typical Cable Patterns</h3>
                <table class="pattern-table">
                    <tr>
                        <th>Information</th>
                        <th>Pattern</th>
                        <th>Matches</th>
                        <th>Explanation</th>
                    </tr>
                    <tr>
                        <td>Cable Numbers</td>
                        <td><code>W*</code> or <code>CBL*</code></td>
                        <td>W001, W123, CBL001</td>
                        <td>Matches cable numbers starting with W or CBL</td>
                    </tr>
                    <tr>
                        <td>Rack Locations</td>
                        <td><code>T[A-F][0-9][0-9]</code></td>
                        <td>TD01, TE03, TF06</td>
                        <td>Matches rack designations from TA00 to TF99</td>
                    </tr>
                    <tr>
                        <td>Device Types</td>
                        <td><code>*-SW-*</code> or <code>*-SRV-*</code></td>
                        <td>TD01-SW-01, TE03-SRV-02</td>
                        <td>Matches switches or servers in racks</td>
                    </tr>
                </table>
            </div>
        """
    },

    # Layer Settings
    "Layer Management": {
        "title": "Layer Management",
        "content": """
            <h2>Layer Management</h2>
            
            <div class="section">
                <h3>Layer Control</h3>
                <p>Manage which layers are processed and how they're handled during extraction:</p>
                <ul>
                    <li>Enable/disable layers for processing</li>
                    <li>Set layer priorities for text extraction</li>
                    <li>Configure layer visibility for preview</li>
                    <li>Group related layers for easier management</li>
                </ul>

                <h3>Layer Settings</h3>
                <table>
                    <tr>
                        <th>Setting</th>
                        <th>Purpose</th>
                    </tr>
                    <tr>
                        <td>Process Layer</td>
                        <td>Include layer in text extraction</td>
                    </tr>
                    <tr>
                        <td>Priority</td>
                        <td>Order of processing when text overlaps</td>
                    </tr>
                    <tr>
                        <td>Visibility</td>
                        <td>Show/hide in preview window</td>
                    </tr>
                </table>
            </div>
        """
    },
    "Layer Visibility": {
        "title": "Layer Visibility",
        "content": """
            <h2>Layer Visibility</h2>
            
            <div class="section">
                <h3>Visibility Controls</h3>
                <p>Manage layer visibility in the preview window:</p>
                <ul>
                    <li>Toggle individual layers on/off</li>
                    <li>Bulk visibility controls</li>
                    <li>Save visibility presets</li>
                    <li>Filter layer list</li>
                </ul>

                <h3>Visibility Presets</h3>
                <p>Common visibility configurations:</p>
                <ul>
                    <li>Cable layers only</li>
                    <li>Text layers only</li>
                    <li>Equipment layers only</li>
                    <li>Custom combinations</li>
                </ul>
            </div>
        """
    },
    "Layer Colors": {
        "title": "Layer Colors",
        "content": """
            <h2>Layer Colors</h2>
            
            <div class="section">
                <h3>Color Management</h3>
                <p>Customize layer colors for better visualization:</p>
                <ul>
                    <li>Set custom colors per layer</li>
                    <li>Use color schemes</li>
                    <li>Import AutoCAD colors</li>
                    <li>Save color presets</li>
                </ul>

                <h3>Color Coding</h3>
                <p>Recommended color schemes:</p>
                <ul>
                    <li>Cable types by color</li>
                    <li>Voltage levels</li>
                    <li>System types</li>
                    <li>Processing status</li>
                </ul>
            </div>
        """
    },

    # Export Settings
    "Excel Export Options": {
        "title": "Excel Export Options",
        "content": """
            <h2>Excel Export Options</h2>
            <div class="section">
                <h3>Export Formats</h3>
                <ul>
                    <li><strong>XLSX:</strong> Standard Excel format with full support for formatting and formulas.</li>
                    <li><strong>CSV:</strong> Comma-separated values for simple data exchange.</li>
                </ul>

                <h3>Export Settings</h3>
                <ul>
                    <li>Include headers</li>
                    <li>Auto-fit column widths</li>
                    <li>Apply data validation</li>
                </ul>
            </div>
        """
    },
    "Column Configuration": {
        "title": "Column Configuration",
        "content": """
            <h2>Column Configuration</h2>
            
            <div class="section">
                <h3>Excel Column Settings</h3>
                <table class="settings-table">
                    <tr>
                        <th>Setting</th>
                        <th>Description</th>
                        <th>Example</th>
                    </tr>
                    <tr>
                        <td>Column Order</td>
                        <td>Arrange columns in preferred order</td>
                        <td>NUMBER → SOURCE → DESTINATION</td>
                    </tr>
                    <tr>
                        <td>Column Width</td>
                        <td>Set custom or auto-width</td>
                        <td>NUMBER: 15, SOURCE: 25</td>
                    </tr>
                    <tr>
                        <td>Column Headers</td>
                        <td>Custom header names</td>
                        <td>"Cable No." instead of "NUMBER"</td>
                    </tr>
                </table>

                <h3>Data Validation</h3>
                <ul>
                    <li>Drop-down lists for standard values</li>
                    <li>Number ranges for quantities</li>
                    <li>Text length limits</li>
                    <li>Custom validation formulas</li>
                </ul>
            </div>
        """
    },
    "Data Formatting": {
        "title": "Data Formatting",
        "content": """
            <h2>Data Formatting</h2>
            
            <div class="section">
                <h3>Cell Formatting Options</h3>
                <ul>
                    <li><strong>Number Formats:</strong>
                        <ul>
                            <li>Cable lengths (with units)</li>
                            <li>Quantities</li>
                            <li>Reference numbers</li>
                        </ul>
                    </li>
                    <li><strong>Text Formats:</strong>
                        <ul>
                            <li>Case formatting</li>
                            <li>Prefix/suffix handling</li>
                            <li>Special characters</li>
                        </ul>
                    </li>
                </ul>

                <h3>Conditional Formatting</h3>
                <p>Highlight cells based on:</p>
                <ul>
                    <li>Cable types</li>
                    <li>Length ranges</li>
                    <li>System categories</li>
                    <li>Validation status</li>
                </ul>
            </div>
        """
    },

    # Drawing Settings
    "Default Settings": {
        "title": "Default Settings",
        "content": """
            <h2>Default Settings</h2>
            
            <div class="section">
                <h3>Application Defaults</h3>
                <table class="settings-table">
                    <tr>
                        <th>Category</th>
                        <th>Setting</th>
                        <th>Default Value</th>
                    </tr>
                    <tr>
                        <td>Drawing</td>
                        <td>Search radius</td>
                        <td>50 units</td>
                    </tr>
                    <tr>
                        <td>Text</td>
                        <td>Case sensitivity</td>
                        <td>False</td>
                    </tr>
                    <tr>
                        <td>Export</td>
                        <td>File format</td>
                        <td>XLSX</td>
                    </tr>
                </table>

                <h3>Customizing Defaults</h3>
                <p>Settings can be modified through:</p>
                <ul>
                    <li>Settings dialog</li>
                    <li>Configuration files</li>
                    <li>Command line arguments</li>
                </ul>
            </div>
        """
    },
    "Text Extraction": {
        "title": "Text Extraction",
        "content": """
            <h2>Text Extraction</h2>
            <div class="section">
                <h3>Text Recognition Settings</h3>
                <table class="settings-table">
                    <tr>
                        <th>Setting</th>
                        <th>Purpose</th>
                        <th>Recommended Value</th>
                    </tr>
                    <tr>
                        <td>Text Search Radius</td>
                        <td>Maximum distance to search for related text</td>
                        <td>50 units (adjustable based on drawing scale)</td>
                    </tr>
                    <tr>
                        <td>Text Alignment Tolerance</td>
                        <td>Allowable deviation for aligned text</td>
                        <td>0.5 units (for text considered on same line)</td>
                    </tr>
                </table>
            </div>
        """
    },
    "Processing Options": {
        "title": "Processing Options",
        "content": """
            <h2>Processing Options</h2>
            
            <div class="section">
                <h3>General Processing Settings</h3>
                <table>
                    <tr>
                        <th>Setting</th>
                        <th>Description</th>
                        <th>Default</th>
                    </tr>
                    <tr>
                        <td>Processing Mode</td>
                        <td>
                            <ul>
                                <li>Standard: Basic text extraction</li>
                                <li>Advanced: Deep entity analysis</li>
                                <li>Custom: User-defined rules</li>
                            </ul>
                        </td>
                        <td>Standard</td>
                    </tr>
                    <tr>
                        <td>Threading</td>
                        <td>
                            <ul>
                                <li>Single-threaded</li>
                                <li>Multi-threaded (faster)</li>
                            </ul>
                        </td>
                        <td>Multi-threaded</td>
                    </tr>
                    <tr>
                        <td>Memory Usage</td>
                        <td>
                            <ul>
                                <li>Conservative: Lower memory use</li>
                                <li>Balanced: Default setting</li>
                                <li>Aggressive: Faster but more memory</li>
                            </ul>
                        </td>
                        <td>Balanced</td>
                    </tr>
                </table>

                <h3>Advanced Processing Options</h3>
                <ul>
                    <li><strong>Entity Processing:</strong>
                        <ul>
                            <li>Block reference handling</li>
                            <li>Attribute extraction methods</li>
                            <li>Text style processing</li>
                            <li>Layer filtering rules</li>
                        </ul>
                    </li>
                    <li><strong>Text Processing:</strong>
                        <ul>
                            <li>Character encoding handling</li>
                            <li>Special character replacement</li>
                            <li>Case sensitivity options</li>
                            <li>White space handling</li>
                        </ul>
                    </li>
                    <li><strong>Geometric Processing:</strong>
                        <ul>
                            <li>Coordinate system handling</li>
                            <li>Scale factor processing</li>
                            <li>Rotation handling</li>
                            <li>Entity relationship analysis</li>
                        </ul>
                    </li>
                </ul>

                <h3>Performance Optimization</h3>
                <p>Tips for optimizing processing speed:</p>
                <ul>
                    <li>Disable unused layers before processing</li>
                    <li>Use specific pattern matching instead of wildcards</li>
                    <li>Limit search radius to necessary area</li>
                    <li>Enable multi-threading for large drawings</li>
                    <li>Use memory-efficient processing for huge files</li>
                </ul>

                <h3>Error Handling</h3>
                <table>
                    <tr>
                        <th>Error Type</th>
                        <th>Handling Method</th>
                    </tr>
                    <tr>
                        <td>Invalid Entities</td>
                        <td>Skip and log</td>
                    </tr>
                    <tr>
                        <td>Pattern Mismatch</td>
                        <td>Report in preview</td>
                    </tr>
                    <tr>
                        <td>Memory Issues</td>
                        <td>Automatic scaling of processing</td>
                    </tr>
                </table>
            </div>
        """
    },

    # Configuration
    "Configuration Management": {
        "title": "Configuration Management",
        "content": """
            <h2>Configuration Management</h2>
            
            <div class="section">
                <h3>Managing Configurations</h3>
                <ul>
                    <li><strong>Save Configurations:</strong>
                        <ul>
                            <li>Field mappings</li>
                            <li>Layer settings</li>
                            <li>Export preferences</li>
                            <li>Default values</li>
                        </ul>
                    </li>
                    <li><strong>Load Configurations:</strong>
                        <ul>
                            <li>Import from file</li>
                            <li>Quick templates</li>
                            <li>Project presets</li>
                        </ul>
                    </li>
                </ul>

                <h3>Configuration Files</h3>
                <pre>
config/
  ├── default.json    # Default settings
  ├── templates/      # Preset templates
  └── projects/       # Project-specific configs
</pre>
            </div>
        """
    },
    "Troubleshooting": {
        "title": "Troubleshooting Guide",
        "content": """
            <h2>Troubleshooting Guide</h2>
            
            <div class="section">
                <h3>Common Issues</h3>
                <ul>
                    <li><strong>Pattern Not Matching:</strong> Ensure patterns are correctly defined and case sensitivity is set appropriately.</li>
                    <li><strong>Missing Data in Export:</strong> Verify layer visibility and ensure correct layers are selected for processing.</li>
                    <li><strong>Excel Formatting Lost:</strong> Check template compatibility and reset to default if necessary.</li>
                    <li><strong>Slow Performance:</strong> Reduce search radius and disable unused layers to improve speed.</li>
                </ul>
            </div>
        """
    }
}

# Debug print available content
logger.debug(f"Loaded help content with keys: {list(HELP_CONTENT.keys())}")

# Update search index to match exact keys
SEARCH_INDEX = {
    "quick": ["Quick Start Guide"],
    "start": ["Quick Start Guide"],
    "guide": ["Quick Start Guide"],
    "getting": ["Getting Started", "Quick Start Guide"],
    "overview": ["Overview"],
    "requirements": ["System Requirements"],
    "mapping": ["Understanding Field Mapping", "Creating Field Maps"],
    "pattern": ["Pattern Matching"],
    "layer": ["Layer Management", "Layer Visibility", "Layer Colors"],
    "export": ["Excel Export Options", "Column Configuration", "Data Formatting"],
    "settings": ["Default Settings", "Text Extraction", "Processing Options"],
    "config": ["Configuration Management"],
    "troubleshoot": ["Troubleshooting"],
    "error": ["Troubleshooting"],
    "issue": ["Troubleshooting"],
    "problem": ["Troubleshooting"],
    "fix": ["Troubleshooting"],
    "debug": ["Troubleshooting"],
    "help": ["Troubleshooting"],
}

