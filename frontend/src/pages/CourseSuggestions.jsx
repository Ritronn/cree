import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  BookOpen, Youtube, FileText, MessageCircle,
  Award, Clock, TrendingUp, ExternalLink, Filter,
  Star, Building2, Calendar, ArrowLeft, Loader,
  Search, Sparkles, Globe, BarChart3, Zap
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CourseSuggestions = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('recent-topics');
  const [recentTopicSuggestions, setRecentTopicSuggestions] = useState([]);
  const [courseraCertificates, setCourseraCertificates] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (activeTab === 'recent-topics') {
      fetchRecentTopicSuggestions();
    } else if (activeTab === 'coursera') {
      fetchCourseraCertificates();
    }
  }, [activeTab]);

  const fetchRecentTopicSuggestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/adaptive-suggestions/recent_topic_suggestions/');
      setRecentTopicSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Error fetching topic suggestions:', error);
      setError('Failed to load topic suggestions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourseraCertificates = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/adaptive-suggestions/coursera_certificates/');
      setCourseraCertificates(response.data.certificates || []);
    } catch (error) {
      console.error('Error fetching Coursera certificates:', error);
      setError('Failed to load certificate recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'beginner':
        return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'intermediate':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'advanced':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      default:
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
    }
  };

  const getMasteryColor = (mastery) => {
    const pct = mastery * 100;
    if (pct >= 70) return 'from-green-500 to-emerald-500';
    if (pct >= 40) return 'from-yellow-500 to-amber-500';
    return 'from-red-500 to-rose-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm sticky top-0 z-50 bg-slate-950/80">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="p-2 hover:bg-white/5 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-3">
                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-2.5 rounded-xl">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold">Course Suggestions</h1>
                  <p className="text-white/50 text-sm">Discover courses based on your learning journey</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => setActiveTab('recent-topics')}
              className={`px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${activeTab === 'recent-topics'
                  ? 'bg-white text-slate-900 shadow-lg shadow-white/10'
                  : 'bg-white/5 text-white/70 hover:bg-white/10 hover:text-white'
                }`}
            >
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Recent Topics
              </div>
            </button>
            <button
              onClick={() => setActiveTab('coursera')}
              className={`px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${activeTab === 'coursera'
                  ? 'bg-white text-slate-900 shadow-lg shadow-white/10'
                  : 'bg-white/5 text-white/70 hover:bg-white/10 hover:text-white'
                }`}
            >
              <div className="flex items-center gap-2">
                <Award className="w-4 h-4" />
                Coursera Certificates
              </div>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-6 flex items-center gap-3"
          >
            <Search className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-red-300 text-sm flex-1">{error}</p>
            <button
              onClick={() => activeTab === 'recent-topics' ? fetchRecentTopicSuggestions() : fetchCourseraCertificates()}
              className="text-red-400 hover:text-red-300 text-sm font-medium"
            >
              Retry
            </button>
          </motion.div>
        )}

        {/* Loading */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center"
            >
              <div className="relative">
                <div className="w-16 h-16 rounded-full border-4 border-blue-500/30 border-t-blue-500 animate-spin mx-auto mb-6" />
                <Sparkles className="w-6 h-6 text-blue-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <div className="text-white/80 font-medium">Loading suggestions...</div>
              <div className="text-white/40 text-sm mt-1">Finding the best resources for you</div>
            </motion.div>
          </div>
        ) : activeTab === 'recent-topics' ? (
          /* Recent Topics Tab */
          <div className="space-y-8">
            {recentTopicSuggestions.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/5 backdrop-blur-lg rounded-2xl p-12 text-center border border-white/10"
              >
                <Globe className="w-16 h-16 text-white/20 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">No Recent Topics</h3>
                <p className="text-white/50 mb-6 max-w-md mx-auto">
                  Start learning to get personalized course suggestions based on your study topics.
                </p>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-3 rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all font-semibold"
                >
                  Go to Dashboard
                </button>
              </motion.div>
            ) : (
              recentTopicSuggestions.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 overflow-hidden"
                >
                  {/* Topic Header */}
                  <div className="p-6 border-b border-white/10 bg-gradient-to-r from-white/5 to-transparent">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 rounded-lg bg-blue-500/20">
                        <Zap className="w-5 h-5 text-blue-400" />
                      </div>
                      <h2 className="text-xl font-bold text-white">{item.topic.name}</h2>
                    </div>
                    {item.topic.description && (
                      <p className="text-white/50 text-sm ml-12 mb-3">{item.topic.description}</p>
                    )}
                    <div className="flex items-center gap-4 ml-12">
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full bg-gradient-to-r ${getMasteryColor(item.topic.mastery_level)}`}
                            style={{ width: `${(item.topic.mastery_level * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-white/50">
                          {(item.topic.mastery_level * 100).toFixed(0)}% mastery
                        </span>
                      </div>
                      <span className="text-xs text-white/40">
                        Difficulty: Level {item.topic.current_difficulty}
                      </span>
                      <span className="text-xs text-white/30">
                        {(item.playlists?.length || 0) + (item.articles?.length || 0) + (item.questions?.length || 0)} resources
                      </span>
                    </div>
                  </div>

                  <div className="p-6 space-y-6">
                    {/* YouTube Playlists */}
                    {item.playlists && item.playlists.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <Youtube className="w-4 h-4 text-red-400" />
                          <h3 className="text-sm font-semibold text-red-400 uppercase tracking-wider">
                            Video Resources
                          </h3>
                          <span className="text-xs text-white/30 ml-auto">{item.playlists.length} found</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {item.playlists.map((playlist, idx) => (
                            <motion.a
                              key={idx}
                              href={playlist.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              whileHover={{ y: -2, scale: 1.01 }}
                              className="bg-red-500/5 hover:bg-red-500/10 rounded-xl p-4 transition-all border border-red-500/20 hover:border-red-500/40 group block"
                            >
                              <div className="flex items-start gap-3">
                                <div className="p-2 rounded-lg bg-red-500/20 flex-shrink-0 mt-0.5">
                                  <Youtube className="w-4 h-4 text-red-400" />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <h4 className="text-white font-medium text-sm line-clamp-2 mb-1 group-hover:text-red-300 transition-colors">
                                    {playlist.title}
                                  </h4>
                                  <p className="text-white/40 text-xs">{playlist.channel}</p>
                                </div>
                                <ExternalLink className="w-4 h-4 text-white/20 group-hover:text-red-400 flex-shrink-0 transition-colors" />
                              </div>
                            </motion.a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Articles */}
                    {item.articles && item.articles.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <FileText className="w-4 h-4 text-blue-400" />
                          <h3 className="text-sm font-semibold text-blue-400 uppercase tracking-wider">
                            Articles & Tutorials
                          </h3>
                          <span className="text-xs text-white/30 ml-auto">{item.articles.length} found</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {item.articles.map((article, idx) => (
                            <motion.a
                              key={idx}
                              href={article.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              whileHover={{ y: -2, scale: 1.01 }}
                              className="bg-blue-500/5 hover:bg-blue-500/10 rounded-xl p-4 transition-all border border-blue-500/20 hover:border-blue-500/40 group block"
                            >
                              <div className="flex items-start gap-3">
                                <div className="p-2 rounded-lg bg-blue-500/20 flex-shrink-0 mt-0.5">
                                  <FileText className="w-4 h-4 text-blue-400" />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <h4 className="text-white font-medium text-sm line-clamp-2 group-hover:text-blue-300 transition-colors">
                                    {article.title}
                                  </h4>
                                </div>
                                <ExternalLink className="w-4 h-4 text-white/20 group-hover:text-blue-400 flex-shrink-0 transition-colors" />
                              </div>
                            </motion.a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Q&A */}
                    {item.questions && item.questions.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-3">
                          <MessageCircle className="w-4 h-4 text-orange-400" />
                          <h3 className="text-sm font-semibold text-orange-400 uppercase tracking-wider">
                            Community Q&A
                          </h3>
                          <span className="text-xs text-white/30 ml-auto">{item.questions.length} found</span>
                        </div>
                        <div className="space-y-2">
                          {item.questions.map((question, idx) => (
                            <motion.a
                              key={idx}
                              href={question.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              whileHover={{ x: 4 }}
                              className="bg-orange-500/5 hover:bg-orange-500/10 rounded-xl p-4 transition-all border border-orange-500/20 hover:border-orange-500/40 group flex items-center gap-4 block"
                            >
                              <div className="p-2 rounded-lg bg-orange-500/20 flex-shrink-0">
                                <MessageCircle className="w-4 h-4 text-orange-400" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-white text-sm line-clamp-1 group-hover:text-orange-300 transition-colors">
                                  {question.title}
                                </p>
                              </div>
                              <span className="text-xs px-2 py-1 rounded-full bg-orange-500/20 text-orange-300 font-medium flex-shrink-0">
                                {question.votes} votes
                              </span>
                              <ExternalLink className="w-4 h-4 text-white/20 group-hover:text-orange-400 flex-shrink-0 transition-colors" />
                            </motion.a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Empty state for a topic */}
                    {(!item.playlists || item.playlists.length === 0) &&
                      (!item.articles || item.articles.length === 0) &&
                      (!item.questions || item.questions.length === 0) && (
                        <div className="text-center py-8 text-white/40">
                          <Search className="w-10 h-10 mx-auto mb-3 opacity-50" />
                          <p className="font-medium">No resources found for this topic</p>
                        </div>
                      )}
                  </div>
                </motion.div>
              ))
            )}
          </div>
        ) : (
          /* Coursera Certificates Tab */
          <div>
            {courseraCertificates.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white/5 backdrop-blur-lg rounded-2xl p-12 text-center border border-white/10"
              >
                <Award className="w-16 h-16 text-white/20 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">No Certificates Available</h3>
                <p className="text-white/50 mb-6 max-w-md mx-auto">
                  Complete some topics to get personalized certificate recommendations from Coursera.
                </p>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-3 rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all font-semibold"
                >
                  Go to Dashboard
                </button>
              </motion.div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {courseraCertificates.map((cert, index) => (
                  <motion.a
                    key={index}
                    href={cert.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ y: -4, scale: 1.02 }}
                    className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10 hover:border-blue-500/40 transition-all group block"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="p-2.5 rounded-xl bg-gradient-to-br from-yellow-500/20 to-orange-500/20">
                        <Award className="w-6 h-6 text-yellow-400" />
                      </div>
                      <ExternalLink className="w-5 h-5 text-white/20 group-hover:text-blue-400 transition-colors" />
                    </div>

                    <h3 className="text-lg font-bold text-white mb-2 line-clamp-2 group-hover:text-blue-300 transition-colors">
                      {cert.title}
                    </h3>

                    <div className="flex items-center gap-2 mb-3">
                      <Building2 className="w-4 h-4 text-white/40" />
                      <p className="text-white/50 text-sm">{cert.provider}</p>
                    </div>

                    <p className="text-white/40 text-sm mb-4 line-clamp-2">
                      {cert.description}
                    </p>

                    <div className="flex items-center gap-3 mb-4">
                      {cert.duration && (
                        <div className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-white/40" />
                          <span className="text-xs text-white/50">{cert.duration}</span>
                        </div>
                      )}
                      {cert.level && (
                        <span className={`px-2 py-0.5 rounded-lg text-xs border ${getLevelColor(cert.level)}`}>
                          {cert.level}
                        </span>
                      )}
                    </div>

                    {cert.recommendation_reason && (
                      <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                        <div className="flex items-start gap-2">
                          <Sparkles className="w-3.5 h-3.5 text-purple-400 flex-shrink-0 mt-0.5" />
                          <p className="text-xs text-white/60">{cert.recommendation_reason}</p>
                        </div>
                      </div>
                    )}
                  </motion.a>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default CourseSuggestions;
