import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronLeft, ChevronRight, Check, AlertCircle, Clock } from 'lucide-react';

function LearningWindow() {
  const [currentView, setCurrentView] = useState('content'); // 'content' or 'assessment'
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [showFeedback, setShowFeedback] = useState(false);

  // Mock data
  const content = {
    type: 'youtube',
    title: 'Python Functions Tutorial',
    url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
  };

  const questions = [
    {
      id: 1,
      text: 'What is the correct syntax to define a function in Python?',
      options: ['function myFunc():', 'def myFunc():', 'func myFunc():', 'define myFunc():'],
      correct: 1,
      explanation: 'In Python, functions are defined using the "def" keyword followed by the function name and parentheses.',
      difficulty: 1,
    },
    {
      id: 2,
      text: 'What does the return statement do in a function?',
      options: ['Prints the value', 'Exits the function and returns a value', 'Deletes the function', 'Pauses the function'],
      correct: 1,
      explanation: 'The return statement exits the function and optionally passes back a value to the caller.',
      difficulty: 1,
    },
  ];

  const handleAnswerSelect = (index) => {
    setSelectedAnswer(index);
  };

  const handleSubmitAnswer = () => {
    const isCorrect = selectedAnswer === questions[currentQuestion].correct;
    setAnswers([...answers, { questionId: questions[currentQuestion].id, answer: selectedAnswer, correct: isCorrect }]);
    setShowFeedback(true);
  };

  const handleNextQuestion = () => {
    setShowFeedback(false);
    setSelectedAnswer(null);
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-white/10 rounded-lg transition-all">
              <X className="w-5 h-5" />
            </button>
            <div>
              <h1 className="font-bold">{content.title}</h1>
              <p className="text-sm text-gray-400">Python Programming</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setCurrentView('content')}
              className={`px-4 py-2 rounded-lg transition-all ${currentView === 'content' ? 'bg-pink-500/20 text-pink-300' : 'text-gray-400 hover:text-white'}`}
            >
              Content
            </button>
            <button
              onClick={() => setCurrentView('assessment')}
              className={`px-4 py-2 rounded-lg transition-all ${currentView === 'assessment' ? 'bg-pink-500/20 text-pink-300' : 'text-gray-400 hover:text-white'}`}
            >
              Assessment
            </button>
          </div>
        </div>
      </header>

      {/* Content View */}
      {currentView === 'content' && (
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="aspect-video bg-black rounded-xl overflow-hidden border border-white/10">
            <iframe
              src={content.url}
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setCurrentView('assessment')}
            className="mt-6 w-full py-4 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold text-lg"
          >
            Start Assessment
          </motion.button>
        </div>
      )}

      {/* Assessment View */}
      {currentView === 'assessment' && (
        <div className="max-w-4xl mx-auto px-6 py-8">
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Question {currentQuestion + 1} of {questions.length}</span>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Clock className="w-4 h-4" />
                <span>2:34</span>
              </div>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
                className="h-full bg-gradient-to-r from-pink-500 to-blue-500"
              />
            </div>
          </div>

          {/* Question Card */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentQuestion}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm mb-6"
            >
              <div className="flex items-start justify-between mb-6">
                <h2 className="text-2xl font-bold flex-1">{questions[currentQuestion].text}</h2>
                <div className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-sm">
                  Level {questions[currentQuestion].difficulty}
                </div>
              </div>

              {/* Options */}
              <div className="space-y-3 mb-6">
                {questions[currentQuestion].options.map((option, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    onClick={() => !showFeedback && handleAnswerSelect(index)}
                    disabled={showFeedback}
                    className={`w-full p-4 rounded-lg text-left transition-all ${
                      selectedAnswer === index
                        ? showFeedback
                          ? index === questions[currentQuestion].correct
                            ? 'bg-green-500/20 border-green-500'
                            : 'bg-red-500/20 border-red-500'
                          : 'bg-pink-500/20 border-pink-500'
                        : 'bg-white/5 border-white/10 hover:bg-white/10'
                    } border`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{option}</span>
                      {showFeedback && index === questions[currentQuestion].correct && (
                        <Check className="w-5 h-5 text-green-400" />
                      )}
                      {showFeedback && selectedAnswer === index && index !== questions[currentQuestion].correct && (
                        <X className="w-5 h-5 text-red-400" />
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>

              {/* Feedback */}
              <AnimatePresence>
                {showFeedback && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`p-4 rounded-lg ${
                      selectedAnswer === questions[currentQuestion].correct
                        ? 'bg-green-500/10 border border-green-500/30'
                        : 'bg-red-500/10 border border-red-500/30'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {selectedAnswer === questions[currentQuestion].correct ? (
                        <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                      )}
                      <div>
                        <div className="font-semibold mb-1">
                          {selectedAnswer === questions[currentQuestion].correct ? 'Correct!' : 'Incorrect'}
                        </div>
                        <div className="text-sm text-gray-300">{questions[currentQuestion].explanation}</div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </AnimatePresence>

          {/* Action Buttons */}
          <div className="flex gap-4">
            {!showFeedback ? (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleSubmitAnswer}
                disabled={selectedAnswer === null}
                className="flex-1 py-4 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Submit Answer
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleNextQuestion}
                className="flex-1 py-4 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold flex items-center justify-center gap-2"
              >
                {currentQuestion < questions.length - 1 ? (
                  <>
                    Next Question
                    <ChevronRight className="w-5 h-5" />
                  </>
                ) : (
                  'Finish Assessment'
                )}
              </motion.button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default LearningWindow;
