# GIVC Healthcare Platform

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![HIPAA Compliant](https://img.shields.io/badge/HIPAA-Compliant-green.svg)](https://www.hhs.gov/hipaa/index.html)
[![RCM Accredited](https://img.shields.io/badge/RCM-Accredited-brightgreen.svg)](https://www.cms.gov/medicare/provider-enrollment-and-certification)

## 🏥 GIVC - Global Integrated Virtual Care

**Advanced HIPAA-compliant healthcare technology platform with AI-powered medical analysis**

- **Project Owner**: Dr. Al Fadil (BRAINSAIT LTD)  
- **Domain**: [givc.thefadil.site](https://givc.thefadil.site)  
- **Tech Stack**: React + TypeScript + Cloudflare Workers + Workers AI  
- **Compliance**: HIPAA, RCM Accredited, ISO 27001

## ✨ Features

### 🤖 AI-Powered Medical Agents
- **DICOM Analysis Agent** - ResNet-50 neural network for medical imaging analysis
- **Lab Results Parser** - OCR and intelligent parsing of laboratory results
- **Clinical Decision Support** - Evidence-based diagnosis and treatment recommendations
- **Compliance Monitor** - Real-time HIPAA compliance and audit monitoring

### 🔐 MediVault - Secure File Management
- HIPAA-compliant file storage with AES-256 encryption
- Support for DICOM, PDF, HL7, and medical image formats
- Drag-and-drop upload with real-time processing status
- Secure URL generation with expiration timestamps

### 🩺 AI Triage Assessment
- Intelligent symptom analysis and urgency determination
- Evidence-based triage recommendations
- Emergency detection and routing
- Clinical guideline integration

### 📊 Real-time Analytics Dashboard
- System performance and uptime monitoring
- Compliance score tracking
- AI agent performance metrics
- Audit trail visualization

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Cloudflare account with Workers, R2, KV, and D1 access
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Fadil369/GIVC.git
   cd GIVC
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Cloudflare credentials and configuration
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

## 🏗️ Architecture

The GIVC platform is built on a modern, serverless architecture using Cloudflare's edge computing platform:

- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: Cloudflare Workers (serverless)
- **AI Processing**: Workers AI with ResNet-50
- **Storage**: R2 (files), KV (metadata), D1 (structured data)
- **Security**: End-to-end encryption, HIPAA compliance

## 🔒 Security & Compliance

### HIPAA Compliance
- ✅ End-to-end encryption (AES-256-GCM)
- ✅ Audit logging with 7-year retention
- ✅ Role-based access control (RBAC)
- ✅ Secure data transmission (TLS 1.3)

### RCM Accreditation
- ✅ Billing code extraction and validation
- ✅ Claims processing workflow
- ✅ Revenue cycle analytics

## 📖 Demo Usage

The platform includes demo functionality for testing:

1. **Login**: Use any email/password combination
2. **Upload Files**: Drag and drop medical files in MediVault
3. **Run AI Analysis**: Test DICOM, Lab, and Clinical agents
4. **Triage Assessment**: Complete symptom questionnaires
5. **View Compliance**: Monitor HIPAA compliance status

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🏢 Organization

**BRAINSAIT LTD**  
**Dr. Al Fadil, MD**  
Healthcare Technology Innovation  
RCM Accredited Provider  

---

**© 2024 Dr. Al Fadil - BRAINSAIT LTD. All rights reserved.**  
**GIVC - Transforming Healthcare Through Technology** 🏥✨
