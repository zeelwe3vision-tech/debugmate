import React, { useState, useEffect, createContext } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './component/header';
import "bootstrap/dist/css/bootstrap.min.css";
import Sidebar from './component/Sidebar';
import Communication from './pages/chatbot/Communication';
import Dashboard from './pages/Dashboard';
import Feedback from './pages/chatbot/feedback';
import ChooseRole from './pages/Role-management/chooserole';
import CreateMail from './pages/Role-management/createmail.js';
import Announcements from './pages/Announcements';
import ChatbotIcon from './component/ChatbotIcon';
import SignIn from './pages/Signin';
import EmployeeProjectForm from './pages/project/project_info.js';
import ApiManagement from './pages/Api_managment/Api_managment.js';
import Overview from './pages/Overview/Overview.js';
import Setting from './pages/Setting/setting.js';
import ProjectDetailsTable from './pages/project/ProjectDetailsTable';
import DualChatbot from './pages/chatbot/DualChatbot.js';
import Home from './pages/home/home.js';
const MyContext = createContext();
function App() {
  const [istoggleSidebar, setIstoggleSidebar] = useState(false);
  const [isSignIn, setIsSignIn] = useState(false);
  const [ishideSidebar, setIshideSidebar] = useState(false);
  const[istheme, setIstheme] = useState(true);
  const [username, setUsername] = useState('');
  const [userEmail, setUserEmail] = useState('');
 
  useEffect(() => {
    if(istheme === true){
      document.body.classList.remove('dark');
      document.body.classList.add('light');
      localStorage.setItem('theme', 'light');
    }else{
      document.body.classList.remove('light');
      document.body.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
  }, [istheme]);



  useEffect(() => {
    console.log(istoggleSidebar);
  }, [istoggleSidebar]);

  const location = window.location;
  const isHomePage = location.pathname === '/' || location.pathname === '/home';


  const values={
    istoggleSidebar,
    setIstoggleSidebar,
    isSignIn,
    setIsSignIn,
    ishideSidebar,
    setIshideSidebar,
    istheme,
    setIstheme,
    username,
    setUsername,
    userEmail,
    setUserEmail
  }
  return (
    <BrowserRouter>
      <MyContext.Provider value={values}>
        {isHomePage ? (
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/home" element={<Home />} />
            <Route path="/signin" element={<SignIn />} />
          </Routes>
        ) : (
          <>
            {ishideSidebar !== true && <Header />}
            <div className="main d-flex">
              {ishideSidebar !== true &&
                <div className={`sidebarwrapper ${istoggleSidebar===true ? 'open' : ''}`}>
                  <Sidebar />
                </div>
              }
              <div className={`content ${ishideSidebar===true && 'full'} ${istoggleSidebar===true ? 'open' : ''}`}>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/EmployeeProjectForm" element={<EmployeeProjectForm/>} />
                  <Route path="/chatbot/communication" element={<Communication />} />
                  <Route path="/role-management/chooserole" element={<ChooseRole />} />
                  <Route path="/communication" element={<Communication />} />
                  <Route path="/chatbot/feedback" element={<Feedback />} />
                  <Route path="/role-management/createmail" element={<CreateMail />} />
                  <Route path="/announcements" element={<Announcements />} />
                  <Route path="/api-management" element={<ApiManagement />} />
                  <Route path="/overview" element={<Overview />} />
                  <Route path="/setting" element={<Setting />} />
                  <Route path="/signin" element={<SignIn />} />
                  <Route path="/project/DetailsTable" element={<ProjectDetailsTable />} />
                  <Route path="/chatbot/DualChatbot" element={<DualChatbot />} />
                </Routes>
              </div>
            </div>
            <ChatbotIcon />
          </>
        )}
      </MyContext.Provider>
    </BrowserRouter>
  );
}

export default App;
export { MyContext };
