import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, Coffee, Zap, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { studySessionAPI, dashboardAPI } from '../services/api';

export default function CreateSession() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [canCreate, setCanCreate] = useState(true);
  const [blockedReason, setBlockedReason] = useState('');
  const [workspaceName, setWorkspaceName] = useState('');
  const [sessionType, setSessionType] = useState('recommended');
  const [error, setError] = useState('');

  useEffect(() => {
    checkSessionLimit();
  }, []);

  const checkSessionLimit = async () => {
    try {
      const response = await dashboardAPI.getOverview();
      const { session_limit } = response.data;

      setCanCreate(session_limit.can_create);
      setBlockedReason(session_limit.blocked_reason || '');
    } catch (err) {
      console.error('Failed to check session limit:', err);
    }
  };

  const handleCreateSession = async () => {
    if (!workspaceName.trim()) {
      setError('Please enter a workspace name');
      return;
    }

    try {
      setLoading(true);
      setError('');

      // Create study session without content (content will be added in the session window)
      const sessionResponse = await studySessionAPI.create({
        session_type: sessionType,
        workspace_name: workspaceName,
      });

      // Navigate to study session window
      // Backend returns { session: {...}, proctoring_config: {...}, session_limit: {...} }
      const session = sessionResponse.data.session || sessionResponse.data;
      if (session && session.id) {
        navigate(`/study-session/${session.id}`);
      }
    } catch (err) {
      console.error('Failed to create session:', err);
      setError(err.response?.data?.error || 'Failed to create session');
    } finally {
      setLoading(false);
    }
  };

  const sessionPresets = [
    {
      type: 'recommended',
      name: 'Recommended',
      duration: '2 hours',
      break: '20 minutes',
      icon: Zap,
      color: 'from-pink-500 to-purple-500',
      description: 'Deep focus session with extended break'
    },
    {
      type: 'standard',
      name: 'Standard',
      duration: '50 minutes',
      break: '10 minutes',
      icon: Clock,
      color: 'from-blue-500 to-cyan-500',
      description: 'Pomodoro-style focused session'
    },
    {
      type: 'custom',
      name: 'Custom',
      duration: 'Your choice',
      break: 'Your choice',
      icon: Coffee,
      color: 'from-orange-500 to-yellow-500',
      description: 'Set your own duration and breaks'
    }
  ];

  if (!canCreate) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
        <header className="border-b border-white/10 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-bold">Create Study Session</h1>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-6 py-12">
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8 text-center">
            <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Cannot Create Session</h2>
            <p className="text-gray-400 mb-6">{blockedReason}</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-lg font-semibold transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-xl font-bold">Create Study Session</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="space-y-8">
          {/* Workspace Name */}
          <div>
            <label className="block text-sm font-medium mb-3">
              Workspace Name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={workspaceName}
              onChange={(e) => setWorkspaceName(e.target.value)}
              placeholder="e.g., Python Data Structures Study"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-pink-500/50 focus:outline-none transition-colors text-white placeholder-gray-500"
            />
          </div>

          {/* Session Type */}
          <div>
            <label className="block text-sm font-medium mb-3">
              Session Type <span className="text-red-400">*</span>
            </label>
            <div className="grid md:grid-cols-3 gap-4">
              {sessionPresets.map((preset) => {
                const Icon = preset.icon;
                const isSelected = sessionType === preset.type;

                return (
                  <motion.button
                    key={preset.type}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSessionType(preset.type)}
                    className={`p-6 rounded-xl border-2 transition-all text-left ${isSelected
                        ? 'border-pink-500 bg-pink-500/10'
                        : 'border-white/10 bg-white/5 hover:border-white/20'
                      }`}
                  >
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${preset.color} flex items-center justify-center mb-4`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="font-bold mb-1">{preset.name}</h3>
                    <div className="text-sm text-gray-400 mb-2">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        <span>{preset.duration}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Coffee className="w-4 h-4" />
                        <span>{preset.break} break</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500">{preset.description}</p>
                  </motion.button>
                );
              })}
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <p className="text-blue-400 text-sm">
              You can add study materials (PDFs, PPTs, Word docs, YouTube videos) after creating the session.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* Create Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleCreateSession}
            disabled={loading || !workspaceName.trim()}
            className="w-full py-4 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-pink-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Session...' : 'Start Study Session'}
          </motion.button>
        </div>
      </main>
    </div>
  );
}
