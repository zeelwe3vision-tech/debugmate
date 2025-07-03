import React, { useEffect } from 'react';
import logo from '../../assets/images/logo.png';
import { useContext } from 'react';
import { MyContext } from '../../App';
import { MdEmail } from "react-icons/md";
import { RiLockPasswordLine } from "react-icons/ri";
import { useNavigate } from 'react-router-dom';
import { IoMdArrowBack } from 'react-icons/io';
import './signin.css';


const SignIn = () => {
    const context = useContext(MyContext);
    const navigate = useNavigate();
    useEffect(() => {
        context.setIshideSidebar(true);
        return () => {
            context.setIshideSidebar(false);
        };
    }, [context]);
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
                    <form>
                            <label htmlFor='email' className='mt-2'>Email</label>
                        <div className='form-group mt-2 position-relative'>
                            <span className='icon'><MdEmail /></span>
                            <input type='email' className='form-control mt-2' id='email' placeholder='Enter your email' autoFocus/>
                        </div>
                            <label htmlFor='password' className='mt-2'>Password</label>
                        <div className='form-group mt-2 position-relative'>
                            <span className='icon '><RiLockPasswordLine /></span>
                            <input type='password' className='form-control mt-2' id='Password' placeholder='Enter your Password' />
                        </div>
                        <div className='d-flex justify-content-between'>
                        <button className='btn btn-primary mt-8'>Login</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default SignIn;