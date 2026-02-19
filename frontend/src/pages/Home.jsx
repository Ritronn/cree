import { ArrowRight, BookOpen, Target, TrendingUp, Zap, Sparkles, Brain, Rocket, Play, CheckCircle, BarChart3, Users, Star, Award } from 'lucide-react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useRef } from 'react';
import FloatingLines from '../components/FloatingLines';

export default function Landing() {
  const navigate = useNavigate();
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"]
  });
  
  const heroOpacity = useTransform(scrollYProgress, [0, 1], [1, 0.3]);
  const heroScale = useTransform(scrollYProgress, [0, 1], [1, 0.95]);

  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, amount: 0.2 },
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
  };

  const staggerChildren = {
    initial: { opacity: 0 },
    whileInView: { opacity: 1 },
    viewport: { once: true },
    transition: { staggerChildren: 0.1 }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white overflow-x-hidden">
      {/* Subtle gradient background */}
      <div className="fixed inset-0 bg-gradient-to-br from-pink-600/5 via-transparent to-blue-600/5 pointer-events-none" />
      
      {/* Floating Lines with reduced intensity */}
      <div className="fixed inset-0 z-0 opacity-30">
        <FloatingLines
          linesGradient={["#E945F5", "#2F4BC0", "#E945F5"]}
          enabledWaves={["top", "bottom"]}
          lineCount={3}
          lineDistance={8}
          bendRadius={8}
          bendStrength={-0.3}
          interactive={false}
          parallax={true}
        />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Navigation */}
        <nav className="fixed top-0 left-0 right-0 z-50">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-xl border-b border-white/10" />
          <div className="relative max-w-7xl mx-auto px-6 md:px-12 py-4 flex items-center justify-between">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6 }}
              className="flex items-center gap-2"
            >
              <div className="relative">
                <Zap className="w-6 h-6 text-pink-500" />
                <div className="absolute inset-0 blur-lg bg-pink-500/30" />
              </div>
              <span className="text-xl font-semibold tracking-tight bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Velocity
              </span>
            </motion.div>
            
            <div className="flex items-center gap-4">
              <motion.a
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                href="#features"
                className="hidden md:block text-sm text-gray-300 hover:text-white transition-colors"
              >
                Features
              </motion.a>
              <motion.a
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                href="#how-it-works"
                className="hidden md:block text-sm text-gray-300 hover:text-white transition-colors"
              >
                How it works
              </motion.a>
              <motion.button 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigate('/signin')}
                className="px-5 py-2 rounded-lg border border-white/10 bg-white/5 text-sm font-medium hover:bg-white/10 transition-all duration-200"
              >
                Sign In
              </motion.button>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section ref={heroRef} className="relative pt-32 pb-20 overflow-hidden">
          <motion.div 
            style={{ opacity: heroOpacity, scale: heroScale }}
            className="max-w-6xl mx-auto px-6 md:px-12 text-center"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="inline-flex items-center gap-2 mb-8 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm"
            >
              <Sparkles className="w-4 h-4 text-pink-400" />
              <span className="text-sm text-gray-300">
                AI-Powered Adaptive Learning
              </span>
            </motion.div>
            
            {/* Headline */}
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-5xl md:text-7xl font-bold mb-6 tracking-tight"
            >
              <span className="block text-white">Learn at your</span>
              <span className="block bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
                own velocity
              </span>
            </motion.h1>
            
            {/* Description */}
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-lg text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed"
            >
              Transform any content into personalized learning experiences. 
              Our AI adapts to your pace, ensuring you master every concept.
            </motion.p>
            
            {/* CTA Buttons */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8"
            >
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigate('/signup')}
                className="group relative px-8 py-4 rounded-lg bg-gradient-to-r from-pink-500 to-blue-500 text-white font-semibold overflow-hidden"
              >
                <span className="relative flex items-center gap-2">
                  Start learning free
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </span>
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-8 py-4 rounded-lg border border-white/10 bg-white/5 text-white font-semibold hover:bg-white/10 transition-all duration-200 flex items-center gap-2"
              >
                <Play className="w-4 h-4" />
                Watch demo
              </motion.button>
            </motion.div>
            
            {/* Trust indicators */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-400"
            >
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span>No credit card</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-400" />
                <span>10k+ active learners</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-400" />
                <span>4.9/5 rating</span>
              </div>
            </motion.div>
          </motion.div>
        </section>

        {/* Feature Cards */}
        <section id="features" className="py-20">
          <div className="max-w-7xl mx-auto px-6 md:px-12">
            <motion.div {...fadeInUp} className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Everything you need to learn effectively
              </h2>
              <p className="text-gray-300 max-w-2xl mx-auto">
                Our platform combines cutting-edge AI with proven learning methodologies
              </p>
            </motion.div>

            <motion.div 
              variants={staggerChildren}
              initial="initial"
              whileInView="whileInView"
              viewport={{ once: true }}
              className="grid md:grid-cols-3 gap-6"
            >
              {[
                {
                  icon: BookOpen,
                  title: "Multi-format learning",
                  description: "Upload videos, PDFs, or presentations. Our AI extracts key concepts automatically.",
                  color: "from-pink-500 to-rose-500"
                },
                {
                  icon: Brain,
                  title: "Adaptive difficulty",
                  description: "Questions adjust in real-time based on your answers. Always challenging, never frustrating.",
                  color: "from-purple-500 to-indigo-500"
                },
                {
                  icon: TrendingUp,
                  title: "Progress tracking",
                  description: "Visualize your mastery levels and get personalized recommendations for improvement.",
                  color: "from-blue-500 to-cyan-500"
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  variants={fadeInUp}
                  className="group relative p-6 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all duration-300"
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 rounded-xl transition-opacity duration-300`} />
                  <div className="relative">
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} bg-opacity-10 flex items-center justify-center mb-4`}>
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                    <p className="text-sm text-gray-400 leading-relaxed">{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="py-20 bg-white/5">
          <div className="max-w-7xl mx-auto px-6 md:px-12">
            <motion.div {...fadeInUp} className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Three steps to mastery
              </h2>
              <p className="text-gray-300 max-w-2xl mx-auto">
                Simple, intuitive process that fits your learning style
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8 relative">
              {/* Connecting line */}
              <div className="hidden md:block absolute top-24 left-[15%] right-[15%] h-0.5 bg-gradient-to-r from-pink-500/20 via-purple-500/20 to-blue-500/20" />
              
              {[
                {
                  step: "01",
                  title: "Add content",
                  description: "Paste a YouTube URL or upload your PDF. Our AI processes it in seconds.",
                  icon: BookOpen
                },
                {
                  step: "02",
                  title: "Take assessments",
                  description: "Answer smart questions that adapt to your knowledge level.",
                  icon: Target
                },
                {
                  step: "03",
                  title: "Track progress",
                  description: "Watch your mastery grow and revisit concepts when needed.",
                  icon: BarChart3
                }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  variants={fadeInUp}
                  initial="initial"
                  whileInView="whileInView"
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="relative text-center"
                >
                  <div className="relative inline-block mb-6">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pink-500 to-blue-500 flex items-center justify-center text-xl font-bold text-white">
                      {item.step}
                    </div>
                  </div>
                  <div className="mb-4 flex justify-center">
                    <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                      <item.icon className="w-5 h-5 text-pink-400" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-gray-400">{item.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-16">
          <div className="max-w-5xl mx-auto px-6 md:px-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {[
                { label: "Active learners", value: "10k+", icon: Users },
                { label: "Questions answered", value: "1.2M", icon: Brain },
                { label: "Content hours", value: "50k+", icon: Play },
                { label: "Avg. improvement", value: "42%", icon: TrendingUp }
              ].map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="text-center"
                >
                  <stat.icon className="w-6 h-6 text-pink-400 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-white">{stat.value}</div>
                  <div className="text-sm text-gray-400">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <div className="max-w-4xl mx-auto px-6 md:px-12">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative p-12 rounded-2xl bg-gradient-to-br from-pink-500/10 via-purple-500/10 to-blue-500/10 border border-white/10 text-center"
            >
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-pink-500/20 via-transparent to-transparent" />
              
              <div className="relative">
                <Award className="w-12 h-12 text-pink-400 mx-auto mb-6" />
                <h2 className="text-3xl md:text-4xl font-bold mb-4">
                  Start learning at your own velocity
                </h2>
                <p className="text-gray-300 mb-8 max-w-lg mx-auto">
                  Join thousands of students who've transformed their learning experience
                </p>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigate('/signup')}
                  className="px-8 py-4 bg-white text-black rounded-lg font-semibold hover:bg-gray-100 transition-all duration-200 inline-flex items-center gap-2"
                >
                  Get started for free
                  <Rocket className="w-4 h-4" />
                </motion.button>
                <p className="text-xs text-gray-500 mt-4">
                  No credit card required • Cancel anytime
                </p>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 py-8">
          <div className="max-w-7xl mx-auto px-6 md:px-12">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-pink-500" />
                <span className="text-sm text-gray-300">Velocity</span>
              </div>
              <div className="flex gap-6 text-xs text-gray-500">
                <a href="#" className="hover:text-gray-300 transition-colors">Terms</a>
                <a href="#" className="hover:text-gray-300 transition-colors">Privacy</a>
                <a href="#" className="hover:text-gray-300 transition-colors">Contact</a>
              </div>
              <p className="text-xs text-gray-500">
                © 2024 Velocity. All rights reserved.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}