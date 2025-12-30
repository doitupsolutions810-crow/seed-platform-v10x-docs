#!/usr/bin/env python3
"""
Documentation Generator for SEED Platform v10.x
Converts USAGE_GUIDE.md and QUICKSTART.md to a single-page HTML site

This script is designed to run in GitHub Actions but can also be run locally.

FIXED: Added section prefixes to IDs to prevent duplicates
"""

import markdown
import re
import sys
from datetime import datetime
from pathlib import Path

def read_file(filename):
    """Read markdown file content with error handling"""
    try:
        filepath = Path(filename)
        if not filepath.exists():
            print(f"❌ Error: {filename} not found")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print(f"⚠️  Warning: {filename} is empty")
            return None
        
        print(f"✅ Read {filename} ({len(content)} bytes)")
        return content
    
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return None

def add_id_prefix(html_content, prefix):
    """Add a prefix to all id attributes in HTML content"""
    
    # Pattern to match id attributes: id="something"
    def replace_id(match):
        quote = match.group(1)
        id_value = match.group(2)
        return f'id={quote}{prefix}{id_value}{quote}'
    
    # Replace all id attributes
    id_pattern = r'\sid=(["\'])([^"\']+)\1'
    modified_html = re.sub(id_pattern, replace_id, html_content)
    
    return modified_html

def add_href_prefix(html_content, prefix):
    """Add a prefix to all href anchor links in HTML content"""
    
    # Pattern to match href="#something"
    def replace_href(match):
        quote = match.group(1)
        anchor = match.group(2)
        return f'href={quote}#{prefix}{anchor}{quote}'
    
    # Replace all href="#anchor" links
    href_pattern = r'href=(["\'])#([^"\']+)\1'
    modified_html = re.sub(href_pattern, replace_href, html_content)
    
    return modified_html

def convert_markdown_to_html(md_content, section_prefix=''):
    """Convert markdown to HTML with extensions and optional ID prefix"""
    try:
        html = markdown.markdown(
            md_content,
            extensions=[
                'extra',
                'codehilite',
                'toc',
                'tables',
                'fenced_code'
            ]
        )
        
        # Add prefix to IDs if specified
        if section_prefix:
            html = add_id_prefix(html, section_prefix)
            html = add_href_prefix(html, section_prefix)
        
        return html
    except Exception as e:
        print(f"❌ Error converting markdown to HTML: {e}")
        return None

def generate_navigation(quickstart_html, usage_html):
    """Generate navigation menu from HTML headers"""
    nav_items = []
    
    # Extract h2 and h3 headers with IDs (now with prefixes)
    header_pattern = r'<h([23])[^>]*id="([^"]*)"[^>]*>([^<]+)</h\1>'
    
    # Process Quick Start
    nav_items.append('<div class="nav-section">QUICK START</div>')
    quickstart_count = 0
    for match in re.finditer(header_pattern, quickstart_html):
        level, id_attr, text = match.groups()
        indent = 'nav-item-sub' if level == '3' else 'nav-item'
        nav_items.append(f'<a href="#{id_attr}" class="{indent}">{text}</a>')
        quickstart_count += 1
    
    # Process Usage Guide
    nav_items.append('<div class="nav-section">USAGE GUIDE</div>')
    usage_count = 0
    for match in re.finditer(header_pattern, usage_html):
        level, id_attr, text = match.groups()
        indent = 'nav-item-sub' if level == '3' else 'nav-item'
        nav_items.append(f'<a href="#{id_attr}" class="{indent}">{text}</a>')
        usage_count += 1
    
    print(f"📊 Generated navigation: {quickstart_count} Quick Start items, {usage_count} Usage Guide items")
    
    return '\n'.join(nav_items)

