import React, { useState, useEffect } from 'react';
import './TaskBreakdown.css';

interface Task {
  id: string;
  goal_id: string;
  week_number: number;
  day_number: number | null;
  title: string;
  description: string | null;
  status: 'Not Started' | 'In Progress' | 'Completed';
  dependencies: string[];
  order: number;
  created_at: string;
  updated_at: string;
}

interface TaskResponse {
  task: Task;
  is_locked: boolean;
}

interface WeeklyTasks {
  [weekNumber: number]: TaskResponse[];
}

interface Goal {
  id: string;
  title: string;
  duration_weeks: number;
  priority: string;
  intensity: string;
}

const TaskBreakdown: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [selectedGoalId, setSelectedGoalId] = useState<string>('');
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [tasksByWeek, setTasksByWeek] = useState<WeeklyTasks>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [showAddTask, setShowAddTask] = useState(false);
  const [newTaskData, setNewTaskData] = useState({
    title: '',
    week_number: 1,
    description: '',
  });

  const API_BASE = 'http://localhost:8000/api';

  // Fetch all goals on component mount
  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      const response = await fetch(`${API_BASE}/goals`);
      const data = await response.json();
      setGoals(data.goals || []);
      
      // Auto-select first goal if available
      if (data.goals && data.goals.length > 0) {
        setSelectedGoalId(data.goals[0].id);
      }
    } catch (err) {
      setError('Failed to fetch goals');
      console.error(err);
    }
  };

  // Fetch tasks when a goal is selected
  useEffect(() => {
    if (selectedGoalId) {
      fetchTasks();
    }
  }, [selectedGoalId]);

  const fetchTasks = async () => {
    if (!selectedGoalId) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/goals/${selectedGoalId}/tasks`);
      
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks || []);
        setTasksByWeek(data.tasks_by_week || {});
      } else if (response.status === 404) {
        // No tasks yet, clear the state
        setTasks([]);
        setTasksByWeek({});
      }
    } catch (err) {
      setError('Failed to fetch tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateTasks = async () => {
    if (!selectedGoalId) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/goals/${selectedGoalId}/tasks/generate`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks || []);
        
        // Organize by weeks
        const byWeek: WeeklyTasks = {};
        data.tasks.forEach((taskResp: TaskResponse) => {
          const week = taskResp.task.week_number;
          if (!byWeek[week]) {
            byWeek[week] = [];
          }
          byWeek[week].push(taskResp);
        });
        setTasksByWeek(byWeek);
      } else {
        setError('Failed to generate tasks');
      }
    } catch (err) {
      setError('Failed to generate tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId: string, newStatus: string) => {
    try {
      const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        fetchTasks(); // Refresh to update lock status
      } else {
        setError('Failed to update task status');
      }
    } catch (err) {
      setError('Failed to update task status');
      console.error(err);
    }
  };

  const startEditTask = (task: Task) => {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
  };

  const saveEditTask = async (taskId: string) => {
    try {
      const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          title: editTitle,
          description: editDescription || null
        }),
      });

      if (response.ok) {
        setEditingTaskId(null);
        fetchTasks();
      } else {
        setError('Failed to update task');
      }
    } catch (err) {
      setError('Failed to update task');
      console.error(err);
    }
  };

  const cancelEdit = () => {
    setEditingTaskId(null);
    setEditTitle('');
    setEditDescription('');
  };

  const deleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchTasks();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to delete task');
      }
    } catch (err) {
      setError('Failed to delete task');
      console.error(err);
    }
  };

  const addTask = async () => {
    // Find the highest order in the selected week
    const weekTasks = tasks.filter(t => t.task.week_number === newTaskData.week_number);
    const maxOrder = weekTasks.length > 0 
      ? Math.max(...weekTasks.map(t => t.task.order)) 
      : -1;

    try {
      const response = await fetch(`${API_BASE}/goals/${selectedGoalId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newTaskData,
          goal_id: selectedGoalId,
          dependencies: [],
          order: maxOrder + 1,
        }),
      });

      if (response.ok) {
        setShowAddTask(false);
        setNewTaskData({ title: '', week_number: 1, description: '' });
        fetchTasks();
      } else {
        setError('Failed to add task');
      }
    } catch (err) {
      setError('Failed to add task');
      console.error(err);
    }
  };

  const moveTask = async (taskId: string, direction: 'up' | 'down') => {
    const taskIndex = tasks.findIndex(t => t.task.id === taskId);
    if (taskIndex === -1) return;

    const currentTask = tasks[taskIndex].task;
    const swapIndex = direction === 'up' ? taskIndex - 1 : taskIndex + 1;

    if (swapIndex < 0 || swapIndex >= tasks.length) return;

    const swapTask = tasks[swapIndex].task;

    // Create reorder instructions
    const reorderData = {
      tasks: [
        {
          task_id: currentTask.id,
          new_order: swapTask.order,
          new_week_number: swapTask.week_number,
        },
        {
          task_id: swapTask.id,
          new_order: currentTask.order,
          new_week_number: currentTask.week_number,
        },
      ],
    };

    try {
      const response = await fetch(`${API_BASE}/goals/${selectedGoalId}/tasks/reorder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reorderData),
      });

      if (response.ok) {
        fetchTasks();
      } else {
        setError('Failed to reorder tasks');
      }
    } catch (err) {
      setError('Failed to reorder tasks');
      console.error(err);
    }
  };

  const moveTaskToWeek = async (taskId: string, newWeek: number) => {
    const task = tasks.find(t => t.task.id === taskId)?.task;
    if (!task) return;

    try {
      const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ week_number: newWeek }),
      });

      if (response.ok) {
        fetchTasks();
      } else {
        setError('Failed to move task to different week');
      }
    } catch (err) {
      setError('Failed to move task');
      console.error(err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'status-completed';
      case 'In Progress':
        return 'status-in-progress';
      default:
        return 'status-not-started';
    }
  };

  const selectedGoal = goals.find((g) => g.id === selectedGoalId);

  return (
    <div className="task-breakdown-container">
      <div className="task-breakdown-header">
        <h1>Intelligent Task Breakdown</h1>
        <p className="subtitle">Automatically decompose your goals into structured weekly tasks</p>
      </div>

      {/* Goal Selection */}
      <div className="goal-selection-section">
        <label htmlFor="goal-select">Select a Goal:</label>
        <select
          id="goal-select"
          value={selectedGoalId}
          onChange={(e) => setSelectedGoalId(e.target.value)}
          className="goal-select"
        >
          <option value="">-- Select a goal --</option>
          {goals.map((goal) => (
            <option key={goal.id} value={goal.id}>
              {goal.title} ({goal.duration_weeks} weeks - {goal.intensity})
            </option>
          ))}
        </select>

        {selectedGoalId && tasks.length === 0 && (
          <button onClick={generateTasks} className="btn-primary" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Tasks'}
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && <div className="error-message">{error}</div>}

      {/* Loading State */}
      {loading && <div className="loading">Loading tasks...</div>}

      {/* Task Display */}
      {selectedGoal && tasks.length > 0 && (
        <div className="tasks-section">
          <div className="tasks-header">
            <h2>Tasks for: {selectedGoal.title}</h2>
            <div className="task-actions">
              <button onClick={() => setShowAddTask(!showAddTask)} className="btn-secondary">
                + Add Custom Task
              </button>
              <button onClick={fetchTasks} className="btn-secondary">
                🔄 Refresh
              </button>
            </div>
          </div>

          {/* Add Task Form */}
          {showAddTask && (
            <div className="add-task-form">
              <h3>Add Custom Task</h3>
              <input
                type="text"
                placeholder="Task title"
                value={newTaskData.title}
                onChange={(e) => setNewTaskData({ ...newTaskData, title: e.target.value })}
                className="input-field"
              />
              <input
                type="number"
                placeholder="Week number"
                min="1"
                max={selectedGoal.duration_weeks}
                value={newTaskData.week_number}
                onChange={(e) =>
                  setNewTaskData({ ...newTaskData, week_number: parseInt(e.target.value) })
                }
                className="input-field"
              />
              <textarea
                placeholder="Description (optional)"
                value={newTaskData.description}
                onChange={(e) => setNewTaskData({ ...newTaskData, description: e.target.value })}
                className="textarea-field"
              />
              <div className="form-actions">
                <button onClick={addTask} className="btn-primary">
                  Add Task
                </button>
                <button onClick={() => setShowAddTask(false)} className="btn-secondary">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Tasks by Week */}
          <div className="weeks-container">
            {Object.keys(tasksByWeek)
              .sort((a, b) => parseInt(a) - parseInt(b))
              .map((weekNum) => (
                <div key={weekNum} className="week-section">
                  <h3 className="week-title">Week {weekNum}</h3>
                  <div className="tasks-list">
                    {tasksByWeek[parseInt(weekNum)].map((taskResp, index) => {
                      const task = taskResp.task;
                      const isLocked = taskResp.is_locked;
                      const isEditing = editingTaskId === task.id;
                      const isFirst = index === 0;
                      const isLast = index === tasksByWeek[parseInt(weekNum)].length - 1;

                      return (
                        <div
                          key={task.id}
                          className={`task-card ${isLocked ? 'task-locked' : ''} ${getStatusColor(
                            task.status
                          )}`}
                        >
                          <div className="task-reorder-controls">
                            <button
                              onClick={() => moveTask(task.id, 'up')}
                              disabled={isFirst}
                              className="btn-reorder"
                              title="Move up"
                            >
                              ↑
                            </button>
                            <button
                              onClick={() => moveTask(task.id, 'down')}
                              disabled={isLast}
                              className="btn-reorder"
                              title="Move down"
                            >
                              ↓
                            </button>
                          </div>

                          <div className="task-content">
                            {isLocked && <span className="lock-icon">🔒</span>}
                            
                            {isEditing ? (
                              <>
                                <input
                                  type="text"
                                  value={editTitle}
                                  onChange={(e) => setEditTitle(e.target.value)}
                                  className="edit-input"
                                  placeholder="Task title"
                                  autoFocus
                                />
                                <textarea
                                  value={editDescription}
                                  onChange={(e) => setEditDescription(e.target.value)}
                                  className="edit-textarea"
                                  placeholder="Task description (optional)"
                                />
                              </>
                            ) : (
                              <>
                                <h4 className="task-title">{task.title}</h4>
                                {task.description && (
                                  <p className="task-description">{task.description}</p>
                                )}
                              </>
                            )}

                            <div className="task-meta">
                              <span className={`task-status ${getStatusColor(task.status)}`}>
                                {task.status}
                              </span>
                              {task.dependencies.length > 0 && (
                                <span className="task-dependencies">
                                  {task.dependencies.length} {task.dependencies.length === 1 ? 'dependency' : 'dependencies'}
                                </span>
                              )}
                            </div>
                          </div>

                          <div className="task-actions-buttons">
                            {isEditing ? (
                              <>
                                <button onClick={() => saveEditTask(task.id)} className="btn-save">
                                  ✓ Save
                                </button>
                                <button onClick={cancelEdit} className="btn-cancel">
                                  ✗ Cancel
                                </button>
                              </>
                            ) : (
                              <>
                                {!isLocked && (
                                  <select
                                    value={task.status}
                                    onChange={(e) => updateTaskStatus(task.id, e.target.value)}
                                    className="status-select"
                                  >
                                    <option value="Not Started">Not Started</option>
                                    <option value="In Progress">In Progress</option>
                                    <option value="Completed">Completed</option>
                                  </select>
                                )}
                                <select
                                  value={task.week_number}
                                  onChange={(e) => moveTaskToWeek(task.id, parseInt(e.target.value))}
                                  className="week-select"
                                  title="Move to week"
                                >
                                  {Array.from({ length: selectedGoal.duration_weeks }, (_, i) => i + 1).map(
                                    (week) => (
                                      <option key={week} value={week}>
                                        Week {week}
                                      </option>
                                    )
                                  )}
                                </select>
                                <button
                                  onClick={() => startEditTask(task)}
                                  className="btn-edit"
                                  title="Edit task"
                                >
                                  ✏️ Edit
                                </button>
                                <button
                                  onClick={() => deleteTask(task.id)}
                                  className="btn-delete"
                                  title="Delete task"
                                >
                                  🗑️
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {selectedGoalId && tasks.length === 0 && !loading && (
        <div className="empty-state">
          <p>No tasks generated yet. Click "Generate Tasks" to create a breakdown for this goal.</p>
        </div>
      )}

      {!selectedGoalId && !loading && (
        <div className="empty-state">
          <p>Select a goal to view or generate task breakdown.</p>
        </div>
      )}
    </div>
  );
};

export default TaskBreakdown;
