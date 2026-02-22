import { useState, useRef, useEffect } from 'react';
import { Globe } from 'lucide-react';
import { useLanguage, LANGUAGES } from '../i18n/LanguageContext';

export default function LanguageSelector() {
    const { language, setLanguage } = useLanguage();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    const currentLang = LANGUAGES.find(l => l.code === language) || LANGUAGES[0];

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <div ref={dropdownRef} className="fixed top-4 right-4 z-[9999]">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 text-white text-xs font-medium hover:bg-white/20 transition-all duration-300 shadow-lg"
                title="Change Language"
            >
                <Globe className="w-3.5 h-3.5 text-pink-400" />
                <span>{currentLang.nativeName}</span>
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-44 rounded-xl bg-gray-900/95 backdrop-blur-xl border border-white/15 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                    {LANGUAGES.map((lang) => (
                        <button
                            key={lang.code}
                            onClick={() => {
                                setLanguage(lang.code);
                                setIsOpen(false);
                            }}
                            className={`w-full px-4 py-2.5 text-left text-sm flex items-center justify-between transition-colors ${language === lang.code
                                    ? 'bg-pink-500/20 text-pink-300'
                                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                                }`}
                        >
                            <span className="font-medium">{lang.nativeName}</span>
                            <span className="text-xs text-gray-500">{lang.name}</span>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
