#!/usr/bin/env python3
"""
Generate a PNG export from the Mermaid diagram using web services and image conversion.
"""

import subprocess
import sys
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

def export_diagram_to_png():
    """Main export function."""
    
    project_dir = Path(__file__).parent
    mermaid_file = project_dir / "Mermaid.js"
    
    if not mermaid_file.exists():
        print(f"Error: {mermaid_file} not found")
        return False
    
    # Read diagram content
    with open(mermaid_file, "r") as f:
        diagram_content = f.read().strip()
    
    print("Attempting to generate UML diagram as PNG...")
    
    # Try quickchart.io service
    if try_quickchart(diagram_content, project_dir):
        return True
    
    # Try mermaid.live API
    if try_mermaid_live(diagram_content, project_dir):
        return True
    
    # Fallback: create a script-able SVG export
    create_svg_export(diagram_content, project_dir)
    return True

def try_quickchart(diagram_content, project_dir):
    """Try using quickchart.io service."""
    try:
        print("  Trying quickchart.io...")
        
        # URL encode the diagram
        encoded = urllib.parse.quote(diagram_content)
        url = f"https://quickchart.io/mermaid?mermaid={encoded}"
        
        output_file = project_dir / "uml_final.png"
        
        # Use Request with timeout to handle it properly
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(output_file, 'wb') as f:
                f.write(response.read())
        
        if output_file.exists() and output_file.stat().st_size > 0:
            size_kb = output_file.stat().st_size / 1024
            print(f"  Success! Created: {output_file}")
            print(f"  File size: {size_kb:.1f} KB")
            return True
    except Exception as e:
        print(f"  Failed: {e}")
    
    return False

def try_mermaid_live(diagram_content, project_dir):
    """Try using mermaid.live API."""
    try:
        print("  Trying mermaid.live...")
        
        # Compress and encode
        import zlib
        compressed = zlib.compress(diagram_content.encode())
        encoded = base64.urlsafe_b64encode(compressed).decode().rstrip('=')
        
        url = f"https://mermaid.live/svg/{encoded}"
        
        temp_svg = project_dir / "temp_diagram.svg"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(temp_svg, 'wb') as f:
                f.write(response.read())
        
        if temp_svg.exists():
            # Convert SVG to PNG using cairosvg
            try:
                import cairosvg
                output_file = project_dir / "uml_final.png"
                with open(temp_svg, 'rb') as f:
                    cairosvg.svg2png(bytestring=f.read(),
                                     write_to=str(output_file))
                
                if output_file.exists():
                    temp_svg.unlink()
                    size_kb = output_file.stat().st_size / 1024
                    print(f"  Success! Created: {output_file}")
                    print(f"  File size: {size_kb:.1f} KB")
                    return True
            except Exception as e:
                print(f"  SVG conversion failed: {e}")
    
    except Exception as e:
        print(f"  Failed: {e}")
    
    return False

def create_svg_export(diagram_content, project_dir):
    """Create an SVG wrapper that can be opened in browsers/editors."""
    try:
        print("  Creating SVG export...")
        
        svg_file = project_dir / "uml_diagram.svg"
        
        html_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="800">
  <defs>
    <style>
      text {{ font-family: Arial, sans-serif; font-size: 12px; }}
      rect {{ fill: white; stroke: #ccc; stroke-width: 1; }}
      line {{ stroke: #999; stroke-width: 1; }}
    </style>
  </defs>
  <rect width="100%" height="100%" fill="white"/>
  <text x="50" y="30" font-size="18" font-weight="bold">PawPal+ UML Class Diagram</text>
  <text x="50" y="50" font-size="12" fill="#666">Open uml_diagram.html in your browser for interactive view</text>
  <text x="50" y="80" font-size="14" font-weight="bold">Mermaid Source:</text>
  <foreignObject x="50" y="100" width="1100" height="650">
    <body xmlns="http://www.w3.org/1999/xhtml">
      <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: monospace; font-size: 10px;">{diagram_content}</pre>
    </body>
  </foreignObject>
</svg>"""
        
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(html_svg)
        
        print(f"  Created: {svg_file}")
        print(f"Note: Open uml_diagram.html to see the rendered diagram")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    import urllib.parse
    success = export_diagram_to_png()
    sys.exit(0 if success else 1)
