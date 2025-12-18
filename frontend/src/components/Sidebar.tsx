import React from 'react'
import { Link } from 'react-router-dom'
import { Grid2X2, Zap } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import './Sidebar.css'

interface SidebarProps {
  currentPath: string
  isOpen: boolean
  onToggle: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ currentPath, isOpen }) => {
  const { user } = useAuth()
  
  const navigationItems = [
    {
      id: 'feature2',
      label: 'Feature 2',
      path: '/feature2',
      icon: Zap,
    },
  ]

  return (
    <aside className={`sidebar ${!isOpen ? 'sidebar-collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">C</div>
          <span className="logo-text">AI Companio</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigationItems.map((item) => {
          const IconComponent = item.icon
          const isActive = currentPath === item.path

          return (
            <Link
              key={item.id}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <IconComponent size={20} className="nav-icon" />
              <span className="nav-label">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="user-avatar">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="user-info">
            <p className="user-name">{user?.username || 'User'}</p>
            <p className="user-email">{user?.email || 'user@example.com'}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
