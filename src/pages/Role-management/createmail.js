import React, { useState } from 'react';
import './createmail.css';
import { FaEdit, FaTrash } from 'react-icons/fa';

const CreateMail = () => {
    const initialEmployees = [
        { id: 1, name: 'John Gerard', email: 'adam@gmail.com', password: 'password123', role: 'Admin' },
        { id: 2, name: 'John Smith Gerard', email: 'adam@gmail.com', password: 'password123', role: 'Hr' },
        { id: 3, name: 'Gerard Antony John', email: 'adam@gmail.com', password: 'password123', role: 'Employee' },
        { id: 4, name: 'Johngerard', email: 'adam@gmail.com', password: 'password123', role: 'Sales' },
    ];

    const [employees, setEmployees] = useState(initialEmployees);
    const [newEmployee, setNewEmployee] = useState({ name: '', email: '', password: '', role: 'Admin' });
    const [isAdding, setIsAdding] = useState(false);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewEmployee({ ...newEmployee, [name]: value });
    };

    const handleAddEmployee = (e) => {
        e.preventDefault();
        const newId = employees.length > 0 ? Math.max(...employees.map(e => e.id)) + 1 : 1;
        setEmployees([...employees, { ...newEmployee, id: newId }]);
        setNewEmployee({ name: '', email: '', password: '', role: 'Admin' });
        setIsAdding(false);
    };

    const handleDeleteEmployee = (id) => {
        setEmployees(employees.filter(emp => emp.id !== id));
    };

    return (
        <div className="employee-list-container">
            <div className="employee-list-header">
                <h1>Employee List</h1>
                <button onClick={() => setIsAdding(!isAdding)} className="new-employee-btn">
                    {isAdding ? 'Cancel' : '+ New Employee'}
                </button>
            </div>
            {isAdding && (
                <form onSubmit={handleAddEmployee} className="add-employee-form">
                    <input type="text" name="name" value={newEmployee.name} onChange={handleInputChange} placeholder="Name" required />
                    <input type="email" name="email" value={newEmployee.email} onChange={handleInputChange} placeholder="Email" required />
                    <input type="password" name="password" value={newEmployee.password} onChange={handleInputChange} placeholder="Password" required />
                    <select name="role" value={newEmployee.role} onChange={handleInputChange}>
                        <option value="Admin">Admin</option>
                        <option value="Hr">Hr</option>
                        <option value="Employee">Employee</option>
                        <option value="Sales">Sales</option>
                    </select>
                    <button type="submit">Add Employee</button>
                </form>
            )}
            <div className="employee-list-controls">
                <div className="filter-icons">
                    {/* Placeholder for filter icons */}
                </div>
                <div className="search-bar">
                    <input type="text" placeholder="Search" />
                </div>
            </div>
            <table className="employee-table">
                <thead>
                    <tr>
                        <th>N0.</th>
                        <th>NAME</th>
                        <th>EMAIL-ID</th>
                        <th>PASSWORD</th>
                        <th>ROLE</th>
                        <th>EDIT</th>
                    </tr>
                </thead>
                <tbody>
                    {employees.map(emp => (
                        <tr key={emp.id}>
                            <td>{emp.id}</td>
                            <td>{emp.name}</td>
                            <td>{emp.email}</td>
                            <td>{'*'.repeat(emp.password.length)}</td>
                            <td><span className={`role-badge role-${emp.role.toLowerCase()}`}>{emp.role}</span></td>
                            <td>
                                <button className="icon-btn"><span><FaEdit /></span>&nbsp;&nbsp;<span onClick={() => handleDeleteEmployee(emp.id)}><FaTrash /></span></button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default CreateMail;

