import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, Clock, Coffee, Zap, AlertCircle, FileText, File, Youtube, Link } from 'lucide-react';
import { motion } from 'framer-motion';
import { createStudySession, contentAPI, dashboardAPI } from '../services/api';

export default function CreateSession() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [canCreate, setCanCreate] = useState(true);
  const [blockedReason, setBlockedReason] = useState('');
  const [workspaceName, setWorkspaceName] = useState('');
  const [sessionType, setSessionType] = useState('recommended');
  const [contentSource, setContentSource] = useState('file'); // 'file' or 'youtube'
  const [file, setFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
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

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check file type
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint'
      ];

      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF, DOCX, or PPT file');
        return;
      }

      // Check file size (max 50MB)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB');
        return;
      }

      setFile(selectedFile);
      setError('');
    }
  };

  const isValidYoutubeUrl = (url) => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/,
      /youtube\.com\/playlist\?list=[\w-]+/,
      /youtube\.com\/.*[?&]list=[\w-]+/,
    ];
    return patterns.some(p => p.test(url));
  };

  const handleCreateSession = async () => {
    if (!workspaceName.trim()) {
      setError('Please enter a workspace name');
      return;
    }

    if (contentSource === 'file' && !file) {
      setError('Please upload a file');
      return;
    }

    if (contentSource === 'youtube' && !youtubeUrl.trim()) {
      setError('Please enter a YouTube URL');
      return;
    }

    if (contentSource === 'youtube' && !isValidYoutubeUrl(youtubeUrl)) {
      setError('Please enter a valid YouTube video or playlist URL');
      return;
    }

    try {
      setLoading(true);
      setError('');

      // Build form data based on content source
      const formData = new FormData();
      formData.append('title', workspaceName);

      if (contentSource === 'youtube') {
        formData.append('content_type', 'youtube');
        formData.append('url', youtubeUrl);
      } else {
        // Determine content type from file
        let contentType = 'pdf';
        if (file.type.includes('word')) contentType = 'word';
        if (file.type.includes('presentation')) contentType = 'ppt';

        formData.append('content_type', contentType);
        formData.append('file', file);
      }

      // Upload content
      const contentResponse = await contentAPI.upload(formData);
      const contentId = contentResponse.data.id;

      // Create study session
      const sessionResponse = await createStudySession(
        contentId,
        sessionType,
        workspaceName
      );

      // Navigate to study session
      if (sessionResponse.session) {
        navigate(`/session/${sessionResponse.session.id}`);
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

          {/* Content Source Toggle */}
          <div>
            <label className="block text-sm font-medium mb-3">
              Upload Study Material <span className="text-red-400">*</span>
            </label>

            {/* Source Toggle Tabs */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => { setContentSource('file'); setError(''); }}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-all ${contentSource === 'file'
                    ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg shadow-pink-500/30'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                  }`}
              >
                <Upload className="w-4 h-4" />
                File Upload
              </button>
              <button
                onClick={() => { setContentSource('youtube'); setError(''); }}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-all ${contentSource === 'youtube'
                    ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-lg shadow-red-500/30'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                  }`}
              >
                <Youtube className="w-4 h-4" />
                YouTube URL
              </button>
            </div>

            {/* File Upload Panel */}
            {contentSource === 'file' && (
              <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-pink-500/50 transition-colors">
                {!file ? (
                  <>
                    <Upload className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400 mb-2">
                      Drag and drop your file here, or click to browse
                    </p>
                    <p className="text-sm text-gray-500 mb-4">
                      Supported formats: PDF, DOCX, PPT (Max 50MB)
                    </p>
                    <input
                      type="file"
                      onChange={handleFileChange}
                      accept=".pdf,.doc,.docx,.ppt,.pptx"
                      className="hidden"
                      id="file-upload"
                    />
                    <label
                      htmlFor="file-upload"
                      className="inline-block px-6 py-2 bg-white/10 hover:bg-white/20 rounded-lg cursor-pointer transition-colors"
                    >
                      Choose File
                    </label>
                  </>
                ) : (
                  <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      {file.type.includes('pdf') ? (
                        <FileText className="w-8 h-8 text-red-400" />
                      ) : (
                        <File className="w-8 h-8 text-blue-400" />
                      )}
                      <div className="text-left">
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-gray-400">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => setFile(null)}
                      className="px-4 py-2 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-lg transition-colors"
                    >
                      Remove
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* YouTube URL Panel */}
            {contentSource === 'youtube' && (
              <div className="border-2 border-dashed border-white/20 rounded-xl p-8 hover:border-red-500/50 transition-colors">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
                    <Youtube className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="font-medium">Paste a YouTube video or playlist URL</p>
                    <p className="text-sm text-gray-500">
                      Transcripts will be extracted automatically
                    </p>
                  </div>
                </div>
                <div className="relative">
                  <Link className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="url"
                    value={youtubeUrl}
                    onChange={(e) => { setYoutubeUrl(e.target.value); setError(''); }}
                    placeholder="https://www.youtube.com/watch?v=... or playlist URL"
                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-red-500/50 focus:outline-none transition-colors text-white placeholder-gray-500"
                  />
                </div>
                {youtubeUrl && isValidYoutubeUrl(youtubeUrl) && (
                  <div className="mt-3 flex items-center gap-2 text-green-400 text-sm">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Valid YouTube URL detected
                  </div>
                )}
                <div className="mt-4 p-3 bg-white/5 rounded-lg">
                  <p className="text-xs text-gray-400">
                    <span className="font-semibold text-gray-300">Supported formats:</span>
                  </p>
                  <ul className="text-xs text-gray-500 mt-1 space-y-1">
                    <li>• Single video: youtube.com/watch?v=...</li>
                    <li>• Playlist: youtube.com/playlist?list=...</li>
                    <li>• Video from playlist: youtube.com/watch?v=...&list=...</li>
                  </ul>
                </div>
              </div>
            )}
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
            disabled={loading || !workspaceName.trim() || (contentSource === 'file' && !file) || (contentSource === 'youtube' && !youtubeUrl.trim())}
            className="w-full py-4 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-pink-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Session...' : 'Start Study Session'}
          </motion.button>
        </div>
      </main>
    </div>
  );
}
