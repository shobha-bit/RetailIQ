import React, { useState } from 'react';
import { DatasetProvider } from './context/DatasetContext';
import { FilterProvider } from './context/FilterContext';
import { Sidebar, PageId } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { ExecutiveDashboard } from './pages/ExecutiveDashboard';
import { SalesAnalysis } from './pages/SalesAnalysis';
import { CustomerAnalysis } from './pages/CustomerAnalysis';
import { InventoryAnalysis } from './pages/InventoryAnalysis';
import { LogisticsAnalysis } from './pages/LogisticsAnalysis';
import { ReturnAnalysis } from './pages/ReturnAnalysis';
import { BusinessInsights } from './pages/BusinessInsights';
import { DataExplorer } from './pages/DataExplorer';
import { UploadDataset } from './pages/UploadDataset';
import { UniversalDashboard } from './pages/UniversalDashboard';
import { PythonHub } from './pages/PythonHub';
import { AboutProject } from './pages/AboutProject';

const AppContent: React.FC = () => {
  const [activePage, setActivePage] = useState<PageId>('executive');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const renderActivePage = () => {
    switch (activePage) {
      case 'executive':
        return <ExecutiveDashboard onNavigate={setActivePage} />;
      case 'sales':
        return <SalesAnalysis />;
      case 'customers':
        return <CustomerAnalysis />;
      case 'inventory':
        return <InventoryAnalysis />;
      case 'logistics':
        return <LogisticsAnalysis />;
      case 'returns':
        return <ReturnAnalysis />;
      case 'insights':
        return <BusinessInsights />;
      case 'explorer':
        return <DataExplorer />;
      case 'upload':
        return <UploadDataset onNavigate={setActivePage} />;
      case 'universal':
        return <UniversalDashboard onNavigate={setActivePage} />;
      case 'python':
        return <PythonHub />;
      case 'about':
        return <AboutProject />;
      default:
        return <ExecutiveDashboard onNavigate={setActivePage} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar Navigation */}
      <Sidebar
        activePage={activePage}
        onSelectPage={(page) => setActivePage(page)}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-h-screen transition-all duration-300 ${
          sidebarCollapsed ? 'ml-18' : 'ml-64'
        }`}
      >
        <Navbar
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
          onNavigate={(page) => setActivePage(page)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <DatasetProvider>
      <FilterProvider>
        <AppContent />
      </FilterProvider>
    </DatasetProvider>
  );
}
