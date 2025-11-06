import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header.jsx';
import Sidebar from './Sidebar.jsx';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Mobile-first responsive detection
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
      // Auto-close sidebar on mobile when screen resizes
      if (window.innerWidth < 1024) {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      {/* Professional Layout Structure */}
      <div className="flex h-screen overflow-hidden">
        {/* Professional Sidebar */}
        <Sidebar 
          isOpen={sidebarOpen} 
          onToggle={toggleSidebar}
          isMobile={isMobile}
        />
        
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Professional Header */}
          <Header 
            onToggleSidebar={toggleSidebar} 
            isMobile={isMobile} 
          />
          
          {/* Main Content with clean spacing */}
          <main className="flex-1 overflow-y-auto bg-transparent">
            <div className="min-h-full">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;