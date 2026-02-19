import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, BookOpen, Zap, TrendingUp, LogOut } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const navigate = useNavigate();
  const [topics] = useState([
    { id: 1, name: 'Python Programming', mastery: 87, difficulty: 3, contentCount: 5 },
    { id: 2, name: 'Calculus', mastery: 45, difficulty: 1, contentCount: 2 },
  ]);

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
            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-2">Welcome back! 👋</h1>
          <p className="text-gray-400">Continue your learning journey</p>
        </div>

        {/* Quick Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-pink-500/20">
                <BookOpen className="w-6 h-6 text-pink-400" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Active Topics</p>
                <p className="text-2xl font-bold">{topics.length}</p>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-blue-500/20">
                <TrendingUp className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Avg Mastery</p>
                <p className="text-2xl font-bold">66%</p>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-purple-500/20">
                <Zap className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Learning Streak</p>
                <p className="text-2xl font-bold">7 days</p>
              </div>
            </div>
          </div>
        </div>

        {/* Topics Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">My Topics</h2>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/topic/new')}
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
                <h3 className="text-xl font-bold mb-4">{topic.name}</h3>
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
                  <div className="flex items-center justify-between text-sm mt-3">
                    <span className="text-gray-400">Difficulty</span>
                    <span className="font-semibold">
                      {topic.difficulty === 1 ? 'Easy' : topic.difficulty === 2 ? 'Medium' : 'Hard'}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}

            {/* Add New Topic Card */}
            <motion.button
              whileHover={{ y: -4 }}
              onClick={() => navigate('/topic/new')}
              className="p-6 rounded-2xl border-2 border-dashed border-white/20 hover:border-pink-500/50 transition-all flex flex-col items-center justify-center min-h-[250px] group"
            >
              <div className="w-16 h-16 rounded-full bg-white/5 group-hover:bg-pink-500/20 flex items-center justify-center mb-4 transition-colors">
                <Plus className="w-8 h-8 text-gray-400 group-hover:text-pink-400 transition-colors" />
              </div>
              <span className="text-gray-400 group-hover:text-white transition-colors font-semibold">
                Create New Topic
              </span>
            </motion.button>
          </div>
        </div>
      </main>
    </div>
  );
}
