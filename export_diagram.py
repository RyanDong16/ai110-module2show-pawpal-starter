#!/usr/bin/env python3
"""
Export the Mermaid UML diagram to a PNG image.
Uses web-based rendering or local conversion methods.
"""

import subprocess
import sys
import os
import base64
import urllib.request
import urllib.parse
from pathlib import Path

def export_mermaid_to_png():
    """Convert Mermaid.js diagram to PNG format."""
    
    project_dir = Path(__file__).parent
    mermaid_file = project_dir / "Mermaid.js"
    output_file = project_dir / "uml_final.png"
    
    if not mermaid_file.exists():
        print(f"❌ Error: {mermaid_file} not found")
        return False
    
    # Read the diagram content
    with open(mermaid_file, "r") as f:
        diagram_content = f.read()
    
    # Try using kroki.io (free online diagram renderer)
    try:
        print(f"🔄 Rendering diagram using web service...")
        success = export_via_kroki(diagram_content, output_file)
        if success:
            return True
    except Exception as e:
        print(f"⚠️  Web service error: {e}")
    
    # Fallback: Create an interactive HTML file
    print("📝 Creating interactive HTML diagram as fallback...")
    return create_html_diagram(diagram_content, project_dir)

def export_via_kroki(diagram_content, output_file):
    """Export using kroki.io service."""
    try:
        # Encode diagram for kroki.io URL
        encoded = base64.urlsafe_b64encode(diagram_content.encode()).decode()
        url = f"https://kroki.io/mermaid/png/{encoded}"
        
        print(f"   URL: {url[:60]}...")
        
        # Download the PNG
        urllib.request.urlretrieve(url, str(output_file))
        
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"✅ Successfully created: {output_file}")
            print(f"   File size: {size_kb:.1f} KB")
            return True
        return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

def create_html_diagram(diagram_content, project_dir):
    """Create an interactive HTML viewer as fallback."""
    html_file = project_dir / "uml_diagram.html"
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PawPal+ UML Diagram</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 1200px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .mermaid {
            display: flex;
            justify-content: center;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
        }
        
        .info {
            margin-top: 30px;
            padding: 20px;
            background: #f0f7ff;
            border-left: 4px solid #667eea;
            border-radius: 6px;
            color: #333;
        }
        
        .info h3 {
            margin-bottom: 10px;
            color: #667eea;
        }
        
        .info p {
            line-height: 1.6;
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PawPal+ System Architecture</h1>
        <p class="subtitle">Phase 3: Final UML Class Diagram</p>
        
        <div class="mermaid">
""" + diagram_content + """
        </div>
        
        <div class="info">
            <h3>Class Overview</h3>
            <p><strong>Owner:</strong> Manages pets and their collective tasks</p>
            <p><strong>Pet:</strong> Represents a pet with its own task list</p>
            <p><strong>Task:</strong> Individual care task with scheduling constraints (supports recurring)</p>
            <p><strong>Scheduler:</strong> Orchestrates task scheduling, conflict detection, and time-based sorting</p>
            <p><strong>Schedule:</strong> A plan for a specific date with task assignments and explanations</p>
        </div>
        
        <div class="info">
            <h3>Key Features</h3>
            <p>[+] Recurring task management (daily, weekly, monthly)</p>
            <p>[+] Time-window based scheduling with conflict detection</p>
            <p>[+] Task priority scoring and sorting by time</p>
            <p>[+] Constraint-based plan generation with explanations</p>
            <p>[+] Multi-pet support with aggregated task management</p>
        </div>
    </div>
    
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'default', securityLevel: 'loose' });
        mermaid.contentLoaded();
    </script>
</body>
</html>"""
    
    try:
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Success! Created interactive diagram: {html_file}")
        print(f"   Open in browser to view the diagram")
        return True
    except Exception as e:
        print(f"Error creating HTML: {e}")
        return False

if __name__ == "__main__":
    success = export_mermaid_to_png()
    sys.exit(0 if success else 1)

