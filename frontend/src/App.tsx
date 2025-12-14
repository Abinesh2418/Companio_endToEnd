import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components'
import { Feature1Page, Feature2Page } from './pages'
import SubFeaturePage from './pages/SubFeaturePage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/feature1" replace />} />
          <Route path="/feature1" element={<Feature1Page />} />
          <Route path="/feature1/:subFeatureId" element={<SubFeaturePage />} />
          <Route path="/feature2" element={<Feature2Page />} />
          <Route path="/feature2/:subFeatureId" element={<SubFeaturePage />} />
          <Route path="*" element={<Navigate to="/feature1" replace />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
