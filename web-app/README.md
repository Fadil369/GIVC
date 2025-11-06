# ClaimLinc AI Workspace

## 🚀 Advanced AI-Powered Team Collaboration Hub

A comprehensive web-based workspace for managing healthcare claims data with embedded Google Sheets integration, AI-powered analysis, and team collaboration features.

---

## ✨ Features

### 📊 **Dashboard Analytics**
- Real-time KPI cards showing claims metrics
- Interactive charts (Chart.js powered)
- Claims by payer distribution
- Monthly trend analysis
- Recent activity feed

### 📑 **Google Sheets Integration**
- **Embedded Views:**
  - All Data View (complete spreadsheet)
  - Specific Sheet View (gid: 562525379)
- **Interactive Controls:**
  - Live search functionality
  - Branch filtering (MainRiyadh, Unaizah, Abha, Madinah, Khamis)
  - Payer filtering (Bupa, Tawuniya, GlobeMed)
  - One-click data extraction

### 🧠 **AI-Powered Analysis**
- **AI Chat Assistant:**
  - Natural language queries
  - Instant insights generation
  - Pattern recognition
  - Trend analysis
- **Automated Insights:**
  - Top rejection reasons identification
  - Performance trends tracking
  - Branch performance comparison
  - Actionable recommendations

### 👥 **Team Collaboration**
- **Team Members Panel:**
  - Online status indicators
  - Branch assignment display
  - Real-time presence tracking
- **Comments & Annotations:**
  - Thread-based discussions
  - @mentions support
  - Activity timestamps
- **Task Manager:**
  - Kanban-style board (To Do / In Progress / Done)
  - Task assignment to branches
  - Drag-and-drop functionality

### 📈 **Reports & Analytics**
- **Report Builder:**
  - Claims Summary
  - Rejection Analysis
  - Branch Performance
  - Payer Analysis
  - Custom Reports
- **Export Options:**
  - Date range selection
  - Multiple formats (PDF, Excel, CSV, HTML)
  - Preview before download

### 💾 **Data Export**
- Export as CSV (for Excel)
- Export as Excel workbook (.xlsx)
- Export as JSON (for APIs)
- Export as PDF (formatted reports)

### 🔔 **Smart Notifications**
- Real-time alerts for new rejections
- Approval notifications
- Task reminders
- System updates

---

## 🛠️ Technology Stack

- **Frontend:**
  - HTML5, CSS3 (Custom CSS Variables)
  - Vanilla JavaScript (ES6+)
  - Font Awesome 6.4.0 (Icons)
  - Chart.js 4.4.0 (Data Visualization)
  - Marked.js (Markdown rendering)

- **Design:**
  - Responsive CSS Grid & Flexbox
  - Custom CSS animations
  - Gradient color schemes
  - Material Design principles

- **Integration:**
  - Google Sheets Public Embed API
  - (Future: Google Sheets API for data extraction)

---

## 📂 Project Structure

```
web-workspace/
├── index.html          # Main HTML structure
├── styles.css          # Complete styling with CSS variables
├── app.js              # Application logic and interactivity
└── README.md           # This file
```

---

## 🚀 Getting Started

### Option 1: Open Directly in Browser
1. Navigate to the `web-workspace` folder
2. Double-click `index.html`
3. The workspace will open in your default browser

### Option 2: Use Live Server (Recommended)
```bash
# If you have Python installed
cd web-workspace
python -m http.server 8080

# Or use VS Code Live Server extension
# Right-click index.html → Open with Live Server
```

Then open: `http://localhost:8080`

---

## 🎨 UI Components

### Navigation Sidebar
- Dashboard
- Data Sheets
- AI Analysis
- Team Collaboration
- Reports
- Task Manager
- Export Data

### Color Scheme
- **Primary**: `#0D8ABC` (ClaimLinc Blue)
- **Secondary**: `#667eea` (Purple gradient)
- **Success**: `#43e97b` (Green)
- **Warning**: `#f5576c` (Red)
- **Info**: `#4facfe` (Light Blue)

### Typography
- Font Family: Segoe UI, system fonts
- Responsive sizing
- Clear hierarchy

---

## 🤖 AI Assistant Features

### Chat Interface
Ask questions like:
- "What are the top rejection reasons?"
- "Analyze Bupa claims performance"
- "Show me trends for Riyadh branch"
- "How can we improve approval rates?"

### AI-Generated Insights
- Automatic pattern detection
- Rejection reason categorization
- Performance benchmarking
- Predictive analytics

### Recommendations Engine
- Process improvement suggestions
- Training needs identification
- Automation opportunities

---

## 📊 Embedded Google Sheets

### Sheet 1: All Data View
```html
https://docs.google.com/spreadsheets/d/e/2PACX-1vQrUv_Zw6mB3rAhGIO_x2OSkUT-6TWATy9b5C1M9_PpQ-3rINTSg2XzpR9JIEUZOWT1-5AEiuukoaJQ/pubhtml?widget=true&headers=false
```

