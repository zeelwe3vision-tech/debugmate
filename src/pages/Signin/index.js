import React, { useEffect } from 'react';
import logo from '../../assets/images/logo.png';
import { useContext } from 'react';
import { MyContext } from '../../App';
import { MdEmail } from "react-icons/md";
import { RiLockPasswordLine } from "react-icons/ri";
import google from '../../assets/images/google.png';


const SignIn = () => {
    const context = useContext(MyContext);
    useEffect(() => {
        context.setIshideSidebar(true);
    }, [context]);
    return (
        <div className="login-section">
            <div className='login-box'>
                <div className='logo text-center'>
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
                        <div className='d-flex justify-content-between'>
                            <span className='text-muted mt-2'>Forgot password? <a href='/forgot-password'>Reset password</a></span>
                        </div>
                        <div className='d-flex justify-content-between mt-2'>
                            <span className='line-height-1'></span>
                            <span className='text rounded-pill mt-2'>or</span>
                            <span className='line-height-1'></span>
                        </div>
                        <div className='justify-content-center'>
                            <div className='d-flex position-relative'>
                            <img src={google} alt="google" className='google-img position-absolute'/>
                            <button className='button'>Continue with Google</button></div>
                        </div>
                       <div className='d-flex justify-content-between mt-3'>
                        <span className='text-muted'>Don't have an account? <a href='/signup'>Sign up</a></span>
                       </div>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default SignIn;