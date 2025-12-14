import React, { useState, useEffect } from 'react'
import { Search, Bell, Moon, Sun, Menu } from 'lucide-react'
import './TopNavbar.css'

interface TopNavbarProps {
  onToggleSidebar?: () => void
}

const TopNavbar: React.FC<TopNavbarProps> = ({ onToggleSidebar }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme')
    return saved === 'dark'
  })
  const [searchQuery, setSearchQuery] = useState('')

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

          <button
            className="navbar-user-button"
            title="User profile"
            aria-label="User profile"
          >
            <div className="user-avatar-small">U</div>
            <span className="user-name-small">User</span>
          </button>
        </div>
      </div>
    </header>
  )
}

export default TopNavbar
