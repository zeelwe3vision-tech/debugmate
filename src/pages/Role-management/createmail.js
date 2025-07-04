import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Button, Table, Form, Badge, Card, Alert } from 'react-bootstrap';
import { FaEdit, FaTrash } from 'react-icons/fa';
import './createmail.css';
import { databaseService } from '../../services/supabase';

const roleColors = {
  Admin: 'primary',
  Hr: 'warning',
  Employee: 'success',
  Sales: 'danger',
};

const CreateMail = () => {
  const [employees, setEmployees] = useState([]);
  const [newEmployee, setNewEmployee] = useState({ name: '', email: '', password: '', role: 'Admin' });
  const [isAdding, setIsAdding] = useState(false);
  const [search, setSearch] = useState('');
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('success');
  const [editEmployeeId, setEditEmployeeId] = useState(null);
  const [editEmployee, setEditEmployee] = useState({ name: '', email: '', password: '', role: 'Admin' });

  // Fetch employees from Supabase on mount
  useEffect(() => {
    const fetchEmployees = async () => {
      const { data, error } = await databaseService.getAllUserLogins();
      if (!error) setEmployees(data);
    };
    fetchEmployees();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewEmployee({ ...newEmployee, [name]: value });
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    try {
      await databaseService.createUserLogin({
        email: newEmployee.email,
        password: newEmployee.password,
        role: newEmployee.role,
        name: newEmployee.name
      });
      const { data } = await databaseService.getAllUserLogins();
      setEmployees(data);
      setNewEmployee({ name: '', email: '', password: '', role: 'Admin' });
      setIsAdding(false);
      setMessageType('success');
      setMessage('User added successfully!');
    } catch (error) {
      setMessageType('danger');
      setMessage('Failed to add user.');
    }
    setTimeout(() => setMessage(null), 3000);
  };

  const handleDeleteEmployee = async (id, email) => {
    try {
      await databaseService.deleteUserLoginByEmail(email);
      const { data } = await databaseService.getAllUserLogins();
      setEmployees(data);
      setMessageType('success');
      setMessage('User deleted successfully!');
    } catch (error) {
      setMessageType('danger');
      setMessage('Failed to delete user.');
    }
    setTimeout(() => setMessage(null), 3000);
  };

  const handleEditClick = (emp) => {
    setEditEmployeeId(emp.id);
    setEditEmployee({ ...emp });
  };

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setEditEmployee({ ...editEmployee, [name]: value });
  };

  const handleEditSave = async () => {
    try {
      await databaseService.updateUserLoginByEmail(editEmployee.email, {
        name: editEmployee.name,
        password: editEmployee.password,
        role: editEmployee.role
      });
      const { data } = await databaseService.getAllUserLogins();
      setEmployees(data);
      setMessageType('success');
      setMessage('User updated successfully!');
      setEditEmployeeId(null);
    } catch (error) {
      setMessageType('danger');
      setMessage('Failed to update user.');
    }
    setTimeout(() => setMessage(null), 3000);
  };

  const handleEditCancel = () => {
    setEditEmployeeId(null);
  };

  const filteredEmployees = employees.filter(emp =>
    emp.name.toLowerCase().includes(search.toLowerCase()) ||
    emp.email.toLowerCase().includes(search.toLowerCase()) ||
    emp.role.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Container fluid className="d-flex justify-content-center align-items-center min-vh-99 createmail-bg">
      <div style={{ position: 'absolute', top: 20, left: 0, right: 0, zIndex: 9999 }}>
        {message && <Alert variant={messageType} className="text-center">{message}</Alert>}
      </div>
      <Card className="w-100 shadow createmail-card">
        <Card.Body className='wrapper'>
          <Row className="align-items-center mb-4">
            <Col xs={12} md={6} className="mb-3 mb-md-0">
              <h2 className="fw-bold mb-0">Employee List</h2>
            </Col>
            <Col xs={6} md={3} className="text-md-end mb-3 mb-md-0">
              <Button
                variant="primary"
                className="rounded-pill px-4 py-2 fw-bold"
                onClick={() => setIsAdding(!isAdding)}
                style={{ background: '#8ca8f4', border: 'none' }}
              >
                {isAdding ? 'Cancel' : '+ New Employee'}
              </Button>
            </Col>
            <Col xs={6} md={3} className="text-md-end">
              <Form.Control
                type="text"
                placeholder="Search"
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="createmail-search"
              />
            </Col>
          </Row>
          {isAdding && (
            <Form onSubmit={handleAddEmployee} className="mb-4 p-3 rounded createmail-add-form">
              <Row className="g-2">
                <Col md={3} xs={12}><Form.Control type="text" name="name" value={newEmployee.name} onChange={handleInputChange} placeholder="Name" required /></Col>
                <Col md={3} xs={12}><Form.Control type="email" name="email" value={newEmployee.email} onChange={handleInputChange} placeholder="Email" required /></Col>
                <Col md={3} xs={12}><Form.Control type="password" name="password" value={newEmployee.password} onChange={handleInputChange} placeholder="Password" required /></Col>
                <Col md={2} xs={12}>
                  <Form.Select name="role" value={newEmployee.role} onChange={handleInputChange}>
                    <option value="Admin">Admin</option>
                    <option value="Hr">Hr</option>
                    <option value="Employee">Employee</option>
                    <option value="Sales">Sales</option>
                  </Form.Select>
                </Col>
                <Col md={1} xs={12} className="d-grid">
                  <Button type="submit" variant="success" className="fw-bold">Add</Button>
                </Col>
              </Row>
            </Form>
          )}
          <div className="table-responsive">
            <Table
              hover
              striped
              className="align-middle createmail-table modern-table"
            >
              <thead>
                <tr>
                  <th className="fw-bold">N0.</th>
                  <th className="fw-bold">NAME</th>
                  <th className="fw-bold">EMAIL-ID</th>
                  <th className="fw-bold">PASSWORD</th>
                  <th className="fw-bold">ROLE</th>
                  <th className="fw-bold">EDIT</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map(emp => (
                  <tr key={emp.id}>
                    <td>{emp.id}</td>
                    <td>{editEmployeeId === emp.id ? (
                      <Form.Control type="text" name="name" value={editEmployee.name} onChange={handleEditInputChange} />
                    ) : emp.name}</td>
                    <td>{editEmployeeId === emp.id ? (
                      <Form.Control type="email" name="email" value={editEmployee.email} onChange={handleEditInputChange} disabled />
                    ) : emp.email}</td>
                    <td>{editEmployeeId === emp.id ? (
                      <Form.Control type="password" name="password" value={editEmployee.password} onChange={handleEditInputChange} />
                    ) : ('*'.repeat(emp.password.length))}</td>
                    <td>{editEmployeeId === emp.id ? (
                      <Form.Select name="role" value={editEmployee.role} onChange={handleEditInputChange}>
                        <option value="Admin">Admin</option>
                        <option value="Hr">Hr</option>
                        <option value="Employee">Employee</option>
                        <option value="Sales">Sales</option>
                      </Form.Select>
                    ) : (
                      <Badge bg={roleColors[emp.role] || 'secondary'} className="px-3 py-2 rounded-pill text-capitalize">{emp.role}</Badge>
                    )}</td>
                    <td>
                      {editEmployeeId === emp.id ? (
                        <>
                          <Button variant="success" size="sm" className="me-2" onClick={handleEditSave}>Save</Button>
                          <Button variant="secondary" size="sm" onClick={handleEditCancel}>Cancel</Button>
                        </>
                      ) : (
                        <>
                          <Button variant="link" className="p-0 me-2 text-primary" onClick={() => handleEditClick(emp)}><FaEdit /></Button>
                          <Button variant="link" className="p-0 text-danger" onClick={() => handleDeleteEmployee(emp.id, emp.email)}><FaTrash /></Button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default CreateMail;

