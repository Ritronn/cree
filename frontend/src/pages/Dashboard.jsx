import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, BookOpen, Zap, LogOut, Rocket, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Dashboard() {
  const navigate = useNavigate();
  const [showCreateTopic, setShowCreateTopic] = useState(false);
  const [topicData, setTopicData] = useState({ name: '', description: '' });
  const [topics, setTopics] = useState([]);

  const handleCreateTopic = () => {
    if (topicData.name.trim()) {
      const newTopic = {
        id: Date.now(),
        name: topicData.name,
        description: topicData.description,
        contentCount: 0,
        mastery: 0
      };
      setTopics([...topics, newTopic]);
      setShowCreateTopic(false);
      setTopicData({ name: '', description: '' });
      navigate(`/topic/${newTopic.id}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="w-8 h-8 text-pink-500" fill="#E945F5" />
            <span className="text-xl font-bold">Velocity</span>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 rounded-lg bg-white/10 transition-colors"
            >
              Dashboard
            </button>
            <button className="px-4 py-2 rounded-lg hover:bg-white/5 transition-colors">
              Progress
            </button>
            <button 
              onClick={() => navigate('/')}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {topics.length === 0 ? (
          /* Empty State - Begin Journey */
          <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="relative mb-8"
            >
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-pink-500 to-blue-500 flex items-center justify-center relative z-10">
                <Rocket className="w-16 h-16 text-white" />
              </div>
              <div className="absolute inset-0 blur-3xl bg-gradient-to-br from-pink-500/50 to-blue-500/50 rounded-full animate-pulse" />
            </motion.div>

            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Begin Your Journey
            </h1>
            <p className="text-xl text-gray-400 mb-12 max-w-2xl">
              Create your first topic and start learning at your own velocity. Add content, take assessments, and watch your progress grow.
            </p>

            <motion.button
              whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(233, 69, 245, 0.5)" }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowCreateTopic(true)}
              className="px-10 py-4 bg-gradient-to-r from-pink-500 to-blue-500 rounded-full text-lg font-semibold flex items-center gap-3"
            >
              <Plus className="w-6 h-6" />
              Create Your First Topic
            </motion.button>
          </div>
        ) : (
          /* Topics Grid */
          <>
            <div className="mb-12">
              <h1 className="text-4xl font-bold mb-2">My Topics</h1>
              <p className="text-gray-400">Continue your learning journey</p>
            </div>

            <div className="flex items-center justify-end mb-6">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowCreateTopic(true)}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-pink-500/50 transition-all"
              >
                <Plus className="w-5 h-5" />
                Create New Topic
              </motion.button>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {topics.map((topic) => (
                <motion.div
                  key={topic.id}
                  whileHover={{ y: -4 }}
                  onClick={() => navigate(`/topic/${topic.id}`)}
                  className="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10 hover:border-pink-500/30 transition-all cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-pink-500/20 to-blue-500/20">
                      <BookOpen className="w-6 h-6 text-pink-400" />
                    </div>
                    <span className="px-3 py-1 rounded-full bg-white/10 text-sm">
                      {topic.contentCount} items
                    </span>
                  </div>
                  <h3 className="text-xl font-bold mb-2">{topic.name}</h3>
                  <p className="text-sm text-gray-400 mb-4 line-clamp-2">{topic.description}</p>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Mastery</span>
                      <span className="font-semibold">{topic.mastery}%</span>
                    </div>
                    <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-pink-500 to-blue-500 rounded-full transition-all duration-500"
                        style={{ width: `${topic.mastery}%` }}
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </>
        )}
      </main>

      {/* Create Topic Modal */}
      <AnimatePresence>
        {showCreateTopic && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
            onClick={() => setShowCreateTopic(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-lg bg-gradient-to-br from-slate-900 to-purple-900/50 rounded-2xl border border-white/10"
            >
              <div className="p-6 border-b border-white/10 flex items-center justify-between">
                <h2 className="text-2xl font-bold">Create New Topic</h2>
                <button onClick={() => setShowCreateTopic(false)} className="p-2 hover:bg-white/10 rounded-lg">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Topic Name *</label>
                  <input
                    type="text"
                    value={topicData.name}
                    onChange={(e) => setTopicData({ ...topicData, name: e.target.value })}
                    placeholder="e.g., Python Programming"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-pink-500/50 focus:outline-none transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Description (Optional)</label>
                  <textarea
                    value={topicData.description}
                    onChange={(e) => setTopicData({ ...topicData, description: e.target.value })}
                    placeholder="Brief description of what you'll learn..."
                    rows={4}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-pink-500/50 focus:outline-none transition-colors resize-none"
                  />
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleCreateTopic}
                  disabled={!topicData.name.trim()}
                  className="w-full py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-pink-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Topic
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
