import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clock, AlertTriangle, Camera, CameraOff, CheckCircle, X, TrendingUp, TrendingDown, Target, Award, BookOpen, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { testAPI } from '../services/api';

export default function TestWindow() {
    const { testId } = useParams();
    const navigate = useNavigate();

    const [test, setTest] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [timeRemaining, setTimeRemaining] = useState(0);
    const [testResult, setTestResult] = useState(null);  // null = in-progress, object = results screen
    const [questionStartTime, setQuestionStartTime] = useState(Date.now());

    const [cameraEnabled, setCameraEnabled] = useState(false);
    const [cameraError, setCameraError] = useState('');
    const videoRef = useRef(null);
    const streamRef = useRef(null);
    const timerRef = useRef(null);

    useEffect(() => {
        loadTest();
        return () => {
            if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, [testId]);

    useEffect(() => {
        if (test && !test.started_at) startTest();
    }, [test]);

    useEffect(() => {
        if (timerRef.current) clearInterval(timerRef.current);
        if (timeRemaining > 0 && !testResult) {
            timerRef.current = setInterval(() => {
                setTimeRemaining(prev => {
                    if (prev <= 1) {
                        // Auto-submit on timer end
                        handleSubmitTest(true);
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
        }
        return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, [timeRemaining, testResult]);

    const loadTest = async () => {
        try {
            setLoading(true);
            const response = await testAPI.get(testId);
            const testData = response.data;
            setTest(testData);
            setQuestions(testData.questions || []);
            if (testData.started_at) {
                const elapsed = Math.floor((Date.now() - new Date(testData.started_at).getTime()) / 1000);
                setTimeRemaining(Math.max(0, testData.time_limit_seconds - elapsed));
            } else {
                setTimeRemaining(testData.time_limit_seconds);
            }
            await initCamera();
        } catch (err) {
            setError(err.response?.status === 404 ? 'Test not found or expired.' : 'Failed to load test.');
        } finally {
            setLoading(false);
        }
    };

    const startTest = async () => {
        try { await testAPI.start(testId); } catch { /* already started is fine */ }
    };

    const initCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 } });
            streamRef.current = stream;
            if (videoRef.current) videoRef.current.srcObject = stream;
            setCameraEnabled(true);
        } catch {
            setCameraError('Camera access denied.');
            setCameraEnabled(false);
        }
    };

    const handleAnswerChange = (questionId, value) => {
        setAnswers(prev => ({ ...prev, [questionId]: value }));
    };

    const handleSubmitTest = async (autoSubmit = false) => {
        if (submitting) return;
        if (!autoSubmit) {
            const answeredCount = Object.keys(answers).filter(id => answers[id] !== undefined && answers[id] !== '').length;
            const unanswered = questions.length - answeredCount;
            const msg = unanswered > 0
                ? `You have ${unanswered} unanswered question${unanswered > 1 ? 's' : ''}. Unanswered questions score 0. Submit anyway?`
                : 'Submit the test? This cannot be undone.';
            if (!window.confirm(msg)) return;
        }

        try {
            setSubmitting(true);
            if (timerRef.current) clearInterval(timerRef.current);

            // Submit only the answered questions
            for (const question of questions) {
                const answer = answers[question.id];
                if (answer !== undefined && answer !== '') {
                    await testAPI.submitAnswer(testId, {
                        question_id: question.id,
                        answer_text: answer.toString(),
                        selected_index: question.question_type === 'mcq' ? parseInt(answer) : null,
                        time_taken_seconds: 60
                    });
                }
            }

            // Complete test and get results
            const response = await testAPI.complete(testId);
            const result = response.data;
            setTestResult(result);

            // Stop camera
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(t => t.stop());
                setCameraEnabled(false);
            }
        } catch (err) {
            console.error('Submit failed:', err);
            alert('Failed to submit test. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${s.toString().padStart(2, '0')}`;
    };

    const isAnswered = (questionId) => answers[questionId] !== undefined && answers[questionId] !== '';

    const answeredCount = Object.keys(answers).filter(id => isAnswered(id)).length;

    // ─── LOADING / ERROR ─────────────────────────────────────────────────────
    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center text-white">
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                    className="w-12 h-12 border-3 border-pink-500 border-t-transparent rounded-full" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center text-white">
                <div className="text-center">
                    <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <p className="text-xl font-semibold mb-2">Test Error</p>
                    <p className="text-gray-400 mb-6">{error}</p>
                    <button onClick={() => navigate('/dashboard')} className="px-6 py-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg">
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    // ─── RESULTS SCREEN ───────────────────────────────────────────────────────
    if (testResult) {
        const score = testResult.overall_score ?? 0;
        const total = testResult.total_questions ?? questions.length;
        const answered = testResult.answered_questions ?? answeredCount;
        const correct = testResult.correct_answers ?? 0;
        const unanswered = total - answered;
        const wrong = answered - correct;

        const scoreColor = score >= 80 ? '#22c55e' : score >= 60 ? '#f59e0b' : score >= 40 ? '#f97316' : '#ef4444';
        const scoreLabel = score >= 80 ? 'Excellent! 🎉' : score >= 60 ? 'Good Work! 👍' : score >= 40 ? 'Keep Practicing 📚' : 'Needs Improvement 💪';

        // Check if each MCQ answer was correct (for review)
        const answeredQuestions = questions.filter(q => isAnswered(q.id));

        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
                {/* Header */}
                <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-10">
                    <div className="flex items-center gap-3">
                        <CheckCircle className="w-6 h-6 text-green-400" />
                        <h1 className="text-xl font-bold">Test Results</h1>
                    </div>
                    <button onClick={() => navigate('/dashboard')}
                        className="px-5 py-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold text-sm hover:shadow-lg hover:shadow-pink-500/30 transition-all">
                        Go to Dashboard
                    </button>
                </header>

                <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">

                    {/* Score Hero */}
                    <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                        className="text-center p-10 rounded-3xl border border-white/10 bg-white/5 backdrop-blur relative overflow-hidden">
                        <div className="absolute inset-0 opacity-5" style={{ background: `radial-gradient(circle at 50% 50%, ${scoreColor}, transparent 70%)` }} />
                        <div className="relative">
                            <div className="text-8xl font-black mb-2" style={{ color: scoreColor }}>
                                {score.toFixed(1)}%
                            </div>
                            <div className="text-2xl font-bold text-white mb-1">{scoreLabel}</div>
                            <div className="text-gray-400 text-sm">
                                {testResult.time_taken_seconds > 0 ? `Completed in ${Math.floor(testResult.time_taken_seconds / 60)}m ${testResult.time_taken_seconds % 60}s` : 'Test Completed'}
                            </div>
                        </div>
                    </motion.div>

                    {/* Score Breakdown Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { icon: <CheckCircle className="w-5 h-5" />, label: 'Correct', value: correct, color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/20' },
                            { icon: <X className="w-5 h-5" />, label: 'Wrong', value: wrong, color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
                            { icon: <AlertTriangle className="w-5 h-5" />, label: 'Skipped', value: unanswered, color: 'text-yellow-400', bg: 'bg-yellow-500/10 border-yellow-500/20' },
                            { icon: <Target className="w-5 h-5" />, label: 'Total', value: total, color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
                        ].map((item, i) => (
                            <motion.div key={i} initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 * i }}
                                className={`p-5 rounded-2xl border ${item.bg} text-center`}>
                                <div className={`${item.color} flex justify-center mb-2`}>{item.icon}</div>
                                <div className={`text-3xl font-bold ${item.color}`}>{item.value}</div>
                                <div className="text-xs text-gray-400 mt-1">{item.label}</div>
                            </motion.div>
                        ))}
                    </div>

                    {/* Score by Type */}
                    {(testResult.mcq_score !== undefined || testResult.short_answer_score !== undefined) && (
                        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }}
                            className="p-6 rounded-2xl border border-white/10 bg-white/5">
                            <h3 className="font-bold mb-4 flex items-center gap-2">
                                <Zap className="w-5 h-5 text-yellow-400" /> Score by Question Type
                            </h3>
                            <div className="space-y-4">
                                {[
                                    { label: 'Multiple Choice (MCQ)', score: testResult.mcq_score, icon: '🔘' },
                                    { label: 'Short Answer', score: testResult.short_answer_score, icon: '✍️' },
                                    { label: 'Problem Solving', score: testResult.problem_solving_score, icon: '🧩' },
                                ].map(({ label, score: s, icon }) => (
                                    <div key={label}>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-300">{icon} {label}</span>
                                            <span className="font-semibold">{(s ?? 0).toFixed(1)}%</span>
                                        </div>
                                        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                            <motion.div initial={{ width: 0 }} animate={{ width: `${s ?? 0}%` }} transition={{ duration: 1, ease: 'easeOut' }}
                                                className="h-full rounded-full"
                                                style={{ background: (s ?? 0) >= 70 ? '#22c55e' : (s ?? 0) >= 50 ? '#f59e0b' : '#ef4444' }} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* Weak Topics */}
                    {testResult.weak_topics && testResult.weak_topics.length > 0 && (
                        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.4 }}
                            className="p-6 rounded-2xl border border-orange-500/20 bg-orange-500/5">
                            <h3 className="font-bold mb-4 flex items-center gap-2 text-orange-400">
                                <TrendingDown className="w-5 h-5" /> Topics to Improve
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {testResult.weak_topics.map((topic, i) => (
                                    <span key={i} className="px-3 py-1 bg-orange-500/20 border border-orange-500/30 rounded-full text-sm text-orange-300">
                                        {topic.name || topic} ({(topic.accuracy ?? 0).toFixed(0)}%)
                                    </span>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* Next Difficulty */}
                    {testResult.difficulty_feedback && (
                        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.5 }}
                            className="p-6 rounded-2xl border border-blue-500/20 bg-blue-500/5">
                            <h3 className="font-bold mb-2 flex items-center gap-2 text-blue-400">
                                <TrendingUp className="w-5 h-5" /> Next Session Recommendation
                            </h3>
                            <p className="text-gray-300 text-sm">{testResult.difficulty_feedback}</p>
                        </motion.div>
                    )}

                    {/* MCQ Answer Review */}
                    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.6 }}
                        className="p-6 rounded-2xl border border-white/10 bg-white/5">
                        <h3 className="font-bold mb-4 flex items-center gap-2">
                            <BookOpen className="w-5 h-5 text-purple-400" /> Answer Review
                        </h3>
                        <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                            {questions.map((q, i) => {
                                const userAnswer = answers[q.id];
                                const answered = userAnswer !== undefined && userAnswer !== '';
                                let isCorrectAnswer = false;
                                if (q.question_type === 'mcq' && answered) {
                                    isCorrectAnswer = parseInt(userAnswer) === q.correct_answer_index;
                                }
                                return (
                                    <div key={q.id} className={`p-3 rounded-xl border text-sm ${!answered ? 'border-yellow-500/20 bg-yellow-500/5'
                                            : q.question_type === 'mcq' ? (isCorrectAnswer ? 'border-green-500/20 bg-green-500/5' : 'border-red-500/20 bg-red-500/5')
                                                : 'border-blue-500/20 bg-blue-500/5'
                                        }`}>
                                        <div className="flex items-start gap-2">
                                            <span className={`font-bold shrink-0 ${!answered ? 'text-yellow-400' : q.question_type !== 'mcq' ? 'text-blue-400' : isCorrectAnswer ? 'text-green-400' : 'text-red-400'}`}>
                                                Q{i + 1}.
                                            </span>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-gray-300 leading-relaxed">{q.question_text}</p>
                                                {!answered && <p className="text-yellow-400/70 text-xs mt-1 italic">Not answered (scored 0)</p>}
                                                {answered && q.question_type === 'mcq' && (
                                                    <div className="mt-1 space-y-0.5">
                                                        <p className={`text-xs ${isCorrectAnswer ? 'text-green-400' : 'text-red-400'}`}>
                                                            Your answer: {q.options?.[parseInt(userAnswer)] || '—'} {isCorrectAnswer ? '✓' : '✗'}
                                                        </p>
                                                        {!isCorrectAnswer && (
                                                            <p className="text-green-400/80 text-xs">
                                                                Correct: {q.options?.[q.correct_answer_index] || '—'}
                                                            </p>
                                                        )}
                                                        {q.explanation && <p className="text-gray-500 text-xs mt-1 italic">{q.explanation}</p>}
                                                    </div>
                                                )}
                                                {answered && q.question_type !== 'mcq' && (
                                                    <p className="text-blue-400/70 text-xs mt-1 italic">Open answer — AI evaluated</p>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </motion.div>

                    {/* CTA */}
                    <div className="text-center pb-8">
                        <button onClick={() => navigate('/dashboard')}
                            className="px-10 py-4 bg-gradient-to-r from-pink-500 to-blue-500 rounded-2xl font-bold text-lg hover:shadow-xl hover:shadow-pink-500/30 hover:scale-105 transition-all">
                            Back to Dashboard
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // ─── ACTIVE TEST ──────────────────────────────────────────────────────────
    if (!test || questions.length === 0) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center text-white">
                <div className="text-center">
                    <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <p className="text-xl">No questions available in this test.</p>
                    <button onClick={() => navigate('/dashboard')} className="mt-4 px-6 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];
    const progress = (answeredCount / questions.length) * 100;
    const isLowTime = timeRemaining < 300;

    return (
        <div className="h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white overflow-hidden flex flex-col">
            {/* Header */}
            <header className="border-b border-white/10 backdrop-blur-sm bg-slate-950/60 px-6 py-3 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-4">
                    <h1 className="text-xl font-bold">Test in Progress</h1>
                    <motion.div animate={isLowTime ? { scale: [1, 1.05, 1] } : {}} transition={{ repeat: Infinity, duration: 1 }}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-mono font-bold text-base ${isLowTime ? 'bg-red-500/30 text-red-300' : 'bg-blue-500/20 text-blue-300'}`}>
                        <Clock className="w-4 h-4" />
                        {formatTime(timeRemaining)}
                    </motion.div>
                    {/* Progress bar */}
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                        <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                            <div className="h-full bg-green-500 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
                        </div>
                        <span>{answeredCount}/{questions.length}</span>
                    </div>
                </div>
                <button onClick={() => handleSubmitTest(false)} disabled={submitting}
                    className="px-6 py-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-pink-500/40 transition-all disabled:opacity-50">
                    {submitting ? 'Submitting...' : 'Submit Test'}
                </button>
            </header>

            {/* 3-Panel Layout */}
            <div className="flex flex-1 overflow-hidden">
                {/* LEFT — Question (70%) */}
                <div className="flex-1 overflow-y-auto p-8">
                    <div className="max-w-2xl mx-auto">

                        {/* Question header */}
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400 font-medium">Question {currentQuestionIndex + 1} of {questions.length}</span>
                            <div className="flex items-center gap-2">
                                <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${currentQuestion.question_type === 'mcq' ? 'bg-blue-500/20 text-blue-300' :
                                        currentQuestion.question_type === 'short_answer' ? 'bg-purple-500/20 text-purple-300' :
                                            'bg-orange-500/20 text-orange-300'
                                    }`}>
                                    {currentQuestion.question_type === 'mcq' ? 'MCQ' :
                                        currentQuestion.question_type === 'short_answer' ? 'Short Answer' : 'Problem Solving'}
                                </span>
                                <span className="px-2.5 py-1 bg-white/10 rounded-lg text-xs font-semibold">
                                    {currentQuestion.points} pt{currentQuestion.points > 1 ? 's' : ''}
                                </span>
                            </div>
                        </div>

                        <AnimatePresence mode="wait">
                            <motion.div key={currentQuestionIndex} initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }}
                                transition={{ duration: 0.2 }}>

                                <h2 className="text-xl font-bold mb-6 leading-relaxed">{currentQuestion.question_text}</h2>

                                {/* MCQ Options */}
                                {currentQuestion.question_type === 'mcq' && currentQuestion.options && (
                                    <div className="space-y-3">
                                        {currentQuestion.options.map((option, index) => {
                                            const selected = answers[currentQuestion.id] === index;
                                            return (
                                                <motion.button key={index} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
                                                    onClick={() => handleAnswerChange(currentQuestion.id, index)}
                                                    className={`w-full p-4 rounded-xl border-2 text-left transition-all ${selected
                                                        ? 'border-pink-500 bg-pink-500/10 shadow-lg shadow-pink-500/20'
                                                        : 'border-white/10 bg-white/5 hover:border-white/30 hover:bg-white/8'
                                                        }`}>
                                                    <div className="flex items-center gap-3">
                                                        <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center shrink-0 transition-all ${selected ? 'border-pink-500 bg-pink-500' : 'border-white/30'}`}>
                                                            {selected && <CheckCircle className="w-4 h-4 text-white" />}
                                                        </div>
                                                        <span className="font-bold text-gray-300">{String.fromCharCode(65 + index)}.</span>
                                                        <span className={selected ? 'text-white' : 'text-gray-300'}>{option}</span>
                                                    </div>
                                                </motion.button>
                                            );
                                        })}
                                    </div>
                                )}

                                {/* Text Answer */}
                                {(currentQuestion.question_type === 'short_answer' || currentQuestion.question_type === 'problem_solving') && (
                                    <div>
                                        {currentQuestion.question_type === 'problem_solving' && (
                                            <p className="text-sm text-gray-500 mb-3">💡 Explain your approach, steps, and solution in detail.</p>
                                        )}
                                        <textarea value={answers[currentQuestion.id] || ''}
                                            onChange={e => handleAnswerChange(currentQuestion.id, e.target.value)}
                                            placeholder={currentQuestion.question_type === 'problem_solving'
                                                ? "Describe your solution approach step by step..."
                                                : "Write your answer here..."}
                                            rows={currentQuestion.question_type === 'problem_solving' ? 10 : 6}
                                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-pink-500/60 focus:ring-2 focus:ring-pink-500/20 focus:outline-none transition-all text-white placeholder-gray-600 resize-none font-mono text-sm leading-relaxed"
                                        />
                                        <div className="text-right text-xs text-gray-600 mt-1">
                                            {(answers[currentQuestion.id] || '').length} chars
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        </AnimatePresence>

                        {/* Navigation */}
                        <div className="flex items-center justify-between mt-8">
                            <button onClick={() => { setCurrentQuestionIndex(p => Math.max(0, p - 1)); setQuestionStartTime(Date.now()); }}
                                disabled={currentQuestionIndex === 0}
                                className="px-6 py-2.5 bg-white/10 hover:bg-white/20 rounded-xl font-semibold transition-colors disabled:opacity-30">
                                ← Previous
                            </button>
                            <div className="text-xs text-gray-500">
                                {isAnswered(currentQuestion.id) ? <span className="text-green-400">✓ Answered</span> : <span className="text-gray-500">Not answered</span>}
                            </div>
                            <button onClick={() => { setCurrentQuestionIndex(p => Math.min(questions.length - 1, p + 1)); setQuestionStartTime(Date.now()); }}
                                disabled={currentQuestionIndex === questions.length - 1}
                                className="px-6 py-2.5 bg-white/10 hover:bg-white/20 rounded-xl font-semibold transition-colors disabled:opacity-30">
                                Next →
                            </button>
                        </div>
                    </div>
                </div>

                {/* RIGHT — Camera + Navigator (320px) */}
                <div className="w-[320px] border-l border-white/10 flex flex-col shrink-0">
                    {/* Camera */}
                    <div className="h-[200px] border-b border-white/10 bg-black/40 p-3 shrink-0">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-semibold text-gray-400">Proctoring Camera</span>
                            <div className={`flex items-center gap-1 text-xs ${cameraEnabled ? 'text-green-400' : 'text-red-400'}`}>
                                {cameraEnabled ? <><Camera className="w-3 h-3" /><span>Live</span></> : <><CameraOff className="w-3 h-3" /><span>Off</span></>}
                            </div>
                        </div>
                        {cameraEnabled ? (
                            <video ref={videoRef} autoPlay playsInline muted className="w-full h-[148px] rounded-lg object-cover bg-black" />
                        ) : (
                            <div className="w-full h-[148px] rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                                <div className="text-center p-3">
                                    <CameraOff className="w-6 h-6 text-red-400 mx-auto mb-1" />
                                    <p className="text-xs text-red-400">{cameraError || 'Camera unavailable'}</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Question Navigator */}
                    <div className="flex-1 overflow-y-auto p-4">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Navigator</h3>
                            <span className="text-xs text-gray-500">{answeredCount}/{questions.length} done</span>
                        </div>
                        <div className="grid grid-cols-5 gap-1.5">
                            {questions.map((q, index) => (
                                <motion.button key={q.id} whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
                                    onClick={() => { setCurrentQuestionIndex(index); setQuestionStartTime(Date.now()); }}
                                    className={`aspect-square rounded-lg text-xs font-bold transition-all ${index === currentQuestionIndex
                                        ? 'bg-pink-500 text-white ring-2 ring-pink-400 ring-offset-1 ring-offset-slate-950'
                                        : isAnswered(q.id)
                                            ? 'bg-green-500/80 text-white hover:bg-green-500'
                                            : 'bg-white/8 text-gray-500 hover:bg-white/15'
                                        }`}>
                                    {index + 1}
                                </motion.button>
                            ))}
                        </div>

                        {/* Legend */}
                        <div className="mt-4 space-y-1.5 text-xs">
                            {[
                                { color: 'bg-green-500/80', label: 'Answered' },
                                { color: 'bg-white/8', label: 'Not Answered' },
                                { color: 'bg-pink-500', label: 'Current' },
                            ].map(({ color, label }) => (
                                <div key={label} className="flex items-center gap-2">
                                    <div className={`w-3 h-3 rounded ${color}`} />
                                    <span className="text-gray-500">{label}</span>
                                </div>
                            ))}
                        </div>

                        {/* Score preview */}
                        <div className="mt-4 p-3 bg-white/5 rounded-xl border border-white/8 space-y-1.5 text-xs">
                            <div className="flex justify-between"><span className="text-gray-500">Answered</span><span className="text-green-400 font-semibold">{answeredCount}</span></div>
                            <div className="flex justify-between"><span className="text-gray-500">Skipped</span><span className="text-yellow-400 font-semibold">{questions.length - answeredCount}</span></div>
                            <div className="border-t border-white/10 pt-1.5 flex justify-between">
                                <span className="text-gray-500">Completion</span>
                                <span className="text-white font-bold">{Math.round(progress)}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
