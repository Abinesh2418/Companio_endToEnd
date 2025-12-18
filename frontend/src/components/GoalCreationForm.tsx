import React, { useState } from 'react';
import './GoalCreationForm.css';

interface GoalFormData {
  title: string;
  duration_weeks: number;
  priority: 'Low' | 'Medium' | 'High';
  intensity: 'Light' | 'Normal' | 'Aggressive';
}

interface GoalResponse {
  id: string;
  title: string;
  duration_weeks: number;
  priority: string;
  intensity: string;
  start_date: string;
  end_date: string;
  created_at: string;
}

const GoalCreationForm: React.FC = () => {
  const [formData, setFormData] = useState<GoalFormData>({
    title: '',
    duration_weeks: 1,
    priority: 'Medium',
    intensity: 'Normal'
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [createdGoal, setCreatedGoal] = useState<GoalResponse | null>(null);

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
    
    // Clear error for this field
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
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setSuccessMessage('');
    setCreatedGoal(null);

    try {
      const response = await fetch('http://localhost:8000/api/goals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create goal');
      }

      const data: GoalResponse = await response.json();
      setCreatedGoal(data);
      setSuccessMessage('Goal created successfully! 🎉');
      
      // Reset form
      setFormData({
        title: '',
        duration_weeks: 1,
        priority: 'Medium',
        intensity: 'Normal'
      });
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage('');
        setCreatedGoal(null);
      }, 5000);

    } catch (error) {
      setErrors({ 
        submit: error instanceof Error ? error.message : 'An error occurred. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="goal-creation-container">
      <div className="goal-creation-header">
        <h2 className="goal-creation-title">Create Your Goal</h2>
        <p className="goal-creation-description">
          Transform your aspirations into structured, actionable plans. Define your goal, 
          set the timeline, and let AI Companio help you achieve it.
        </p>
      </div>

      {successMessage && (
        <div className="success-banner">
          <div className="success-content">
            <span className="success-icon">✓</span>
            <div>
              <p className="success-title">{successMessage}</p>
              {createdGoal && (
                <p className="success-details">
                  Your goal "{createdGoal.title}" is scheduled from{' '}
                  {new Date(createdGoal.start_date).toLocaleDateString()} to{' '}
                  {new Date(createdGoal.end_date).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="goal-form">
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
            <label htmlFor="priority" className="form-label">
              Priority Level
            </label>
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
            <label htmlFor="intensity" className="form-label">
              Learning Intensity
            </label>
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
          <div className="error-banner">
            <span className="error-icon">⚠</span>
            {errors.submit}
          </div>
        )}

        <div className="form-actions">
          <button 
            type="submit" 
            className="submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating Goal...' : 'Create Goal'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default GoalCreationForm;
