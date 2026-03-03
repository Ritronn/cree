import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ChevronLeft,
    ChevronRight,
    LayoutGrid,
    CreditCard,
    Map,
    Home,
    BookOpen,
    Zap,
    ExternalLink
} from 'lucide-react';

// URLs for the standalone cree-eisenhower_matrix app
const CREE_BASE_URL = 'http://localhost:5174';
const CREE_API_URL = 'http://localhost:8001/api';

const NAV_SECTIONS = [
    {
        title: 'Main',
        items: [
            { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/dashboard', type: 'internal' },
            { id: 'sessions', label: 'Study Sessions', icon: BookOpen, path: '/dashboard', type: 'internal' },
        ]
    },
    {
        title: 'Productivity Tools',
        items: [
            {
                id: 'eisenhower',
                label: 'Eisenhower Matrix',
                icon: LayoutGrid,
                url: CREE_BASE_URL,
                apiUrl: `${CREE_API_URL}/tasks/`,
                type: 'external',
                description: 'Prioritize tasks by urgency & importance',
                color: '#F44336',
            },
            {
                id: 'flashcards',
                label: 'Que Cards',
                icon: CreditCard,
                url: `${CREE_BASE_URL}?tab=flashcards`,
                apiUrl: `${CREE_API_URL}/flashcards/`,
                type: 'external',
                description: 'Study with AI-generated flashcards',
                color: '#FF9800',
            },
            {
                id: 'roadmap',
                label: 'Roadmap',
                icon: Map,
                url: `${CREE_BASE_URL}?tab=roadmap`,
                apiUrl: `${CREE_API_URL}/roadmap/list/`,
                type: 'external',
                description: 'Visual learning path & milestones',
                color: '#4CAF50',
            },
        ]
    }
];

export default function FeatureSidebar() {
    const [collapsed, setCollapsed] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();

    const handleClick = (item) => {
        if (item.type === 'internal') {
            navigate(item.path);
        } else {
            window.open(item.url, '_blank');
        }
    };

    return (
        <>
            {/* Backdrop for mobile */}
            <AnimatePresence>
                {!collapsed && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/40 z-40 lg:hidden"
                        onClick={() => setCollapsed(true)}
                    />
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <motion.aside
                animate={{ width: collapsed ? 56 : 240 }}
                transition={{ duration: 0.25, ease: 'easeInOut' }}
                className="fixed left-0 top-0 h-full z-50 flex flex-col bg-[#0d0d1a]/95 backdrop-blur-xl border-r border-white/10"
                style={{ overflow: 'hidden' }}
            >
                {/* Toggle Button */}
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="h-14 flex items-center justify-center border-b border-white/10 hover:bg-white/5 transition-colors flex-shrink-0"
                >
                    {collapsed ? (
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                    ) : (
                        <div className="w-full px-4 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Zap className="w-5 h-5 text-pink-500" fill="#E945F5" />
                                <span className="font-bold text-white text-sm">Velocity</span>
                            </div>
                            <ChevronLeft className="w-5 h-5 text-gray-400" />
                        </div>
                    )}
                </button>

                {/* Nav Items */}
                <div className="flex-1 overflow-y-auto py-3 px-2">
                    {NAV_SECTIONS.map((section) => (
                        <div key={section.title} className="mb-4">
                            {/* Section Title (only when expanded) */}
                            {!collapsed && (
                                <div className="px-2 mb-2 text-[10px] font-semibold uppercase tracking-widest text-gray-600">
                                    {section.title}
                                </div>
                            )}

                            <div className="space-y-1">
                                {section.items.map((item) => {
                                    const Icon = item.icon;
                                    const isActive = item.type === 'internal' && location.pathname === item.path;

                                    return (
                                        <button
                                            key={item.id}
                                            onClick={() => handleClick(item)}
                                            title={collapsed ? item.label : undefined}
                                            className={`
                        w-full flex items-center gap-3 rounded-lg transition-all relative group
                        ${collapsed ? 'justify-center p-3' : 'px-3 py-2.5'}
                        ${isActive
                                                    ? 'bg-purple-600/20 text-purple-300'
                                                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                                                }
                      `}
                                        >
                                            <div
                                                className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
                                                style={{
                                                    background: item.color ? `${item.color}20` : 'transparent',
                                                }}
                                            >
                                                <Icon
                                                    className="w-4 h-4"
                                                    style={{ color: item.color || (isActive ? '#c084fc' : '#9ca3af') }}
                                                />
                                            </div>

                                            {!collapsed && (
                                                <div className="flex-1 text-left min-w-0">
                                                    <div className="flex items-center gap-1.5">
                                                        <span className="text-sm font-medium truncate">{item.label}</span>
                                                        {item.type === 'external' && (
                                                            <ExternalLink className="w-3 h-3 text-gray-600 flex-shrink-0" />
                                                        )}
                                                    </div>
                                                    {item.description && (
                                                        <p className="text-[10px] text-gray-600 truncate mt-0.5">{item.description}</p>
                                                    )}
                                                </div>
                                            )}

                                            {/* Tooltip for collapsed state */}
                                            {collapsed && (
                                                <div className="absolute left-full ml-2 px-3 py-2 bg-[#1a1a30] rounded-lg shadow-xl border border-white/10 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                                                    <div className="text-sm font-medium text-white">{item.label}</div>
                                                    {item.description && (
                                                        <div className="text-[10px] text-gray-400 mt-0.5">{item.description}</div>
                                                    )}
                                                </div>
                                            )}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer */}
                {!collapsed && (
                    <div className="p-3 border-t border-white/10 flex-shrink-0">
                        <div className="px-2 py-2 rounded-lg bg-white/[0.03] border border-white/5">
                            <p className="text-[10px] text-gray-600 text-center">
                                Productivity tools run on separate server
                            </p>
                            <p className="text-[10px] text-purple-400 text-center mt-0.5">
                                localhost:5174
                            </p>
                        </div>
                    </div>
                )}
            </motion.aside>
        </>
    );
}
