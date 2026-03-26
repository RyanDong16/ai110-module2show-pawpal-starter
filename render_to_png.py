#!/usr/bin/env python3
"""
Generate PNG from the UML diagram using Playwright headless browser.
"""

import sys
from pathlib import Path

def render_html_to_png():
    """Render the HTML diagram to PNG using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: Playwright not installed. Run: pip install playwright")
        return False
    
    project_dir = Path(__file__).parent
    html_file = project_dir / "uml_diagram.html"
    output_file = project_dir / "uml_final.png"
    
    if not html_file.exists():
        print(f"Error: {html_file} not found")
        return False
    
    try:
        print("Rendering diagram to PNG using Playwright...")
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            
            # Load HTML file
            page_path = html_file.as_uri()
            print(f"  Loading: {page_path}")
            page.goto(page_path)
            
            # Wait for Mermaid to render
            print("  Waiting for diagram to render...")
            page.wait_for_load_state("networkidle")
            
            # Take screenshot
            print(f"  Taking screenshot...")
            page.screenshot(path=str(output_file), full_page=False)
            
            browser.close()
        
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"Success! Created: {output_file}")
            print(f"File size: {size_kb:.1f} KB")
            return True
        else:
            print("Error: PNG file was not created")
            return False
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = render_html_to_png()
    sys.exit(0 if success else 1)