def generate_html_template(navigation, quickstart_content, usage_content):
    """Generate complete HTML document"""
    
    generation_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Complete documentation for SEED Platform v10.x - Quick Start Guide and Usage Guide">
    <meta name="keywords" content="SEED Platform, documentation, quick start, usage guide, v10.x">
    <meta name="author" content="SEED Platform Team">
    <meta name="generator" content="SEED Documentation Generator">
    <meta name="last-updated" content="{generation_time}">
    <title>SEED Platform v10.x - Documentation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            padding: 0 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: 600;
        }}
        
        .header-icon {{
            margin-right: 12px;
            font-size: 28px;
        }}
        
        .container {{
            display: flex;
            margin-top: 60px;
            min-height: calc(100vh - 60px);
        }}
        
        .sidebar {{
            position: fixed;
            left: 0;
            top: 60px;
            width: 280px;
            height: calc(100vh - 60px);
            background: white;
            border-right: 1px solid #e0e0e0;
            overflow-y: auto;
            padding: 20px;
            box-shadow: 2px 0 10px rgba(0,0,0,0.05);
        }}
        
        .sidebar-title {{
            font-size: 18px;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .sidebar-icon {{
            margin-right: 8px;
        }}
        
        .sidebar-subtitle {{
            font-size: 14px;
            color: #999;
            margin-bottom: 20px;
        }}
        
        .nav-section {{
            font-size: 12px;
            font-weight: 700;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 20px 0 10px 0;
        }}
        
        .nav-item, .nav-item-sub {{
            display: block;
            padding: 8px 12px;
            color: #555;
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.2s;
            margin-bottom: 4px;
        }}
        
        .nav-item-sub {{
            padding-left: 24px;
            font-size: 14px;
        }}
        
        .nav-item:hover, .nav-item-sub:hover {{
            background: #f0f0f0;
            color: #667eea;
        }}
        
        .main-content {{
            margin-left: 280px;
            flex: 1;
            padding: 40px;
            background: white;
            min-height: calc(100vh - 60px);
        }}
        
        .content-section {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        h1 {{
            font-size: 36px;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        h2 {{
            font-size: 28px;
            color: #333;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        h3 {{
            font-size: 22px;
            color: #555;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        
        p {{
            margin-bottom: 15px;
            color: #555;
        }}
        
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        code {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
        }}
        
        p code, li code {{
            background: #f4f4f4;
            color: #e83e8c;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 13px;
        }}
        
        ul, ol {{
            margin: 15px 0 15px 30px;
        }}
        
        li {{
            margin-bottom: 8px;
            color: #555;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f9f9f9;
        }}
        
        .scroll-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s;
            z-index: 999;
        }}
        
        .scroll-top:hover {{
            background: #764ba2;
            transform: translateY(-5px);
        }}
        
        .scroll-top.visible {{
            display: flex;
        }}
        
        @media (max-width: 768px) {{
            .sidebar {{
                transform: translateX(-100%);
                transition: transform 0.3s;
            }}
            
            .main-content {{
                margin-left: 0;
            }}
        }}
        
        @media print {{
            .header, .sidebar, .scroll-top {{
                display: none;
            }}
            
            .main-content {{
                margin-left: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <span class="header-icon">🚀</span>
        <h1>SEED Platform v10.x Documentation</h1>
    </div>
    
    <div class="sidebar">
        <div class="sidebar-title">
            <span class="sidebar-icon">📚</span>
            Docs
        </div>
        <div class="sidebar-subtitle">Complete Guide</div>
        {navigation}
    </div>
    
    <div class="container">
        <div class="main-content">
            <div class="content-section">
                {quickstart_content}
                <hr style="margin: 60px 0; border: none; border-top: 2px solid #e0e0e0;">
                {usage_content}
            </div>
        </div>
    </div>
    
    <button class="scroll-top" id="scrollTop">↑</button>
    
    <script>
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
        
        const scrollTopBtn = document.getElementById('scrollTop');
        window.addEventListener('scroll', () => {{
            if (window.pageYOffset > 300) {{
                scrollTopBtn.classList.add('visible');
            }} else {{
                scrollTopBtn.classList.remove('visible');
            }}
        }});
        
        scrollTopBtn.addEventListener('click', () => {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }});
    </script>
    
    <div style="text-align: center; padding: 40px 0; color: #999; font-size: 12px;">
        Last updated: {generation_time} | Auto-generated from source repository
    </div>
</body>
</html>'''
    
    return html_template

def main():
    """Main generation function"""
    print("=" * 60)
    print("🚀 SEED Platform Documentation Generator (FIXED)")
    print("=" * 60)
    print()
    
    # Read markdown files
    print("📖 Reading markdown files...")
    quickstart_md = read_file('QUICKSTART.md')
    usage_md = read_file('USAGE_GUIDE.md')
    
    if not quickstart_md or not usage_md:
        print()
        print("❌ Failed to read required markdown files")
        return False
    
    print()
    
    # Convert to HTML with section prefixes
    print("🔄 Converting markdown to HTML with section prefixes...")
    quickstart_html = convert_markdown_to_html(quickstart_md, 'quickstart-')
    usage_html = convert_markdown_to_html(usage_md, 'usage-')
    
    if not quickstart_html or not usage_html:
        print()
        print("❌ Failed to convert markdown to HTML")
        return False
    
    print("✅ Markdown converted successfully with unique IDs")
    print("   - Quick Start IDs prefixed with 'quickstart-'")
    print("   - Usage Guide IDs prefixed with 'usage-'")
    print()
    
    # Generate navigation
    print("🗺️  Generating navigation...")
    navigation = generate_navigation(quickstart_html, usage_html)
    print()
    
    # Generate final HTML
    print("📝 Generating final HTML document...")
    final_html = generate_html_template(navigation, quickstart_html, usage_html)
    
    if not final_html:
        print()
        print("❌ Failed to generate HTML template")
        return False
    
    print(f"✅ HTML document generated ({len(final_html):,} bytes)")
    print()
    
    # Write output
    print("💾 Writing output file...")
    try:
        output_path = Path('index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        file_size = output_path.stat().st_size
        print(f"✅ Output written to: {output_path}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print()
        
    except Exception as e:
        print(f"❌ Error writing output file: {e}")
        print()
        return False
    
    # Success
    print("=" * 60)
    print("✅ Documentation generated successfully!")
    print("✅ Duplicate ID issue FIXED!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
