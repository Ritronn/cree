import { useState, useRef, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useGLTF, OrbitControls, Environment } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Loader2, MessageSquare } from 'lucide-react';
import * as THREE from 'three';

// Avatar Model Component
function AvatarModel({ mousePosition, onClick }) {
  const groupRef = useRef();
  const neckRef = useRef();
  const { scene } = useGLTF('/avatar_1771664816504.glb');
  
  // Clone the scene to avoid issues with multiple instances
  const clonedScene = scene.clone();

  useEffect(() => {
    // Rotate the entire model to face forward
    clonedScene.rotation.y = Math.PI; // 180 degrees to face camera
    
    // Try to find the neck/head bone in the model
    clonedScene.traverse((child) => {
      if (child.isBone) {
        // Look for neck, head, or spine bones
        if (child.name.toLowerCase().includes('neck') || 
            child.name.toLowerCase().includes('head') ||
            child.name.toLowerCase().includes('spine')) {
          neckRef.current = child;
        }
      }
    });
  }, [clonedScene]);

  useFrame(() => {
    // Smooth neck rotation based on mouse position
    if (neckRef.current) {
      const targetRotationY = mousePosition.x * 0.3; // Reduced range
      const targetRotationX = -mousePosition.y * 0.2; // Reduced range
      
      neckRef.current.rotation.y = THREE.MathUtils.lerp(
        neckRef.current.rotation.y,
        targetRotationY,
        0.1
      );
      neckRef.current.rotation.x = THREE.MathUtils.lerp(
        neckRef.current.rotation.x,
        targetRotationX,
        0.1
      );
    }

    // Gentle idle animation
    if (groupRef.current) {
      groupRef.current.position.y = Math.sin(Date.now() * 0.001) * 0.03;
    }
  });

  return (
    <group ref={groupRef} onClick={onClick}>
      <primitive object={clonedScene} scale={1.5} position={[0, -2.2, 0]} />
    </group>
  );
}

// Chatbot Component
function Chatbot({ onClose }) {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hi! I'm your study assistant. How can I help you today?", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: input,
      sender: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const botMessage = {
        id: Date.now() + 1,
        text: "I'm here to help! This is a demo response. Connect me to your AI backend for real conversations!",
        sender: 'bot'
      };
      setMessages(prev => [...prev, botMessage]);
      setLoading(false);
    }, 1000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.9 }}
      className="absolute bottom-full right-0 mb-4 w-96 h-[500px] bg-slate-900/95 backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 border-b border-white/10 bg-gradient-to-r from-pink-500/20 to-blue-500/20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-blue-500 flex items-center justify-center">
            <MessageSquare className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white">Study Assistant</h3>
            <p className="text-xs text-gray-400">Always here to help</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-white" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-r from-pink-500 to-blue-500 text-white'
                  : 'bg-white/10 text-white'
              }`}
            >
              <p className="text-sm">{msg.text}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white/10 px-4 py-2 rounded-2xl">
              <Loader2 className="w-4 h-4 text-white animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10 bg-black/20">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask me anything..."
            className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-pink-500/50 focus:outline-none text-white placeholder-gray-500 text-sm"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="p-2 bg-gradient-to-r from-pink-500 to-blue-500 rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
          >
            <Send className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

// Main Floating Avatar Component
export default function FloatingAvatar() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [showChat, setShowChat] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e) => {
      // Normalize mouse position to -0.5 to 0.5 range
      setMousePosition({
        x: (e.clientX / window.innerWidth) - 0.5,
        y: (e.clientY / window.innerHeight) - 0.5
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleAvatarClick = () => {
    setShowChat(!showChat);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chatbot */}
      <AnimatePresence>
        {showChat && <Chatbot onClose={() => setShowChat(false)} />}
      </AnimatePresence>

      {/* Avatar Container */}
      <motion.div
        className="relative"
        onHoverStart={() => setIsHovered(true)}
        onHoverEnd={() => setIsHovered(false)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {/* Avatar Canvas - No circle, just standing */}
        <div 
          className="relative w-48 h-64 cursor-pointer"
          onClick={handleAvatarClick}
        >
          <Canvas
            camera={{ position: [0, 0, 3.5], fov: 40 }}
            gl={{ alpha: true, antialias: true }}
          >
            <ambientLight intensity={0.8} />
            <directionalLight position={[2, 3, 2]} intensity={1.5} />
            <pointLight position={[-2, 2, 2]} intensity={0.5} color="#ec4899" />
            <pointLight position={[2, 1, 2]} intensity={0.5} color="#3b82f6" />
            
            <Suspense fallback={null}>
              <AvatarModel 
                mousePosition={mousePosition} 
                onClick={handleAvatarClick}
              />
              <Environment preset="sunset" />
            </Suspense>
          </Canvas>
        </div>

        {/* Tooltip */}
        <AnimatePresence>
          {isHovered && !showChat && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1 bg-black/90 text-white text-sm rounded-lg whitespace-nowrap"
            >
              Click to chat with me!
            </motion.div>
          )}
        </AnimatePresence>

        {/* Notification Badge */}
        {!showChat && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute top-2 right-2 w-8 h-8 bg-gradient-to-r from-pink-500 to-red-500 rounded-full flex items-center justify-center text-white shadow-lg cursor-pointer"
            onClick={handleAvatarClick}
          >
            <MessageSquare className="w-4 h-4" />
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

// Preload the GLB model
useGLTF.preload('/avatar_1771664816504.glb');
