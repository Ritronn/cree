import { createContext, useContext, useState, useEffect, useMemo } from 'react';

import en from './translations/en.json';
import hi from './translations/hi.json';
import mr from './translations/mr.json';
import te from './translations/te.json';
import ta from './translations/ta.json';

const translations = { en, hi, mr, te, ta };

const LanguageContext = createContext();

export const LANGUAGES = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
    { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
    { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
];

export function LanguageProvider({ children }) {
    const [language, setLanguageState] = useState(() => {
        return localStorage.getItem('velocity-language') || 'en';
    });

    const setLanguage = (lang) => {
        setLanguageState(lang);
        localStorage.setItem('velocity-language', lang);
    };

    // t() function: looks up a dot-separated key path in the current translation
    const t = useMemo(() => {
        const currentTranslation = translations[language] || translations.en;
        const fallback = translations.en;

        return (key) => {
            const keys = key.split('.');
            let value = currentTranslation;
            let fallbackValue = fallback;

            for (const k of keys) {
                value = value?.[k];
                fallbackValue = fallbackValue?.[k];
            }

            // Return translated value, or fallback to English, or return the key itself
            return value || fallbackValue || key;
        };
    }, [language]);

    const contextValue = useMemo(() => ({
        language,
        setLanguage,
        t,
    }), [language, t]);

    return (
        <LanguageContext.Provider value={contextValue}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}

export default LanguageContext;
