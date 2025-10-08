#!/bin/bash

# Fix HTML linting issues in index.html

# Create backup
cp index.html index.html.backup

# Fix ID attributes (camelCase to kebab-case)
sed -i 's/id="loadingScreen"/id="loading-screen"/g' index.html
sed -i 's/id="logoGradient"/id="logo-gradient"/g' index.html
sed -i 's/id="mobileMenuToggle"/id="mobile-menu-toggle"/g' index.html
sed -i 's/id="mobileMenu"/id="mobile-menu"/g' index.html
sed -i 's/id="contactForm"/id="contact-form"/g' index.html
sed -i 's/id="backToTop"/id="back-to-top"/g' index.html
sed -i 's/id="footerLogoGradient"/id="footer-logo-gradient"/g' index.html

# Fix SVG elements (uppercase to lowercase)
sed -i 's/<linearGradient/<lineargradient/g' index.html
sed -i 's/<\/linearGradient>/<\/lineargradient>/g' index.html

# Fix special characters (& to &amp;)
sed -i 's/Analytics & Insights/Analytics \&amp; Insights/g' index.html
sed -i 's/Founder & CEO/Founder \&amp; CEO/g' index.html
sed -i 's/Physician & Tech Entrepreneur/Physician \&amp; Tech Entrepreneur/g' index.html

# Fix hex colors (#ffffff to #fff)
sed -i 's/#ffffff/#fff/g' index.html

echo "HTML linting fixes applied to index.html"
echo "Backup saved as index.html.backup"