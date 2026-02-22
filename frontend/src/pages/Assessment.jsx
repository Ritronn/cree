import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, CheckCircle, XCircle, Zap, Clock, Loader } from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../services/api';

export default function Assessment() {
  const navigate = useNavigate();
  const { assessmentId } = useParams();

  const [loading, setLoading] = useState(true);
  const [assessment, setAssessment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (assessmentId) {
      loadAssessment();
    }
  }, [assessmentId]);

  const loadAssessment = async () => {
    try {
      setLoading(true);
      console.log(`[Assessment] Loading assessment ${assessmentId}...`);
      const response = await api.get(`/assessments/${assessmentId}/`);
      console.log('[Assessment] Response:', response.data);

      setAssessment(response.data);
      setQuestions(response.data.questions || []);

      if (!response.data.questions || response.data.questions.length === 0) {
        console.error('[Assessment] No questions in response');
        setError('No questions found in this assessment.');
      } else {
        console.log(`[Assessment] Loaded ${response.data.questions.length} questions`);
        setError(null);
      }
    } catch (err) {
      console.error('[Assessment] Failed to load assessment:', err);
      console.error('[Assessment] Error response:', err.response?.data);
      setError(err.response?.data?.detail || 'Failed to load assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin mx-auto mb-4 text-purple-400" />
          <p className="text-lg">Loading assessment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold mb-4 text-red-400">{error}</h2>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!questions || questions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold mb-4">No Questions Available</h2>
          <p className="text-gray-400 mb-6">This assessment doesn't have any questions yet.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold mb-4">Question Not Found</h2>
          <p className="text-gray-400 mb-6">Unable to load the current question.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const handleSelectAnswer = (optionIndex) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [currentQuestionIndex]: optionIndex
    });
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);

      // Submit each answer to backend
      for (let i = 0; i < questions.length; i++) {
        const question = questions[i];
        const selectedIndex = selectedAnswers[i];

        if (selectedIndex !== undefined) {
          await api.post(`/assessments/${assessmentId}/submit_answer/`, {
            question_id: question.id,
            selected_answer_index: selectedIndex,
            time_taken_seconds: 60 // You can track actual time if needed
          });
        }
      }

      // Complete the assessment
      await api.post(`/assessments/${assessmentId}/complete/`);

      setShowResults(true);
    } catch (err) {
      console.error('Failed to submit assessment:', err);
      alert('Failed to submit assessment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const calculateScore = () => {
    let correct = 0;
    questions.forEach((q, index) => {
      if (selectedAnswers[index] === q.correct_answer_index) {
        correct++;
      }
    });
    return {
      correct,
      total: questions.length,
      percentage: Math.round((correct / questions.length) * 100)
    };
  };

  if (showResults) {
    const score = calculateScore();
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
        <header className="border-b border-white/10 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Zap className="w-8 h-8 text-pink-500" fill="#E945F5" />
              <span className="text-xl font-bold">Velocity</span>
            </div>
          </div>
        </header>

        <div className="max-w-4xl mx-auto px-6 py-12">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8 text-center"
          >
            <div className="mb-8">
              {score.percentage >= 70 ? (
                <CheckCircle className="w-24 h-24 text-green-400 mx-auto mb-4" />
              ) : (
                <XCircle className="w-24 h-24 text-red-400 mx-auto mb-4" />
              )}
              <h2 className="text-4xl font-bold mb-2">Assessment Complete!</h2>
              <p className="text-gray-400">{assessment?.content_title || 'Assessment'}</p>
            </div>

            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-white/5 rounded-xl p-6">
                <div className="text-4xl font-bold text-pink-500 mb-2">{score.correct}</div>
                <div className="text-sm text-gray-400">Correct</div>
              </div>
              <div className="bg-white/5 rounded-xl p-6">
                <div className="text-4xl font-bold text-blue-500 mb-2">{score.total - score.correct}</div>
                <div className="text-sm text-gray-400">Incorrect</div>
              </div>
              <div className="bg-white/5 rounded-xl p-6">
                <div className="text-4xl font-bold text-purple-500 mb-2">{score.percentage}%</div>
                <div className="text-sm text-gray-400">Score</div>
              </div>
            </div>

            <div className="space-y-4 mb-8">
              {questions.map((q, index) => {
                const userAnswer = selectedAnswers[index];
                const isCorrect = userAnswer === q.correct_answer_index;

                return (
                  <div
                    key={index}
                    className={`bg-white/5 rounded-xl p-6 text-left border ${isCorrect ? 'border-green-500/50' : 'border-red-500/50'
                      }`}
                  >
                    <div className="flex items-start gap-4">
                      {isCorrect ? (
                        <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                      ) : (
                        <XCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
                      )}
                      <div className="flex-1">
                        <p className="font-semibold mb-2">Q{index + 1}: {q.question_text}</p>
                        <p className="text-sm text-gray-400 mb-1">
                          Your answer: <span className={isCorrect ? 'text-green-400' : 'text-red-400'}>
                            {userAnswer !== undefined ? q.options[userAnswer] : 'Not answered'}
                          </span>
                        </p>
                        {!isCorrect && (
                          <p className="text-sm text-gray-400 mb-2">
                            Correct answer: <span className="text-green-400">{q.options[q.correct_answer_index]}</span>
                          </p>
                        )}
                        <p className="text-sm text-gray-300 mt-2">{q.explanation}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <button
              onClick={() => navigate('/dashboard')}
              className="px-8 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg transition-all"
            >
              Back to Dashboard
            </button>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      <header className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <Zap className="w-8 h-8 text-pink-500" fill="#E945F5" />
            <span className="text-xl font-bold">Velocity</span>
          </div>
          <div className="text-sm text-gray-400">
            Question {currentQuestionIndex + 1} of {questions.length}
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-12">
        <motion.div
          key={currentQuestionIndex}
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8"
        >
          <h2 className="text-2xl font-bold mb-6">{currentQuestion.question_text}</h2>

          <div className="space-y-3 mb-8">
            {currentQuestion.options && Array.isArray(currentQuestion.options) && currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleSelectAnswer(index)}
                className={`w-full p-4 rounded-xl text-left transition-all border ${selectedAnswers[currentQuestionIndex] === index
                    ? 'bg-pink-500/20 border-pink-500'
                    : 'bg-white/5 border-white/10 hover:border-pink-500/50'
                  }`}
              >
                <span className="font-semibold mr-3">{String.fromCharCode(65 + index)}.</span>
                {option}
              </button>
            ))}
            {(!currentQuestion.options || !Array.isArray(currentQuestion.options) || currentQuestion.options.length === 0) && (
              <div className="text-center py-8 text-red-400">
                <p>Error: Question options are not properly formatted</p>
                <p className="text-sm text-gray-400 mt-2">Options: {JSON.stringify(currentQuestion.options)}</p>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
              className="px-6 py-3 bg-white/10 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20 transition-all"
            >
              Previous
            </button>

            <div className="flex gap-2">
              {questions.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full ${index === currentQuestionIndex
                      ? 'bg-pink-500'
                      : selectedAnswers[index]
                        ? 'bg-blue-500'
                        : 'bg-white/20'
                    }`}
                />
              ))}
            </div>

            {currentQuestionIndex === questions.length - 1 ? (
              <button
                onClick={handleSubmit}
                className="px-6 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg transition-all"
              >
                Submit
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="px-6 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg transition-all"
              >
                Next
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