### Sheet 2: Specific Sheet (gid: 562525379)
```html
https://docs.google.com/spreadsheets/d/e/2PACX-1vQrUv_Zw6mB3rAhGIO_x2OSkUT-6TWATy9b5C1M9_PpQ-3rINTSg2XzpR9JIEUZOWT1-5AEiuukoaJQ/pubhtml?gid=562525379&single=true&widget=true&headers=false
```

---

## 🔧 Customization

### Adding New Branches
Edit `app.js` and update the branch filter:
```javascript
<option value="YourNewBranch">Your New Branch</option>
```

### Changing Color Theme
Edit CSS variables in `styles.css`:
```css
:root {
    --primary-color: #0D8ABC;  /* Change this */
    --secondary-color: #667eea; /* And this */
}
```

### Adding Custom Charts
Use Chart.js in `app.js`:
```javascript
new Chart(ctx, {
    type: 'bar', // or 'line', 'pie', 'doughnut'
    data: { /* your data */ },
    options: { /* your options */ }
});
```

---

## 🔒 Security & Compliance

### Data Privacy
- No sensitive data stored in frontend
- All credentials managed via environment variables
- Google Sheets accessed via public embed URLs only
- HTTPS recommended for production

### PDPL Compliance
- PHI data encrypted in transit
- Access control via authentication (add in production)
- Audit logs for data access
- User consent mechanisms

---

## 📱 Responsive Design

- **Desktop**: Full feature set (1920x1080+)
- **Tablet**: Optimized layout (768px - 1200px)
- **Mobile**: Simplified UI (< 768px)
- **Touch-friendly**: All buttons and controls

---

## 🚀 Future Enhancements

### Phase 2 (Planned)
- [ ] Real-time data sync with Google Sheets API
- [ ] User authentication (OAuth 2.0)
- [ ] Role-based access control
- [ ] WebSocket for live collaboration
- [ ] Advanced AI models (GPT-4 integration)
- [ ] Mobile app (React Native)

### Phase 3 (Future)
- [ ] Blockchain-based audit trails
- [ ] Machine learning predictions
- [ ] Voice commands (Alexa/Google Assistant)
- [ ] Multi-language support (Arabic/English)
- [ ] Offline mode with sync

---

## 🐛 Troubleshooting

### Sheets not loading?
- Check internet connection
- Verify Google Sheet is published to web
- Check browser console for errors
- Try different browser (Chrome recommended)

### Charts not displaying?
- Ensure Chart.js CDN is accessible
- Check browser console for errors
- Verify data format in `app.js`

### AI Assistant not responding?
- Check JavaScript console for errors
- Ensure `app.js` is loaded correctly
- Try refreshing the page

---

## 📞 Support

For issues or questions:
- **Email**: support@brainsait.io
- **Teams**: ClaimLinc Support Channel
- **Documentation**: [ClaimLinc Docs](https://docs.claimlinc.brainsait.io)

---

## 📄 License

© 2025 BrainSAIT LTD. All rights reserved.

---

## 👨‍💻 Developer Notes

### Key Functions in `app.js`

| Function | Purpose |
|----------|---------|
| `initializeApp()` | Main initialization |
| `switchView(viewName)` | Navigate between views |
| `loadDashboardData()` | Load KPI metrics |
| `sendAIMessage()` | Process AI chat |
| `extractSheetData()` | Extract Google Sheets data |
| `generateReport()` | Create custom reports |

### Event Listeners
- Navigation clicks
- Sheet tab switching
- Filter changes
- AI chat input
- Export buttons
- Task management
- Notifications

---

## 🎯 Quick Start Guide for Team

1. **Access the Workspace**
   - Open `index.html` in your browser
   - Or access via: `http://your-server/web-workspace`

2. **Navigate the Dashboard**
   - View KPIs and charts
   - Check recent activity

3. **View Data Sheets**
   - Click "Data Sheets" in sidebar
   - Switch between sheet views
   - Use filters to narrow down data

4. **Use AI Assistant**
   - Click "AI Assistant" button
   - Type your question
   - Get instant insights

5. **Collaborate with Team**
   - Go to "Team Collaboration"
   - Add comments
   - Assign tasks
   - Track progress

6. **Generate Reports**
   - Select "Reports" from sidebar
   - Choose report type and date range
   - Generate and download

---

## ✅ Checklist for Deployment

- [ ] Update Google Sheets URLs
- [ ] Configure environment variables
- [ ] Set up authentication (production)
- [ ] Enable HTTPS
- [ ] Test on all browsers
- [ ] Optimize images and assets
- [ ] Set up monitoring (Google Analytics)
- [ ] Configure backup strategy
- [ ] Document API endpoints
- [ ] Train team members

---

**Built with ❤️ by BrainSAIT for Al-Hayat Hospital Group**

*Version 1.0 - November 2025*
