import React, { useState } from 'react'
import { useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopNavbar from './TopNavbar'
import './Layout.css'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  return (
    <div className="layout">
      <Sidebar currentPath={location.pathname} isOpen={isSidebarOpen} onToggle={toggleSidebar} />
      <div className={`layout-content ${!isSidebarOpen ? 'sidebar-closed' : ''}`}>
        <TopNavbar onToggleSidebar={toggleSidebar} />
        <main className="main-content">{children}</main>
      </div>
    </div>
  )
}

export default Layout
