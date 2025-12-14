import React from 'react'
import SubFeatureCard from '../components/SubFeatureCard'
import { Battery, Zap, Wind, Wifi, Cpu, Network, Gauge, Settings } from 'lucide-react'
import './FeaturePage.css'

const Feature2Page: React.FC = () => {
  const subFeatures = [
    {
      id: 1,
      title: 'Sub Feature 1',
      description: 'Monitor system performance and resource utilization in real-time.',
      icon: <Battery size={24} />,
    },
    {
      id: 2,
      title: 'Sub Feature 2',
      description: 'Optimize energy consumption with intelligent power management.',
      icon: <Zap size={24} />,
    },
    {
      id: 3,
      title: 'Sub Feature 3',
      description: 'Control and manage network connectivity with ease.',
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
    {
      id: 6,
      title: 'Sub Feature 6',
      description: 'Manage network protocols and connectivity options.',
      icon: <Network size={24} />,
    },
    {
      id: 7,
      title: 'Sub Feature 7',
      description: 'Track performance gauges and system health indicators.',
      icon: <Gauge size={24} />,
    },
    {
      id: 8,
      title: 'Sub Feature 8',
      description: 'Fine-tune system preferences and advanced configurations.',
      icon: <Settings size={24} />,
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
