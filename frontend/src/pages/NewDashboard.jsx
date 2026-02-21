import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, BookOpen, Clock, AlertTriangle, CheckCircle, XCircle, Zap, LogOut, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import { dashboardAPI, authenticationAPI } from '../services/api';

export default function NewDashboard() {
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

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getTimeRemaining = (expiresAt) => {
    if (!expiresAt) return 'N/A';
    const now = new Date();
    const expiry = new Date(expiresAt);
    const diff = expiry - now;

    if (diff < 0) return 'Expired';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    return `${hours}h ${minutes}m`;
  };

  const handleLogout = async () => {
    try {
      await authenticationAPI.signout();
      navigate('/signin');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center">
        <div className="text-white text-xl">Loading dashboard...</div>
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

  const { completion_percentage, weekly_sessions, session_limit, weak_points_count, stats } = dashboardData || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50 bg-slate-950/50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-pink-500" />
            <h1 className="text-2xl font-bold">Study Dashboard</h1>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Completion Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-pink-500/10 to-blue-500/10 border border-white/10 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Overall Completion</h2>
            <span className="text-3xl font-bold text-pink-500">{completion_percentage}%</span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-4 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${completion_percentage}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="h-full bg-gradient-to-r from-pink-500 to-blue-500 rounded-full"
            />
          </div>
          <p className="text-sm text-gray-400 mt-2">
            {dashboardData?.completed_tests} of {dashboardData?.total_sessions} tests completed
          </p>
        </motion.div>

        {/* Session Limit Warning */}
        {!session_limit?.can_create && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3"
          >
            <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0" />
            <div>
              <p className="font-semibold text-red-400">Cannot Create New Session</p>
              <p className="text-sm text-gray-400">{session_limit?.blocked_reason}</p>
            </div>
          </motion.div>
        )}

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/5 border border-white/10 rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="w-5 h-5 text-blue-400" />
              <span className="text-sm text-gray-400">Sessions Today</span>
            </div>
            <p className="text-3xl font-bold">{session_limit?.sessions_today}/{session_limit?.max_sessions}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/5 border border-white/10 rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-green-400" />
              <span className="text-sm text-gray-400">Study Time</span>
            </div>
            <p className="text-3xl font-bold">{formatTime(stats?.total_study_time || 0)}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white/5 border border-white/10 rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
              <span className="text-sm text-gray-400">Pending Tests</span>
            </div>
            <p className="text-3xl font-bold">{dashboardData?.pending_tests || 0}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white/5 border border-white/10 rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <Zap className="w-5 h-5 text-red-400" />
              <span className="text-sm text-gray-400">Weak Points</span>
            </div>
            <p className="text-3xl font-bold">{weak_points_count || 0}</p>
          </motion.div>
        </div>

        {/* Create Session Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => navigate('/create-session')}
          disabled={!session_limit?.can_create}
          className="w-full py-4 bg-gradient-to-r from-pink-500 to-blue-500 rounded-xl font-semibold text-lg hover:shadow-lg hover:shadow-pink-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          <Plus className="w-6 h-6" />
          Create New Study Session
        </motion.button>

        {/* Weekly Sessions */}
        <div>
          <h2 className="text-2xl font-bold mb-4">This Week's Sessions</h2>
          {weekly_sessions && weekly_sessions.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {weekly_sessions.map((session, index) => (
                <motion.div
                  key={session.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-pink-500/50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-lg mb-1">{session.workspace_name}</h3>
                      <p className="text-sm text-gray-400">
                        {new Date(session.started_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    {session.test_status.completed ? (
                      <CheckCircle className="w-6 h-6 text-green-400" />
                    ) : session.test_status.expired ? (
                      <XCircle className="w-6 h-6 text-red-400" />
                    ) : (
                      <Clock className="w-6 h-6 text-yellow-400" />
                    )}
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Duration:</span>
                      <span className="font-semibold">{formatTime(session.study_duration_seconds)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Type:</span>
                      <span className="font-semibold capitalize">{session.session_type}</span>
                    </div>
                    {session.test_status.exists && (
                      <>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Test Status:</span>
                          <span className={`font-semibold ${session.test_status.completed ? 'text-green-400' :
                              session.test_status.expired ? 'text-red-400' : 'text-yellow-400'
                            }`}>
                            {session.test_status.completed ? 'Completed' :
                              session.test_status.expired ? 'Expired' : 'Pending'}
                          </span>
                        </div>
                        {session.test_status.completed && session.test_status.score !== null && (
                          <div className="flex items-center justify-between">
                            <span className="text-gray-400">Score:</span>
                            <span className="font-semibold text-pink-400">{session.test_status.score}%</span>
                          </div>
                        )}
                        {!session.test_status.completed && !session.test_status.expired && (
                          <div className="flex items-center justify-between">
                            <span className="text-gray-400">Expires in:</span>
                            <span className="font-semibold text-yellow-400">
                              {getTimeRemaining(session.test_status.expires_at)}
                            </span>
                          </div>
                        )}
                      </>
                    )}
                  </div>

                  {session.test_status.exists && !session.test_status.completed && !session.test_status.expired && (
                    <button
                      onClick={() => navigate(`/test/${session.test_status.test_id}`)}
                      className="w-full mt-4 py-2 bg-pink-500/20 hover:bg-pink-500/30 text-pink-400 rounded-lg font-semibold transition-colors"
                    >
                      Take Test
                    </button>
                  )}
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="bg-white/5 border border-white/10 rounded-xl p-12 text-center">
              <BookOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No study sessions this week</p>
              <p className="text-gray-500 text-sm mt-2">Create your first session to get started!</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
