import React, { useState, useContext } from "react";
import { Link } from "react-router-dom";
import logo from "../../assets/images/logo.png";
import Button from '@mui/material/Button';
import { MdMenuOpen } from "react-icons/md";
import { MdOutlineMenu } from "react-icons/md";
import 'bootstrap/dist/css/bootstrap.min.css';
import { MdOutlineLightMode } from "react-icons/md";
import { FaUserCircle } from "react-icons/fa";
import { IoMdNotificationsOutline } from "react-icons/io";
import { MyContext } from "../../App";

import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import Divider from '@mui/material/Divider';
import PersonAdd from '@mui/icons-material/PersonAdd';
import Settings from '@mui/icons-material/Settings';
import Logout from '@mui/icons-material/Logout';
import Avatar from '@mui/material/Avatar';

const Header = ({ onToggleSidebar }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const context = useContext(MyContext);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  return (
    <header className="d-flex align-items-center">
      <div className="container-fluid w-100">
        <div className="row d-flex align-items-center w-100">
          {/* logo wrapper*/}
          <div className="col-2 part1">
            <Link to={"/"} className="d-flex align-items-center logo">
              <img src={logo} alt="logo" />
              <span className="ml-2">DebugMate </span>
            </Link>
          </div>
          <div className="col-2 d-flex part2">
            {/* <Button className="rounded-circle menu-btn" onClick={onToggleSidebar}><MdMenuOpen /></Button> */}
            <Button className="rounded-circle menu-btn" onClick={() => context.setIstoggleSidebar(!context.istoggleSidebar)}>
              {
                context.istoggleSidebar === false ? <MdMenuOpen /> : <MdOutlineMenu />}</Button>
          </div>
          <div className="col-8 d-flex align-items-center justify-content-end space-between part3">
            <div className="d-flex align-items-center">
            <Button className="rounded-circle" onClick={() => context.setIstheme(!context.istheme)}><MdOutlineLightMode /></Button>
            <Button className="rounded-circle"><IoMdNotificationsOutline /></Button>
            </div>
          {
            context.isSignIn !== true ?
             <Link to={`/signin`}><Button className="signin-btn btn-rounded">Sign In</Button></Link>
              : 
              <div className="myacc-wrapper">
              <div className="d-flex align-items-center myacc">
                <div className="userImg">
                  <Button className="rounded-circle  profile" onClick={handleClick}><FaUserCircle /></Button>
                  <Menu
                    anchorEl={anchorEl}
                    id="account-menu"
                    open={open}
                    onClose={handleClose}
                    onClick={handleClose}
                    slotProps={{
                      paper: {
                        elevation: 0,
                        sx: {
                          overflow: 'visible',
                          filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                          mt: 1.5,
                          '& .MuiAvatar-root': {
                            width: 32,
                            height: 32,
                            ml: -0.5,
                            mr: 1,
                          },
                          '&::before': {
                            content: '""',
                            display: 'block',
                            position: 'absolute',
                            top: 0,
                            right: 14,
                            width: 10,
                            height: 10,
                            bgcolor: 'background.paper',
                            transform: 'translateY(-50%) rotate(45deg)',
                            zIndex: 0,
                          },
                        },
                      },
                    }}
                    transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                    anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                  >
                    <MenuItem onClick={handleClose}>
                      <Avatar /> My account
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={handleClose}>
                      <ListItemIcon>
                        <PersonAdd fontSize="small" />
                      </ListItemIcon>
                      Add another account
                    </MenuItem>
                    <MenuItem onClick={handleClose}>
                      <ListItemIcon>
                        <Settings fontSize="small" />
                      </ListItemIcon>
                      Settings
                    </MenuItem>
                    <MenuItem onClick={handleClose}>
                      <ListItemIcon>
                        <Logout fontSize="small" />
                      </ListItemIcon>
                      Logout
                    </MenuItem>
                  </Menu>
                </div>
                <div className="userInfo">
                  <h4>John Doe</h4>
                  <p className="mb-0">john.doe@example.com</p>
                </div>
              </div>
            </div>
          }
</div>
        </div>
      </div>
    </header>
  )
}

export default Header;