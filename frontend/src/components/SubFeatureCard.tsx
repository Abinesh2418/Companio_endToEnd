import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import './SubFeatureCard.css'

interface SubFeatureCardProps {
  title: string
  description: string
  icon?: React.ReactNode
}

const SubFeatureCard: React.FC<SubFeatureCardProps> = ({
  title,
  description,
  icon,
}) => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleClick = () => {
    // Convert "Sub Feature 1" to "sub-feature-1"
    const subFeatureId = title.toLowerCase().replace(/\s+/g, '-')
    
    // Get current feature (feature1 or feature2)
    const currentFeature = location.pathname.split('/')[1]
    
    // Navigate to sub-feature page
    navigate(`/${currentFeature}/${subFeatureId}`)
  }

  return (
    <div className="sub-feature-card" onClick={handleClick}>
      {icon && <div className="card-icon">{icon}</div>}
      <h3 className="card-title">{title}</h3>
      <p className="card-description">{description}</p>
    </div>
  )
}

export default SubFeatureCard
