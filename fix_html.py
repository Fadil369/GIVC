#!/usr/bin/env python3

import re

# Read the HTML file
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Create backup
with open('index.html.backup', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix ID attributes (camelCase to kebab-case)
content = content.replace('id="loadingScreen"', 'id="loading-screen"')
content = content.replace('id="logoGradient"', 'id="logo-gradient"')
content = content.replace('id="mobileMenuToggle"', 'id="mobile-menu-toggle"')
content = content.replace('id="mobileMenu"', 'id="mobile-menu"')
content = content.replace('id="contactForm"', 'id="contact-form"')
content = content.replace('id="backToTop"', 'id="back-to-top"')
content = content.replace('id="footerLogoGradient"', 'id="footer-logo-gradient"')

# Fix SVG elements (uppercase to lowercase)
content = content.replace('<linearGradient', '<lineargradient')
content = content.replace('</linearGradient>', '</lineargradient>')

# Fix special characters (& to &amp;)
content = content.replace('Analytics & Insights', 'Analytics &amp; Insights')
content = content.replace('Founder & CEO', 'Founder &amp; CEO')
content = content.replace('Physician & Tech Entrepreneur', 'Physician &amp; Tech Entrepreneur')

# Fix hex colors (#ffffff to #fff)
content = content.replace('#ffffff', '#fff')

# Write the fixed content back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML linting fixes applied to index.html")
print("Backup saved as index.html.backup")