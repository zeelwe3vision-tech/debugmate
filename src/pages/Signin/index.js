import React, { useEffect } from 'react';
import logo from '../../assets/images/logo.png';
import { useContext } from 'react';
import { MyContext } from '../../App';
import { MdEmail } from "react-icons/md";
import { RiLockPasswordLine } from "react-icons/ri";
import { useNavigate } from 'react-router-dom';
import { IoMdArrowBack } from 'react-icons/io';
import './signin.css';
import { databaseService } from '../../services/supabase';
import { useState } from 'react';

const SignIn = () => {
    const context = useContext(MyContext);
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    useEffect(() => {
        context.setIshideSidebar(true);
        return () => {
            context.setIshideSidebar(false);
        };
    }, [context]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        // 1. Check user_perms for email
        const { data: userPerm, error: permError } = await databaseService.getUserByEmail(email);
        if (permError || !userPerm) {
            setError('Email not found or not allowed.');
            return;
        }
        // 2. Check password
        if (userPerm.password !== password) {
            setError('Incorrect password.');
            return;
        }
        
        
        // 3. Proceed with Supabase Auth signIn
        if (context.setIsSignIn) context.setIsSignIn(true);
        if (context.setUsername) context.setUsername(userPerm.name); // for header
        if (context.setUserEmail) context.setUserEmail(email);
        // Log employee login event
        await databaseService.logEmployeeLogin({ email, name: userPerm.name, password });
        navigate('/dashboard');
      
        await fetch("http://localhost:5000/set_session", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include", // 🛡️ required to send session cookie!
            body: JSON.stringify({ email }),
          });

          await fetch("http://localhost:5000/chat", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({ email }),
          });
    };
};

    return (
        <div className="login-section">
            <div className='login-box'>
                <div className='d-flex justify-content-between align-items-center'>
                    <span></span>
                    <span className='arrow1' onClick={() => navigate(-1)} title="Back">
                        <IoMdArrowBack />
                    </span>
                </div>
                <div className='logo text-center justify-content-center align-items-center'>
                    <img src={logo} alt="logo" />
                    <h5 className='text mt-2'>Login to DebugMate</h5>
                </div>
                <div className='form-box mt-4'>
                    <form onSubmit={handleLogin}>
                        <label htmlFor='email' className='mt-2'>Email</label>
                        <div className='form-group mt-2 position-relative'>
                            <span className='icon'><MdEmail /></span>
                            <input type='email' className='form-control mt-2' id='email' placeholder='Enter your email' autoFocus value={email} onChange={e => setEmail(e.target.value)} required/>
                        </div>
                        <label htmlFor='password' className='mt-2'>Password</label>
                        <div className='form-group mt-2 position-relative'>
                            <span className='icon '><RiLockPasswordLine /></span>
                            <input type='password' className='form-control mt-2' id='Password' placeholder='Enter your Password' value={password} onChange={e => setPassword(e.target.value)} required/>
                        </div>
                        {error && <div className='text-danger mt-2'>{error}</div>}
                        <div className='d-flex justify-content-between'>
                            <button className='btn btn-primary mt-8' type='submit'>Login</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default SignIn;
