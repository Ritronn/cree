import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, BookOpen, Zap, LogOut, Clock, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { dashboardAPI } from '../services/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getOverview();
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('isAuthenticated');
    navigate('/signin');
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getTimeRemaining = (expiresAt) => {
    if (!expiresAt) return 'Expired';
    const now = new Date();
    const expiry = new Date(expiresAt);
    const diff = expiry - now;
    
    if (diff <= 0) return 'Expired';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center">
        <div className="text-red-400 text-xl">{error}</div>
      </div>
    );
  }

  const {
    completion_percentage = 0,
    total_sessions = 0,
    completed_tests = 0,
    pending_tests = 0,
    weekly_sessions = [],
    session_limit = {},
    weak_points_count = 0,
    stats = {}
  } = dashboardData || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50 bg-slate-950/50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="w-8 h-8 text-pink-500" fill="#E945F5" />
            <span className="text-xl font-bold">Adaptive Learning</span>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/weak-points')}
              className="px-4 py-2 rounded-lg hover:bg-white/5 transition-colors"
            >
              Weak Points {weak_points_count > 0 && `(${weak_points_count})`}
            </button>
            <button 
              onClick={handleLogout}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Completion Bar - Very Top */}
      <div className="bg-slate-900/50 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Completion</span>
            <span className="text-2xl font-bold text-pink-500">{completion_percentage.toFixed(1)}%</span>
          </div>
          <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${completion_percentage}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="h-full bg-gradient-to-r from-pink-500 to-blue-500 rounded-full"
            />
          </div>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
            <span>{completed_tests} tests completed</span>
            <span>{total_sessions} total sessions</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Session Limit & Create Button */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">My Study Sessions</h1>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${session_limit.can_create ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-gray-400">
                  {session_limit.sessions_today || 0}/{session_limit.max_sessions || 3} sessions today
                </span>
              </div>
              {pending_tests > 0 && (
                <div className="flex items-center gap-2 text-orange-400">
                  <AlertCircle className="w-4 h-4" />
                  <span>{pending_tests} pending test{pending_tests > 1 ? 's' : ''}</span>
                </div>
              )}
            </div>
          </div>

          {session_limit.can_create ? (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/create-session')}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-pink-500/50 transition-all"
            >
              <Plus className="w-5 h-5" />
              Create New Session
            </motion.button>
          ) : (
            <div className="text-right">
              <div className="px-6 py-3 bg-red-500/20 border border-red-500/30 rounded-lg">
                <div className="flex items-center gap-2 text-red-400 mb-1">
                  <XCircle className="w-5 h-5" />
                  <span className="font-semibold">Cannot Create Session</span>
                </div>
                <p className="text-sm text-gray-400">{session_limit.blocked_reason}</p>
              </div>
            </div>
          )}
        </div>

        {/* Pending Tests Section */}
        {pending_tests > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <AlertCircle className="w-6 h-6 text-orange-400" />
              Pending Tests
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {weekly_sessions
                .filter(s => s.test_status?.exists && !s.test_status?.completed && !s.test_status?.expired)
                .map((session) => (
                  <motion.div
                    key={session.id}
                    whileHover={{ y: -4 }}
                    className="p-6 rounded-xl bg-orange-500/10 border border-orange-500/30 hover:border-orange-500/50 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="p-2 rounded-lg bg-orange-500/20">
                        <BookOpen className="w-5 h-5 text-orange-400" />
                      </div>
                      <div className="flex items-center gap-1 text-orange-400 text-sm">
                        <Clock className="w-4 h-4" />
                        <span>{getTimeRemaining(session.test_status?.expires_at)}</span>
                      </div>
                    </div>
                    <h3 className="font-bold mb-2">{session.workspace_name}</h3>
                    <p className="text-sm text-gray-400 mb-4">
                      Session completed {new Date(session.ended_at).toLocaleDateString()}
                    </p>
                    <button
                      onClick={() => navigate(`/test/${session.id}`)}
                      className="w-full py-2 bg-orange-500 hover:bg-orange-600 rounded-lg font-semibold transition-colors"
                    >
                      Start Test
                    </button>
                  </motion.div>
                ))}
            </div>
          </div>
        )}

        {/* Weekly Sessions Grid */}
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4">This Week's Sessions</h2>
          {weekly_sessions.length === 0 ? (
            <div className="text-center py-12 bg-white/5 rounded-xl border border-white/10">
              <BookOpen className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400 mb-4">No sessions this week</p>
              <button
                onClick={() => navigate('/create-session')}
                className="px-6 py-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold"
              >
                Create Your First Session
              </button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {weekly_sessions.map((session) => {
                const testStatus = session.test_status || {};
                const isCompleted = session.is_completed;
                const hasTest = testStatus.exists;
                const testCompleted = testStatus.completed;
                const testExpired = testStatus.expired;

                return (
                  <motion.div
                    key={session.id}
                    whileHover={{ y: -4 }}
                    className="p-6 rounded-xl bg-white/5 backdrop-blur-lg border border-white/10 hover:border-pink-500/30 transition-all"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-pink-500/20 to-blue-500/20">
                        <BookOpen className="w-6 h-6 text-pink-400" />
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        {isCompleted ? (
                          <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-xs flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" />
                            Completed
                          </span>
                        ) : (
                          <span className="px-2 py-1 rounded-full bg-blue-500/20 text-blue-400 text-xs">
                            In Progress
                          </span>
                        )}
                        {hasTest && (
                          testCompleted ? (
                            <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-xs">
                              Test: {testStatus.score?.toFixed(0)}%
                            </span>
                          ) : testExpired ? (
                            <span className="px-2 py-1 rounded-full bg-red-500/20 text-red-400 text-xs">
                              Test Expired
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded-full bg-orange-500/20 text-orange-400 text-xs">
                              Test Pending
                            </span>
                          )
                        )}
                      </div>
                    </div>

                    <h3 className="text-lg font-bold mb-2">{session.workspace_name}</h3>
                    <div className="space-y-1 text-sm text-gray-400 mb-4">
                      <div className="flex items-center justify-between">
                        <span>Type:</span>
                        <span className="capitalize">{session.session_type}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Duration:</span>
                        <span>{formatTime(session.study_duration_seconds)}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Date:</span>
                        <span>{new Date(session.started_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {!isCompleted && (
                      <button
                        onClick={() => navigate(`/study-session/${session.id}`)}
                        className="w-full py-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg transition-all"
                      >
                        Continue Session
                      </button>
                    )}

                    {isCompleted && hasTest && !testCompleted && !testExpired && (
                      <button
                        onClick={() => navigate(`/test/${session.id}`)}
                        className="w-full py-2 bg-orange-500 hover:bg-orange-600 rounded-lg font-semibold transition-colors"
                      >
                        Take Test
                      </button>
                    )}

                    {testCompleted && (
                      <button
                        onClick={() => navigate(`/test-results/${session.id}`)}
                        className="w-full py-2 bg-white/10 hover:bg-white/20 rounded-lg font-semibold transition-colors"
                      >
                        View Results
                      </button>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid md:grid-cols-4 gap-4">
          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <div className="text-3xl font-bold text-pink-500 mb-2">
              {formatTime(stats.total_study_time || 0)}
            </div>
            <div className="text-sm text-gray-400">Total Study Time</div>
          </div>
          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <div className="text-3xl font-bold text-blue-500 mb-2">
              {stats.sessions_this_week || 0}
            </div>
            <div className="text-sm text-gray-400">Sessions This Week</div>
          </div>
          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <div className="text-3xl font-bold text-green-500 mb-2">
              {completed_tests}
            </div>
            <div className="text-sm text-gray-400">Tests Completed</div>
          </div>
          <div className="p-6 rounded-xl bg-white/5 border border-white/10">
            <div className="text-3xl font-bold text-orange-500 mb-2">
              {weak_points_count}
            </div>
            <div className="text-sm text-gray-400">Areas to Improve</div>
          </div>
        </div>
      </main>
    </div>
  );
}
