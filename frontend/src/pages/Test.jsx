import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock, CheckCircle, XCircle, AlertCircle, ChevronRight,
  ChevronLeft, Send, Loader2, Trophy, TrendingUp, TrendingDown
} from 'lucide-react';

export default function Test() {
  const { testId } = useParams();
  const navigate = useNavigate();
  
  const [test, setTest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState(null);

  useEffect(() => {
    loadTest();
  }, [testId]);

  useEffect(() => {
    if (test && !showResults) {
      const timer = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
      
      return () => clearInterval(timer);
    }
  }, [test, showResults]);

  const loadTest = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`/api/adaptive/tests/${testId}/`);
      const testData = await response.json();
      
      setTest(testData);
      setQuestions(testData.questions || []);
      
      // Start the test
      await fetch(`/api/adaptive/tests/${testId}/start/`, {
        method: 'POST'
      });
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to load test:', err);
      setError('Failed to load test');
      setLoading(false);
    }
  };

  const handleAnswerChange = (value) => {
    const currentQuestion = questions[currentQuestionIndex];
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: value
    }));
  };

  const handleNextQuestion = async () => {
    const currentQuestion = questions[currentQuestionIndex];
    const answer = answers[currentQuestion.id];
    
    if (answer !== undefined && answer !== '') {
      // Submit answer to backend
      try {
        const timeTaken = Math.floor((Date.now() - questionStartTime) / 1000);
        
        await fetch(`/api/adaptive/tests/${testId}/submit_answer/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question_id: currentQuestion.id,
            answer_text: currentQuestion.question_type === 'mcq' ? '' : answer,
            selected_index: currentQuestion.question_type === 'mcq' ? answer : null,
            time_taken_seconds: timeTaken
          })
        });
      } catch (err) {
        console.error('Failed to submit answer:', err);
      }
    }
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setQuestionStartTime(Date.now());
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      setQuestionStartTime(Date.now());
    }
  };

  const handleSubmitTest = async () => {
    // Submit current answer if exists
    const currentQuestion = questions[currentQuestionIndex];
    const answer = answers[currentQuestion.id];
    
    if (answer !== undefined && answer !== '') {
      try {
        const timeTaken = Math.floor((Date.now() - questionStartTime) / 1000);
        
        await fetch(`/api/adaptive/tests/${testId}/submit_answer/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question_id: currentQuestion.id,
            answer_text: currentQuestion.question_type === 'mcq' ? '' : answer,
            selected_index: currentQuestion.question_type === 'mcq' ? answer : null,
            time_taken_seconds: timeTaken
          })
        });
      } catch (err) {
        console.error('Failed to submit answer:', err);
      }
    }
    
    // Complete test
    try {
      setSubmitting(true);
      
      const response = await fetch(`/api/adaptive/tests/${testId}/complete/`, {
        method: 'POST'
      });
      
      const resultsData = await response.json();
      setResults(resultsData);
      setShowResults(true);
      
      setSubmitting(false);
    } catch (err) {
      console.error('Failed to submit test:', err);
      setError('Failed to submit test');
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getAnsweredCount = () => {
    return Object.keys(answers).filter(key => answers[key] !== undefined && answers[key] !== '').length;
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
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
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

  if (showResults && results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <div className="relative inline-block mb-6">
              <Trophy className="w-24 h-24 text-yellow-400 mx-auto" />
              <div className="absolute inset-0 blur-2xl bg-yellow-400/30" />
            </div>
            
            <h1 className="text-4xl font-bold mb-4">Test Complete!</h1>
            <p className="text-xl text-gray-300">
              You scored {results.overall_score?.toFixed(1)}%
            </p>
          </motion.div>

          {/* Score Card */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="p-6 rounded-xl bg-white/5 border border-white/10">
              <div className="text-3xl font-bold text-green-400 mb-2">
                {results.correct_answers}/{results.total_questions}
              </div>
              <div className="text-sm text-gray-400">Correct Answers</div>
            </div>
            
            <div className="p-6 rounded-xl bg-white/5 border border-white/10">
              <div className="text-3xl font-bold text-blue-400 mb-2">
                {formatTime(timeElapsed)}
              </div>
              <div className="text-sm text-gray-400">Time Taken</div>
            </div>
            
            <div className="p-6 rounded-xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-2 text-3xl font-bold mb-2">
                {results.next_difficulty > test.difficulty_level ? (
                  <>
                    <TrendingUp className="w-8 h-8 text-green-400" />
                    <span className="text-green-400">Level {results.next_difficulty}</span>
                  </>
                ) : results.next_difficulty < test.difficulty_level ? (
                  <>
                    <TrendingDown className="w-8 h-8 text-orange-400" />
                    <span className="text-orange-400">Level {results.next_difficulty}</span>
                  </>
                ) : (
                  <span className="text-blue-400">Level {results.next_difficulty}</span>
                )}
              </div>
              <div className="text-sm text-gray-400">Next Difficulty</div>
            </div>
          </div>

          {/* Feedback */}
          <div className="p-6 rounded-xl bg-gradient-to-br from-pink-500/10 to-blue-500/10 border border-white/10 mb-8">
            <h3 className="text-lg font-semibold mb-2">Feedback</h3>
            <p className="text-gray-300">{results.difficulty_feedback}</p>
          </div>

          {/* Weak Areas */}
          {results.weak_areas && results.weak_areas.length > 0 && (
            <div className="p-6 rounded-xl bg-white/5 border border-white/10 mb-8">
              <h3 className="text-lg font-semibold mb-4">Areas to Improve</h3>
              <div className="space-y-3">
                {results.weak_areas.map((area, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                    <span>{area.concept}</span>
                    <span className="text-sm text-gray-400">{area.accuracy?.toFixed(1)}% accuracy</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex-1 py-3 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
            >
              Back to Dashboard
            </button>
            <button
              onClick={() => window.location.reload()}
              className="flex-1 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg hover:shadow-lg transition-all"
            >
              Take Another Test
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold">Test - Difficulty Level {test.difficulty_level}</h1>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/10">
                <Clock className="w-4 h-4" />
                <span className="text-sm font-mono">{formatTime(timeElapsed)}</span>
              </div>
              <span className="text-sm text-gray-400">
                {getAnsweredCount()}/{questions.length} answered
              </span>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              className="h-full bg-gradient-to-r from-pink-500 to-blue-500"
            />
          </div>
        </div>
      </header>

      {/* Question */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestionIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="mb-8"
          >
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <div className="text-sm text-gray-400 mb-2">
                  Question {currentQuestionIndex + 1} of {questions.length}
                </div>
                <h2 className="text-2xl font-bold">{currentQuestion.question_text}</h2>
              </div>
              <div className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-sm">
                {currentQuestion.question_type === 'mcq' ? 'Multiple Choice' : 
                 currentQuestion.question_type === 'short_answer' ? 'Short Answer' : 
                 'Problem Solving'}
              </div>
            </div>

            {/* Answer Input */}
            {currentQuestion.question_type === 'mcq' ? (
              <div className="space-y-3">
                {currentQuestion.options?.map((option, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    onClick={() => handleAnswerChange(index)}
                    className={`w-full p-4 rounded-lg text-left transition-all border ${
                      answers[currentQuestion.id] === index
                        ? 'bg-pink-500/20 border-pink-500'
                        : 'bg-white/5 border-white/10 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                        answers[currentQuestion.id] === index
                          ? 'border-pink-500 bg-pink-500'
                          : 'border-white/30'
                      }`}>
                        {answers[currentQuestion.id] === index && (
                          <CheckCircle className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <span>{option}</span>
                    </div>
                  </motion.button>
                ))}
              </div>
            ) : (
              <textarea
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswerChange(e.target.value)}
                placeholder="Type your answer here..."
                rows={6}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-pink-500/50 focus:outline-none resize-none"
              />
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex gap-4">
          <button
            onClick={handlePreviousQuestion}
            disabled={currentQuestionIndex === 0}
            className="flex items-center gap-2 px-6 py-3 bg-white/10 rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-5 h-5" />
            Previous
          </button>
          
          <div className="flex-1" />
          
          {currentQuestionIndex < questions.length - 1 ? (
            <button
              onClick={handleNextQuestion}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg hover:shadow-lg transition-all"
            >
              Next
              <ChevronRight className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={handleSubmitTest}
              disabled={submitting}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Submit Test
                </>
              )}
            </button>
          )}
        </div>

        {/* Question Navigator */}
        <div className="mt-8 p-6 rounded-xl bg-white/5 border border-white/10">
          <h3 className="text-sm font-semibold mb-4">Question Navigator</h3>
          <div className="grid grid-cols-10 gap-2">
            {questions.map((q, index) => (
              <button
                key={q.id}
                onClick={() => {
                  setCurrentQuestionIndex(index);
                  setQuestionStartTime(Date.now());
                }}
                className={`aspect-square rounded-lg flex items-center justify-center text-sm font-semibold transition-all ${
                  index === currentQuestionIndex
                    ? 'bg-pink-500 text-white'
                    : answers[q.id] !== undefined && answers[q.id] !== ''
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                    : 'bg-white/10 text-gray-400 hover:bg-white/20'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
