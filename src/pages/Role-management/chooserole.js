import React, { useState } from 'react';
import './chooserole.css';

const modules = [
  'Roles', 'Users', 'Report'
];
const actions = ['All', 'Index', 'Create', 'Edit', 'Delete'];

const initialPermissions = modules.reduce((acc, module) => {
  acc[module] = actions.reduce((a, action) => {
    a[action] = false;
    return a;
  }, {});
  return acc;
}, {});

const ChooseRoles = () => {
  const [username, setUsername] = useState('');
  const [permissions, setPermissions] = useState(initialPermissions);

  const handleCheckbox = (module, action) => {
    setPermissions(prev => {
      const updated = { ...prev };
      // Toggle the clicked action
      updated[module] = { ...updated[module], [action]: !updated[module][action] };

      if (action === 'All') {
        // If 'All' is toggled, set all actions to its value
        const newValue = !prev[module]['All'];
        actions.forEach(act => {
          updated[module][act] = newValue;
        });
      } else {
        // If all individual actions are checked, set 'All' to true
        const allChecked = actions.slice(1).every(act => act === action ? !prev[module][act] : updated[module][act]);
        updated[module]['All'] = allChecked;
        // If any is unchecked, 'All' should be false
        if (!updated[module][action]) {
          updated[module]['All'] = false;
        }
      }
      return updated;
    });
  };

  const handleUsername = (e) => setUsername(e.target.value);

  const handleSave = (e) => {
    e.preventDefault();
    alert(`Username: ${username}\nPermissions: ${JSON.stringify(permissions, null, 2)}`);
  };

  return (
    <div className="chooserole-container">
      <form className="chooserole-form" onSubmit={handleSave}>
        <label className="chooserole-label">Name</label>
        <input
          className="chooserole-input"
          type="text"
          placeholder="Username"
          value={username}
          onChange={handleUsername}
          required
        />
        <div className="chooserole-permissions">
          <label className="chooserole-label">Permissions</label>
          <table className="chooserole-table">
            <thead>
              <tr>
                <th>Module</th>
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
        <button className="chooserole-save" type="submit">Save</button>
      </form>
    </div>
  );
};

export default ChooseRoles;
