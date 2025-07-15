import React, { useState, useEffect, useRef } from 'react';
import './chooserole.css';
import { databaseService } from '../../services/supabase';
import { Alert } from 'react-bootstrap';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const modules = [
  'Web Devlopment', 'Ar-Vr devlopment', 'Graphic Designer','AI Devlopment','SEO and Degital Marketing',
];
const actions = ['All', 'Index', 'Create', 'Edit', 'Delete'];

const initialPermissions = modules.reduce((acc, module) => {
  acc[module] = actions.reduce((a, action) => {
    a[action] = false;
    return a;
  }, {});
  return acc;
}, {});

// Helper to filter only selected permissions
const getSelectedPermissions = (permissions) => {
  const filtered = {};
  Object.keys(permissions).forEach(module => {
    // If "All" is checked, only save "All": true for that module
    if (permissions[module]['All']) {
      filtered[module] = { All: true };
    } else {
      // Otherwise, only save checked actions (not "All")
      const selected = {};
      Object.keys(permissions[module]).forEach(action => {
        if (action !== 'All' && permissions[module][action]) {
          selected[action] = true;
        }
      });
      if (Object.keys(selected).length > 0) {
        filtered[module] = selected;
      }
    }
  });
  return filtered;
};

const ChooseRoles = () => {
  const [username, setUsername] = useState('');
  const [permissions, setPermissions] = useState(initialPermissions);
  const [allUsers, setAllUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('success');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationText, setNotificationText] = useState('');
  const [notificationType, setNotificationType] = useState('');
  const notificationTimeout = useRef(null);

  useEffect(() => {
    const fetchUsers = async () => {
      const { data, error } = await databaseService.getAllUserLogins();
      if (!error) setAllUsers(data);
    };
    fetchUsers();
  }, []);

  useEffect(() => {
    if (username) {
      setFilteredUsers(allUsers.filter(u => u.name.toLowerCase().includes(username.toLowerCase())));
      setShowDropdown(true);
    } else {
      setFilteredUsers([]);
      setShowDropdown(false);
    }
  }, [username, allUsers]);

  const handleDropdownSelect = (name) => {
    setUsername(name);
    setShowDropdown(false);
  };

  const handleCheckbox = (module, action) => {
    setPermissions(prev => {
      const updated = { ...prev };
      updated[module] = { ...updated[module], [action]: !updated[module][action] };
      if (action === 'All') {
        const newValue = !prev[module]['All'];
        actions.forEach(act => {
          updated[module][act] = newValue;
        });
      } else {
        const allChecked = actions.slice(1).every(act => act === action ? !prev[module][act] : updated[module][act]);
        updated[module]['All'] = allChecked;
        if (!updated[module][action]) {
          updated[module]['All'] = false;
        }
      }
      return updated;
    });
  };

  const handleUsername = (e) => setUsername(e.target.value);

  const showAnimatedNotification = (text, type = 'success') => {
    setNotificationText(text);
    setNotificationType(type);
    setShowNotification(true);
    if (notificationTimeout.current) clearTimeout(notificationTimeout.current);
    notificationTimeout.current = setTimeout(() => setShowNotification(false), 2000);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      const user = allUsers.find(u => u.name === username);
      if (!user) throw new Error('User not found');
      const selectedPermissions = getSelectedPermissions(permissions);
      const { error } = await databaseService.updateUserLoginByEmail(user.email, { permission_roles: selectedPermissions });
      if (error) {
        console.error('Supabase update error:', error);
        showAnimatedNotification('Failed to update permissions: ' + error.message, 'error');
        return;
      }
      showAnimatedNotification('Permissions updated successfully!', 'success');
    } catch (error) {
      console.error('Update error:', error);
      showAnimatedNotification('Failed to update permissions: ' + error.message, 'error');
    }
  };

  return (
    <div className="chooserole-container">
      <ToastContainer />
      <div style={{ position: 'absolute', top: 20, left: 0, right: 0, zIndex: 9999 }}>
        {message && <Alert variant={messageType} className="text-center">{message}</Alert>}
      </div>
      <div className={`animated-notification${showNotification ? ' show' : ''}${notificationType === 'error' ? ' error' : ''}`}>
        {notificationText}
      </div>
      <form className="chooserole-form" onSubmit={handleSave} autoComplete="off">
        <label className="chooserole-label">Name</label>
        <div style={{ position: 'relative' }}>
          <input
            className="chooserole-input"
            type="text"
            placeholder="Username"
            value={username}
            onChange={handleUsername}
            onFocus={() => setShowDropdown(true)}
            required
            autoComplete="off"
          />
          {showDropdown && filteredUsers.length > 0 && (
            <div style={{ position: 'absolute', zIndex: 1000, background: '#fff', width: '100%', border: '1px solid #ccc', maxHeight: 150, overflowY: 'auto' }}>
              {filteredUsers.map(u => (
                <div key={u.email} style={{ padding: 8, cursor: 'pointer' }} onClick={() => handleDropdownSelect(u.name)}>
                  {u.name}
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="chooserole-permissions">
          <label className="chooserole-label">Permissions</label>
          <div className="chooserole-table-wrapper">
            <table className="chooserole-table table-responsive">
              <thead>
                <tr>
                  <th>Roles</th>
                  {actions.map(action => <th key={action}>{action}</th>)}
                </tr>
              </thead>
              <tbody>
                {modules.map(module => (
                  <tr key={module}>
                    <td>{module}</td>
                    {actions.map(action => (
                      <td key={action}>
                        <input
                          type="checkbox"
                          checked={permissions[module][action]}
                          onChange={() => handleCheckbox(module, action)}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <button className="chooserole-save" type="submit">Save</button>
      </form>
    </div>
  );
};

export default ChooseRoles;
