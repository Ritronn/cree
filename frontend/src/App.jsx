import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import LanguageSelector from './components/LanguageSelector';
import Landing from './pages/Landing';
import SignUp from './pages/SignUp';
import SignIn from './pages/SignIn';
import Dashboard from './pages/Dashboard';
import CreateSession from './pages/CreateSession';
import TopicWindow from './pages/TopicWindow';
import Assessment from './pages/Assessment';
import AdaptiveSuggestions from './pages/AdaptiveSuggestions';
import CourseSuggestions from './pages/CourseSuggestions';

function App() {
  return (
    <LanguageProvider>
      <Router>
        <LanguageSelector />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create-session" element={<CreateSession />} />
          <Route path="/study-session/:sessionId" element={<TopicWindow />} />
          <Route path="/topic/:topicId" element={<TopicWindow />} />
          <Route path="/assessment" element={<Assessment />} />
          <Route path="/assessment/:assessmentId" element={<Assessment />} />
          <Route path="/adaptive-suggestions" element={<AdaptiveSuggestions />} />
          <Route path="/course-suggestions" element={<CourseSuggestions />} />
        </Routes>
      </Router>
    </LanguageProvider>
  );
}

export default App;
