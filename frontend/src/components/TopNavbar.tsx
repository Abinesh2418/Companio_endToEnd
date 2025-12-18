import React, { useState, useEffect } from 'react'
import { Search, Bell, Moon, Sun, Menu, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import './TopNavbar.css'

interface TopNavbarProps {
  onToggleSidebar?: () => void
}

const TopNavbar: React.FC<TopNavbarProps> = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth()
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme')
    return saved === 'dark'
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [showUserMenu, setShowUserMenu] = useState(false)

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark-mode')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark-mode')
      localStorage.setItem('theme', 'light')
    }
  }, [isDarkMode])

  const handleThemeToggle = () => {
    setIsDarkMode(!isDarkMode)
  }

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    console.log('Search query:', searchQuery)
  }

  return (
    <header className="top-navbar">
      <div className="navbar-content">
        <button
          className="navbar-menu-button"
          onClick={onToggleSidebar}
          title="Toggle sidebar"
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>

        <form className="search-bar" onSubmit={handleSearch}>
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search..."
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>

        <div className="navbar-actions">
          <button
            className="navbar-icon-button"
            title="Notifications"
            aria-label="Notifications"
          >
            <Bell size={20} />
            <span className="notification-badge">3</span>
          </button>

          <button
            className="navbar-icon-button"
            onClick={handleThemeToggle}
            title={isDarkMode ? 'Light mode' : 'Dark mode'}
            aria-label={isDarkMode ? 'Light mode' : 'Dark mode'}
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          <div className="navbar-divider"></div>

          <div className="user-menu-container">
            <button
              className="navbar-user-button"
              onClick={() => setShowUserMenu(!showUserMenu)}
              title="User profile"
              aria-label="User profile"
            >
              <div className="user-avatar-small">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="user-name-small">{user?.username || 'User'}</span>
            </button>

            {showUserMenu && (
              <div className="user-dropdown-menu">
                <div className="user-dropdown-header">
                  <div className="user-avatar-large">
                    {user?.username?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="user-info">
                    <div className="user-name-large">{user?.username || 'User'}</div>
                    <div className="user-email">{user?.email || 'user@example.com'}</div>
                  </div>
                </div>
                <div className="user-dropdown-divider"></div>
                <button className="user-dropdown-item logout-btn" onClick={logout}>
                  <LogOut size={18} />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default TopNavbar
