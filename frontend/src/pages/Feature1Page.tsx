import React from 'react'
import SubFeatureCard from '../components/SubFeatureCard'
import { Zap, Award, Flame, Lightbulb, Rocket, Shield, Star, TrendingUp } from 'lucide-react'
import './FeaturePage.css'

const Feature1Page: React.FC = () => {
  const subFeatures = [
    {
      id: 1,
      title: 'Sub Feature 1',
      description: 'Explore the capabilities of sub feature 1 with advanced analytics and insights.',
      icon: <Zap size={24} />,
    },
    {
      id: 2,
      title: 'Sub Feature 2',
      description: 'Get detailed reports and monitor your performance with real-time data.',
      icon: <Award size={24} />,
    },
    {
      id: 3,
      title: 'Sub Feature 3',
      description: 'Create and manage customized workflows to optimize your operations.',
      icon: <Flame size={24} />,
    },
    {
      id: 4,
      title: 'Sub Feature 4',
      description: 'Access intelligent recommendations based on your usage patterns.',
      icon: <Lightbulb size={24} />,
    },
    {
      id: 5,
      title: 'Sub Feature 5',
      description: 'Integrate seamlessly with your favorite tools and platforms.',
      icon: <Rocket size={24} />,
    },
  ]

  return (
    <div className="feature-page">
      <div className="page-header">
        <h1 className="page-title">Feature 1</h1>
        <p className="page-description">
          Discover all the powerful capabilities and tools available in Feature 1
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

export default Feature1Page
