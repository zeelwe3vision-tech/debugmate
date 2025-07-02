import React, { useState } from 'react';
import { Container, Row, Col, Button, Table, Form, Badge, Card } from 'react-bootstrap';
import { FaEdit, FaTrash } from 'react-icons/fa';
import './createmail.css';

const roleColors = {
  Admin: 'primary',
  Hr: 'warning',
  Employee: 'success',
  Sales: 'danger',
};

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
  const [search, setSearch] = useState('');

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

  const filteredEmployees = employees.filter(emp =>
    emp.name.toLowerCase().includes(search.toLowerCase()) ||
    emp.email.toLowerCase().includes(search.toLowerCase()) ||
    emp.role.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Container fluid className="d-flex justify-content-center align-items-center min-vh-99 createmail-bg">
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
                    <td>{emp.name}</td>
                    <td>{emp.email}</td>
                    <td>{'*'.repeat(emp.password.length)}</td>
                    <td>
                      <Badge bg={roleColors[emp.role] || 'secondary'} className="px-3 py-2 rounded-pill text-capitalize">{emp.role}</Badge>
                    </td>
                    <td>
                      <Button variant="link" className="p-0 me-2 text-primary"><FaEdit /></Button>
                      <Button variant="link" className="p-0 text-danger" onClick={() => handleDeleteEmployee(emp.id)}><FaTrash /></Button>
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

