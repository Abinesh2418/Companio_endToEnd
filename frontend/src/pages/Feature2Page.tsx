import React from 'react'
import SubFeatureCard from '../components/SubFeatureCard'
import { Target, Zap, Wind, Wifi, Cpu, Network, Gauge, Settings } from 'lucide-react'
import './FeaturePage.css'

const Feature2Page: React.FC = () => {
  const subFeatures = [
    {
      id: 1,
      title: 'Goal Creation & Planning',
      description: 'Transform your aspirations into structured, actionable plans with clear timelines.',
      icon: <Target size={24} />,
    },
    {
      id: 2,
      title: 'Intelligent Task Breakdown & Customization',
      description: 'Automatically decompose goals into structured tasks and customize them.',
      icon: <Zap size={24} />,
    },
    {
      id: 3,
      title: 'Smart Proactive Productivity & Motivation',
      description: 'Context-aware reminders and motivation system to reduce procrastination.',
      icon: <Wind size={24} />,
    },
    {
      id: 4,
      title: 'Sub Feature 4',
      description: 'Configure wireless settings and connections effortlessly.',
      icon: <Wifi size={24} />,
    },
    {
      id: 5,
      title: 'Sub Feature 5',
      description: 'Access processor information and performance metrics.',
      icon: <Cpu size={24} />,
    },
  ]

  return (
    <div className="feature-page">
      <div className="page-header">
        <h1 className="page-title">Feature 2</h1>
        <p className="page-description">
          Manage and optimize all system features with comprehensive control tools
        </p>
      </div>

      <div className="cards-grid">
        {subFeatures.map((feature) => (
          <SubFeatureCard
            key={feature.id}
            title={feature.title}
            description={feature.description}
            icon={feature.icon}
          />
        ))}
      </div>
    </div>
  )
}

export default Feature2Page
