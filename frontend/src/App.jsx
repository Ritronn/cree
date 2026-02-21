import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import SignUp from './pages/SignUp';
import SignIn from './pages/SignIn';
import Dashboard from './pages/Dashboard';
import NewDashboard from './pages/NewDashboard';
import CreateSession from './pages/CreateSession';
import TestWindow from './pages/TestWindow';
import TopicWindow from './pages/TopicWindow';
import StudySession from './pages/StudySession';
import Test from './pages/Test';
import LearningWindow from './pages/LearningWindow';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/dashboard" element={<NewDashboard />} />
        <Route path="/old-dashboard" element={<Dashboard />} />
        <Route path="/create-session" element={<CreateSession />} />
        <Route path="/test/:testId" element={<TestWindow />} />
        <Route path="/topic/:topicId" element={<TopicWindow />} />
        <Route path="/session/:sessionId" element={<StudySession />} />
        <Route path="/old-test/:testId" element={<Test />} />
        <Route path="/learning/:contentId" element={<LearningWindow />} />
      </Routes>
    </Router>
  );
}

export default App;
