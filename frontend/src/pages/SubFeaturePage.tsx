import React from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import './SubFeaturePage.css'

const SubFeaturePage: React.FC = () => {
  const { subFeatureId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  // Get feature from current path
  const featureId = location.pathname.split('/')[1]

  const handleBack = () => {
    navigate(`/${featureId}`)
  }

  // Convert sub-feature-1 to Sub Feature 1
  const subFeatureTitle = subFeatureId
    ?.split('-')
    .map((word, index) => 
      index === 0 || index === 1 
        ? word.charAt(0).toUpperCase() + word.slice(1) 
        : word
    )
    .join(' ')

  const featureTitle = featureId
    ?.split(/(\d+)/)
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
    .trim()

  return (
    <div className="sub-feature-page">
      <button className="back-button" onClick={handleBack}>
        <ArrowLeft size={20} />
        <span>Back to {featureTitle}</span>
      </button>

      <div className="sub-feature-content">
        <div className="sub-feature-header">
          <h1 className="sub-feature-title">{subFeatureTitle}</h1>
          <p className="sub-feature-breadcrumb">
            {featureTitle} / {subFeatureTitle}
          </p>
        </div>

        <div className="sub-feature-body">
          <div className="placeholder-message">
            <h2>Update the {subFeatureTitle} work here</h2>
            <p>This is where you can add specific functionality for {subFeatureTitle}.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SubFeaturePage
