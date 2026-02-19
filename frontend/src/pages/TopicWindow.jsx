import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Upload, Link as LinkIcon, FileText, Video, X, Plus, Zap, Play, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function TopicWindow() {
  const navigate = useNavigate();
  const { topicId } = useParams();
  const [showAddContent, setShowAddContent] = useState(false);
  const [contentType, setContentType] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [topicName, setTopicName] = useState(topicId === 'new' ? '' : 'Python Programming');
  const [contentItems] = useState(topicId === 'new' ? [] : [
    { id: 1, type: 'youtube', title: 'Python Functions Tutorial', thumbnail: 'https://via.placeholder.com/300x200' },
    { id: 2, type: 'pdf', title: 'Python Basics.pdf', pages: 45 },
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <Zap className="w-8 h-8 text-pink-500" fill="#E945F5" />
            <span className="text-xl font-bold">Velocity</span>
          </div>
          <div className="flex items-center gap-4">
            <button className="px-4 py-2 rounded-lg hover:bg-white/5 transition-colors">
              Dashboard
            </button>
            <button className="px-4 py-2 rounded-lg hover:bg-white/5 transition-colors">
              Progress
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Topic Header */}
        <div className="mb-12">
          {topicId === 'new' ? (
            <div className="max-w-2xl">
              <h1 className="text-4xl font-bold mb-4">Create New Topic</h1>
              <input
                type="text"
                value={topicName}
                onChange={(e) => setTopicName(e.target.value)}
                placeholder="Enter topic name (e.g., Python Programming)"
                className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-xl focus:border-pink-500/50 focus:outline-none text-2xl font-semibold transition-colors"
              />
            </div>
          ) : (
            <div>
              <h1 className="text-4xl font-bold mb-2">{topicName}</h1>
              <div className="flex items-center gap-6 text-gray-400">
                <span>Mastery: 87%</span>
                <span>•</span>
                <span>5 Content Items</span>
                <span>•</span>
                <span>Difficulty: Hard</span>
              </div>
            </div>
          )}
        </div>

        {/* Content Window */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left: Content List */}
          <div className="lg:col-span-1">
            <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold">Content Library</h2>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowAddContent(true)}
                  className="p-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg hover:shadow-lg hover:shadow-pink-500/50 transition-all"
                >
                  <Plus className="w-5 h-5" />
                </motion.button>
              </div>

              {contentItems.length === 0 ? (
                <div className="text-center py-12">
                  <BookOpen className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">No content yet</p>
                  <button
                    onClick={() => setShowAddContent(true)}
                    className="text-pink-400 hover:text-pink-300 transition-colors text-sm"
                  >
                    Add your first content
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {contentItems.map((item) => (
                    <motion.div
                      key={item.id}
                      whileHover={{ x: 4 }}
                      className="p-4 bg-white/5 rounded-xl border border-white/10 hover:border-pink-500/30 cursor-pointer transition-all"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg ${item.type === 'youtube' ? 'bg-red-500/20' : 'bg-blue-500/20'}`}>
                          {item.type === 'youtube' ? (
                            <Video className="w-5 h-5 text-red-400" />
                          ) : (
                            <FileText className="w-5 h-5 text-blue-400" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-sm truncate">{item.title}</h3>
                          <p className="text-xs text-gray-400 mt-1">
                            {item.type === 'youtube' ? 'Video' : `${item.pages} pages`}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right: Content Viewer */}
          <div className="lg:col-span-2">
            <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-8 min-h-[600px]">
              {contentItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-pink-500/20 to-blue-500/20 flex items-center justify-center mb-6">
                    <Upload className="w-12 h-12 text-pink-400" />
                  </div>
                  <h3 className="text-2xl font-bold mb-3">Add Your First Content</h3>
                  <p className="text-gray-400 mb-8 max-w-md">
                    Upload a YouTube video, PDF, or PowerPoint to start learning. Our AI will extract key concepts and generate assessments.
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowAddContent(true)}
                    className="px-8 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-pink-500/50 transition-all"
                  >
                    Add Content
                  </motion.button>
                </div>
              ) : (
                <div>
                  <div className="aspect-video bg-black/50 rounded-xl mb-6 flex items-center justify-center">
                    <Play className="w-16 h-16 text-white/50" />
                  </div>
                  <h3 className="text-2xl font-bold mb-4">Python Functions Tutorial</h3>
                  <p className="text-gray-400 mb-6">
                    Learn about Python functions, parameters, return values, and more in this comprehensive tutorial.
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold hover:shadow-lg hover:shadow-pink-500/50 transition-all"
                  >
                    Take Assessment
                  </motion.button>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Add Content Modal */}
      <AnimatePresence>
        {showAddContent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
            onClick={() => {
              setShowAddContent(false);
              setContentType(null);
            }}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-2xl bg-gradient-to-br from-slate-900 to-purple-900/50 rounded-2xl border border-white/10"
            >
              <div className="p-6 border-b border-white/10 flex items-center justify-between">
                <h2 className="text-2xl font-bold">Add Learning Content</h2>
                <button onClick={() => setShowAddContent(false)} className="p-2 hover:bg-white/10 rounded-lg">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-6">
                {!contentType ? (
                  <div className="space-y-4">
                    <p className="text-gray-400 mb-6">Choose content type</p>
                    
                    <button
                      onClick={() => setContentType('youtube')}
                      className="w-full p-6 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-pink-500/50 transition-all flex items-center gap-4"
                    >
                      <div className="p-4 rounded-xl bg-red-500/20">
                        <Video className="w-8 h-8 text-red-400" />
                      </div>
                      <div className="text-left">
                        <h3 className="text-lg font-bold">YouTube Video</h3>
                        <p className="text-sm text-gray-400">Paste a YouTube link</p>
                      </div>
                    </button>

                    <button
                      onClick={() => setContentType('pdf')}
                      className="w-full p-6 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-pink-500/50 transition-all flex items-center gap-4"
                    >
                      <div className="p-4 rounded-xl bg-blue-500/20">
                        <FileText className="w-8 h-8 text-blue-400" />
                      </div>
                      <div className="text-left">
                        <h3 className="text-lg font-bold">PDF Document</h3>
                        <p className="text-sm text-gray-400">Upload a PDF file</p>
                      </div>
                    </button>

                    <button
                      onClick={() => setContentType('ppt')}
                      className="w-full p-6 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-pink-500/50 transition-all flex items-center gap-4"
                    >
                      <div className="p-4 rounded-xl bg-orange-500/20">
                        <Upload className="w-8 h-8 text-orange-400" />
                      </div>
                      <div className="text-left">
                        <h3 className="text-lg font-bold">PowerPoint</h3>
                        <p className="text-sm text-gray-400">Upload PPT/PPTX</p>
                      </div>
                    </button>
                  </div>
                ) : contentType === 'youtube' ? (
                  <div className="space-y-6">
                    <button onClick={() => setContentType(null)} className="text-sm text-gray-400 hover:text-white">
                      ← Back
                    </button>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">YouTube URL</label>
                      <div className="relative">
                        <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          value={youtubeUrl}
                          onChange={(e) => setYoutubeUrl(e.target.value)}
                          placeholder="https://youtube.com/watch?v=..."
                          className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-pink-500/50 focus:outline-none"
                        />
                      </div>
                    </div>

                    <button className="w-full py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold">
                      Process Video
                    </button>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <button onClick={() => setContentType(null)} className="text-sm text-gray-400 hover:text-white">
                      ← Back
                    </button>
                    
                    <div className="border-2 border-dashed border-white/20 rounded-xl p-12 text-center hover:border-pink-500/50 cursor-pointer">
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-400">Drop your file here or click to browse</p>
                    </div>

                    <button className="w-full py-3 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg font-semibold">
                      Upload & Process
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
