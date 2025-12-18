import React, { useState, useEffect } from 'react';
import './ProductivityMotivation.css';

interface Reminder {
  id: string;
  reminder_type: string;
  title: string;
  message: string;
  motivation_level: string;
  scheduled_time: string;
  status: string;
  delivered_at?: string;
  seen_at?: string;
}



const ProductivityMotivation: React.FC = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  const API_BASE = 'http://localhost:8000/api';

  useEffect(() => {
    fetchPendingReminders();
    fetchReminders();
    
    // Update current time every second
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);

  const fetchPendingReminders = async () => {
    try {
      // Fetch and auto-deliver pending reminders
      const response = await fetch(`${API_BASE}/productivity/reminders/pending`);
      const data = await response.json();
      if (data.reminders && data.reminders.length > 0) {
        // Show notification
        console.log(`${data.count} new reminder(s) delivered!`);
      }
    } catch (error) {
      console.error('Failed to fetch pending reminders:', error);
    }
  };

  const fetchReminders = async () => {
    try {
      const response = await fetch(`${API_BASE}/productivity/reminders`);
      const data = await response.json();
      // Only show pending and delivered reminders, hide dismissed and seen ones
      const activeReminders = (data.reminders || []).filter(
        (r: Reminder) => r.status === 'pending' || r.status === 'delivered'
      );
      setReminders(activeReminders);
    } catch (error) {
      console.error('Failed to fetch reminders:', error);
    } finally {
      setLoading(false);
    }
  };



  const generateDailyCheckin = async () => {
    try {
      const response = await fetch(`${API_BASE}/productivity/daily-checkin`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        alert(errorData.detail || 'Failed to generate daily check-in');
        return;
      }
      
      const data = await response.json();
      alert('Daily check-in reminder created! ✨');
      fetchReminders();
    } catch (error) {
      console.error('Failed to generate check-in:', error);
      alert('Failed to generate daily check-in. Please try again.');
    }
  };

  const generateReminders = async () => {
    try {
      const response = await fetch(`${API_BASE}/productivity/reminders/generate`, {
        method: 'POST',
      });
      const data = await response.json();
      alert(`${data.reminders_generated} reminder(s) generated! 🎯`);
      fetchReminders();
    } catch (error) {
      console.error('Failed to generate reminders:', error);
    }
  };

  const clearAllReminders = async () => {
    if (!confirm('Clear all reminders? You will need to log out and log back in to generate a fresh daily check-in.')) {
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/productivity/reminders/clear-all`, {
        method: 'DELETE',
      });
      const data = await response.json();
      alert(`✅ Cleared ${data.count} reminder(s)! Please log out and log back in.`);
      fetchReminders();
    } catch (error) {
      console.error('Failed to clear reminders:', error);
      alert('❌ Failed to clear reminders');
    }
  };

  const markReminderAsSeen = async (reminderId: string) => {
    try {
      await fetch(`${API_BASE}/productivity/reminders/${reminderId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'seen', action_taken: true }),
      });
      // Remove the reminder from the list immediately
      setReminders(reminders.filter(r => r.id !== reminderId));
    } catch (error) {
      console.error('Failed to mark reminder:', error);
    }
  };

  const dismissReminder = async (reminderId: string) => {
    try {
      await fetch(`${API_BASE}/productivity/reminders/${reminderId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'dismissed', action_taken: false }),
      });
      // Remove the reminder from the list immediately
      setReminders(reminders.filter(r => r.id !== reminderId));
    } catch (error) {
      console.error('Failed to dismiss reminder:', error);
    }
  };



  const formatTime = (dateString: string) => {
    const date = new Date(dateString + 'Z'); // Add Z to indicate UTC time
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatCurrentDateTime = () => {
    const dateStr = currentTime.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
    const timeStr = currentTime.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
    return { date: dateStr, time: timeStr };
  };



  const getMotivationEmoji = (level: string) => {
    switch (level) {
      case 'positive': return '🌟';
      case 'encouraging': return '💪';
      case 'gentle': return '💚';
      default: return '✨';
    }
  };

  if (loading) {
    return <div className="productivity-loading">Loading productivity data...</div>;
  }

  return (
    <div className="productivity-motivation">
      <div className="productivity-header">
        <h1>🎯 Smart Productivity & Motivation</h1>
        <p>Stay motivated and productive with context-aware reminders</p>
      </div>

      <div className="reminders-section">
          <div className="current-datetime-display">
            <div className="datetime-item">
              <span className="datetime-icon">📅</span>
              <span className="datetime-value">{formatCurrentDateTime().date}</span>
            </div>
            <div className="datetime-item">
              <span className="datetime-icon">⏰</span>
              <span className="datetime-label">Current Time:</span>
              <span className="datetime-value">{formatCurrentDateTime().time}</span>
            </div>
          </div>
          
          <div className="action-buttons">
            <button className="btn-primary" onClick={generateDailyCheckin}>
              ☀️ Generate Daily Check-In
            </button>
            <button className="btn-secondary" onClick={generateReminders}>
              🔔 Generate Smart Reminders
            </button>
            <button className="btn-danger" onClick={clearAllReminders}>
              🗑️ Clear All Reminders
            </button>
          </div>

          <div className="reminders-list">
            {reminders.length === 0 ? (
              <div className="empty-state">
                <p>📭 No reminders yet</p>
                <p>Your daily check-in will appear here when you log in!</p>
              </div>
            ) : (
              reminders
                .sort((a, b) => new Date(b.scheduled_time).getTime() - new Date(a.scheduled_time).getTime())
                .map((reminder) => (
                <div key={reminder.id} className={`reminder-card ${reminder.status} ${reminder.status === 'delivered' ? 'new-reminder' : ''}`}>
                  <div className="reminder-header">
                    <span className="reminder-type">
                      {getMotivationEmoji(reminder.motivation_level)} {reminder.title}
                    </span>
                  </div>
                  <div className="reminder-timestamp">
                    <span className="timestamp-icon">📅</span> {formatTime(reminder.scheduled_time)}
                  </div>
                  <div className="reminder-message">{reminder.message}</div>
                  <div className="reminder-actions">
                    {(reminder.status === 'pending' || reminder.status === 'delivered') && (
                      <>
                        <button
                          className="btn-action"
                          onClick={() => markReminderAsSeen(reminder.id)}
                        >
                          ✅ Got it!
                        </button>
                        <button
                          className="btn-dismiss"
                          onClick={() => dismissReminder(reminder.id)}
                        >
                          ❌ Dismiss
                        </button>
                      </>
                    )}
                    {reminder.status === 'seen' && (
                      <span className="status-badge seen">✓ Seen</span>
                    )}
                    {reminder.status === 'dismissed' && (
                      <span className="status-badge dismissed">Dismissed</span>
                    )}
                    {reminder.status === 'pending' && (
                      <span className="status-badge pending">⏳ Scheduled</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
    </div>
  );
};

export default ProductivityMotivation;
