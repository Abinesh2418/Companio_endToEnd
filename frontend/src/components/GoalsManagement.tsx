import React, { useState, useEffect } from 'react';
import { Pencil, Trash2, Plus, X, ArrowLeft } from 'lucide-react';
import './GoalsManagement.css';

interface Goal {
  id: string;
  title: string;
  duration_weeks: number;
  priority: 'Low' | 'Medium' | 'High';
  intensity: 'Light' | 'Normal' | 'Aggressive';
  start_date: string;
  end_date: string;
  created_at: string;
}

interface GoalFormData {
  title: string;
  duration_weeks: number;
  priority: 'Low' | 'Medium' | 'High';
  intensity: 'Light' | 'Normal' | 'Aggressive';
}

const GoalsManagement: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [formData, setFormData] = useState<GoalFormData>({
    title: '',
    duration_weeks: 1,
    priority: 'Medium',
    intensity: 'Normal'
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');

  // Fetch all goals
  const fetchGoals = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/goals');
      const data = await response.json();
      setGoals(data.goals || []);
    } catch (error) {
      console.error('Error fetching goals:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Goal title is required';
    } else if (formData.title.length > 200) {
      newErrors.title = 'Goal title must be less than 200 characters';
    }
    if (formData.duration_weeks < 1 || formData.duration_weeks > 52) {
      newErrors.duration_weeks = 'Duration must be between 1 and 52 weeks';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'duration_weeks' ? parseInt(value) || 1 : value
    }));
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    setSuccessMessage('');

    try {
      const url = editingGoal 
        ? `http://localhost:8000/api/goals/${editingGoal.id}`
        : 'http://localhost:8000/api/goals';
      
      const method = editingGoal ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save goal');
      }

      setSuccessMessage(editingGoal ? 'Goal updated successfully! 🎉' : 'Goal created successfully! 🎉');
      
      setFormData({
        title: '',
        duration_weeks: 1,
        priority: 'Medium',
        intensity: 'Normal'
      });
      setShowForm(false);
      setEditingGoal(null);
      
      await fetchGoals();
      
      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      setErrors({ 
        submit: error instanceof Error ? error.message : 'An error occurred. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (goal: Goal) => {
    setEditingGoal(goal);
    setFormData({
      title: goal.title,
      duration_weeks: goal.duration_weeks,
      priority: goal.priority,
      intensity: goal.intensity
    });
    setShowForm(true);
    setSelectedGoal(null);
    setErrors({});
  };

  const handleDelete = async (goalId: string, goalTitle: string) => {
    if (!confirm(`Are you sure you want to delete "${goalTitle}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/goals/${goalId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // If goal not found (404), it might have been deleted already or backend restarted
        if (response.status === 404) {
          setSuccessMessage('Goal has already been deleted or not found. Refreshing list...');
          setSelectedGoal(null);
          await fetchGoals();
          setTimeout(() => setSuccessMessage(''), 3000);
          return;
        }
        
        throw new Error(errorData.detail || 'Failed to delete goal');
      }

      setSuccessMessage('Goal deleted successfully! ✓');
      setSelectedGoal(null);
      await fetchGoals();
      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error deleting goal. Please try again.';
      setErrors({ submit: errorMessage });
      setTimeout(() => setErrors({}), 5000);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingGoal(null);
    setSelectedGoal(null);
    setFormData({
      title: '',
      duration_weeks: 1,
      priority: 'Medium',
      intensity: 'Normal'
    });
    setErrors({});
  };

  const handleGoalClick = (goal: Goal) => {
    setSelectedGoal(goal);
    setShowForm(false);
  };

  const handleBackToList = () => {
    setSelectedGoal(null);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'priority-high';
      case 'Medium': return 'priority-medium';
      case 'Low': return 'priority-low';
      default: return '';
    }
  };

  return (
    <div className="goals-management">
      {selectedGoal ? (
        <div className="goal-detail-view">
          <button className="back-to-list-btn" onClick={handleBackToList}>
            ← Back to Goals
          </button>
          
          <div className="goal-detail-card">
            <div className="goal-detail-header">
              <div className="goal-detail-title-section">
                <h2 className="goal-detail-title">{selectedGoal.title}</h2>
                <div className="goal-detail-actions">
                  <button 
                    className="detail-action-btn edit-detail-btn" 
                    onClick={() => handleEdit(selectedGoal)}
                  >
                    <Pencil size={18} />
                    Edit Goal
                  </button>
                  <button 
                    className="detail-action-btn delete-detail-btn" 
                    onClick={() => handleDelete(selectedGoal.id, selectedGoal.title)}
                  >
                    <Trash2 size={18} />
                    Delete Goal
                  </button>
                </div>
              </div>
            </div>

            <div className="goal-detail-content">
              <div className="goal-detail-grid">
                <div className="detail-card">
                  <div className="detail-card-icon">📅</div>
                  <h3 className="detail-card-title">Duration</h3>
                  <p className="detail-card-value">{selectedGoal.duration_weeks} weeks</p>
                </div>

                <div className="detail-card">
                  <div className="detail-card-icon">📊</div>
                  <h3 className="detail-card-title">Priority</h3>
                  <p className={`detail-card-badge ${getPriorityColor(selectedGoal.priority)}`}>
                    {selectedGoal.priority}
                  </p>
                </div>

                <div className="detail-card">
                  <div className="detail-card-icon">⚡</div>
                  <h3 className="detail-card-title">Intensity</h3>
                  <p className="detail-card-value">{selectedGoal.intensity}</p>
                </div>
              </div>

              <div className="timeline-section">
                <h3 className="section-title">Timeline</h3>
                <div className="timeline-details">
                  <div className="timeline-item">
                    <span className="timeline-label">Start Date:</span>
                    <span className="timeline-value">
                      {new Date(selectedGoal.start_date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                  <div className="timeline-item">
                    <span className="timeline-label">End Date:</span>
                    <span className="timeline-value">
                      {new Date(selectedGoal.end_date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                  <div className="timeline-item">
                    <span className="timeline-label">Created:</span>
                    <span className="timeline-value">
                      {new Date(selectedGoal.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                </div>
              </div>

              <div className="progress-section">
                <h3 className="section-title">Progress</h3>
                <div className="progress-placeholder">
                  <p>Track your progress here. This section can be enhanced with milestones and completion tracking.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="goals-header">
            <div>
              <h2 className="goals-title">Goal Creation & Planning</h2>
              <p className="goals-description">
                Transform your aspirations into structured, actionable plans
              </p>
            </div>
            {!showForm && (
              <button className="add-goal-btn" onClick={() => setShowForm(true)}>
                <Plus size={20} />
                Create New Goal
              </button>
            )}
          </div>

          {successMessage && (
            <div className="success-alert">
              <span className="success-icon">✓</span>
              {successMessage}
            </div>
          )}

          {errors.submit && (
            <div className="error-alert">
              <span className="error-icon">⚠</span>
              {errors.submit}
            </div>
          )}

          {showForm && (
            <div className="goal-form-card">
              <div className="form-card-header">
                <h3>{editingGoal ? 'Edit Goal' : 'Create New Goal'}</h3>
                <button className="close-btn" onClick={handleCancel}>
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="title" className="form-label">
                    Goal Title <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    className={`form-input ${errors.title ? 'input-error' : ''}`}
                    placeholder="e.g., Learn React and Build a Portfolio Project"
                    maxLength={200}
                  />
                  {errors.title && <span className="error-message">{errors.title}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="duration_weeks" className="form-label">
                    Duration (weeks) <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    id="duration_weeks"
                    name="duration_weeks"
                    value={formData.duration_weeks}
                    onChange={handleInputChange}
                    className={`form-input ${errors.duration_weeks ? 'input-error' : ''}`}
                    min="1"
                    max="52"
                  />
                  {errors.duration_weeks && (
                    <span className="error-message">{errors.duration_weeks}</span>
                  )}
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="priority" className="form-label">Priority Level</label>
                    <select
                      id="priority"
                      name="priority"
                      value={formData.priority}
                      onChange={handleInputChange}
                      className="form-select"
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="intensity" className="form-label">Learning Intensity</label>
                    <select
                      id="intensity"
                      name="intensity"
                      value={formData.intensity}
                      onChange={handleInputChange}
                      className="form-select"
                    >
                      <option value="Light">Light - Casual pace</option>
                      <option value="Normal">Normal - Steady progress</option>
                      <option value="Aggressive">Aggressive - Fast track</option>
                    </select>
                  </div>
                </div>

                {errors.submit && (
                  <div className="error-alert">
                    <span className="error-icon">⚠</span>
                    {errors.submit}
                  </div>
                )}

                <div className="form-actions">
                  <button type="button" className="cancel-btn" onClick={handleCancel}>
                    Cancel
                  </button>
                  <button type="submit" className="submit-btn" disabled={isSubmitting}>
                    {isSubmitting ? 'Saving...' : (editingGoal ? 'Update Goal' : 'Create Goal')}
                  </button>
                </div>
              </form>
            </div>
          )}

          {!showForm && (
            <div className="goals-list">
              <h3 className="list-title">Your Goals ({goals.length})</h3>
              
              {loading ? (
                <div className="loading-state">Loading goals...</div>
              ) : goals.length === 0 ? (
                <div className="empty-state">
                  <p>No goals yet. Create your first goal to get started!</p>
                </div>
              ) : (
                <div className="goals-grid">
                  {goals.map((goal) => (
                    <div 
                      key={goal.id} 
                      className="goal-card"
                      onClick={() => handleGoalClick(goal)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="goal-card-header">
                        <h4 className="goal-title">{goal.title}</h4>
                        <div className="goal-actions" onClick={(e) => e.stopPropagation()}>
                          <button 
                            className="action-btn edit-btn" 
                            onClick={() => handleEdit(goal)}
                            title="Edit goal"
                          >
                            <Pencil size={16} />
                          </button>
                          <button 
                            className="action-btn delete-btn" 
                            onClick={() => handleDelete(goal.id, goal.title)}
                            title="Delete goal"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>
                      
                      <div className="goal-details">
                        <div className="detail-row">
                          <span className="detail-label">Duration:</span>
                          <span className="detail-value">{goal.duration_weeks} weeks</span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Timeline:</span>
                          <span className="detail-value">
                            {new Date(goal.start_date).toLocaleDateString()} - {new Date(goal.end_date).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Priority:</span>
                          <span className={`priority-badge ${getPriorityColor(goal.priority)}`}>
                            {goal.priority}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Intensity:</span>
                          <span className="detail-value">{goal.intensity}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default GoalsManagement;
