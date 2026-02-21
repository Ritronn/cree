import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X, Play, Pause, Coffee, CheckCircle, AlertTriangle,
  Camera, CameraOff, Clock, Eye, EyeOff, MessageSquare,
  Send, Download, Loader2, FileText, Video
} from 'lucide-react';
import {
  topicsAPI, contentAPI, monitoringAPI,
  progressAPI, studySessionAPI, chatAPI, proctoringAPI
} from '../services/api';
import { initializeMonitoring, trackEvent } from '../utils/monitoring';

export default function StudySession() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  // Session state
  const [session, setSession] = useState(null);
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Monitoring state
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [isOnBreak, setIsOnBreak] = useState(false);
  const [breakTimeLeft, setBreakTimeLeft] = useState(0);
  const [sessionTime, setSessionTime] = useState(0);
  const [violations, setViolations] = useState({
    tab_switches: 0,
    copy_attempts: 0,
    focus_lost: 0
  });

  // Chat state
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Whiteboard state
  const whiteboardCanvasRef = useRef(null);
  const isDrawingRef = useRef(false);
  const lastPosRef = useRef({ x: 0, y: 0 });
  const [drawColor, setDrawColor] = useState('#000000');
  const [drawSize, setDrawSize] = useState(2);
  // Store draw settings in refs so event handlers always see the latest
  // values without needing to re-register (which would wipe the canvas).
  const drawColorRef = useRef('#000000');
  const drawSizeRef = useRef(2);

  // Monitoring refs
  const monitoringSessionId = useRef(null);
  const sessionTimer = useRef(null);
  const breakTimer = useRef(null);

  // Camera refs
  const cameraStreamRef = useRef(null);   // holds MediaStream
  const cameraVideoRef = useRef(null);    // holds <video> element

  // Initialize session
  useEffect(() => {
    loadSession();
    return () => {
      if (sessionTimer.current) clearInterval(sessionTimer.current);
      if (breakTimer.current) clearInterval(breakTimer.current);
      // Stop camera stream on unmount
      if (cameraStreamRef.current) {
        cameraStreamRef.current.getTracks().forEach(t => t.stop());
        cameraStreamRef.current = null;
      }
    };
  }, [sessionId]);

  // Initialize monitoring
  useEffect(() => {
    if (session && content) {
      initializeSessionMonitoring();
    }
  }, [session, content]);

  // Session timer
  useEffect(() => {
    if (session && !isOnBreak) {
      sessionTimer.current = setInterval(() => {
        setSessionTime(prev => prev + 1);
      }, 1000);
    } else {
      if (sessionTimer.current) clearInterval(sessionTimer.current);
    }

    return () => {
      if (sessionTimer.current) clearInterval(sessionTimer.current);
    };
  }, [session, isOnBreak]);

  // Break timer
  useEffect(() => {
    if (isOnBreak && breakTimeLeft > 0) {
      breakTimer.current = setInterval(() => {
        setBreakTimeLeft(prev => {
          if (prev <= 1) {
            handleEndBreak();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      if (breakTimer.current) clearInterval(breakTimer.current);
    }

    return () => {
      if (breakTimer.current) clearInterval(breakTimer.current);
    };
  }, [isOnBreak, breakTimeLeft]);

  // Keep draw-setting refs in sync whenever state changes (no effect side-effects)
  useEffect(() => { drawColorRef.current = drawColor; }, [drawColor]);
  useEffect(() => { drawSizeRef.current = drawSize; }, [drawSize]);

  // Initialize whiteboard canvas — runs ONCE on mount only.
  // Using refs for color/size means we never need to re-run this effect,
  // which prevents the canvas from being wiped on every color change.
  useEffect(() => {
    const canvas = whiteboardCanvasRef.current;
    if (!canvas) return;

    const resizeCanvas = () => {
      const parent = canvas.parentElement;
      if (parent) {
        // Preserve existing drawing by copying to a temp canvas before resize
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(canvas, 0, 0);

        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;

        const ctx = canvas.getContext('2d');
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        // Restore previous drawing
        ctx.drawImage(tempCanvas, 0, 0);
      }
    };

    // Initial sizing
    const parent = canvas.parentElement;
    if (parent) {
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
    }

    const ctx = canvas.getContext('2d');
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    window.addEventListener('resize', resizeCanvas);

    const getPos = (e) => {
      const rect = canvas.getBoundingClientRect();
      if (e.touches) {
        return { x: e.touches[0].clientX - rect.left, y: e.touches[0].clientY - rect.top };
      }
      return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };

    const startDraw = (e) => {
      e.preventDefault();
      isDrawingRef.current = true;
      lastPosRef.current = getPos(e);
    };

    const draw = (e) => {
      e.preventDefault();
      if (!isDrawingRef.current) return;
      const pos = getPos(e);
      // Use refs so latest color/size is always used without re-registering events
      ctx.strokeStyle = drawColorRef.current;
      ctx.lineWidth = drawSizeRef.current;
      ctx.beginPath();
      ctx.moveTo(lastPosRef.current.x, lastPosRef.current.y);
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
      lastPosRef.current = pos;
    };

    const endDraw = () => {
      isDrawingRef.current = false;
    };

    canvas.addEventListener('mousedown', startDraw);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', endDraw);
    canvas.addEventListener('mouseleave', endDraw);
    canvas.addEventListener('touchstart', startDraw, { passive: false });
    canvas.addEventListener('touchmove', draw, { passive: false });
    canvas.addEventListener('touchend', endDraw);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousedown', startDraw);
      canvas.removeEventListener('mousemove', draw);
      canvas.removeEventListener('mouseup', endDraw);
      canvas.removeEventListener('mouseleave', endDraw);
      canvas.removeEventListener('touchstart', startDraw);
      canvas.removeEventListener('touchmove', draw);
      canvas.removeEventListener('touchend', endDraw);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // empty deps — runs once only

  const loadSession = async () => {
    try {
      setLoading(true);

      // Fetch real session from backend
      const sessionResponse = await studySessionAPI.get(sessionId);
      const sessionData = sessionResponse.data;
      setSession(sessionData);

      // Load content using the real content ID from the session
      if (sessionData.content) {
        try {
          const contentResponse = await contentAPI.get(sessionData.content);
          setContent(contentResponse.data);
        } catch (contentErr) {
          console.warn('Could not load content details:', contentErr);
          // Session still works without content details
          setContent({ id: sessionData.content, title: sessionData.content_title || 'Study Session' });
        }
      }

      setLoading(false);
    } catch (err) {
      console.error('Failed to load session:', err);
      setError('Failed to load study session');
      setLoading(false);
    }
  };

  const initializeSessionMonitoring = async () => {
    try {
      const response = await monitoringAPI.startSession(content.id);
      monitoringSessionId.current = response.data.id;

      // Initialize client-side monitoring with a proper callback function.
      // IMPORTANT: Do NOT call trackEvent() inside this callback — trackEvent()
      // calls emitEvent() which calls this callback, creating an infinite loop.
      // Only update React state and POST to backend API here.
      initializeMonitoring(monitoringSessionId.current, async (eventType, _data) => {
        switch (eventType) {
          case 'tab_switch':
            setViolations(prev => ({ ...prev, tab_switches: prev.tab_switches + 1 }));
            // Persist to backend so it's saved in the database
            try {
              await proctoringAPI.recordEvent(sessionId, 'tab_switch');
            } catch { }
            break;
          case 'focus_lost':
            setViolations(prev => ({ ...prev, focus_lost: prev.focus_lost + 1 }));
            // Persist to backend
            try {
              await proctoringAPI.recordEvent(sessionId, 'focus_lost');
            } catch { }
            break;
          case 'focus_gained':
            try {
              await proctoringAPI.recordEvent(sessionId, 'focus_gained');
            } catch { }
            break;
          case 'time_update':
            // Time updates handled silently
            break;
          default:
            break;
        }
      });
    } catch (err) {
      console.error('Failed to initialize monitoring:', err);
    }
  };

  const handleToggleCamera = async () => {
    if (cameraEnabled) {
      // Turn OFF — stop all tracks
      if (cameraStreamRef.current) {
        cameraStreamRef.current.getTracks().forEach(t => t.stop());
        cameraStreamRef.current = null;
      }
      if (cameraVideoRef.current) {
        cameraVideoRef.current.srcObject = null;
      }
      setCameraEnabled(false);
      try { await studySessionAPI.updateCamera(sessionId, false); } catch { }
    } else {
      // Turn ON — request webcam
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        cameraStreamRef.current = stream;
        if (cameraVideoRef.current) {
          cameraVideoRef.current.srcObject = stream;
        }
        setCameraEnabled(true);
        try { await studySessionAPI.updateCamera(sessionId, true); } catch { }
        trackEvent('camera_toggle', { enabled: true, sessionId: monitoringSessionId.current });
      } catch (err) {
        console.error('Camera access denied or unavailable:', err);
        alert('Camera access was denied. Please allow camera permissions in your browser and try again.');
      }
    }
  };

  const handleStartBreak = async () => {
    try {
      const response = await studySessionAPI.startBreak(sessionId);
      const data = response.data;

      setIsOnBreak(true);
      setBreakTimeLeft(data.break_duration_seconds || 300); // 5 minutes default

      trackEvent('break_started', { sessionId: monitoringSessionId.current });
    } catch (err) {
      console.error('Failed to start break:', err);
    }
  };

  const handleEndBreak = async () => {
    try {
      await studySessionAPI.endBreak(sessionId);

      setIsOnBreak(false);
      setBreakTimeLeft(0);

      trackEvent('break_ended', { sessionId: monitoringSessionId.current });
    } catch (err) {
      console.error('Failed to end break:', err);
    }
  };

  const handleCompleteSession = async () => {
    try {
      // End monitoring session
      if (monitoringSessionId.current) {
        await monitoringAPI.endSession(monitoringSessionId.current);
      }

      // Complete study session using proper API service
      const response = await studySessionAPI.complete(sessionId);
      const data = response.data;

      // Test is generated in background — always go to dashboard
      // The user will see their test available on the dashboard in ~1–2 minutes
      navigate('/dashboard', {
        state: {
          message: data.message || 'Session complete! Your test will be ready on the dashboard shortly.',
          testGenerating: true
        }
      });
    } catch (err) {
      console.error('Failed to complete session:', err);
      setError('Failed to complete session');
    }
  };


  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: chatInput,
      sender: 'user',
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    const savedInput = chatInput;
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await chatAPI.sendQuery(sessionId, savedInput, content?.title);
      const data = response.data;

      const aiMessage = {
        id: Date.now() + 1,
        text: data.response || 'Sorry, I could not process your question.',
        sender: 'ai',
        timestamp: new Date()
      };

      setChatMessages(prev => [...prev, aiMessage]);

      trackEvent('chat_query', { query: savedInput, sessionId: monitoringSessionId.current });
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, there was an error processing your question.',
        sender: 'ai',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-pink-500 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <p className="text-white text-xl mb-4">{error}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-2 bg-pink-500 rounded-lg hover:bg-pink-600 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-full px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold">{content?.title || 'Study Session'}</h1>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/10">
              <Clock className="w-4 h-4" />
              <span className="text-sm font-mono">{formatTime(sessionTime)}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Camera Preview (live feed when enabled) */}
            {cameraEnabled && (
              <div className="relative w-20 h-14 rounded-lg overflow-hidden border border-green-500/40 bg-black">
                <video
                  ref={cameraVideoRef}
                  autoPlay
                  muted
                  playsInline
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-0.5 right-1 text-xs text-green-400 font-bold">● REC</div>
              </div>
            )}

            {/* Camera Toggle */}
            <button
              onClick={handleToggleCamera}
              className={`p-2 rounded-lg transition-colors ${cameraEnabled ? 'bg-green-500/20 text-green-400' : 'bg-white/10'
                }`}
              title={cameraEnabled ? 'Camera On (click to turn off)' : 'Camera Off (click to enable)'}
            >
              {cameraEnabled ? <Camera className="w-5 h-5" /> : <CameraOff className="w-5 h-5" />}
            </button>

            {/* Break Button */}
            {!isOnBreak ? (
              <button
                onClick={handleStartBreak}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
              >
                <Coffee className="w-5 h-5" />
                <span>Break</span>
              </button>
            ) : (
              <div className="flex items-center gap-2 px-4 py-2 bg-orange-500/20 rounded-lg">
                <Coffee className="w-5 h-5 text-orange-400" />
                <span className="text-orange-400">{formatTime(breakTimeLeft)}</span>
              </div>
            )}

            {/* Complete Button */}
            <button
              onClick={handleCompleteSession}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg hover:shadow-lg transition-all"
            >
              <CheckCircle className="w-5 h-5" />
              <span>Complete</span>
            </button>

            {/* Close Button */}
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Violations Bar */}
        {(violations.tab_switches > 0 || violations.copy_attempts > 0 || violations.focus_lost > 0) && (
          <div className="px-6 py-2 bg-red-500/10 border-t border-red-500/20 flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span className="text-red-400">Proctoring Alerts:</span>
            </div>
            {violations.tab_switches > 0 && (
              <span className="text-gray-300">Tab Switches: {violations.tab_switches}</span>
            )}
            {violations.copy_attempts > 0 && (
              <span className="text-gray-300">Copy Attempts: {violations.copy_attempts}</span>
            )}
            {violations.focus_lost > 0 && (
              <span className="text-gray-300">Focus Lost: {violations.focus_lost}</span>
            )}
          </div>
        )}
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Left: Content Viewer */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            {content?.content_type === 'youtube' && (() => {
              // Convert any YouTube URL format to the embeddable embed URL.
              // Regular watch URLs (youtube.com/watch?v=ID) and share URLs
              // (youtu.be/ID) both block in iframes via X-Frame-Options.
              // Only youtube.com/embed/ID is allowed.
              const getEmbedUrl = (url) => {
                if (!url) return '';
                try {
                  // Already an embed URL
                  if (url.includes('youtube.com/embed/')) return url;

                  // youtu.be/ID short link
                  const shortMatch = url.match(/youtu\.be\/([^?&]+)/);
                  if (shortMatch) return `https://www.youtube.com/embed/${shortMatch[1]}`;

                  // youtube.com/watch?v=ID
                  const watchMatch = url.match(/[?&]v=([^&]+)/);
                  if (watchMatch) return `https://www.youtube.com/embed/${watchMatch[1]}`;

                  // Fallback: return as-is
                  return url;
                } catch {
                  return url;
                }
              };
              const embedUrl = getEmbedUrl(content.url);
              return (
                <div className="aspect-video bg-black rounded-xl overflow-hidden mb-6">
                  <iframe
                    src={embedUrl}
                    className="w-full h-full"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    title="YouTube video player"
                  />
                </div>
              );
            })()}

            {content?.content_type === 'pdf' && content?.file && (
              <div className="rounded-xl overflow-hidden border border-white/10" style={{ height: '75vh' }}>
                <object
                  data={content.file.startsWith('http') ? content.file : `http://localhost:8000${content.file}`}
                  type="application/pdf"
                  className="w-full h-full"
                  title="PDF Viewer"
                >
                  <div className="flex flex-col items-center justify-center h-full bg-white/5 p-8">
                    <FileText className="w-16 h-16 text-blue-400 mb-4" />
                    <p className="text-gray-300 mb-4">Unable to display PDF inline</p>
                    <a
                      href={content.file.startsWith('http') ? content.file : `http://localhost:8000${content.file}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-6 py-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg hover:shadow-lg transition-all text-white"
                    >
                      Open PDF in new tab
                    </a>
                  </div>
                </object>
              </div>
            )}

            {content?.content_type === 'pdf' && !content?.file && (
              <div className="bg-white/5 rounded-xl p-6 text-center">
                <FileText className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                <p className="text-gray-400">PDF file not available</p>
              </div>
            )}

            {isOnBreak && (
              <div className="mt-6 p-8 bg-orange-500/10 border border-orange-500/30 rounded-xl text-center">
                <Coffee className="w-16 h-16 text-orange-400 mx-auto mb-4" />
                <h3 className="text-2xl font-bold mb-2">Break Time</h3>
                <p className="text-gray-300 mb-4">Take a rest. You'll be back in {formatTime(breakTimeLeft)}</p>
                <button
                  onClick={handleEndBreak}
                  className="px-6 py-2 bg-orange-500 rounded-lg hover:bg-orange-600 transition-colors"
                >
                  End Break Early
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Right: Whiteboard & Chat */}
        <div className="w-96 border-l border-white/10 flex flex-col">
          {/* Whiteboard */}
          <div className="h-1/2 border-b border-white/10 flex flex-col">
            <div className="p-3 border-b border-white/10 bg-black/20 flex items-center justify-between">
              <h3 className="font-semibold text-sm">Whiteboard</h3>
              <div className="flex items-center gap-2">
                {['#000000', '#ef4444', '#3b82f6', '#22c55e', '#eab308'].map(color => (
                  <button
                    key={color}
                    onClick={() => setDrawColor(color)}
                    className={`w-5 h-5 rounded-full border-2 transition-transform ${drawColor === color ? 'border-white scale-125' : 'border-transparent'
                      }`}
                    style={{ backgroundColor: color }}
                  />
                ))}
                <button
                  onClick={() => {
                    const canvas = whiteboardCanvasRef.current;
                    if (canvas) {
                      const ctx = canvas.getContext('2d');
                      ctx.fillStyle = '#ffffff';
                      ctx.fillRect(0, 0, canvas.width, canvas.height);
                    }
                  }}
                  className="text-xs px-2 py-1 bg-white/10 rounded hover:bg-white/20 transition-colors"
                >
                  Clear
                </button>
              </div>
            </div>
            <div className="flex-1 relative">
              <canvas
                ref={whiteboardCanvasRef}
                className="absolute inset-0 cursor-crosshair"
                style={{ background: '#ffffff' }}
              />
            </div>
          </div>

          {/* Chat */}
          <div className="h-1/2 flex flex-col bg-black/20">
            <div className="p-4 border-b border-white/10">
              <h3 className="font-semibold flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                AI Assistant
              </h3>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-8">
                  Ask questions about the content
                </p>
              ) : (
                chatMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] px-4 py-2 rounded-lg ${msg.sender === 'user'
                        ? 'bg-gradient-to-r from-pink-500 to-blue-500'
                        : 'bg-white/10'
                        }`}
                    >
                      <p className="text-sm">{msg.text}</p>
                    </div>
                  </div>
                ))
              )}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 px-4 py-2 rounded-lg">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-white/10">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask a question..."
                  className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-pink-500/50 focus:outline-none text-sm"
                  disabled={chatLoading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={chatLoading || !chatInput.trim()}
                  className="p-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
