import { ArrowRight, BookOpen, Target, TrendingUp, Zap, Sparkles, Brain, Rocket } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import FloatingLines from '../components/FloatingLines';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      {/* Floating Lines Background */}
      <div className="fixed inset-0 z-0">
        <FloatingLines
          linesGradient={["#E945F5", "#2F4BC0", "#E945F5"]}
          enabledWaves={["top", "middle", "bottom"]}
          lineCount={5}
          lineDistance={5}
          bendRadius={5}
          bendStrength={-0.5}
          interactive={true}
          parallax={true}
        />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Navigation */}
        <nav className="flex items-center justify-between px-6 md:px-12 py-6 max-w-7xl mx-auto backdrop-blur-sm">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <div className="relative">
              <Zap className="w-8 h-8 text-pink-500" fill="#E945F5" />
              <div className="absolute inset-0 blur-xl bg-pink-500/50" />
            </div>
            <span className="text-2xl font-bold tracking-tight">Velocity</span>
          </motion.div>
          
          <motion.button 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/signin')}
            className="px-6 py-2.5 rounded-full border border-pink-500/30 bg-pink-500/10 backdrop-blur-md text-pink-300 hover:bg-pink-500/20 hover:border-pink-500/50 transition-all duration-300"
          >
            Sign In
          </motion.button>
        </nav>

        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 md:px-12 pt-20 pb-32 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.div 
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 mb-8 px-4 py-2 rounded-full bg-gradient-to-r from-pink-500/20 to-blue-500/20 border border-pink-500/30 backdrop-blur-md"
            >
              <Sparkles className="w-4 h-4 text-pink-400" />
              <span className="text-sm font-medium bg-gradient-to-r from-pink-300 to-blue-300 bg-clip-text text-transparent">
                AI-Powered Adaptive Learning
              </span>
            </motion.div>
            
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight">
              <span className="block bg-gradient-to-r from-white via-pink-200 to-blue-200 bg-clip-text text-transparent">
                Learn at Your
              </span>
              <span className="block bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
                Own Velocity
              </span>
            </h1>
            
            <p className="text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
              Experience the future of learning with AI that adapts to your pace. 
              <span className="text-pink-300"> Master any topic</span> with personalized difficulty and intelligent insights.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-6">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(233, 69, 245, 0.5)" }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/signup')}
                className="group relative px-8 py-4 rounded-full bg-gradient-to-r from-pink-500 to-blue-500 text-white text-lg font-semibold overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-pink-600 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <span className="relative flex items-center gap-2">
                  Get Started Free
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 rounded-full border border-pink-500/30 bg-white/5 backdrop-blur-md text-white text-lg font-semibold hover:bg-white/10 hover:border-pink-500/50 transition-all duration-300"
              >
                Watch Demo
              </motion.button>
            </div>
            
            <p className="text-sm text-gray-400 flex items-center justify-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              No credit card required • Start in 2 minutes
            </p>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="grid md:grid-cols-3 gap-6 mt-24"
          >
            {[
              {
                icon: BookOpen,
                title: "Multi-Format Learning",
                description: "YouTube videos, PDFs, presentations. We extract content and generate smart assessments.",
                gradient: "from-pink-500/20 to-purple-500/20",
                iconColor: "text-pink-400"
              },
              {
                icon: Brain,
                title: "Adaptive Intelligence",
                description: "AI adjusts difficulty in real-time based on your performance. Always challenged, never overwhelmed.",
                gradient: "from-purple-500/20 to-blue-500/20",
                iconColor: "text-purple-400"
              },
              {
                icon: TrendingUp,
                title: "Smart Analytics",
                description: "Track mastery levels, identify weak concepts, and get personalized revision schedules.",
                gradient: "from-blue-500/20 to-cyan-500/20",
                iconColor: "text-blue-400"
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className={`relative group p-8 rounded-2xl bg-gradient-to-br ${feature.gradient} border border-white/10 backdrop-blur-md hover:border-pink-500/30 transition-all duration-300`}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-pink-500/0 to-blue-500/0 group-hover:from-pink-500/10 group-hover:to-blue-500/10 rounded-2xl transition-all duration-300" />
                <div className="relative">
                  <div className="mb-4 inline-block p-3 rounded-xl bg-white/5 backdrop-blur-sm">
                    <feature.icon className={`w-8 h-8 ${feature.iconColor}`} />
                  </div>
                  <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* How It Works Section */}
        <section className="max-w-7xl mx-auto px-6 md:px-12 py-24">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                How It Works
              </h2>
              <p className="text-gray-300 text-lg">Three simple steps to accelerate your learning</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  number: "01",
                  title: "Add Content",
                  description: "Paste a YouTube link or upload your study materials. Our AI extracts key concepts instantly.",
                  icon: BookOpen
                },
                {
                  number: "02",
                  title: "Take Assessments",
                  description: "Answer AI-generated questions tailored to your content. Get instant feedback and explanations.",
                  icon: Target
                },
                {
                  number: "03",
                  title: "Adapt & Master",
                  description: "Watch as the system adjusts difficulty and tracks your progress. Master topics at your own velocity.",
                  icon: Rocket
                }
              ].map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.2 }}
                  viewport={{ once: true }}
                  className="relative"
                >
                  <div className="relative p-8 rounded-2xl bg-black/60 backdrop-blur-xl border border-white/10 text-center">
                    <div className="relative inline-block mb-6">
                      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-pink-500 to-blue-500 flex items-center justify-center text-3xl font-bold relative z-10">
                        {step.number}
                      </div>
                      <div className="absolute inset-0 blur-2xl bg-gradient-to-br from-pink-500/50 to-blue-500/50 rounded-full" />
                    </div>
                    <div className="mb-4 flex justify-center">
                      <div className="p-3 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
                        <step.icon className="w-6 h-6 text-pink-400" />
                      </div>
                    </div>
                    <h3 className="text-2xl font-bold mb-3 text-white">{step.title}</h3>
                    <p className="text-gray-200 leading-relaxed">{step.description}</p>
                  </div>
                  {index < 2 && (
                    <div className="hidden md:block absolute top-1/2 left-full w-full h-0.5 bg-gradient-to-r from-pink-500/50 to-transparent -translate-y-1/2 z-0" />
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        </section>

        {/* CTA Section */}
        <section className="max-w-5xl mx-auto px-6 md:px-12 py-24">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="relative overflow-hidden rounded-3xl"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-pink-500/30 via-purple-500/30 to-blue-500/30 backdrop-blur-xl" />
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLW9wYWNpdHk9IjAuMDUiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-30" />
            
            <div className="relative p-12 md:p-16 text-center border border-white/10">
              <Sparkles className="w-12 h-12 text-pink-400 mx-auto mb-6" />
              <h2 className="text-4xl md:text-5xl font-bold mb-4">
                Ready to accelerate your learning?
              </h2>
              <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
                Join thousands of students who are learning smarter, not harder
              </p>
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: "0 0 40px rgba(255, 255, 255, 0.3)" }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/signup')}
                className="px-10 py-4 bg-white text-black rounded-full text-lg font-bold hover:bg-gray-100 transition-all duration-300 inline-flex items-center gap-2"
              >
                Start Learning Now
                <Rocket className="w-5 h-5" />
              </motion.button>
            </div>
          </motion.div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 py-8 text-center text-gray-400 backdrop-blur-sm">
          <p className="text-sm">© 2024 Velocity. Empowering adaptive learners worldwide.</p>
        </footer>
      </div>
    </div>
  );
}
